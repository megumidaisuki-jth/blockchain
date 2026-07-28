"""Independent blind validator for drift_formula_final.py.

This oracle deliberately does not import the production simulator.  It uses
Philox, samples a uniform unordered-pair index from a precomputed pair table,
and stores 30 independent batch means per scenario.
"""

from __future__ import annotations

import concurrent.futures
import csv
import hashlib
import json
import math
import platform
import sys
import time
from importlib.metadata import version
from pathlib import Path
from statistics import NormalDist

import numpy as np

from drift_formula_final import FORMULA_VERSION, predict_stopping_time


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
K_VALUES = tuple(range(3, 51))
N_VALUES = (14, 28, 56, 112)
P_VALUES = (0.325, 0.525, 0.725, 0.94, 1.00, 1.06, 1.275, 1.675, 1.875)
REPETITIONS = 6_000
BATCHES = 30
MAX_WORKERS = 4


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def independent_simulation(k: int, N: int, p_bias: float, repetitions: int) -> np.ndarray:
    seed = np.random.SeedSequence([20260716, k, N, int(round(p_bias * 1_000_000)), repetitions])
    rng = np.random.Generator(np.random.Philox(seed))
    pair_left, pair_right = np.triu_indices(k, 1)
    balances = np.full((repetitions, k), N, dtype=np.int64)
    times = np.zeros(repetitions, dtype=np.int64)
    active = np.arange(repetitions, dtype=np.int64)
    theta = p_bias / 2.0

    while active.size:
        pair_index = rng.integers(0, pair_left.size, size=active.size)
        left = pair_left[pair_index]
        right = pair_right[pair_index]
        sender = left.copy()
        receiver = right.copy()
        contains_zero = left == 0
        if np.any(contains_zero):
            toward_zero = rng.random(np.count_nonzero(contains_zero)) < theta
            other = right[contains_zero]
            sender[contains_zero] = np.where(toward_zero, other, 0)
            receiver[contains_zero] = np.where(toward_zero, 0, other)
        peripheral = ~contains_zero
        if np.any(peripheral):
            reverse = rng.random(np.count_nonzero(peripheral)) < 0.5
            original_left = left[peripheral]
            original_right = right[peripheral]
            sender[peripheral] = np.where(reverse, original_right, original_left)
            receiver[peripheral] = np.where(reverse, original_left, original_right)

        balances[active, sender] -= 1
        balances[active, receiver] += 1
        times[active] += 1
        stopped = balances[active, sender] == 0
        active = active[~stopped]
    return times


def run_scenario(args: tuple[int, int, float]) -> dict:
    k, N, p_bias = args
    values = independent_simulation(k, N, p_bias, REPETITIONS).astype(float)
    batch_size = REPETITIONS // BATCHES
    batch_means = values.reshape(BATCHES, batch_size).mean(axis=1)
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    se = sd / math.sqrt(REPETITIONS)
    return {
        "k": k,
        "N": N,
        "p_bias": p_bias,
        "repetitions": REPETITIONS,
        "mc_mean": mean,
        "mc_sd": sd,
        "mc_se": se,
        "batch_means_json": json.dumps(batch_means.tolist(), separators=(",", ":")),
    }


def write_rows(path: Path, rows: list[dict]) -> None:
    ordered = sorted(rows, key=lambda row: (row["k"], row["N"], row["p_bias"]))
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(ordered[0]))
        writer.writeheader()
        writer.writerows(ordered)


