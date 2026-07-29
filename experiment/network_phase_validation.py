"""Marginal diagnostics and frozen evidence for correlated network kernels."""

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

from network_exact import solve_exact
from network_model import (
    NetworkKernel,
    perturb_route_probabilities,
    two_overlapping_triads_uniform,
)
from network_simulation import initial_balances, simulate_network, summarize_times


PHASE_GRID = {
    0.5: (10, 20, 40, 80),
    1.0: (10, 20, 40, 80),
    1.5: (10, 20, 40, 80),
}
MASTER_SEED = 20260717

_PIPELINE_VERSION = "2"
_EXACT_GRID = (1, 2, 3)
_PROXY_GRID = (10, 20, 40)
_SURVIVAL_GRID = tuple(round(index * 0.05, 2) for index in range(81))
_AMPLITUDE = 0.01
_CI_MULTIPLIER = 1.959963984540054
_MC_Z_LIMIT = 2.58

_EXACT_FIELDS = (
    "scale",
    "state_count",
    "exact_mean",
    "max_abs_residual",
    "all_states_reach_boundary",
    "survival_horizon",
    "survival_json",
)
_MC_FIELDS = (
    "scale",
    "repetitions",
    "seed",
    "exact_mean",
    "mc_mean",
    "mc_sd",
    "standard_error",
    "ci_low",
    "ci_high",
    "z_score",
    "gate_pass",
)
_PHASE_FIELDS = (
    "alpha",
    "scale",
    "repetitions",
    "seed",
    "mean",
    "sd",
    "q10",
    "q50",
    "q90",
    "normalizer",
    "normalized_mean",
    "normalized_q10",
    "normalized_q50",
    "normalized_q90",
)
_PROXY_FIELDS = (
    "scale",
    "repetitions",
    "seed",
    "correlated_mean",
    "proxy_mean",
    "normalized_correlated_mean",
    "normalized_proxy_mean",
    "mean_difference",
    "paired_standard_error",
    "ci_low",
    "ci_high",
    "sign",
    "q10_difference",
    "q50_difference",
    "q90_difference",
    "nonidentical_fraction",
)
_SURVIVAL_FIELDS = (
    "scale",
    "normalized_time",
    "correlated_survival",
    "proxy_survival",
    "difference",
)


class DeterministicGateError(RuntimeError):
    """Raised after artifacts are written when an exact gate fails."""

    def __init__(self, failures: tuple[str, ...], metadata: dict):
        super().__init__("; ".join(failures))
        self.failures = failures
        self.metadata = metadata


@dataclass(frozen=True)
class PairedProxySample:
    correlated_times: np.ndarray
    proxy_times: np.ndarray
    seed: int


def block_marginals(
    kernel: NetworkKernel,
) -> tuple[tuple[np.ndarray, np.ndarray], ...]:
    """Aggregate each hyperedge block's exact increment distribution."""
    marginals: list[tuple[np.ndarray, np.ndarray]] = []
    for edge_index in range(len(kernel.spec.edges)):
        block = kernel.edge_slice(edge_index)
        grouped: dict[tuple[int, ...], float] = {}
        for increment, probability in zip(kernel.increments[:, block], kernel.probabilities):
            key = tuple(int(value) for value in increment)
            grouped[key] = grouped.get(key, 0.0) + float(probability)
        keys = sorted(grouped)
        increments = np.asarray(keys, dtype=np.int8)
        probabilities = np.asarray([grouped[key] for key in keys], dtype=np.float64)
        residual = 1.0 - float(probabilities.sum())
        if residual != 0.0:
            probabilities[-1] += residual
        marginals.append((increments, probabilities))
    return tuple(marginals)


