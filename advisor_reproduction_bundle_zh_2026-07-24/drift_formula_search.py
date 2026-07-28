"""Generate separated calibration/development data for k<=50 drift formulas.

The final blind test grid is intentionally not present in this file.  It will
be added only after the formula is frozen.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import math
import time
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import least_squares
from scipy.special import ndtr

from drift_experiments import simulate_drifted_hyperedge


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"


CALIBRATION_K = (3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30, 40, 50)
CALIBRATION_N = (10, 20, 40, 80)
CALIBRATION_P = (0.30, 0.50, 0.70, 0.85, 1.00, 1.15, 1.30, 1.50, 1.70, 1.90)

DEVELOPMENT_K = (7, 9, 11, 14, 18, 22, 28, 35, 45, 48)
DEVELOPMENT_N = (15, 30, 60)
DEVELOPMENT_P = (0.40, 0.60, 0.80, 0.925, 1.075, 1.20, 1.40, 1.60, 1.80)


def scenario_seed(split: str, k: int, N: int, p: float) -> int:
    split_code = 11 if split == "calibration" else 29
    return 7_160_001 + 100_003 * split_code + 1009 * k + 17 * N + int(round(1000 * p))


def _simulate_scenario(arguments: tuple[str, int, int, float, int]) -> dict:
    split, k, N, p, repetitions = arguments
    times = simulate_drifted_hyperedge(
        k, N, p, repetitions, scenario_seed(split, k, N, p)
    ).astype(float)
    mean = float(np.mean(times))
    sd = float(np.std(times, ddof=1))
    se = sd / math.sqrt(repetitions)
    return {
        "split": split,
        "k": k,
        "N": N,
        "p_bias": p,
        "repetitions": repetitions,
        "mc_mean": mean,
        "mc_sd": sd,
        "mc_se": se,
        "ci_low": mean - 1.959963984540054 * se,
        "ci_high": mean + 1.959963984540054 * se,
        "seed": scenario_seed(split, k, N, p),
    }


def _write_rows(path: Path, rows: list[dict]) -> None:
    ordered = sorted(rows, key=lambda row: (row["k"], row["N"], row["p_bias"]))
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(ordered[0]))
        writer.writeheader()
        writer.writerows(ordered)


def generate_split(
    split: str, repetitions: int, overwrite: bool = False, workers: int = 8
) -> Path:
    if split == "calibration":
        ks, ns, ps = CALIBRATION_K, CALIBRATION_N, CALIBRATION_P
    elif split == "development":
        ks, ns, ps = DEVELOPMENT_K, DEVELOPMENT_N, DEVELOPMENT_P
    else:
        raise ValueError(split)
    path = RESULTS / f"drift-{split}-data.csv"
    if path.exists() and not overwrite:
        print(f"reuse {path}", flush=True)
        return path
    RESULTS.mkdir(exist_ok=True)
    rows: list[dict] = []
    total = len(ks) * len(ns) * len(ps)
    started = time.perf_counter()
    done = 0
    tasks = [(split, k, N, p, repetitions) for k in ks for N in ns for p in ps]
    checkpoint = path.with_name(path.stem + ".partial.csv")
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(_simulate_scenario, task) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            rows.append(future.result())
            done += 1
            if done % 25 == 0 or done == total:
                _write_rows(checkpoint, rows)
                elapsed = time.perf_counter() - started
                print(f"{split}: {done}/{total}, elapsed={elapsed:.1f}s", flush=True)
    _write_rows(path, rows)
    if checkpoint.exists():
        checkpoint.unlink()
    return path


def read_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for row in rows:
        for key in ("k", "N", "repetitions", "seed"):
            row[key] = int(row[key])
        for key in ("p_bias", "mc_mean", "mc_sd", "mc_se", "ci_low", "ci_high"):
            row[key] = float(row[key])
    return rows


def neutral_features(k: np.ndarray, N: np.ndarray) -> np.ndarray:
    q = k - 3.0
    return np.column_stack(
        [
            np.ones_like(k),
            q,
            q * q,
            np.log(k / 3.0),
            1.0 / N,
            q / N,
        ]
    )


def fit_neutral(rows: list[dict]) -> np.ndarray:
    neutral = [row for row in rows if math.isclose(row["p_bias"], 1.0)]
    k = np.array([row["k"] for row in neutral], dtype=float)
    N = np.array([row["N"] for row in neutral], dtype=float)
    target = np.array([row["mc_mean"] / (row["N"] ** 2) for row in neutral])
    weights = np.array([1.0 / max(row["mc_se"] / (row["N"] ** 2), 1e-4) for row in neutral])
    design = neutral_features(k, N)
    return np.linalg.lstsq(design * weights[:, None], target * weights, rcond=None)[0]


def neutral_constant(k: np.ndarray, N: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    values = neutral_features(k, N) @ coefficients
    # For k=3 under zero drift, E[tau]=N^2 is an exact theorem for every N.
    return np.where(np.asarray(k) == 3.0, 1.0, values)


_KAPPA_CACHE: dict[int, float] = {}


def gaussian_max_mean(count: int) -> float:
    if count not in _KAPPA_CACHE:
        if count == 1:
            value = 0.0
        else:
            value = quad(
                lambda x: 1.0 - ndtr(x) ** count - (1.0 - ndtr(x)) ** count,
                0.0,
                np.inf,
                epsabs=1e-11,
            )[0]
        _KAPPA_CACHE[count] = float(value)
    return _KAPPA_CACHE[count]


def predict_master(
    k: np.ndarray,
    N: np.ndarray,
    p: np.ndarray,
    neutral_coefficients: np.ndarray,
    branch_parameters: np.ndarray,
) -> np.ndarray:
    """Asymptotically constrained rational crossover formula.

    branch_parameters = [neg0, neg_logk, neg_quad, pos0, pos_logk,
                         pos_quad, competition_scale]
    """
    k = np.asarray(k, dtype=float)
    N = np.asarray(N, dtype=float)
    p = np.asarray(p, dtype=float)
    a0 = np.maximum(neutral_constant(k, N, neutral_coefficients), 0.1)
    neutral_time = a0 * N * N
    result = neutral_time.copy()
    delta = p - 1.0

    neg = delta < -1e-14
    if np.any(neg):
        t_star = k[neg] * N[neg] / (2.0 * (-delta[neg]))
        x = neutral_time[neg] / t_star
        logk = np.log(k[neg] / 3.0)
        adjustment = branch_parameters[0] + branch_parameters[1] * logk
        weak_shape = x / (1.0 + x) + branch_parameters[2] * x * x / (1.0 + x) ** 2
        denominator = 1.0 + x + adjustment * weak_shape
        result[neg] = neutral_time[neg] / np.maximum(denominator, 0.05)

    pos = delta > 1e-14
    if np.any(pos):
        t_star = k[pos] * (k[pos] - 1.0) * N[pos] / (2.0 * delta[pos])
        x = neutral_time[pos] / t_star
        logk = np.log(k[pos] / 3.0)
        adjustment = branch_parameters[3] + branch_parameters[4] * logk
        weak_shape = x / (1.0 + x) + branch_parameters[5] * x * x / (1.0 + x) ** 2
        kappas = np.array([gaussian_max_mean(int(value - 1)) for value in k[pos]])
        c_theory = kappas * np.sqrt(2.0 * a0[pos] / (k[pos] - 1.0))
        competition = c_theory * x * x / (1.0 + x) ** 1.5
        denominator = (
            1.0
            + x
            + adjustment * weak_shape
            + branch_parameters[6] * competition
        )
        result[pos] = neutral_time[pos] / np.maximum(denominator, 0.05)
    return result


def fit_branches(rows: list[dict], neutral_coefficients: np.ndarray) -> np.ndarray:
    drifted = [row for row in rows if not math.isclose(row["p_bias"], 1.0)]
    k = np.array([row["k"] for row in drifted], dtype=float)
    N = np.array([row["N"] for row in drifted], dtype=float)
    p = np.array([row["p_bias"] for row in drifted], dtype=float)
    target = np.array([row["mc_mean"] for row in drifted])
    relative_mc_se = np.array([row["mc_se"] / row["mc_mean"] for row in drifted])

    def residual(parameters: np.ndarray) -> np.ndarray:
        predicted = predict_master(k, N, p, neutral_coefficients, parameters)
        log_error = np.log(predicted / target)
        # Do not let unusually low Monte Carlo noise make one region dominate.
        weights = 1.0 / np.maximum(relative_mc_se, 0.006)
        return log_error * weights

    initial = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0])
    fit = least_squares(residual, initial, loss="soft_l1", f_scale=1.0, max_nfev=50_000)
    return fit.x


def crossover_design(k: np.ndarray, N: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Corrections vanish in both the neutral (x=0) and strong-drift limits."""
    lk = np.log(k / 10.0)
    ln = np.log(N / 20.0)
    s = x / (1.0 + x)
    h = x / (1.0 + x) ** 2
    lx = np.log1p(x)
    base = np.column_stack(
        [
            np.ones_like(k),
            lk,
            ln,
            lk * lk,
            ln * ln,
            lk * ln,
        ]
    )
    return np.column_stack([h[:, None] * base, (h * s)[:, None] * base[:, :3], (h * lx)[:, None] * base[:, :3]])


