"""Unified-request-clock warning calibration and equal-capital topology comparison."""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import tempfile
from typing import Iterable, Mapping

import numpy as np
import scipy
from scipy import stats

from network_model import HypergraphSpec, NetworkKernel
from network_simulation import validate_initial
from network_topologies import shortest_route_kernel


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "results" / "request-clock-topology-validation"
FIGURE_PATH = (
    ROOT
    / "outputs"
    / "researchwrite"
    / "hypergraph-stopping-time"
    / "figures"
    / "fig_request_clock_topology_validation.png"
)

EXPERIMENT_ID = "request-clock-equal-node-capital-20260731"
TOPOLOGY_ORDER = ("chain", "star", "branch")
SCALES = (10, 20, 40, 80)
HORIZONS = (1, 9, 45, 90)
STAGES = ("primary", "replication")
STAGE_SEEDS = {"primary": 2026073101, "replication": 2026073102}
FORMAL_REPETITIONS = 12_000
FORMAL_BLOCKS = 40
FAMILY_ALPHA = 0.05
MAX_REQUESTS = 2_000_000

TIME_FAMILY_SIZE = len(TOPOLOGY_ORDER) * len(SCALES) * 2
RISK_FAMILY_SIZE = len(TOPOLOGY_ORDER) * len(HORIZONS)
CALIBRATION_FAMILY_SIZE = len(TOPOLOGY_ORDER)
STAGE_COMPARISON_FAMILY_SIZE = TIME_FAMILY_SIZE + RISK_FAMILY_SIZE
CONTRAST_FAMILY_SIZE = math.comb(len(TOPOLOGY_ORDER), 2) * 2


@dataclass(frozen=True)
class RequestClockSample:
    """First-zero and first-balance-rejection times under one request clock."""

    scale: int
    repetitions: int
    seed: int
    hit_times: dict[str, np.ndarray]
    failure_times: dict[str, np.ndarray]
    hit_next_failure_probabilities: dict[str, np.ndarray]
    censored_count: int
    indexing_violations: int

    def lead_times(self, topology: str) -> np.ndarray:
        if topology not in self.hit_times:
            raise KeyError(topology)
        return self.failure_times[topology] - self.hit_times[topology]


def _topology_specs() -> dict[str, HypergraphSpec]:
    """Return the frozen topology set with equal per-node capital coefficients."""
    return {
        "chain": HypergraphSpec(
            (
                (0, 1, 2),
                (2, 3, 4),
                (4, 5, 6),
                (6, 7, 8),
            ),
            (10, 8, 8, 10),
        ),
        "star": HypergraphSpec(
            (
                (0, 1, 2),
                (0, 3, 4),
                (0, 5, 6),
                (0, 7, 8),
            ),
            (9, 9, 9, 9),
        ),
        "branch": HypergraphSpec(
            (
                (0, 1, 2),
                (2, 3, 4),
                (3, 5, 6),
                (4, 7, 8),
            ),
            (10, 6, 10, 10),
        ),
    }


def build_equal_capital_kernels() -> dict[str, NetworkKernel]:
    """Build zero-drift shortest-route kernels for the frozen fair design."""
    return {
        name: shortest_route_kernel(spec)
        for name, spec in _topology_specs().items()
    }


def equal_node_budget_initial(kernel: NetworkKernel, scale: int) -> np.ndarray:
    """Give every node total capital 4*scale, split equally across incident edges."""
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    nodes = sorted({node for edge in kernel.spec.edges for node in edge})
    degrees = {
        node: sum(node in edge for edge in kernel.spec.edges)
        for node in nodes
    }
    budget = 4 * scale
    values: list[int] = []
    for _, node in kernel.spec.coordinates:
        degree = degrees[node]
        value, remainder = divmod(budget, degree)
        if remainder:
            raise ValueError("per-node budget is not divisible by incidence degree")
        values.append(value)
    initial = validate_initial(kernel, scale, values)
    node_totals = {
        node: sum(
            int(value)
            for value, (_, coordinate_node) in zip(initial, kernel.spec.coordinates)
            if coordinate_node == node
        )
        for node in nodes
    }
    if set(node_totals.values()) != {budget}:
        raise RuntimeError("equal-node-capital construction failed")
    if int(initial.sum()) != 36 * scale:
        raise RuntimeError("network capital does not equal 36*scale")
    return initial


