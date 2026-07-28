"""Adaptive independent precision audit for the frozen v4 formula.

Only scenarios whose first blind-test simultaneous uncertainty bound exceeded
5% receive fresh trajectories.  Fresh and original sufficient statistics are
then pooled without changing the frozen predictor.
"""

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
SOURCE = RESULTS / "drift-final-blind2-results.csv"
EXPECTED_SOURCE_SHA = "aeebc03cb1db7d38ad76a14aea3bf9ce1eac9085b67b69b341a6b11d7ba2db9c"
EXPECTED_FORMULA_SHA = "fc6ed5692c5e33a9fffe770a3a11e12d0b94dbf5a1eec4c0ae7c81aee87c07d7"
MAX_WORKERS = 4
SEED_ROOT = 20260718


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repetitions_for(k: int) -> int:
    return 60_000 if k <= 8 else 20_000


def simulate(k: int, N: int, p_bias: float, repetitions: int) -> np.ndarray:
    seed = np.random.SeedSequence(
        [SEED_ROOT, k, N, int(round(p_bias * 1_000_000)), repetitions]
    )
    rng = np.random.Generator(np.random.Philox(seed))
    left_table, right_table = np.triu_indices(k, 1)
    balances = np.full((repetitions, k), N, dtype=np.int64)
    times = np.zeros(repetitions, dtype=np.int64)
    active = np.arange(repetitions, dtype=np.int64)
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


def run_scenario(args: tuple[int, int, float, int]) -> dict:
    k, N, p_bias, repetitions = args
    values = simulate(k, N, p_bias, repetitions).astype(float)
    batch_count = 40
    batch_size = repetitions // batch_count
    batch_means = values.reshape(batch_count, batch_size).mean(axis=1)
    return {
        "k": k,
        "N": N,
        "p_bias": p_bias,
        "new_repetitions": repetitions,
        "new_mc_mean": float(np.mean(values)),
        "new_mc_sd": float(np.std(values, ddof=1)),
        "new_batch_means_json": json.dumps(batch_means.tolist(), separators=(",", ":")),
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
        for key, value in provenance.items():
            if row.get(key) != value:
                raise RuntimeError(f"checkpoint provenance mismatch for {key}")
        row["k"] = int(row["k"])
        row["N"] = int(row["N"])
        row["p_bias"] = float(row["p_bias"])
        row["new_repetitions"] = int(row["new_repetitions"])
        row["new_mc_mean"] = float(row["new_mc_mean"])
        row["new_mc_sd"] = float(row["new_mc_sd"])
    return rows


def main() -> None:
    RESULTS.mkdir(exist_ok=True)
    formula_sha = sha256(ROOT / "drift_formula_final.py")
    source_sha = sha256(SOURCE)
    validator_sha = sha256(Path(__file__).resolve())
    if formula_sha != EXPECTED_FORMULA_SHA or source_sha != EXPECTED_SOURCE_SHA:
        raise RuntimeError("frozen input hash mismatch")

    with SOURCE.open(newline="", encoding="utf-8-sig") as handle:
        source_rows = list(csv.DictReader(handle))
    targets = [
        (int(row["k"]), int(row["N"]), float(row["p_bias"]), repetitions_for(int(row["k"])))
        for row in source_rows
        if float(row["uncertainty_aware_error_upper"]) > 0.05
    ]
    grid_hash = hashlib.sha256(json.dumps(targets, separators=(",", ":")).encode()).hexdigest()
    run_id = f"precision-v1-{grid_hash[:12]}"
    provenance = {
        "run_id": run_id,
        "formula_sha256": formula_sha,
        "validator_sha256": validator_sha,
        "source_results_sha256": source_sha,
        "grid_sha256": grid_hash,
    }
    manifest = {
        **provenance,
        "formula_version": FORMULA_VERSION,
        "python": sys.version,
        "seed_root": SEED_ROOT,
        "targets": targets,
        "selection_rule": "blind2 uncertainty_aware_error_upper > 0.05",
    }
    manifest_path = RESULTS / "drift-final-precision-manifest.json"
    manifest_text = json.dumps(manifest, ensure_ascii=False, indent=2)
    if manifest_path.exists() and manifest_path.read_text(encoding="utf-8") != manifest_text:
        raise RuntimeError("existing manifest does not match this run")
    manifest_path.write_text(manifest_text, encoding="utf-8")

    checkpoint = RESULTS / "drift-final-precision.partial.csv"
    rows = load_checkpoint(checkpoint, provenance)
    completed = {(row["k"], row["N"], row["p_bias"]) for row in rows}
    remaining = [target for target in targets if target[:3] not in completed]
    with concurrent.futures.ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(run_scenario, target) for target in remaining]
        for index, future in enumerate(concurrent.futures.as_completed(futures), start=1):
            row = future.result()
            row.update(provenance)
            rows.append(row)
            write_rows(checkpoint, rows)
            print(f"precision: {len(completed)+index}/{len(targets)}", flush=True)

    source_map = {
        (int(row["k"]), int(row["N"]), float(row["p_bias"])): row for row in source_rows
    }
    global_z = NormalDist().inv_cdf(1.0 - 0.05 / (2.0 * len(source_rows)))
    for row in rows:
        old = source_map[(row["k"], row["N"], row["p_bias"])]
        n1, n2 = int(old["repetitions"]), row["new_repetitions"]
        mean1, mean2 = float(old["mc_mean"]), row["new_mc_mean"]
        sd1, sd2 = float(old["mc_sd"]), row["new_mc_sd"]
        n = n1 + n2
        mean = (n1 * mean1 + n2 * mean2) / n
        m2 = (n1 - 1) * sd1 * sd1 + (n2 - 1) * sd2 * sd2
        m2 += n1 * (mean1 - mean) ** 2 + n2 * (mean2 - mean) ** 2
        sd = math.sqrt(m2 / (n - 1))
        se = sd / math.sqrt(n)
        prediction = predict_stopping_time(row["k"], row["N"], row["p_bias"])
        low = mean - global_z * se
        high = mean + global_z * se
        row.update(
            {
                "pooled_repetitions": n,
                "pooled_mc_mean": mean,
                "pooled_mc_sd": sd,
                "pooled_mc_se": se,
                "formula_mean": prediction,
                "pooled_absolute_relative_error": abs(prediction - mean) / mean,
                "pooled_simultaneous_ci_low": low,
                "pooled_simultaneous_ci_high": high,
                "pooled_uncertainty_aware_error_upper": max(
                    abs(prediction / low - 1.0), abs(prediction / high - 1.0)
                ),
            }
        )
    final_path = RESULTS / "drift-final-precision-results.csv"
    write_rows(final_path, rows)
    if checkpoint.exists():
        checkpoint.unlink()
    uncertainty = np.array([row["pooled_uncertainty_aware_error_upper"] for row in rows])
    point = np.array([row["pooled_absolute_relative_error"] for row in rows])
    summary = {
        "target_count": len(rows),
        "max_pooled_point_error": float(point.max()),
        "fraction_pooled_simultaneous_upper_within_05": float(np.mean(uncertainty <= 0.05)),
        "max_pooled_uncertainty_aware_error_upper": float(uncertainty.max()),
        "global_simultaneous_z_for_1728": global_z,
        **provenance,
    }
    summary_path = RESULTS / "drift-final-precision-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
