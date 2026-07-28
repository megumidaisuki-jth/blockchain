"""Generate Nature-style figures for the hyperedge stopping-time validation.

The script uses every row of the conservative 2,112-scenario acceptance set in
the principal accuracy, heatmap and uncertainty figures. Figure 3 uses a stated
representative subset to make the scaling relations legible.
"""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle


SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
INPUT = ROOT / "results" / "drift-final-acceptance-results.csv"
OUT = SCRIPT_DIR
SOURCE_OUT = OUT / "source_data"


# Nature-style typography: editable SVG text and embedded TrueType PDF fonts.
mpl.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
        "svg.fonttype": "none",
        "pdf.fonttype": 42,
        "font.size": 7.2,
        "axes.labelsize": 7.5,
        "axes.titlesize": 8.0,
        "axes.titleweight": "normal",
        "axes.linewidth": 0.75,
        "axes.spines.right": False,
        "axes.spines.top": False,
        "xtick.labelsize": 6.6,
        "ytick.labelsize": 6.6,
        "xtick.major.width": 0.65,
        "ytick.major.width": 0.65,
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "legend.fontsize": 6.4,
        "legend.frameon": False,
        "lines.linewidth": 1.15,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    }
)


COLORS = {
    "navy": "#355C7D",
    "blue": "#4C78A8",
    "blue_soft": "#9BB7D4",
    "teal": "#72B7B2",
    "teal_dark": "#3E8E8A",
    "violet": "#9C78A8",
    "rose": "#C07A8A",
    "amber": "#D69C4E",
    "red": "#B64342",
    "grey_dark": "#4D4D4D",
    "grey_mid": "#858585",
    "grey_light": "#D9D9D9",
    "grey_pale": "#F1F1F1",
}

SOURCE_ORDER = ["blind2", "fresh_precision_confirmation", "boundary_confirmation"]
SOURCE_LABELS = {
    "blind2": "Internal blind grid",
    "fresh_precision_confirmation": "Fresh precision check",
    "boundary_confirmation": "Boundary / weak drift",
}
SOURCE_COLORS = {
    "blind2": COLORS["blue"],
    "fresh_precision_confirmation": COLORS["violet"],
    "boundary_confirmation": COLORS["teal"],
}

P_COLORS = {
    0.325: "#355C7D",
    0.94: "#79A7C7",
    1.0: "#5F5F5F",
    1.06: "#C58C99",
    1.875: "#9B4A5A",
}


def load_rows() -> list[dict]:
    with INPUT.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    numeric_int = ("k", "N", "repetitions")
    numeric_float = (
        "p_bias",
        "mc_mean",
        "mc_sd",
        "formula_mean",
        "mc_se",
        "signed_relative_error",
        "absolute_relative_error",
        "simultaneous_ci_low",
        "simultaneous_ci_high",
        "uncertainty_aware_error_upper",
    )
    for row in rows:
        for key in numeric_int:
            row[key] = int(row[key])
        for key in numeric_float:
            row[key] = float(row[key])
    return rows


def validate_rows(rows: list[dict]) -> None:
    keys = {(row["k"], row["N"], row["p_bias"]) for row in rows}
    if len(rows) != 2_112 or len(keys) != 2_112:
        raise RuntimeError("expected exactly 2,112 unique validation scenarios")
    if {row["k"] for row in rows} != set(range(3, 51)):
        raise RuntimeError("k coverage must be every integer from 3 through 50")
    expected_sources = {
        "blind2": 1_710,
        "fresh_precision_confirmation": 18,
        "boundary_confirmation": 384,
    }
    if Counter(row["source"] for row in rows) != expected_sources:
        raise RuntimeError("unexpected source composition")
    for row in rows:
        for key in (
            "mc_mean",
            "formula_mean",
            "absolute_relative_error",
            "uncertainty_aware_error_upper",
        ):
            if not math.isfinite(row[key]):
                raise RuntimeError(f"non-finite {key}")
        if row["mc_mean"] <= 0 or row["formula_mean"] <= 0:
            raise RuntimeError("log-scale stopping times must be strictly positive")


