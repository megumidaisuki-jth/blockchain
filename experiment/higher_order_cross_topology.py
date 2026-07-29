"""Formal T18-A cross-topology paired stopping-time validation."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import numpy as np
import scipy
from scipy.stats import kurtosis, norm, skew, t as student_t

from network_model import NetworkKernel, perturb_route_probabilities
from network_exact import solve_exact
from network_phase_validation import block_marginals
from network_simulation import initial_balances
from network_topologies import (
    overlap_chain_triads,
    overlap_star_triads,
    random_connected_triads,
    shortest_route_kernel,
)


TOPOLOGY_ORDER = ("chain", "star", "random")
REGIME_ORDER = ("balanced", "positive", "negative")
SCALE_GRID = (10, 20, 40, 80)
RANDOM_TOPOLOGY_SEED = 7
PERTURBATION_AMPLITUDE = 0.01
MASTER_SEED = 20260718
FAMILYWISE_ALPHA = 0.05
PRIMARY_COMPARISON_COUNT = 36
FULL_REPETITIONS = 30000
QUICK_REPETITIONS = 200
DETERMINISTIC_TOLERANCE = 1e-12
FULL_MAX_SIMULTANEOUS_HALF_WIDTH = 0.02
PIPELINE_VERSION = "1"

_PRIMARY_FIELDS = (
    "cell_id",
    "topology",
    "regime",
    "scale",
    "repetitions",
    "seed",
    "correlated_mean",
    "proxy_mean",
    "normalized_correlated_mean",
    "normalized_proxy_mean",
    "mean_difference",
    "paired_sd",
    "paired_standard_error",
    "simultaneous_multiplier",
    "half_width",
    "ci_low",
    "ci_high",
    "point_sign",
    "resolved_sign",
    "paired_standardized_effect",
    "relative_mean_difference",
    "q10_difference",
    "q50_difference",
    "q90_difference",
    "nonidentical_fraction",
)

_DIAGNOSTIC_FIELDS = (
    "cell_id",
    "topology",
    "regime",
    "scale",
    "seed",
    "edge_count",
    "route_count",
    "minimum_probability",
    "probability_sum_error",
    "minimum_normal_variance",
    "cross_covariance_frobenius",
    "scaled_drift_norm",
    "scaled_drift_error",
    "second_moment_error",
    "covariance_identity_error",
    "proxy_marginal_mean_error",
    "proxy_marginal_covariance_error",
)

_SENSITIVITY_FIELDS = (
    "cell_id",
    "topology",
    "regime",
    "scale",
    "seed",
    "repetitions",
    "blocks",
    "block_size",
    "mean_difference",
    "paired_sd",
    "normal_critical",
    "normal_ci_low",
    "normal_ci_high",
    "path_t_critical",
    "path_t_ci_low",
    "path_t_ci_high",
    "block_t_critical",
    "block_standard_error",
    "block_t_ci_low",
    "block_t_ci_high",
    "difference_skewness",
    "difference_excess_kurtosis",
    "minimum_difference",
    "maximum_difference",
)

_EXACT_ANCHOR_FIELDS = (
    "topology",
    "scale",
    "state_count",
    "repetitions",
    "seed",
    "exact_mean",
    "mc_mean",
    "mc_sd",
    "standard_error",
    "z_score",
    "max_abs_residual",
    "all_states_reach_boundary",
    "gate_pass",
)


@dataclass(frozen=True)
class T18Scenario:
    cell_id: str
    topology: str
    regime: str
    scale: int
    seed: int
    base_kernel: NetworkKernel
    kernel: NetworkKernel
    forward_index: int
    reverse_index: int


@dataclass(frozen=True)
class ActivePairedProxySample:
    correlated_times: np.ndarray
    proxy_times: np.ndarray
    seed: int
    random_row_count: int
    naive_random_row_count: int


def select_reversible_route_pair(kernel: NetworkKernel) -> tuple[int, int]:
    """Select a deterministic longest route with an equal-probability reverse."""
    lookup = {
        (route.nodes, route.edges): index for index, route in enumerate(kernel.routes)
    }
    candidates = sorted(
        range(len(kernel.routes)),
        key=lambda index: (
            -len(kernel.routes[index].edges),
            kernel.routes[index].edges,
            kernel.routes[index].nodes,
        ),
    )
    for forward_index in candidates:
        route = kernel.routes[forward_index]
        reverse_index = lookup.get(
            (tuple(reversed(route.nodes)), tuple(reversed(route.edges)))
        )
        if reverse_index is None or reverse_index == forward_index:
            continue
        if not np.isclose(
            kernel.probabilities[forward_index],
            kernel.probabilities[reverse_index],
            rtol=0.0,
            atol=1e-15,
        ):
            continue
        if np.array_equal(
            kernel.increments[forward_index], -kernel.increments[reverse_index]
        ):
            return forward_index, reverse_index
    raise ValueError("kernel has no equal-probability reversible route pair")


def critical_kernel(
    base: NetworkKernel,
    scale: int,
    sign: int,
    amplitude: float = PERTURBATION_AMPLITUDE,
) -> NetworkKernel:
    """Return the balanced or signed critical route-pair perturbation."""
    if sign not in (-1, 0, 1) or isinstance(sign, bool):
        raise ValueError("sign must be -1, 0, or 1")
    if sign == 0:
        return base
    forward_index, reverse_index = select_reversible_route_pair(base)
    if sign < 0:
        forward_index, reverse_index = reverse_index, forward_index
    return perturb_route_probabilities(
        base,
        scale,
        alpha=1.0,
        forward_index=forward_index,
        reverse_index=reverse_index,
        amplitude=amplitude,
    )


def _base_kernels() -> dict[str, NetworkKernel]:
    specs = {
        "chain": overlap_chain_triads(4),
        "star": overlap_star_triads(4),
        "random": random_connected_triads(4, seed=RANDOM_TOPOLOGY_SEED),
    }
    return {name: shortest_route_kernel(spec) for name, spec in specs.items()}


def build_scenarios() -> tuple[T18Scenario, ...]:
    """Build the frozen 3 topology x 3 regime x 4 scale design."""
    sign_by_regime = {"balanced": 0, "positive": 1, "negative": -1}
    bases = _base_kernels()
    scenarios: list[T18Scenario] = []
    for topology_index, topology in enumerate(TOPOLOGY_ORDER):
        base = bases[topology]
        forward_index, reverse_index = select_reversible_route_pair(base)
        for regime_index, regime in enumerate(REGIME_ORDER):
            for scale in SCALE_GRID:
                seed = (
                    MASTER_SEED * 1000
                    + topology_index * 100
                    + regime_index * 10
                    + SCALE_GRID.index(scale)
                )
                scenarios.append(
                    T18Scenario(
                        cell_id=f"{topology}-{regime}-N{scale}",
                        topology=topology,
                        regime=regime,
                        scale=scale,
                        seed=seed,
                        base_kernel=base,
                        kernel=critical_kernel(
                            base, scale, sign_by_regime[regime]
                        ),
                        forward_index=forward_index,
                        reverse_index=reverse_index,
                    )
                )
    return tuple(scenarios)


def _max_abs(values: np.ndarray) -> float:
    return float(np.max(np.abs(values))) if values.size else 0.0


def kernel_diagnostics(scenario: T18Scenario) -> dict[str, float | int | str]:
    """Return deterministic identities and proxy-marginal validation errors."""
    sign = {"balanced": 0, "positive": 1, "negative": -1}[scenario.regime]
    base = scenario.base_kernel
    kernel = scenario.kernel
    zeta = base.increments[scenario.forward_index].astype(np.float64)
    expected_scaled_drift = 2.0 * sign * PERTURBATION_AMPLITUDE * zeta
    scaled_drift_error = _max_abs(
        scenario.scale * kernel.drift - expected_scaled_drift
    )

    base_second_moment = base.covariance + np.outer(base.drift, base.drift)
    second_moment = kernel.covariance + np.outer(kernel.drift, kernel.drift)
    second_moment_error = _max_abs(second_moment - base_second_moment)
    expected_covariance = base.covariance - np.outer(kernel.drift, kernel.drift)
    covariance_identity_error = _max_abs(kernel.covariance - expected_covariance)

    marginal_mean_error = 0.0
    marginal_covariance_error = 0.0
    for edge_index, (increments, probabilities) in enumerate(block_marginals(kernel)):
        block = kernel.edge_slice(edge_index)
        mean = probabilities @ increments
        centered = increments - mean
        covariance = centered.T @ (centered * probabilities[:, None])
        marginal_mean_error = max(
            marginal_mean_error, _max_abs(mean - kernel.drift[block])
        )
        marginal_covariance_error = max(
            marginal_covariance_error,
            _max_abs(covariance - kernel.covariance[block, block]),
        )

    cross_squared = 0.0
    for left in range(len(kernel.spec.edges)):
        for right in range(left + 1, len(kernel.spec.edges)):
            cross = kernel.covariance[
                kernel.edge_slice(left), kernel.edge_slice(right)
            ]
            cross_squared += float(np.sum(cross * cross))

    return {
        "cell_id": scenario.cell_id,
        "topology": scenario.topology,
        "regime": scenario.regime,
        "scale": scenario.scale,
        "seed": scenario.seed,
        "edge_count": len(kernel.spec.edges),
        "route_count": len(kernel.routes),
        "minimum_probability": float(np.min(kernel.probabilities)),
        "probability_sum_error": abs(float(np.sum(kernel.probabilities)) - 1.0),
        "minimum_normal_variance": float(np.min(np.diag(kernel.covariance))),
        "cross_covariance_frobenius": float(np.sqrt(cross_squared)),
        "scaled_drift_norm": float(np.linalg.norm(scenario.scale * kernel.drift)),
        "scaled_drift_error": scaled_drift_error,
        "second_moment_error": second_moment_error,
        "covariance_identity_error": covariance_identity_error,
        "proxy_marginal_mean_error": marginal_mean_error,
        "proxy_marginal_covariance_error": marginal_covariance_error,
    }


def simulate_paired_proxy_active(
    kernel: NetworkKernel,
    scale: int,
    repetitions: int,
    seed: int,
) -> ActivePairedProxySample:
    """Pair models while drawing uniforms only for rows active in either model."""
    starting = initial_balances(kernel, scale)
    if type(repetitions) is not int or repetitions <= 1:
        raise ValueError("repetitions must be an integer greater than one")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")

    rng = np.random.default_rng(seed)
    correlated_balances = np.repeat(starting[None, :], repetitions, axis=0)
    proxy_balances = correlated_balances.copy()
    correlated_times = np.zeros(repetitions, dtype=np.int64)
    proxy_times = np.zeros(repetitions, dtype=np.int64)
    correlated_active = np.ones(repetitions, dtype=bool)
    proxy_active = np.ones(repetitions, dtype=bool)

    route_cdf = np.cumsum(kernel.probabilities)
    route_cdf[-1] = 1.0
    marginals = block_marginals(kernel)
    marginal_cdfs: list[np.ndarray] = []
    for _, probabilities in marginals:
        cdf = np.cumsum(probabilities)
        cdf[-1] = 1.0
        marginal_cdfs.append(cdf)

    edge_count = len(kernel.spec.edges)
    random_row_count = 0
    naive_random_row_count = 0
    while np.any(correlated_active) or np.any(proxy_active):
        union_rows = np.flatnonzero(correlated_active | proxy_active)
        uniforms = rng.random((union_rows.size, edge_count))
        random_row_count += int(union_rows.size)
        naive_random_row_count += repetitions

        correlated_rows = np.flatnonzero(correlated_active)
        if correlated_rows.size:
            positions = np.searchsorted(union_rows, correlated_rows)
            route_ids = np.searchsorted(
                route_cdf, uniforms[positions, 0], side="right"
            )
            correlated_balances[correlated_rows] += kernel.increments[route_ids]
            correlated_times[correlated_rows] += 1
            correlated_active[correlated_rows] = ~np.any(
                correlated_balances[correlated_rows] == 0, axis=1
            )

        proxy_rows = np.flatnonzero(proxy_active)
        if proxy_rows.size:
            positions = np.searchsorted(union_rows, proxy_rows)
            for edge_index, ((increments, _), cdf) in enumerate(
                zip(marginals, marginal_cdfs)
            ):
                marginal_ids = np.searchsorted(
                    cdf, uniforms[positions, edge_index], side="right"
                )
                proxy_balances[proxy_rows, kernel.edge_slice(edge_index)] += increments[
                    marginal_ids
                ]
            proxy_times[proxy_rows] += 1
            proxy_active[proxy_rows] = ~np.any(
                proxy_balances[proxy_rows] == 0, axis=1
            )

    return ActivePairedProxySample(
        correlated_times=correlated_times,
        proxy_times=proxy_times,
        seed=seed,
        random_row_count=random_row_count,
        naive_random_row_count=naive_random_row_count,
    )


def simultaneous_multiplier(
    comparisons: int = PRIMARY_COMPARISON_COUNT,
    familywise_alpha: float = FAMILYWISE_ALPHA,
) -> float:
    """Return a two-sided Bonferroni normal critical value."""
    if type(comparisons) is not int or comparisons <= 0:
        raise ValueError("comparisons must be a positive integer")
    if not math.isfinite(familywise_alpha) or not 0.0 < familywise_alpha < 1.0:
        raise ValueError("familywise_alpha must be strictly between zero and one")
    return float(norm.ppf(1.0 - familywise_alpha / (2.0 * comparisons)))


def summarize_paired_cell(
    correlated_times: np.ndarray,
    proxy_times: np.ndarray,
    scale: int,
    multiplier: float,
) -> dict[str, float | int | str]:
    """Summarize one paired cell on the N-squared time scale."""
    correlated_raw = np.asarray(correlated_times, dtype=np.float64).ravel()
    proxy_raw = np.asarray(proxy_times, dtype=np.float64).ravel()
    if correlated_raw.size < 2 or correlated_raw.shape != proxy_raw.shape:
        raise ValueError("paired arrays must have the same length of at least two")
    if not np.all(np.isfinite(correlated_raw)) or not np.all(np.isfinite(proxy_raw)):
        raise ValueError("paired stopping times must be finite")
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    if not math.isfinite(multiplier) or multiplier <= 0.0:
        raise ValueError("multiplier must be finite and positive")

    divisor = float(scale**2)
    correlated = correlated_raw / divisor
    proxy = proxy_raw / divisor
    differences = correlated - proxy
    repetitions = int(differences.size)
    mean_difference = float(differences.mean())
    paired_sd = float(differences.std(ddof=1))
    paired_standard_error = paired_sd / math.sqrt(repetitions)
    half_width = multiplier * paired_standard_error
    ci_low = mean_difference - half_width
    ci_high = mean_difference + half_width
    point_sign = (
        "positive" if mean_difference > 0.0 else "negative" if mean_difference < 0.0 else "zero"
    )
    resolved_sign = (
        "positive" if ci_low > 0.0 else "negative" if ci_high < 0.0 else "unresolved"
    )
    if paired_sd == 0.0:
        paired_standardized_effect = (
            0.0 if mean_difference == 0.0 else math.copysign(math.inf, mean_difference)
        )
    else:
        paired_standardized_effect = mean_difference / paired_sd
    proxy_mean = float(proxy.mean())
    relative_mean_difference = mean_difference / proxy_mean
    quantile_differences = np.quantile(correlated, (0.1, 0.5, 0.9)) - np.quantile(
        proxy, (0.1, 0.5, 0.9)
    )
    return {
        "repetitions": repetitions,
        "correlated_mean": float(correlated_raw.mean()),
        "proxy_mean": float(proxy_raw.mean()),
        "normalized_correlated_mean": float(correlated.mean()),
        "normalized_proxy_mean": proxy_mean,
        "mean_difference": mean_difference,
        "paired_sd": paired_sd,
        "paired_standard_error": paired_standard_error,
        "simultaneous_multiplier": multiplier,
        "half_width": half_width,
        "ci_low": ci_low,
        "ci_high": ci_high,
        "point_sign": point_sign,
        "resolved_sign": resolved_sign,
        "paired_standardized_effect": paired_standardized_effect,
        "relative_mean_difference": relative_mean_difference,
        "q10_difference": float(quantile_differences[0]),
        "q50_difference": float(quantile_differences[1]),
        "q90_difference": float(quantile_differences[2]),
        "nonidentical_fraction": float(np.mean(correlated_raw != proxy_raw)),
    }


def summarize_sensitivity(
    correlated_times: np.ndarray,
    proxy_times: np.ndarray,
    scale: int,
    blocks: int = 100,
    comparisons: int = PRIMARY_COMPARISON_COUNT,
    familywise_alpha: float = FAMILYWISE_ALPHA,
) -> dict[str, float | int]:
    """Compare normal, path-level t, and independent block-mean t intervals."""
    correlated = np.asarray(correlated_times, dtype=np.float64).ravel()
    proxy = np.asarray(proxy_times, dtype=np.float64).ravel()
    if correlated.size < 2 or correlated.shape != proxy.shape:
        raise ValueError("paired arrays must have the same length of at least two")
    if not np.all(np.isfinite(correlated)) or not np.all(np.isfinite(proxy)):
        raise ValueError("paired stopping times must be finite")
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    if type(blocks) is not int or blocks < 2 or correlated.size % blocks:
        raise ValueError("blocks must divide repetitions and be at least two")

    differences = (correlated - proxy) / float(scale**2)
    repetitions = int(differences.size)
    mean_difference = float(differences.mean())
    paired_sd = float(differences.std(ddof=1))
    path_se = paired_sd / math.sqrt(repetitions)
    normal_critical = simultaneous_multiplier(comparisons, familywise_alpha)
    path_t_critical = float(
        student_t.ppf(1.0 - familywise_alpha / (2.0 * comparisons), repetitions - 1)
    )
    block_means = differences.reshape(blocks, repetitions // blocks).mean(axis=1)
    block_se = float(block_means.std(ddof=1) / math.sqrt(blocks))
    block_t_critical = float(
        student_t.ppf(1.0 - familywise_alpha / (2.0 * comparisons), blocks - 1)
    )
    if paired_sd == 0.0:
        difference_skewness = 0.0
        difference_excess_kurtosis = 0.0
    else:
        difference_skewness = float(skew(differences, bias=False))
        difference_excess_kurtosis = float(
            kurtosis(differences, fisher=True, bias=False)
        )
    return {
        "repetitions": repetitions,
        "blocks": blocks,
        "block_size": repetitions // blocks,
        "mean_difference": mean_difference,
        "paired_sd": paired_sd,
        "normal_critical": normal_critical,
        "normal_ci_low": mean_difference - normal_critical * path_se,
        "normal_ci_high": mean_difference + normal_critical * path_se,
        "path_t_critical": path_t_critical,
        "path_t_ci_low": mean_difference - path_t_critical * path_se,
        "path_t_ci_high": mean_difference + path_t_critical * path_se,
        "block_t_critical": block_t_critical,
        "block_standard_error": block_se,
        "block_t_ci_low": mean_difference - block_t_critical * block_se,
        "block_t_ci_high": mean_difference + block_t_critical * block_se,
        "difference_skewness": difference_skewness,
        "difference_excess_kurtosis": difference_excess_kurtosis,
        "minimum_difference": float(differences.min()),
        "maximum_difference": float(differences.max()),
    }


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _temporary_sibling(path: Path) -> Path:
    return path.with_name(f".{path.name}.tmp")


def _atomic_write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict]) -> None:
    temporary = _temporary_sibling(path)
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write_text(path: Path, value: str) -> None:
    temporary = _temporary_sibling(path)
    try:
        temporary.write_text(value, encoding="utf-8", newline="")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _config(quick: bool) -> dict:
    return {
        "familywise_alpha": FAMILYWISE_ALPHA,
        "full_max_simultaneous_half_width": FULL_MAX_SIMULTANEOUS_HALF_WIDTH,
        "master_seed": MASTER_SEED,
        "perturbation_amplitude": PERTURBATION_AMPLITUDE,
        "primary_comparison_count": PRIMARY_COMPARISON_COUNT,
        "random_topology_seed": RANDOM_TOPOLOGY_SEED,
        "regimes": list(REGIME_ORDER),
        "repetitions": {
            "full": FULL_REPETITIONS,
            "quick": QUICK_REPETITIONS,
            "selected": QUICK_REPETITIONS if quick else FULL_REPETITIONS,
        },
        "scales": list(SCALE_GRID),
        "topologies": list(TOPOLOGY_ORDER),
    }


def _scenario_input_payload(scenarios: tuple[T18Scenario, ...]) -> list[dict]:
    payload = []
    for scenario in scenarios:
        payload.append(
            {
                "cell_id": scenario.cell_id,
                "edges": [list(edge) for edge in scenario.kernel.spec.edges],
                "probabilities": [float(value).hex() for value in scenario.kernel.probabilities],
                "routes": [
                    {"nodes": list(route.nodes), "edges": list(route.edges)}
                    for route in scenario.kernel.routes
                ],
                "seed": scenario.seed,
            }
        )
    return payload


def run_t18_validation(
    output: Path,
    quick: bool = False,
    progress: bool = False,
) -> dict:
    """Run and atomically freeze the T18-A scenario matrix."""
    started = time.perf_counter()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    scenarios = build_scenarios()
    config = _config(quick)
    repetitions = int(config["repetitions"]["selected"])
    multiplier = simultaneous_multiplier()

    diagnostic_rows = [kernel_diagnostics(scenario) for scenario in scenarios]
    deterministic_failures: list[str] = []
    for row in diagnostic_rows:
        for field in (
            "probability_sum_error",
            "scaled_drift_error",
            "second_moment_error",
            "covariance_identity_error",
            "proxy_marginal_mean_error",
            "proxy_marginal_covariance_error",
        ):
            if not float(row[field]) <= DETERMINISTIC_TOLERANCE:
                deterministic_failures.append(
                    f"{row['cell_id']}:{field}={float(row[field]):.17g}"
                )
        if not float(row["minimum_probability"]) > 0.0:
            deterministic_failures.append(f"{row['cell_id']}:nonpositive_probability")
        if not float(row["minimum_normal_variance"]) > DETERMINISTIC_TOLERANCE:
            deterministic_failures.append(f"{row['cell_id']}:degenerate_normal_variance")

    primary_rows: list[dict] = []
    random_row_fractions: list[float] = []
    for index, scenario in enumerate(scenarios, start=1):
        paired = simulate_paired_proxy_active(
            scenario.kernel,
            scenario.scale,
            repetitions,
            scenario.seed,
        )
        random_row_fractions.append(
            paired.random_row_count / paired.naive_random_row_count
        )
        summary = summarize_paired_cell(
            paired.correlated_times,
            paired.proxy_times,
            scenario.scale,
            multiplier,
        )
        primary_rows.append(
            {
                "cell_id": scenario.cell_id,
                "topology": scenario.topology,
                "regime": scenario.regime,
                "scale": scenario.scale,
                "seed": scenario.seed,
                **summary,
            }
        )
        if progress:
            print(
                f"cell={index}/{len(scenarios)} id={scenario.cell_id} "
                f"delta={summary['mean_difference']:.6f} "
                f"half_width={summary['half_width']:.6f} "
                f"sign={summary['resolved_sign']}",
                flush=True,
            )

    precision_failures = [
        f"{row['cell_id']}:half_width={float(row['half_width']):.17g}"
        for row in primary_rows
        if float(row["half_width"]) > FULL_MAX_SIMULTANEOUS_HALF_WIDTH
    ]
    precision_gate_applicable = not quick
    precision_gates_pass = not precision_failures if precision_gate_applicable else False

    primary_path = output / "t18-primary-effects.csv"
    diagnostic_path = output / "t18-kernel-diagnostics.csv"
    metadata_path = output / "t18-run-metadata.json"
    manifest_path = output / "SHA256SUMS.txt"
    _atomic_write_csv(primary_path, _PRIMARY_FIELDS, primary_rows)
    _atomic_write_csv(diagnostic_path, _DIAGNOSTIC_FIELDS, diagnostic_rows)

    files = [primary_path, diagnostic_path, metadata_path, manifest_path]
    metadata = {
        "all_gates_pass": not deterministic_failures
        and (not precision_gate_applicable or not precision_failures),
        "config": config,
        "config_sha256": _canonical_sha256(config),
        "deterministic_gate_failures": deterministic_failures,
        "deterministic_gates_pass": not deterministic_failures,
        "files": [str(path.resolve()) for path in files],
        "input_sha256": _canonical_sha256(_scenario_input_payload(scenarios)),
        "model": "t18-cross-topology-first-depletion",
        "maximum_random_row_fraction": max(random_row_fractions),
        "minimum_random_row_fraction": min(random_row_fractions),
        "numpy": np.__version__,
        "pipeline_version": PIPELINE_VERSION,
        "platform": platform.platform(),
        "precision_gate_applicable": precision_gate_applicable,
        "precision_gate_failures": precision_failures,
        "precision_gates_pass": precision_gates_pass,
        "proxy_semantics": "independent exact edge-block marginals; not routed traffic",
        "python": platform.python_version(),
        "quick": quick,
        "row_counts": {
            "kernel_diagnostics": len(diagnostic_rows),
            "primary_effects": len(primary_rows),
        },
        "runtime_seconds": time.perf_counter() - started,
        "scipy": scipy.__version__,
        "simulation_algorithm": "active-union paired uniforms",
        "stop_event": "first balance coordinate equal to zero",
    }
    _atomic_write_text(
        metadata_path,
        json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
    )
    hashed_paths = sorted(
        (primary_path, diagnostic_path, metadata_path),
        key=lambda path: path.name,
    )
    _atomic_write_text(
        manifest_path,
        "".join(f"{_file_sha256(path)}  {path.name}\n" for path in hashed_paths),
    )
    return metadata


def run_weakest_sensitivity(
    output: Path,
    repetitions: int = 100000,
    blocks: int = 100,
    seed: int = 202607189999,
    progress: bool = False,
) -> dict:
    """Re-estimate the weakest primary cell under three interval constructions."""
    started = time.perf_counter()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    scenario = next(
        item for item in build_scenarios() if item.cell_id == "star-balanced-N80"
    )
    paired = simulate_paired_proxy_active(
        scenario.kernel, scenario.scale, repetitions, seed
    )
    summary = summarize_sensitivity(
        paired.correlated_times,
        paired.proxy_times,
        scenario.scale,
        blocks=blocks,
    )
    row = {
        "cell_id": scenario.cell_id,
        "topology": scenario.topology,
        "regime": scenario.regime,
        "scale": scenario.scale,
        "seed": seed,
        **summary,
    }
    interval_lower_bounds = (
        float(row["normal_ci_low"]),
        float(row["path_t_ci_low"]),
        float(row["block_t_ci_low"]),
    )
    intervals_all_positive = all(value > 0.0 for value in interval_lower_bounds)
    diagnostic = kernel_diagnostics(scenario)
    deterministic_gates_pass = all(
        float(diagnostic[field]) <= DETERMINISTIC_TOLERANCE
        for field in (
            "probability_sum_error",
            "scaled_drift_error",
            "second_moment_error",
            "covariance_identity_error",
            "proxy_marginal_mean_error",
            "proxy_marginal_covariance_error",
        )
    )

    csv_path = output / "t18-weakest-cell-sensitivity.csv"
    metadata_path = output / "t18-weakest-cell-metadata.json"
    manifest_path = output / "SHA256SUMS.txt"
    _atomic_write_csv(csv_path, _SENSITIVITY_FIELDS, [row])
    metadata = {
        "all_gates_pass": deterministic_gates_pass and intervals_all_positive,
        "blocks": blocks,
        "cell_id": scenario.cell_id,
        "config_sha256": _canonical_sha256(
            {
                "blocks": blocks,
                "cell_id": scenario.cell_id,
                "comparisons": PRIMARY_COMPARISON_COUNT,
                "familywise_alpha": FAMILYWISE_ALPHA,
                "repetitions": repetitions,
                "seed": seed,
            }
        ),
        "deterministic_gates_pass": deterministic_gates_pass,
        "files": [
            str(csv_path.resolve()),
            str(metadata_path.resolve()),
            str(manifest_path.resolve()),
        ],
        "input_sha256": _canonical_sha256(_scenario_input_payload((scenario,))),
        "intervals_all_positive": intervals_all_positive,
        "maximum_random_row_fraction": paired.random_row_count
        / paired.naive_random_row_count,
        "model": "t18-weakest-cell-sensitivity",
        "numpy": np.__version__,
        "pipeline_version": PIPELINE_VERSION,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "repetitions": repetitions,
        "runtime_seconds": time.perf_counter() - started,
        "scipy": scipy.__version__,
        "seed": seed,
        "simulation_algorithm": "active-union paired uniforms",
        "stop_event": "first balance coordinate equal to zero",
    }
    _atomic_write_text(
        metadata_path,
        json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
    )
    _atomic_write_text(
        manifest_path,
        "".join(
            f"{_file_sha256(path)}  {path.name}\n"
            for path in sorted((csv_path, metadata_path), key=lambda path: path.name)
        ),
    )
    if progress:
        print(
            f"cell={scenario.cell_id} repetitions={repetitions} "
            f"delta={float(row['mean_difference']):.6f} "
            f"normal_low={float(row['normal_ci_low']):.6f} "
            f"path_t_low={float(row['path_t_ci_low']):.6f} "
            f"block_t_low={float(row['block_t_ci_low']):.6f}",
            flush=True,
        )
    return metadata


def run_exact_anchors(
    output: Path,
    scale: int = 2,
    repetitions: int = 100000,
    topology_names: tuple[str, ...] = TOPOLOGY_ORDER,
) -> dict:
    """Cross-check the correlated simulator against finite-state exact means."""
    started = time.perf_counter()
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    if type(repetitions) is not int or repetitions <= 1:
        raise ValueError("repetitions must be an integer greater than one")
    if not topology_names or any(name not in TOPOLOGY_ORDER for name in topology_names):
        raise ValueError("topology_names must contain declared topology names")
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    bases = _base_kernels()
    rows: list[dict] = []
    failures: list[str] = []
    for index, topology in enumerate(topology_names):
        kernel = bases[topology]
        exact = solve_exact(kernel, scale, survival_horizon=20)
        seed = 202607180100 + index
        sample = simulate_paired_proxy_active(kernel, scale, repetitions, seed)
        values = sample.correlated_times.astype(np.float64)
        mc_mean = float(values.mean())
        mc_sd = float(values.std(ddof=1))
        standard_error = mc_sd / math.sqrt(repetitions)
        if standard_error == 0.0:
            z_score = 0.0 if mc_mean == exact.mean else math.copysign(
                math.inf, mc_mean - exact.mean
            )
        else:
            z_score = (mc_mean - exact.mean) / standard_error
        gate_pass = (
            exact.all_states_reach_boundary
            and exact.max_abs_residual < 1e-10
            and abs(z_score) <= 3.29
        )
        if not gate_pass:
            failures.append(f"{topology}:z={z_score:.17g}")
        rows.append(
            {
                "topology": topology,
                "scale": scale,
                "state_count": exact.state_count,
                "repetitions": repetitions,
                "seed": seed,
                "exact_mean": exact.mean,
                "mc_mean": mc_mean,
                "mc_sd": mc_sd,
                "standard_error": standard_error,
                "z_score": z_score,
                "max_abs_residual": exact.max_abs_residual,
                "all_states_reach_boundary": exact.all_states_reach_boundary,
                "gate_pass": gate_pass,
            }
        )

    csv_path = output / "t18-exact-anchors.csv"
    metadata_path = output / "t18-exact-anchor-metadata.json"
    manifest_path = output / "SHA256SUMS.txt"
    _atomic_write_csv(csv_path, _EXACT_ANCHOR_FIELDS, rows)
    metadata = {
        "all_gates_pass": not failures,
        "files": [
            str(csv_path.resolve()),
            str(metadata_path.resolve()),
            str(manifest_path.resolve()),
        ],
        "gate_failures": failures,
        "input_sha256": _canonical_sha256(
            _scenario_input_payload(
                tuple(
                    item
                    for item in build_scenarios()
                    if item.topology in topology_names
                    and item.regime == "balanced"
                    and item.scale == SCALE_GRID[0]
                )
            )
        ),
        "model": "t18-correlated-exact-anchor",
        "numpy": np.__version__,
        "pipeline_version": PIPELINE_VERSION,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "repetitions": repetitions,
        "row_count": len(rows),
        "runtime_seconds": time.perf_counter() - started,
        "scale": scale,
        "scipy": scipy.__version__,
        "simulation_algorithm": "active-union paired uniforms; correlated component only",
        "stop_event": "first balance coordinate equal to zero",
        "topologies": list(topology_names),
        "z_gate": 3.29,
    }
    _atomic_write_text(
        metadata_path,
        json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
    )
    _atomic_write_text(
        manifest_path,
        "".join(
            f"{_file_sha256(path)}  {path.name}\n"
            for path in sorted((csv_path, metadata_path), key=lambda path: path.name)
        ),
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--weakest-only", action="store_true")
    parser.add_argument("--exact-anchors", action="store_true")
    parser.add_argument("--anchor-scale", type=int, default=2)
    parser.add_argument("--anchor-repetitions", type=int, default=100000)
    parser.add_argument("--sensitivity-repetitions", type=int, default=100000)
    parser.add_argument("--sensitivity-blocks", type=int, default=100)
    arguments = parser.parse_args()
    if arguments.exact_anchors:
        metadata = run_exact_anchors(
            arguments.output,
            scale=arguments.anchor_scale,
            repetitions=arguments.anchor_repetitions,
        )
    elif arguments.weakest_only:
        metadata = run_weakest_sensitivity(
            arguments.output,
            repetitions=arguments.sensitivity_repetitions,
            blocks=arguments.sensitivity_blocks,
            progress=True,
        )
    else:
        metadata = run_t18_validation(arguments.output, quick=arguments.quick, progress=True)
    print(
        f"output={arguments.output.resolve()} "
        f"gates={'PASS' if metadata['all_gates_pass'] else 'FAIL'} "
        f"runtime={metadata['runtime_seconds']:.3f}s",
        flush=True,
    )
    if not metadata["all_gates_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
