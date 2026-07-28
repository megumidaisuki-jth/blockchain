"""T12 positive-drift competition theory, simulation, and artifact pipeline."""

import argparse
import csv
from dataclasses import dataclass
import hashlib
from itertools import product
import json
import math
from pathlib import Path
import platform
import time
from typing import Mapping, Sequence

import numpy as np
import scipy
from scipy.integrate import quad
from scipy.special import ndtr
from scipy.stats import t as student_t

from drift_experiments import exact_drifted_markov_mean


PIPELINE_VERSION = "1"
FORMAL_REPETITIONS = 20_000
FORMAL_BLOCKS = 40
QUICK_REPETITIONS = 200
QUICK_BLOCKS = 20
EXACT_REPETITIONS = 100_000
EXACT_BLOCKS = 100
SENSITIVITY_REPETITIONS = 100_000
SENSITIVITY_BLOCKS = 100
PRIMARY_COMPARISONS = 36
ANCHOR_COMPARISONS = 9
DETERMINISTIC_TOLERANCE = 1e-12
EXACT_RESIDUAL_TOLERANCE = 1e-10
MAX_SIMULTANEOUS_HALF_WIDTH = 0.03
REFERENCE_SEED = 2026071814
REFERENCE_BASE_DRAWS = 1_000_000
EXACT_MASTER_SEED = 2026071816


@dataclass(frozen=True)
class CompetitionTheory:
    k: int
    p_bias: float
    delta: float
    peripheral_count: int
    v: float
    tstar_per_capacity: float
    kappa: float
    gaussian_difference_scale: float
    mean_correction_coefficient: float


@dataclass(frozen=True)
class T12CoupledSample:
    stopping_times: np.ndarray
    martingale_at_nstar: np.ndarray
    local_proxy_times: np.ndarray
    terminal_balances: np.ndarray
    nstar: int
    seed: int
    censored_count: int
    generated_rows: int


@dataclass(frozen=True)
class T12Scenario:
    """One seeded cell in the fixed positive-competition validation grid."""

    cell_id: str
    k: int
    N: int
    p_bias: float
    seed: int


def _validate_parameters(k: int, p_bias: float) -> None:
    if isinstance(k, bool) or not isinstance(k, (int, np.integer)) or k < 3:
        raise ValueError("k must be an integer at least 3")
    if not (1.0 < p_bias <= 2.0):
        raise ValueError("p_bias must lie in (1,2]")


def closed_form_peripheral_moments(k: int, p_bias: float):
    _validate_parameters(k, p_bias)
    delta = p_bias - 1.0
    v = 2.0 * delta / (k * (k - 1))
    m = k - 1
    mean = np.full(m, -v, dtype=np.float64)
    covariance = np.full((m, m), -2.0 / (k * (k - 1)) - v * v)
    np.fill_diagonal(covariance, 2.0 / k - v * v)
    return mean, covariance


def enumerate_peripheral_increment_law(k: int, p_bias: float):
    _validate_parameters(k, p_bias)
    m = k - 1
    pair_probability = 2.0 / (k * (k - 1))
    rows, probabilities = [], []
    for r in range(m):
        toward = np.zeros(m)
        toward[r] = -1.0
        away = -toward
        rows.extend((toward, away))
        probabilities.extend(
            (
                pair_probability * p_bias / 2.0,
                pair_probability * (2.0 - p_bias) / 2.0,
            )
        )
    for left in range(m):
        for right in range(left + 1, m):
            increment = np.zeros(m)
            increment[left], increment[right] = -1.0, 1.0
            rows.extend((increment, -increment))
            probabilities.extend((pair_probability / 2.0, pair_probability / 2.0))
    return np.asarray(rows), np.asarray(probabilities)


def gaussian_max_mean(count: int) -> float:
    if isinstance(count, bool) or not isinstance(count, (int, np.integer)) or count < 1:
        raise ValueError("count must be a positive integer")
    if count == 1:
        return 0.0

    def integrand(x: float) -> float:
        cdf = ndtr(x)
        return 1.0 - cdf**count - (1.0 - cdf)**count

    return float(quad(integrand, 0.0, np.inf, epsabs=1e-12)[0])


def competition_theory(k: int, p_bias: float) -> CompetitionTheory:
    _validate_parameters(k, p_bias)
    delta = p_bias - 1.0
    v = 2.0 * delta / (k * (k - 1))
    kappa = gaussian_max_mean(k - 1)
    scale = math.sqrt(k / delta)
    return CompetitionTheory(
        k=k,
        p_bias=p_bias,
        delta=delta,
        peripheral_count=k - 1,
        v=v,
        tstar_per_capacity=1.0 / v,
        kappa=kappa,
        gaussian_difference_scale=scale,
        mean_correction_coefficient=kappa * scale / v,
    )


def _draw_transfers(
    rng: np.random.Generator, k: int, p_bias: float, count: int
) -> tuple[np.ndarray, np.ndarray]:
    """Draw ordered transfers with the same vectorized law as the drift simulator."""
    first = rng.integers(0, k, size=count)
    second_raw = rng.integers(0, k - 1, size=count)
    second = second_raw + (second_raw >= first)
    sender = first.copy()
    receiver = second.copy()

    star = (first == 0) | (second == 0)
    if np.any(star):
        other = np.where(first[star] == 0, second[star], first[star])
        toward_zero = rng.random(np.count_nonzero(star)) < p_bias / 2.0
        sender[star] = np.where(toward_zero, other, 0)
        receiver[star] = np.where(toward_zero, 0, other)

    return sender, receiver