def simulate_paired_proxy(
    kernel: NetworkKernel,
    scale: int,
    repetitions: int,
    seed: int,
) -> PairedProxySample:
    """Compare correlated increments with independent exact edge marginals."""
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
    marginal_cdfs = []
    for _, probabilities in marginals:
        cdf = np.cumsum(probabilities)
        cdf[-1] = 1.0
        marginal_cdfs.append(cdf)

    edge_count = len(kernel.spec.edges)
    while np.any(correlated_active) or np.any(proxy_active):
        uniforms = rng.random((repetitions, edge_count))

        correlated_rows = np.flatnonzero(correlated_active)
        if correlated_rows.size:
            route_ids = np.searchsorted(
                route_cdf, uniforms[correlated_rows, 0], side="right"
            )
            correlated_balances[correlated_rows] += kernel.increments[route_ids]
            correlated_times[correlated_rows] += 1
            correlated_active[correlated_rows] = ~np.any(
                correlated_balances[correlated_rows] == 0, axis=1
            )

        proxy_rows = np.flatnonzero(proxy_active)
        if proxy_rows.size:
            for edge_index, ((increments, _), cdf) in enumerate(
                zip(marginals, marginal_cdfs)
            ):
                marginal_ids = np.searchsorted(
                    cdf, uniforms[proxy_rows, edge_index], side="right"
                )
                proxy_balances[proxy_rows, kernel.edge_slice(edge_index)] += increments[
                    marginal_ids
                ]
            proxy_times[proxy_rows] += 1
            proxy_active[proxy_rows] = ~np.any(
                proxy_balances[proxy_rows] == 0, axis=1
            )

    return PairedProxySample(correlated_times, proxy_times, seed)


def _canonical_sha256(value: object) -> str:
    payload = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _input_sha256(kernel: NetworkKernel) -> str:
    inputs = {
        "capacity_units": list(kernel.spec.capacity_units),
        "edges": [list(edge) for edge in kernel.spec.edges],
        "probabilities": [float(value).hex() for value in kernel.probabilities],
        "routes": [
            {"edges": list(route.edges), "nodes": list(route.nodes)}
            for route in kernel.routes
        ],
    }
    return _canonical_sha256(inputs)


def _validation_config(quick: bool) -> dict:
    exact_horizon = 50 if quick else 200
    repetitions = {
        "mc": {"full": 50000, "quick": 5000},
        "paired": {"full": 50000, "quick": 2000},
        "phase": {"full": 20000, "quick": 2000},
    }
    mode = "quick" if quick else "full"
    return {
        "amplitude": _AMPLITUDE,
        "base_kernel": "two_overlapping_triads_uniform",
        "confidence": {
            "ci_multiplier": _CI_MULTIPLIER,
            "mc_z_limit": _MC_Z_LIMIT,
        },
        "exact_expected_state_counts": {"1": 1, "2": 100, "3": 784},
        "exact_grid": list(_EXACT_GRID),
        "exact_survival_horizon": {
            "full": 200,
            "quick": 50,
            "selected": exact_horizon,
        },
        "master_seed": MASTER_SEED,
        "mode": mode,
        "phase_grid": {
            format(alpha, ".1f"): list(scales)
            for alpha, scales in PHASE_GRID.items()
        },
        "phase_normalizers": {"0.5": "N**1.5", "1.0": "N**2", "1.5": "N**2"},
        "proxy_grid": list(_PROXY_GRID),
        "repetitions": {
            **repetitions,
            "selected": {name: values[mode] for name, values in repetitions.items()},
        },
        "seed_formulas": {
            "mc": "2026071700 + N",
            "phase": "2026072000 + int(alpha * 10) * 100 + N",
            "proxy": "2026073000 + N",
        },
        "survival_grid": list(_SURVIVAL_GRID),
    }


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