def panel_label(ax: mpl.axes.Axes, label: str, x: float = -0.12, y: float = 1.04) -> None:
    ax.text(
        x,
        y,
        label,
        transform=ax.transAxes,
        ha="left",
        va="bottom",
        fontsize=9,
        fontweight="bold",
        color="#222222",
    )


def quiet_axes(ax: mpl.axes.Axes) -> None:
    ax.tick_params(direction="out")
    ax.spines["left"].set_color("#555555")
    ax.spines["bottom"].set_color("#555555")


def save_figure(fig: mpl.figure.Figure, stem: str) -> None:
    targets = {
        "svg": OUT / "svg" / f"{stem}.svg",
        "pdf": OUT / "pdf" / f"{stem}.pdf",
        "png": OUT / "png" / f"{stem}.png",
        "tiff": OUT / "tiff" / f"{stem}.tiff",
    }
    for path in targets.values():
        path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(targets["svg"], bbox_inches="tight", pad_inches=0.03)
    fig.savefig(targets["pdf"], bbox_inches="tight", pad_inches=0.03)
    fig.savefig(targets["png"], dpi=300, bbox_inches="tight", pad_inches=0.03)
    fig.savefig(
        targets["tiff"],
        dpi=600,
        bbox_inches="tight",
        pad_inches=0.03,
        pil_kwargs={"compression": "tiff_lzw"},
    )
    plt.close(fig)


def ecdf(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x = np.sort(values)
    y = np.arange(1, len(x) + 1) / len(x)
    return x, y


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in fields})


