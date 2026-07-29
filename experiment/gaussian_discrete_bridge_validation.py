"""Deterministic validation of the discrete-to-Gaussian survival-order bridge.

The controlled topology is the three-node path.  Uniform ordered-pair demand
induces a two-dimensional centered walk with six equiprobable increments.  Its
independent-edge proxy is the product of the two exact one-edge marginals.
Stopping occurs when either signed channel displacement first reaches +/- N.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import scipy
from scipy import sparse
from scipy.sparse.linalg import spsolve

matplotlib.rcParams.update({
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
})
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial', 'DejaVu Sans']
plt.rcParams['svg.fonttype'] = 'none'
plt.rcParams['pdf.fonttype'] = 42


PIPELINE_VERSION = "1"
DEFAULT_SCALES = (1, 2, 4, 8, 16, 32, 64, 128, 256)
CORRELATED_MOVES = (
    (-1, 0, 1.0 / 6.0),
    (1, 0, 1.0 / 6.0),
    (0, -1, 1.0 / 6.0),
    (0, 1, 1.0 / 6.0),
    (-1, -1, 1.0 / 6.0),
    (1, 1, 1.0 / 6.0),
)
PROXY_MOVES = tuple(
    (left, right, 1.0 / 9.0)
    for left in (-1, 0, 1)
    for right in (-1, 0, 1)
)


def move_moments(moves: tuple[tuple[int, int, float], ...]) -> tuple[np.ndarray, np.ndarray]:
    increments = np.asarray([(left, right) for left, right, _ in moves], dtype=float)
    probabilities = np.asarray([probability for _, _, probability in moves], dtype=float)
    mean = probabilities @ increments
    centered = increments - mean
    covariance = centered.T @ (centered * probabilities[:, None])
    return mean, covariance


def solve_exact_mean(
    scale: int, moves: tuple[tuple[int, int, float], ...]
) -> tuple[float, float, int, int]:
    """Solve (I-Q)u=1 for the killed walk and return u(0,0)."""
    if type(scale) is not int or scale < 1:
        raise ValueError("scale must be a positive integer")
    width = 2 * scale - 1
    state_count = width * width
    indices = np.arange(state_count, dtype=np.int64).reshape(width, width)
    rows = [np.arange(state_count, dtype=np.int64)]
    columns = [rows[0]]
    values = [np.ones(state_count, dtype=float)]
    for delta_i, delta_j, probability in moves:
        i0, i1 = max(0, -delta_i), min(width, width - delta_i)
        j0, j1 = max(0, -delta_j), min(width, width - delta_j)
        source = indices[i0:i1, j0:j1].ravel()
        target = indices[
            i0 + delta_i : i1 + delta_i,
            j0 + delta_j : j1 + delta_j,
        ].ravel()
        rows.append(source)
        columns.append(target)
        values.append(np.full(source.size, -probability, dtype=float))
    system = sparse.csr_matrix(
        (np.concatenate(values), (np.concatenate(rows), np.concatenate(columns))),
        shape=(state_count, state_count),
    )
    solution = spsolve(system, np.ones(state_count, dtype=float))
    residual = float(np.max(np.abs(system @ solution - 1.0)))
    center = int(indices[scale - 1, scale - 1])
    return float(solution[center]), residual, state_count, int(system.nnz)


def independent_brownian_mean(term_count: int = 4000) -> float:
    """Return E[min(T1,T2)] from the squared 1-D survival series.

    Each coordinate has Brownian variance rate 2/3 and starts at the center of
    (-1, 1).  Integrating the product of the two survival series gives the
    absolutely convergent double sum evaluated below in bounded-memory chunks.
    """
    if type(term_count) is not int or term_count < 2:
        raise ValueError("term_count must be an integer of at least two")
    odd = 2 * np.arange(term_count, dtype=float) + 1.0
    coefficients = (4.0 / math.pi) * ((-1.0) ** np.arange(term_count)) / odd
    rates = odd**2 * math.pi**2 * (2.0 / 3.0) / 8.0
    total = 0.0
    chunk = 200
    for start in range(0, term_count, chunk):
        stop = min(start + chunk, term_count)
        total += float(
            np.sum(
                coefficients[start:stop, None]
                * coefficients[None, :]
                / (rates[start:stop, None] + rates[None, :])
            )
        )
    return total


def extrapolate_limit(
    scales: np.ndarray, values: np.ndarray, minimum_scale: int
) -> tuple[float, np.ndarray]:
    mask = scales >= minimum_scale
    if np.count_nonzero(mask) < 3:
        raise ValueError("at least three scales are required for quadratic extrapolation")
    x = 1.0 / scales[mask].astype(float) ** 2
    coefficients = np.polyfit(x, values[mask], deg=2)
    return float(coefficients[-1]), coefficients


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _plot(rows: list[dict[str, object]], metadata: dict[str, object], output: Path) -> None:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial", "DejaVu Sans"]
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["font.size"] = 7
    plt.rcParams["axes.linewidth"] = 0.8
    plt.rcParams["axes.spines.right"] = False
    plt.rcParams["axes.spines.top"] = False
    plt.rcParams["legend.frameon"] = False

    scales = np.asarray([row["scale"] for row in rows], dtype=float)
    correlated = np.asarray([row["normalized_correlated_mean"] for row in rows], dtype=float)
    proxy = np.asarray([row["normalized_proxy_mean"] for row in rows], dtype=float)
    difference = correlated - proxy
    corr_limit = float(metadata["correlated_limit_extrapolation"])
    proxy_limit = float(metadata["independent_brownian_analytic_mean"])
    difference_limit = corr_limit - proxy_limit

    figure, axes = plt.subplots(1, 2, figsize=(7.2047244094, 3.3858267717))
    blue, gray, red = "#0F4D92", "#767676", "#B64342"
    axes[0].plot(scales, correlated, "o-", color=blue, lw=1.5, ms=3.8, label="相关原子路由")
    axes[0].plot(scales, proxy, "s-", color=gray, lw=1.4, ms=3.5, label="独立通道边际")
    axes[0].axhline(corr_limit, color=blue, ls="--", lw=0.9, alpha=0.75)
    axes[0].axhline(proxy_limit, color=gray, ls="--", lw=0.9, alpha=0.75)
    axes[0].set_xscale("log", base=2)
    axes[0].set_xticks(scales)
    axes[0].set_xticklabels([str(int(value)) for value in scales])
    axes[0].set_xlabel("余额尺度 $N$")
    axes[0].set_ylabel(r"确定性 Poisson 均值  $E[\tau_N]/N^2$")
    axes[0].legend(loc="upper right", fontsize=6.5)
    axes[0].text(10, corr_limit + 0.004, "相关极限", color=blue, fontsize=6.1)
    axes[0].text(10, proxy_limit - 0.006, "独立极限", color=gray, fontsize=6.1)

    point_colors = [red if value < 0 else blue for value in difference]
    axes[1].plot(scales, difference, color=blue, lw=1.3, zorder=1)
    axes[1].scatter(scales, difference, c=point_colors, s=18, zorder=2, edgecolor="white", linewidth=0.4)
    axes[1].axhline(0.0, color="#272727", lw=0.8)
    axes[1].axhline(difference_limit, color=blue, ls="--", lw=1.0)
    axes[1].set_xscale("log", base=2)
    axes[1].set_xticks(scales)
    axes[1].set_xticklabels([str(int(value)) for value in scales])
    axes[1].set_xlabel("余额尺度 $N$")
    axes[1].set_ylabel(r"确定性归一化差值  $\Delta_N$")
    axes[1].annotate(
        "有限尺度反转",
        xy=(1.0, difference[0]),
        xytext=(1.6, -0.075),
        arrowprops={"arrowstyle": "->", "color": red, "lw": 0.8},
        color=red,
        fontsize=6.5,
    )
    axes[1].text(
        0.98,
        0.10,
        rf"高斯极限：$\Delta\approx{difference_limit:.5f}$",
        transform=axes[1].transAxes,
        ha="right",
        color=blue,
        fontsize=6.5,
    )
    for label, axis in zip(("a", "b"), axes):
        axis.text(-0.15, 1.03, label, transform=axis.transAxes, fontsize=9, fontweight="bold")
        axis.grid(axis="y", color="#D8D8D8", lw=0.5, alpha=0.65)
    figure.suptitle("离散停止时间收敛到中心高斯生存序", fontsize=8.5, y=1.01)
    figure.tight_layout(pad=1.1)
    figure.savefig(output, dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def run(output_dir: Path, scales: tuple[int, ...] = DEFAULT_SCALES) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    corr_mean, corr_cov = move_moments(CORRELATED_MOVES)
    proxy_mean, proxy_cov = move_moments(PROXY_MOVES)
    if not np.allclose(corr_mean, 0.0, atol=1e-15, rtol=0.0):
        raise AssertionError("correlated increments are not centered")
    if not np.allclose(proxy_mean, 0.0, atol=1e-15, rtol=0.0):
        raise AssertionError("proxy increments are not centered")
    if not np.allclose(np.diag(corr_cov), np.diag(proxy_cov), atol=1e-15, rtol=0.0):
        raise AssertionError("proxy does not preserve channel marginal variances")
    if not np.allclose(proxy_cov - np.diag(np.diag(proxy_cov)), 0.0, atol=1e-15, rtol=0.0):
        raise AssertionError("proxy covariance is not block diagonal")

    rows: list[dict[str, object]] = []
    for scale in scales:
        corr_steps, corr_residual, state_count, corr_nnz = solve_exact_mean(scale, CORRELATED_MOVES)
        proxy_steps, proxy_residual, proxy_state_count, proxy_nnz = solve_exact_mean(scale, PROXY_MOVES)
        if state_count != proxy_state_count:
            raise AssertionError("state counts differ")
        rows.append(
            {
                "scale": scale,
                "state_count": state_count,
                "correlated_matrix_nnz": corr_nnz,
                "proxy_matrix_nnz": proxy_nnz,
                "correlated_exact_mean": corr_steps,
                "proxy_exact_mean": proxy_steps,
                "normalized_correlated_mean": corr_steps / scale**2,
                "normalized_proxy_mean": proxy_steps / scale**2,
                "normalized_difference": (corr_steps - proxy_steps) / scale**2,
                "correlated_residual_max_abs": corr_residual,
                "proxy_residual_max_abs": proxy_residual,
            }
        )

    scale_array = np.asarray(scales, dtype=int)
    corr_values = np.asarray([row["normalized_correlated_mean"] for row in rows], dtype=float)
    proxy_values = np.asarray([row["normalized_proxy_mean"] for row in rows], dtype=float)
    corr_limit_16, _ = extrapolate_limit(scale_array, corr_values, 16)
    corr_limit_32, _ = extrapolate_limit(scale_array, corr_values, 32)
    proxy_limit_16, _ = extrapolate_limit(scale_array, proxy_values, 16)
    proxy_limit_32, _ = extrapolate_limit(scale_array, proxy_values, 32)
    analytic_2000 = independent_brownian_mean(2000)
    analytic_4000 = independent_brownian_mean(4000)
    max_residual = max(
        max(float(row["correlated_residual_max_abs"]), float(row["proxy_residual_max_abs"]))
        for row in rows
    )
    difference_limit = corr_limit_32 - analytic_4000
    gates = {
        "n1_correlated_mean_exact": abs(float(rows[0]["correlated_exact_mean"]) - 1.0) < 1e-13,
        "n1_proxy_mean_exact": abs(float(rows[0]["proxy_exact_mean"]) - 9.0 / 8.0) < 1e-13,
        "all_linear_residuals_below_2e_9": max_residual < 2e-9,
        "analytic_series_stable_below_3e_10": abs(analytic_4000 - analytic_2000) < 3e-10,
        "proxy_extrapolation_matches_analytic_below_5e_8": abs(proxy_limit_32 - analytic_4000) < 5e-8,
        "all_scales_from_n2_have_positive_difference": all(float(row["normalized_difference"]) > 0.0 for row in rows[1:]),
        "limiting_difference_positive": difference_limit > 0.0,
        "extrapolation_window_sensitivity_below_1e_6": abs(corr_limit_32 - corr_limit_16) < 1e-6,
    }
    metadata: dict[str, object] = {
        "pipeline_version": PIPELINE_VERSION,
        "design": "three-node path; uniform ordered-pair atomic routes; balanced binary channels",
        "scales": list(scales),
        "sampling": "none; deterministic sparse Poisson solve",
        "correlated_increment_mean": corr_mean.tolist(),
        "proxy_increment_mean": proxy_mean.tolist(),
        "correlated_covariance": corr_cov.tolist(),
        "proxy_covariance": proxy_cov.tolist(),
        "correlated_limit_extrapolation": corr_limit_32,
        "correlated_limit_window16": corr_limit_16,
        "correlated_extrapolation_window_sensitivity": abs(corr_limit_32 - corr_limit_16),
        "proxy_limit_extrapolation": proxy_limit_32,
        "proxy_limit_window16": proxy_limit_16,
        "independent_brownian_analytic_mean": analytic_4000,
        "analytic_series_2000_terms": analytic_2000,
        "analytic_series_truncation_discrepancy": abs(analytic_4000 - analytic_2000),
        "gaussian_limit_difference_estimate": difference_limit,
        "largest_linear_system_residual": max_residual,
        "finite_sign_reversal_at_n1": float(rows[0]["normalized_difference"]),
        "gates": gates,
        "all_gates_pass": all(gates.values()),
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "matplotlib": matplotlib.__version__},
        "claim_boundary": "deterministic convergence diagnostic; theorem proof does not rely on this finite grid; no universal finite-N sign claim",
    }

    csv_path = output_dir / "discrete-gaussian-bridge-exact.csv"
    metadata_path = output_dir / "metadata.json"
    figure_path = output_dir / "discrete-gaussian-bridge.png"
    _write_csv(csv_path, rows)
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _plot(rows, metadata, figure_path)
    manifest_path = output_dir / "SHA256SUMS"
    manifest_rows = []
    for path in (csv_path, metadata_path, figure_path):
        manifest_rows.append(f"{_sha256(path)}  {path.name}")
    manifest_path.write_text("\n".join(manifest_rows) + "\n", encoding="ascii")
    if not metadata["all_gates_pass"]:
        failed = [name for name, passed in gates.items() if not passed]
        raise RuntimeError(f"validation gates failed: {failed}")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("results/discrete-gaussian-bridge"))
    args = parser.parse_args()
    metadata = run(args.output_dir)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
