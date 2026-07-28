"""Create publication figures for historical and current Lightning validation."""
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "researchwrite" / "hypergraph-stopping-time" / "figures"

mpl.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans", "sans-serif"],
    "svg.fonttype": "none",
    "pdf.fonttype": 42,
    "font.size": 7,
    "axes.spines.right": False,
    "axes.spines.top": False,
    "axes.linewidth": 0.8,
    "legend.frameon": False,
})

BLUE, ORANGE, GREY, RED = "#4C78A8", "#F28E2B", "#777777", "#C44E52"


def read(relative):
    return pd.read_csv(ROOT / relative)


def effect_panel(ax, frame, title, date_labels):
    frame = frame.sort_values(["date", "mode", "demand_kind", "scale"]).reset_index(drop=True)
    x = np.arange(len(frame))
    y = frame["pooled_mean_difference"].to_numpy()
    lo = frame["pooled_ci_low"].to_numpy()
    hi = frame["pooled_ci_high"].to_numpy()
    colors = np.where(y >= 0, ORANGE, BLUE)
    ax.axhline(0, color="black", lw=0.7)
    ax.errorbar(x, y, yerr=np.vstack([y-lo, hi-y]), fmt="none", ecolor=GREY, lw=0.7, capsize=1.2)
    ax.scatter(x, y, c=colors, s=10, zorder=3)
    ax.set_title(title, loc="left", fontweight="bold")
    ax.set_ylabel("Correlated − independent\nmean stopping time")
    ax.set_xticks([])
    starts = frame.groupby("date", sort=False).head(1).index.to_list()
    ends = frame.groupby("date", sort=False).tail(1).index.to_list()
    for i, (start, end) in enumerate(zip(starts, ends)):
        ax.text((start+end)/2, ax.get_ylim()[0], date_labels[i], ha="center", va="top", fontsize=6)
        if i and start:
            ax.axvline(start-0.5, color="#DDDDDD", lw=0.6)


def save_all(fig, stem):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{stem}.svg", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.pdf", bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.tiff", dpi=600, bbox_inches="tight")
    fig.savefig(OUT / f"{stem}.png", dpi=300, bbox_inches="tight")


def main():
    hist_pool = read("results/lightning-real-topology-pooled-sensitivity/lightning-real-topology-pooled-sensitivity.csv")
    curr_pool = read("results/lightning-current-2026-pooled-sensitivity/lightning-current-2026-pooled-sensitivity.csv")
    hist_cmp = read("results/lightning-real-topology-replication-comparison/lightning-replication-comparison.csv")
    curr_cmp = read("results/lightning-current-2026-replication-comparison/lightning-current-2026-replication-comparison.csv")

    fig, axes = plt.subplots(2, 2, figsize=(183/25.4, 128/25.4), constrained_layout=True)
    effect_panel(axes[0, 0], hist_pool, "a  Historical topology: pooled sensitivity", ["2020", "2022", "2023"])
    effect_panel(axes[0, 1], curr_pool, "b  Current-2026 filtered projection: pooled sensitivity", ["2026"])

    ax = axes[1, 0]
    ax.axline((0, 0), slope=1, color="black", lw=0.8, ls="--")
    ax.scatter(hist_cmp["formal_mean"], hist_cmp["replication_mean"], s=12, alpha=0.75, color=BLUE, label="Historical (48 cells)")
    ax.scatter(curr_cmp["formal_mean"], curr_cmp["replication_mean"], s=18, alpha=0.85, color=ORANGE, label="Current 2026 (16 cells)")
    bounds = np.array([hist_cmp.formal_mean.min(), hist_cmp.formal_mean.max(), hist_cmp.replication_mean.min(), hist_cmp.replication_mean.max(), curr_cmp.formal_mean.min(), curr_cmp.formal_mean.max(), curr_cmp.replication_mean.min(), curr_cmp.replication_mean.max()])
    pad = 0.006
    ax.set_xlim(bounds.min()-pad, bounds.max()+pad); ax.set_ylim(bounds.min()-pad, bounds.max()+pad)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("Formal mean difference"); ax.set_ylabel("Replication mean difference")
    ax.set_title("c  Independent replication consistency", loc="left", fontweight="bold")
    ax.legend(loc="upper left", fontsize=6)
    ax.text(0.98, 0.03, "All 64 direct simultaneous CIs include zero", transform=ax.transAxes, ha="right", va="bottom", fontsize=6)

    ax = axes[1, 1]
    layers = [
        ("Hist. formal", hist_cmp["formal_block_ci_halfwidth"], BLUE),
        ("Hist. repl.", hist_cmp["replication_block_ci_halfwidth"], BLUE),
        ("Hist. pooled", hist_pool["pooled_ci_halfwidth"], BLUE),
        ("2026 formal", curr_cmp["formal_block_ci_halfwidth"], ORANGE),
        ("2026 repl.", curr_cmp["replication_block_ci_halfwidth"], ORANGE),
        ("2026 pooled", curr_pool["pooled_ci_halfwidth"], ORANGE),
    ]
    for i, (label, values, color) in enumerate(layers):
        jitter = np.linspace(-0.13, 0.13, len(values))
        ax.scatter(np.full(len(values), i)+jitter, values, s=8, alpha=0.65, color=color)
        ax.plot([i-0.2, i+0.2], [values.max(), values.max()], color="black", lw=1)
    ax.axhline(0.03, color=RED, lw=1, ls="--", label="Precision target = 0.03")
    ax.set_xticks(range(len(layers)), [x[0] for x in layers], rotation=28, ha="right")
    ax.set_ylabel("Simultaneous CI half-width")
    ax.set_title("d  Precision audit", loc="left", fontweight="bold")
    ax.legend(loc="upper right", fontsize=6)

    save_all(fig, "fig_real_topology_validation")
    plt.close(fig)


if __name__ == "__main__":
    main()