def figure1_accuracy(rows: list[dict]) -> None:
    fig = plt.figure(figsize=(7.2, 5.55))
    gs = fig.add_gridspec(
        3,
        4,
        width_ratios=[1.0, 1.0, 0.92, 0.92],
        height_ratios=[1.0, 1.0, 1.0],
        left=0.075,
        right=0.985,
        bottom=0.09,
        top=0.975,
        hspace=0.55,
        wspace=0.72,
    )
    ax_a = fig.add_subplot(gs[:, :2])
    ax_b = fig.add_subplot(gs[0, 2:])
    ax_c = fig.add_subplot(gs[1, 2:])
    ax_d = fig.add_subplot(gs[2, 2:])

    # a | Hero parity panel.
    mc_all = np.array([row["mc_mean"] for row in rows])
    pred_all = np.array([row["formula_mean"] for row in rows])
    lo, hi = min(mc_all.min(), pred_all.min()), max(mc_all.max(), pred_all.max())
    band_x = np.geomspace(lo, hi, 300)
    ax_a.fill_between(
        band_x,
        0.95 * band_x,
        1.05 * band_x,
        color=COLORS["blue_soft"],
        alpha=0.20,
        linewidth=0,
        label="±5% band",
    )
    ax_a.plot([lo, hi], [lo, hi], color=COLORS["grey_dark"], lw=0.9, zorder=2)
    for source in SOURCE_ORDER:
        subset = [row for row in rows if row["source"] == source]
        ax_a.scatter(
            [row["mc_mean"] for row in subset],
            [row["formula_mean"] for row in subset],
            s=7 if source == "blind2" else 11,
            color=SOURCE_COLORS[source],
            alpha=0.62 if source == "blind2" else 0.82,
            edgecolors="none",
            rasterized=True,
            label=f"{SOURCE_LABELS[source]} (n={len(subset):,})",
            zorder=3,
        )
    ax_a.set_xscale("log")
    ax_a.set_yscale("log")
    ax_a.set_xlim(lo * 0.88, hi * 1.12)
    ax_a.set_ylim(lo * 0.88, hi * 1.12)
    ax_a.set_aspect("equal", adjustable="box")
    ax_a.set_xlabel("Independent Monte Carlo mean")
    ax_a.set_ylabel("Frozen-v4 prediction")
    ax_a.legend(loc="upper left", handletextpad=0.4, borderaxespad=0.2)
    ax_a.text(
        0.98,
        0.03,
        "2,112 scenarios",
        transform=ax_a.transAxes,
        ha="right",
        va="bottom",
        color=COLORS["grey_mid"],
    )
    quiet_axes(ax_a)
    panel_label(ax_a, "a", x=-0.10, y=1.02)

    # b | Error envelope over all integer k.
    k_values = np.arange(3, 51)
    max_by_k = np.array(
        [
            max(row["absolute_relative_error"] for row in rows if row["k"] == k) * 100
            for k in k_values
        ]
    )
    p95_by_k = np.array(
        [
            np.quantile(
                [row["absolute_relative_error"] for row in rows if row["k"] == k], 0.95
            )
            * 100
            for k in k_values
        ]
    )
    ax_b.fill_between(k_values, p95_by_k, max_by_k, color=COLORS["blue_soft"], alpha=0.28)
    ax_b.plot(k_values, max_by_k, color=COLORS["navy"], marker="o", ms=2.1, label="Maximum")
    ax_b.plot(k_values, p95_by_k, color=COLORS["teal_dark"], marker="s", ms=1.9, label="95th percentile")
    ax_b.axhline(4.0, color=COLORS["red"], ls=(0, (3, 2)), lw=0.9)
    ax_b.text(50.2, 4.0, "4% criterion", ha="left", va="center", color=COLORS["red"], fontsize=6.2)
    ax_b.set_xlim(3, 54.5)
    ax_b.set_ylim(0, 4.25)
    ax_b.set_xticks([3, 10, 20, 30, 40, 50])
    ax_b.set_xlabel("Hyperedge size $k$")
    ax_b.set_ylabel("Point error (%)")
    ax_b.legend(loc="upper left", ncol=2, handlelength=1.5, columnspacing=0.9)
    quiet_axes(ax_b)
    panel_label(ax_b, "b", x=-0.11, y=1.04)

    # c | ECDF directly shows threshold compliance.
    point = np.array([row["absolute_relative_error"] for row in rows]) * 100
    upper = np.array([row["uncertainty_aware_error_upper"] for row in rows]) * 100
    x_point, y_point = ecdf(point)
    x_upper, y_upper = ecdf(upper)
    ax_c.plot(x_point, y_point, color=COLORS["navy"], label="Point error")
    ax_c.plot(x_upper, y_upper, color=COLORS["amber"], label="Simultaneous upper error")
    ax_c.axvline(4.0, color=COLORS["navy"], ls=(0, (2, 2)), lw=0.75, alpha=0.65)
    ax_c.axvline(5.0, color=COLORS["red"], ls=(0, (3, 2)), lw=0.9)
    ax_c.set_xlim(0, 5.25)
    ax_c.set_ylim(0, 1.01)
    ax_c.set_yticks([0, 0.5, 0.9, 1.0])
    ax_c.set_xlabel("Relative error (%)")
    ax_c.set_ylabel("Cumulative fraction")
    ax_c.legend(loc="lower right", handlelength=1.6)
    quiet_axes(ax_c)
    panel_label(ax_c, "c", x=-0.11, y=1.04)

    # d | Distribution by independent validation source.
    datasets = [
        np.array(
            [row["absolute_relative_error"] * 100 for row in rows if row["source"] == source]
        )
        for source in SOURCE_ORDER
    ]
    positions = np.arange(1, 4)
    violin = ax_d.violinplot(
        datasets,
        positions=positions,
        widths=0.72,
        showmeans=False,
        showmedians=False,
        showextrema=False,
        bw_method=0.25,
    )
    for body, source in zip(violin["bodies"], SOURCE_ORDER):
        body.set_facecolor(SOURCE_COLORS[source])
        body.set_edgecolor("none")
        body.set_alpha(0.60)
    box = ax_d.boxplot(
        datasets,
        positions=positions,
        widths=0.15,
        showfliers=False,
        patch_artist=True,
        medianprops={"color": "#222222", "lw": 0.9},
        whiskerprops={"color": "#555555", "lw": 0.7},
        capprops={"color": "#555555", "lw": 0.7},
        boxprops={"facecolor": "white", "edgecolor": "#555555", "lw": 0.7},
    )
    _ = box
    ax_d.axhline(4.0, color=COLORS["red"], ls=(0, (3, 2)), lw=0.8)
    ax_d.set_xticks(
        positions,
        [
            "Blind\nn=1,710",
            "Precision\nn=18",
            "Boundary\nn=384",
        ],
    )
    ax_d.set_ylim(0, 4.25)
    ax_d.set_ylabel("Point error (%)")
    quiet_axes(ax_d)
    panel_label(ax_d, "d", x=-0.11, y=1.04)

    save_figure(fig, "figure1_overall_validation")


