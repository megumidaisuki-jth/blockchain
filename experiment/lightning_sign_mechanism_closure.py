"""Close the finite-grid Lightning sign-mechanism evidence chain.

This script consumes the frozen formal and independent-replication block
artifacts. It performs no new Monte Carlo simulation and never overwrites its
inputs. Its claim is intentionally limited to the eight frozen topology
anchors and the synthetic demand interpolation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import platform
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy
from scipy.stats import t as student_t


WEIGHTS = (0.0, 0.25, 0.5, 0.75, 1.0)
MODES = ("primary", "hub")
BLOCK_COUNT = 40
ANCHOR_COUNT = 8
DATE_COUNT = 4
STAGES = ("formal", "replication")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_manifest(root: Path) -> int:
    manifest = root / "SHA256SUMS.txt"
    if not manifest.is_file():
        raise ValueError(f"missing input manifest: {manifest}")
    count = 0
    for line_number, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            raise ValueError(f"malformed manifest line {line_number}: {manifest}")
        expected, relative = parts
        target = root / relative
        if not target.is_file() or sha256(target) != expected:
            raise ValueError(f"input manifest mismatch: {target}")
        count += 1
    return count


def linear_slope_weights() -> np.ndarray:
    x = np.asarray(WEIGHTS, dtype=float)
    return (x - x.mean()) / np.sum((x - x.mean()) ** 2)


def t_summary(values: np.ndarray, *, comparisons: int) -> dict[str, float | int]:
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or len(values) < 2 or not np.all(np.isfinite(values)):
        raise ValueError("values must be a finite vector of length at least two")
    if type(comparisons) is not int or comparisons < 1:
        raise ValueError("comparisons must be a positive integer")
    mean = float(values.mean())
    standard_error = float(values.std(ddof=1) / math.sqrt(len(values)))
    critical = float(student_t.ppf(1.0 - 0.05 / (2 * comparisons), len(values) - 1))
    halfwidth = critical * standard_error
    return {
        "n_blocks": int(len(values)),
        "mean": mean,
        "standard_error": standard_error,
        "simultaneous_critical": critical,
        "ci_low": mean - halfwidth,
        "ci_high": mean + halfwidth,
        "ci_halfwidth": halfwidth,
    }


def exact_sign_flip_pvalue(values: np.ndarray) -> float:
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not 1 <= len(values) <= 20 or not np.all(np.isfinite(values)):
        raise ValueError("values must be a finite vector with length 1 to 20")
    observed = abs(float(values.mean()))
    exceedances = sum(
        abs(float(np.mean(values * np.asarray(signs)))) >= observed - 1e-15
        for signs in itertools.product((-1.0, 1.0), repeat=len(values))
    )
    return exceedances / (2 ** len(values))


def _load_stage(root: Path, stage: str) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, object]]:
    if stage not in STAGES:
        raise ValueError("unknown stage")
    manifest_entries = verify_manifest(root)
    prefix = f"drift-interpolation-{stage}"
    cells = pd.read_csv(root / f"{prefix}.csv")
    blocks = pd.read_csv(root / f"{prefix}-blocks.csv")
    metadata = json.loads((root / f"{prefix}-metadata.json").read_text(encoding="utf-8"))

    if len(cells) != ANCHOR_COUNT * len(WEIGHTS) or len(blocks) != len(cells) * BLOCK_COUNT:
        raise ValueError(f"incomplete {stage} grid")
    if cells["seed"].nunique() != len(cells) or int(cells["censored_count"].sum()) != 0:
        raise ValueError(f"invalid {stage} seed or censoring audit")
    if set(cells["hotspot_weight"].astype(float)) != set(WEIGHTS):
        raise ValueError(f"incomplete {stage} weight grid")
    if set(cells["mode"]) != set(MODES) or cells["date"].nunique() != DATE_COUNT:
        raise ValueError(f"incomplete {stage} topology anchors")

    expected_blocks = list(range(BLOCK_COUNT))
    for cell_id, frame in blocks.groupby("cell_id", sort=False):
        if sorted(frame["block_index"].astype(int).tolist()) != expected_blocks:
            raise ValueError(f"noncontiguous blocks: {cell_id}")
    merged = blocks.merge(
        cells[["cell_id", "date", "mode", "hotspot_weight", "seed", "increment_sha256", "maximum_absolute_drift"]],
        on="cell_id",
        validate="many_to_one",
    )
    for (date, mode), frame in cells.groupby(["date", "mode"], sort=False):
        ordered = frame.sort_values("hotspot_weight")
        if len(ordered) != len(WEIGHTS) or ordered["increment_sha256"].nunique() != 1:
            raise ValueError(f"increment support changed: {date}-{mode}")
        weights = ordered["hotspot_weight"].to_numpy(float)
        drifts = ordered["maximum_absolute_drift"].to_numpy(float)
        if abs(drifts[0]) > 1e-12:
            raise ValueError(f"zero-weight drift is not numerically zero: {date}-{mode}")
        if np.max(np.abs(drifts - weights * drifts[-1])) > 2e-15:
            raise ValueError(f"maximum drift is not affine: {date}-{mode}")
    return cells, merged, {"manifest_entries": manifest_entries, **metadata}


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def _summarize_grouped(frame: pd.DataFrame, keys: list[str], value: str, comparisons: int) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    grouper: str | list[str] = keys[0] if len(keys) == 1 else keys
    for group_key, group in frame.groupby(grouper, sort=True):
        key_values = (group_key,) if len(keys) == 1 else tuple(group_key)
        row = dict(zip(keys, key_values))
        row.update(t_summary(group[value].to_numpy(float), comparisons=comparisons))
        rows.append(row)
    return pd.DataFrame(rows)


def _plot(curve: pd.DataFrame, anchors: pd.DataFrame, dates: pd.DataFrame, output: Path) -> None:
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"],
            "font.size": 7,
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "axes.unicode_minus": False,
            "axes.spines.right": False,
            "axes.spines.top": False,
            "axes.linewidth": 0.8,
            "legend.frameon": False,
        }
    )
    blue, orange, grey = "#4C78A8", "#E07B39", "#777777"
    fig, axes = plt.subplots(1, 3, figsize=(7.2047, 2.9921), constrained_layout=True)

    ax = axes[0]
    ax.errorbar(
        curve["hotspot_weight"], curve["mean"], yerr=curve["ci_halfwidth"],
        color=blue, marker="o", markersize=3.5, capsize=2.5, linewidth=1.2,
    )
    ax.axhline(0.0, color="black", linewidth=0.7)
    ax.fill_between([0.0, 0.25], ax.get_ylim()[0], ax.get_ylim()[1], color=grey, alpha=0.05)
    ax.set_xlabel("热点需求权重 λ")
    ax.set_ylabel("平均标准化停止时间效应")
    ax.set_title("a  平均效应发生符号转折", loc="left", fontweight="bold")
    ax.text(0.03, 0.04, "五重同时 95% 区间\n8锚点 × 2独立阶段", transform=ax.transAxes, va="bottom", fontsize=6)

    ax = axes[1]
    anchor_plot = anchors.assign(mode_order=anchors["mode"].map({"primary": 0, "hub": 1})).sort_values(["date", "mode_order"]).reset_index(drop=True)
    y = np.arange(len(anchor_plot))
    labels = [f"{date[:4]} {'主锚' if mode == 'primary' else '枢纽'}" for date, mode in zip(anchor_plot.date, anchor_plot["mode"])]
    colors = np.where(anchor_plot["mean"] < 0, blue, orange)
    for index, row in anchor_plot.iterrows():
        ax.errorbar(row["mean"], index, xerr=row["ci_halfwidth"], fmt="o", color=colors[index], markersize=3, capsize=2)
    ax.axvline(0.0, color="black", linewidth=0.7)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlabel("效应斜率 / 单位 λ\n八重同时95%区间")
    ax.set_title("b  八锚点方向与异质性", loc="left", fontweight="bold")

    ax = axes[2]
    date_plot = dates.sort_values("date").reset_index(drop=True)
    y = np.arange(len(date_plot))
    ax.errorbar(date_plot["mean"], y, xerr=date_plot["ci_halfwidth"], fmt="o", color=blue, markersize=3.5, capsize=2.5)
    ax.axvline(0.0, color="black", linewidth=0.7)
    ax.set_yticks(y, date_plot["date"].str[:4])
    ax.invert_yaxis()
    pvalue = exact_sign_flip_pvalue(date_plot["mean"].to_numpy(float))
    ax.set_xlabel(f"日期聚类平均斜率\n四重同时95%区间；精确符号翻转 p={pvalue:.3f}")
    ax.set_title("c  四日期保守聚类", loc="left", fontweight="bold")

    fig.savefig(output, dpi=600, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def _write_manifest(output: Path) -> None:
    artifacts = sorted(path for path in output.iterdir() if path.name != "SHA256SUMS.txt")
    (output / "SHA256SUMS.txt").write_text(
        "".join(f"{sha256(path)}  {path.name}\n" for path in artifacts), encoding="utf-8"
    )


def refresh_published_figure(output: Path, formal_dir: Path, replication_dir: Path) -> None:
    """Refresh disclosures, re-render the PNG, and update the manifest."""
    output = Path(output)
    formal_dir, replication_dir = Path(formal_dir), Path(replication_dir)
    formal_metadata = json.loads(
        (formal_dir / "drift-interpolation-formal-metadata.json").read_text(encoding="utf-8")
    )
    replication_metadata = json.loads(
        (replication_dir / "drift-interpolation-replication-metadata.json").read_text(encoding="utf-8")
    )
    metadata_path = output / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["original_formal_slope_precision_gate_pass"] = bool(formal_metadata["slope_precision_gate_pass"])
    metadata["original_replication_slope_precision_gate_pass"] = bool(replication_metadata["slope_precision_gate_pass"])
    disclosures = [
        "the original replication precision gate failed for the 2026-primary anchor (maximum half-width exceeded 0.03); pooling does not erase that failure",
        "the five-point mean curve is not strictly monotone between lambda=0.75 and lambda=1",
    ]
    limitations = list(metadata["limitations"])
    for disclosure in disclosures:
        if disclosure not in limitations:
            limitations.append(disclosure)
    metadata["limitations"] = limitations
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    design_path = output / "sign-mechanism-design-audit.csv"
    design = pd.read_csv(design_path)
    for stage, stage_metadata in (("formal", formal_metadata), ("replication", replication_metadata)):
        mask = design["stage"] == stage
        design.loc[mask, "original_slope_precision_gate_pass"] = bool(stage_metadata["slope_precision_gate_pass"])
        design.loc[mask, "original_maximum_slope_ci_halfwidth"] = float(stage_metadata["maximum_anchor_slope_ci_halfwidth"])
    _write_csv(design_path, design)

    curve = pd.read_csv(output / "sign-mechanism-curve.csv")
    anchors = pd.read_csv(output / "sign-mechanism-anchor-slopes.csv")
    dates = pd.read_csv(output / "sign-mechanism-date-clusters.csv")
    _plot(curve, anchors, dates, output / "sign-mechanism-closure.png")
    _write_manifest(output)


def run(formal_dir: Path, replication_dir: Path, output: Path) -> dict[str, object]:
    formal_dir, replication_dir, output = Path(formal_dir), Path(replication_dir), Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)

    stage_data: list[pd.DataFrame] = []
    design_rows: list[dict[str, object]] = []
    cell_frames: list[pd.DataFrame] = []
    seed_sets: dict[str, set[int]] = {}
    stage_audits: dict[str, dict[str, object]] = {}
    for stage, root in (("formal", formal_dir), ("replication", replication_dir)):
        cells, blocks, audit = _load_stage(root, stage)
        blocks["stage"] = stage
        cells["stage"] = stage
        stage_data.append(blocks)
        cell_frames.append(cells)
        seed_sets[stage] = set(cells["seed"].astype(int))
        stage_audits[stage] = audit
        design_rows.append(
            {
                "stage": stage,
                "manifest_entries": audit["manifest_entries"],
                "cell_count": len(cells),
                "block_row_count": len(blocks),
                "unique_seed_count": cells["seed"].nunique(),
                "censored_count": int(cells["censored_count"].sum()),
                "maximum_affine_drift_residual": float(audit["maximum_affine_drift_residual"]),
                "original_slope_precision_gate_pass": bool(audit["slope_precision_gate_pass"]),
                "original_maximum_slope_ci_halfwidth": float(audit["maximum_anchor_slope_ci_halfwidth"]),
            }
        )
    if not seed_sets["formal"].isdisjoint(seed_sets["replication"]):
        raise ValueError("formal and replication seed sets overlap")

    blocks = pd.concat(stage_data, ignore_index=True)
    cells = pd.concat(cell_frames, ignore_index=True)
    pivot = blocks.pivot_table(
        index=["stage", "date", "mode", "block_index"],
        columns="hotspot_weight", values="normalized_mean_difference", aggfunc="first",
    ).reset_index()
    if len(pivot) != len(STAGES) * ANCHOR_COUNT * BLOCK_COUNT or pivot[list(WEIGHTS)].isna().any().any():
        raise ValueError("block-level interpolation matrix is incomplete")
    slope_weights = linear_slope_weights()
    pivot["slope"] = pivot[list(WEIGHTS)].to_numpy(float) @ slope_weights
    pivot["endpoint_contrast"] = pivot[1.0] - pivot[0.0]

    anchor_slopes = _summarize_grouped(pivot, ["date", "mode"], "slope", ANCHOR_COUNT)
    anchor_endpoints = _summarize_grouped(pivot, ["date", "mode"], "endpoint_contrast", ANCHOR_COUNT)
    anchor_endpoints = anchor_endpoints.rename(columns={column: f"endpoint_{column}" for column in anchor_endpoints.columns if column not in {"date", "mode"}})
    anchor_summary = anchor_slopes.merge(anchor_endpoints, on=["date", "mode"], validate="one_to_one")

    date_blocks = pivot.groupby(["stage", "date", "block_index"], as_index=False)[["slope", "endpoint_contrast"]].mean()
    date_slopes = _summarize_grouped(date_blocks, ["date"], "slope", DATE_COUNT)
    date_endpoints = _summarize_grouped(date_blocks, ["date"], "endpoint_contrast", DATE_COUNT)
    date_endpoints = date_endpoints.rename(columns={column: f"endpoint_{column}" for column in date_endpoints.columns if column != "date"})
    date_summary = date_slopes.merge(date_endpoints, on="date", validate="one_to_one")

    curve_blocks = blocks.groupby(["stage", "block_index", "hotspot_weight"], as_index=False)["normalized_mean_difference"].mean()
    curve = _summarize_grouped(curve_blocks, ["hotspot_weight"], "normalized_mean_difference", len(WEIGHTS))
    curve["sign_class"] = np.where(curve["ci_low"] > 0, "positive", np.where(curve["ci_high"] < 0, "negative", "unresolved"))

    global_blocks = pivot.groupby(["stage", "block_index"], as_index=False)[["slope", "endpoint_contrast"]].mean()
    global_slope = t_summary(global_blocks["slope"].to_numpy(float), comparisons=1)
    global_endpoint = t_summary(global_blocks["endpoint_contrast"].to_numpy(float), comparisons=1)

    curve_index = curve.set_index("hotspot_weight")
    date_pvalue = exact_sign_flip_pvalue(date_summary["mean"].to_numpy(float))
    gates = {
        "input_manifests_verified": True,
        "complete_design": len(cells) == 80 and len(blocks) == 3200,
        "stage_seeds_disjoint": True,
        "zero_censoring": int(cells["censored_count"].sum()) == 0,
        "route_increment_support_fixed_within_anchor": True,
        "uniform_effect_simultaneously_positive": float(curve_index.loc[0.0, "ci_low"]) > 0,
        "half_hotspot_effect_simultaneously_negative": float(curve_index.loc[0.5, "ci_high"]) < 0,
        "hotspot_effect_simultaneously_negative": float(curve_index.loc[1.0, "ci_high"]) < 0,
        "fixed_anchor_mean_slope_negative": float(global_slope["ci_high"]) < 0,
        "fixed_anchor_endpoint_contrast_negative": float(global_endpoint["ci_high"]) < 0,
    }
    status = "PASS" if all(gates.values()) else "FAIL"
    metadata: dict[str, object] = {
        "artifact_kind": "post-primary-sign-mechanism-closure",
        "claim_status": "finite-grid mechanistic synthesis; not a universal sign theorem",
        "status": status,
        "weights": list(WEIGHTS),
        "stage_count": len(STAGES),
        "date_cluster_count": DATE_COUNT,
        "anchor_count": ANCHOR_COUNT,
        "cell_count": int(len(cells)),
        "block_row_count": int(len(blocks)),
        "unique_seed_count": int(cells["seed"].nunique()),
        "global_fixed_anchor_slope": global_slope,
        "global_endpoint_contrast_lambda1_minus_lambda0": global_endpoint,
        "negative_anchor_slope_count": int((anchor_summary["mean"] < 0).sum()),
        "negative_date_slope_count": int((date_summary["mean"] < 0).sum()),
        "date_cluster_exact_sign_flip_p_two_sided": date_pvalue,
        "original_formal_slope_precision_gate_pass": bool(stage_audits["formal"]["slope_precision_gate_pass"]),
        "original_replication_slope_precision_gate_pass": bool(stage_audits["replication"]["slope_precision_gate_pass"]),
        "gates": gates,
        "limitations": [
            "the four dates, not the eight primary/hub anchors, are the conservative topology-time units",
            "the date-cluster exact sign-flip p-value is descriptive because only four dates are available",
            "the original replication precision gate failed for the 2026-primary anchor (maximum half-width exceeded 0.03); pooling does not erase that failure",
            "the five-point mean curve is not strictly monotone between lambda=0.75 and lambda=1",
            "route-probability interpolation changes drift, covariance, and higher increment moments together",
            "the analysis covers frozen 31-node projections, synthetic shortest-path demand, N=40, unit payments, no retries, and no rebalancing",
            "the stopping event is first directional balance depletion, not observed real-payment failure",
        ],
        "software": {"python": platform.python_version(), "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__, "matplotlib": mpl.__version__},
    }

    _write_csv(output / "sign-mechanism-curve.csv", curve)
    _write_csv(output / "sign-mechanism-anchor-slopes.csv", anchor_summary)
    _write_csv(output / "sign-mechanism-date-clusters.csv", date_summary)
    _write_csv(output / "sign-mechanism-design-audit.csv", pd.DataFrame(design_rows))
    (output / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _plot(curve, anchor_summary, date_summary, output / "sign-mechanism-closure.png")
    _write_manifest(output)
    if status != "PASS":
        raise AssertionError(f"sign-mechanism closure gates failed: {gates}")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser(description="闭合真实拓扑混合符号的有限网格机制证据。")
    parser.add_argument("--formal-dir", type=Path, default=Path("results/lightning-drift-interpolation-formal"))
    parser.add_argument("--replication-dir", type=Path, default=Path("results/lightning-drift-interpolation-replication"))
    parser.add_argument("--output", type=Path, default=Path("results/lightning-sign-mechanism-closure"))
    parser.add_argument("--refresh-figure-only", action="store_true")
    args = parser.parse_args()
    if args.refresh_figure_only:
        refresh_published_figure(args.output, args.formal_dir, args.replication_dir)
        print(json.dumps({"status": "PASS", "action": "figure_refreshed"}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(run(args.formal_dir, args.replication_dir, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
