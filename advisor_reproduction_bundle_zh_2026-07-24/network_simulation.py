"""Independent Monte Carlo simulation for correlated network routes."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

import numpy as np

from network_model import NetworkKernel


@dataclass(frozen=True)
class NetworkSample:
    stopping_times: np.ndarray
    boundary_coordinates: np.ndarray
    seed: int


@dataclass(frozen=True)
class TimeSummary:
    mean: float
    sd: float
    standard_error: float
    ci_low: float
    ci_high: float


def _require_positive_scale(scale: int) -> None:
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")


def _require_positive_integer(value: int, name: str) -> None:
    if type(value) is not int or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _require_int32_capacity_totals(kernel: NetworkKernel, scale: int) -> None:
    maximum = np.iinfo(np.int32).max
    if any(scale * capacity > maximum for capacity in kernel.spec.capacity_units):
        raise ValueError("declared edge capacity total exceeds int32 range")


def initial_balances(kernel: NetworkKernel, scale: int) -> np.ndarray:
    """Return balanced strictly positive coordinates for every hyperedge."""
    _require_positive_scale(scale)
    _require_int32_capacity_totals(kernel, scale)
    values: list[int] = []
    for edge, capacity in zip(kernel.spec.edges, kernel.spec.capacity_units):
        total = scale * capacity
        balance, remainder = divmod(total, len(edge))
        if remainder:
            raise ValueError("balanced initial state is not integral")
        values.extend([balance] * len(edge))
    return np.asarray(values, dtype=np.int32)


def validate_initial(kernel: NetworkKernel, scale: int, initial: Sequence[int]) -> np.ndarray:
    """Validate explicit balances before simulating any trajectories."""
    _require_positive_scale(scale)
    _require_int32_capacity_totals(kernel, scale)
    try:
        supplied = tuple(initial)
    except TypeError as error:
        raise ValueError("initial balances must be integer scalars") from error
    if any(
        isinstance(value, (bool, np.bool_))
        or not isinstance(value, (int, np.integer))
        for value in supplied
    ):
        raise ValueError("initial balances must be integer scalars")
    if any(int(value) < 1 for value in supplied):
        raise ValueError("initial balances must be strictly positive")
    maximum = np.iinfo(np.int32).max
    if any(int(value) > maximum for value in supplied):
        raise ValueError("initial balances must be within int32 range")
    if len(supplied) != len(kernel.spec.coordinates):
        raise ValueError("initial balances have the wrong shape")
    for edge_index, capacity in enumerate(kernel.spec.capacity_units):
        block = supplied[kernel.edge_slice(edge_index)]
        if sum(int(value) for value in block) != scale * capacity:
            raise ValueError("initial balances must conserve every declared edge capacity")
    return np.asarray(supplied, dtype=np.int32)


def simulate_network(
    kernel: NetworkKernel,
    scale: int,
    repetitions: int,
    seed: int,
    initial: Sequence[int] | None = None,
    max_steps: int | None = None,
) -> NetworkSample:
    """Simulate i.i.d. route samples until every trajectory first hits zero."""
    _require_positive_scale(scale)
    if type(repetitions) is not int or repetitions <= 1:
        raise ValueError("repetitions must be an integer greater than one")
    if max_steps is not None:
        _require_positive_integer(max_steps, "max_steps")

    rng = np.random.default_rng(seed)
    starting = initial_balances(kernel, scale) if initial is None else validate_initial(kernel, scale, initial)
    balances = np.repeat(starting[None, :], repetitions, axis=0)
    times = np.zeros(repetitions, dtype=np.int64)
    boundary = np.full(repetitions, -1, dtype=np.int32)
    active = np.arange(repetitions)
    while active.size:
        route_ids = rng.choice(len(kernel.routes), size=active.size, p=kernel.probabilities)
        balances[active] += kernel.increments[route_ids]
        times[active] += 1
        depleted_mask = np.any(balances[active] == 0, axis=1)
        depleted_rows = active[depleted_mask]
        if depleted_rows.size:
            boundary[depleted_rows] = np.argmin(balances[depleted_rows], axis=1)
        active = active[~depleted_mask]
        if max_steps is not None and active.size and int(times[active].max()) >= max_steps:
            raise RuntimeError("max_steps reached before all trajectories depleted")
    return NetworkSample(times, boundary, seed)


def summarize_times(stopping_times: np.ndarray) -> TimeSummary:
    """Summarize finite stopping times with a normal 95% confidence interval."""
    values = np.asarray(stopping_times, dtype=np.float64).ravel()
    if values.size < 2 or not np.all(np.isfinite(values)):
        raise ValueError("at least two finite observations are required")
    mean = float(values.mean())
    sd = float(values.std(ddof=1))
    standard_error = sd / math.sqrt(values.size)
    margin = 1.959963984540054 * standard_error
    return TimeSummary(
        mean=mean,
        sd=sd,
        standard_error=standard_error,
        ci_low=mean - margin,
        ci_high=mean + margin,
    )