def base_asymptotic_prediction(
    k: np.ndarray, N: np.ndarray, p: np.ndarray, neutral_coefficients: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    a0 = np.maximum(neutral_constant(k, N, neutral_coefficients), 0.1)
    neutral_time = a0 * N * N
    result = neutral_time.copy()
    x = np.zeros_like(result)
    delta = p - 1.0
    neg = delta < -1e-14
    if np.any(neg):
        t_star = k[neg] * N[neg] / (2.0 * (-delta[neg]))
        x[neg] = neutral_time[neg] / t_star
        result[neg] = neutral_time[neg] / (1.0 + x[neg])
    pos = delta > 1e-14
    if np.any(pos):
        t_star = k[pos] * (k[pos] - 1.0) * N[pos] / (2.0 * delta[pos])
        x[pos] = neutral_time[pos] / t_star
        kappas = np.array([gaussian_max_mean(int(value - 1)) for value in k[pos]])
        c_theory = kappas * np.sqrt(2.0 * a0[pos] / (k[pos] - 1.0))
        competition = c_theory * x[pos] * x[pos] / (1.0 + x[pos]) ** 1.5
        result[pos] = neutral_time[pos] / (1.0 + x[pos] + competition)
    return result, x


def fit_crossover_corrections(
    rows: list[dict], neutral_coefficients: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    fitted: list[np.ndarray] = []
    for positive in (False, True):
        branch = [
            row
            for row in rows
            if (row["p_bias"] > 1.0 if positive else row["p_bias"] < 1.0)
        ]
        k = np.array([row["k"] for row in branch], dtype=float)
        N = np.array([row["N"] for row in branch], dtype=float)
        p = np.array([row["p_bias"] for row in branch], dtype=float)
        target = np.array([row["mc_mean"] for row in branch])
        base, x = base_asymptotic_prediction(k, N, p, neutral_coefficients)
        design = crossover_design(k, N, x)
        relative_mc_se = np.array([row["mc_se"] / row["mc_mean"] for row in branch])

        def residual(parameters: np.ndarray) -> np.ndarray:
            prediction = base * np.exp(design @ parameters)
            weights = 1.0 / np.maximum(relative_mc_se, 0.006)
            return np.log(prediction / target) * weights

        fit = least_squares(
            residual,
            np.zeros(design.shape[1]),
            loss="soft_l1",
            f_scale=1.0,
            max_nfev=50_000,
        )
        fitted.append(fit.x)
    return fitted[0], fitted[1]


def predict_v2(
    k: np.ndarray,
    N: np.ndarray,
    p: np.ndarray,
    neutral_coefficients: np.ndarray,
    negative_correction: np.ndarray,
    positive_correction: np.ndarray,
) -> np.ndarray:
    k = np.asarray(k, dtype=float)
    N = np.asarray(N, dtype=float)
    p = np.asarray(p, dtype=float)
    base, x = base_asymptotic_prediction(k, N, p, neutral_coefficients)
    result = base.copy()
    neg = p < 1.0 - 1e-14
    if np.any(neg):
        result[neg] *= np.exp(crossover_design(k[neg], N[neg], x[neg]) @ negative_correction)
    pos = p > 1.0 + 1e-14
    if np.any(pos):
        result[pos] *= np.exp(crossover_design(k[pos], N[pos], x[pos]) @ positive_correction)
    return result


def evaluate_predictions(rows: list[dict], prediction: np.ndarray) -> dict:
    target = np.array([row["mc_mean"] for row in rows])
    relative = np.abs(prediction - target) / target
    signed = (prediction - target) / target
    return {
        "count": len(rows),
        "mean_abs_relative_error": float(np.mean(relative)),
        "median_abs_relative_error": float(np.median(relative)),
        "p90_abs_relative_error": float(np.quantile(relative, 0.90)),
        "p95_abs_relative_error": float(np.quantile(relative, 0.95)),
        "max_abs_relative_error": float(np.max(relative)),
        "mean_signed_relative_error": float(np.mean(signed)),
        "fraction_within_05": float(np.mean(relative <= 0.05)),
        "fraction_within_10": float(np.mean(relative <= 0.10)),
    }


def v2_predictions(
    rows: list[dict],
    neutral_coefficients: np.ndarray,
    negative_correction: np.ndarray,
    positive_correction: np.ndarray,
) -> np.ndarray:
    return predict_v2(
        np.array([row["k"] for row in rows], dtype=float),
        np.array([row["N"] for row in rows], dtype=float),
        np.array([row["p_bias"] for row in rows], dtype=float),
        neutral_coefficients,
        negative_correction,
        positive_correction,
    )


def write_prediction_array(name: str, rows: list[dict], predictions: np.ndarray) -> None:
    output: list[dict] = []
    for row, prediction in zip(rows, predictions):
        copy = dict(row)
        copy["formula_mean"] = float(prediction)
        copy["signed_relative_error"] = float((prediction - row["mc_mean"]) / row["mc_mean"])
        copy["absolute_relative_error"] = abs(copy["signed_relative_error"])
        copy["formula_inside_mc_95ci"] = row["ci_low"] <= prediction <= row["ci_high"]
        output.append(copy)
    with (RESULTS / name).open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(output[0]))
        writer.writeheader()
        writer.writerows(output)


def evaluate(rows: list[dict], neutral_coefficients: np.ndarray, branch_parameters: np.ndarray) -> dict:
    k = np.array([row["k"] for row in rows], dtype=float)
    N = np.array([row["N"] for row in rows], dtype=float)
    p = np.array([row["p_bias"] for row in rows], dtype=float)
    target = np.array([row["mc_mean"] for row in rows])
    prediction = predict_master(k, N, p, neutral_coefficients, branch_parameters)
    relative = np.abs(prediction - target) / target
    signed = (prediction - target) / target
    return {
        "count": len(rows),
        "mean_abs_relative_error": float(np.mean(relative)),
        "median_abs_relative_error": float(np.median(relative)),
        "p90_abs_relative_error": float(np.quantile(relative, 0.90)),
        "p95_abs_relative_error": float(np.quantile(relative, 0.95)),
        "max_abs_relative_error": float(np.max(relative)),
        "mean_signed_relative_error": float(np.mean(signed)),
        "fraction_within_05": float(np.mean(relative <= 0.05)),
        "fraction_within_10": float(np.mean(relative <= 0.10)),
    }


def write_predictions(
    name: str,
    rows: list[dict],
    neutral_coefficients: np.ndarray,
    branch_parameters: np.ndarray,
) -> None:
    k = np.array([row["k"] for row in rows], dtype=float)
    N = np.array([row["N"] for row in rows], dtype=float)
    p = np.array([row["p_bias"] for row in rows], dtype=float)
    predictions = predict_master(k, N, p, neutral_coefficients, branch_parameters)
    output: list[dict] = []
    for row, prediction in zip(rows, predictions):
        copy = dict(row)
        copy["formula_mean"] = float(prediction)
        copy["signed_relative_error"] = float((prediction - row["mc_mean"]) / row["mc_mean"])
        copy["absolute_relative_error"] = abs(copy["signed_relative_error"])
        copy["formula_inside_mc_95ci"] = row["ci_low"] <= prediction <= row["ci_high"]
        output.append(copy)
    with (RESULTS / name).open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(output[0]))
        writer.writeheader()
        writer.writerows(output)