def simulate_coupled_competition(
    k: int, N: int, p_bias: float, repetitions: int, seed: int
) -> T12CoupledSample:
    """Couple first-depletion paths to their free walks at deterministic time nstar."""
    theory = competition_theory(k, p_bias)
    if isinstance(N, bool) or not isinstance(N, (int, np.integer)) or N < 1:
        raise ValueError("N must be a positive integer")
    if (
        isinstance(repetitions, bool)
        or not isinstance(repetitions, (int, np.integer))
        or repetitions < 2
    ):
        raise ValueError("repetitions must be an integer at least 2")

    rng = np.random.default_rng(seed)
    balances = np.full((repetitions, k), N, dtype=np.int64)
    terminal = np.empty_like(balances)
    stopping_times = np.zeros(repetitions, dtype=np.int64)
    stopped = np.zeros(repetitions, dtype=bool)
    nstar = math.floor(N / theory.v)
    martingale_at_nstar = None
    generated_rows = 0
    step = 0
    all_rows = np.arange(repetitions, dtype=np.int64)

    while step < nstar or np.any(~stopped):
        step += 1
        active = all_rows if step <= nstar else np.flatnonzero(~stopped)
        sender, receiver = _draw_transfers(rng, k, p_bias, active.size)
        balances[active, sender] -= 1
        balances[active, receiver] += 1
        generated_rows += int(active.size)

        newly_local = (~stopped[active]) & (balances[active, sender] == 0)
        newly = active[newly_local]
        stopping_times[newly] = step
        terminal[newly] = balances[newly]
        stopped[newly] = True

        if step == nstar:
            martingale_at_nstar = (
                balances[:, 1:].astype(np.float64) - (N - theory.v * nstar)
            ).copy()

    if martingale_at_nstar is None:
        raise RuntimeError("deterministic reference time was not recorded")

    local_proxy = N / theory.v + np.min(martingale_at_nstar, axis=1) / theory.v
    return T12CoupledSample(
        stopping_times=stopping_times,
        martingale_at_nstar=martingale_at_nstar,
        local_proxy_times=local_proxy,
        terminal_balances=terminal,
        nstar=nstar,
        seed=seed,
        censored_count=int(np.count_nonzero(stopping_times == 0)),
        generated_rows=generated_rows,
    )


def _positive_integer(value: int, name: str, *, minimum: int = 1) -> int:
    if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < minimum:
        raise ValueError(f"{name} must be an integer at least {minimum}")
    return int(value)


def build_scenarios(master_seed: int = 2026071812) -> tuple[T12Scenario, ...]:
    """Return the formal 3 x 3 x 4 grid with non-overlapping seed ranges."""
    master_seed = _positive_integer(master_seed, "master_seed", minimum=0)
    scenarios = []
    for index, (k, p_bias, N) in enumerate(
        product((3, 4, 5), (1.25, 1.5, 2.0), (40, 80, 160, 320))
    ):
        scenarios.append(
            T12Scenario(
                cell_id=f"k{k}-p{p_bias:g}-N{N}",
                k=k,
                N=N,
                p_bias=p_bias,
                seed=master_seed * 36 + index,
            )
        )
    return tuple(scenarios)


def bonferroni_t_critical(degrees_of_freedom: int, comparisons: int = 36) -> float:
    """Two-sided 95% familywise Student-t critical value."""
    degrees_of_freedom = _positive_integer(degrees_of_freedom, "degrees_of_freedom")
    comparisons = _positive_integer(comparisons, "comparisons")
    return float(student_t.ppf(1.0 - 0.05 / (2.0 * comparisons), df=degrees_of_freedom))


def _finite_block_values(values: np.ndarray, name: str) -> np.ndarray:
    array = np.asarray(values, dtype=np.float64)
    if array.ndim != 1 or array.size < 2 or not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must be a finite one-dimensional array with at least two values")
    return array


def _replication_block_values(
    values: np.ndarray | Mapping[str, object], name: str
) -> tuple[np.ndarray, str | None]:
    if isinstance(values, Mapping):
        if "cell_id" not in values or "block_correction_ratios" not in values:
            raise ValueError("replication rows must contain cell_id and block_correction_ratios")
        cell_id = values["cell_id"]
        if not isinstance(cell_id, str):
            raise ValueError("replication cell_id must be a string")
        return _finite_block_values(values["block_correction_ratios"], name), cell_id
    return _finite_block_values(values, name), None


def summarize_cell(
    sample: T12CoupledSample,
    *,
    k: int,
    N: int,
    p_bias: float,
    blocks: int = 40,
    comparisons: int = 36,
) -> dict[str, object]:
    """Summarize a run using contiguous path blocks as independent units."""
    if not isinstance(sample, T12CoupledSample):
        raise ValueError("sample must be a T12CoupledSample")
    N = _positive_integer(N, "N")
    blocks = _positive_integer(blocks, "blocks", minimum=2)
    comparisons = _positive_integer(comparisons, "comparisons")
    stopping_times = _finite_block_values(sample.stopping_times, "stopping_times")
    if stopping_times.size % blocks:
        raise ValueError("repetitions must be divisible by blocks")

    theory = competition_theory(k, p_bias)
    paths_per_block = stopping_times.size // blocks
    block_mean_times = stopping_times.reshape(blocks, paths_per_block).mean(axis=1)
    block_scaled_corrections = (N / theory.v - block_mean_times) / math.sqrt(N)
    block_ratios = block_scaled_corrections / theory.mean_correction_coefficient
    scaled_correction = float(block_scaled_corrections.mean())
    correction_ratio = float(block_ratios.mean())
    block_standard_error = float(block_ratios.std(ddof=1) / math.sqrt(blocks))
    critical = bonferroni_t_critical(blocks - 1, comparisons)
    half_width = critical * block_standard_error
    return {
        "k": theory.k,
        "N": N,
        "p_bias": theory.p_bias,
        "seed": sample.seed,
        "repetitions": int(stopping_times.size),
        "blocks": blocks,
        "paths_per_block": paths_per_block,
        "comparisons": comparisons,
        "scaled_correction": scaled_correction,
        "correction_ratio": correction_ratio,
        "block_correction_ratios": block_ratios.copy(),
        "block_standard_error": block_standard_error,
        "simultaneous_critical": critical,
        "simultaneous_half_width": half_width,
        "simultaneous_ci_low": correction_ratio - half_width,
        "simultaneous_ci_high": correction_ratio + half_width,
    }


def gaussian_reference_quantiles(
    k: int,
    p_bias: float,
    *,
    base_draws: int = 1_000_000,
    seed: int = 2026071814,
    quantile_levels: tuple[float, ...] = (0.025, 0.5, 0.975),
) -> dict[str, object]:
    """Deterministic antithetic Gaussian diagnostic; never an inferential input."""
    base_draws = _positive_integer(base_draws, "base_draws")
    seed = _positive_integer(seed, "seed", minimum=0)
    levels = np.asarray(quantile_levels, dtype=np.float64)
    if levels.ndim != 1 or levels.size == 0 or not np.all(np.isfinite(levels)) or np.any((levels < 0.0) | (levels > 1.0)):
        raise ValueError("quantile_levels must be finite probabilities in [0, 1]")

    theory = competition_theory(k, p_bias)
    _, covariance = closed_form_peripheral_moments(k, p_bias)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance / theory.v)
    if np.any(eigenvalues < -1e-12):
        raise RuntimeError("Gaussian reference covariance is not positive semidefinite")
    factor = eigenvectors * np.sqrt(np.clip(eigenvalues, 0.0, None))
    standard = np.random.default_rng(seed).standard_normal((base_draws, theory.peripheral_count))
    gaussian = np.vstack((standard @ factor.T, -standard @ factor.T))
    scaled_corrections = -np.min(gaussian, axis=1) / theory.v
    correction_ratios = scaled_corrections / theory.mean_correction_coefficient
    metadata = {
        "reference_seed": seed,
        "reference_sample_size": 2 * base_draws,
        "base_draws": base_draws,
    }
    return {
        "quantile_levels": levels.copy(),
        "scaled_correction_quantiles": np.quantile(scaled_corrections, levels),
        "correction_ratio_quantiles": np.quantile(correction_ratios, levels),
        "covariance": covariance / theory.v,
        "eigenvalues": eigenvalues,
        "metadata": metadata,
        **metadata,
    }


