"""Render the unified-clock warning and equal-capital topology figure.

The plotting path reads only gate-passing formal results and emits exactly one
PNG, as requested for the manuscript workflow.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

import matplotlib as mpl
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch
import matplotlib.pyplot as plt
import numpy as np


TOPOLOGY_ORDER = ("chain", "star", "branch")
TOPOLOGY_LABELS = {"chain": "链式", "star": "星形", "branch": "分支式"}
TOPOLOGY_COLORS = {
    "chain": "#0072B2",
    "star": "#D55E00",
    "branch": "#009E73",
}
TOPOLOGY_MARKERS = {"chain": "o", "star": "s", "branch": "^"}
ENDPOINT_LABELS = {"first_zero": "首次触零", "first_failure": "首次余额拒绝"}
ENDPOINT_STYLES = {"first_zero": "-", "first_failure": "--"}
ENDPOINT_MARKERS = {"first_zero": "o", "first_failure": "D"}
FIGURE_WIDTH_MM = 183.0
FIGURE_HEIGHT_MM = 152.0
FIGURE_DPI = 600


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _require_columns(
    rows: list[dict[str, str]], required: Iterable[str], table_name: str
) -> None:
    if not rows:
        raise ValueError(f"{table_name} is empty")
    missing = sorted(set(required) - set(rows[0]))
    if missing:
        raise ValueError(f"{table_name} is missing columns: {missing}")


def _font_family() -> str:
    available = {entry.name for entry in font_manager.fontManager.ttflist}
    for candidate in (
        "Microsoft YaHei",
        "Noto Sans CJK SC",
        "Source Han Sans SC",
        "SimHei",
        "Arial Unicode MS",
    ):
        if candidate in available:
            return candidate
    return "DejaVu Sans"


def _configure_style() -> None:
    mpl.rcParams.update(
        {
            "font.family": _font_family(),
            "axes.unicode_minus": False,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "font.size": 7.4,
            "axes.labelsize": 7.4,
            "axes.titlesize": 7.8,
            "xtick.labelsize": 6.8,
            "ytick.labelsize": 6.8,
            "legend.fontsize": 6.5,
            "axes.linewidth": 0.65,
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.55,
            "xtick.major.size": 2.8,
            "ytick.major.size": 2.8,
            "savefig.dpi": FIGURE_DPI,
        }
    )


def _panel_label(axis: plt.Axes, label: str) -> None:
    axis.text(
        -0.13,
        1.05,
        label,
        transform=axis.transAxes,
        fontsize=9,
        fontweight="bold",
        va="top",
        ha="left",
    )


def _draw_design_panel(axis: plt.Axes) -> None:
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    _panel_label(axis, "a")

    y = 0.70
    axis.annotate(
        "",
        xy=(0.94, y),
        xytext=(0.06, y),
        arrowprops={"arrowstyle": "->", "lw": 0.8, "color": "#333333"},
    )
    hit_x, failure_x = 0.35, 0.79
    axis.plot([hit_x, hit_x], [y - 0.055, y + 0.055], color="#0072B2", lw=1.3)
    axis.plot(
        [failure_x, failure_x], [y - 0.055, y + 0.055], color="#D55E00", lw=1.3
    )
    axis.text(hit_x, y + 0.09, r"首次触零 $T_0$", ha="center", va="bottom")
    axis.text(failure_x, y + 0.09, r"首次拒绝 $R$", ha="center", va="bottom")
    axis.annotate(
        "",
        xy=(failure_x, y - 0.12),
        xytext=(hit_x, y - 0.12),
        arrowprops={"arrowstyle": "<->", "lw": 0.75, "color": "#555555"},
    )
    axis.text((hit_x + failure_x) / 2, y - 0.17, r"提前量 $L=R-T_0$", ha="center")
    for x in (0.46, 0.55, 0.64, 0.73):
        axis.plot(x, y, marker="|", color="#777777", ms=6, mew=0.65)
    axis.text(0.50, 0.92, "统一请求时钟（接受与拒绝均计数）", ha="center", fontweight="bold")

    cards = (
        (0.06, "节点数相同\n$n=9$"),
        (0.30, "人均资本相同\n$C_v=4N$"),
        (0.54, "总资本相同\n$C=36N$"),
        (0.78, "需求相同\n72 个有向 OD"),
    )
    for x, text in cards:
        patch = FancyBboxPatch(
            (x, 0.10),
            0.17,
            0.22,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            ec="#777777",
            fc="#F5F5F5",
            lw=0.65,
        )
        axis.add_patch(patch)
        axis.text(
            x + 0.085,
            0.21,
            text,
            ha="center",
            va="center",
            linespacing=1.35,
            fontsize=6.4,
        )


def _draw_risk_panel(axis: plt.Axes, rows: list[dict[str, str]]) -> None:
    _panel_label(axis, "b")
    pooled = [row for row in rows if row["stage"] == "pooled"]
    if not pooled:
        raise ValueError("pooled warning-risk estimates are absent")
    maximum_scale = max(int(row["scale"]) for row in pooled)
    for topology in TOPOLOGY_ORDER:
        selected = sorted(
            (
                row
                for row in pooled
                if row["topology"] == topology and int(row["scale"]) == maximum_scale
            ),
            key=lambda row: int(row["horizon_requests"]),
        )
        x = np.asarray([int(row["horizon_requests"]) for row in selected])
        y = np.asarray([float(row["mean"]) for row in selected])
        error = np.asarray([float(row["simultaneous_half_width"]) for row in selected])
        axis.errorbar(
            x,
            y,
            yerr=error,
            color=TOPOLOGY_COLORS[topology],
            marker=TOPOLOGY_MARKERS[topology],
            ms=3.3,
            lw=1.0,
            elinewidth=0.65,
            capsize=1.8,
            label=TOPOLOGY_LABELS[topology],
        )
    axis.set_xlabel("触零后的请求窗口 $h$")
    axis.set_ylabel(r"后续拒绝风险 $\Pr(L\leq h)$")
    axis.set_xticks(sorted({int(row["horizon_requests"]) for row in pooled}))
    axis.set_ylim(-0.025, 1.025)
    axis.grid(axis="y", color="#D9D9D9", lw=0.45, alpha=0.8)
    axis.legend(frameon=False, loc="lower right", title=f"$N={maximum_scale}$")


def _draw_time_panel(axis: plt.Axes, rows: list[dict[str, str]]) -> None:
    _panel_label(axis, "c")
    pooled = [row for row in rows if row["stage"] == "pooled"]
    if not pooled:
        raise ValueError("pooled time estimates are absent")
    scales = sorted({int(row["scale"]) for row in pooled})
    for topology in TOPOLOGY_ORDER:
        for endpoint in ENDPOINT_LABELS:
            selected = sorted(
                (
                    row
                    for row in pooled
                    if row["topology"] == topology and row["endpoint"] == endpoint
                ),
                key=lambda row: int(row["scale"]),
            )
            x = np.arange(len(selected), dtype=float)
            y = np.asarray([float(row["mean"]) for row in selected])
            error = np.asarray(
                [float(row["simultaneous_half_width"]) for row in selected]
            )
            axis.errorbar(
                x,
                y,
                yerr=error,
                color=TOPOLOGY_COLORS[topology],
                linestyle=ENDPOINT_STYLES[endpoint],
                marker=ENDPOINT_MARKERS[endpoint],
                ms=2.8,
                lw=0.9,
                elinewidth=0.55,
                capsize=1.4,
            )
    axis.set_xticks(np.arange(len(scales)), labels=[str(value) for value in scales])
    axis.set_xlabel("资本尺度 $N$")
    axis.set_ylabel(r"归一化平均请求时刻 $\mathbb{E}T/(4N)^2$")
    axis.grid(axis="y", color="#D9D9D9", lw=0.45, alpha=0.8)
    topology_handles = [
        Line2D(
            [0],
            [0],
            color=TOPOLOGY_COLORS[name],
            marker=TOPOLOGY_MARKERS[name],
            lw=1,
            ms=3,
            label=TOPOLOGY_LABELS[name],
        )
        for name in TOPOLOGY_ORDER
    ]
    endpoint_handles = [
        Line2D(
            [0],
            [0],
            color="#333333",
            linestyle=ENDPOINT_STYLES[name],
            marker=ENDPOINT_MARKERS[name],
            lw=1,
            ms=3,
            label=ENDPOINT_LABELS[name],
        )
        for name in ENDPOINT_LABELS
    ]
    first_legend = axis.legend(
        handles=topology_handles, frameon=False, loc="upper right", ncol=3
    )
    axis.add_artist(first_legend)
    axis.legend(handles=endpoint_handles, frameon=False, loc="lower right")


def _draw_contrast_panel(axis: plt.Axes, rows: list[dict[str, str]]) -> None:
    _panel_label(axis, "d")
    order = []
    for endpoint in ("first_zero", "first_failure"):
        for contrast in ("chain_minus_star", "chain_minus_branch", "star_minus_branch"):
            order.append((endpoint, contrast))
    lookup = {(row["endpoint"], row["contrast"]): row for row in rows}
    if set(order) != set(lookup):
        raise ValueError("the six prespecified paired topology contrasts are incomplete")
    label_map = {
        "chain_minus_star": "链式−星形",
        "chain_minus_branch": "链式−分支式",
        "star_minus_branch": "星形−分支式",
    }
    y_positions = np.arange(len(order))[::-1]
    labels: list[str] = []
    for y, key in zip(y_positions, order):
        endpoint, contrast = key
        row = lookup[key]
        mean = float(row["mean"])
        low = float(row["simultaneous_ci_low"])
        high = float(row["simultaneous_ci_high"])
        color = "#0072B2" if endpoint == "first_zero" else "#D55E00"
        axis.errorbar(
            mean,
            y,
            xerr=[[mean - low], [high - mean]],
            color=color,
            marker=ENDPOINT_MARKERS[endpoint],
            ms=3.5,
            lw=0,
            elinewidth=0.9,
            capsize=2.0,
        )
        labels.append(f"{ENDPOINT_LABELS[endpoint]}：{label_map[contrast]}")
    axis.axvline(0, color="#555555", lw=0.7, linestyle=":")
    axis.set_yticks(y_positions, labels=labels)
    axis.set_xlabel(r"配对均值差（按 $(4N)^2$ 归一化）")
    axis.grid(axis="x", color="#D9D9D9", lw=0.45, alpha=0.8)
    axis.text(
        0.01,
        0.02,
        "正值表示差值中的前一拓扑更晚",
        transform=axis.transAxes,
        ha="left",
        va="bottom",
        color="#555555",
        fontsize=6.4,
    )


def render_figure(*, result_dir: Path, output_path: Path) -> None:
    metadata_path = result_dir / "request-clock-metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if metadata.get("status") != "PASS" or not all(metadata.get("gates", {}).values()):
        raise ValueError("refusing to plot results that did not pass every frozen gate")
    if metadata.get("quick"):
        raise ValueError("refusing to publish a quick-run figure")

    risk_rows = _load_csv(result_dir / "request-clock-warning-risk.csv")
    time_rows = _load_csv(result_dir / "request-clock-time-summary.csv")
    contrast_rows = _load_csv(result_dir / "request-clock-topology-contrasts.csv")
    _require_columns(
        risk_rows,
        {
            "stage",
            "topology",
            "scale",
            "horizon_requests",
            "mean",
            "simultaneous_half_width",
        },
        "request-clock-warning-risk.csv",
    )
    _require_columns(
        time_rows,
        {
            "stage",
            "topology",
            "scale",
            "endpoint",
            "mean",
            "simultaneous_half_width",
        },
        "request-clock-time-summary.csv",
    )
    _require_columns(
        contrast_rows,
        {
            "stage",
            "endpoint",
            "contrast",
            "mean",
            "simultaneous_ci_low",
            "simultaneous_ci_high",
        },
        "request-clock-topology-contrasts.csv",
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    for suffix in (".svg", ".pdf", ".tif", ".tiff"):
        alternate = output_path.with_suffix(suffix)
        if alternate.exists():
            raise ValueError(f"forbidden alternate figure exists: {alternate}")

    _configure_style()
    width = FIGURE_WIDTH_MM / 25.4
    height = FIGURE_HEIGHT_MM / 25.4
    figure, axes = plt.subplots(2, 2, figsize=(width, height), constrained_layout=True)
    _draw_design_panel(axes[0, 0])
    _draw_risk_panel(axes[0, 1], risk_rows)
    _draw_time_panel(axes[1, 0], time_rows)
    _draw_contrast_panel(axes[1, 1], contrast_rows)
    figure.savefig(
        output_path,
        dpi=FIGURE_DPI,
        format="png",
        facecolor="white",
        metadata={
            "Title": "统一请求时钟预警与等资本拓扑比较",
            "Software": "matplotlib",
        },
    )
    plt.close(figure)


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    render_figure(
        result_dir=root / "results" / "request-clock-topology-validation",
        output_path=(
            root
            / "outputs"
            / "researchwrite"
            / "hypergraph-stopping-time"
            / "figures"
            / "fig_request_clock_topology_validation.png"
        ),
    )
