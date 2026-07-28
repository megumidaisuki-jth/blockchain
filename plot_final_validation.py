"""Create publication-ready plots for the frozen k=3..50 blind validation."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "results" / "drift-final-blind2-results.csv"
OUTPUT = ROOT / "figures" / "fig7-k3-50-blind-validation.png"
BOUNDARY_INPUT = ROOT / "results" / "drift-final-boundary-results.csv"
BOUNDARY_OUTPUT = ROOT / "figures" / "fig8-boundary-weak-drift-validation.png"


def main() -> None:
    with INPUT.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    k = np.array([int(row["k"]) for row in rows])
    p = np.array([float(row["p_bias"]) for row in rows])
    mc = np.array([float(row["mc_mean"]) for row in rows])
    formula = np.array([float(row["formula_mean"]) for row in rows])
    error = 100.0 * np.array([float(row["absolute_relative_error"]) for row in rows])

    k_values = np.array(sorted(set(k)))
    p_values = np.array(sorted(set(p)))
    max_by_k = np.array([np.max(error[k == value]) for value in k_values])
    p95_by_k = np.array([np.quantile(error[k == value], 0.95) for value in k_values])
    heat = np.array(
        [[np.mean(error[(k == kval) & (p == pval)]) for kval in k_values] for pval in p_values]
    )

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
        }
    )
    fig = plt.figure(figsize=(12.2, 8.0), constrained_layout=True)
    grid = fig.add_gridspec(2, 2, height_ratios=(1.0, 1.05))

    ax = fig.add_subplot(grid[0, 0])
    scatter = ax.scatter(mc, formula, c=error, s=10, cmap="viridis", vmin=0.0, vmax=4.0, alpha=0.75)
    limits = [min(mc.min(), formula.min()), max(mc.max(), formula.max())]
    ax.plot(limits, limits, color="#d95f02", linewidth=1.2, label="identity")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Independent Monte Carlo mean")
    ax.set_ylabel("Frozen-formula prediction")
    ax.set_title("(a) Prediction against independent simulation")
    ax.legend(frameon=False, loc="upper left")
    colorbar = fig.colorbar(scatter, ax=ax, pad=0.01)
    colorbar.set_label("absolute relative error (%)")

    ax = fig.add_subplot(grid[0, 1])
    ax.plot(k_values, max_by_k, color="#d95f02", marker="o", markersize=2.7, linewidth=1.1, label="maximum")
    ax.plot(k_values, p95_by_k, color="#1b9e77", marker="s", markersize=2.3, linewidth=1.0, label="95th percentile")
    ax.axhline(4.0, color="#666666", linestyle="--", linewidth=0.9, label="4% acceptance ceiling")
    ax.set_xlim(3, 50)
    ax.set_ylim(0, 4.25)
    ax.set_xlabel("hyperedge size k")
    ax.set_ylabel("absolute relative error (%)")
    ax.set_title("(b) Error envelope for every integer k")
    ax.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    ax.legend(frameon=False, ncol=2, loc="upper left")

    ax = fig.add_subplot(grid[1, :])
    image = ax.imshow(
        heat,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        extent=[k_values.min() - 0.5, k_values.max() + 0.5, p_values.min() - 0.1, p_values.max() + 0.1],
        cmap="magma",
        vmin=0.0,
        vmax=2.0,
    )
    ax.set_xlabel("hyperedge size k")
    ax.set_ylabel("bias parameter p")
    ax.set_yticks(p_values)
    ax.set_title("(c) Mean absolute relative error across N = 14, 28, 56, 112")
    colorbar = fig.colorbar(image, ax=ax, pad=0.01, aspect=35)
    colorbar.set_label("mean error (%)")

    fig.suptitle(
        "Frozen v4 blind validation: 1,728 unseen scenarios, k = 3,...,50",
        fontsize=12,
        fontweight="normal",
    )
    OUTPUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUTPUT, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(OUTPUT)

    with BOUNDARY_INPUT.open(encoding="utf-8-sig", newline="") as handle:
        boundary_rows = list(csv.DictReader(handle))
    bk = np.array([int(row["k"]) for row in boundary_rows])
    bp = np.array([float(row["p_bias"]) for row in boundary_rows])
    be = 100.0 * np.array([float(row["absolute_relative_error"]) for row in boundary_rows])
    bu = 100.0 * np.array([float(row["uncertainty_aware_error_upper"]) for row in boundary_rows])
    bk_values = np.array(sorted(set(bk)))
    bp_values = np.array(sorted(set(bp)))
    max_point = np.array([np.max(be[bk == value]) for value in bk_values])
    max_upper = np.array([np.max(bu[bk == value]) for value in bk_values])
    boundary_heat = np.array(
        [[np.mean(be[(bk == kval) & (bp == pval)]) for kval in bk_values] for pval in bp_values]
    )

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12.2, 6.6), constrained_layout=True)
    ax1.plot(bk_values, max_point, color="#1b9e77", marker="s", markersize=2.5, linewidth=1.0, label="maximum point error")
    ax1.plot(bk_values, max_upper, color="#d95f02", marker="o", markersize=2.5, linewidth=1.0, label="maximum simultaneous upper bound")
    ax1.axhline(5.0, color="#666666", linestyle="--", linewidth=0.9, label="5% ceiling")
    ax1.set_xlim(3, 50)
    ax1.set_ylim(0, 5.25)
    ax1.set_xlabel("hyperedge size k")
    ax1.set_ylabel("relative error (%)")
    ax1.set_title("(a) Boundary and new weak-drift confirmation for every integer k")
    ax1.grid(axis="y", color="#d9d9d9", linewidth=0.6)
    ax1.legend(frameon=False, ncol=3, loc="upper left")

    image = ax2.imshow(
        boundary_heat,
        origin="lower",
        aspect="auto",
        interpolation="nearest",
        extent=[bk_values.min() - 0.5, bk_values.max() + 0.5, -0.5, len(bp_values) - 0.5],
        cmap="magma",
        vmin=0.0,
        vmax=3.0,
    )
    ax2.set_xlabel("hyperedge size k")
    ax2.set_ylabel("bias parameter p")
    ax2.set_yticks(np.arange(len(bp_values)), labels=[f"{value:.3f}" for value in bp_values])
    ax2.set_title("(b) Mean point error across N = 10 and 128")
    colorbar = fig.colorbar(image, ax=ax2, pad=0.01, aspect=28)
    colorbar.set_label("mean error (%)")
    fig.suptitle("Frozen v4 confirmation: 384 boundary and weak-drift scenarios", fontsize=12)
    fig.savefig(BOUNDARY_OUTPUT, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(BOUNDARY_OUTPUT)


if __name__ == "__main__":
    main()
