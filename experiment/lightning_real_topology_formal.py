"""Checkpointed formal and replication runs for real-topology kernels."""

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
from lightning_real_topology_preflight import (
    COMPARISONS,
    DEMAND_KINDS,
    MODES,
    SCALES,
    summarize_preflight_cell,
)
from lightning_topology_mapping import (
    build_snapshot_kernel,
    extract_connected_subgraph,
    load_snapshot,
    snapshot_sha256,
)


SEED_BASES = {"formal": 202607230000, "replication": 202607240000}


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


def block_difference_summary(
    correlated: np.ndarray,
    proxy: np.ndarray,
    *,
    scale: int,
    block_size: int,
    comparisons: int = COMPARISONS,
) -> tuple[np.ndarray, dict[str, float | int]]:
    """Summarize non-overlapping block means of the paired normalized difference."""
    if correlated.shape != proxy.shape or correlated.ndim != 1:
        raise ValueError("paired arrays must be one-dimensional and shape-matched")
    if type(block_size) is not int or block_size < 2 or len(correlated) % block_size:
        raise ValueError("block_size must divide the paired sample length")
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    if type(comparisons) is not int or comparisons <= 0:
        raise ValueError("comparisons must be a positive integer")
    normalized = (correlated.astype(np.float64) - proxy.astype(np.float64)) / (
        scale * scale
    )
    block_means = normalized.reshape(-1, block_size).mean(axis=1)
    block_count = len(block_means)
    standard_error = float(block_means.std(ddof=1) / math.sqrt(block_count))
    critical = float(student_t.ppf(1.0 - 0.05 / (2.0 * comparisons), block_count - 1))
    mean = float(block_means.mean())
    halfwidth = critical * standard_error
    return block_means, {
        "block_size": block_size,
        "block_count": block_count,
        "block_mean_difference": mean,
        "block_standard_error": standard_error,
        "block_simultaneous_critical": critical,
        "block_ci_low": mean - halfwidth,
        "block_ci_high": mean + halfwidth,
        "block_ci_halfwidth": halfwidth,
    }


def _checkpoint_path(raw_dir: Path, cell_number: int, cell_id: str) -> Path:
    safe = cell_id.replace("/", "-")
    return raw_dir / f"{cell_number:02d}-{safe}.npz"


def _load_or_run_cell(
    path: Path,
    kernel,
    *,
    scale: int,
    repetitions: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, float, bool]:
    if path.exists():
        with np.load(path, allow_pickle=False) as checkpoint:
            if (
                int(checkpoint["scale"]) != scale
                or int(checkpoint["repetitions"]) != repetitions
                or int(checkpoint["seed"]) != seed
            ):
                raise ValueError(f"checkpoint configuration mismatch: {path}")
            correlated = checkpoint["correlated_times"]
            proxy = checkpoint["proxy_times"]
            runtime = float(checkpoint["runtime_seconds"])
        if correlated.shape != (repetitions,) or proxy.shape != (repetitions,):
            raise ValueError(f"checkpoint shape mismatch: {path}")
        return correlated, proxy, runtime, True

    started = time.perf_counter()
    sample = simulate_paired_proxy_compiled(
        kernel, scale=scale, repetitions=repetitions, seed=seed
    )
    runtime = time.perf_counter() - started
    temporary = path.with_suffix(".tmp.npz")
    np.savez_compressed(
        temporary,
        correlated_times=sample.correlated_times,
        proxy_times=sample.proxy_times,
        scale=np.int64(scale),
        repetitions=np.int64(repetitions),
        seed=np.int64(seed),
        runtime_seconds=np.float64(runtime),
    )
    temporary.replace(path)
    return sample.correlated_times, sample.proxy_times, runtime, False