def _atomic_write_text(path: Path, text: str) -> None:
    temporary = _temporary_sibling(path)
    try:
        temporary.write_text(text, encoding="utf-8", newline="")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_validation(output: Path, quick: bool = False) -> dict:
    """Produce the frozen exact, Monte Carlo, phase, and proxy evidence."""
    started = time.perf_counter()
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    kernel = two_overlapping_triads_uniform()
    config = _validation_config(quick)
    config_sha256 = _canonical_sha256(config)
    input_sha256 = _input_sha256(kernel)
    mode = "quick" if quick else "full"
    exact_horizon = int(config["exact_survival_horizon"]["selected"])
    mc_repetitions = int(config["repetitions"]["mc"][mode])
    phase_repetitions = int(config["repetitions"]["phase"][mode])
    paired_repetitions = int(config["repetitions"]["paired"][mode])

    exact_rows: list[dict] = []
    exact_results = {}
    for scale in _EXACT_GRID:
        result = solve_exact(kernel, scale, survival_horizon=exact_horizon)
        exact_results[scale] = result
        exact_rows.append(
            {
                "scale": scale,
                "state_count": result.state_count,
                "exact_mean": result.mean,
                "max_abs_residual": result.max_abs_residual,
                "all_states_reach_boundary": result.all_states_reach_boundary,
                "survival_horizon": exact_horizon,
                "survival_json": json.dumps(
                    result.survival.tolist(), separators=(",", ":")
                ),
            }
        )

    deterministic_failures: list[str] = []
    expected_counts = {1: 1, 2: 100, 3: 784}
    for scale, result in exact_results.items():
        if result.state_count != expected_counts[scale]:
            deterministic_failures.append(
                f"N={scale}:state_count={result.state_count}:expected={expected_counts[scale]}"
            )
        if not result.max_abs_residual < 1e-10:
            deterministic_failures.append(
                f"N={scale}:max_abs_residual={result.max_abs_residual:.17g}"
            )
        if not result.all_states_reach_boundary:
            deterministic_failures.append(f"N={scale}:reachability=false")
    if abs(exact_results[1].mean - 1.0) > 1e-14:
        deterministic_failures.append(f"N=1:exact_mean={exact_results[1].mean:.17g}")

    mc_rows: list[dict] = []
    mc_failures: list[str] = []
    for scale in _EXACT_GRID:
        seed = 2026071700 + scale
        sample = simulate_network(kernel, scale, mc_repetitions, seed)
        summary = summarize_times(sample.stopping_times)
        exact_mean = exact_results[scale].mean
        difference = summary.mean - exact_mean
        if summary.standard_error == 0.0:
            agrees = summary.mean == exact_mean
            z_score = 0.0 if agrees else math.copysign(math.inf, difference)
            gate_pass = agrees
        else:
            z_score = difference / summary.standard_error
            gate_pass = abs(z_score) <= _MC_Z_LIMIT
        if scale == 1:
            gate_pass = summary.mean == exact_mean
        if not gate_pass:
            mc_failures.append(f"N={scale}:z_score={z_score:.17g}")
        mc_rows.append(
            {
                "scale": scale,
                "repetitions": mc_repetitions,
                "seed": seed,
                "exact_mean": exact_mean,
                "mc_mean": summary.mean,
                "mc_sd": summary.sd,
                "standard_error": summary.standard_error,
                "ci_low": summary.ci_low,
                "ci_high": summary.ci_high,
                "z_score": z_score,
                "gate_pass": gate_pass,
            }
        )

    forward_index = next(
        index for index, route in enumerate(kernel.routes) if route.nodes == (0, 2, 3)
    )
    reverse_index = next(
        index for index, route in enumerate(kernel.routes) if route.nodes == (3, 2, 0)
    )
    phase_rows: list[dict] = []
    for alpha, scales in PHASE_GRID.items():
        for scale in scales:
            seed = 2026072000 + int(alpha * 10) * 100 + scale
            phase_kernel = perturb_route_probabilities(
                kernel,
                scale,
                alpha,
                forward_index,
                reverse_index,
                amplitude=_AMPLITUDE,
            )
            sample = simulate_network(
                phase_kernel, scale, phase_repetitions, seed
            ).stopping_times
            summary = summarize_times(sample)
            q10, q50, q90 = (float(value) for value in np.quantile(sample, (0.1, 0.5, 0.9)))
            normalizer = scale ** (1.5 if alpha == 0.5 else 2.0)
            phase_rows.append(
                {
                    "alpha": alpha,
                    "scale": scale,
                    "repetitions": phase_repetitions,
                    "seed": seed,
                    "mean": summary.mean,
                    "sd": summary.sd,
                    "q10": q10,
                    "q50": q50,
                    "q90": q90,
                    "normalizer": normalizer,
                    "normalized_mean": summary.mean / normalizer,
                    "normalized_q10": q10 / normalizer,
                    "normalized_q50": q50 / normalizer,
                    "normalized_q90": q90 / normalizer,
                }
            )

    proxy_rows: list[dict] = []
    survival_rows: list[dict] = []
    for scale in _PROXY_GRID:
        seed = 2026073000 + scale
        paired = simulate_paired_proxy(kernel, scale, paired_repetitions, seed)
        divisor = float(scale**2)
        correlated = paired.correlated_times.astype(np.float64) / divisor
        proxy = paired.proxy_times.astype(np.float64) / divisor
        differences = correlated - proxy
        difference_mean = float(differences.mean())
        difference_se = float(differences.std(ddof=1) / math.sqrt(paired_repetitions))
        margin = _CI_MULTIPLIER * difference_se
        correlated_quantiles = np.quantile(correlated, (0.1, 0.5, 0.9))
        proxy_quantiles = np.quantile(proxy, (0.1, 0.5, 0.9))
        quantile_differences = correlated_quantiles - proxy_quantiles
        sign = "positive" if difference_mean > 0 else "negative" if difference_mean < 0 else "zero"
        proxy_rows.append(
            {
                "scale": scale,
                "repetitions": paired_repetitions,
                "seed": seed,
                "correlated_mean": float(paired.correlated_times.mean()),
                "proxy_mean": float(paired.proxy_times.mean()),
                "normalized_correlated_mean": float(correlated.mean()),
                "normalized_proxy_mean": float(proxy.mean()),
                "mean_difference": difference_mean,
                "paired_standard_error": difference_se,
                "ci_low": difference_mean - margin,
                "ci_high": difference_mean + margin,
                "sign": sign,
                "q10_difference": float(quantile_differences[0]),
                "q50_difference": float(quantile_differences[1]),
                "q90_difference": float(quantile_differences[2]),
                "nonidentical_fraction": float(
                    np.mean(paired.correlated_times != paired.proxy_times)
                ),
            }
        )
        for normalized_time in _SURVIVAL_GRID:
            correlated_survival = float(np.mean(correlated > normalized_time))
            proxy_survival = float(np.mean(proxy > normalized_time))
            survival_rows.append(
                {
                    "scale": scale,
                    "normalized_time": normalized_time,
                    "correlated_survival": correlated_survival,
                    "proxy_survival": proxy_survival,
                    "difference": correlated_survival - proxy_survival,
                }
            )

    csv_specs = (
        (output / "network-exact.csv", _EXACT_FIELDS, exact_rows),
        (output / "network-mc-exact-check.csv", _MC_FIELDS, mc_rows),
        (output / "network-phase-scaling.csv", _PHASE_FIELDS, phase_rows),
        (output / "network-correlated-vs-proxy.csv", _PROXY_FIELDS, proxy_rows),
        (output / "network-survival-curves.csv", _SURVIVAL_FIELDS, survival_rows),
    )
    for path, fieldnames, rows in csv_specs:
        _atomic_write_csv(path, fieldnames, rows)

    metadata_path = output / "network-run-metadata.json"
    manifest_path = output / "SHA256SUMS.txt"
    file_paths = [path for path, _, _ in csv_specs] + [metadata_path, manifest_path]
    metadata = {
        "all_gates_pass": not deterministic_failures and not mc_failures,
        "config": config,
        "config_sha256": config_sha256,
        "deterministic_gate_failures": deterministic_failures,
        "deterministic_gates_pass": not deterministic_failures,
        "files": [str(path.resolve()) for path in file_paths],
        "input_sha256": input_sha256,
        "mc_gate_failures": mc_failures,
        "mc_gates_pass": not mc_failures,
        "model": "network-first-depletion",
        "numpy": np.__version__,
        "pipeline_version": _PIPELINE_VERSION,
        "platform": platform.platform(),
        "proxy_semantics": "independent edge-marginal diagnostic; not routed traffic",
        "python": platform.python_version(),
        "quick": quick,
        "row_counts": {
            "correlated_vs_proxy": len(proxy_rows),
            "exact": len(exact_rows),
            "mc_exact_check": len(mc_rows),
            "phase_scaling": len(phase_rows),
            "survival_curves": len(survival_rows),
        },
        "runtime_seconds": time.perf_counter() - started,
        "scipy": scipy.__version__,
        "seed": MASTER_SEED,
        "stop_event": "first balance coordinate equal to zero",
    }
    _atomic_write_text(
        metadata_path,
        json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
    )

    hashed_paths = sorted(
        [path for path, _, _ in csv_specs] + [metadata_path],
        key=lambda path: path.relative_to(output).as_posix(),
    )
    manifest = "".join(
        f"{_file_sha256(path)}  {path.relative_to(output).as_posix()}\n"
        for path in hashed_paths
    )
    _atomic_write_text(manifest_path, manifest)

    if deterministic_failures:
        raise DeterministicGateError(tuple(deterministic_failures), metadata)
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="use quick repetition counts")
    parser.add_argument("--output", required=True, type=Path, help="evidence output directory")
    arguments = parser.parse_args()

    try:
        metadata = run_validation(arguments.output, quick=arguments.quick)
    except DeterministicGateError as error:
        metadata = error.metadata
    row_counts = metadata["row_counts"]
    failed = metadata["deterministic_gate_failures"] + metadata["mc_gate_failures"]
    print(
        f"output={arguments.output.resolve()} "
        f"gates={'PASS' if metadata['all_gates_pass'] else 'FAIL'} "
        f"rows={sum(row_counts.values())} "
        f"runtime={metadata['runtime_seconds']:.3f}s"
        + (f" failures={','.join(failed)}" if failed else "")
    )
    if not metadata["all_gates_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
