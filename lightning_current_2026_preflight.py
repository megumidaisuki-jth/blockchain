"""Preflight the frozen 2026 mempool.space topology projection."""

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

from lightning_mapping_simulation import simulate_paired_proxy_compiled
from lightning_real_topology_formal import block_difference_summary
from lightning_real_topology_preflight import summarize_preflight_cell
from lightning_topology_mapping import (
    build_snapshot_kernel,
    extract_connected_subgraph,
    load_mempool_channels_geo,
    snapshot_sha256,
)


SCALES = (10, 20, 40, 80)
MODES = ("primary", "hub")
DEMAND_KINDS = ("uniform", "hotspot")
COMPARISONS = len(SCALES) * len(MODES) * len(DEMAND_KINDS)
BLOCK_COUNT = 40
SEED_BASE = 202607250000
EXPECTED_SOURCE_SHAPE = {
    "record_count": 10_000,
    "unique_undirected_pair_count": 9_999,
    "duplicate_undirected_pair_count": 1,
    "node_count": 1_277,
    "edge_count": 9_999,
    "component_count": 3,
    "largest_component_node_count": 1_273,
    "largest_component_edge_count": 9_997,
}


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


def plan_formal_repetitions(
    maximum_block_halfwidth: float,
    *,
    pilot_repetitions: int,
    target: float = 0.03,
    minimum: int = 20_000,
    multiple: int = BLOCK_COUNT,
) -> int:
    """Scale the worst block halfwidth by n^-1/2 and round conservatively."""
    if (
        not math.isfinite(maximum_block_halfwidth)
        or maximum_block_halfwidth <= 0.0
        or type(pilot_repetitions) is not int
        or pilot_repetitions < BLOCK_COUNT
        or not math.isfinite(target)
        or target <= 0.0
        or type(minimum) is not int
        or minimum < 1
        or type(multiple) is not int
        or multiple < 1
    ):
        raise ValueError("invalid formal repetition planning arguments")
    required = pilot_repetitions * (maximum_block_halfwidth / target) ** 2
    planned = max(minimum, math.ceil(required - 1e-12))
    return int(math.ceil(planned / multiple) * multiple)