def ordered_pair_route_groups(
    kernel: NetworkKernel,
) -> dict[tuple[int, int], tuple[int, ...]]:
    """Group route indices by their ordered source-destination request."""
    groups: dict[tuple[int, int], list[int]] = {}
    for route_id, route in enumerate(kernel.routes):
        pair = (route.nodes[0], route.nodes[-1])
        groups.setdefault(pair, []).append(route_id)
    ordered = {
        pair: tuple(route_ids)
        for pair, route_ids in sorted(groups.items())
    }
    if len(ordered) != 72:
        raise ValueError("the fair design must contain all 72 ordered node pairs")
    for pair, route_ids in ordered.items():
        if pair[0] == pair[1]:
            raise ValueError("request endpoints must be distinct")
        mass = float(kernel.probabilities[list(route_ids)].sum())
        if not math.isclose(mass, 1.0 / 72.0, rel_tol=0.0, abs_tol=1e-14):
            raise ValueError("ordered-pair demand mass is not uniform")
        probabilities = kernel.probabilities[list(route_ids)]
        if not np.allclose(
            probabilities,
            np.full(len(route_ids), 1.0 / (72.0 * len(route_ids))),
            rtol=0.0,
            atol=1e-14,
        ):
            raise ValueError("shortest-route ties are not uniform")
    return ordered


def _route_choice_tables(
    kernels: Mapping[str, NetworkKernel],
) -> tuple[tuple[tuple[int, int], ...], dict[str, np.ndarray], dict[str, np.ndarray]]:
    pair_order: tuple[tuple[int, int], ...] | None = None
    counts: dict[str, np.ndarray] = {}
    tables: dict[str, np.ndarray] = {}
    for name in TOPOLOGY_ORDER:
        groups = ordered_pair_route_groups(kernels[name])
        pairs = tuple(groups)
        if pair_order is None:
            pair_order = pairs
        elif pairs != pair_order:
            raise ValueError("topologies do not share the same ordered-pair demand support")
        local_counts = np.asarray([len(groups[pair]) for pair in pairs], dtype=np.int32)
        maximum = int(local_counts.max())
        table = np.full((len(pairs), maximum), -1, dtype=np.int32)
        for pair_index, pair in enumerate(pairs):
            route_ids = groups[pair]
            table[pair_index, : len(route_ids)] = route_ids
        counts[name] = local_counts
        tables[name] = table
    assert pair_order is not None
    return pair_order, counts, tables


def _choose_route_ids(
    pair_indices: np.ndarray,
    tie_uniforms: np.ndarray,
    counts: np.ndarray,
    table: np.ndarray,
) -> np.ndarray:
    local_counts = counts[pair_indices]
    tie_indices = np.floor(tie_uniforms * local_counts).astype(np.int32)
    tie_indices = np.minimum(tie_indices, local_counts - 1)
    route_ids = table[pair_indices, tie_indices]
    if np.any(route_ids < 0):
        raise RuntimeError("invalid shortest-route tie lookup")
    return route_ids


def exact_next_failure_probabilities(
    states: np.ndarray,
    kernel: NetworkKernel,
    chunk_size: int = 1024,
) -> np.ndarray:
    """Return exact one-request balance-rejection probabilities for supplied states."""
    values = np.asarray(states, dtype=np.int32)
    if values.ndim != 2 or values.shape[1] != len(kernel.spec.coordinates):
        raise ValueError("states have the wrong shape")
    probabilities = np.empty(values.shape[0], dtype=np.float64)
    increments = kernel.increments.astype(np.int32, copy=False)
    for start in range(0, values.shape[0], chunk_size):
        stop = min(start + chunk_size, values.shape[0])
        candidate = values[start:stop, None, :] + increments[None, :, :]
        infeasible = np.any(candidate < 0, axis=2)
        probabilities[start:stop] = infeasible @ kernel.probabilities
    return probabilities