def compare_replication_rows(
    first: np.ndarray | Mapping[str, object],
    second: np.ndarray | Mapping[str, object],
    *,
    comparisons: int = 36,
    first_cell_id: str | None = None,
    second_cell_id: str | None = None,
) -> dict[str, float]:
    """Welch simultaneous interval for the difference between two block runs."""
    first_values, inferred_first_cell_id = _replication_block_values(first, "first replication blocks")
    second_values, inferred_second_cell_id = _replication_block_values(second, "second replication blocks")
    if first_cell_id is not None and inferred_first_cell_id not in (None, first_cell_id):
        raise ValueError("replication cells must match")
    if second_cell_id is not None and inferred_second_cell_id not in (None, second_cell_id):
        raise ValueError("replication cells must match")
    first_cell_id = first_cell_id if first_cell_id is not None else inferred_first_cell_id
    second_cell_id = second_cell_id if second_cell_id is not None else inferred_second_cell_id
    if first_cell_id != second_cell_id:
        raise ValueError("replication cells must match")
    comparisons = _positive_integer(comparisons, "comparisons")
    n1, n2 = first_values.size, second_values.size
    mean1, mean2 = float(first_values.mean()), float(second_values.mean())
    s1, s2 = float(first_values.std(ddof=1)), float(second_values.std(ddof=1))
    se2 = s1 * s1 / n1 + s2 * s2 / n2
    difference = mean1 - mean2
    if se2 == 0.0:
        critical = float(student_t.ppf(1.0 - 0.05 / (2.0 * comparisons), df=math.inf))
        return {
            "difference": difference,
            "welch_standard_error": 0.0,
            "degrees_of_freedom": math.inf,
            "simultaneous_critical": critical,
            "ci_low": difference,
            "ci_high": difference,
        }

    denominator = (s1 * s1 / n1) ** 2 / (n1 - 1) + (s2 * s2 / n2) ** 2 / (n2 - 1)
    degrees_of_freedom = se2 * se2 / denominator
    critical = float(student_t.ppf(1.0 - 0.05 / (2.0 * comparisons), df=degrees_of_freedom))
    standard_error = math.sqrt(se2)
    half_width = critical * standard_error
    return {
        "difference": difference,
        "welch_standard_error": standard_error,
        "degrees_of_freedom": degrees_of_freedom,
        "simultaneous_critical": critical,
        "ci_low": difference - half_width,
        "ci_high": difference + half_width,
    }


_PRIMARY_FIELDS = (
    "cell_id",
    "k",
    "N",
    "p_bias",
    "seed",
    "repetitions",
    "blocks",
    "paths_per_block",
    "comparisons",
    "censored_count",
    "mean_stopping_time",
    "sd_stopping_time",
    "tstar",
    "theory_correction_coefficient",
    "scaled_correction",
    "correction_ratio",
    "block_correction_ratios",
    "block_standard_error",
    "simultaneous_critical",
    "simultaneous_half_width",
    "simultaneous_ci_low",
    "simultaneous_ci_high",
    "precision_gate_applicable",
    "precision_gate_pass",
    "local_proxy_scaled_absolute_error_mean",
    "local_proxy_scaled_absolute_error_median",
    "local_proxy_scaled_absolute_error_q90",
    "scaled_correction_q10",
    "scaled_correction_q25",
    "scaled_correction_q50",
    "scaled_correction_q75",
    "scaled_correction_q90",
    "gaussian_reference_q10",
    "gaussian_reference_q25",
    "gaussian_reference_q50",
    "gaussian_reference_q75",
    "gaussian_reference_q90",
    "quantile_difference_q10",
    "quantile_difference_q25",
    "quantile_difference_q50",
    "quantile_difference_q75",
    "quantile_difference_q90",
    "reference_seed",
    "reference_sample_size",
)

_MOMENT_FIELDS = (
    "k",
    "p_bias",
    "probability_sum_error",
    "mean_max_abs_error",
    "raw_second_max_abs_error",
    "covariance_max_abs_error",
    "difference_variance_error",
    "maximum_error",
    "gate_pass",
)

_EXACT_ANCHOR_FIELDS = (
    "cell_id",
    "k",
    "N",
    "p_bias",
    "state_count",
    "repetitions",
    "blocks",
    "paths_per_block",
    "comparisons",
    "seed",
    "exact_mean",
    "mc_mean",
    "mc_sd",
    "block_standard_error",
    "simultaneous_critical",
    "simultaneous_half_width",
    "simultaneous_ci_low",
    "simultaneous_ci_high",
    "contains_exact_mean",
    "max_abs_residual",
    "censored_count",
    "gate_pass",
)

_COMPARISON_FIELDS = (
    "cell_id",
    "k",
    "N",
    "p_bias",
    "primary_seed",
    "replication_seed",
    "primary_repetitions",
    "replication_repetitions",
    "primary_blocks",
    "replication_blocks",
    "comparisons",
    "primary_correction_ratio",
    "replication_correction_ratio",
    "difference",
    "welch_standard_error",
    "degrees_of_freedom",
    "simultaneous_critical",
    "ci_low",
    "ci_high",
    "contains_zero",
    "primary_half_width",
    "replication_half_width",
    "precision_gate_pass",
    "replication_gate_pass",
    "gate_pass",
)


def _prepare_output(output: Path) -> None:
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)


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


def _atomic_write_text(path: Path, value: str) -> None:
    temporary = _temporary_sibling(path)
    try:
        temporary.write_text(value, encoding="utf-8", newline="")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write_csv(
    path: Path, fieldnames: Sequence[str], rows: Sequence[Mapping[str, object]]
) -> None:
    temporary = _temporary_sibling(path)
    try:
        with temporary.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="raise"
            )
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def _software_metadata() -> dict[str, str]:
    return {
        "numpy": np.__version__,
        "pipeline_version": PIPELINE_VERSION,
        "platform": platform.platform(),
        "python": platform.python_version(),
        "scipy": scipy.__version__,
    }