def run_preflight(
    source: Path,
    output: Path,
    *,
    repetitions: int = 2_000,
) -> dict[str, object]:
    if (
        type(repetitions) is not int
        or repetitions < BLOCK_COUNT * 2
        or repetitions % BLOCK_COUNT
    ):
        raise ValueError("repetitions must be divisible by 40 and give at least two paths per block")
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    source = Path(source)
    digest = snapshot_sha256(source)
    if digest != "fbddddc486a8bb644520c373fd9588dc3811a6414c77185f0b2e8740e338637b":
        raise ValueError("2026 projection SHA-256 does not match the frozen contract")
    graph, source_shape = load_mempool_channels_geo(source, expected_records=10_000)
    if source_shape != EXPECTED_SOURCE_SHAPE:
        raise ValueError("2026 projection shape does not match the frozen contract")

    warm_graph = nx.path_graph(("a", "b", "c"))
    for index, edge in enumerate(warm_graph.edges):
        warm_graph.edges[edge]["scid"] = str(index)
    warm_kernel, _ = build_snapshot_kernel(warm_graph, demand_kind="uniform")
    simulate_paired_proxy_compiled(warm_kernel, scale=1, repetitions=2, seed=1)

    started = time.perf_counter()
    rows: list[dict[str, object]] = []
    block_rows: list[dict[str, object]] = []
    block_size = repetitions // BLOCK_COUNT
    cell_number = 0
    for mode_index, mode in enumerate(MODES):
        subgraph = extract_connected_subgraph(graph, digest, mode=mode, node_count=31)
        for demand_index, demand_kind in enumerate(DEMAND_KINDS):
            kernel, kernel_metadata = build_snapshot_kernel(
                subgraph, demand_kind=demand_kind
            )
            for scale_index, scale in enumerate(SCALES):
                seed = SEED_BASE + mode_index * 100 + demand_index * 10 + scale_index
                cell_id = f"2026-07-22-{mode}-{demand_kind}-N{scale}"
                cell_started = time.perf_counter()
                sample = simulate_paired_proxy_compiled(
                    kernel, scale=scale, repetitions=repetitions, seed=seed
                )
                runtime = time.perf_counter() - cell_started
                path_summary = summarize_preflight_cell(
                    sample.correlated_times,
                    sample.proxy_times,
                    scale=scale,
                    comparisons=COMPARISONS,
                )
                block_means, block_summary = block_difference_summary(
                    sample.correlated_times,
                    sample.proxy_times,
                    scale=scale,
                    block_size=block_size,
                    comparisons=COMPARISONS,
                )
                rows.append(
                    {
                        "cell_id": cell_id,
                        "source": source.name,
                        "source_sha256": digest,
                        "date": "2026-07-22",
                        "mode": mode,
                        "demand_kind": demand_kind,
                        "scale": scale,
                        "seed": seed,
                        "node_count": subgraph.number_of_nodes(),
                        "channel_pair_count": subgraph.number_of_edges(),
                        "route_count": kernel_metadata["route_count"],
                        "multi_channel_route_count": kernel_metadata[
                            "multi_channel_route_count"
                        ],
                        **path_summary,
                        **block_summary,
                        "censored_count": 0,
                        "runtime_seconds": runtime,
                    }
                )
                for block_index, value in enumerate(block_means):
                    block_rows.append(
                        {
                            "cell_id": cell_id,
                            "block_index": block_index,
                            "normalized_mean_difference": float(value),
                        }
                    )
                cell_number += 1
                print(
                    f"[{cell_number:02d}/{COMPARISONS}] {cell_id} "
                    f"runtime={runtime:.3f}s block_halfwidth={block_summary['block_ci_halfwidth']:.6g}",
                    flush=True,
                )

    if len(rows) != COMPARISONS or len(block_rows) != COMPARISONS * BLOCK_COUNT:
        raise AssertionError("2026 preflight grid is incomplete")
    maximum_halfwidth = max(float(row["block_ci_halfwidth"]) for row in rows)
    planned_repetitions = plan_formal_repetitions(
        maximum_halfwidth, pilot_repetitions=repetitions
    )
    summary_path = output / "lightning-current-2026-preflight.csv"
    blocks_path = output / "lightning-current-2026-preflight-blocks.csv"
    _write_csv(summary_path, rows)
    _write_csv(blocks_path, block_rows)
    metadata: dict[str, object] = {
        "artifact_kind": "current-2026-filtered-topology-preflight",
        "claim_boundary": "current filtered high-capacity geolocated projection; planning only",
        "cell_count": COMPARISONS,
        "comparisons": COMPARISONS,
        "repetitions_per_cell": repetitions,
        "block_count_per_cell": BLOCK_COUNT,
        "block_size": block_size,
        "censored_count": 0,
        "maximum_block_ci_halfwidth": maximum_halfwidth,
        "minimum_block_ci_halfwidth": min(float(row["block_ci_halfwidth"]) for row in rows),
        "precision_target": 0.03,
        "planned_formal_repetitions_per_cell": planned_repetitions,
        "planned_formal_block_size": planned_repetitions // BLOCK_COUNT,
        "source_sha256": digest,
        "source_shape": source_shape,
        "maximum_cell_runtime_seconds": max(float(row["runtime_seconds"]) for row in rows),
        "wall_runtime_seconds": time.perf_counter() - started,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "networkx": nx.__version__,
            "numba": numba.__version__,
        },
    }
    metadata_path = output / "lightning-current-2026-preflight-metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    artifacts = (summary_path, blocks_path, metadata_path)
    (output / "SHA256SUMS.txt").write_text(
        "".join(f"{_sha256(path)}  {path.name}\n" for path in artifacts),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("data/raw/mempool-lightning-2026-07-22/channels-geo.json"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/lightning-current-2026-preflight"),
    )
    parser.add_argument("--repetitions", type=int, default=2_000)
    arguments = parser.parse_args()
    metadata = run_preflight(
        arguments.source, arguments.output, repetitions=arguments.repetitions
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