def simulate_matched_request_clock(
    kernels: Mapping[str, NetworkKernel],
    *,
    scale: int,
    repetitions: int,
    seed: int,
    max_requests: int = MAX_REQUESTS,
) -> RequestClockSample:
    """Drive all topologies with the same OD/tie stream until their first rejection."""
    if tuple(kernels) != TOPOLOGY_ORDER:
        raise ValueError("kernels must follow the frozen topology order")
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    if type(repetitions) is not int or repetitions <= 1:
        raise ValueError("repetitions must be an integer greater than one")
    if type(max_requests) is not int or max_requests <= 0:
        raise ValueError("max_requests must be a positive integer")

    _, counts, route_tables = _route_choice_tables(kernels)
    rng = np.random.default_rng(seed)
    balances = {
        name: np.repeat(
            equal_node_budget_initial(kernels[name], scale)[None, :],
            repetitions,
            axis=0,
        )
        for name in TOPOLOGY_ORDER
    }
    hit_times = {
        name: np.zeros(repetitions, dtype=np.int64)
        for name in TOPOLOGY_ORDER
    }
    failure_times = {
        name: np.zeros(repetitions, dtype=np.int64)
        for name in TOPOLOGY_ORDER
    }
    hit_next_failure_probabilities = {
        name: np.full(repetitions, np.nan, dtype=np.float64)
        for name in TOPOLOGY_ORDER
    }
    active = {
        name: np.ones(repetitions, dtype=bool)
        for name in TOPOLOGY_ORDER
    }

    request_clock = 0
    while any(np.any(active[name]) for name in TOPOLOGY_ORDER):
        request_clock += 1
        if request_clock > max_requests:
            censored = sum(int(np.count_nonzero(active[name])) for name in TOPOLOGY_ORDER)
            raise RuntimeError(
                f"max_requests reached with {censored} topology trajectories active"
            )
        union_mask = np.logical_or.reduce([active[name] for name in TOPOLOGY_ORDER])
        union_rows = np.flatnonzero(union_mask)
        pair_indices = rng.integers(0, 72, size=union_rows.size, dtype=np.int32)
        tie_uniforms = rng.random(union_rows.size)

        for name in TOPOLOGY_ORDER:
            rows = np.flatnonzero(active[name])
            if not rows.size:
                continue
            positions = np.searchsorted(union_rows, rows)
            route_ids = _choose_route_ids(
                pair_indices[positions],
                tie_uniforms[positions],
                counts[name],
                route_tables[name],
            )
            increments = kernels[name].increments[route_ids].astype(np.int32, copy=False)
            proposed = balances[name][rows] + increments
            feasible = np.all(proposed >= 0, axis=1)

            failed_rows = rows[~feasible]
            if failed_rows.size:
                failure_times[name][failed_rows] = request_clock
                active[name][failed_rows] = False

            accepted_rows = rows[feasible]
            if accepted_rows.size:
                accepted_states = proposed[feasible]
                balances[name][accepted_rows] = accepted_states
                new_hit_mask = (
                    hit_times[name][accepted_rows] == 0
                ) & np.any(accepted_states == 0, axis=1)
                new_hit_rows = accepted_rows[new_hit_mask]
                if new_hit_rows.size:
                    hit_times[name][new_hit_rows] = request_clock
                    hit_next_failure_probabilities[name][new_hit_rows] = (
                        exact_next_failure_probabilities(
                            balances[name][new_hit_rows], kernels[name]
                        )
                    )

    indexing_violations = sum(
        int(
            np.count_nonzero(
                (hit_times[name] <= 0)
                | (failure_times[name] <= hit_times[name])
                | ~np.isfinite(hit_next_failure_probabilities[name])
            )
        )
        for name in TOPOLOGY_ORDER
    )
    if indexing_violations:
        raise RuntimeError(f"request-clock indexing violations: {indexing_violations}")
    if any(np.any(balances[name] < 0) for name in TOPOLOGY_ORDER):
        raise RuntimeError("negative balance created by the request-clock simulator")

    return RequestClockSample(
        scale=scale,
        repetitions=repetitions,
        seed=seed,
        hit_times=hit_times,
        failure_times=failure_times,
        hit_next_failure_probabilities=hit_next_failure_probabilities,
        censored_count=0,
        indexing_violations=0,
    )