def read_rows(path: Path) -> list[dict]:
    """Load a checkpoint without changing any simulated values."""
    if not path.exists():
        return []
    rows: list[dict] = []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            rows.append(
                {
                    "k": int(row["k"]),
                    "N": int(row["N"]),
                    "p_bias": float(row["p_bias"]),
                    "repetitions": int(row["repetitions"]),
                    "mc_mean": float(row["mc_mean"]),
                    "mc_sd": float(row["mc_sd"]),
                    "mc_se": float(row["mc_se"]),
                    "batch_means_json": row["batch_means_json"],
                }
            )
    return rows


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    formula_path = ROOT / "drift_formula_final.py"
    validator_path = Path(__file__).resolve()
    manifest = {
        "formula_version": FORMULA_VERSION,
        "formula_sha256": file_sha256(formula_path),
        "validator_sha256": file_sha256(validator_path),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": version("scipy"),
        "k_values": list(K_VALUES),
        "N_values": list(N_VALUES),
        "p_values": list(P_VALUES),
        "repetitions": REPETITIONS,
        "batches": BATCHES,
        "rng": "numpy.random.Philox",
    }
    (RESULTS / "drift-final-blind2-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    scenarios = [(k, N, p) for k in K_VALUES for N in N_VALUES for p in P_VALUES]
    checkpoint = RESULTS / "drift-final-blind2.partial.csv"
    rows = read_rows(checkpoint)
    completed = {(row["k"], row["N"], row["p_bias"]) for row in rows}
    remaining = [scenario for scenario in scenarios if scenario not in completed]
    started = time.perf_counter()
    if rows:
        print(f"resuming: {len(rows)}/{len(scenarios)} already complete", flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(run_scenario, scenario) for scenario in remaining]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            rows.append(future.result())
            total_complete = len(completed) + index
            if index % 50 == 0 or index == len(remaining):
                write_rows(checkpoint, rows)
                print(
                    f"blind: {total_complete}/{len(scenarios)}, "
                    f"elapsed={time.perf_counter()-started:.1f}s",
                    flush=True,
                )

    scenario_count = len(rows)
    simultaneous_z = NormalDist().inv_cdf(1.0 - 0.05 / (2.0 * scenario_count))
    for row in rows:
        prediction = predict_stopping_time(row["k"], row["N"], row["p_bias"])
        low = max(1e-12, row["mc_mean"] - simultaneous_z * row["mc_se"])
        high = row["mc_mean"] + simultaneous_z * row["mc_se"]
        point_error = abs(prediction - row["mc_mean"]) / row["mc_mean"]
        uncertainty_error = max(abs(prediction / low - 1.0), abs(prediction / high - 1.0))
        row.update(
            {
                "formula_mean": prediction,
                "signed_relative_error": (prediction - row["mc_mean"]) / row["mc_mean"],
                "absolute_relative_error": point_error,
                "simultaneous_ci_low": low,
                "simultaneous_ci_high": high,
                "uncertainty_aware_error_upper": uncertainty_error,
                "formula_sha256": manifest["formula_sha256"],
            }
        )
    final_path = RESULTS / "drift-final-blind2-results.csv"
    write_rows(final_path, rows)
    if checkpoint.exists():
        checkpoint.unlink()

    errors = np.array([row["absolute_relative_error"] for row in rows])
    uncertainty = np.array([row["uncertainty_aware_error_upper"] for row in rows])
    signed = np.array([row["signed_relative_error"] for row in rows])
    summary = {
        "scenario_count": scenario_count,
        "mean_absolute_relative_error": float(np.mean(errors)),
        "median_absolute_relative_error": float(np.median(errors)),
        "p90_absolute_relative_error": float(np.quantile(errors, 0.90)),
        "p95_absolute_relative_error": float(np.quantile(errors, 0.95)),
        "max_absolute_relative_error": float(np.max(errors)),
        "rms_relative_error": float(np.sqrt(np.mean(signed * signed))),
        "mean_signed_relative_error": float(np.mean(signed)),
        "fraction_point_error_within_03": float(np.mean(errors <= 0.03)),
        "fraction_point_error_within_05": float(np.mean(errors <= 0.05)),
        "fraction_point_error_within_10": float(np.mean(errors <= 0.10)),
        "fraction_simultaneous_upper_within_05": float(np.mean(uncertainty <= 0.05)),
        "fraction_simultaneous_upper_within_10": float(np.mean(uncertainty <= 0.10)),
        "max_uncertainty_aware_error_upper": float(np.max(uncertainty)),
        "simultaneous_z": simultaneous_z,
        "runtime_seconds": time.perf_counter() - started,
        "formula_sha256": manifest["formula_sha256"],
    }
    with (RESULTS / "drift-final-blind2-summary.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(summary))
        writer.writeheader()
        writer.writerow(summary)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
