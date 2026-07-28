"""Exact absorbing-chain calculations for route-correlated hypergraph networks."""

from dataclasses import dataclass
from itertools import product

import numpy as np
from scipy.sparse import csr_matrix, eye
from scipy.sparse.linalg import spsolve

from network_model import HypergraphSpec, NetworkKernel


SURVIVAL_NUMERICAL_TOLERANCE = 1e-12


def _normalize_survival_probabilities(survival: np.ndarray) -> np.ndarray:
    """Validate and normalize tolerance-scale probability roundoff."""
    values = np.asarray(survival, dtype=np.float64)
    if not np.isfinite(values).all():
        raise ValueError("survival probabilities must be finite")
    tolerance = SURVIVAL_NUMERICAL_TOLERANCE
    if np.any(values < -tolerance) or np.any(values > 1.0 + tolerance):
        raise ValueError("survival probabilities exceed the [0,1] range tolerance")
    prior_running_minimum = np.minimum.accumulate(values[:-1])
    if np.any(values[1:] - prior_running_minimum > tolerance):
        raise ValueError("survival probabilities must be non-increasing")
    return np.minimum.accumulate(np.clip(values, 0.0, 1.0))


def positive_compositions(total: int, parts: int):
    """Yield ordered compositions of ``total`` into ``parts`` positive parts."""
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - parts + 2):
        for tail in positive_compositions(total - first, parts - 1):
            yield (first,) + tail


def _require_positive_scale(scale: int) -> None:
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive Python integer")


def enumerate_internal_states(spec: HypergraphSpec, scale: int) -> tuple[tuple[int, ...], ...]:
    """Enumerate full ordered positive balance compositions in edge order."""
    _require_positive_scale(scale)
    blocks = [
        tuple(positive_compositions(scale * capacity, len(edge)))
        for edge, capacity in zip(spec.edges, spec.capacity_units)
    ]
    return tuple(tuple(value for block in state for value in block) for state in product(*blocks))


@dataclass(frozen=True)
class ExactNetworkResult:
    mean: float
    state_count: int
    max_abs_residual: float
    all_states_reach_boundary: bool
    survival: np.ndarray


def build_transient_matrix(kernel: NetworkKernel, scale: int):
    """Build Q and certify every internal state can reach a boundary leak."""
    states = enumerate_internal_states(kernel.spec, scale)
    index = {state: i for i, state in enumerate(states)}
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []
    reverse: list[list[int]] = [[] for _ in states]
    leaks = np.zeros(len(states), dtype=bool)
    for row, state in enumerate(states):
        x = np.asarray(state, dtype=np.int64)
        for probability, increment in zip(kernel.probabilities, kernel.increments):
            nxt = x + increment
            if np.any(nxt == 0):
                leaks[row] = True
                continue
            col = index[tuple(int(value) for value in nxt)]
            rows.append(row)
            cols.append(col)
            data.append(float(probability))
            reverse[col].append(row)
    q = csr_matrix((data, (rows, cols)), shape=(len(states), len(states)))
    reachable = leaks.copy()
    stack = list(np.flatnonzero(leaks))
    while stack:
        child = stack.pop()
        for parent in reverse[child]:
            if not reachable[parent]:
                reachable[parent] = True
                stack.append(parent)
    return states, index, q, bool(np.all(reachable))


def balanced_initial_state(spec: HypergraphSpec, scale: int) -> tuple[int, ...]:
    """Return the equal-per-participant internal state when it is integral."""
    _require_positive_scale(scale)
    values: list[int] = []
    for edge, capacity in zip(spec.edges, spec.capacity_units):
        total = scale * capacity
        quotient, remainder = divmod(total, len(edge))
        if remainder:
            raise ValueError("balanced initial state is not integral")
        values.extend([quotient] * len(edge))
    return tuple(values)


def solve_exact(
    kernel: NetworkKernel,
    scale: int,
    initial=None,
    survival_horizon: int = 0,
) -> ExactNetworkResult:
    """Solve the exact expected depletion time and optional survival curve."""
    if type(survival_horizon) is not int or survival_horizon < 0:
        raise ValueError("survival_horizon must be a nonnegative Python integer")
    states, index, q, all_states_reach_boundary = build_transient_matrix(kernel, scale)
    if not all_states_reach_boundary:
        raise ValueError("finite-state depletion reachability fails")
    if initial is None:
        initial_state = balanced_initial_state(kernel.spec, scale)
    else:
        try:
            initial_state = tuple(initial)
        except TypeError as error:
            raise ValueError("initial must be an internal state") from error
    if any(
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, (int, np.integer))
        for value in initial_state
    ):
        raise ValueError("initial coordinates must be integer scalars")
    if initial_state not in index:
        raise ValueError("initial must be an internal state")

    state_count = len(states)
    matrix = eye(state_count, format="csr") - q
    rhs = np.ones(state_count)
    solution = spsolve(matrix, rhs)
    residual = matrix @ solution - rhs

    survival = np.empty(survival_horizon + 1, dtype=np.float64)
    survival[0] = 1.0
    mass = np.zeros(state_count, dtype=np.float64)
    mass[index[initial_state]] = 1.0
    for step in range(1, survival_horizon + 1):
        mass = mass @ q
        survival[step] = float(mass.sum())
    survival = _normalize_survival_probabilities(survival)

    return ExactNetworkResult(
        mean=float(solution[index[initial_state]]),
        state_count=state_count,
        max_abs_residual=float(np.max(np.abs(residual))),
        all_states_reach_boundary=all_states_reach_boundary,
        survival=survival,
    )