def run_formal_stage(
    snapshot_root: Path,
    output: Path,
    *,
    stage: str,
    repetitions: int = 20_000,
    block_size: int = 500,
) -> dict[str, object]:
    if stage not in SEED_BASES:
        raise ValueError("stage must be 'formal' or 'replication'")
    if type(repetitions) is not int or repetitions <= 1:
        raise ValueError("repetitions must be an integer greater than one")
    if repetitions % block_size:
        raise ValueError("block_size must divide repetitions")
    if (output / "SHA256SUMS.txt").exists():
        raise ValueError("completed output directory must not be overwritten")
    output.mkdir(parents=True, exist_ok=True)
    raw_dir = output / "raw"
    raw_dir.mkdir(exist_ok=True)
    started = time.perf_counter()
    rows: list[dict[str, object]] = []
    block_rows: list[dict[str, object]] = []
    checkpoint_hits = 0

    # Compile before timed cells.
    warm_graph = nx.path_graph(("a", "b", "c"))
    for index, edge in enumerate(warm_graph.edges):
        warm_graph.edges[edge]["scid"] = str(index)
    warm_kernel, _ = build_snapshot_kernel(warm_graph, demand_kind="uniform")
    simulate_paired_proxy_compiled(warm_kernel, scale=1, repetitions=2, seed=1)

    cell_number = 0
    for snapshot_index, (filename, declared) in enumerate(SNAPSHOTS.items()):
        snapshot_path = snapshot_root / filename
        digest = snapshot_sha256(snapshot_path)
        graph = load_snapshot(
            snapshot_path,
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
                    cell_number += 1
                    cell_id = f"{declared['date']}-{mode}-{demand_kind}-N{scale}"
                    seed = (
                        SEED_BASES[stage]
                        + snapshot_index * 1000
                        + mode_index * 100
                        + demand_index * 10
                        + scale_index
                    )
                    checkpoint = _checkpoint_path(raw_dir, cell_number, cell_id)
                    correlated, proxy, runtime, reused = _load_or_run_cell(
                        checkpoint,
                        kernel,
                        scale=scale,
                        repetitions=repetitions,
                        seed=seed,
                    )
                    checkpoint_hits += int(reused)
                    path_summary = summarize_preflight_cell(
                        correlated, proxy, scale=scale
                    )
                    block_means, block_summary = block_difference_summary(
                        correlated,
                        proxy,
                        scale=scale,
                        block_size=block_size,
                    )
                    rows.append(
                        {
                            "cell_id": cell_id,
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
                            **path_summary,
                            **block_summary,
                            "censored_count": 0,
                            "runtime_seconds": runtime,
                            "raw_file": checkpoint.relative_to(output).as_posix(),
                            "raw_sha256": _sha256(checkpoint),
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
                    print(
                        f"[{cell_number:02d}/{COMPARISONS}] {stage} {cell_id} "
                        f"runtime={runtime:.3f}s reused={reused} "
                        f"halfwidth={block_summary['block_ci_halfwidth']:.6g}",
                        flush=True,
                    )

    if len(rows) != COMPARISONS or len(block_rows) != COMPARISONS * (repetitions // block_size):
        raise AssertionError("formal grid or block table is incomplete")
    prefix = f"lightning-{stage}"
    summary_path = output / f"{prefix}.csv"
    blocks_path = output / f"{prefix}-blocks.csv"
    _write_csv(summary_path, rows)
    _write_csv(blocks_path, block_rows)
    maximum_halfwidth = max(float(row["block_ci_halfwidth"]) for row in rows)
    metadata: dict[str, object] = {
        "artifact_kind": f"real-topology-stopping-time-{stage}",
        "claim_boundary": "real topology, synthetic demand; finite-grid evidence only",
        "repetitions_per_cell": repetitions,
        "block_size": block_size,
        "block_count_per_cell": repetitions // block_size,
        "comparisons": COMPARISONS,
        "cell_count": len(rows),
        "unique_seed_count": len({row["seed"] for row in rows}),
        "checkpoint_hits": checkpoint_hits,
        "censored_count": 0,
        "maximum_block_ci_halfwidth": maximum_halfwidth,
        "precision_target": 0.03,
        "precision_gate_pass": maximum_halfwidth <= 0.03,
        "maximum_cell_runtime_seconds": max(float(row["runtime_seconds"]) for row in rows),
        "sum_cell_runtime_seconds": sum(float(row["runtime_seconds"]) for row in rows),
        "wall_runtime_seconds": time.perf_counter() - started,
        "source_archive_sha256": "f380b71796edd86019ddc0b7822938559bfd40a2f650b21ccb66f14ef10e9320",
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "networkx": nx.__version__,
            "numba": numba.__version__,
        },
    }
    metadata_path = output / f"{prefix}-metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    artifacts = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = "".join(
        f"{_sha256(path)}  {path.relative_to(output).as_posix()}\n" for path in artifacts
    )
    (output / "SHA256SUMS.txt").write_text(manifest, encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=tuple(SEED_BASES), required=True)
    parser.add_argument(
        "--snapshot-root",
        type=Path,
        default=Path("data/raw/ln-geolocated-2019-2023/selected_snapshots"),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repetitions", type=int, default=20_000)
    parser.add_argument("--block-size", type=int, default=500)
    arguments = parser.parse_args()
    metadata = run_formal_stage(
        arguments.snapshot_root,
        arguments.output,
        stage=arguments.stage,
        repetitions=arguments.repetitions,
        block_size=arguments.block_size,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
