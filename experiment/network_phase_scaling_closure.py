"""Frozen finite-scale audit for the stopping-time phase diagram.

The experiment is specified in
``41_phase_scaling_and_higher_order_figure_contract_2026-07-28.md``.
It deliberately keeps trajectory-level artifacts, uses two disjoint seed sets,
and writes every derived statistic from the saved raw arrays.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import time
from typing import Iterable

import numpy as np
import scipy
from scipy import stats

from network_model import (
    NetworkKernel,
    perturb_route_probabilities,
    two_overlapping_triads_uniform,
    validate_phase_kernel,
)
from network_simulation import NetworkSample, initial_balances


EXPERIMENT_ID = "network-phase-closure-20260728"
PIPELINE_VERSION = "1.0"
MASTER_SEED = 202607280000
AMPLITUDE = 0.40
FULL_REPETITIONS = 8000
BLOCK_COUNT = 40
BOOTSTRAP_REPETITIONS = 10000
CHUNK_STEPS = 128
FAMILY_ALPHA = 0.05


@dataclass(frozen=True)
class Regime:
    key: str
    label_cn: str
    regime_id: int
    alpha: float | None
    scales: tuple[int, ...]
    theoretical_exponent: float


REGIMES = (
    Regime("zero", "零漂移基线", 0, None, (25, 50, 100, 200, 400), 2.0),
    Regime("drift", "漂移主导", 1, 0.5, (100, 200, 400, 800, 1600), 1.5),
    Regime("critical", "临界扩散", 2, 1.0, (25, 50, 100, 200, 400), 2.0),
    Regime("fair", "公平扩散", 3, 2.0, (25, 50, 100, 200, 400), 2.0),
)

STAGE_NAMES = ("primary", "replication")
FORWARD_NODES = (0, 2, 3)
REVERSE_NODES = (3, 2, 0)


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _kernel_sha256(kernel: NetworkKernel) -> str:
    payload = {
        "edges": [list(edge) for edge in kernel.spec.edges],
        "capacity_units": list(kernel.spec.capacity_units),
        "routes": [
            {"nodes": list(route.nodes), "edges": list(route.edges)}
            for route in kernel.routes
        ],
        "probabilities_hex": [float(value).hex() for value in kernel.probabilities],
        "increments": kernel.increments.astype(int).tolist(),
    }
    return _sha256_bytes(_canonical_json(payload).encode("utf-8"))


def find_reverse_route_pair(kernel: NetworkKernel) -> tuple[int, int]:
    """Return the frozen forward and reverse route indices."""
    forward = [i for i, route in enumerate(kernel.routes) if route.nodes == FORWARD_NODES]
    reverse = [i for i, route in enumerate(kernel.routes) if route.nodes == REVERSE_NODES]
    if len(forward) != 1 or len(reverse) != 1:
        raise ValueError("frozen forward/reverse route pair is not unique")
    return forward[0], reverse[0]


def cell_seed(stage_index: int, regime_id: int, scale: int) -> int:
    """Return the seed frozen in the experiment contract."""
    if stage_index not in (0, 1):
        raise ValueError("stage_index must be zero or one")
    if regime_id not in range(4):
        raise ValueError("regime_id must be in {0,1,2,3}")
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    return MASTER_SEED + 1_000_000 * stage_index + 10_000 * regime_id + scale


def build_phase_kernel(regime: Regime, scale: int) -> NetworkKernel:
    """Build exactly one cell kernel from the frozen triangular array."""
    base = two_overlapping_triads_uniform()
    if regime.alpha is None:
        return base
    forward, reverse = find_reverse_route_pair(base)
    return perturb_route_probabilities(
        base=base,
        scale=scale,
        alpha=regime.alpha,
        forward_index=forward,
        reverse_index=reverse,
        amplitude=AMPLITUDE,
    )


def _raw_second_moment(kernel: NetworkKernel) -> np.ndarray:
    increments = kernel.increments.astype(np.float64)
    return increments.T @ (increments * kernel.probabilities[:, None])


def kernel_diagnostics(regime: Regime, scale: int, kernel: NetworkKernel) -> dict[str, object]:
    """Evaluate all deterministic implementation gates for one cell."""
    base = two_overlapping_triads_uniform()
    forward, reverse = find_reverse_route_pair(base)
    zeta = base.increments[forward].astype(np.float64)
    reverse_error = float(
        np.max(np.abs(base.increments[forward] + base.increments[reverse]))
    )
    probability_sum_error = abs(float(kernel.probabilities.sum()) - 1.0)
    minimum_probability = float(kernel.probabilities.min())
    if regime.alpha is None:
        expected_scaled_drift = np.zeros_like(zeta)
        scaled_drift = np.zeros_like(zeta)
    else:
        expected_scaled_drift = 2.0 * AMPLITUDE * zeta
        # Evaluate the perturbation contrast in extended precision.  A direct
        # float64 dot product first cancels twenty O(1) baseline terms and then
        # multiplies the O(N^-alpha) remainder by N^alpha; that diagnostic is
        # needlessly ill-conditioned for alpha=2.  The contrast below audits
        # the probabilities actually supplied to the simulator while removing
        # the analytically zero uniform baseline before scaling.
        probability_contrast = (
            kernel.probabilities.astype(np.longdouble)
            - base.probabilities.astype(np.longdouble)
        )
        scaled_drift = np.asarray(
            (probability_contrast @ kernel.increments.astype(np.longdouble))
            * np.longdouble(scale) ** np.longdouble(regime.alpha),
            dtype=np.float64,
        )
    scaled_drift_error = float(np.max(np.abs(scaled_drift - expected_scaled_drift)))
    float64_scaled_drift_error = (
        0.0
        if regime.alpha is None
        else float(
            np.max(
                np.abs(scale ** regime.alpha * kernel.drift - expected_scaled_drift)
            )
        )
    )
    raw_second_moment_error = float(
        np.max(np.abs(_raw_second_moment(kernel) - _raw_second_moment(base)))
    )
    expected_covariance = base.covariance - np.outer(kernel.drift, kernel.drift)
    covariance_identity_error = float(
        np.max(np.abs(kernel.covariance - expected_covariance))
    )
    minimum_normal_variance = float(np.diag(kernel.covariance).min())
    validate_phase_kernel(kernel)
    starting = initial_balances(kernel, scale)
    initial_scale_error = float(np.max(np.abs(starting / float(scale) - 1.0)))
    capacity_errors = []
    for edge_index, capacity_unit in enumerate(kernel.spec.capacity_units):
        block = starting[kernel.edge_slice(edge_index)]
        capacity_errors.append(abs(int(block.sum()) - scale * capacity_unit))
    initial_capacity_error = int(max(capacity_errors, default=0))
    deterministic_gate_pass = bool(
        reverse_error == 0.0
        and probability_sum_error <= 1e-14
        and minimum_probability > 0.0
        and scaled_drift_error <= 1e-12
        and raw_second_moment_error <= 1e-12
        and covariance_identity_error <= 1e-12
        and minimum_normal_variance > 0.0
        and initial_scale_error <= 1e-12
        and initial_capacity_error == 0
    )
    return {
        "experiment_id": EXPERIMENT_ID,
        "pipeline_version": PIPELINE_VERSION,
        "regime": regime.key,
        "regime_label_cn": regime.label_cn,
        "regime_id": regime.regime_id,
        "alpha": "" if regime.alpha is None else regime.alpha,
        "scale": scale,
        "amplitude": 0.0 if regime.alpha is None else AMPLITUDE,
        "forward_route": "0->2->3",
        "reverse_route": "3->2->0",
        "kernel_sha256": _kernel_sha256(kernel),
        "minimum_probability": minimum_probability,
        "probability_sum_error": probability_sum_error,
        "reverse_increment_error": reverse_error,
        "scaled_drift_vector_json": _canonical_json(scaled_drift.tolist()),
        "expected_scaled_drift_vector_json": _canonical_json(expected_scaled_drift.tolist()),
        "scaled_drift_error": scaled_drift_error,
        "float64_direct_scaled_drift_error": float64_scaled_drift_error,
        "raw_second_moment_error": raw_second_moment_error,
        "covariance_identity_error": covariance_identity_error,
        "minimum_normal_variance": minimum_normal_variance,
        "initial_scale_error": initial_scale_error,
        "initial_capacity_error": initial_capacity_error,
        "deterministic_gate_pass": deterministic_gate_pass,
    }


def normalizer(regime: Regime, scale: int) -> float:
    if regime.alpha == 0.5:
        return float((1.0 / (2.0 * AMPLITUDE)) * scale ** 1.5)
    return float(scale**2)


def simulate_network_chunked(
    kernel: NetworkKernel,
    scale: int,
    repetitions: int,
    seed: int,
    *,
    chunk_steps: int = CHUNK_STEPS,
) -> NetworkSample:
    """Simulate exact first zero hits using vectorized finite path chunks.

    Random route labels remain i.i.d.  Drawing a chunk for every currently
    active trajectory only discards labels after that trajectory's first hit;
    it does not change any retained path distribution.  Unit increments imply
    that a coordinate cannot cross from positive to negative without first
    equalling zero, so scanning every state inside the chunk preserves the
    stopping event exactly.
    """
    if type(repetitions) is not int or repetitions <= 1:
        raise ValueError("repetitions must be an integer greater than one")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    if type(chunk_steps) is not int or chunk_steps <= 0:
        raise ValueError("chunk_steps must be a positive integer")
    starting = initial_balances(kernel, scale)
    balances = np.repeat(starting[None, :], repetitions, axis=0)
    stopping_times = np.zeros(repetitions, dtype=np.int64)
    boundary_coordinates = np.full(repetitions, -1, dtype=np.int32)
    active = np.arange(repetitions, dtype=np.int64)
    rng = np.random.default_rng(seed)
    while active.size:
        route_ids = rng.choice(
            len(kernel.routes),
            size=(active.size, chunk_steps),
            p=kernel.probabilities,
        )
        states = np.cumsum(
            kernel.increments[route_ids], axis=1, dtype=np.int32
        )
        states += balances[active, None, :]
        depleted = np.any(states == 0, axis=2)
        hit_mask = np.any(depleted, axis=1)
        if np.any(hit_mask):
            local_hits = np.flatnonzero(hit_mask)
            first_offsets = np.argmax(depleted[hit_mask], axis=1)
            global_hits = active[local_hits]
            hit_states = states[local_hits, first_offsets]
            stopping_times[global_hits] += first_offsets.astype(np.int64) + 1
            boundary_coordinates[global_hits] = np.argmin(hit_states, axis=1)
        survivor_mask = ~hit_mask
        if np.any(survivor_mask):
            global_survivors = active[survivor_mask]
            balances[global_survivors] = states[survivor_mask, -1]
            stopping_times[global_survivors] += chunk_steps
            active = global_survivors
        else:
            active = np.empty(0, dtype=np.int64)
    return NetworkSample(stopping_times, boundary_coordinates, seed)


def summarize_cell(
    *,
    regime: Regime,
    scale: int,
    stopping_times: np.ndarray,
    boundary_coordinates: np.ndarray,
    stage: str,
    seed: int,
    block_count: int,
    family_size: int,
) -> tuple[dict[str, object], list[dict[str, object]]]:
    """Summarize one raw cell using non-overlapping trajectory blocks."""
    values = np.asarray(stopping_times, dtype=np.int64).ravel()
    boundaries = np.asarray(boundary_coordinates, dtype=np.int32).ravel()
    if values.size < 2 or values.size != boundaries.size:
        raise ValueError("stopping times and boundary coordinates must have equal nontrivial size")
    if block_count < 2 or values.size % block_count:
        raise ValueError("block_count must divide the trajectory count")
    if np.any(values <= 0) or not np.all(np.isfinite(values)):
        raise ValueError("stopping times must be finite and positive")
    censored_count = int(np.count_nonzero(boundaries < 0))
    if censored_count:
        raise ValueError("boundary coordinate audit detected censored trajectories")
    block_size = values.size // block_count
    norm = normalizer(regime, scale)
    block_means = values.astype(np.float64).reshape(block_count, block_size).mean(axis=1)
    normalized_blocks = block_means / norm
    normalized_se = float(normalized_blocks.std(ddof=1) / math.sqrt(block_count))
    multiplier = float(stats.t.ppf(1.0 - FAMILY_ALPHA / (2.0 * family_size), block_count - 1))
    normalized_mean = float(values.mean() / norm)
    half_width = multiplier * normalized_se
    q10, q50, q90 = (float(value) for value in np.quantile(values, (0.1, 0.5, 0.9)))
    relative_width = (q90 - q10) / (2.0 * q50)
    if regime.alpha == 0.5:
        relative_deviation_probability = float(np.mean(np.abs(values / norm - 1.0) > 0.30))
    else:
        relative_deviation_probability = float("nan")
    counts = np.bincount(boundaries, minlength=values.ndim + 6)[:6]
    summary = {
        "experiment_id": EXPERIMENT_ID,
        "stage": stage,
        "regime": regime.key,
        "regime_label_cn": regime.label_cn,
        "regime_id": regime.regime_id,
        "alpha": "" if regime.alpha is None else regime.alpha,
        "scale": scale,
        "amplitude": 0.0 if regime.alpha is None else AMPLITUDE,
        "seed": seed,
        "repetitions": int(values.size),
        "block_count": block_count,
        "block_size": block_size,
        "mean_tau": float(values.mean()),
        "sd_tau": float(values.std(ddof=1)),
        "se_tau": float(values.std(ddof=1) / math.sqrt(values.size)),
        "q10_tau": q10,
        "q50_tau": q50,
        "q90_tau": q90,
        "normalizer": norm,
        "normalizer_type": "1.25*N^1.5" if regime.alpha == 0.5 else "N^2",
        "normalized_mean": normalized_mean,
        "normalized_se_blocks": normalized_se,
        "simultaneous_multiplier": multiplier,
        "normalized_ci_low": normalized_mean - half_width,
        "normalized_ci_high": normalized_mean + half_width,
        "normalized_ci_half_width": half_width,
        "relative_interdecile_width": relative_width,
        "relative_deviation_probability_30pct": relative_deviation_probability,
        "maximum_stopping_time": int(values.max()),
        "minimum_stopping_time": int(values.min()),
        "censored_count": censored_count,
        "nan_count": 0,
        "excluded_count": 0,
        "boundary_counts_json": _canonical_json(counts.astype(int).tolist()),
        "theoretical_exponent": regime.theoretical_exponent,
    }
    block_rows = [
        {
            "experiment_id": EXPERIMENT_ID,
            "stage": stage,
            "regime": regime.key,
            "alpha": "" if regime.alpha is None else regime.alpha,
            "scale": scale,
            "seed": seed,
            "block": block_index,
            "block_size": block_size,
            "mean_tau": float(block_mean),
            "normalized_mean": float(block_mean / norm),
        }
        for block_index, block_mean in enumerate(block_means)
    ]
    return summary, block_rows


def _write_csv(path: Path, rows: Iterable[dict[str, object]]) -> None:
    materialized = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not materialized:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in materialized:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(materialized)


def _save_raw_atomic(
    path: Path,
    *,
    stopping_times: np.ndarray,
    boundary_coordinates: np.ndarray,
    seed: int,
    stage: str,
    regime: Regime,
    scale: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp.npz")
    np.savez_compressed(
        temporary,
        stopping_times=np.asarray(stopping_times, dtype=np.int64),
        boundary_coordinates=np.asarray(boundary_coordinates, dtype=np.int32),
        seed=np.asarray(seed, dtype=np.int64),
        stage=np.asarray(stage),
        regime=np.asarray(regime.key),
        alpha=np.asarray(np.nan if regime.alpha is None else regime.alpha),
        scale=np.asarray(scale, dtype=np.int64),
        experiment_id=np.asarray(EXPERIMENT_ID),
    )
    os.replace(temporary, path)


def _load_or_simulate_cell(
    *,
    output_dir: Path,
    stage: str,
    stage_index: int,
    regime: Regime,
    scale: int,
    repetitions: int,
) -> tuple[np.ndarray, np.ndarray, int, Path, bool, float]:
    seed = cell_seed(stage_index, regime.regime_id, scale)
    raw_path = output_dir / "raw" / f"{stage}__{regime.key}__N{scale}.npz"
    if raw_path.exists():
        with np.load(raw_path, allow_pickle=False) as payload:
            times = payload["stopping_times"].astype(np.int64, copy=True)
            boundaries = payload["boundary_coordinates"].astype(np.int32, copy=True)
            saved_seed = int(payload["seed"])
            saved_stage = str(payload["stage"])
            saved_regime = str(payload["regime"])
            saved_scale = int(payload["scale"])
            saved_experiment = str(payload["experiment_id"])
        if (
            saved_seed != seed
            or saved_stage != stage
            or saved_regime != regime.key
            or saved_scale != scale
            or saved_experiment != EXPERIMENT_ID
            or times.size != repetitions
        ):
            raise ValueError(f"existing raw artifact does not match frozen cell: {raw_path}")
        return times, boundaries, seed, raw_path, True, 0.0
    kernel = build_phase_kernel(regime, scale)
    started = time.perf_counter()
    sample = simulate_network_chunked(
        kernel, scale, repetitions, seed=seed, chunk_steps=CHUNK_STEPS
    )
    elapsed = time.perf_counter() - started
    _save_raw_atomic(
        raw_path,
        stopping_times=sample.stopping_times,
        boundary_coordinates=sample.boundary_coordinates,
        seed=seed,
        stage=stage,
        regime=regime,
        scale=scale,
    )
    return (
        sample.stopping_times,
        sample.boundary_coordinates,
        seed,
        raw_path,
        False,
        elapsed,
    )


def run_stage(
    *,
    output_dir: Path,
    stage: str,
    repetitions: int,
    block_count: int,
    regimes: tuple[Regime, ...] = REGIMES,
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    """Run or resume one complete stage and persist derived CSVs."""
    if stage not in STAGE_NAMES:
        raise ValueError(f"stage must be one of {STAGE_NAMES}")
    if repetitions <= 1 or repetitions % block_count:
        raise ValueError("repetitions must exceed one and be divisible by block_count")
    stage_index = STAGE_NAMES.index(stage)
    cell_count = sum(len(regime.scales) for regime in regimes)
    summaries: list[dict[str, object]] = []
    block_rows: list[dict[str, object]] = []
    diagnostics: list[dict[str, object]] = []
    for regime in regimes:
        for scale in regime.scales:
            kernel = build_phase_kernel(regime, scale)
            diagnostic = kernel_diagnostics(regime, scale, kernel)
            if not diagnostic["deterministic_gate_pass"]:
                raise RuntimeError(f"deterministic kernel gate failed for {regime.key}, N={scale}")
            times, boundaries, seed, raw_path, reused, elapsed = _load_or_simulate_cell(
                output_dir=output_dir,
                stage=stage,
                stage_index=stage_index,
                regime=regime,
                scale=scale,
                repetitions=repetitions,
            )
            summary, blocks = summarize_cell(
                regime=regime,
                scale=scale,
                stopping_times=times,
                boundary_coordinates=boundaries,
                stage=stage,
                seed=seed,
                block_count=block_count,
                family_size=cell_count,
            )
            summary["raw_artifact"] = raw_path.relative_to(output_dir).as_posix()
            summary["raw_result_sha256"] = _sha256_file(raw_path)
            summary["reused_existing_raw"] = reused
            summary["simulation_elapsed_seconds"] = elapsed
            summaries.append(summary)
            block_rows.extend(blocks)
            diagnostic.update({"stage": stage, "seed": seed, "repetitions": repetitions})
            diagnostics.append(diagnostic)
            _write_csv(output_dir / f"{stage}-cell-summaries.csv", summaries)
            _write_csv(output_dir / f"{stage}-block-means.csv", block_rows)
            _write_csv(output_dir / f"{stage}-kernel-diagnostics.csv", diagnostics)
            print(
                f"[{stage}] {regime.key} N={scale}: mean={summary['mean_tau']:.6g}, "
                f"normalized={summary['normalized_mean']:.6g}, "
                f"half-width={summary['normalized_ci_half_width']:.4g}, "
                f"{'reused' if reused else f'{elapsed:.1f}s'}",
                flush=True,
            )
    return summaries, block_rows, diagnostics


def _group_blocks(
    block_rows: list[dict[str, object]], stage: str, regime: str, scale: int
) -> np.ndarray:
    values = [
        float(row["mean_tau"])
        for row in block_rows
        if row["stage"] == stage and row["regime"] == regime and int(row["scale"]) == scale
    ]
    if not values:
        raise ValueError(f"missing block means for {stage}, {regime}, N={scale}")
    return np.asarray(values, dtype=np.float64)


def compute_bootstrap_slopes(
    *,
    summaries: list[dict[str, object]],
    block_rows: list[dict[str, object]],
    bootstrap_repetitions: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    """Compute adjacent and final-three slopes from block-level resampling."""
    adjacent_rows: list[dict[str, object]] = []
    final_rows: list[dict[str, object]] = []
    stages = sorted({str(row["stage"]) for row in summaries})
    adjacent_family = sum(len(regime.scales) - 1 for regime in REGIMES)
    for stage_index, stage in enumerate(stages):
        for regime in REGIMES:
            cell_rows = sorted(
                (
                    row
                    for row in summaries
                    if row["stage"] == stage and row["regime"] == regime.key
                ),
                key=lambda row: int(row["scale"]),
            )
            if len(cell_rows) != len(regime.scales):
                continue
            means = np.asarray([float(row["mean_tau"]) for row in cell_rows])
            scales = np.asarray([int(row["scale"]) for row in cell_rows], dtype=np.float64)
            rng = np.random.default_rng(MASTER_SEED + 9_000_000 + 100_000 * stage_index + regime.regime_id)
            bootstrap_means = []
            for scale in regime.scales:
                blocks = _group_blocks(block_rows, stage, regime.key, scale)
                indices = rng.integers(0, blocks.size, size=(bootstrap_repetitions, blocks.size))
                bootstrap_means.append(blocks[indices].mean(axis=1))
            boot = np.stack(bootstrap_means, axis=1)
            adjacent_alpha = FAMILY_ALPHA / adjacent_family
            for index in range(len(scales) - 1):
                point = float(math.log(means[index + 1] / means[index]) / math.log(2.0))
                draws = np.log(boot[:, index + 1] / boot[:, index]) / math.log(2.0)
                low, high = np.quantile(draws, (adjacent_alpha / 2.0, 1.0 - adjacent_alpha / 2.0))
                adjacent_rows.append(
                    {
                        "experiment_id": EXPERIMENT_ID,
                        "stage": stage,
                        "regime": regime.key,
                        "alpha": "" if regime.alpha is None else regime.alpha,
                        "scale_low": int(scales[index]),
                        "scale_high": int(scales[index + 1]),
                        "effective_exponent": point,
                        "simultaneous_ci_low": float(low),
                        "simultaneous_ci_high": float(high),
                        "target_exponent": regime.theoretical_exponent,
                        "bootstrap_repetitions": bootstrap_repetitions,
                        "family_size": adjacent_family,
                    }
                )
            last_scales = scales[-3:]
            x = np.log(last_scales)
            centered_x = x - x.mean()
            denominator = float(np.dot(centered_x, centered_x))
            point = float(np.dot(centered_x, np.log(means[-3:])) / denominator)
            draws = (np.log(boot[:, -3:]) @ centered_x) / denominator
            final_alpha = FAMILY_ALPHA / len(REGIMES)
            low, high = np.quantile(draws, (final_alpha / 2.0, 1.0 - final_alpha / 2.0))
            final_rows.append(
                {
                    "experiment_id": EXPERIMENT_ID,
                    "stage": stage,
                    "regime": regime.key,
                    "alpha": "" if regime.alpha is None else regime.alpha,
                    "scales_json": _canonical_json(last_scales.astype(int).tolist()),
                    "effective_exponent": point,
                    "simultaneous_ci_low": float(low),
                    "simultaneous_ci_high": float(high),
                    "simultaneous_ci_half_width": float((high - low) / 2.0),
                    "target_exponent": regime.theoretical_exponent,
                    "bootstrap_repetitions": bootstrap_repetitions,
                    "family_size": len(REGIMES),
                }
            )
    return adjacent_rows, final_rows


def compare_stages(
    summaries: list[dict[str, object]], block_rows: list[dict[str, object]]
) -> list[dict[str, object]]:
    """Compute Bonferroni--Welch intervals for replication minus primary."""
    by_key = {
        (str(row["stage"]), str(row["regime"]), int(row["scale"])): row
        for row in summaries
    }
    family_size = sum(len(regime.scales) for regime in REGIMES)
    rows: list[dict[str, object]] = []
    for regime in REGIMES:
        for scale in regime.scales:
            primary = by_key.get(("primary", regime.key, scale))
            replication = by_key.get(("replication", regime.key, scale))
            if primary is None or replication is None:
                continue
            norm = normalizer(regime, scale)
            first = _group_blocks(block_rows, "primary", regime.key, scale) / norm
            second = _group_blocks(block_rows, "replication", regime.key, scale) / norm
            difference = float(second.mean() - first.mean())
            v1 = float(first.var(ddof=1) / first.size)
            v2 = float(second.var(ddof=1) / second.size)
            standard_error = math.sqrt(v1 + v2)
            numerator = (v1 + v2) ** 2
            denominator = v1**2 / (first.size - 1) + v2**2 / (second.size - 1)
            degrees_freedom = numerator / denominator
            multiplier = float(
                stats.t.ppf(1.0 - FAMILY_ALPHA / (2.0 * family_size), degrees_freedom)
            )
            half_width = multiplier * standard_error
            low, high = difference - half_width, difference + half_width
            rows.append(
                {
                    "experiment_id": EXPERIMENT_ID,
                    "regime": regime.key,
                    "alpha": "" if regime.alpha is None else regime.alpha,
                    "scale": scale,
                    "normalized_difference_replication_minus_primary": difference,
                    "standard_error_blocks": standard_error,
                    "degrees_freedom": degrees_freedom,
                    "simultaneous_multiplier": multiplier,
                    "simultaneous_ci_low": low,
                    "simultaneous_ci_high": high,
                    "simultaneous_ci_contains_zero": bool(low <= 0.0 <= high),
                    "family_size": family_size,
                }
            )
    return rows


def evaluate_gates(
    *,
    summaries: list[dict[str, object]],
    diagnostics: list[dict[str, object]],
    final_slopes: list[dict[str, object]],
    stage_comparisons: list[dict[str, object]],
) -> dict[str, object]:
    checks: list[dict[str, object]] = []

    def add(name: str, passed: bool, value: object, criterion: str) -> None:
        checks.append({"name": name, "pass": bool(passed), "value": value, "criterion": criterion})

    add(
        "deterministic_implementation",
        all(bool(row["deterministic_gate_pass"]) for row in diagnostics),
        sum(not bool(row["deterministic_gate_pass"]) for row in diagnostics),
        "all deterministic cell gates pass",
    )
    add(
        "zero_censoring_nan_exclusion",
        all(
            int(row["censored_count"]) == 0
            and int(row["nan_count"]) == 0
            and int(row["excluded_count"]) == 0
            for row in summaries
        ),
        {
            "censored": sum(int(row["censored_count"]) for row in summaries),
            "nan": sum(int(row["nan_count"]) for row in summaries),
            "excluded": sum(int(row["excluded_count"]) for row in summaries),
        },
        "all three counts equal zero",
    )
    for stage in sorted({str(row["stage"]) for row in summaries}):
        stage_rows = [row for row in summaries if row["stage"] == stage]
        maximum_half_width = max(float(row["normalized_ci_half_width"]) for row in stage_rows)
        add(
            f"precision_{stage}",
            maximum_half_width <= 0.03,
            maximum_half_width,
            "maximum 20-cell simultaneous normalized half-width <= 0.03",
        )
    if stage_comparisons:
        add(
            "independent_stage_agreement",
            len(stage_comparisons) == 20
            and all(bool(row["simultaneous_ci_contains_zero"]) for row in stage_comparisons),
            sum(not bool(row["simultaneous_ci_contains_zero"]) for row in stage_comparisons),
            "all 20 Bonferroni-Welch intervals contain zero",
        )
    slope_ranges = {
        "drift": (1.40, 1.65),
        "zero": (1.90, 2.10),
        "critical": (1.90, 2.10),
        "fair": (1.90, 2.10),
    }
    for row in final_slopes:
        low, high = slope_ranges[str(row["regime"])]
        point = float(row["effective_exponent"])
        half_width = float(row["simultaneous_ci_half_width"])
        add(
            f"final_slope_{row['stage']}_{row['regime']}",
            low <= point <= high and half_width <= 0.10,
            {"point": point, "half_width": half_width},
            f"point in [{low},{high}] and simultaneous half-width <= 0.10",
        )
    by_key = {
        (str(row["stage"]), str(row["regime"]), int(row["scale"])): row
        for row in summaries
    }
    for stage in sorted({str(row["stage"]) for row in summaries}):
        for regime in REGIMES:
            rows = [by_key[(stage, regime.key, scale)] for scale in regime.scales]
            last = rows[-3:]
            normalized = [float(row["normalized_mean"]) for row in last]
            ratio = max(normalized) / min(normalized)
            ratio_limit = 1.20 if regime.key == "drift" else 1.10
            add(
                f"plateau_ratio_{stage}_{regime.key}",
                ratio <= ratio_limit,
                ratio,
                f"last-three normalized maximum/minimum <= {ratio_limit}",
            )
        drift_final = float(by_key[(stage, "drift", 1600)]["normalized_mean"])
        add(
            f"drift_center_{stage}",
            0.80 <= drift_final <= 1.05,
            drift_final,
            "N=1600 normalized drift mean in [0.80,1.05]",
        )
        deviation = float(
            by_key[(stage, "drift", 1600)]["relative_deviation_probability_30pct"]
        )
        add(
            f"drift_concentration_{stage}",
            deviation <= 0.25,
            deviation,
            "N=1600 probability of >30% relative deviation <= 0.25",
        )
        fair_difference = abs(
            float(by_key[(stage, "fair", 400)]["normalized_mean"])
            - float(by_key[(stage, "zero", 400)]["normalized_mean"])
        )
        add(
            f"fair_to_zero_{stage}",
            fair_difference <= 0.03,
            fair_difference,
            "absolute normalized mean difference at N=400 <= 0.03",
        )
    return {
        "experiment_id": EXPERIMENT_ID,
        "pipeline_version": PIPELINE_VERSION,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "checks": checks,
        "passed": all(bool(check["pass"]) for check in checks),
        "failed_checks": [check["name"] for check in checks if not check["pass"]],
    }


def _write_gate_report(path: Path, gate_result: dict[str, object]) -> None:
    lines = [
        "# 三分区有限尺度实验门禁报告",
        "",
        f"- 实验：`{gate_result['experiment_id']}`",
        f"- 总体：{'PASS' if gate_result['passed'] else 'FAIL'}",
        f"- 生成时间（UTC）：{gate_result['generated_utc']}",
        "",
        "| 门禁 | 结果 | 观测值 | 判据 |",
        "|---|---|---|---|",
    ]
    for check in gate_result["checks"]:
        value = _canonical_json(check["value"])
        lines.append(
            f"| `{check['name']}` | {'PASS' if check['pass'] else 'FAIL'} | `{value}` | {check['criterion']} |"
        )
    lines.extend(
        [
            "",
            "失败门禁不等同于数学定理失败；它只限制该有限网格可支持的数值表述。",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_sha256_manifest(output_dir: Path) -> None:
    files = sorted(
        path
        for path in output_dir.rglob("*")
        if path.is_file() and path.name != "SHA256SUMS.txt"
    )
    lines = [f"{_sha256_file(path)}  {path.relative_to(output_dir).as_posix()}" for path in files]
    (output_dir / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="ascii")


def run_full_experiment(
    *,
    output_dir: Path,
    stages: tuple[str, ...],
    repetitions: int,
    block_count: int,
    bootstrap_repetitions: int,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    all_summaries: list[dict[str, object]] = []
    all_blocks: list[dict[str, object]] = []
    all_diagnostics: list[dict[str, object]] = []
    started = time.perf_counter()
    for stage in stages:
        summaries, blocks, diagnostics = run_stage(
            output_dir=output_dir,
            stage=stage,
            repetitions=repetitions,
            block_count=block_count,
        )
        all_summaries.extend(summaries)
        all_blocks.extend(blocks)
        all_diagnostics.extend(diagnostics)
    _write_csv(output_dir / "phase-cell-summaries.csv", all_summaries)
    _write_csv(output_dir / "phase-block-means.csv", all_blocks)
    _write_csv(output_dir / "phase-kernel-diagnostics.csv", all_diagnostics)
    adjacent, final_slopes = compute_bootstrap_slopes(
        summaries=all_summaries,
        block_rows=all_blocks,
        bootstrap_repetitions=bootstrap_repetitions,
    )
    _write_csv(output_dir / "phase-adjacent-slopes.csv", adjacent)
    _write_csv(output_dir / "phase-final-three-slopes.csv", final_slopes)
    comparisons = compare_stages(all_summaries, all_blocks)
    _write_csv(output_dir / "phase-stage-comparisons.csv", comparisons)
    gate_result = evaluate_gates(
        summaries=all_summaries,
        diagnostics=all_diagnostics,
        final_slopes=final_slopes,
        stage_comparisons=comparisons,
    )
    (output_dir / "phase-gates.json").write_text(
        json.dumps(gate_result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _write_gate_report(output_dir / "phase-gates.md", gate_result)
    metadata = {
        "experiment_id": EXPERIMENT_ID,
        "pipeline_version": PIPELINE_VERSION,
        "contract": "outputs/researchwrite/hypergraph-stopping-time/41_phase_scaling_and_higher_order_figure_contract_2026-07-28.md",
        "stages": list(stages),
        "stage_seed_indices": {name: STAGE_NAMES.index(name) for name in stages},
        "repetitions_per_cell": repetitions,
        "block_count": block_count,
        "block_size": repetitions // block_count,
        "bootstrap_repetitions": bootstrap_repetitions,
        "amplitude": AMPLITUDE,
        "regimes": [asdict(regime) for regime in REGIMES],
        "maximum_steps": None,
        "simulator": "exact-zero-scan chunked i.i.d. route labels",
        "chunk_steps": CHUNK_STEPS,
        "censoring_allowed": False,
        "exclusions_allowed": False,
        "python": platform.python_version(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "platform": platform.platform(),
        "elapsed_seconds_this_invocation": time.perf_counter() - started,
        "gate_pass": gate_result["passed"],
        "failed_gates": gate_result["failed_checks"],
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    (output_dir / "phase-run-metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    _write_sha256_manifest(output_dir)
    return {"metadata": metadata, "gates": gate_result}


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/network-phase-closure"),
    )
    parser.add_argument(
        "--stages",
        choices=("primary", "replication", "both"),
        default="both",
    )
    parser.add_argument("--repetitions", type=int, default=FULL_REPETITIONS)
    parser.add_argument("--block-count", type=int, default=BLOCK_COUNT)
    parser.add_argument("--bootstrap-repetitions", type=int, default=BOOTSTRAP_REPETITIONS)
    parser.add_argument(
        "--strict-gates",
        action="store_true",
        help="exit nonzero when a prespecified finite-scale gate fails",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    stages = STAGE_NAMES if args.stages == "both" else (args.stages,)
    result = run_full_experiment(
        output_dir=args.output_dir,
        stages=stages,
        repetitions=args.repetitions,
        block_count=args.block_count,
        bootstrap_repetitions=args.bootstrap_repetitions,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return int(args.strict_gates and not bool(result["gates"]["passed"]))


if __name__ == "__main__":
    raise SystemExit(main())