def _write_metadata_and_manifest(
    output: Path,
    metadata_name: str,
    metadata: dict[str, object],
    artifact_paths: Sequence[Path],
) -> None:
    metadata_path = output / metadata_name
    manifest_path = output / "SHA256SUMS.txt"
    all_paths = [*artifact_paths, metadata_path, manifest_path]
    metadata["files"] = [str(path.resolve()) for path in all_paths]
    _atomic_write_text(
        metadata_path,
        json.dumps(metadata, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        + "\n",
    )
    hashed_paths = sorted(
        (path for path in output.iterdir() if path.name != manifest_path.name),
        key=lambda path: path.name,
    )
    _atomic_write_text(
        manifest_path,
        "".join(f"{_file_sha256(path)}  {path.name}\n" for path in hashed_paths),
    )


def _validate_run_shape(repetitions: int, blocks: int) -> tuple[int, int]:
    repetitions = _positive_integer(repetitions, "repetitions", minimum=2)
    blocks = _positive_integer(blocks, "blocks", minimum=2)
    if repetitions % blocks:
        raise ValueError("repetitions must be divisible by blocks")
    return repetitions, blocks


def _moment_diagnostic_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for k, p_bias in product((3, 4, 5), (1.25, 1.5, 2.0)):
        increments, probabilities = enumerate_peripheral_increment_law(k, p_bias)
        enumerated_mean = probabilities @ increments
        raw_second = np.einsum("r,ri,rj->ij", probabilities, increments, increments)
        enumerated_covariance = raw_second - np.outer(enumerated_mean, enumerated_mean)
        expected_mean, expected_covariance = closed_form_peripheral_moments(k, p_bias)
        expected_raw_second = expected_covariance + np.outer(expected_mean, expected_mean)
        errors = {
            "probability_sum_error": abs(float(probabilities.sum()) - 1.0),
            "mean_max_abs_error": float(np.max(np.abs(enumerated_mean - expected_mean))),
            "raw_second_max_abs_error": float(
                np.max(np.abs(raw_second - expected_raw_second))
            ),
            "covariance_max_abs_error": float(
                np.max(np.abs(enumerated_covariance - expected_covariance))
            ),
            "difference_variance_error": abs(
                float(enumerated_covariance[0, 0] - enumerated_covariance[0, 1])
                - 2.0 / (k - 1)
            ),
        }
        maximum_error = max(errors.values())
        rows.append(
            {
                "k": k,
                "p_bias": p_bias,
                **errors,
                "maximum_error": maximum_error,
                "gate_pass": maximum_error < DETERMINISTIC_TOLERANCE,
            }
        )
    return rows


def _primary_row(
    scenario: T12Scenario,
    sample: T12CoupledSample,
    *,
    blocks: int,
    quick: bool,
    gaussian_reference: Mapping[str, object],
) -> dict[str, object]:
    summary = summarize_cell(
        sample,
        k=scenario.k,
        N=scenario.N,
        p_bias=scenario.p_bias,
        blocks=blocks,
        comparisons=PRIMARY_COMPARISONS,
    )
    theory = competition_theory(scenario.k, scenario.p_bias)
    values = sample.stopping_times.astype(np.float64)
    scaled_corrections = (scenario.N / theory.v - values) / math.sqrt(scenario.N)
    levels = np.asarray(gaussian_reference["quantile_levels"], dtype=np.float64)
    expected_levels = np.asarray((0.1, 0.25, 0.5, 0.75, 0.9))
    if not np.array_equal(levels, expected_levels):
        raise RuntimeError("Gaussian reference quantile levels do not match the artifact schema")
    empirical_quantiles = np.quantile(scaled_corrections, levels)
    reference_quantiles = np.asarray(
        gaussian_reference["scaled_correction_quantiles"], dtype=np.float64
    )
    quantile_differences = empirical_quantiles - reference_quantiles
    local_scaled_error = np.abs(values - sample.local_proxy_times) / math.sqrt(scenario.N)
    half_width = float(summary["simultaneous_half_width"])
    precision_gate_applicable = not quick
    return {
        "cell_id": scenario.cell_id,
        "k": scenario.k,
        "N": scenario.N,
        "p_bias": scenario.p_bias,
        "seed": scenario.seed,
        "repetitions": int(values.size),
        "blocks": blocks,
        "paths_per_block": int(summary["paths_per_block"]),
        "comparisons": PRIMARY_COMPARISONS,
        "censored_count": sample.censored_count,
        "mean_stopping_time": float(values.mean()),
        "sd_stopping_time": float(values.std(ddof=1)),
        "tstar": scenario.N / theory.v,
        "theory_correction_coefficient": theory.mean_correction_coefficient,
        "scaled_correction": float(summary["scaled_correction"]),
        "correction_ratio": float(summary["correction_ratio"]),
        "block_correction_ratios": json.dumps(
            np.asarray(summary["block_correction_ratios"], dtype=float).tolist(),
            separators=(",", ":"),
        ),
        "block_standard_error": float(summary["block_standard_error"]),
        "simultaneous_critical": float(summary["simultaneous_critical"]),
        "simultaneous_half_width": half_width,
        "simultaneous_ci_low": float(summary["simultaneous_ci_low"]),
        "simultaneous_ci_high": float(summary["simultaneous_ci_high"]),
        "precision_gate_applicable": precision_gate_applicable,
        "precision_gate_pass": precision_gate_applicable
        and half_width <= MAX_SIMULTANEOUS_HALF_WIDTH,
        "local_proxy_scaled_absolute_error_mean": float(local_scaled_error.mean()),
        "local_proxy_scaled_absolute_error_median": float(np.median(local_scaled_error)),
        "local_proxy_scaled_absolute_error_q90": float(np.quantile(local_scaled_error, 0.9)),
        "scaled_correction_q10": float(empirical_quantiles[0]),
        "scaled_correction_q25": float(empirical_quantiles[1]),
        "scaled_correction_q50": float(empirical_quantiles[2]),
        "scaled_correction_q75": float(empirical_quantiles[3]),
        "scaled_correction_q90": float(empirical_quantiles[4]),
        "gaussian_reference_q10": float(reference_quantiles[0]),
        "gaussian_reference_q25": float(reference_quantiles[1]),
        "gaussian_reference_q50": float(reference_quantiles[2]),
        "gaussian_reference_q75": float(reference_quantiles[3]),
        "gaussian_reference_q90": float(reference_quantiles[4]),
        "quantile_difference_q10": float(quantile_differences[0]),
        "quantile_difference_q25": float(quantile_differences[1]),
        "quantile_difference_q50": float(quantile_differences[2]),
        "quantile_difference_q75": float(quantile_differences[3]),
        "quantile_difference_q90": float(quantile_differences[4]),
        "reference_seed": int(gaussian_reference["reference_seed"]),
        "reference_sample_size": int(gaussian_reference["reference_sample_size"]),
    }


def _run_scenario_rows(
    scenarios: Sequence[T12Scenario],
    *,
    repetitions: int,
    blocks: int,
    quick: bool,
    reference_base_draws: int,
    progress: bool,
) -> tuple[list[dict[str, object]], int]:
    cache: dict[tuple[int, float], Mapping[str, object]] = {}
    rows: list[dict[str, object]] = []
    censored_count = 0
    for index, scenario in enumerate(sorted(scenarios, key=lambda item: item.cell_id), start=1):
        reference_key = (scenario.k, scenario.p_bias)
        if reference_key not in cache:
            cache[reference_key] = gaussian_reference_quantiles(
                scenario.k,
                scenario.p_bias,
                base_draws=reference_base_draws,
                seed=REFERENCE_SEED,
                quantile_levels=(0.1, 0.25, 0.5, 0.75, 0.9),
            )
        sample = simulate_coupled_competition(
            scenario.k,
            scenario.N,
            scenario.p_bias,
            repetitions,
            scenario.seed,
        )
        censored_count += sample.censored_count
        row = _primary_row(
            scenario,
            sample,
            blocks=blocks,
            quick=quick,
            gaussian_reference=cache[reference_key],
        )
        rows.append(row)
        if progress:
            print(
                f"cell={index}/{len(scenarios)} id={scenario.cell_id} "
                f"ratio={float(row['correction_ratio']):.6f} "
                f"half_width={float(row['simultaneous_half_width']):.6f}",
                flush=True,
            )
    return rows, censored_count


def run_t12_validation(
    output: Path,
    repetitions: int = FORMAL_REPETITIONS,
    blocks: int = FORMAL_BLOCKS,
    master_seed: int = 2026071812,
    quick: bool = False,
    reference_base_draws: int | None = None,
    progress: bool = False,
) -> dict[str, object]:
    """Run the fixed 36-cell grid and write immutable, hashed artifacts."""
    started = time.perf_counter()
    repetitions, blocks = _validate_run_shape(repetitions, blocks)
    master_seed = _positive_integer(master_seed, "master_seed", minimum=0)
    if not isinstance(quick, bool):
        raise ValueError("quick must be a boolean")
    if reference_base_draws is None:
        reference_base_draws = 10_000 if quick else REFERENCE_BASE_DRAWS
    reference_base_draws = _positive_integer(
        reference_base_draws, "reference_base_draws"
    )
    output = Path(output)
    _prepare_output(output)

    scenarios = build_scenarios(master_seed)
    moment_rows = _moment_diagnostic_rows()
    primary_rows, censored_count = _run_scenario_rows(
        scenarios,
        repetitions=repetitions,
        blocks=blocks,
        quick=quick,
        reference_base_draws=reference_base_draws,
        progress=progress,
    )
    moment_rows.sort(key=lambda row: (int(row["k"]), float(row["p_bias"])))
    deterministic_failures = [
        f"k{row['k']}-p{float(row['p_bias']):g}:error={float(row['maximum_error']):.17g}"
        for row in moment_rows
        if not bool(row["gate_pass"])
    ]
    precision_failures = [
        f"{row['cell_id']}:half_width={float(row['simultaneous_half_width']):.17g}"
        for row in primary_rows
        if float(row["simultaneous_half_width"]) > MAX_SIMULTANEOUS_HALF_WIDTH
    ]
    precision_gate_applicable = not quick
    precision_gate_pass = precision_gate_applicable and not precision_failures

    primary_path = output / "t12-primary.csv"
    moment_path = output / "t12-moment-diagnostics.csv"
    _atomic_write_csv(primary_path, _PRIMARY_FIELDS, primary_rows)
    _atomic_write_csv(moment_path, _MOMENT_FIELDS, moment_rows)
    config = {
        "blocks": blocks,
        "comparisons": PRIMARY_COMPARISONS,
        "deterministic_tolerance": DETERMINISTIC_TOLERANCE,
        "formal_blocks": FORMAL_BLOCKS,
        "formal_repetitions": FORMAL_REPETITIONS,
        "master_seed": master_seed,
        "maximum_simultaneous_half_width": MAX_SIMULTANEOUS_HALF_WIDTH,
        "quick": quick,
        "reference_base_draws": reference_base_draws,
        "reference_seed": REFERENCE_SEED,
        "repetitions": repetitions,
    }
    scenario_payload = [
        {
            "cell_id": scenario.cell_id,
            "k": scenario.k,
            "N": scenario.N,
            "p_bias": float(scenario.p_bias).hex(),
            "seed": scenario.seed,
        }
        for scenario in sorted(scenarios, key=lambda item: item.cell_id)
    ]
    metadata: dict[str, object] = {
        "all_gates_pass": not deterministic_failures
        and censored_count == 0
        and (not precision_gate_applicable or not precision_failures),
        "censored_count": censored_count,
        "claim_boundary": "有限网格数值诊断不证明渐近定理",
        "config": config,
        "config_sha256": _canonical_sha256(config),
        "deterministic_moment_gate_failures": deterministic_failures,
        "deterministic_moment_gate_pass": not deterministic_failures,
        "input_sha256": _canonical_sha256(scenario_payload),
        "model": "t12-positive-drift-competition",
        "precision_gate_applicable": precision_gate_applicable,
        "precision_gate_failures": precision_failures,
        "precision_gate_pass": precision_gate_pass,
        "quick": quick,
        "row_counts": {"moments": len(moment_rows), "primary": len(primary_rows)},
        "runtime_seconds": time.perf_counter() - started,
        "seeds": [int(row["seed"]) for row in primary_rows],
        "simulation_algorithm": "coupled free walk and uncensored first depletion",
        "stop_event": "first balance coordinate equal to zero",
        **_software_metadata(),
    }
    _write_metadata_and_manifest(
        output,
        "t12-run-metadata.json",
        metadata,
        (primary_path, moment_path),
    )
    return metadata


def run_exact_anchors(
    output: Path,
    N: int = 6,
    repetitions: int = EXACT_REPETITIONS,
    blocks: int = EXACT_BLOCKS,
    parameter_pairs: Sequence[tuple[int, float]] = tuple(
        product((3, 4, 5), (1.25, 1.5, 2.0))
    ),
    master_seed: int = EXACT_MASTER_SEED,
    progress: bool = False,
) -> dict[str, object]:
    """Compare the coupled simulator with exact symmetric-state Markov means."""
    started = time.perf_counter()
    N = _positive_integer(N, "N")
    repetitions, blocks = _validate_run_shape(repetitions, blocks)
    master_seed = _positive_integer(master_seed, "master_seed", minimum=0)
    normalized_pairs: list[tuple[int, float]] = []
    for k, p_bias in parameter_pairs:
        _validate_parameters(k, p_bias)
        normalized_pairs.append((int(k), float(p_bias)))
    if not normalized_pairs or len(set(normalized_pairs)) != len(normalized_pairs):
        raise ValueError("parameter_pairs must be non-empty and unique")
    output = Path(output)
    _prepare_output(output)

    rows: list[dict[str, object]] = []
    failures: list[str] = []
    censored_count = 0
    for index, (k, p_bias) in enumerate(sorted(normalized_pairs)):
        exact_mean, state_count, residual = exact_drifted_markov_mean(k, N, p_bias)
        seed = master_seed * ANCHOR_COMPARISONS + index
        sample = simulate_coupled_competition(k, N, p_bias, repetitions, seed)
        censored_count += sample.censored_count
        values = sample.stopping_times.astype(np.float64)
        block_means = values.reshape(blocks, repetitions // blocks).mean(axis=1)
        block_standard_error = float(block_means.std(ddof=1) / math.sqrt(blocks))
        critical = bonferroni_t_critical(blocks - 1, ANCHOR_COMPARISONS)
        half_width = critical * block_standard_error
        mc_mean = float(block_means.mean())
        ci_low, ci_high = mc_mean - half_width, mc_mean + half_width
        contains_exact = ci_low <= exact_mean <= ci_high
        gate_pass = (
            residual < EXACT_RESIDUAL_TOLERANCE
            and contains_exact
            and sample.censored_count == 0
        )
        cell_id = f"k{k}-p{p_bias:g}-N{N}"
        if not gate_pass:
            failures.append(
                f"{cell_id}:residual={residual:.17g}:contains_exact={contains_exact}"
            )
        rows.append(
            {
                "cell_id": cell_id,
                "k": k,
                "N": N,
                "p_bias": p_bias,
                "state_count": state_count,
                "repetitions": repetitions,
                "blocks": blocks,
                "paths_per_block": repetitions // blocks,
                "comparisons": ANCHOR_COMPARISONS,
                "seed": seed,
                "exact_mean": exact_mean,
                "mc_mean": mc_mean,
                "mc_sd": float(values.std(ddof=1)),
                "block_standard_error": block_standard_error,
                "simultaneous_critical": critical,
                "simultaneous_half_width": half_width,
                "simultaneous_ci_low": ci_low,
                "simultaneous_ci_high": ci_high,
                "contains_exact_mean": contains_exact,
                "max_abs_residual": residual,
                "censored_count": sample.censored_count,
                "gate_pass": gate_pass,
            }
        )
        if progress:
            print(
                f"anchor={index + 1}/{len(normalized_pairs)} id={cell_id} "
                f"exact={exact_mean:.6f} mc={mc_mean:.6f} pass={gate_pass}",
                flush=True,
            )

    anchor_path = output / "t12-exact-anchors.csv"
    _atomic_write_csv(anchor_path, _EXACT_ANCHOR_FIELDS, rows)
    metadata: dict[str, object] = {
        "all_gates_pass": not failures,
        "anchor_gate_failures": failures,
        "anchor_gate_pass": not failures,
        "blocks": blocks,
        "censored_count": censored_count,
        "comparisons": ANCHOR_COMPARISONS,
        "exact_residual_tolerance": EXACT_RESIDUAL_TOLERANCE,
        "input_sha256": _canonical_sha256(
            {"N": N, "parameter_pairs": normalized_pairs, "master_seed": master_seed}
        ),
        "master_seed": master_seed,
        "maximum_residual": max(float(row["max_abs_residual"]) for row in rows),
        "model": "t12-positive-drift-exact-anchors",
        "N": N,
        "parameter_pairs": [list(pair) for pair in normalized_pairs],
        "repetitions": repetitions,
        "row_count": len(rows),
        "runtime_seconds": time.perf_counter() - started,
        "seeds": [int(row["seed"]) for row in rows],
        "simulation_algorithm": "coupled free walk and uncensored first depletion",
        "stop_event": "first balance coordinate equal to zero",
        **_software_metadata(),
    }
    _write_metadata_and_manifest(
        output,
        "t12-exact-anchor-metadata.json",
        metadata,
        (anchor_path,),
    )
    return metadata


def _read_csv_rows(path: Path) -> list[dict[str, str]]:
    path = Path(path)
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if tuple(reader.fieldnames or ()) != _PRIMARY_FIELDS:
            raise ValueError(
                f"primary CSV schema must exactly match the declared full schema: {path}"
            )
        rows = list(reader)
    if not rows:
        raise ValueError(f"CSV contains no data rows: {path}")
    if not all(row.get("cell_id") for row in rows):
        raise ValueError(f"CSV rows must contain cell_id: {path}")
    if len({row["cell_id"] for row in rows}) != len(rows):
        raise ValueError(f"CSV contains duplicate cell_id values: {path}")
    return rows


def _replication_config(row: Mapping[str, str]) -> tuple[object, ...]:
    return (
        row["cell_id"],
        int(row["k"]),
        int(row["N"]),
        float(row["p_bias"]),
        int(row["repetitions"]),
        int(row["blocks"]),
        int(row["paths_per_block"]),
        int(row["comparisons"]),
        row["precision_gate_applicable"],
        float(row["tstar"]),
        float(row["theory_correction_coefficient"]),
        int(row["reference_seed"]),
        int(row["reference_sample_size"]),
    )


def _validate_primary_contract(
    rows: Sequence[Mapping[str, str]], path: Path
) -> tuple[set[int], dict[str, Mapping[str, str]]]:
    expected = {
        scenario.cell_id: (scenario.k, scenario.N, scenario.p_bias)
        for scenario in build_scenarios(master_seed=0)
    }
    by_id = {row["cell_id"]: row for row in rows}
    if len(rows) != PRIMARY_COMPARISONS or set(by_id) != set(expected):
        raise ValueError(
            f"primary CSV must contain the exact canonical 36-cell grid: {path}"
        )

    for cell_id in sorted(expected):
        row = by_id[cell_id]
        observed = (int(row["k"]), int(row["N"]), float(row["p_bias"]))
        if observed != expected[cell_id]:
            raise ValueError(f"noncanonical cell configuration for {cell_id}: {path}")
        repetitions = _positive_integer(int(row["repetitions"]), "repetitions", minimum=2)
        blocks = _positive_integer(int(row["blocks"]), "blocks", minimum=2)
        paths_per_block = _positive_integer(
            int(row["paths_per_block"]), "paths_per_block"
        )
        if repetitions % blocks or paths_per_block != repetitions // blocks:
            raise ValueError(f"invalid run-shape configuration for {cell_id}: {path}")
        if int(row["comparisons"]) != PRIMARY_COMPARISONS:
            raise ValueError(
                f"comparisons must equal 36 for every primary cell: {cell_id}"
            )
        if row["precision_gate_applicable"] not in ("True", "False"):
            raise ValueError(
                f"invalid precision_gate_applicable for {cell_id}: {path}"
            )
        _positive_integer(int(row["reference_seed"]), "reference_seed", minimum=0)
        _positive_integer(int(row["reference_sample_size"]), "reference_sample_size")

    seeds = {int(row["seed"]) for row in rows}
    if len(seeds) != PRIMARY_COMPARISONS:
        raise ValueError(f"primary CSV must contain exactly 36 unique seeds: {path}")
    return seeds, by_id


def _parse_block_ratios(row: Mapping[str, str]) -> np.ndarray:
    try:
        values = np.asarray(json.loads(row["block_correction_ratios"]), dtype=np.float64)
    except (json.JSONDecodeError, TypeError, ValueError) as error:
        raise ValueError(f"invalid block_correction_ratios for {row['cell_id']}") from error
    blocks = int(row["blocks"])
    if values.ndim != 1 or values.size != blocks or not np.all(np.isfinite(values)):
        raise ValueError(
            f"block_correction_ratios must contain {blocks} finite values for {row['cell_id']}"
        )
    return values


def run_replication_comparison(
    primary: Path,
    replication: Path,
    output: Path,
    *,
    progress: bool = False,
) -> dict[str, object]:
    """Compare two complete primary CSVs without mutating either run directory."""
    started = time.perf_counter()
    primary = Path(primary)
    replication = Path(replication)
    first_rows = _read_csv_rows(primary)
    second_rows = _read_csv_rows(replication)
    first_seeds, first_by_id = _validate_primary_contract(first_rows, primary)
    second_seeds, second_by_id = _validate_primary_contract(second_rows, replication)

    for cell_id in sorted(first_by_id):
        if _replication_config(first_by_id[cell_id]) != _replication_config(
            second_by_id[cell_id]
        ):
            raise ValueError(f"replication configuration mismatch for {cell_id}")
    if not first_seeds.isdisjoint(second_seeds):
        raise ValueError("replication seeds must be disjoint")

    rows: list[dict[str, object]] = []
    failing_cells: list[str] = []
    for index, cell_id in enumerate(sorted(first_by_id), start=1):
        first = first_by_id[cell_id]
        second = second_by_id[cell_id]
        comparisons = int(first["comparisons"])
        first_values = _parse_block_ratios(first)
        second_values = _parse_block_ratios(second)
        comparison = compare_replication_rows(
            {"cell_id": cell_id, "block_correction_ratios": first_values},
            {"cell_id": cell_id, "block_correction_ratios": second_values},
            comparisons=comparisons,
        )
        primary_half_width = float(first["simultaneous_half_width"])
        replication_half_width = float(second["simultaneous_half_width"])
        precision_gate_pass = (
            primary_half_width <= MAX_SIMULTANEOUS_HALF_WIDTH
            and replication_half_width <= MAX_SIMULTANEOUS_HALF_WIDTH
        )
        contains_zero = float(comparison["ci_low"]) <= 0.0 <= float(
            comparison["ci_high"]
        )
        gate_pass = precision_gate_pass and contains_zero
        if not gate_pass:
            failing_cells.append(cell_id)
        rows.append(
            {
                "cell_id": cell_id,
                "k": int(first["k"]),
                "N": int(first["N"]),
                "p_bias": float(first["p_bias"]),
                "primary_seed": int(first["seed"]),
                "replication_seed": int(second["seed"]),
                "primary_repetitions": int(first["repetitions"]),
                "replication_repetitions": int(second["repetitions"]),
                "primary_blocks": int(first["blocks"]),
                "replication_blocks": int(second["blocks"]),
                "comparisons": comparisons,
                "primary_correction_ratio": float(first_values.mean()),
                "replication_correction_ratio": float(second_values.mean()),
                **comparison,
                "contains_zero": contains_zero,
                "primary_half_width": primary_half_width,
                "replication_half_width": replication_half_width,
                "precision_gate_pass": precision_gate_pass,
                "replication_gate_pass": contains_zero,
                "gate_pass": gate_pass,
            }
        )
        if progress:
            print(
                f"comparison={index}/{len(first_by_id)} id={cell_id} "
                f"difference={float(comparison['difference']):.6f} pass={gate_pass}",
                flush=True,
            )

    output = Path(output)
    _prepare_output(output)
    comparison_path = output / "t12-replication-comparison.csv"
    failing_path = output / "t12-failing-cells.txt"
    _atomic_write_csv(comparison_path, _COMPARISON_FIELDS, rows)
    _atomic_write_text(
        failing_path, "".join(f"{cell_id}\n" for cell_id in failing_cells)
    )
    metadata: dict[str, object] = {
        "all_gates_pass": not failing_cells,
        "all_intervals_contain_zero": all(bool(row["contains_zero"]) for row in rows),
        "comparisons": len(rows),
        "failing_cell_count": len(failing_cells),
        "failing_cells": failing_cells,
        "input_sha256": {
            "primary": _file_sha256(primary),
            "replication": _file_sha256(replication),
        },
        "maximum_primary_half_width": max(
            float(row["primary_half_width"]) for row in rows
        ),
        "maximum_replication_half_width": max(
            float(row["replication_half_width"]) for row in rows
        ),
        "model": "t12-independent-replication-comparison",
        "primary": str(primary.resolve()),
        "replication": str(replication.resolve()),
        "row_count": len(rows),
        "runtime_seconds": time.perf_counter() - started,
        "seeds_disjoint": True,
        **_software_metadata(),
    }
    _write_metadata_and_manifest(
        output,
        "t12-replication-comparison-metadata.json",
        metadata,
        (comparison_path, failing_path),
    )
    return metadata


def _selected_scenarios(
    cells_file: Path, master_seed: int
) -> tuple[T12Scenario, ...]:
    cells_file = Path(cells_file)
    requested = [
        line.strip()
        for line in cells_file.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    if not requested:
        raise ValueError("cells_file must contain at least one cell ID")
    if len(set(requested)) != len(requested):
        raise ValueError("cells_file must not contain duplicate cell IDs")
    scenario_by_id = {
        scenario.cell_id: scenario for scenario in build_scenarios(master_seed)
    }
    unknown = sorted(set(requested) - set(scenario_by_id))
    if unknown:
        raise ValueError(f"cells_file contains unknown cell IDs: {', '.join(unknown)}")
    return tuple(scenario_by_id[cell_id] for cell_id in sorted(requested))


def run_sensitivity(
    output: Path,
    *,
    cells_file: Path,
    repetitions: int = SENSITIVITY_REPETITIONS,
    blocks: int = SENSITIVITY_BLOCKS,
    master_seed: int = 2026071815,
    reference_base_draws: int = REFERENCE_BASE_DRAWS,
    progress: bool = False,
) -> dict[str, object]:
    """Run the predeclared higher-repetition grid for selected failing cells."""
    started = time.perf_counter()
    repetitions, blocks = _validate_run_shape(repetitions, blocks)
    master_seed = _positive_integer(master_seed, "master_seed", minimum=0)
    reference_base_draws = _positive_integer(
        reference_base_draws, "reference_base_draws"
    )
    scenarios = _selected_scenarios(cells_file, master_seed)
    output = Path(output)
    _prepare_output(output)
    rows, censored_count = _run_scenario_rows(
        scenarios,
        repetitions=repetitions,
        blocks=blocks,
        quick=False,
        reference_base_draws=reference_base_draws,
        progress=progress,
    )
    failures = [
        str(row["cell_id"])
        for row in rows
        if not bool(row["precision_gate_pass"]) or int(row["censored_count"]) != 0
    ]
    sensitivity_path = output / "t12-sensitivity.csv"
    _atomic_write_csv(sensitivity_path, _PRIMARY_FIELDS, rows)
    metadata: dict[str, object] = {
        "all_gates_pass": not failures,
        "blocks": blocks,
        "cell_ids": [str(row["cell_id"]) for row in rows],
        "cells_file": str(Path(cells_file).resolve()),
        "cells_file_sha256": _file_sha256(Path(cells_file)),
        "censored_count": censored_count,
        "failing_cells": failures,
        "master_seed": master_seed,
        "maximum_simultaneous_half_width": max(
            float(row["simultaneous_half_width"]) for row in rows
        ),
        "model": "t12-predeclared-sensitivity",
        "reference_base_draws": reference_base_draws,
        "reference_seed": REFERENCE_SEED,
        "repetitions": repetitions,
        "row_count": len(rows),
        "runtime_seconds": time.perf_counter() - started,
        "seeds": [int(row["seed"]) for row in rows],
        "simulation_algorithm": "coupled free walk and uncensored first depletion",
        "stop_event": "first balance coordinate equal to zero",
        **_software_metadata(),
    }
    _write_metadata_and_manifest(
        output,
        "t12-sensitivity-metadata.json",
        metadata,
        (sensitivity_path,),
    )
    return metadata


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--formal", action="store_true", help="run the formal 36-cell grid")
    modes.add_argument("--quick", action="store_true", help="run a small 36-cell smoke grid")
    modes.add_argument("--exact-anchors", action="store_true", help="run exact Markov anchors")
    modes.add_argument("--compare", action="store_true", help="compare two primary CSVs")
    modes.add_argument("--sensitivity", action="store_true", help="run selected failing cells")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int)
    parser.add_argument("--blocks", type=int)
    parser.add_argument("--master-seed", type=int)
    parser.add_argument("--reference-base-draws", type=int)
    parser.add_argument("--N", type=int, default=6)
    parser.add_argument("--primary", type=Path)
    parser.add_argument("--replication", type=Path)
    parser.add_argument("--cells-file", type=Path)
    parser.add_argument("--progress", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    if arguments.compare:
        if arguments.primary is None or arguments.replication is None:
            parser.error("--compare requires --primary and --replication")
        metadata = run_replication_comparison(
            arguments.primary,
            arguments.replication,
            arguments.output,
            progress=arguments.progress,
        )
    elif arguments.exact_anchors:
        metadata = run_exact_anchors(
            arguments.output,
            N=arguments.N,
            repetitions=arguments.repetitions
            if arguments.repetitions is not None
            else EXACT_REPETITIONS,
            blocks=arguments.blocks if arguments.blocks is not None else EXACT_BLOCKS,
            master_seed=arguments.master_seed
            if arguments.master_seed is not None
            else EXACT_MASTER_SEED,
            progress=arguments.progress,
        )
    elif arguments.sensitivity:
        if arguments.cells_file is None:
            parser.error("--sensitivity requires --cells-file")
        metadata = run_sensitivity(
            arguments.output,
            cells_file=arguments.cells_file,
            repetitions=arguments.repetitions
            if arguments.repetitions is not None
            else SENSITIVITY_REPETITIONS,
            blocks=arguments.blocks
            if arguments.blocks is not None
            else SENSITIVITY_BLOCKS,
            master_seed=arguments.master_seed
            if arguments.master_seed is not None
            else 2026071815,
            reference_base_draws=arguments.reference_base_draws
            if arguments.reference_base_draws is not None
            else REFERENCE_BASE_DRAWS,
            progress=arguments.progress,
        )
    else:
        quick = bool(arguments.quick)
        metadata = run_t12_validation(
            arguments.output,
            repetitions=arguments.repetitions
            if arguments.repetitions is not None
            else (QUICK_REPETITIONS if quick else FORMAL_REPETITIONS),
            blocks=arguments.blocks
            if arguments.blocks is not None
            else (QUICK_BLOCKS if quick else FORMAL_BLOCKS),
            master_seed=arguments.master_seed
            if arguments.master_seed is not None
            else 2026071812,
            quick=quick,
            reference_base_draws=arguments.reference_base_draws,
            progress=arguments.progress,
        )
    print(
        json.dumps(
            {
                "all_gates_pass": metadata.get("all_gates_pass"),
                "model": metadata.get("model"),
                "output": str(arguments.output.resolve()),
            },
            sort_keys=True,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