def figure2_landscape(rows: list[dict]) -> None:
    n_values = [10, 14, 28, 56, 112, 128]
    k_values = list(range(3, 51))
    cmap = LinearSegmentedColormap.from_list(
        "nature_blue",
        ["#F7FAFC", "#D6E5F2", "#93B9D4", "#4C78A8", "#274A6A"],
    )
    fig = plt.figure(figsize=(7.2, 5.95))
    gs = fig.add_gridspec(
        2,
        4,
        width_ratios=[1, 1, 1, 0.045],
        left=0.075,
        right=0.955,
        bottom=0.085,
        top=0.975,
        hspace=0.35,
        wspace=0.31,
    )
    axes = [fig.add_subplot(gs[r, c]) for r in range(2) for c in range(3)]
    panel_names = "abcdef"
    im = None
    source_rows: list[dict] = []

    for idx, (ax, N) in enumerate(zip(axes, n_values)):
        subset = [row for row in rows if row["N"] == N]
        p_values = sorted({row["p_bias"] for row in subset})
        lookup = {(row["p_bias"], row["k"]): row for row in subset}
        matrix = np.full((len(p_values), len(k_values)), np.nan)
        for r_idx, p_bias in enumerate(p_values):
            for c_idx, k in enumerate(k_values):
                row = lookup.get((p_bias, k))
                if row is not None:
                    matrix[r_idx, c_idx] = row["absolute_relative_error"] * 100
                    source_rows.append(
                        {
                            "k": k,
                            "N": N,
                            "p_bias": p_bias,
                            "absolute_relative_error_percent": matrix[r_idx, c_idx],
                        }
                    )
        im = ax.imshow(matrix, aspect="auto", interpolation="nearest", cmap=cmap, vmin=0, vmax=4)
        max_pos = np.unravel_index(np.nanargmax(matrix), matrix.shape)
        ax.add_patch(
            Rectangle(
                (max_pos[1] - 0.5, max_pos[0] - 0.5),
                1,
                1,
                fill=False,
                edgecolor=COLORS["red"],
                lw=0.8,
            )
        )
        ax.set_title(f"$N={N}$   max {np.nanmax(matrix):.2f}%")
        tick_k = [3, 10, 20, 30, 40, 50]
        ax.set_xticks([k_values.index(value) for value in tick_k], tick_k)
        if idx < 3:
            ax.tick_params(labelbottom=False)
        else:
            ax.set_xlabel("Hyperedge size $k$")
        ax.set_yticks(
            np.arange(len(p_values)),
            [f"{value:g}" for value in p_values],
        )
        if idx % 3 == 0:
            ax.set_ylabel("Bias $p$")
        ax.tick_params(length=0)
        for spine in ax.spines.values():
            spine.set_visible(False)
        panel_label(ax, panel_names[idx], x=-0.12, y=1.04)

    cax = fig.add_subplot(gs[:, 3])
    cbar = fig.colorbar(im, cax=cax, ticks=[0, 1, 2, 3, 4])
    cbar.set_label("Absolute relative error (%)")
    cbar.outline.set_linewidth(0.6)

    write_csv(
        SOURCE_OUT / "figure2_heatmap_source.csv",
        source_rows,
        ["k", "N", "p_bias", "absolute_relative_error_percent"],
    )
    save_figure(fig, "figure2_error_landscape")


