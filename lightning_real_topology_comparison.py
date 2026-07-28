"""Audit and compare the formal and independent real-topology runs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import platform
from typing import Iterable

import numpy as np
import scipy
from scipy.stats import t as student_t


COMPARISONS = 48
ALPHA = 0.05
PRECISION_TARGET = 0.03


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def welch_block_comparison(
    formal_blocks: np.ndarray,
    replication_blocks: np.ndarray,
    *,
    comparisons: int = COMPARISONS,
) -> dict[str, float | bool]:
    """Compare replication minus formal means using a Welch simultaneous interval."""
    formal = np.asarray(formal_blocks, dtype=np.float64)
    replication = np.asarray(replication_blocks, dtype=np.float64)
    if (
        formal.ndim != 1
        or replication.ndim != 1
        or formal.size < 2
        or formal.shape != replication.shape
        or not np.all(np.isfinite(formal))
        or not np.all(np.isfinite(replication))
    ):
        raise ValueError("block samples must be finite, one-dimensional, and shape-matched")
    if type(comparisons) is not int or comparisons <= 0:
        raise ValueError("comparisons must be a positive integer")

    formal_mean = float(formal.mean())
    replication_mean = float(replication.mean())
    difference = replication_mean - formal_mean
    n_formal = formal.size
    n_replication = replication.size
    formal_variance = float(formal.var(ddof=1))
    replication_variance = float(replication.var(ddof=1))
    formal_component = formal_variance / n_formal
    replication_component = replication_variance / n_replication
    standard_error_squared = formal_component + replication_component

    if standard_error_squared == 0.0:
        degrees_of_freedom = math.inf
        standard_error = 0.0
        halfwidth = 0.0
    else:
        denominator = (
            formal_component * formal_component / (n_formal - 1)
            + replication_component * replication_component / (n_replication - 1)
        )
        degrees_of_freedom = standard_error_squared * standard_error_squared / denominator
        standard_error = math.sqrt(standard_error_squared)
        critical = float(
            student_t.ppf(
                1.0 - ALPHA / (2.0 * comparisons), degrees_of_freedom
            )
        )
        halfwidth = critical * standard_error
    critical = float(
        student_t.ppf(1.0 - ALPHA / (2.0 * comparisons), degrees_of_freedom)
    )
    ci_low = difference - halfwidth
    ci_high = difference + halfwidth
    return {
        "formal_mean": formal_mean,
        "replication_mean": replication_mean,
        "difference_replication_minus_formal": difference,
        "welch_standard_error": standard_error,
        "welch_degrees_of_freedom": degrees_of_freedom,
        "simultaneous_critical": critical,
        "simultaneous_ci_low": ci_low,
        "simultaneous_ci_high": ci_high,
        "simultaneous_ci_halfwidth": halfwidth,
        "contains_zero": ci_low <= 0.0 <= ci_high,
    }


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _verify_manifest(directory: Path) -> int:
    manifest = directory / "SHA256SUMS.txt"
    lines = manifest.read_text(encoding="utf-8").splitlines()
    for line in lines:
        expected, relative = line.split("  ", 1)
        if _sha256(directory / relative) != expected:
            raise ValueError(f"manifest mismatch: {directory / relative}")
    return len(lines)


def _stage_paths(directory: Path, stage: str) -> tuple[Path, Path, Path]:
    prefix = f"lightning-{stage}"
    return (
        directory / f"{prefix}.csv",
        directory / f"{prefix}-blocks.csv",
        directory / f"{prefix}-metadata.json",
    )


def _group_blocks(rows: Iterable[dict[str, str]]) -> dict[str, np.ndarray]:
    grouped: dict[str, list[tuple[int, float]]] = {}
    for row in rows:
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
            raise ValueError(f"non-finite block value: {cell_id}")
        result[cell_id] = array
    return result


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run_comparison(formal_dir: Path, replication_dir: Path, output: Path) -> dict[str, object]:
    formal_dir = Path(formal_dir)
    replication_dir = Path(replication_dir)
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("comparison output directory must be empty or absent")
    output.mkdir(parents=True, exist_ok=True)

    formal_manifest_entries = _verify_manifest(formal_dir)
    replication_manifest_entries = _verify_manifest(replication_dir)
    formal_summary_path, formal_blocks_path, formal_metadata_path = _stage_paths(
        formal_dir, "formal"
    )
    replication_summary_path, replication_blocks_path, replication_metadata_path = (
        _stage_paths(replication_dir, "replication")
    )
    formal_metadata = json.loads(formal_metadata_path.read_text(encoding="utf-8"))
    replication_metadata = json.loads(
        replication_metadata_path.read_text(encoding="utf-8")
    )
    formal_rows = _read_csv(formal_summary_path)
    replication_rows = _read_csv(replication_summary_path)
    formal_by_id = {row["cell_id"]: row for row in formal_rows}
    replication_by_id = {row["cell_id"]: row for row in replication_rows}
    expected_ids = set(formal_by_id)
    if (
        len(formal_rows) != COMPARISONS
        or len(replication_rows) != COMPARISONS
        or len(formal_by_id) != COMPARISONS
        or set(replication_by_id) != expected_ids
    ):
        raise ValueError("formal and replication grids must contain the same 48 unique cells")

    configuration_fields = (
        "snapshot",
        "snapshot_sha256",
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
    formal_seeds = {int(row["seed"]) for row in formal_rows}
    replication_seeds = {int(row["seed"]) for row in replication_rows}
    if not formal_seeds.isdisjoint(replication_seeds):
        raise ValueError("formal and replication seeds must be disjoint")
    for cell_id in expected_ids:
        if any(
            formal_by_id[cell_id][field] != replication_by_id[cell_id][field]
            for field in configuration_fields
        ):
            raise ValueError(f"configuration mismatch: {cell_id}")

    formal_blocks = _group_blocks(_read_csv(formal_blocks_path))
    replication_blocks = _group_blocks(_read_csv(replication_blocks_path))
    if set(formal_blocks) != expected_ids or set(replication_blocks) != expected_ids:
        raise ValueError("block tables do not cover the complete grid")

    rows: list[dict[str, object]] = []
    direct_failures: list[str] = []
    precision_failures: list[str] = []
    for cell_id in sorted(expected_ids):
        formal_row = formal_by_id[cell_id]
        replication_row = replication_by_id[cell_id]
        comparison = welch_block_comparison(
            formal_blocks[cell_id], replication_blocks[cell_id]
        )
        formal_halfwidth = float(formal_row["block_ci_halfwidth"])
        replication_halfwidth = float(replication_row["block_ci_halfwidth"])
        precision_pass = (
            formal_halfwidth <= PRECISION_TARGET
            and replication_halfwidth <= PRECISION_TARGET
        )
        if not bool(comparison["contains_zero"]):
            direct_failures.append(cell_id)
        if not precision_pass:
            precision_failures.append(cell_id)
        rows.append(
            {
                "cell_id": cell_id,
                "date": formal_row["date"],
                "mode": formal_row["mode"],
                "demand_kind": formal_row["demand_kind"],
                "scale": int(formal_row["scale"]),
                "formal_seed": int(formal_row["seed"]),
                "replication_seed": int(replication_row["seed"]),
                "block_count": int(formal_row["block_count"]),
                **comparison,
                "formal_block_ci_halfwidth": formal_halfwidth,
                "replication_block_ci_halfwidth": replication_halfwidth,
                "precision_gate_pass": precision_pass,
                "direct_replication_gate_pass": bool(comparison["contains_zero"]),
                "combined_gate_pass": precision_pass
                and bool(comparison["contains_zero"]),
            }
        )

    comparison_path = output / "lightning-replication-comparison.csv"
    failure_path = output / "lightning-replication-failing-cells.txt"
    _write_csv(comparison_path, rows)
    failure_path.write_text(
        "[direct_replication_interval_excludes_zero]\n"
        + "".join(f"{cell_id}\n" for cell_id in direct_failures)
        + "[precision_halfwidth_exceeds_0.03]\n"
        + "".join(f"{cell_id}\n" for cell_id in precision_failures),
        encoding="utf-8",
    )

    formal_effects = np.asarray([float(row["formal_mean"]) for row in rows])
    replication_effects = np.asarray(
        [float(row["replication_mean"]) for row in rows]
    )
    metadata: dict[str, object] = {
        "artifact_kind": "real-topology-independent-replication-comparison",
        "claim_boundary": "real 2020-2023 topology, synthetic demand; finite-grid evidence only",
        "cell_count": len(rows),
        "comparisons": COMPARISONS,
        "seeds_disjoint": True,
        "formal_manifest_entries": formal_manifest_entries,
        "replication_manifest_entries": replication_manifest_entries,
        "all_direct_intervals_contain_zero": not direct_failures,
        "direct_failure_count": len(direct_failures),
        "direct_failure_cells": direct_failures,
        "both_precision_gates_pass": not precision_failures,
        "precision_failure_count": len(precision_failures),
        "precision_failure_cells": precision_failures,
        "overall_gate_pass": not direct_failures and not precision_failures,
        "maximum_absolute_replication_difference": float(
            np.max(np.abs(replication_effects - formal_effects))
        ),
        "root_mean_squared_replication_difference": float(
            np.sqrt(np.mean((replication_effects - formal_effects) ** 2))
        ),
        "effect_correlation": float(np.corrcoef(formal_effects, replication_effects)[0, 1]),
        "formal_precision_gate_pass": bool(formal_metadata["precision_gate_pass"]),
        "replication_precision_gate_pass": bool(
            replication_metadata["precision_gate_pass"]
        ),
        "formal_input_sha256": _sha256(formal_summary_path),
        "replication_input_sha256": _sha256(replication_summary_path),
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scipy": scipy.__version__,
        },
    }
    metadata_path = output / "lightning-replication-comparison-metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    artifacts = sorted(path for path in output.iterdir() if path.is_file())
    manifest = "".join(
        f"{_sha256(path)}  {path.name}\n" for path in artifacts
    )
    (output / "SHA256SUMS.txt").write_text(manifest, encoding="utf-8")
    return metadata


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--formal-dir", type=Path, required=True)
    parser.add_argument("--replication-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    metadata = run_comparison(
        arguments.formal_dir, arguments.replication_dir, arguments.output
    )
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
