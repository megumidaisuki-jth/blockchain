"""Freeze real-topology/synthetic-demand Lightning mapping artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform
import time

import networkx as nx
import numpy as np

from lightning_topology_mapping import (
    build_snapshot_kernel,
    extract_connected_subgraph,
    graph_to_hypergraph_spec,
    load_snapshot,
    snapshot_sha256,
)


SNAPSHOTS = {
    "20201014.gml.geo": {
        "date": "2020-10-14",
        "nodes": 5963,
        "channels": 29940,
        "sha256": "900dbdce07298a65bafcc793bb18efbcd4bd43875a412c4195213dda41bce802",
    },
    "20220531.gml.geo": {
        "date": "2022-05-31",
        "nodes": 15947,
        "channels": 79552,
        "sha256": "1aee99d82a6f60791f17e4176d76d3cfa20cd5931397f46d627a89b6e646e7a4",
    },
    "20230716.gml.geo": {
        "date": "2023-07-16",
        "nodes": 15100,
        "channels": 64212,
        "sha256": "ee1b054a6ba2cb0ea3184f9f68f5cca7d8e70d17ff2d9e44e5e8871be8a8b855",
    },
}


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty artifact {path.name}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_mapping_audit(snapshot_root: Path, output: Path) -> dict[str, object]:
    """Build and serialize all frozen topology-to-kernel mappings."""
    if output.exists() and any(output.iterdir()):
        raise ValueError("output directory must be absent or empty")
    output.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()

    subgraph_rows: list[dict[str, object]] = []
    node_rows: list[dict[str, object]] = []
    channel_rows: list[dict[str, object]] = []
    kernel_rows: list[dict[str, object]] = []
    route_rows: list[dict[str, object]] = []

    for filename, declared in SNAPSHOTS.items():
        path = snapshot_root / filename
        digest = snapshot_sha256(path)
        if digest != declared["sha256"]:
            raise ValueError(f"snapshot SHA-256 mismatch for {filename}")
        graph = load_snapshot(
            path,
            expected_nodes=int(declared["nodes"]),
            expected_edges=int(declared["channels"]),
        )
        for mode in ("primary", "hub"):
            subgraph = extract_connected_subgraph(
                graph, digest, mode=mode, node_count=31
            )
            diameter = nx.diameter(subgraph)
            if subgraph.number_of_edges() < 30:
                raise ValueError(f"subgraph channel gate failed for {filename}/{mode}")
            spec, node_ids = graph_to_hypergraph_spec(subgraph)
            node_index = {node: index for index, node in enumerate(node_ids)}
            subgraph_rows.append(
                {
                    "snapshot": filename,
                    "date": declared["date"],
                    "mode": mode,
                    "snapshot_sha256": digest,
                    "node_count": subgraph.number_of_nodes(),
                    "channel_count": subgraph.number_of_edges(),
                    "diameter": diameter,
                    "connected": nx.is_connected(subgraph),
                }
            )
            for local_index, node_id in enumerate(node_ids):
                node_rows.append(
                    {
                        "snapshot": filename,
                        "mode": mode,
                        "local_node_index": local_index,
                        "node_id": node_id,
                        "subgraph_degree": subgraph.degree(node_id),
                    }
                )
            for edge_index, (left_index, right_index) in enumerate(spec.edges):
                left = node_ids[left_index]
                right = node_ids[right_index]
                attributes = subgraph.edges[left, right]
                channel_rows.append(
                    {
                        "snapshot": filename,
                        "mode": mode,
                        "edge_index": edge_index,
                        "left_node_index": node_index[left],
                        "right_node_index": node_index[right],
                        "left_node_id": left,
                        "right_node_id": right,
                        "scid": attributes["scid"],
                        "htlc_maximum_msat": attributes["htlc_maximum_msat"],
                    }
                )

            for demand_kind in ("uniform", "hotspot"):
                kernel, summary = build_snapshot_kernel(
                    subgraph, demand_kind=demand_kind
                )
                if summary["multi_channel_route_count"] <= 0:
                    raise ValueError("mapping has no atomic multi-channel route")
                if summary["cross_channel_covariance_max_abs"] <= 0.0:
                    raise ValueError("mapping has no cross-channel covariance")
                if demand_kind == "uniform" and summary["maximum_absolute_drift"] > 1e-14:
                    raise ValueError("uniform demand drift gate failed")
                if demand_kind == "hotspot" and summary["maximum_absolute_drift"] <= 1e-14:
                    raise ValueError("hotspot demand drift gate failed")
                kernel_rows.append(
                    {
                        "snapshot": filename,
                        "date": declared["date"],
                        "mode": mode,
                        **summary,
                    }
                )
                for route_index, (route, probability) in enumerate(
                    zip(kernel.routes, kernel.probabilities)
                ):
                    route_rows.append(
                        {
                            "snapshot": filename,
                            "mode": mode,
                            "demand_kind": demand_kind,
                            "route_index": route_index,
                            "probability_hex": float(probability).hex(),
                            "node_indices": ";".join(map(str, route.nodes)),
                            "edge_indices": ";".join(map(str, route.edges)),
                        }
                    )

    files = {
        "lightning-subgraphs.csv": subgraph_rows,
        "lightning-subgraph-nodes.csv": node_rows,
        "lightning-subgraph-channels.csv": channel_rows,
        "lightning-kernels.csv": kernel_rows,
        "lightning-routes.csv": route_rows,
    }
    for name, rows in files.items():
        _write_csv(output / name, rows)

    metadata: dict[str, object] = {
        "artifact_kind": "real-topology-synthetic-demand-mapping",
        "source_dataset_doi": "10.7910/DVN/2OAVO6",
        "source_archive_md5": "e6edd6fd7acae460abd0f70f71c9dbec",
        "source_archive_sha256": "f380b71796edd86019ddc0b7822938559bfd40a2f650b21ccb66f14ef10e9320",
        "snapshot_count": len(SNAPSHOTS),
        "subgraph_count": len(subgraph_rows),
        "kernel_count": len(kernel_rows),
        "node_rows": len(node_rows),
        "channel_rows": len(channel_rows),
        "route_rows": len(route_rows),
        "node_count_per_subgraph": 31,
        "modes": ["primary", "hub"],
        "demand_kinds": ["uniform", "hotspot"],
        "all_shape_gates_pass": len(subgraph_rows) == 6,
        "all_kernel_gates_pass": len(kernel_rows) == 12,
        "claim_boundary": "real topology, transparent synthetic demand; not observed flows or balances",
        "runtime_seconds": time.perf_counter() - started,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "networkx": nx.__version__,
        },
    }
    metadata_path = output / "lightning-mapping-metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    artifact_paths = sorted(path for path in output.iterdir() if path.is_file())
    manifest = "".join(f"{_sha256(path)}  {path.name}\n" for path in artifact_paths)
    (output / "SHA256SUMS.txt").write_text(manifest, encoding="utf-8")
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
        default=Path("results/lightning-real-topology-mapping"),
    )
    arguments = parser.parse_args()
    metadata = run_mapping_audit(arguments.snapshot_root, arguments.output)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