def _split_blocks(values: np.ndarray, blocks: int) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64).ravel()
    if type(blocks) is not int or blocks < 2 or array.size % blocks:
        raise ValueError("blocks must divide the trajectory count")
    return array.reshape(blocks, array.size // blocks)


def summarize_request_clock_sample(
    sample: RequestClockSample,
    *,
    scale: int,
    blocks: int,
) -> dict[str, object]:
    """Return path-level summaries and non-overlapping block means."""
    if scale != sample.scale:
        raise ValueError("summary scale does not match sample")
    normalizer = float((4 * scale) ** 2)
    cells: dict[str, dict[str, float | int]] = {}
    block_rows: list[dict[str, float | int | str]] = []
    for topology in TOPOLOGY_ORDER:
        hit = sample.hit_times[topology].astype(np.float64)
        failure = sample.failure_times[topology].astype(np.float64)
        lead = failure - hit
        p1_exact = sample.hit_next_failure_probabilities[topology]
        cells[topology] = {
            "repetitions": int(hit.size),
            "hit_mean": float(hit.mean()),
            "failure_mean": float(failure.mean()),
            "normalized_hit_mean": float(hit.mean() / normalizer),
            "normalized_failure_mean": float(failure.mean() / normalizer),
            "lead_mean": float(lead.mean()),
            "lead_q25": float(np.quantile(lead, 0.25)),
            "lead_median": float(np.quantile(lead, 0.5)),
            "lead_q75": float(np.quantile(lead, 0.75)),
            "lead_q90": float(np.quantile(lead, 0.9)),
            "exact_next_failure_probability_mean": float(p1_exact.mean()),
        }
        for horizon in HORIZONS:
            cells[topology][f"risk_h{horizon}"] = float(np.mean(lead <= horizon))

        hit_blocks = _split_blocks(hit / normalizer, blocks)
        failure_blocks = _split_blocks(failure / normalizer, blocks)
        lead_blocks = _split_blocks(lead, blocks)
        exact_blocks = _split_blocks(p1_exact, blocks)
        observed_one_blocks = _split_blocks((lead == 1).astype(np.float64), blocks)
        risk_blocks = {
            horizon: _split_blocks((lead <= horizon).astype(np.float64), blocks)
            for horizon in HORIZONS
        }
        for block in range(blocks):
            row: dict[str, float | int | str] = {
                "topology": topology,
                "scale": scale,
                "block": block,
                "trajectories": int(hit_blocks.shape[1]),
                "normalized_hit_mean": float(hit_blocks[block].mean()),
                "normalized_failure_mean": float(failure_blocks[block].mean()),
                "lead_mean": float(lead_blocks[block].mean()),
                "exact_p1_mean": float(exact_blocks[block].mean()),
                "observed_p1_mean": float(observed_one_blocks[block].mean()),
                "p1_calibration_difference": float(
                    observed_one_blocks[block].mean() - exact_blocks[block].mean()
                ),
            }
            for horizon in HORIZONS:
                row[f"risk_h{horizon}"] = float(risk_blocks[horizon][block].mean())
            block_rows.append(row)
    return {"cells": cells, "blocks": block_rows}


def _student_interval(
    block_values: Iterable[float],
    *,
    family_size: int,
    alpha: float = FAMILY_ALPHA,
) -> dict[str, float | int]:
    values = np.asarray(tuple(block_values), dtype=np.float64)
    if values.size < 2 or not np.all(np.isfinite(values)):
        raise ValueError("at least two finite block values are required")
    mean = float(values.mean())
    standard_error = float(values.std(ddof=1) / math.sqrt(values.size))
    multiplier = float(
        stats.t.ppf(1.0 - alpha / (2.0 * family_size), values.size - 1)
    )
    half_width = multiplier * standard_error
    return {
        "block_count": int(values.size),
        "mean": mean,
        "standard_error": standard_error,
        "simultaneous_multiplier": multiplier,
        "simultaneous_half_width": half_width,
        "simultaneous_ci_low": mean - half_width,
        "simultaneous_ci_high": mean + half_width,
        "family_size": family_size,
    }


def _welch_interval(
    primary: np.ndarray,
    replication: np.ndarray,
    *,
    family_size: int,
) -> dict[str, float | int | bool]:
    first = np.asarray(primary, dtype=np.float64)
    second = np.asarray(replication, dtype=np.float64)
    difference = float(second.mean() - first.mean())
    v1 = float(first.var(ddof=1) / first.size)
    v2 = float(second.var(ddof=1) / second.size)
    standard_error = math.sqrt(v1 + v2)
    degrees_freedom = (v1 + v2) ** 2 / (
        v1**2 / (first.size - 1) + v2**2 / (second.size - 1)
    )
    multiplier = float(
        stats.t.ppf(
            1.0 - FAMILY_ALPHA / (2.0 * family_size),
            degrees_freedom,
        )
    )
    half_width = multiplier * standard_error
    low, high = difference - half_width, difference + half_width
    return {
        "difference_replication_minus_primary": difference,
        "standard_error": standard_error,
        "degrees_freedom": degrees_freedom,
        "simultaneous_multiplier": multiplier,
        "simultaneous_half_width": half_width,
        "simultaneous_ci_low": low,
        "simultaneous_ci_high": high,
        "simultaneous_ci_contains_zero": bool(low <= 0.0 <= high),
        "family_size": family_size,
    }


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _atomic_write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    os.close(handle)
    temporary_path = Path(temporary)
    try:
        temporary_path.write_text(value, encoding="utf-8", newline="\n")
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _atomic_write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    handle, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    os.close(handle)
    temporary_path = Path(temporary)
    try:
        with temporary_path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _save_sample(path: Path, sample: RequestClockSample) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, np.ndarray] = {}
    for topology in TOPOLOGY_ORDER:
        payload[f"{topology}_hit"] = sample.hit_times[topology]
        payload[f"{topology}_failure"] = sample.failure_times[topology]
        payload[f"{topology}_exact_p1"] = sample.hit_next_failure_probabilities[topology]
    handle, temporary = tempfile.mkstemp(
        prefix=f".{path.stem}.", suffix=".npz", dir=path.parent
    )
    os.close(handle)
    temporary_path = Path(temporary)
    try:
        np.savez_compressed(temporary_path, **payload)
        temporary_path.replace(path)
    finally:
        temporary_path.unlink(missing_ok=True)


def _group_block_values(
    rows: list[dict[str, object]],
    *,
    stage: str,
    topology: str,
    scale: int,
    metric: str,
) -> np.ndarray:
    values = [
        float(row[metric])
        for row in rows
        if row["stage"] == stage
        and row["topology"] == topology
        and int(row["scale"]) == scale
    ]
    if not values:
        raise ValueError(f"missing block values for {stage}/{topology}/N{scale}/{metric}")
    return np.asarray(values, dtype=np.float64)


