"""Frozen-formula confirmation on declared boundaries and new weak drifts."""

from __future__ import annotations

import concurrent.futures
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from statistics import NormalDist

import numpy as np

from drift_formula_final import FORMULA_VERSION, predict_stopping_time


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
K_VALUES = tuple(range(3, 51))
N_VALUES = (10, 128)
P_VALUES = (0.30, 0.975, 1.025, 1.90)
REPETITIONS = 8_000
BATCHES = 40
MAX_WORKERS = 4
SEED_ROOT = 20260719
EXPECTED_FORMULA_SHA = "fc6ed5692c5e33a9fffe770a3a11e12d0b94dbf5a1eec4c0ae7c81aee87c07d7"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def simulate(k: int, N: int, p_bias: float) -> np.ndarray:
    seed = np.random.SeedSequence(
        [SEED_ROOT, k, N, int(round(p_bias * 1_000_000)), REPETITIONS]
    )
    rng = np.random.Generator(np.random.Philox(seed))
    left_table, right_table = np.triu_indices(k, 1)
    balances = np.full((REPETITIONS, k), N, dtype=np.int64)
    times = np.zeros(REPETITIONS, dtype=np.int64)
    active = np.arange(REPETITIONS, dtype=np.int64)
    theta = p_bias / 2.0

    while active.size:
        pair_index = rng.integers(0, left_table.size, size=active.size)
        left = left_table[pair_index]
        right = right_table[pair_index]
        sender = left.copy()
        receiver = right.copy()
        center_pair = left == 0
        if np.any(center_pair):
            toward_center = rng.random(np.count_nonzero(center_pair)) < theta
            other = right[center_pair]
            sender[center_pair] = np.where(toward_center, other, 0)
            receiver[center_pair] = np.where(toward_center, 0, other)
        peripheral = ~center_pair
        if np.any(peripheral):
            reverse = rng.random(np.count_nonzero(peripheral)) < 0.5
            a = left[peripheral]
            b = right[peripheral]
            sender[peripheral] = np.where(reverse, b, a)
            receiver[peripheral] = np.where(reverse, a, b)

        balances[active, sender] -= 1
        balances[active, receiver] += 1
        times[active] += 1
        active = active[balances[active, sender] != 0]
    return times


def run_scenario(scenario: tuple[int, int, float]) -> dict:
    k, N, p_bias = scenario
    values = simulate(k, N, p_bias).astype(float)
    batch_means = values.reshape(BATCHES, REPETITIONS // BATCHES).mean(axis=1)
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    return {
        "k": k,
        "N": N,
        "p_bias": p_bias,
        "repetitions": REPETITIONS,
        "mc_mean": mean,
        "mc_sd": sd,
        "mc_se": sd / math.sqrt(REPETITIONS),
        "batch_means_json": json.dumps(batch_means.tolist(), separators=(",", ":")),
    }


def write_rows(path: Path, rows: list[dict]) -> None:
    ordered = sorted(rows, key=lambda row: (int(row["k"]), int(row["N"]), float(row["p_bias"])))
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(ordered[0]))
        writer.writeheader()
        writer.writerows(ordered)


def load_checkpoint(path: Path, provenance: dict[str, str]) -> list[dict]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key, expected in provenance.items():
            if row.get(key) != expected:
                raise RuntimeError(f"checkpoint provenance mismatch for {key}")
        for key in ("k", "N", "repetitions"):
            row[key] = int(row[key])
        for key in ("p_bias", "mc_mean", "mc_sd", "mc_se"):
            row[key] = float(row[key])
    return rows


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    formula_sha = sha256(ROOT / "drift_formula_final.py")
    validator_sha = sha256(Path(__file__).resolve())
    if formula_sha != EXPECTED_FORMULA_SHA:
        raise RuntimeError("frozen formula hash mismatch")
    scenarios = [(k, N, p) for k in K_VALUES for N in N_VALUES for p in P_VALUES]
    grid_sha = hashlib.sha256(json.dumps(scenarios, separators=(",", ":")).encode()).hexdigest()
    run_id = f"boundary-v1-{grid_sha[:12]}"
    provenance = {
        "run_id": run_id,
        "formula_sha256": formula_sha,
        "validator_sha256": validator_sha,
        "grid_sha256": grid_sha,
    }
    manifest = {
        **provenance,
        "formula_version": FORMULA_VERSION,
        "python": sys.version,
        "seed_root": SEED_ROOT,
        "k_values": K_VALUES,
        "N_values": N_VALUES,
        "p_values": P_VALUES,
        "repetitions": REPETITIONS,
        "batches": BATCHES,
        "rng": "numpy.random.Philox",
    }
    manifest_path = RESULTS / "drift-final-boundary-manifest.json"
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2)
    if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") != manifest_text:
        raise RuntimeError("existing manifest does not match this run")
    manifest_path.write_text(manifest_text, encoding="utf-8")

    checkpoint = RESULTS / "drift-final-boundary.partial.csv"
    rows = load_checkpoint(checkpoint, provenance)
    completed = {(row["k"], row["N"], row["p_bias"]) for row in rows}
    remaining = [scenario for scenario in scenarios if scenario not in completed]
    if rows:
        print(f"resuming: {len(rows)}/{len(scenarios)}", flush=True)
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(run_scenario, scenario) for scenario in remaining]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            row = future.result()
            row.update(provenance)
            rows.append(row)
            if index % 16 == 0 or index == len(remaining):
                write_rows(checkpoint, rows)
                print(f"boundary: {len(completed)+index}/{len(scenarios)}", flush=True)

    z = NormalDist().inv_cdf(1.0 - 0.05 / (2.0 * len(rows)))
    for row in rows:
        prediction = predict_stopping_time(row["k"], row["N"], row["p_bias"])
        low = row["mc_mean"] - z * row["mc_se"]
        high = row["mc_mean"] + z * row["mc_se"]
        row.update(
            {
                "formula_mean": prediction,
                "signed_relative_error": (prediction - row["mc_mean"]) / row["mc_mean"],
                "absolute_relative_error": abs(prediction - row["mc_mean"]) / row["mc_mean"],
                "simultaneous_ci_low": low,
                "simultaneous_ci_high": high,
                "uncertainty_aware_error_upper": max(
                    abs(prediction / low - 1.0), abs(prediction / high - 1.0)
                ),
            }
        )
    final_path = RESULTS / "drift-final-boundary-results.csv"
    write_rows(final_path, rows)
    if checkpoint.exists():
        checkpoint.unlink()

    errors = np.array([row["absolute_relative_error"] for row in rows])
    signed = np.array([row["signed_relative_error"] for row in rows])
    uncertainty = np.array([row["uncertainty_aware_error_upper"] for row in rows])
    summary = {
        "scenario_count": len(rows),
        "mean_absolute_relative_error": float(errors.mean()),
        "p95_absolute_relative_error": float(np.quantile(errors, 0.95)),
        "max_absolute_relative_error": float(errors.max()),
        "rms_relative_error": float(np.sqrt(np.mean(signed * signed))),
        "mean_signed_relative_error": float(signed.mean()),
        "fraction_point_error_within_04": float(np.mean(errors <= 0.04)),
        "fraction_point_error_within_05": float(np.mean(errors <= 0.05)),
        "fraction_simultaneous_upper_within_05": float(np.mean(uncertainty <= 0.05)),
        "max_uncertainty_aware_error_upper": float(uncertainty.max()),
        "simultaneous_z": z,
        **provenance,
    }
    (RESULTS / "drift-final-boundary-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