def figure3_scaling(rows: list[dict]) -> None:
    selected_n = [14, 56, 112]
    selected_p = [0.325, 0.94, 1.0, 1.06, 1.875]
    fig = plt.figure(figsize=(7.2, 5.5))
    gs = fig.add_gridspec(
        2,
        3,
        height_ratios=[1.0, 1.05],
        left=0.075,
        right=0.985,
        bottom=0.09,
        top=0.91,
        hspace=0.48,
        wspace=0.34,
    )
    top_axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
    ax_d = fig.add_subplot(gs[1, :])
    source_rows: list[dict] = []

    for panel, (ax, N) in enumerate(zip(top_axes, selected_n)):
        for p_bias in selected_p:
            subset = sorted(
                [
                    row
                    for row in rows
                    if row["N"] == N and math.isclose(row["p_bias"], p_bias)
                ],
                key=lambda row: row["k"],
            )
            k = np.array([row["k"] for row in subset])
            mc = np.array([row["mc_mean"] for row in subset])
            pred = np.array([row["formula_mean"] for row in subset])
            color = P_COLORS[p_bias]
            ax.plot(k, pred, color=color, lw=1.05)
            ax.scatter(
                k,
                mc,
                s=8,
                facecolor="white",
                edgecolor=color,
                linewidth=0.65,
                zorder=3,
                rasterized=True,
            )
            for row in subset:
                source_rows.append(
                    {
                        "panel": f"N={N}",
                        "k": row["k"],
                        "N": N,
                        "p_bias": p_bias,
                        "mc_mean": row["mc_mean"],
                        "formula_mean": row["formula_mean"],
                    }
                )
        ax.set_yscale("log")
        ax.set_xlim(3, 50)
        ax.set_xticks([3, 10, 20, 30, 40, 50])
        ax.set_title(f"$N={N}$")
        ax.set_xlabel("Hyperedge size $k$")
        if panel == 0:
            ax.set_ylabel("Expected stopping time")
        quiet_axes(ax)
        panel_label(ax, "abc"[panel], x=-0.18, y=1.04)

    p_handles = [
        Line2D(
            [0],
            [0],
            color=P_COLORS[p],
            marker="o",
            markerfacecolor="white",
            markeredgewidth=0.65,
            markersize=3.2,
            lw=1.0,
            label=f"$p={p:g}$",
        )
        for p in selected_p
    ]
    fig.legend(
        handles=p_handles,
        loc="upper center",
        bbox_to_anchor=(0.52, 0.995),
        ncol=5,
        handlelength=1.6,
        columnspacing=1.1,
    )

    # d | Drift-response profile at fixed N, with direct labels by k.
    N = 56
    k_profiles = [3, 10, 30, 50]
    k_colors = ["#A9BED1", "#7599B8", "#4C78A8", "#274A6A"]
    for k_value, color in zip(k_profiles, k_colors):
        subset = sorted(
            [row for row in rows if row["N"] == N and row["k"] == k_value],
            key=lambda row: row["p_bias"],
        )
        p = np.array([row["p_bias"] for row in subset])
        mc_norm = np.array([row["mc_mean"] / (N * N) for row in subset])
        pred_norm = np.array([row["formula_mean"] / (N * N) for row in subset])
        ax_d.plot(p, pred_norm, color=color, lw=1.2)
        ax_d.scatter(
            p,
            mc_norm,
            s=12,
            facecolor="white",
            edgecolor=color,
            linewidth=0.7,
            rasterized=True,
            zorder=3,
        )
        ax_d.text(
            p[-1] + 0.025,
            pred_norm[-1],
            f"$k={k_value}$",
            color=color,
            va="center",
            fontsize=6.5,
        )
        for row in subset:
            source_rows.append(
                {
                    "panel": "drift profile N=56",
                    "k": row["k"],
                    "N": N,
                    "p_bias": row["p_bias"],
                    "mc_mean": row["mc_mean"],
                    "formula_mean": row["formula_mean"],
                }
            )
    ax_d.axvline(1.0, color=COLORS["grey_mid"], ls=(0, (2, 2)), lw=0.8)
    ax_d.text(
        1.0,
        1.015,
        "zero drift",
        transform=ax_d.get_xaxis_transform(),
        ha="center",
        va="bottom",
        color=COLORS["grey_mid"],
    )
    ax_d.set_xlim(0.28, 2.08)
    ax_d.set_xlabel("Bias parameter $p$")
    ax_d.set_ylabel("Normalized stopping time $E[\\tau]/N^2$")
    quiet_axes(ax_d)
    panel_label(ax_d, "d", x=-0.045, y=1.04)

    write_csv(
        SOURCE_OUT / "figure3_scaling_source.csv",
        source_rows,
        ["panel", "k", "N", "p_bias", "mc_mean", "formula_mean"],
    )
    save_figure(fig, "figure3_stopping_time_scaling")


