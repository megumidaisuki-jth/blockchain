"""Merge the 18 precision-audit sufficient statistics into blind2 results."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
BASE = RESULTS / "drift-final-blind2-results.csv"
PRECISION = RESULTS / "drift-final-precision-results.csv"
OUTPUT = RESULTS / "drift-final-refined-results.csv"
SUMMARY = RESULTS / "drift-final-refined-summary.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with BASE.open(newline="", encoding="utf-8-sig") as handle:
        base_rows = list(csv.DictReader(handle))
    with PRECISION.open(newline="", encoding="utf-8-sig") as handle:
        precision_rows = list(csv.DictReader(handle))
    precision = {
        (int(row["k"]), int(row["N"]), float(row["p_bias"])): row
        for row in precision_rows
    }

    rows: list[dict] = []
    for original in base_rows:
        key = (int(original["k"]), int(original["N"]), float(original["p_bias"]))
        row = {
            "k": key[0],
            "N": key[1],
            "p_bias": key[2],
            "formula_mean": float(original["formula_mean"]),
            "refined": key in precision,
        }
        if key in precision:
            update = precision[key]
            mean = float(update["pooled_mc_mean"])
            sd = float(update["pooled_mc_sd"])
            se = float(update["pooled_mc_se"])
            repetitions = int(update["pooled_repetitions"])
            low = float(update["pooled_simultaneous_ci_low"])
            high = float(update["pooled_simultaneous_ci_high"])
            upper = float(update["pooled_uncertainty_aware_error_upper"])
        else:
            mean = float(original["mc_mean"])
            sd = float(original["mc_sd"])
            se = float(original["mc_se"])
            repetitions = int(original["repetitions"])
            low = float(original["simultaneous_ci_low"])
            high = float(original["simultaneous_ci_high"])
            upper = float(original["uncertainty_aware_error_upper"])
        prediction = row["formula_mean"]
        row.update(
            {
                "repetitions": repetitions,
                "mc_mean": mean,
                "mc_sd": sd,
                "mc_se": se,
                "signed_relative_error": (prediction - mean) / mean,
                "absolute_relative_error": abs(prediction - mean) / mean,
                "simultaneous_ci_low": low,
                "simultaneous_ci_high": high,
                "uncertainty_aware_error_upper": upper,
            }
        )
        rows.append(row)

    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    errors = np.array([row["absolute_relative_error"] for row in rows])
    signed = np.array([row["signed_relative_error"] for row in rows])
    uncertainty = np.array([row["uncertainty_aware_error_upper"] for row in rows])
    summary = {
        "scenario_count": len(rows),
        "refined_scenario_count": len(precision),
        "total_trajectories_after_refinement": int(sum(row["repetitions"] for row in rows)),
        "mean_absolute_relative_error": float(errors.mean()),
        "median_absolute_relative_error": float(np.median(errors)),
        "p90_absolute_relative_error": float(np.quantile(errors, 0.90)),
        "p95_absolute_relative_error": float(np.quantile(errors, 0.95)),
        "max_absolute_relative_error": float(errors.max()),
        "rms_relative_error": float(math.sqrt(np.mean(signed * signed))),
        "mean_signed_relative_error": float(signed.mean()),
        "fraction_point_error_within_04": float(np.mean(errors <= 0.04)),
        "fraction_point_error_within_05": float(np.mean(errors <= 0.05)),
        "fraction_simultaneous_upper_within_05": float(np.mean(uncertainty <= 0.05)),
        "max_uncertainty_aware_error_upper": float(uncertainty.max()),
        "formula_sha256": base_rows[0]["formula_sha256"],
        "base_results_sha256": sha256(BASE),
        "precision_results_sha256": sha256(PRECISION),
        "combined_results_sha256": sha256(OUTPUT),
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
