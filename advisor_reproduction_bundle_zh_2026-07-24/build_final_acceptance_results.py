"""Build the conservative 2,112-scenario acceptance dataset.

For the 18 adaptively selected precision targets this uses only the fresh
confirmation sample, not the original sample.  The Bonferroni denominator is
2,130 = 1,728 original tests + 18 confirmations + 384 boundary confirmations.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import NormalDist

import numpy as np


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
BASE = RESULTS / "drift-final-blind2-results.csv"
PRECISION = RESULTS / "drift-final-precision-results.csv"
BOUNDARY = RESULTS / "drift-final-boundary-results.csv"
OUTPUT = RESULTS / "drift-final-acceptance-results.csv"
SUMMARY = RESULTS / "drift-final-acceptance-summary.json"
BONFERRONI_TEST_COUNT = 2_130


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    with BASE.open(newline="", encoding="utf-8-sig") as handle:
        base_rows = list(csv.DictReader(handle))
    with PRECISION.open(newline="", encoding="utf-8-sig") as handle:
        precision_rows = list(csv.DictReader(handle))
    with BOUNDARY.open(newline="", encoding="utf-8-sig") as handle:
        boundary_rows = list(csv.DictReader(handle))

    precision = {
        (int(row["k"]), int(row["N"]), float(row["p_bias"])): row
        for row in precision_rows
    }
    z = NormalDist().inv_cdf(1.0 - 0.05 / (2.0 * BONFERRONI_TEST_COUNT))
    rows: list[dict] = []

    for original in base_rows:
        key = (int(original["k"]), int(original["N"]), float(original["p_bias"]))
        if key in precision:
            confirmation = precision[key]
            repetitions = int(confirmation["new_repetitions"])
            mean = float(confirmation["new_mc_mean"])
            sd = float(confirmation["new_mc_sd"])
            source = "fresh_precision_confirmation"
        else:
            repetitions = int(original["repetitions"])
            mean = float(original["mc_mean"])
            sd = float(original["mc_sd"])
            source = "blind2"
        rows.append(
            {
                "k": key[0],
                "N": key[1],
                "p_bias": key[2],
                "source": source,
                "repetitions": repetitions,
                "mc_mean": mean,
                "mc_sd": sd,
                "formula_mean": float(original["formula_mean"]),
            }
        )

    for boundary in boundary_rows:
        rows.append(
            {
                "k": int(boundary["k"]),
                "N": int(boundary["N"]),
                "p_bias": float(boundary["p_bias"]),
                "source": "boundary_confirmation",
                "repetitions": int(boundary["repetitions"]),
                "mc_mean": float(boundary["mc_mean"]),
                "mc_sd": float(boundary["mc_sd"]),
                "formula_mean": float(boundary["formula_mean"]),
            }
        )

    for row in rows:
        row["mc_se"] = row["mc_sd"] / math.sqrt(row["repetitions"])
        row["signed_relative_error"] = (row["formula_mean"] - row["mc_mean"]) / row["mc_mean"]
        row["absolute_relative_error"] = abs(row["signed_relative_error"])
        row["simultaneous_ci_low"] = row["mc_mean"] - z * row["mc_se"]
        row["simultaneous_ci_high"] = row["mc_mean"] + z * row["mc_se"]
        row["uncertainty_aware_error_upper"] = max(
            abs(row["formula_mean"] / row["simultaneous_ci_low"] - 1.0),
            abs(row["formula_mean"] / row["simultaneous_ci_high"] - 1.0),
        )
        row["formula_sha256"] = base_rows[0]["formula_sha256"]

    keys = {(row["k"], row["N"], row["p_bias"]) for row in rows}
    if len(rows) != 2_112 or len(keys) != 2_112:
        raise RuntimeError("acceptance grid must contain 2,112 unique scenarios")
    rows.sort(key=lambda row: (row["k"], row["N"], row["p_bias"]))
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    errors = np.array([row["absolute_relative_error"] for row in rows])
    signed = np.array([row["signed_relative_error"] for row in rows])
    uncertainty = np.array([row["uncertainty_aware_error_upper"] for row in rows])
    summary = {
        "scenario_count": len(rows),
        "unique_k_count": len({row["k"] for row in rows}),
        "k_min": min(row["k"] for row in rows),
        "k_max": max(row["k"] for row in rows),
        "bonferroni_test_count": BONFERRONI_TEST_COUNT,
        "simultaneous_z": z,
        "mean_absolute_relative_error": float(errors.mean()),
        "median_absolute_relative_error": float(np.median(errors)),
        "p90_absolute_relative_error": float(np.quantile(errors, 0.90)),
        "p95_absolute_relative_error": float(np.quantile(errors, 0.95)),
        "max_absolute_relative_error": float(errors.max()),
        "rms_relative_error": float(np.sqrt(np.mean(signed * signed))),
        "mean_signed_relative_error": float(signed.mean()),
        "fraction_point_error_within_04": float(np.mean(errors <= 0.04)),
        "fraction_point_error_within_05": float(np.mean(errors <= 0.05)),
        "fraction_simultaneous_upper_within_05": float(np.mean(uncertainty <= 0.05)),
        "max_uncertainty_aware_error_upper": float(uncertainty.max()),
        "formula_sha256": base_rows[0]["formula_sha256"],
        "base_results_sha256": sha256(BASE),
        "precision_results_sha256": sha256(PRECISION),
        "boundary_results_sha256": sha256(BOUNDARY),
        "acceptance_results_sha256": sha256(OUTPUT),
    }
    SUMMARY.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