def figure4_uncertainty(rows: list[dict]) -> None:
    fig = plt.figure(figsize=(7.2, 5.9))
    gs = fig.add_gridspec(
        2,
        2,
        width_ratios=[1.05, 1.0],
        height_ratios=[1.0, 1.12],
        left=0.08,
        right=0.985,
        bottom=0.09,
        top=0.975,
        hspace=0.47,
        wspace=0.42,
    )
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[:, 1])
    lower = gs[1, 0].subgridspec(1, 2, width_ratios=[1.08, 1.0], wspace=0.68)
    ax_c = fig.add_subplot(lower[0, 0])
    ax_d = fig.add_subplot(lower[0, 1])

    # a | Point error versus conservative upper error.
    for source in SOURCE_ORDER:
        subset = [row for row in rows if row["source"] == source]
        ax_a.scatter(
            [row["absolute_relative_error"] * 100 for row in subset],
            [row["uncertainty_aware_error_upper"] * 100 for row in subset],
            s=7 if source == "blind2" else 10,
            color=SOURCE_COLORS[source],
            alpha=0.55 if source == "blind2" else 0.78,
            edgecolors="none",
            rasterized=True,
            label=SOURCE_LABELS[source],
        )
    ax_a.plot([0, 5], [0, 5], color=COLORS["grey_mid"], ls=(0, (2, 2)), lw=0.75)
    ax_a.axhline(5.0, color=COLORS["red"], ls=(0, (3, 2)), lw=0.9)
    ax_a.set_xlim(0, 4.1)
    ax_a.set_ylim(0, 5.15)
    ax_a.set_xlabel("Point error (%)")
    ax_a.set_ylabel("Simultaneous upper error (%)")
    ax_a.legend(loc="upper left", handletextpad=0.35)
    quiet_axes(ax_a)
    panel_label(ax_a, "a", x=-0.15, y=1.04)

    # b | Forest-style audit of the 20 largest upper bounds.
    worst = sorted(rows, key=lambda row: row["uncertainty_aware_error_upper"], reverse=True)[:20]
    worst = list(reversed(worst))
    y = np.arange(len(worst))
    ax_b.axvspan(-5, 5, color=COLORS["grey_pale"], zorder=0)
    for yi, row in zip(y, worst):
        pred = row["formula_mean"]
        rel_a = pred / row["simultaneous_ci_high"] - 1.0
        rel_b = pred / row["simultaneous_ci_low"] - 1.0
        ci_low, ci_high = sorted([rel_a * 100, rel_b * 100])
        point = row["signed_relative_error"] * 100
        color = SOURCE_COLORS[row["source"]]
        ax_b.plot([ci_low, ci_high], [yi, yi], color=color, lw=1.1, solid_capstyle="round")
        ax_b.plot(point, yi, marker="o", ms=3.0, color=color)
    ax_b.axvline(0, color=COLORS["grey_dark"], lw=0.75)
    ax_b.axvline(-5, color=COLORS["red"], ls=(0, (3, 2)), lw=0.75)
    ax_b.axvline(5, color=COLORS["red"], ls=(0, (3, 2)), lw=0.75)
    ax_b.set_yticks(
        y,
        [f"k={r['k']}, N={r['N']}, p={r['p_bias']:g}" for r in worst],
    )
    ax_b.set_xlim(-5.4, 5.4)
    ax_b.set_xlabel("Signed prediction error and simultaneous interval (%)")
    ax_b.set_title("20 largest conservative upper bounds", loc="left")
    quiet_axes(ax_b)
    panel_label(ax_b, "b", x=-0.42, y=1.02)

    # c | Signed-error distribution by drift regime.
    regimes = [
        ("Negative drift", [row["signed_relative_error"] * 100 for row in rows if row["p_bias"] < 1]),
        ("Zero drift", [row["signed_relative_error"] * 100 for row in rows if math.isclose(row["p_bias"], 1)]),
        ("Positive drift", [row["signed_relative_error"] * 100 for row in rows if row["p_bias"] > 1]),
    ]
    regime_colors = [COLORS["blue"], COLORS["grey_mid"], COLORS["rose"]]
    datasets = [np.array(values) for _, values in regimes]
    positions = np.arange(1, 4)
    vp = ax_c.violinplot(
        datasets,
        positions=positions,
        widths=0.75,
        showmeans=False,
        showmedians=False,
        showextrema=False,
        bw_method=0.22,
    )
    for body, color in zip(vp["bodies"], regime_colors):
        body.set_facecolor(color)
        body.set_edgecolor("none")
        body.set_alpha(0.62)
    ax_c.boxplot(
        datasets,
        positions=positions,
        widths=0.14,
        showfliers=False,
        patch_artist=True,
        medianprops={"color": "#222222", "lw": 0.9},
        whiskerprops={"color": "#555555", "lw": 0.65},
        capprops={"color": "#555555", "lw": 0.65},
        boxprops={"facecolor": "white", "edgecolor": "#555555", "lw": 0.65},
    )
    ax_c.axhline(0, color=COLORS["grey_dark"], lw=0.75)
    ax_c.set_xticks(
        positions,
        [
            f"Neg.\nn={len(datasets[0]):,}",
            f"Zero\nn={len(datasets[1]):,}",
            f"Pos.\nn={len(datasets[2]):,}",
        ],
    )
    ax_c.set_xlim(0.45, 3.55)
    ax_c.set_ylabel("Signed error (%)")
    quiet_axes(ax_c)
    panel_label(ax_c, "c", x=-0.15, y=1.04)

    # d | Threshold-normalized acceptance metrics.
    point = np.array([row["absolute_relative_error"] for row in rows]) * 100
    signed = np.array([row["signed_relative_error"] for row in rows]) * 100
    upper = np.array([row["uncertainty_aware_error_upper"] for row in rows]) * 100
    metric_names = ["P95", "RMS", "Maximum", "Max upper"]
    metric_values = [
        np.quantile(point, 0.95),
        math.sqrt(np.mean(signed * signed)),
        np.max(point),
        np.max(upper),
    ]
    thresholds = [3.0, 2.0, 4.0, 5.0]
    ratios = np.array(metric_values) / np.array(thresholds)
    ypos = np.arange(4)
    ax_d.barh(ypos, ratios, color=[COLORS["blue"], COLORS["teal"], COLORS["navy"], COLORS["amber"]], height=0.58)
    ax_d.axvline(1.0, color=COLORS["red"], ls=(0, (3, 2)), lw=0.8)
    ax_d.set_yticks(ypos, metric_names)
    ax_d.set_xlim(0, 1.08)
    ax_d.set_xticks([0, 0.5, 1.0])
    ax_d.set_xlabel("Fraction of threshold")
    ax_d.invert_yaxis()
    for yi, ratio, value in zip(ypos, ratios, metric_values):
        ax_d.text(
            max(ratio - 0.025, 0.08),
            yi,
            f"{value:.2f}%",
            ha="right",
            va="center",
            fontsize=5.8,
            color="white",
        )
    ax_d.spines["left"].set_visible(False)
    ax_d.tick_params(axis="y", length=0)
    panel_label(ax_d, "d", x=-0.42, y=1.04)

    top_keys = {(row["k"], row["N"], row["p_bias"]) for row in worst}
    source_rows = []
    for row in rows:
        source_rows.append(
            {
                "k": row["k"],
                "N": row["N"],
                "p_bias": row["p_bias"],
                "source": row["source"],
                "signed_relative_error_percent": row["signed_relative_error"] * 100,
                "absolute_relative_error_percent": row["absolute_relative_error"] * 100,
                "uncertainty_aware_error_upper_percent": row["uncertainty_aware_error_upper"] * 100,
                "top20_conservative_bound": (row["k"], row["N"], row["p_bias"]) in top_keys,
            }
        )
    write_csv(
        SOURCE_OUT / "figure4_uncertainty_source.csv",
        source_rows,
        [
            "k",
            "N",
            "p_bias",
            "source",
            "signed_relative_error_percent",
            "absolute_relative_error_percent",
            "uncertainty_aware_error_upper_percent",
            "top20_conservative_bound",
        ],
    )
    save_figure(fig, "figure4_uncertainty_audit")


