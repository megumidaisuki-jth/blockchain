"""Post-primary pooled independent-seed precision sensitivity analysis."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform

import numpy as np
import scipy
from scipy.stats import t as student_t


ALPHA = 0.05
PRECISION_TARGET = 0.03


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def pooled_block_summary(
    primary_blocks: np.ndarray,
    replication_blocks: np.ndarray,
    *,
    comparisons: int,
) -> dict[str, float | int]:
    """Pool equal-sized independent-seed block means and form a simultaneous CI."""
    primary = np.asarray(primary_blocks, dtype=np.float64)
    replication = np.asarray(replication_blocks, dtype=np.float64)
    if (
        primary.ndim != 1
        or replication.ndim != 1
        or primary.shape != replication.shape
        or primary.size < 2
        or not np.all(np.isfinite(primary))
        or not np.all(np.isfinite(replication))
    ):
        raise ValueError("independent block samples must be finite and shape-matched")
    if type(comparisons) is not int or comparisons <= 0:
        raise ValueError("comparisons must be a positive integer")
    pooled = np.concatenate((primary, replication))
    block_count = pooled.size
    mean = float(pooled.mean())
    standard_error = float(pooled.std(ddof=1) / math.sqrt(block_count))
    critical = float(
        student_t.ppf(1.0 - ALPHA / (2.0 * comparisons), block_count - 1)
    )
    halfwidth = critical * standard_error
    return {
        "pooled_block_count": int(block_count),
        "pooled_mean_difference": mean,
        "pooled_standard_error": standard_error,
        "pooled_simultaneous_critical": critical,
        "pooled_ci_low": mean - halfwidth,
        "pooled_ci_high": mean + halfwidth,
        "pooled_ci_halfwidth": halfwidth,
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _blocks_by_cell(path: Path) -> dict[str, np.ndarray]:
    grouped: dict[str, list[tuple[int, float]]] = {}
    for row in _read_csv(path):
        grouped.setdefault(row["cell_id"], []).append(
            (int(row["block_index"]), float(row["normalized_mean_difference"]))
        )
    result: dict[str, np.ndarray] = {}
    for cell_id, values in grouped.items():
        values.sort()
        if [index for index, _ in values] != list(range(len(values))):
            raise ValueError(f"non-contiguous block indices: {cell_id}")
        array = np.asarray([value for _, value in values], dtype=np.float64)
        if not np.all(np.isfinite(array)):
            raise ValueError(f"non-finite block sample: {cell_id}")
        result[cell_id] = array
    return result


def run_pooled_sensitivity(
    primary_summary: Path,
    replication_summary: Path,
    primary_blocks_path: Path,
    replication_blocks_path: Path,
    output: Path,
    *,
    comparisons: int,
    label: str,
) -> dict[str, object]:
    if type(comparisons) is not int or comparisons <= 0:
        raise ValueError("comparisons must be a positive integer")
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("pooled sensitivity output must be empty or absent")
    output.mkdir(parents=True, exist_ok=True)
    primary_rows = _read_csv(primary_summary)
    replication_rows = _read_csv(replication_summary)
    primary_by_id = {row["cell_id"]: row for row in primary_rows}
    replication_by_id = {row["cell_id"]: row for row in replication_rows}
    ids = set(primary_by_id)
    if (
        len(primary_rows) != comparisons
        or len(replication_rows) != comparisons
        or len(primary_by_id) != comparisons
        or set(replication_by_id) != ids
    ):
        raise ValueError("summary tables must cover the same declared comparison family")
    configuration_fields = (
        "date",
        "mode",
        "demand_kind",
        "scale",
        "node_count",
        "channel_count",
        "route_count",
        "multi_channel_route_count",
        "repetitions",
        "block_size",
        "block_count",
        "censored_count",
    )
    primary_seeds = {int(row["seed"]) for row in primary_rows}
    replication_seeds = {int(row["seed"]) for row in replication_rows}
    if not primary_seeds.isdisjoint(replication_seeds):
        raise ValueError("pooled runs must use disjoint seed sets")
    for cell_id in ids:
        if any(
            primary_by_id[cell_id][field] != replication_by_id[cell_id][field]
            for field in configuration_fields
        ):
            raise ValueError(f"configuration mismatch: {cell_id}")
    primary_blocks = _blocks_by_cell(primary_blocks_path)
    replication_blocks = _blocks_by_cell(replication_blocks_path)
    if set(primary_blocks) != ids or set(replication_blocks) != ids:
        raise ValueError("block tables do not cover the declared family")

    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for cell_id in sorted(ids):
        first = primary_by_id[cell_id]
        second = replication_by_id[cell_id]
        summary = pooled_block_summary(
            primary_blocks[cell_id],
            replication_blocks[cell_id],
            comparisons=comparisons,
        )
        precision_pass = float(summary["pooled_ci_halfwidth"]) <= PRECISION_TARGET
        if not precision_pass:
            failures.append(cell_id)
        rows.append(
            {
                "cell_id": cell_id,
                "date": first["date"],
                "mode": first["mode"],
                "demand_kind": first["demand_kind"],
                "scale": int(first["scale"]),
                "primary_seed": int(first["seed"]),
                "replication_seed": int(second["seed"]),
                "primary_repetitions": int(first["repetitions"]),
                "replication_repetitions": int(second["repetitions"]),
                "total_repetitions": int(first["repetitions"])
                + int(second["repetitions"]),
                "block_size": int(first["block_size"]),
                **summary,
                "precision_target": PRECISION_TARGET,
                "pooled_precision_gate_pass": precision_pass,
            }
        )

    results_path = output / f"{label}-pooled-sensitivity.csv"
    failures_path = output / f"{label}-pooled-sensitivity-failing-cells.txt"
    _write_csv(results_path, rows)
    failures_path.write_text(
        "".join(f"{cell_id}\n" for cell_id in failures), encoding="utf-8"
    )
    metadata: dict[str, object] = {
        "artifact_kind": "post-primary-pooled-independent-seed-precision-sensitivity",
        "label": label,
        "not_a_replacement_for_primary_runs": True,
        "comparisons": comparisons,
        "cell_count": len(rows),
        "seed_sets_disjoint": True,
        "pooled_block_count_per_cell": int(rows[0]["pooled_block_count"]),
        "total_repetitions_per_cell": int(rows[0]["total_repetitions"]),
        "precision_target": PRECISION_TARGET,
        "maximum_pooled_ci_halfwidth": max(
            float(row["pooled_ci_halfwidth"]) for row in rows
        ),
        "all_pooled_precision_gates_pass": not failures,
        "failure_count": len(failures),
        "failure_cells": failures,
        "input_sha256": {
            "primary_summary": _sha256(primary_summary),
            "replication_summary": _sha256(replication_summary),
            "primary_blocks": _sha256(primary_blocks_path),
            "replication_blocks": _sha256(replication_blocks_path),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }
    metadata_path = output / f"{label}-pooled-sensitivity-metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    artifacts = (results_path, failures_path, metadata_path)
    (output / "SHA256SUMS.txt").write_text(
        "".join(f"{_sha256(path)}  {path.name}\n" for path in artifacts),
        encoding="utf-8",
    )
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--primary-summary", type=Path, required=True)
    parser.add_argument("--replication-summary", type=Path, required=True)
    parser.add_argument("--primary-blocks", type=Path, required=True)
    parser.add_argument("--replication-blocks", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--comparisons", type=int, required=True)
    parser.add_argument("--label", required=True)
    arguments = parser.parse_args()
    metadata = run_pooled_sensitivity(
        arguments.primary_summary,
        arguments.replication_summary,
        arguments.primary_blocks,
        arguments.replication_blocks,
        arguments.output,
        comparisons=arguments.comparisons,
        label=arguments.label,
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
