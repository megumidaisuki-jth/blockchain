"""Run the predeclared 48-cell real-topology stopping-time preflight."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import time

import networkx as nx
import numba
import numpy as np
import scipy
from scipy.stats import t as student_t

from lightning_mapping_simulation import simulate_paired_proxy_compiled
from lightning_mapping_validation import SNAPSHOTS
from lightning_topology_mapping import (
    build_snapshot_kernel,
    extract_connected_subgraph,
    load_snapshot,
    snapshot_sha256,
)


SCALES = (10, 20, 40, 80)
MODES = ("primary", "hub")
DEMAND_KINDS = ("uniform", "hotspot")
COMPARISONS = len(SNAPSHOTS) * len(MODES) * len(DEMAND_KINDS) * len(SCALES)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def summarize_preflight_cell(
    correlated: np.ndarray,
    proxy: np.ndarray,
    *,
    scale: int,
    comparisons: int = COMPARISONS,
) -> dict[str, float | int]:
    """Return paired statistics and a simultaneous normalized mean-difference CI."""
    if correlated.shape != proxy.shape or correlated.ndim != 1 or len(correlated) < 2:
        raise ValueError("paired time arrays must be one-dimensional and shape-matched")
    if not np.all(np.isfinite(correlated)) or not np.all(np.isfinite(proxy)):
        raise ValueError("paired time arrays must be finite")
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    if type(comparisons) is not int or comparisons <= 0:
        raise ValueError("comparisons must be a positive integer")
    differences = correlated.astype(np.float64) - proxy.astype(np.float64)
    repetitions = len(differences)
    mean_difference = float(differences.mean())
    paired_se = float(differences.std(ddof=1) / math.sqrt(repetitions))
    critical = float(student_t.ppf(1.0 - 0.05 / (2.0 * comparisons), repetitions - 1))
    normalized = mean_difference / (scale * scale)
    normalized_halfwidth = critical * paired_se / (scale * scale)
    mean_proxy = float(proxy.mean())
    return {
        "repetitions": repetitions,
        "mean_correlated": float(correlated.mean()),
        "mean_proxy": mean_proxy,
        "mean_difference": mean_difference,
        "relative_mean_difference": mean_difference / mean_proxy,
        "normalized_mean_difference": normalized,
        "paired_standard_error": paired_se,
        "simultaneous_critical": critical,
        "normalized_ci_low": normalized - normalized_halfwidth,
        "normalized_ci_high": normalized + normalized_halfwidth,
        "normalized_ci_halfwidth": normalized_halfwidth,
        "correlated_q10": float(np.quantile(correlated, 0.10)),
        "correlated_median": float(np.median(correlated)),
        "correlated_q90": float(np.quantile(correlated, 0.90)),
        "proxy_q10": float(np.quantile(proxy, 0.10)),
        "proxy_median": float(np.median(proxy)),
        "proxy_q90": float(np.quantile(proxy, 0.90)),
        "maximum_stopping_time": int(max(correlated.max(), proxy.max())),
    }


def run_preflight(
    snapshot_root: Path,
    output: Path,
    *,
    repetitions: int = 2_000,
) -> dict[str, object]:
    if type(repetitions) is not int or repetitions <= 1:
        raise ValueError("repetitions must be an integer greater than one")
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    rows: list[dict[str, object]] = []

    # Compile before cell timing so the first row does not include JIT latency.
    warm_graph = nx.path_graph(("a", "b", "c"))
    for index, edge in enumerate(warm_graph.edges):
        warm_graph.edges[edge]["scid"] = str(index)
    warm_kernel, _ = build_snapshot_kernel(warm_graph, demand_kind="uniform")
    simulate_paired_proxy_compiled(warm_kernel, scale=1, repetitions=2, seed=1)

    cell_index = 0
    for snapshot_index, (filename, declared) in enumerate(SNAPSHOTS.items()):
        path = snapshot_root / filename
        digest = snapshot_sha256(path)
        graph = load_snapshot(
            path,
            expected_nodes=int(declared["nodes"]),
            expected_edges=int(declared["channels"]),
        )
        for mode_index, mode in enumerate(MODES):
            subgraph = extract_connected_subgraph(graph, digest, mode=mode, node_count=31)
            for demand_index, demand_kind in enumerate(DEMAND_KINDS):
                kernel, kernel_metadata = build_snapshot_kernel(
                    subgraph, demand_kind=demand_kind
                )
                for scale_index, scale in enumerate(SCALES):
                    seed = (
                        202607220000
                        + snapshot_index * 1000
                        + mode_index * 100
                        + demand_index * 10
                        + scale_index
                    )
                    cell_started = time.perf_counter()
                    sample = simulate_paired_proxy_compiled(
                        kernel,
                        scale=scale,
                        repetitions=repetitions,
                        seed=seed,
                    )
                    runtime = time.perf_counter() - cell_started
                    summary = summarize_preflight_cell(
                        sample.correlated_times,
                        sample.proxy_times,
                        scale=scale,
                    )
                    row = {
                        "cell_id": f"{declared['date']}-{mode}-{demand_kind}-N{scale}",
                        "snapshot": filename,
                        "snapshot_sha256": digest,
                        "date": declared["date"],
                        "mode": mode,
                        "demand_kind": demand_kind,
                        "scale": scale,
                        "seed": seed,
                        "node_count": subgraph.number_of_nodes(),
                        "channel_count": subgraph.number_of_edges(),
                        "route_count": kernel_metadata["route_count"],
                        "multi_channel_route_count": kernel_metadata[
                            "multi_channel_route_count"
                        ],
                        **summary,
                        "censored_count": 0,
                        "runtime_seconds": runtime,
                    }
                    rows.append(row)
                    cell_index += 1
                    print(
                        f"[{cell_index:02d}/{COMPARISONS}] {row['cell_id']} "
                        f"runtime={runtime:.3f}s halfwidth={row['normalized_ci_halfwidth']:.6g}",
                        flush=True,
                    )

    if len(rows) != COMPARISONS or len({row["cell_id"] for row in rows}) != COMPARISONS:
        raise AssertionError("preflight grid is incomplete or duplicated")
    csv_path = output / "lightning-preflight.csv"
    _write_csv(csv_path, rows)
    metadata: dict[str, object] = {
        "artifact_kind": "real-topology-stopping-time-preflight",
        "claim_boundary": "performance and uncertainty planning only; not formal evidence",
        "repetitions_per_cell": repetitions,
        "comparisons": COMPARISONS,
        "cell_count": len(rows),
        "unique_seed_count": len({row["seed"] for row in rows}),
        "censored_count": 0,
        "maximum_cell_runtime_seconds": max(row["runtime_seconds"] for row in rows),
        "total_runtime_seconds": time.perf_counter() - started,
        "maximum_normalized_ci_halfwidth": max(
            row["normalized_ci_halfwidth"] for row in rows
        ),
        "minimum_normalized_ci_halfwidth": min(
            row["normalized_ci_halfwidth"] for row in rows
        ),
        "source_archive_sha256": "f380b71796edd86019ddc0b7822938559bfd40a2f650b21ccb66f14ef10e9320",
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "networkx": nx.__version__,
            "numba": numba.__version__,
        },
    }
    metadata_path = output / "lightning-preflight-metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    manifest_lines = [
        f"{_sha256(csv_path)}  {csv_path.name}\n",
        f"{_sha256(metadata_path)}  {metadata_path.name}\n",
    ]
    (output / "SHA256SUMS.txt").write_text("".join(manifest_lines), encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--snapshot-root",
        type=Path,
        default=Path("data/raw/ln-geolocated-2019-2023/selected_snapshots"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/lightning-real-topology-preflight"),
    )
    parser.add_argument("--repetitions", type=int, default=2_000)
    arguments = parser.parse_args()
    metadata = run_preflight(
        arguments.snapshot_root,
        arguments.output,
        repetitions=arguments.repetitions,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