def _design_diagnostics(kernels: Mapping[str, NetworkKernel]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for topology in TOPOLOGY_ORDER:
        kernel = kernels[topology]
        initial = equal_node_budget_initial(kernel, 1)
        node_totals = {
            node: sum(
                int(value)
                for value, (_, coordinate_node) in zip(initial, kernel.spec.coordinates)
                if coordinate_node == node
            )
            for node in range(9)
        }
        groups = ordered_pair_route_groups(kernel)
        mean_hops = float(
            sum(
                kernel.probabilities[index] * len(route.edges)
                for index, route in enumerate(kernel.routes)
            )
        )
        maximum_drift = float(np.max(np.abs(kernel.drift)))
        rows.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "topology": topology,
                "node_count": 9,
                "edge_count": len(kernel.spec.edges),
                "coordinate_count": len(kernel.spec.coordinates),
                "capacity_units_json": _canonical_json(kernel.spec.capacity_units),
                "network_capital_units_per_scale": int(initial.sum()),
                "per_node_capital_units_per_scale_json": _canonical_json(node_totals),
                "ordered_pair_count": len(groups),
                "maximum_absolute_drift": maximum_drift,
                "mean_shortest_route_hops": mean_hops,
                "deterministic_gate_pass": bool(
                    len(kernel.spec.edges) == 4
                    and len(kernel.spec.coordinates) == 12
                    and int(initial.sum()) == 36
                    and set(node_totals.values()) == {4}
                    and len(groups) == 72
                    and maximum_drift <= 1e-14
                ),
            }
        )
    return rows


