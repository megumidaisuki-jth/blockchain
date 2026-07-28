"""Exploratory structural analysis of mixed stopping-time effect signs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from lightning_mapping_validation import SNAPSHOTS
from lightning_topology_mapping import build_snapshot_kernel, extract_connected_subgraph, load_mempool_channels_geo, load_snapshot, snapshot_sha256

SCALES = (10, 20, 40, 80)
MODES = ("primary", "hub")
DEMANDS = ("uniform", "hotspot")


def kernel_structure_metrics(kernel) -> dict[str, float | int]:
    """Return graph-channel dependence metrics from a binary-edge kernel."""
    if any(len(edge) != 2 for edge in kernel.spec.edges):
        raise ValueError("structural sign metrics require binary channels")
    scalar_increments = kernel.increments[:, ::2].astype(np.float64)
    drift = kernel.drift[::2].astype(np.float64)
    centered = scalar_increments - drift
    covariance = centered.T @ (centered * kernel.probabilities[:, None])
    off_diagonal = covariance.copy()
    np.fill_diagonal(off_diagonal, 0.0)
    route_lengths = np.fromiter((len(route.edges) for route in kernel.routes), float)
    weights = kernel.probabilities
    positive = off_diagonal[off_diagonal > 0.0]
    negative = off_diagonal[off_diagonal < 0.0]
    return {
        "edge_count": len(kernel.spec.edges), "route_count": len(kernel.routes),
        "mean_route_length": float(weights @ route_lengths),
        "second_moment_route_length": float(weights @ (route_lengths**2)),
        "multi_channel_probability": float(weights[route_lengths > 1].sum()),
        "maximum_absolute_drift": float(np.max(np.abs(drift))),
        "drift_l1": float(np.abs(drift).sum()), "drift_l2": float(np.linalg.norm(drift)),
        "cross_covariance_frobenius": float(np.linalg.norm(off_diagonal)),
        "cross_covariance_spectral": float(np.linalg.norm(off_diagonal, ord=2)),
        "positive_cross_covariance_mass": float(positive.sum()) if positive.size else 0.0,
        "negative_cross_covariance_mass": float(-negative.sum()) if negative.size else 0.0,
        "maximum_absolute_cross_covariance": float(np.max(np.abs(off_diagonal))),
    }


def exact_sign_flip_pvalue(values: np.ndarray) -> float:
    """Exact two-sided sign-flip p-value for the absolute mean statistic."""
    values = np.asarray(values, dtype=float)
    if values.ndim != 1 or not len(values) or not np.all(np.isfinite(values)):
        raise ValueError("values must be a nonempty finite vector")
    if len(values) > 20:
        raise ValueError("exact enumeration is limited to at most 20 values")
    observed = abs(float(values.mean()))
    exceed = 0
    for signs in itertools.product((-1.0, 1.0), repeat=len(values)):
        statistic = abs(float(np.mean(values * np.asarray(signs))))
        exceed += statistic >= observed - 1e-15
    return exceed / (2 ** len(values))


def _historical_kernels(snapshot_root: Path) -> list[dict[str, object]]:
    rows = []
    for filename, declared in SNAPSHOTS.items():
        path = snapshot_root / filename
        digest = snapshot_sha256(path)
        graph = load_snapshot(path, expected_nodes=int(declared["nodes"]), expected_edges=int(declared["channels"]))
        for mode in MODES:
            subgraph = extract_connected_subgraph(graph, digest, mode=mode, node_count=31)
            for demand in DEMANDS:
                kernel, _ = build_snapshot_kernel(subgraph, demand_kind=demand)
                rows.append({"date": declared["date"], "mode": mode, "demand_kind": demand, **kernel_structure_metrics(kernel)})
    return rows


def _current_kernels(source: Path) -> list[dict[str, object]]:
    digest = snapshot_sha256(source)
    graph, _ = load_mempool_channels_geo(source, expected_records=10_000)
    rows = []
    for mode in MODES:
        subgraph = extract_connected_subgraph(graph, digest, mode=mode, node_count=31)
        for demand in DEMANDS:
            kernel, _ = build_snapshot_kernel(subgraph, demand_kind=demand)
            rows.append({"date": "2026-07-22", "mode": mode, "demand_kind": demand, **kernel_structure_metrics(kernel)})
    return rows


def _write_csv(path: Path, frame: pd.DataFrame) -> None:
    frame.to_csv(path, index=False, quoting=csv.QUOTE_MINIMAL)


def _plot(anchor: pd.DataFrame, scale_contrasts: pd.DataFrame, output: Path) -> None:
    mpl.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"], "font.size": 7, "axes.spines.right": False, "axes.spines.top": False, "svg.fonttype": "none", "pdf.fonttype": 42})
    blue, orange, red = "#4C78A8", "#F28E2B", "#C44E52"
    labels = [f"{d[:4]} {m}" for d, m in zip(anchor.date, anchor["mode"])]
    y = np.arange(len(anchor))
    fig, axes = plt.subplots(1, 3, figsize=(183/25.4, 64/25.4), constrained_layout=True)
    ax = axes[0]
    for i, row in anchor.reset_index(drop=True).iterrows(): ax.plot([row.uniform, row.hotspot], [i, i], color="#BBBBBB", lw=1)
    ax.scatter(anchor.uniform, y, color=blue, s=18, label="Uniform (zero drift)", zorder=3)
    ax.scatter(anchor.hotspot, y, color=orange, s=18, label="Hotspot (nonzero drift)", zorder=3)
    ax.axvline(0, color="black", lw=0.7); ax.set_yticks(y, labels); ax.invert_yaxis()
    ax.set_xlabel("Mean normalized effect over four scales"); ax.set_title("a  Drift regime separates effects", loc="left", fontweight="bold"); ax.legend(fontsize=6, loc="lower left")
    ax = axes[1]
    ax.scatter(anchor.contrast, y, color=np.where(anchor.contrast < 0, blue, red), s=18)
    ax.axvline(0, color="black", lw=0.7); ax.set_yticks(y, labels); ax.invert_yaxis(); ax.set_xlabel("Hotspot − uniform effect")
    ax.set_title("b  Paired anchor contrasts", loc="left", fontweight="bold")
    ax.text(0.03, 0.03, f"8/8 negative\nexact sign-flip p = {exact_sign_flip_pvalue(anchor.contrast.to_numpy()):.4f}", transform=ax.transAxes, va="bottom", fontsize=6)
    ax = axes[2]
    matrix = scale_contrasts.pivot(index="anchor", columns="scale", values="contrast").loc[labels, list(SCALES)]
    limit = float(np.max(np.abs(matrix.to_numpy())))
    image = ax.imshow(matrix, cmap="RdBu_r", vmin=-limit, vmax=limit, aspect="auto")
    ax.set_yticks(range(len(labels)), labels); ax.set_xticks(range(4), SCALES); ax.set_xlabel("Scale N")
    ax.set_title("c  Scale-specific contrasts", loc="left", fontweight="bold")
    colorbar = fig.colorbar(image, ax=ax, fraction=0.05, pad=0.03); colorbar.set_label("Hotspot − uniform")
    fig.savefig(output, dpi=600, bbox_inches="tight"); plt.close(fig)


def run_analysis(snapshot_root: Path, current_source: Path, output: Path) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()): raise ValueError("output directory must be absent or empty")
    metrics = pd.DataFrame(_historical_kernels(snapshot_root) + _current_kernels(current_source))
    effects = pd.concat([pd.read_csv("results/lightning-real-topology-pooled-sensitivity/lightning-real-topology-pooled-sensitivity.csv"), pd.read_csv("results/lightning-current-2026-pooled-sensitivity/lightning-current-2026-pooled-sensitivity.csv")], ignore_index=True)
    cells = effects.merge(metrics, on=["date", "mode", "demand_kind"], validate="many_to_one")
    wide = cells.pivot_table(index=["date", "mode", "scale"], columns="demand_kind", values="pooled_mean_difference").reset_index()
    wide["contrast"] = wide["hotspot"] - wide["uniform"]; wide["anchor"] = wide["date"].str[:4] + " " + wide["mode"]
    anchor = wide.groupby(["date", "mode"], as_index=False)[["uniform", "hotspot", "contrast"]].mean()
    date = anchor.groupby("date", as_index=False)["contrast"].mean()
    metadata = {
        "artifact_kind": "post-primary-structural-sign-analysis", "claim_status": "exploratory; theorem-motivating, not preregistered confirmatory evidence",
        "kernel_count": int(len(metrics)), "cell_count": int(len(cells)), "anchor_count": int(len(anchor)), "date_cluster_count": int(len(date)),
        "negative_anchor_contrast_count": int((anchor.contrast < 0).sum()), "negative_scale_contrast_count": int((wide.contrast < 0).sum()), "scale_contrast_count": int(len(wide)),
        "mean_anchor_contrast": float(anchor.contrast.mean()), "median_anchor_contrast": float(anchor.contrast.median()),
        "anchor_exact_sign_flip_p_two_sided": exact_sign_flip_pvalue(anchor.contrast.to_numpy()), "date_cluster_exact_sign_flip_p_two_sided": exact_sign_flip_pvalue(date.contrast.to_numpy()),
        "limitations": ["primary and hub anchors from the same date are not fully independent", "only four date clusters are available", "hotspot demand differs from uniform demand in more than drift magnitude", "pooled effects are post-primary sensitivity estimates"],
    }
    _write_csv(output / "kernel-structure-metrics.csv", metrics); _write_csv(output / "cell-effects-with-structure.csv", cells)
    _write_csv(output / "scale-paired-contrasts.csv", wide); _write_csv(output / "anchor-paired-contrasts.csv", anchor); _write_csv(output / "date-cluster-contrasts.csv", date)
    (output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    _plot(anchor, wide, output / "structural-sign-analysis.png")
    artifacts = sorted(p for p in output.iterdir() if p.name != "SHA256SUMS.txt")
    (output / "SHA256SUMS.txt").write_text("\n".join(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in artifacts) + "\n", encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot-root", type=Path, default=Path("data/raw/ln-geolocated-2019-2023/selected_snapshots"))
    parser.add_argument("--current-source", type=Path, default=Path("data/raw/mempool-lightning-2026-07-22/channels-geo.json"))
    parser.add_argument("--output", type=Path, default=Path("results/lightning-structural-sign-analysis"))
    args = parser.parse_args(); print(json.dumps(run_analysis(args.snapshot_root, args.current_source, args.output), indent=2))


if __name__ == "__main__": main()
