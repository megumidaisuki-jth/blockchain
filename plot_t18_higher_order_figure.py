"""Render the frozen T18 higher-order cross-topology validation figure.

The script is intentionally read-only with respect to the T18 experiment.  It
accepts only the accepted primary grid, exact-anchor, and weakest-cell
sensitivity outputs, validates their manifests and frozen design, and writes a
single publication PNG plus a machine-readable input audit.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Iterable, Mapping

import matplotlib as mpl
from matplotlib import font_manager
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle
import matplotlib.pyplot as plt
import numpy as np


FIGURE_WIDTH_MM = 170.0
FIGURE_HEIGHT_MM = 140.0
FIGURE_DPI = 600
SIMULTANEOUS_MULTIPLIER = 3.1969502291312546
EXACT_Z_GATE = 3.29
TOPOLOGY_ORDER = ("chain", "star", "random")
REGIME_ORDER = ("balanced", "positive", "negative")
SCALE_GRID = (10, 20, 40, 80)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_input_paths(project_root: Path) -> dict[str, Path]:
    project_root = project_root.resolve()
    primary = project_root / "results" / "t18-cross-topology"
    anchors = project_root / "results" / "t18-exact-anchors"
    weakest = project_root / "results" / "t18-weakest-sensitivity"
    return {
        "primary_csv": primary / "t18-primary-effects.csv",
        "primary_metadata": primary / "t18-run-metadata.json",
        "primary_manifest": primary / "SHA256SUMS.txt",
        "anchor_csv": anchors / "t18-exact-anchors.csv",
        "anchor_metadata": anchors / "t18-exact-anchor-metadata.json",
        "anchor_manifest": anchors / "SHA256SUMS.txt",
        "weakest_csv": weakest / "t18-weakest-cell-sensitivity.csv",
        "weakest_metadata": weakest / "t18-weakest-cell-metadata.json",
        "weakest_manifest": weakest / "SHA256SUMS.txt",
    }


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"metadata must be a JSON object: {path}")
    return value


def _as_bool(value: str) -> bool:
    if value == "True":
        return True
    if value == "False":
        return False
    raise ValueError(f"expected CSV boolean True/False, received {value!r}")


def _assert_close(actual: float, expected: float, tolerance: float, message: str) -> None:
    if not math.isfinite(actual) or abs(actual - expected) > tolerance:
        raise ValueError(f"{message}: expected {expected!r}, received {actual!r}")


def _verify_sha256_manifest(manifest_path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        pieces = line.split(maxsplit=1)
        if len(pieces) != 2 or len(pieces[0]) != 64:
            raise ValueError(f"malformed SHA256 manifest line in {manifest_path}: {line!r}")
        expected, filename = pieces
        filename = filename.lstrip("* ")
        target = manifest_path.parent / filename
        if not target.is_file():
            raise ValueError(f"manifest target is missing: {target}")
        actual = sha256_file(target)
        if actual != expected.lower():
            raise ValueError(f"SHA-256 mismatch for {target.name}: {actual} != {expected}")
        entries[filename] = actual
    if not entries:
        raise ValueError(f"empty SHA256 manifest: {manifest_path}")
    return entries


def _refuse_rejected_seed_paths(paths: Mapping[str, Path]) -> None:
    rejected = [str(path) for path in paths.values() if "rejected" in str(path).lower()]
    if rejected:
        raise ValueError(
            "rejected-seed inputs are forbidden by the frozen figure contract: "
            + ", ".join(rejected)
        )


def validate_and_load_inputs(paths: Mapping[str, Path]) -> dict[str, Any]:
    """Validate accepted T18 outputs and return parsed records.

    Every deterministic condition is fail-closed: plotting never begins after
    a provenance, hash, row-count, grid, or interval-sign failure.
    """

    normalized_paths = {name: Path(path).resolve() for name, path in paths.items()}
    _refuse_rejected_seed_paths(normalized_paths)
    missing = [str(path) for path in normalized_paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError("missing frozen T18 input(s): " + ", ".join(missing))

    manifests = {
        "primary": _verify_sha256_manifest(normalized_paths["primary_manifest"]),
        "anchors": _verify_sha256_manifest(normalized_paths["anchor_manifest"]),
        "weakest": _verify_sha256_manifest(normalized_paths["weakest_manifest"]),
    }
    primary = _load_csv(normalized_paths["primary_csv"])
    anchors = _load_csv(normalized_paths["anchor_csv"])
    weakest = _load_csv(normalized_paths["weakest_csv"])
    metadata = {
        "primary": _load_json(normalized_paths["primary_metadata"]),
        "anchors": _load_json(normalized_paths["anchor_metadata"]),
        "weakest": _load_json(normalized_paths["weakest_metadata"]),
    }

    if len(primary) != 36:
        raise ValueError(f"primary grid must contain 36 rows, received {len(primary)}")
    expected_cells = {
        (topology, regime, scale)
        for topology in TOPOLOGY_ORDER
        for regime in REGIME_ORDER
        for scale in SCALE_GRID
    }
    actual_cells = {
        (row["topology"], row["regime"], int(row["scale"])) for row in primary
    }
    if actual_cells != expected_cells:
        missing_cells = sorted(expected_cells - actual_cells)
        extra_cells = sorted(actual_cells - expected_cells)
        raise ValueError(f"primary grid mismatch; missing={missing_cells}, extra={extra_cells}")
    if len(actual_cells) != len(primary):
        raise ValueError("primary grid contains duplicate cells")
    if {int(row["repetitions"]) for row in primary} != {30000}:
        raise ValueError("every primary cell must contain 30,000 paired trajectories")
    if len({int(row["seed"]) for row in primary}) != 36:
        raise ValueError("primary grid seeds must be unique across 36 cells")

    for row in primary:
        effect = float(row["mean_difference"])
        half_width = float(row["half_width"])
        ci_low = float(row["ci_low"])
        ci_high = float(row["ci_high"])
        _assert_close(
            float(row["simultaneous_multiplier"]),
            SIMULTANEOUS_MULTIPLIER,
            1e-12,
            f"unexpected simultaneous multiplier in {row['cell_id']}",
        )
        _assert_close(
            effect,
            float(row["normalized_correlated_mean"]) - float(row["normalized_proxy_mean"]),
            2e-15,
            f"normalized effect identity failed in {row['cell_id']}",
        )
        _assert_close(ci_low, effect - half_width, 2e-15, f"CI lower identity failed in {row['cell_id']}")
        _assert_close(ci_high, effect + half_width, 2e-15, f"CI upper identity failed in {row['cell_id']}")
        if half_width > 0.02:
            raise ValueError(f"primary precision gate failed in {row['cell_id']}")
        if not (ci_low > 0.0 and row["point_sign"] == "positive" and row["resolved_sign"] == "positive"):
            raise ValueError(f"primary sign gate failed in {row['cell_id']}")
    primary_meta = metadata["primary"]
    if not (
        primary_meta.get("all_gates_pass") is True
        and primary_meta.get("deterministic_gates_pass") is True
        and primary_meta.get("precision_gates_pass") is True
        and primary_meta.get("row_counts", {}).get("primary_effects") == 36
    ):
        raise ValueError("primary metadata gates are not all PASS")
    if primary_meta.get("proxy_semantics") != "independent exact edge-block marginals; not routed traffic":
        raise ValueError("unexpected independent-proxy semantics in primary metadata")

    if len(anchors) != 3 or {row["topology"] for row in anchors} != set(TOPOLOGY_ORDER):
        raise ValueError("exact-anchor table must contain one row for each frozen topology")
    for row in anchors:
        if int(row["scale"]) != 2 or int(row["state_count"]) != 10000:
            raise ValueError(f"unexpected exact-anchor design in {row['topology']}")
        if int(row["repetitions"]) != 100000:
            raise ValueError(f"unexpected exact-anchor Monte Carlo count in {row['topology']}")
        if abs(float(row["z_score"])) > EXACT_Z_GATE:
            raise ValueError(f"exact-anchor z gate failed in {row['topology']}")
        if float(row["max_abs_residual"]) > 1e-12:
            raise ValueError(f"exact-anchor residual gate failed in {row['topology']}")
        if not (_as_bool(row["all_states_reach_boundary"]) and _as_bool(row["gate_pass"])):
            raise ValueError(f"exact-anchor reachability gate failed in {row['topology']}")
    if metadata["anchors"].get("all_gates_pass") is not True or metadata["anchors"].get("row_count") != 3:
        raise ValueError("exact-anchor metadata gates are not all PASS")

    if len(weakest) != 1:
        raise ValueError(f"weakest-cell sensitivity table must contain one row, received {len(weakest)}")
    weak = weakest[0]
    frozen_weak_design = {
        "cell_id": "star-balanced-N80",
        "topology": "star",
        "regime": "balanced",
        "scale": 80,
        "seed": 202607189999,
        "repetitions": 100000,
        "blocks": 100,
        "block_size": 1000,
    }
    for field, expected in frozen_weak_design.items():
        actual: Any = weak[field]
        if isinstance(expected, int):
            actual = int(actual)
        if actual != expected:
            raise ValueError(f"weakest-cell frozen design mismatch for {field}: {actual!r} != {expected!r}")
    lower_bounds = [
        float(weak["normal_ci_low"]),
        float(weak["path_t_ci_low"]),
        float(weak["block_t_ci_low"]),
    ]
    if not all(bound > 0.0 for bound in lower_bounds):
        raise ValueError("weakest-cell different-seed interval sign gate failed")
    weak_meta = metadata["weakest"]
    if not (weak_meta.get("all_gates_pass") is True and weak_meta.get("intervals_all_positive") is True):
        raise ValueError("weakest-cell metadata gates are not all PASS")

    return {
        "paths": normalized_paths,
        "manifests": manifests,
        "primary": primary,
        "anchors": anchors,
        "weakest": weakest,
        "metadata": metadata,
    }


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def build_input_audit(paths: Mapping[str, Path], loaded: Mapping[str, Any]) -> dict[str, Any]:
    root = Path(__file__).resolve().parent
    primary = loaded["primary"]
    anchors = loaded["anchors"]
    weak = loaded["weakest"][0]
    min_row = min(primary, key=lambda row: float(row["mean_difference"]))
    topology_summaries: dict[str, Any] = {}
    for topology in TOPOLOGY_ORDER:
        values = [float(row["mean_difference"]) for row in primary if row["topology"] == topology]
        topology_summaries[topology] = {
            "minimum": min(values),
            "maximum": max(values),
            "mean": float(math.fsum(values) / len(values)),
        }
    sources = {
        name: {
            "path": _relative(Path(path), root),
            "sha256": sha256_file(Path(path)),
        }
        for name, path in sorted(paths.items())
    }
    return {
        "contract_status": "PASS",
        "contract_date": "2026-07-28",
        "figure_scope": "accepted T18 higher-order cross-topology evidence only; no experiment rerun",
        "provenance": {
            "source_files": sources,
            "rejected_seed_inputs_used": False,
            "same_seed_full_recalculation_used_as_independent_replication": False,
            "different_seed_evidence_scope": "weakest cell star-balanced-N80 only",
            "plotting_script_sha256": sha256_file(Path(__file__).resolve()),
        },
        "primary_grid": {
            "row_count": len(primary),
            "topologies": sorted({row["topology"] for row in primary}),
            "regimes": sorted({row["regime"] for row in primary}),
            "scales": sorted({int(row["scale"]) for row in primary}),
            "repetitions": sorted({int(row["repetitions"]) for row in primary}),
            "paired_trajectory_count": sum(int(row["repetitions"]) for row in primary),
            "simultaneous_multiplier": SIMULTANEOUS_MULTIPLIER,
            "positive_simultaneous_intervals": sum(float(row["ci_low"]) > 0.0 for row in primary),
            "maximum_half_width": max(float(row["half_width"]) for row in primary),
            "weakest_point_estimate": {
                "cell_id": min_row["cell_id"],
                "estimate": float(min_row["mean_difference"]),
                "ci_low": float(min_row["ci_low"]),
                "ci_high": float(min_row["ci_high"]),
            },
            "topology_effect_summaries": topology_summaries,
        },
        "exact_anchors": {
            "row_count": len(anchors),
            "scale": 2,
            "state_counts": sorted({int(row["state_count"]) for row in anchors}),
            "repetitions": sorted({int(row["repetitions"]) for row in anchors}),
            "maximum_absolute_z_score": max(abs(float(row["z_score"])) for row in anchors),
            "maximum_absolute_linear_system_residual": max(float(row["max_abs_residual"]) for row in anchors),
            "all_states_reach_boundary": all(_as_bool(row["all_states_reach_boundary"]) for row in anchors),
        },
        "weakest_cell_sensitivity": {
            "row_count": 1,
            "cell_id": weak["cell_id"],
            "seed": int(weak["seed"]),
            "repetitions": int(weak["repetitions"]),
            "blocks": int(weak["blocks"]),
            "block_size": int(weak["block_size"]),
            "estimate": float(weak["mean_difference"]),
            "intervals": {
                "normal": [float(weak["normal_ci_low"]), float(weak["normal_ci_high"])],
                "path_student_t": [float(weak["path_t_ci_low"]), float(weak["path_t_ci_high"])],
                "block_student_t": [float(weak["block_t_ci_low"]), float(weak["block_t_ci_high"])],
            },
            "all_interval_lower_bounds_positive": all(
                float(weak[name]) > 0.0
                for name in ("normal_ci_low", "path_t_ci_low", "block_t_ci_low")
            ),
        },
        "figure_export": {
            "backend": "Python/matplotlib",
            "formats": ["PNG"],
            "width_mm": FIGURE_WIDTH_MM,
            "height_mm": FIGURE_HEIGHT_MM,
            "dpi": FIGURE_DPI,
            "white_background": True,
            "black_and_white_discrimination": "regime encoded redundantly by marker and line style",
        },
    }


def _configure_matplotlib() -> str:
    installed = {entry.name for entry in font_manager.fontManager.ttflist}
    candidates = ("Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC")
    font = next((candidate for candidate in candidates if candidate in installed), None)
    if font is None:
        raise RuntimeError("no supported Chinese font is installed (Microsoft YaHei/SimHei/Noto Sans CJK SC)")
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [font, "Arial", "DejaVu Sans"],
            "mathtext.fontset": "dejavusans",
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "axes.unicode_minus": False,
            "font.size": 6.2,
            "axes.titlesize": 6.5,
            "axes.labelsize": 6.2,
            "xtick.labelsize": 5.7,
            "ytick.labelsize": 5.7,
            "axes.linewidth": 0.65,
            "lines.linewidth": 0.9,
            "legend.fontsize": 5.5,
            "legend.frameon": False,
            "xtick.major.width": 0.55,
            "ytick.major.width": 0.55,
            "xtick.major.size": 2.3,
            "ytick.major.size": 2.3,
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )
    return font


def _panel_label(axis: mpl.axes.Axes, label: str, x: float = -0.045, y: float = 1.055) -> None:
    axis.text(x, y, label, transform=axis.transAxes, fontsize=8.0, fontweight="bold", va="bottom")


def _draw_node(axis: mpl.axes.Axes, xy: tuple[float, float], radius: float = 0.026) -> None:
    axis.add_patch(Circle(xy, radius, facecolor="white", edgecolor="#1f1f1f", linewidth=0.55, zorder=5))


def _draw_mechanism_panel(axis: mpl.axes.Axes) -> None:
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    _panel_label(axis, "a", x=-0.02, y=0.94)
    axis.plot([0.5, 0.5], [0.08, 0.92], color="#b8b8b8", linewidth=0.6, linestyle=(0, (2, 2)))

    # Atomic route: two triads share a node and are updated by one route draw.
    left_positions = {"s": (0.055, 0.33), "u": (0.17, 0.76), "h": (0.245, 0.38), "v": (0.34, 0.76), "t": (0.46, 0.33)}
    axis.add_patch(
        Polygon([left_positions[k] for k in ("s", "u", "h")], closed=True, facecolor="#d9e2ec", edgecolor="#355c7d", linewidth=0.8)
    )
    axis.add_patch(
        Polygon([left_positions[k] for k in ("h", "v", "t")], closed=True, facecolor="#f1dfcf", edgecolor="#955f35", linewidth=0.8, linestyle="--")
    )
    for point in left_positions.values():
        _draw_node(axis, point)
    for start, end in ((left_positions["s"], left_positions["h"]), (left_positions["h"], left_positions["t"])):
        axis.add_patch(
            FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=6, color="#111111", linewidth=1.0, shrinkA=5, shrinkB=5, zorder=6)
        )
    axis.text(0.25, 0.93, "相关原子路由", ha="center", va="top", fontweight="bold")
    axis.text(0.25, 0.12, "一次路由抽样 → 两个超边块同步更新", ha="center", va="center", fontsize=5.5)
    axis.text(0.135, 0.57, "$e_1$", color="#355c7d", fontweight="bold")
    axis.text(0.37, 0.57, "$e_2$", color="#7b4c27", fontweight="bold")

    # Independent exact edge-block marginals: one sample per edge block.
    box_style = {"facecolor": "#f7f7f7", "edgecolor": "#333333", "linewidth": 0.7}
    axis.add_patch(Rectangle((0.55, 0.44), 0.15, 0.23, **box_style))
    axis.add_patch(Rectangle((0.80, 0.44), 0.15, 0.23, **box_style))
    axis.text(0.625, 0.555, "$A^{(1)}$", ha="center", va="center", fontsize=7.2)
    axis.text(0.875, 0.555, "$A^{(2)}$", ha="center", va="center", fontsize=7.2)
    axis.text(0.75, 0.555, r"$\perp$", ha="center", va="center", fontsize=8.0)
    axis.text(0.75, 0.93, "独立超边边际代理", ha="center", va="top", fontweight="bold")
    axis.text(0.75, 0.30, "分别抽取逐超边一步边际", ha="center", va="center", fontsize=5.5)
    axis.text(0.75, 0.12, "不构成可执行的端到端路由", ha="center", va="center", fontsize=5.5, fontweight="bold")


TOPOLOGY_EDGES = {
    "chain": ((0, 1, 2), (2, 3, 4), (4, 5, 6), (6, 7, 8)),
    "star": ((0, 1, 2), (0, 3, 4), (0, 5, 6), (0, 7, 8)),
    "random": ((0, 1, 2), (2, 3, 4), (3, 5, 6), (4, 7, 8)),
}


TOPOLOGY_POSITIONS = {
    "chain": {
        0: (0.03, 0.30), 1: (0.10, 0.76), 2: (0.25, 0.40),
        3: (0.35, 0.77), 4: (0.48, 0.38), 5: (0.59, 0.76),
        6: (0.72, 0.40), 7: (0.84, 0.76), 8: (0.96, 0.30),
    },
    "star": {
        0: (0.50, 0.50), 1: (0.18, 0.82), 2: (0.34, 0.88),
        3: (0.67, 0.88), 4: (0.83, 0.82), 5: (0.82, 0.18),
        6: (0.66, 0.12), 7: (0.34, 0.12), 8: (0.18, 0.18),
    },
    "random": {
        0: (0.03, 0.60), 1: (0.16, 0.88), 2: (0.27, 0.55),
        3: (0.48, 0.73), 4: (0.51, 0.30), 5: (0.67, 0.96),
        6: (0.76, 0.72), 7: (0.76, 0.32), 8: (0.91, 0.16),
    },
}


def _draw_hypergraph(axis: mpl.axes.Axes, topology: str, title: str, degrees: str) -> None:
    axis.set_xlim(-0.03, 1.03)
    axis.set_ylim(-0.08, 1.06)
    axis.axis("off")
    fills = ("#dfe7ee", "#efdfd1", "#e3e3e3", "#e8dfeb")
    edges = TOPOLOGY_EDGES[topology]
    positions = TOPOLOGY_POSITIONS[topology]
    for index, edge in enumerate(edges):
        axis.add_patch(
            Polygon(
                [positions[node] for node in edge],
                closed=True,
                facecolor=fills[index],
                edgecolor="#3b3b3b",
                linewidth=0.55,
                linestyle=("-", "--", "-.", ":")[index],
                zorder=1,
            )
        )
    for position in positions.values():
        _draw_node(axis, position, radius=0.035)
    axis.text(0.5, 1.05, title, ha="center", va="bottom", fontsize=5.7, fontweight="bold")
    axis.text(0.5, -0.06, f"交度 {degrees}", ha="center", va="top", fontsize=5.0, color="#333333")


def _draw_topology_panel(axis: mpl.axes.Axes) -> None:
    axis.axis("off")
    _panel_label(axis, "b", x=-0.02, y=0.94)
    axis.text(
        0.5,
        0.98,
        "四条三元超边的非同构拓扑",
        transform=axis.transAxes,
        ha="center",
        va="top",
        fontweight="bold",
        fontsize=6.5,
    )
    items = (
        ("chain", "链式重叠", "[1,1,2,2]"),
        ("star", "共枢纽星形", "[3,3,3,3]"),
        ("random", "固定随机分支", "[1,1,1,3]"),
    )
    for index, item in enumerate(items):
        inset = axis.inset_axes([index / 3 + 0.015, 0.03, 0.30, 0.70])
        _draw_hypergraph(inset, *item)


def _primary_by_cell(rows: Iterable[Mapping[str, str]]) -> dict[tuple[str, str], list[Mapping[str, str]]]:
    grouped: dict[tuple[str, str], list[Mapping[str, str]]] = {}
    for row in rows:
        grouped.setdefault((row["topology"], row["regime"]), []).append(row)
    for key in grouped:
        grouped[key] = sorted(grouped[key], key=lambda row: int(row["scale"]))
    return grouped


def _draw_primary_panel(spec: mpl.gridspec.SubplotSpec, rows: list[Mapping[str, str]]) -> list[mpl.axes.Axes]:
    nested = spec.subgridspec(1, 3, wspace=0.16)
    axes: list[mpl.axes.Axes] = []
    grouped = _primary_by_cell(rows)
    styles = {
        "balanced": {"label": "平衡", "color": "#111111", "marker": "o", "linestyle": "-"},
        "positive": {"label": "+0.01/N", "color": "#3f6f8f", "marker": "s", "linestyle": "--"},
        "negative": {"label": "−0.01/N", "color": "#9a6233", "marker": "^", "linestyle": ":"},
    }
    title_labels = {"chain": "链式重叠", "star": "共枢纽星形", "random": "固定随机分支"}
    for topology_index, topology in enumerate(TOPOLOGY_ORDER):
        axis = plt.subplot(nested[0, topology_index], sharey=axes[0] if axes else None)
        axes.append(axis)
        axis.axhline(0.0, color="#777777", linewidth=0.55, linestyle=(0, (2, 2)), zorder=0)
        for regime in REGIME_ORDER:
            cell_rows = grouped[(topology, regime)]
            x = np.asarray([int(row["scale"]) for row in cell_rows], dtype=float)
            y = np.asarray([float(row["mean_difference"]) for row in cell_rows], dtype=float)
            error = np.asarray([float(row["half_width"]) for row in cell_rows], dtype=float)
            if np.any(x <= 0):
                raise ValueError("logarithmic capacity axis requires strictly positive scales")
            style = styles[regime]
            axis.errorbar(
                x,
                y,
                yerr=error,
                color=style["color"],
                marker=style["marker"],
                linestyle=style["linestyle"],
                markersize=3.0,
                markerfacecolor="white" if regime != "balanced" else style["color"],
                markeredgewidth=0.75,
                capsize=1.6,
                elinewidth=0.7,
                label=style["label"],
                zorder=3,
            )
        topology_values = [float(row["mean_difference"]) for row in rows if row["topology"] == topology]
        axis.set_title(f"{title_labels[topology]}\n均值 {np.mean(topology_values):.4f}", pad=2.5)
        axis.set_xscale("log", base=2)
        axis.set_xticks(SCALE_GRID)
        axis.set_xticklabels([str(value) for value in SCALE_GRID])
        axis.set_xlim(8.6, 92)
        axis.set_ylim(-0.004, 0.132)
        axis.grid(axis="y", color="#e4e4e4", linewidth=0.45)
        axis.set_xlabel("容量尺度 $N$", labelpad=1.5)
        axis.spines[["top", "right"]].set_visible(False)
        if topology_index == 0:
            axis.set_ylabel(r"归一化停止时间效应 $\widehat{\Delta}_N$")
            _panel_label(axis, "c", x=-0.27, y=1.15)
        else:
            axis.tick_params(labelleft=False)
    handles, labels = axes[0].get_legend_handles_labels()
    axes[1].legend(handles, labels, loc="lower center", bbox_to_anchor=(0.5, 1.24), ncol=3, handlelength=2.4, columnspacing=1.5)
    axes[2].text(
        0.98,
        0.96,
        "36/36 同时区间下界 > 0",
        transform=axes[2].transAxes,
        ha="right",
        va="top",
        fontsize=5.4,
        fontweight="bold",
    )
    return axes


def _draw_exact_anchor_axis(axis: mpl.axes.Axes, rows: list[Mapping[str, str]]) -> None:
    labels = {"chain": "链式", "star": "星形", "random": "随机分支"}
    ordered = sorted(rows, key=lambda row: TOPOLOGY_ORDER.index(row["topology"]))
    x = np.arange(len(ordered))
    z = np.asarray([float(row["z_score"]) for row in ordered])
    axis.axhspan(-EXACT_Z_GATE, EXACT_Z_GATE, color="#eeeeee", zorder=0)
    axis.axhline(0.0, color="#3a3a3a", linewidth=0.65)
    axis.axhline(EXACT_Z_GATE, color="#777777", linewidth=0.55, linestyle="--")
    axis.axhline(-EXACT_Z_GATE, color="#777777", linewidth=0.55, linestyle="--")
    axis.scatter(x, z, s=18, marker="D", facecolor="#3f6f8f", edgecolor="#222222", linewidth=0.45, zorder=3)
    for index, value in enumerate(z):
        offset = 0.20 if value >= 0 else -0.22
        axis.text(index, value + offset, f"{value:.2f}", ha="center", va="bottom" if value >= 0 else "top", fontsize=5.2)
    axis.set_xticks(x, [labels[row["topology"]] for row in ordered])
    axis.set_ylim(-3.65, 3.65)
    axis.set_yticks([-3.29, 0, 3.29])
    axis.set_ylabel("Monte Carlo 标准化偏差 $z$")
    axis.set_title("精确锚点（$N=2$；每拓扑 10,000 状态）", pad=2.5)
    axis.spines[["top", "right"]].set_visible(False)
    _panel_label(axis, "d", x=-0.14, y=1.11)


def _draw_weakest_axis(axis: mpl.axes.Axes, primary: list[Mapping[str, str]], weak: Mapping[str, str]) -> None:
    source = next(row for row in primary if row["cell_id"] == "star-balanced-N80")
    estimate_primary = float(source["mean_difference"])
    estimate_weak = float(weak["mean_difference"])
    items = (
        ("主网格：36 重同时区间", estimate_primary, float(source["ci_low"]), float(source["ci_high"]), "o", "#111111"),
        ("异种子：正态区间", estimate_weak, float(weak["normal_ci_low"]), float(weak["normal_ci_high"]), "s", "#3f6f8f"),
        ("异种子：轨迹 $t$ 区间", estimate_weak, float(weak["path_t_ci_low"]), float(weak["path_t_ci_high"]), "^", "#6e6e6e"),
        ("异种子：区块 $t$ 区间", estimate_weak, float(weak["block_t_ci_low"]), float(weak["block_t_ci_high"]), "D", "#9a6233"),
    )
    y = np.arange(len(items))[::-1]
    axis.axvline(0.0, color="#555555", linewidth=0.65, linestyle=(0, (2, 2)))
    for position, (label, estimate, lower, upper, marker, color) in zip(y, items):
        axis.errorbar(
            estimate,
            position,
            xerr=np.asarray([[estimate - lower], [upper - estimate]]),
            fmt=marker,
            color=color,
            markerfacecolor="white" if marker != "o" else color,
            markeredgecolor=color,
            markeredgewidth=0.75,
            markersize=3.6,
            capsize=2.0,
            elinewidth=0.85,
            zorder=3,
        )
    axis.set_yticks(y, [item[0] for item in items])
    axis.set_xlim(-0.002, 0.034)
    axis.set_xticks([0.0, 0.01, 0.02, 0.03])
    axis.set_xlabel(r"$\widehat{\Delta}_{80}$", labelpad=0.0)
    axis.set_title("最弱单元：星形–平衡–$N=80$", pad=2.5)
    axis.grid(axis="x", color="#e4e4e4", linewidth=0.45)
    axis.spines[["top", "right", "left"]].set_visible(False)
    axis.tick_params(axis="y", length=0, pad=1.5)


def render_figure(loaded: Mapping[str, Any], output_path: Path) -> str:
    font = _configure_matplotlib()
    width = FIGURE_WIDTH_MM / 25.4
    height = FIGURE_HEIGHT_MM / 25.4
    figure = plt.figure(figsize=(width, height))
    outer = figure.add_gridspec(
        3,
        1,
        height_ratios=(1.12, 1.85, 1.26),
        left=0.075,
        right=0.985,
        top=0.965,
        bottom=0.150,
        hspace=0.51,
    )
    top = outer[0].subgridspec(1, 2, width_ratios=(1.05, 0.95), wspace=0.13)
    mechanism_axis = figure.add_subplot(top[0, 0])
    topology_axis = figure.add_subplot(top[0, 1])
    _draw_mechanism_panel(mechanism_axis)
    _draw_topology_panel(topology_axis)
    _draw_primary_panel(outer[1], loaded["primary"])

    bottom = outer[2].subgridspec(1, 2, width_ratios=(0.78, 1.22), wspace=0.43)
    anchor_axis = figure.add_subplot(bottom[0, 0])
    weakest_axis = figure.add_subplot(bottom[0, 1])
    _draw_exact_anchor_axis(anchor_axis, loaded["anchors"])
    _draw_weakest_axis(weakest_axis, loaded["primary"], loaded["weakest"][0])

    figure.text(
        0.075,
        0.064,
        "主网格：每单元 30,000 对配对轨迹；误差线为 36 重 Bonferroni 同时 95% 区间（临界值 3.19695）；最弱单元异种子敏感性为 100,000 对。",
        ha="left",
        va="bottom",
        fontsize=5.15,
    )
    figure.text(
        0.075,
        0.036,
        "注：独立代理仅保持逐超边一步边际，不代表可执行的端到端路由；同种子完整复算仅属计算复现，异种子证据仅覆盖最弱单元。",
        ha="left",
        va="bottom",
        fontsize=5.15,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        output_path,
        dpi=FIGURE_DPI,
        facecolor="white",
        edgecolor="none",
        metadata={
            "Title": "高阶超图跨拓扑验证",
            "Author": "",
            "Description": "Frozen T18 cross-topology evidence; accepted inputs only.",
            "Software": f"Python/matplotlib; Chinese font={font}",
        },
    )
    plt.close(figure)
    return font


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_output_manifest(path: Path, outputs: Iterable[Path]) -> None:
    lines = [f"{sha256_file(output)}  {output.name}" for output in outputs]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "outputs" / "researchwrite" / "hypergraph-stopping-time" / "figures",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = default_input_paths(args.project_root)
    loaded = validate_and_load_inputs(paths)
    audit = build_input_audit(paths, loaded)

    output_dir = args.output_dir.resolve()
    png_path = output_dir / "fig_higher_order_cross_topology_validation.png"
    audit_path = output_dir / "fig_higher_order_cross_topology_input_audit.json"
    manifest_path = output_dir / "fig_higher_order_cross_topology_SHA256SUMS.txt"
    audit["figure_export"]["font"] = render_figure(loaded, png_path)
    audit["figure_export"]["output_path"] = _relative(png_path, args.project_root.resolve())
    audit["figure_export"]["pixel_dimensions"] = list(plt.imread(png_path).shape[1::-1])
    _write_json(audit_path, audit)
    _write_output_manifest(manifest_path, (png_path, audit_path))

    print(json.dumps({
        "status": "PASS",
        "png": str(png_path),
        "audit": str(audit_path),
        "manifest": str(manifest_path),
        "positive_simultaneous_intervals": audit["primary_grid"]["positive_simultaneous_intervals"],
        "rejected_seed_inputs_used": False,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