def _build_statistical_tables(
    *,
    samples: dict[tuple[str, int], RequestClockSample],
    block_rows: list[dict[str, object]],
    scales: tuple[int, ...],
    blocks: int,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    time_rows: list[dict[str, object]] = []
    risk_rows: list[dict[str, object]] = []
    lead_rows: list[dict[str, object]] = []
    comparison_rows: list[dict[str, object]] = []
    contrast_rows: list[dict[str, object]] = []

    for stage in STAGES:
        for topology in TOPOLOGY_ORDER:
            for scale in scales:
                for endpoint, metric in (
                    ("first_zero", "normalized_hit_mean"),
                    ("first_failure", "normalized_failure_mean"),
                ):
                    interval = _student_interval(
                        _group_block_values(
                            block_rows,
                            stage=stage,
                            topology=topology,
                            scale=scale,
                            metric=metric,
                        ),
                        family_size=len(TOPOLOGY_ORDER) * len(scales) * 2,
                    )
                    time_rows.append(
                        {
                            "experiment_id": EXPERIMENT_ID,
                            "stage": stage,
                            "topology": topology,
                            "scale": scale,
                            "endpoint": endpoint,
                            "normalizer": "(4*N)^2",
                            "trajectories": samples[(stage, scale)].repetitions,
                            **interval,
                        }
                    )

    maximum_scale = max(scales)
    for stage in STAGES:
        sample = samples[(stage, maximum_scale)]
        for topology in TOPOLOGY_ORDER:
            lead = sample.lead_times(topology).astype(np.float64)
            exact_p1 = sample.hit_next_failure_probabilities[topology]
            lead_rows.append(
                {
                    "experiment_id": EXPERIMENT_ID,
                    "stage": stage,
                    "topology": topology,
                    "scale": maximum_scale,
                    "trajectories": sample.repetitions,
                    "lead_mean": float(lead.mean()),
                    "lead_q25": float(np.quantile(lead, 0.25)),
                    "lead_median": float(np.quantile(lead, 0.5)),
                    "lead_q75": float(np.quantile(lead, 0.75)),
                    "lead_q90": float(np.quantile(lead, 0.9)),
                    "observed_p1": float(np.mean(lead == 1)),
                    "exact_state_averaged_p1": float(exact_p1.mean()),
                }
            )
            calibration = _student_interval(
                _group_block_values(
                    block_rows,
                    stage=stage,
                    topology=topology,
                    scale=maximum_scale,
                    metric="p1_calibration_difference",
                ),
                family_size=CALIBRATION_FAMILY_SIZE,
            )
            for horizon in HORIZONS:
                interval = _student_interval(
                    _group_block_values(
                        block_rows,
                        stage=stage,
                        topology=topology,
                        scale=maximum_scale,
                        metric=f"risk_h{horizon}",
                    ),
                    family_size=RISK_FAMILY_SIZE,
                )
                risk_rows.append(
                    {
                        "experiment_id": EXPERIMENT_ID,
                        "stage": stage,
                        "topology": topology,
                        "scale": maximum_scale,
                        "horizon_requests": horizon,
                        "trajectories": sample.repetitions,
                        **interval,
                        "p1_calibration_difference": calibration["mean"]
                        if horizon == 1
                        else "",
                        "p1_calibration_ci_low": calibration["simultaneous_ci_low"]
                        if horizon == 1
                        else "",
                        "p1_calibration_ci_high": calibration["simultaneous_ci_high"]
                        if horizon == 1
                        else "",
                    }
                )

    comparison_metrics: list[tuple[str, str, int, str]] = []
    for topology in TOPOLOGY_ORDER:
        for scale in scales:
            comparison_metrics.extend(
                [
                    (topology, "first_zero", scale, "normalized_hit_mean"),
                    (topology, "first_failure", scale, "normalized_failure_mean"),
                ]
            )
    for topology in TOPOLOGY_ORDER:
        for horizon in HORIZONS:
            comparison_metrics.append(
                (topology, f"risk_h{horizon}", maximum_scale, f"risk_h{horizon}")
            )
    for topology, endpoint, scale, metric in comparison_metrics:
        comparison = _welch_interval(
            _group_block_values(
                block_rows,
                stage="primary",
                topology=topology,
                scale=scale,
                metric=metric,
            ),
            _group_block_values(
                block_rows,
                stage="replication",
                topology=topology,
                scale=scale,
                metric=metric,
            ),
            family_size=len(comparison_metrics),
        )
        comparison_rows.append(
            {
                "experiment_id": EXPERIMENT_ID,
                "topology": topology,
                "scale": scale,
                "endpoint": endpoint,
                **comparison,
            }
        )

    stage_agreement = all(
        bool(row["simultaneous_ci_contains_zero"]) for row in comparison_rows
    )
    if stage_agreement:
        for topology in TOPOLOGY_ORDER:
            for scale in scales:
                for endpoint, metric in (
                    ("first_zero", "normalized_hit_mean"),
                    ("first_failure", "normalized_failure_mean"),
                ):
                    combined = np.concatenate(
                        [
                            _group_block_values(
                                block_rows,
                                stage=stage,
                                topology=topology,
                                scale=scale,
                                metric=metric,
                            )
                            for stage in STAGES
                        ]
                    )
                    interval = _student_interval(
                        combined,
                        family_size=len(TOPOLOGY_ORDER) * len(scales) * 2,
                    )
                    time_rows.append(
                        {
                            "experiment_id": EXPERIMENT_ID,
                            "stage": "pooled",
                            "topology": topology,
                            "scale": scale,
                            "endpoint": endpoint,
                            "normalizer": "(4*N)^2",
                            "trajectories": sum(
                                samples[(stage, scale)].repetitions for stage in STAGES
                            ),
                            **interval,
                        }
                    )

        for topology in TOPOLOGY_ORDER:
            pooled_lead = np.concatenate(
                [
                    samples[(stage, maximum_scale)].lead_times(topology)
                    for stage in STAGES
                ]
            ).astype(np.float64)
            pooled_exact = np.concatenate(
                [
                    samples[(stage, maximum_scale)].hit_next_failure_probabilities[
                        topology
                    ]
                    for stage in STAGES
                ]
            )
            lead_rows.append(
                {
                    "experiment_id": EXPERIMENT_ID,
                    "stage": "pooled",
                    "topology": topology,
                    "scale": maximum_scale,
                    "trajectories": int(pooled_lead.size),
                    "lead_mean": float(pooled_lead.mean()),
                    "lead_q25": float(np.quantile(pooled_lead, 0.25)),
                    "lead_median": float(np.quantile(pooled_lead, 0.5)),
                    "lead_q75": float(np.quantile(pooled_lead, 0.75)),
                    "lead_q90": float(np.quantile(pooled_lead, 0.9)),
                    "observed_p1": float(np.mean(pooled_lead == 1)),
                    "exact_state_averaged_p1": float(pooled_exact.mean()),
                }
            )
            for horizon in HORIZONS:
                combined = np.concatenate(
                    [
                        _group_block_values(
                            block_rows,
                            stage=stage,
                            topology=topology,
                            scale=maximum_scale,
                            metric=f"risk_h{horizon}",
                        )
                        for stage in STAGES
                    ]
                )
                interval = _student_interval(
                    combined,
                    family_size=RISK_FAMILY_SIZE,
                )
                risk_rows.append(
                    {
                        "experiment_id": EXPERIMENT_ID,
                        "stage": "pooled",
                        "topology": topology,
                        "scale": maximum_scale,
                        "horizon_requests": horizon,
                        "trajectories": sum(
                            samples[(stage, maximum_scale)].repetitions
                            for stage in STAGES
                        ),
                        **interval,
                        "p1_calibration_difference": "",
                        "p1_calibration_ci_low": "",
                        "p1_calibration_ci_high": "",
                    }
                )

        topology_pairs = [
            (TOPOLOGY_ORDER[left], TOPOLOGY_ORDER[right])
            for left in range(len(TOPOLOGY_ORDER))
            for right in range(left + 1, len(TOPOLOGY_ORDER))
        ]
        for endpoint, attribute in (
            ("first_zero", "hit_times"),
            ("first_failure", "failure_times"),
        ):
            for first_name, second_name in topology_pairs:
                block_differences: list[float] = []
                raw_differences: list[np.ndarray] = []
                for stage in STAGES:
                    sample = samples[(stage, maximum_scale)]
                    first = getattr(sample, attribute)[first_name].astype(np.float64)
                    second = getattr(sample, attribute)[second_name].astype(np.float64)
                    differences = (first - second) / float((4 * maximum_scale) ** 2)
                    raw_differences.append(differences)
                    block_differences.extend(
                        _split_blocks(differences, blocks).mean(axis=1).tolist()
                    )
                interval = _student_interval(
                    block_differences,
                    family_size=CONTRAST_FAMILY_SIZE,
                )
                contrast_rows.append(
                    {
                        "experiment_id": EXPERIMENT_ID,
                        "stage": "pooled",
                        "scale": maximum_scale,
                        "endpoint": endpoint,
                        "contrast": f"{first_name}_minus_{second_name}",
                        "first_topology": first_name,
                        "second_topology": second_name,
                        "paired_trajectory_bundles": int(
                            sum(array.size for array in raw_differences)
                        ),
                        **interval,
                        "resolved_direction": "positive"
                        if float(interval["simultaneous_ci_low"]) > 0.0
                        else "negative"
                        if float(interval["simultaneous_ci_high"]) < 0.0
                        else "unresolved",
                    }
                )

    return time_rows, risk_rows, lead_rows, comparison_rows, contrast_rows


def _evaluate_gates(
    *,
    diagnostics: list[dict[str, object]],
    samples: dict[tuple[str, int], RequestClockSample],
    time_rows: list[dict[str, object]],
    risk_rows: list[dict[str, object]],
    comparison_rows: list[dict[str, object]],
    scales: tuple[int, ...],
) -> dict[str, bool]:
    nonpooled_time = [row for row in time_rows if row["stage"] in STAGES]
    nonpooled_risk = [row for row in risk_rows if row["stage"] in STAGES]
    calibration_rows = [
        row
        for row in nonpooled_risk
        if int(row["horizon_requests"]) == 1
    ]
    return {
        "deterministic_equal_capital_and_demand": all(
            bool(row["deterministic_gate_pass"]) for row in diagnostics
        ),
        "zero_censoring_and_indexing_violations": all(
            sample.censored_count == 0 and sample.indexing_violations == 0
            for sample in samples.values()
        ),
        "risk_precision": max(
            float(row["simultaneous_half_width"]) for row in nonpooled_risk
        )
        <= 0.03,
        "time_precision": max(
            float(row["simultaneous_half_width"]) for row in nonpooled_time
        )
        <= 0.03,
        "independent_stage_agreement": len(comparison_rows)
        == len(TOPOLOGY_ORDER) * (len(scales) * 2 + len(HORIZONS))
        and all(
            bool(row["simultaneous_ci_contains_zero"])
            for row in comparison_rows
        ),
        "exact_p1_calibration": all(
            float(row["p1_calibration_ci_low"]) <= 0.0
            <= float(row["p1_calibration_ci_high"])
            for row in calibration_rows
        ),
        "pooled_outputs_permitted": any(row["stage"] == "pooled" for row in time_rows)
        and any(row["stage"] == "pooled" for row in risk_rows),
    }


def run_request_clock_validation(
    *,
    result_dir: Path = RESULT_DIR,
    quick: bool = False,
    repetitions: int | None = None,
    max_requests: int = MAX_REQUESTS,
) -> dict[str, object]:
    """Run both independent stages, write raw/results, and return metadata."""
    kernels = build_equal_capital_kernels()
    diagnostics = _design_diagnostics(kernels)
    scales = (2, 4) if quick else SCALES
    actual_repetitions = repetitions or (400 if quick else FORMAL_REPETITIONS)
    blocks = 20 if quick else FORMAL_BLOCKS
    if actual_repetitions % blocks:
        raise ValueError("repetitions must be divisible by the block count")

    result_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = result_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    samples: dict[tuple[str, int], RequestClockSample] = {}
    block_rows: list[dict[str, object]] = []
    cell_rows: list[dict[str, object]] = []
    for stage_index, stage in enumerate(STAGES):
        for scale in scales:
            seed = STAGE_SEEDS[stage] + 1000 * scale + 100_000 * stage_index
            sample = simulate_matched_request_clock(
                kernels,
                scale=scale,
                repetitions=actual_repetitions,
                seed=seed,
                max_requests=max_requests,
            )
            samples[(stage, scale)] = sample
            _save_sample(raw_dir / f"{stage}-N{scale}.npz", sample)
            summary = summarize_request_clock_sample(
                sample,
                scale=scale,
                blocks=blocks,
            )
            for topology, values in summary["cells"].items():
                cell_rows.append(
                    {
                        "experiment_id": EXPERIMENT_ID,
                        "stage": stage,
                        "topology": topology,
                        "scale": scale,
                        "seed": seed,
                        **values,
                        "censored_count": sample.censored_count,
                        "indexing_violations": sample.indexing_violations,
                    }
                )
            for row in summary["blocks"]:
                block_rows.append(
                    {
                        "experiment_id": EXPERIMENT_ID,
                        "stage": stage,
                        "seed": seed,
                        **row,
                    }
                )

    (
        time_rows,
        risk_rows,
        lead_rows,
        comparison_rows,
        contrast_rows,
    ) = _build_statistical_tables(
        samples=samples,
        block_rows=block_rows,
        scales=scales,
        blocks=blocks,
    )
    gates = _evaluate_gates(
        diagnostics=diagnostics,
        samples=samples,
        time_rows=time_rows,
        risk_rows=risk_rows,
        comparison_rows=comparison_rows,
        scales=scales,
    )
    status = "PASS" if all(gates.values()) else "FAIL"

    _atomic_write_csv(result_dir / "request-clock-design-diagnostics.csv", diagnostics)
    _atomic_write_csv(result_dir / "request-clock-cell-summaries.csv", cell_rows)
    _atomic_write_csv(result_dir / "request-clock-block-means.csv", block_rows)
    _atomic_write_csv(result_dir / "request-clock-time-summary.csv", time_rows)
    _atomic_write_csv(result_dir / "request-clock-warning-risk.csv", risk_rows)
    _atomic_write_csv(result_dir / "request-clock-lead-summary.csv", lead_rows)
    _atomic_write_csv(result_dir / "request-clock-stage-comparisons.csv", comparison_rows)
    if contrast_rows:
        _atomic_write_csv(result_dir / "request-clock-topology-contrasts.csv", contrast_rows)

    metadata: dict[str, object] = {
        "experiment_id": EXPERIMENT_ID,
        "status": status,
        "quick": quick,
        "design": {
            "topologies": list(TOPOLOGY_ORDER),
            "node_count": 9,
            "edge_count": 4,
            "per_node_capital_units": "4*N",
            "network_capital_units": "36*N",
            "scales": list(scales),
            "ordered_pair_demand": "uniform over 72 ordered source-destination pairs",
            "routing": "uniform over shortest hypergraph route ties",
            "request_clock": "accepted and rejected requests both count; rejected requests do not update balances",
            "failure_event": "first fixed-route balance rejection after first accepted request reaches zero",
            "horizons": list(HORIZONS),
        },
        "sampling": {
            "stages": list(STAGES),
            "repetitions_per_scale_stage": actual_repetitions,
            "blocks_per_scale_stage_topology": blocks,
            "stage_seeds": STAGE_SEEDS,
            "maximum_requests_failure_guard": max_requests,
            "censoring": "none permitted",
        },
        "statistics": {
            "risk_family_size": RISK_FAMILY_SIZE,
            "time_family_size": len(TOPOLOGY_ORDER) * len(scales) * 2,
            "stage_comparison_family_size": len(comparison_rows),
            "topology_contrast_family_size": CONTRAST_FAMILY_SIZE,
            "familywise_alpha": FAMILY_ALPHA,
            "independent_unit": "one common OD/tie request stream driving all three topologies",
        },
        "gates": gates,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
        "claim_boundary": (
            "finite-design calibration of fixed-route balance rejection under unit requests; "
            "not global route unavailability and not empirical Lightning failure prediction"
        ),
    }
    _atomic_write_text(
        result_dir / "request-clock-metadata.json",
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
    )
    return metadata


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_sha256_manifest(
    *,
    result_dir: Path = RESULT_DIR,
    figure_path: Path = FIGURE_PATH,
) -> None:
    """Hash all published results and the single PNG using repository-relative paths."""
    paths = sorted(
        path
        for path in result_dir.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS.txt"
    )
    if figure_path.exists():
        paths.append(figure_path)
    lines = [
        f"{_sha256(path)}  {path.relative_to(ROOT).as_posix()}"
        for path in paths
    ]
    _atomic_write_text(result_dir / "SHA256SUMS.txt", "\n".join(lines) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    parser.add_argument("--result-dir", type=Path, default=RESULT_DIR)
    parser.add_argument("--skip-plot", action="store_true")
    args = parser.parse_args()
    metadata = run_request_clock_validation(
        result_dir=args.result_dir,
        quick=args.quick,
        repetitions=args.repetitions,
        max_requests=args.max_requests,
    )
    if not args.skip_plot:
        from plot_request_clock_topology_validation import render_figure

        render_figure(result_dir=args.result_dir, output_path=FIGURE_PATH)
        write_sha256_manifest(result_dir=args.result_dir, figure_path=FIGURE_PATH)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    if metadata["status"] != "PASS":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