def write_common_source(rows: list[dict]) -> None:
    fields = [
        "k",
        "N",
        "p_bias",
        "source",
        "repetitions",
        "mc_mean",
        "mc_sd",
        "mc_se",
        "formula_mean",
        "signed_relative_error",
        "absolute_relative_error",
        "simultaneous_ci_low",
        "simultaneous_ci_high",
        "uncertainty_aware_error_upper",
    ]
    write_csv(SOURCE_OUT / "all_2112_validation_scenarios.csv", rows, fields)
    point = np.array([row["absolute_relative_error"] for row in rows])
    signed = np.array([row["signed_relative_error"] for row in rows])
    upper = np.array([row["uncertainty_aware_error_upper"] for row in rows])
    summary = {
        "scenario_count": len(rows),
        "unique_k_count": len({row["k"] for row in rows}),
        "k_min": min(row["k"] for row in rows),
        "k_max": max(row["k"] for row in rows),
        "mean_absolute_relative_error_percent": float(point.mean() * 100),
        "p95_absolute_relative_error_percent": float(np.quantile(point, 0.95) * 100),
        "rms_relative_error_percent": float(math.sqrt(np.mean(signed * signed)) * 100),
        "max_absolute_relative_error_percent": float(point.max() * 100),
        "max_uncertainty_aware_error_upper_percent": float(upper.max() * 100),
        "source_counts": Counter(row["source"] for row in rows),
        "figure3_subset_rule": {
            "scaling_panels": "N in {14,56,112}; p in {0.325,0.94,1,1.06,1.875}; all k",
            "drift_profile": "N=56; k in {3,10,30,50}; all available internal p",
            "reason": "representative negative, near-neutral, neutral and positive drift curves at three capacity scales",
        },
        "uncertainty_note": "Bonferroni-normal large-sample simultaneous intervals; not distribution-free finite-sample guarantees",
    }
    (SOURCE_OUT / "figure_statistics.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main() -> None:
    rows = load_rows()
    validate_rows(rows)
    SOURCE_OUT.mkdir(parents=True, exist_ok=True)
    write_common_source(rows)
    figure1_accuracy(rows)
    figure2_landscape(rows)
    figure3_scaling(rows)
    figure4_uncertainty(rows)
    print(f"Nature figures written to: {OUT}")


if __name__ == "__main__":
    main()