def fit_and_report() -> None:
    calibration = read_rows(RESULTS / "drift-calibration-data.csv")
    development = read_rows(RESULTS / "drift-development-data.csv")
    neutral = fit_neutral(calibration)
    branches = fit_branches(calibration, neutral)
    print("neutral_coefficients", neutral.tolist())
    print("branch_parameters", branches.tolist())
    print("calibration", evaluate(calibration, neutral, branches))
    print("development", evaluate(development, neutral, branches))
    write_predictions("drift-calibration-predictions.csv", calibration, neutral, branches)
    write_predictions("drift-development-predictions.csv", development, neutral, branches)
    with (RESULTS / "drift-formula-v1-parameters.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["parameter", "value"])
        for index, value in enumerate(neutral):
            writer.writerow([f"neutral_{index}", value])
        for index, value in enumerate(branches):
            writer.writerow([f"branch_{index}", value])

    negative_correction, positive_correction = fit_crossover_corrections(calibration, neutral)
    calibration_v2 = v2_predictions(calibration, neutral, negative_correction, positive_correction)
    development_v2 = v2_predictions(development, neutral, negative_correction, positive_correction)
    print("v2_negative_correction", negative_correction.tolist())
    print("v2_positive_correction", positive_correction.tolist())
    print("v2_calibration", evaluate_predictions(calibration, calibration_v2))
    print("v2_development", evaluate_predictions(development, development_v2))
    write_prediction_array("drift-calibration-predictions-v2.csv", calibration, calibration_v2)
    write_prediction_array("drift-development-predictions-v2.csv", development, development_v2)
    with (RESULTS / "drift-formula-v2-parameters.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["parameter", "value"])
        for index, value in enumerate(neutral):
            writer.writerow([f"neutral_{index}", value])
        for index, value in enumerate(negative_correction):
            writer.writerow([f"negative_{index}", value])
        for index, value in enumerate(positive_correction):
            writer.writerow([f"positive_{index}", value])

    # After the v2 development audit, development becomes part of the fitting
    # data.  v3 is the candidate to freeze before a new, unseen final test.
    combined = calibration + development
    negative_v3, positive_v3 = fit_crossover_corrections(combined, neutral)
    calibration_v3 = v2_predictions(calibration, neutral, negative_v3, positive_v3)
    development_v3 = v2_predictions(development, neutral, negative_v3, positive_v3)
    print("v3_negative_correction", negative_v3.tolist())
    print("v3_positive_correction", positive_v3.tolist())
    print("v3_calibration", evaluate_predictions(calibration, calibration_v3))
    print("v3_development", evaluate_predictions(development, development_v3))
    write_prediction_array("drift-calibration-predictions-v3.csv", calibration, calibration_v3)
    write_prediction_array("drift-development-predictions-v3.csv", development, development_v3)
    with (RESULTS / "drift-formula-v3-parameters.csv").open(
        "w", newline="", encoding="utf-8-sig"
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["parameter", "value"])
        for index, value in enumerate(neutral):
            writer.writerow([f"neutral_{index}", value])
        for index, value in enumerate(negative_v3):
            writer.writerow([f"negative_{index}", value])
        for index, value in enumerate(positive_v3):
            writer.writerow([f"positive_{index}", value])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--generate", choices=("calibration", "development", "both"))
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--fit", action="store_true")
    args = parser.parse_args()
    if args.generate in ("calibration", "both"):
        generate_split("calibration", 5_000, args.overwrite, args.workers)
    if args.generate in ("development", "both"):
        generate_split("development", 7_000, args.overwrite, args.workers)
    if args.fit:
        fit_and_report()


if __name__ == "__main__":
    main()
