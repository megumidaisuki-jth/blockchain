"""Compare the 2026 formal run with its independent-seed replication."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import platform

import numpy as np
import scipy

from lightning_current_2026_preflight import COMPARISONS
from lightning_real_topology_comparison import welch_block_comparison


PRECISION_TARGET = 0.03


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _verify_manifest(directory: Path) -> int:
    lines = (directory / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    for line in lines:
        expected, relative = line.split("  ", 1)
        if _sha256(directory / relative) != expected:
            raise ValueError(f"manifest mismatch: {directory / relative}")
    return len(lines)


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
        if array.shape != (40,) or not np.all(np.isfinite(array)):
            raise ValueError(f"invalid 40-block sample: {cell_id}")
        result[cell_id] = array
    return result


def run_comparison(formal_dir: Path, replication_dir: Path, output: Path) -> dict[str, object]:
    formal_dir = Path(formal_dir)
    replication_dir = Path(replication_dir)
    output = Path(output)
    if output.exists() and any(output.iterdir()):
        raise ValueError("comparison output directory must be empty or absent")
    output.mkdir(parents=True, exist_ok=True)
    formal_manifest_entries = _verify_manifest(formal_dir)
    replication_manifest_entries = _verify_manifest(replication_dir)

    formal_summary_path = formal_dir / "lightning-current-2026-formal.csv"
    replication_summary_path = (
        replication_dir / "lightning-current-2026-replication.csv"
    )
    formal_metadata = json.loads(
        (formal_dir / "lightning-current-2026-formal-metadata.json").read_text(
            encoding="utf-8"
        )
    )
    replication_metadata = json.loads(
        (
            replication_dir / "lightning-current-2026-replication-metadata.json"
        ).read_text(encoding="utf-8")
    )
    formal_rows = _read_csv(formal_summary_path)
    replication_rows = _read_csv(replication_summary_path)
    formal_by_id = {row["cell_id"]: row for row in formal_rows}
    replication_by_id = {row["cell_id"]: row for row in replication_rows}
    ids = set(formal_by_id)
    if (
        len(formal_rows) != COMPARISONS
        or len(replication_rows) != COMPARISONS
        or len(formal_by_id) != COMPARISONS
        or set(replication_by_id) != ids
    ):
        raise ValueError("formal and replication must contain the same 16 cells")

    configuration_fields = (
        "source",
        "source_sha256",
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
    for cell_id in ids:
        if any(
            formal_by_id[cell_id][field] != replication_by_id[cell_id][field]
            for field in configuration_fields
        ):
            raise ValueError(f"configuration mismatch: {cell_id}")

    formal_blocks = _blocks_by_cell(
        formal_dir / "lightning-current-2026-formal-blocks.csv"
    )
    replication_blocks = _blocks_by_cell(
        replication_dir / "lightning-current-2026-replication-blocks.csv"
    )
    if set(formal_blocks) != ids or set(replication_blocks) != ids:
        raise ValueError("block tables do not cover all 16 cells")

    rows: list[dict[str, object]] = []
    direct_failures: list[str] = []
    precision_failures: list[str] = []
    for cell_id in sorted(ids):
        first = formal_by_id[cell_id]
        second = replication_by_id[cell_id]
        comparison = welch_block_comparison(
            formal_blocks[cell_id],
            replication_blocks[cell_id],
            comparisons=COMPARISONS,
        )
        formal_halfwidth = float(first["block_ci_halfwidth"])
        replication_halfwidth = float(second["block_ci_halfwidth"])
        precision_pass = (
            formal_halfwidth <= PRECISION_TARGET
            and replication_halfwidth <= PRECISION_TARGET
        )
        contains_zero = bool(comparison["contains_zero"])
        if not contains_zero:
            direct_failures.append(cell_id)
        if not precision_pass:
            precision_failures.append(cell_id)
        rows.append(
            {
                "cell_id": cell_id,
                "date": first["date"],
                "mode": first["mode"],
                "demand_kind": first["demand_kind"],
                "scale": int(first["scale"]),
                "formal_seed": int(first["seed"]),
                "replication_seed": int(second["seed"]),
                **comparison,
                "formal_block_ci_halfwidth": formal_halfwidth,
                "replication_block_ci_halfwidth": replication_halfwidth,
                "precision_gate_pass": precision_pass,
                "direct_replication_gate_pass": contains_zero,
                "combined_gate_pass": precision_pass and contains_zero,
            }
        )

    comparison_path = output / "lightning-current-2026-replication-comparison.csv"
    failures_path = output / "lightning-current-2026-replication-failing-cells.txt"
    _write_csv(comparison_path, rows)
    failures_path.write_text(
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
        "artifact_kind": "current-2026-independent-replication-comparison",
        "claim_boundary": "current filtered high-capacity geolocated projection; finite-grid evidence only",
        "cell_count": COMPARISONS,
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
        "effect_correlation": float(
            np.corrcoef(formal_effects, replication_effects)[0, 1]
        ),
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
    metadata_path = output / "lightning-current-2026-replication-comparison-metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    artifacts = (comparison_path, failures_path, metadata_path)
    (output / "SHA256SUMS.txt").write_text(
        "".join(f"{_sha256(path)}  {path.name}\n" for path in artifacts),
        encoding="utf-8",
    )
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
