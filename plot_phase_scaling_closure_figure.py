"""Render the frozen three-regime finite-scale validation figure.

The plotting path is deliberately read-only with respect to experiment data.
It refuses incomplete or mutated inputs, verifies the frozen 40-cell design and
its SHA-256 manifest, and emits exactly one 170-mm, 600-dpi PNG together with a
machine-readable audit and a self-contained Chinese figure legend.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
from typing import Any, Iterable, Mapping

import matplotlib as mpl
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
import numpy as np


FIGURE_WIDTH_MM = 170.0
FIGURE_HEIGHT_MM = 145.0
FIGURE_DPI = 600
FORBIDDEN_ALTERNATE_IMAGE_SUFFIXES = (".svg", ".pdf", ".tif", ".tiff")
EXPERIMENT_ID = "network-phase-closure-20260728"
AMPLITUDE = 0.40
REPETITIONS_PER_CELL = 8000
BLOCK_COUNT = 40
BLOCK_SIZE = 200
BOOTSTRAP_REPETITIONS = 10000
STAGES = ("primary", "replication")

REGIMES: dict[str, dict[str, Any]] = {
    "zero": {
        "label": "零漂移",
        "regime_id": 0,
        "alpha": None,
        "scales": (25, 50, 100, 200, 400),
        "normalizer_type": "N^2",
        "target_exponent": 2.0,
    },
    "drift": {
        "label": r"漂移主导 $\alpha=0.5$",
        "regime_id": 1,
        "alpha": 0.5,
        "scales": (100, 200, 400, 800, 1600),
        "normalizer_type": "1.25*N^1.5",
        "target_exponent": 1.5,
    },
    "critical": {
        "label": r"临界扩散 $\alpha=1$",
        "regime_id": 2,
        "alpha": 1.0,
        "scales": (25, 50, 100, 200, 400),
        "normalizer_type": "N^2",
        "target_exponent": 2.0,
    },
    "fair": {
        "label": r"公平扩散 $\alpha=2$",
        "regime_id": 3,
        "alpha": 2.0,
        "scales": (25, 50, 100, 200, 400),
        "normalizer_type": "N^2",
        "target_exponent": 2.0,
    },
}
REGIME_ORDER = tuple(REGIMES)

# All colors are literal grays. Marker and line style independently encode the
# regime, so the figure remains interpretable after grayscale reproduction.
REGIME_STYLES: dict[str, dict[str, Any]] = {
    "zero": {"rgb": (0.08, 0.08, 0.08), "marker": "o", "linestyle": "-"},
    "drift": {"rgb": (0.25, 0.25, 0.25), "marker": "s", "linestyle": "--"},
    "critical": {"rgb": (0.40, 0.40, 0.40), "marker": "^", "linestyle": "-."},
    "fair": {"rgb": (0.55, 0.55, 0.55), "marker": "D", "linestyle": ":"},
}

EXPECTED_CELL_KEYS = frozenset(
    (stage, regime, scale)
    for stage in STAGES
    for regime, specification in REGIMES.items()
    for scale in specification["scales"]
)
EXPECTED_ADJACENT_KEYS = frozenset(
    (stage, regime, low, high)
    for stage in STAGES
    for regime, specification in REGIMES.items()
    for low, high in zip(specification["scales"][:-1], specification["scales"][1:])
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_input_paths(project_root: Path) -> dict[str, Path]:
    data_dir = project_root.resolve() / "results" / "network-phase-closure"
    return {
        "data_dir": data_dir,
        "cell_csv": data_dir / "phase-cell-summaries.csv",
        "block_csv": data_dir / "phase-block-means.csv",
        "kernel_csv": data_dir / "phase-kernel-diagnostics.csv",
        "adjacent_csv": data_dir / "phase-adjacent-slopes.csv",
        "final_slope_csv": data_dir / "phase-final-three-slopes.csv",
        "comparison_csv": data_dir / "phase-stage-comparisons.csv",
        "gate_json": data_dir / "phase-gates.json",
        "metadata_json": data_dir / "phase-run-metadata.json",
        "manifest": data_dir / "SHA256SUMS.txt",
        "raw_dir": data_dir / "raw",
    }


def _load_csv(path: Path) -> list[dict[str, str]]:
    # ``utf-8-sig`` accepts both ordinary UTF-8 and the BOM used by the final
    # PowerShell merge step without changing any source bytes.
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        value = json.load(stream)
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
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


def _require_columns(rows: list[dict[str, str]], required: Iterable[str], table: str) -> None:
    if not rows:
        raise ValueError(f"{table} is empty")
    missing = sorted(set(required) - set(rows[0]))
    if missing:
        raise ValueError(f"{table} is missing required columns: {missing}")


def _verify_sha256_manifest(manifest_path: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for line in manifest_path.read_text(encoding="ascii").splitlines():
        if not line.strip():
            continue
        pieces = line.split(maxsplit=1)
        if len(pieces) != 2 or len(pieces[0]) != 64:
            raise ValueError(f"malformed SHA-256 line in {manifest_path}: {line!r}")
        expected, filename = pieces
        filename = filename.lstrip("* ")
        target = manifest_path.parent / Path(filename)
        if not target.is_file():
            raise ValueError(f"SHA-256 manifest target is missing: {target}")
        actual = sha256_file(target)
        if actual != expected.lower():
            raise ValueError(f"SHA-256 mismatch for {filename}: {actual} != {expected}")
        entries[Path(filename).as_posix()] = actual
    if not entries:
        raise ValueError(f"empty SHA-256 manifest: {manifest_path}")
    return entries


def _expected_seed(stage: str, regime: str, scale: int) -> int:
    return (
        202607280000
        + 1_000_000 * STAGES.index(stage)
        + 10_000 * int(REGIMES[regime]["regime_id"])
        + scale
    )


def _normalizer(regime: str, scale: int) -> float:
    if regime == "drift":
        return 1.25 * scale**1.5
    return float(scale**2)


def _validate_cells(rows: list[dict[str, str]]) -> None:
    required = {
        "experiment_id", "stage", "regime", "regime_id", "alpha", "scale",
        "amplitude", "seed", "repetitions", "block_count", "block_size",
        "mean_tau", "normalizer", "normalizer_type", "normalized_mean",
        "normalized_ci_low", "normalized_ci_high", "normalized_ci_half_width",
        "relative_interdecile_width", "relative_deviation_probability_30pct",
        "censored_count", "nan_count", "excluded_count", "theoretical_exponent",
        "raw_artifact", "raw_result_sha256",
    }
    _require_columns(rows, required, "phase-cell-summaries.csv")
    if len(rows) != 40:
        raise ValueError(f"phase cell table must contain 40 rows, received {len(rows)}")
    keys = [(row["stage"], row["regime"], int(row["scale"])) for row in rows]
    if frozenset(keys) != EXPECTED_CELL_KEYS or len(set(keys)) != len(keys):
        missing = sorted(EXPECTED_CELL_KEYS - set(keys))
        extra = sorted(set(keys) - EXPECTED_CELL_KEYS)
        raise ValueError(f"frozen 40-cell grid mismatch; missing={missing}, extra={extra}")
    for row in rows:
        stage, regime, scale = row["stage"], row["regime"], int(row["scale"])
        specification = REGIMES[regime]
        if row["experiment_id"] != EXPERIMENT_ID:
            raise ValueError(f"unexpected experiment id in {stage}/{regime}/N{scale}")
        if int(row["regime_id"]) != specification["regime_id"]:
            raise ValueError(f"unexpected regime id in {stage}/{regime}/N{scale}")
        if int(row["seed"]) != _expected_seed(stage, regime, scale):
            raise ValueError(f"unexpected seed in {stage}/{regime}/N{scale}")
        if int(row["repetitions"]) != REPETITIONS_PER_CELL:
            raise ValueError(f"unexpected trajectory count in {stage}/{regime}/N{scale}")
        if int(row["block_count"]) != BLOCK_COUNT or int(row["block_size"]) != BLOCK_SIZE:
            raise ValueError(f"unexpected block design in {stage}/{regime}/N{scale}")
        expected_amplitude = 0.0 if regime == "zero" else AMPLITUDE
        _assert_close(float(row["amplitude"]), expected_amplitude, 1e-15, "amplitude mismatch")
        expected_alpha = specification["alpha"]
        if expected_alpha is None:
            if row["alpha"].strip() not in ("", "nan"):
                raise ValueError("zero-drift alpha field must be blank")
        else:
            _assert_close(float(row["alpha"]), expected_alpha, 1e-15, "alpha mismatch")
        _assert_close(float(row["normalizer"]), _normalizer(regime, scale), 1e-9, "normalizer mismatch")
        if row["normalizer_type"] != specification["normalizer_type"]:
            raise ValueError(f"normalizer type mismatch in {stage}/{regime}/N{scale}")
        _assert_close(
            float(row["normalized_mean"]),
            float(row["mean_tau"]) / float(row["normalizer"]),
            2e-14,
            "normalized mean identity failed",
        )
        center = float(row["normalized_mean"])
        low = float(row["normalized_ci_low"])
        high = float(row["normalized_ci_high"])
        half_width = float(row["normalized_ci_half_width"])
        _assert_close(low, center - half_width, 3e-14, "CI lower identity failed")
        _assert_close(high, center + half_width, 3e-14, "CI upper identity failed")
        if half_width > 0.03:
            raise ValueError(f"prespecified precision gate failed in {stage}/{regime}/N{scale}")
        if not math.isfinite(float(row["relative_interdecile_width"])):
            raise ValueError(f"non-finite relative interdecile width in {stage}/{regime}/N{scale}")
        if any(int(row[name]) != 0 for name in ("censored_count", "nan_count", "excluded_count")):
            raise ValueError(f"censoring, NaN, or exclusion detected in {stage}/{regime}/N{scale}")
        _assert_close(
            float(row["theoretical_exponent"]),
            float(specification["target_exponent"]),
            1e-15,
            "theoretical exponent mismatch",
        )
        expected_raw = f"raw/{stage}__{regime}__N{scale}.npz"
        if Path(row["raw_artifact"]).as_posix() != expected_raw:
            raise ValueError(f"unexpected raw artifact path in {stage}/{regime}/N{scale}")


def _validate_blocks(rows: list[dict[str, str]], cells: list[dict[str, str]]) -> None:
    _require_columns(
        rows,
        {"stage", "regime", "scale", "block", "block_size", "mean_tau", "normalized_mean"},
        "phase-block-means.csv",
    )
    if len(rows) != 40 * BLOCK_COUNT:
        raise ValueError(f"block table must contain 1,600 rows, received {len(rows)}")
    grouped: dict[tuple[str, str, int], list[dict[str, str]]] = {}
    for row in rows:
        key = (row["stage"], row["regime"], int(row["scale"]))
        grouped.setdefault(key, []).append(row)
    if set(grouped) != EXPECTED_CELL_KEYS:
        raise ValueError("block table does not cover the frozen 40-cell grid")
    cell_lookup = {(row["stage"], row["regime"], int(row["scale"])): row for row in cells}
    for key, cell_blocks in grouped.items():
        if {int(row["block"]) for row in cell_blocks} != set(range(BLOCK_COUNT)):
            raise ValueError(f"block indices are incomplete for {key}")
        if {int(row["block_size"]) for row in cell_blocks} != {BLOCK_SIZE}:
            raise ValueError(f"block sizes are inconsistent for {key}")
        block_mean = float(np.mean([float(row["normalized_mean"]) for row in cell_blocks]))
        _assert_close(
            block_mean,
            float(cell_lookup[key]["normalized_mean"]),
            3e-14,
            f"block-to-cell normalized mean mismatch for {key}",
        )


def _validate_kernels(rows: list[dict[str, str]]) -> None:
    _require_columns(
        rows,
        {
            "stage", "regime", "scale", "amplitude", "minimum_probability",
            "probability_sum_error", "reverse_increment_error", "scaled_drift_error",
            "float64_direct_scaled_drift_error", "raw_second_moment_error",
            "covariance_identity_error", "minimum_normal_variance", "initial_scale_error",
            "initial_capacity_error", "deterministic_gate_pass", "seed", "repetitions",
        },
        "phase-kernel-diagnostics.csv",
    )
    keys = [(row["stage"], row["regime"], int(row["scale"])) for row in rows]
    if len(rows) != 40 or frozenset(keys) != EXPECTED_CELL_KEYS or len(set(keys)) != len(keys):
        raise ValueError("kernel diagnostics must contain exactly the frozen 40 cells")
    for row in rows:
        if not _as_bool(row["deterministic_gate_pass"]):
            raise ValueError(f"deterministic kernel gate failed in {row['stage']}/{row['regime']}/N{row['scale']}")
        if float(row["minimum_probability"]) <= 0.0 or float(row["minimum_normal_variance"]) <= 0.0:
            raise ValueError("kernel has a non-positive probability or normal variance")
        for field in (
            "probability_sum_error", "reverse_increment_error", "scaled_drift_error",
            "raw_second_moment_error", "covariance_identity_error", "initial_scale_error",
            "initial_capacity_error",
        ):
            if float(row[field]) > 1e-12:
                raise ValueError(f"deterministic tolerance exceeded for {field}")
        # This field is an explicitly ill-conditioned direct float64 audit, not
        # the frozen gate statistic; require it to remain finite without
        # replacing the long-double contrast gate above.
        if not math.isfinite(float(row["float64_direct_scaled_drift_error"])):
            raise ValueError("non-finite direct float64 drift diagnostic")


def _validate_slopes(adjacent: list[dict[str, str]], final_rows: list[dict[str, str]]) -> None:
    _require_columns(
        adjacent,
        {
            "stage", "regime", "scale_low", "scale_high", "effective_exponent",
            "simultaneous_ci_low", "simultaneous_ci_high", "target_exponent",
            "bootstrap_repetitions", "family_size",
        },
        "phase-adjacent-slopes.csv",
    )
    keys = [
        (row["stage"], row["regime"], int(row["scale_low"]), int(row["scale_high"]))
        for row in adjacent
    ]
    if len(adjacent) != 32 or frozenset(keys) != EXPECTED_ADJACENT_KEYS or len(set(keys)) != len(keys):
        raise ValueError("adjacent-slope table must contain the frozen 32 stage-wise comparisons")
    for row in adjacent:
        values = [
            float(row["effective_exponent"]),
            float(row["simultaneous_ci_low"]),
            float(row["simultaneous_ci_high"]),
        ]
        if not all(math.isfinite(value) for value in values) or not values[1] < values[2]:
            raise ValueError("adjacent-slope table contains an invalid interval")
        if int(row["bootstrap_repetitions"]) != BOOTSTRAP_REPETITIONS or int(row["family_size"]) != 16:
            raise ValueError("adjacent-slope bootstrap design differs from the frozen contract")

    _require_columns(
        final_rows,
        {
            "stage", "regime", "effective_exponent", "simultaneous_ci_low",
            "simultaneous_ci_high", "simultaneous_ci_half_width", "target_exponent",
            "bootstrap_repetitions", "family_size",
        },
        "phase-final-three-slopes.csv",
    )
    final_keys = [(row["stage"], row["regime"]) for row in final_rows]
    expected_final = {(stage, regime) for stage in STAGES for regime in REGIME_ORDER}
    if len(final_rows) != 8 or set(final_keys) != expected_final or len(set(final_keys)) != len(final_keys):
        raise ValueError("final-three-slope table must contain eight stage-wise rows")
    for row in final_rows:
        if int(row["bootstrap_repetitions"]) != BOOTSTRAP_REPETITIONS or int(row["family_size"]) != 4:
            raise ValueError("final-slope bootstrap design differs from the frozen contract")


def _validate_comparisons(rows: list[dict[str, str]]) -> None:
    _require_columns(
        rows,
        {
            "regime", "scale", "normalized_difference_replication_minus_primary",
            "simultaneous_ci_low", "simultaneous_ci_high",
            "simultaneous_ci_contains_zero", "family_size",
        },
        "phase-stage-comparisons.csv",
    )
    keys = {("primary", row["regime"], int(row["scale"])) for row in rows}
    expected = {key for key in EXPECTED_CELL_KEYS if key[0] == "primary"}
    if len(rows) != 20 or keys != expected:
        raise ValueError("stage-comparison table must contain the frozen 20 cells")
    if {int(row["family_size"]) for row in rows} != {20}:
        raise ValueError("stage-comparison family size must equal 20")


def validate_and_load_inputs(paths: Mapping[str, Path]) -> dict[str, Any]:
    """Fail closed on an incomplete, mutated, or off-contract result bundle."""

    normalized = {name: Path(path).resolve() for name, path in paths.items()}
    file_keys = tuple(name for name in normalized if name not in ("data_dir", "raw_dir"))
    missing = [str(normalized[name]) for name in file_keys if not normalized[name].is_file()]
    if not normalized["raw_dir"].is_dir():
        missing.append(str(normalized["raw_dir"]))
    if missing:
        raise FileNotFoundError("phase figure inputs are incomplete: " + ", ".join(missing))

    manifest_entries = _verify_sha256_manifest(normalized["manifest"])
    cells = _load_csv(normalized["cell_csv"])
    blocks = _load_csv(normalized["block_csv"])
    kernels = _load_csv(normalized["kernel_csv"])
    adjacent = _load_csv(normalized["adjacent_csv"])
    final_slopes = _load_csv(normalized["final_slope_csv"])
    comparisons = _load_csv(normalized["comparison_csv"])
    gates = _load_json(normalized["gate_json"])
    metadata = _load_json(normalized["metadata_json"])

    _validate_cells(cells)
    _validate_blocks(blocks, cells)
    _validate_kernels(kernels)
    _validate_slopes(adjacent, final_slopes)
    _validate_comparisons(comparisons)

    expected_raw_paths = {
        normalized["raw_dir"] / f"{stage}__{regime}__N{scale}.npz"
        for stage, regime, scale in EXPECTED_CELL_KEYS
    }
    actual_raw_paths = set(normalized["raw_dir"].glob("*.npz"))
    if actual_raw_paths != expected_raw_paths:
        missing_raw = sorted(str(path) for path in expected_raw_paths - actual_raw_paths)
        extra_raw = sorted(str(path) for path in actual_raw_paths - expected_raw_paths)
        raise ValueError(f"raw cell bundle must contain exactly 40 NPZ files; missing={missing_raw}, extra={extra_raw}")
    cell_lookup = {(row["stage"], row["regime"], int(row["scale"])): row for row in cells}
    for key, row in cell_lookup.items():
        raw_path = normalized["data_dir"] / Path(row["raw_artifact"])
        actual_hash = sha256_file(raw_path)
        if actual_hash != row["raw_result_sha256"]:
            raise ValueError(f"raw-result SHA-256 mismatch for {key}")
        manifest_key = raw_path.relative_to(normalized["data_dir"]).as_posix()
        if manifest_entries.get(manifest_key) != actual_hash:
            raise ValueError(f"raw result is not correctly recorded in SHA256SUMS.txt: {manifest_key}")

    if metadata.get("experiment_id") != EXPERIMENT_ID or metadata.get("pipeline_version") != "1.0":
        raise ValueError("unexpected phase experiment identity or pipeline version")
    if metadata.get("stages") != ["primary", "replication"]:
        raise ValueError("metadata must record primary and replication stages in frozen order")
    if metadata.get("repetitions_per_cell") != REPETITIONS_PER_CELL:
        raise ValueError("metadata trajectory count differs from the frozen contract")
    if metadata.get("block_count") != BLOCK_COUNT or metadata.get("block_size") != BLOCK_SIZE:
        raise ValueError("metadata block design differs from the frozen contract")
    if metadata.get("bootstrap_repetitions") != BOOTSTRAP_REPETITIONS:
        raise ValueError("metadata bootstrap count differs from the frozen contract")
    _assert_close(float(metadata.get("amplitude")), AMPLITUDE, 1e-15, "metadata amplitude mismatch")
    if metadata.get("maximum_steps") is not None:
        raise ValueError("the frozen experiment forbids a maximum-step truncation")
    if metadata.get("censoring_allowed") is not False or metadata.get("exclusions_allowed") is not False:
        raise ValueError("metadata unexpectedly permits censoring or exclusions")
    if gates.get("experiment_id") != EXPERIMENT_ID or not isinstance(gates.get("passed"), bool):
        raise ValueError("invalid prespecified gate report")
    checks = gates.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ValueError("gate report has no checks")
    failed_from_checks = [check.get("name") for check in checks if check.get("pass") is not True]
    if failed_from_checks != gates.get("failed_checks"):
        raise ValueError("gate-report failure list is internally inconsistent")
    if bool(metadata.get("gate_pass")) != bool(gates["passed"]):
        raise ValueError("metadata and gate report disagree")

    return {
        "paths": normalized,
        "manifest_entries": manifest_entries,
        "cells": cells,
        "blocks": blocks,
        "kernels": kernels,
        "adjacent": adjacent,
        "final_slopes": final_slopes,
        "comparisons": comparisons,
        "gates": gates,
        "metadata": metadata,
    }


def _relative(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def build_figure_audit(paths: Mapping[str, Path], loaded: Mapping[str, Any]) -> dict[str, Any]:
    cells = loaded["cells"]
    gates = loaded["gates"]
    comparisons = loaded["comparisons"]
    final_slopes = loaded["final_slopes"]
    project_root = Path(paths["data_dir"]).resolve().parents[1]
    source_keys = (
        "cell_csv", "block_csv", "kernel_csv", "adjacent_csv", "final_slope_csv",
        "comparison_csv", "gate_json", "metadata_json", "manifest",
    )
    all_gray = all(max(style["rgb"]) - min(style["rgb"]) < 1e-15 for style in REGIME_STYLES.values())
    unique_markers = len({style["marker"] for style in REGIME_STYLES.values()}) == len(REGIME_STYLES)
    unique_lines = len({str(style["linestyle"]) for style in REGIME_STYLES.values()}) == len(REGIME_STYLES)
    return {
        "contract_status": "PASS" if gates["passed"] else "FINITE_SCALE_GATE_FAIL",
        "core_conclusion": (
            "A fixed two-triad atomic-routing kernel exhibits the prespecified finite-scale "
            "drift-dominated, critical-diffusion, and fair-diffusion morphology; the numerical "
            "figure checks rather than proves the asymptotic theorem."
        ),
        "archetype": "quantitative grid with one theory-led orientation panel",
        "data_integrity": {
            "pass": True,
            "raw_cell_count": len(list(Path(paths["raw_dir"]).glob("*.npz"))),
            "cell_summary_rows": len(cells),
            "block_rows": len(loaded["blocks"]),
            "kernel_rows": len(loaded["kernels"]),
            "adjacent_slope_rows": len(loaded["adjacent"]),
            "final_slope_rows": len(final_slopes),
            "stage_comparison_rows": len(comparisons),
            "censored_count": sum(int(row["censored_count"]) for row in cells),
            "nan_count": sum(int(row["nan_count"]) for row in cells),
            "excluded_count": sum(int(row["excluded_count"]) for row in cells),
            "sha256_manifest_entries_verified": len(loaded["manifest_entries"]),
        },
        "design": {
            "cell_count": len(cells),
            "stage_count": 2,
            "cells_per_stage": 20,
            "trajectories_per_cell": REPETITIONS_PER_CELL,
            "trajectory_count_total": len(cells) * REPETITIONS_PER_CELL,
            "block_count_per_cell": BLOCK_COUNT,
            "block_size": BLOCK_SIZE,
            "amplitude": AMPLITUDE,
            "maximum_steps": None,
        },
        "statistics": {
            "cell_interval": "20-comparison Bonferroni--Student-t simultaneous 95% interval within each stage, based on 40 non-overlapping block means",
            "adjacent_slope_interval": "stage-wise 16-comparison bootstrap simultaneous 95% interval, 10,000 resamples of block means",
            "stage_comparison": "20-comparison Bonferroni--Welch simultaneous 95% interval for replication minus primary",
            "relative_interdecile_width": "(q90-q10)/(2*q50), trajectory-level quantiles",
            "stages_pooled": False,
        },
        "finite_scale_gates": {
            "pass": bool(gates["passed"]),
            "failed": list(gates["failed_checks"]),
            "independent_stage_intervals_containing_zero": sum(
                _as_bool(row["simultaneous_ci_contains_zero"]) for row in comparisons
            ),
            "maximum_cell_interval_half_width": max(float(row["normalized_ci_half_width"]) for row in cells),
            "maximum_final_slope_interval_half_width": max(
                float(row["simultaneous_ci_half_width"]) for row in final_slopes
            ),
        },
        "figure_export": {
            "backend": "Python/matplotlib",
            "formats": ["PNG"],
            "width_mm": FIGURE_WIDTH_MM,
            "height_mm": FIGURE_HEIGHT_MM,
            "dpi": FIGURE_DPI,
            "white_background": True,
            "black_and_white_discrimination": {
                "all_colors_are_gray": all_gray,
                "four_unique_markers": unique_markers,
                "four_unique_line_styles": unique_lines,
                "stage_encoding": "filled primary markers versus open replication markers",
            },
            "panel_map": {
                "a": "theoretical three-regime partition and asymptotic scale",
                "b": "adjacent-capacity effective exponent with prespecified simultaneous intervals",
                "c": "regime-specific normalized mean with prespecified simultaneous intervals",
                "d": "robust relative interdecile width without inferential interval",
            },
        },
        "source_data": {
            _relative(Path(paths[key]), project_root): sha256_file(Path(paths[key]))
            for key in source_keys
        },
    }


def _configure_matplotlib() -> str:
    installed = {entry.name for entry in font_manager.fontManager.ttflist}
    candidates = ("Microsoft YaHei", "Noto Sans SC", "SimHei", "Noto Sans CJK SC", "Source Han Sans SC")
    font = next((candidate for candidate in candidates if candidate in installed), None)
    if font is None:
        raise RuntimeError("no supported Chinese font is installed")
    mpl.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [font, "Arial", "DejaVu Sans"],
            "mathtext.fontset": "dejavusans",
            "svg.fonttype": "none",
            "pdf.fonttype": 42,
            "axes.unicode_minus": False,
            "font.size": 6.2,
            "axes.titlesize": 6.7,
            "axes.labelsize": 6.2,
            "xtick.labelsize": 5.5,
            "ytick.labelsize": 5.5,
            "axes.linewidth": 0.65,
            "lines.linewidth": 0.9,
            "legend.fontsize": 5.4,
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


def _panel_label(axis: mpl.axes.Axes, label: str) -> None:
    axis.text(-0.12, 1.055, label, transform=axis.transAxes, fontsize=8.0, fontweight="bold", va="bottom")


def _style_axis(axis: mpl.axes.Axes) -> None:
    axis.spines[["top", "right"]].set_visible(False)
    axis.grid(axis="y", color=(0.90, 0.90, 0.90), linewidth=0.45, zorder=0)


def _draw_theory_panel(axis: mpl.axes.Axes) -> None:
    bands = (
        (-0.05, 0.95, (0.95, 0.95, 0.95), "///", "漂移主导", r"$\tau_N=\Theta(N^{1+\alpha})$", r"$\mathrm{Pe}_N\to\infty$"),
        (0.95, 1.05, (0.82, 0.82, 0.82), "...", "临界扩散", r"$\tau_N=\Theta(N^2)$", r"$\mathrm{Pe}_N=O(1)$"),
        (1.05, 2.25, (1.0, 1.0, 1.0), "xxx", "公平扩散", r"$\tau_N=\Theta(N^2)$", r"$\mathrm{Pe}_N\to0$"),
    )
    for left, right, color, hatch, label, scale_text, pe_text in bands:
        axis.add_patch(
            Rectangle(
                (left, 0.12), right - left, 0.70,
                facecolor=color, edgecolor=(0.35, 0.35, 0.35), linewidth=0.6, hatch=hatch,
            )
        )
        center = (left + right) / 2.0
        if right - left < 0.2:
            axis.text(center, 0.47, "临界", ha="center", va="center", fontsize=5.2, rotation=90, fontweight="bold")
        else:
            axis.text(center, 0.66, label, ha="center", va="center", fontweight="bold")
            axis.text(center, 0.44, scale_text, ha="center", va="center", fontsize=5.6)
            axis.text(center, 0.24, pe_text, ha="center", va="center", fontsize=5.4)
    axis.axvline(1.0, color=(0.05, 0.05, 0.05), linewidth=0.8)
    axis.text(0.5, 0.91, r"$\alpha<1$", ha="center", va="center")
    axis.text(1.0, 0.91, r"$\alpha=1$", ha="center", va="center")
    axis.text(1.65, 0.91, r"$\alpha>1$", ha="center", va="center")
    axis.scatter([0.5, 1.0, 2.0], [0.07] * 3, marker="v", s=13, color=(0.05, 0.05, 0.05), clip_on=False)
    axis.text(0.5, 0.0, r"本实验 $\alpha=0.5$", ha="center", va="top", fontsize=5.2)
    axis.text(1.0, 0.0, r"本实验 $\alpha=1$", ha="center", va="top", fontsize=5.2)
    axis.text(2.0, 0.0, r"本实验 $\alpha=2$", ha="center", va="top", fontsize=5.2)
    axis.text(0.50, 1.01, r"有效漂移—扩散比 $\mathrm{Pe}_N=0.8N^{1-\alpha}$", transform=axis.transAxes, ha="center", va="bottom")
    axis.set_xlim(-0.08, 2.28)
    axis.set_ylim(-0.10, 1.06)
    axis.set_xticks([])
    axis.set_yticks([])
    axis.spines[:].set_visible(False)
    axis.set_title("理论三分区与冻结数值网格", y=1.15, pad=0.0)
    _panel_label(axis, "a")


def _group_rows(rows: Iterable[Mapping[str, str]], stage: str, regime: str, x_field: str) -> list[Mapping[str, str]]:
    return sorted(
        (row for row in rows if row["stage"] == stage and row["regime"] == regime),
        key=lambda row: int(row[x_field]),
    )


def _stage_x(values: np.ndarray, stage: str) -> np.ndarray:
    return values * (2.0 ** (-0.025 if stage == "primary" else 0.025))


def _draw_effective_exponent(axis: mpl.axes.Axes, rows: list[Mapping[str, str]]) -> None:
    for regime in REGIME_ORDER:
        style = REGIME_STYLES[regime]
        for stage in STAGES:
            selected = _group_rows(rows, stage, regime, "scale_high")
            x = np.asarray([int(row["scale_high"]) for row in selected], dtype=float)
            y = np.asarray([float(row["effective_exponent"]) for row in selected])
            low = np.asarray([float(row["simultaneous_ci_low"]) for row in selected])
            high = np.asarray([float(row["simultaneous_ci_high"]) for row in selected])
            axis.errorbar(
                _stage_x(x, stage), y, yerr=np.vstack((y - low, high - y)),
                color=style["rgb"], marker=style["marker"],
                linestyle=style["linestyle"] if stage == "primary" else "None",
                markerfacecolor=style["rgb"] if stage == "primary" else "white",
                markeredgecolor=style["rgb"], markeredgewidth=0.7, markersize=3.1,
                capsize=1.5, elinewidth=0.65, zorder=3,
            )
    axis.axhline(1.5, color=(0.20, 0.20, 0.20), linestyle=(0, (4, 2)), linewidth=0.65)
    axis.axhline(2.0, color=(0.20, 0.20, 0.20), linestyle=(0, (1, 2)), linewidth=0.65)
    axis.text(1750, 1.50, "1.5", ha="right", va="bottom", fontsize=5.0)
    axis.text(1750, 2.00, "2", ha="right", va="bottom", fontsize=5.0)
    axis.set_xscale("log", base=2)
    ticks = (25, 50, 100, 200, 400, 800, 1600)
    axis.set_xticks(ticks, [str(value) for value in ticks])
    axis.set_xlim(20, 1900)
    y_values = [float(row["simultaneous_ci_low"]) for row in rows] + [float(row["simultaneous_ci_high"]) for row in rows]
    axis.set_ylim(min(1.25, min(y_values) - 0.04), max(2.13, max(y_values) + 0.04))
    axis.set_xlabel("相邻容量上端 $2N$")
    axis.set_ylabel(r"有效指数 $s_N$")
    axis.set_title("相邻容量有效指数", pad=3.0)
    _style_axis(axis)
    _panel_label(axis, "b")


def _draw_normalized_means(axis: mpl.axes.Axes, rows: list[Mapping[str, str]]) -> None:
    for regime in REGIME_ORDER:
        style = REGIME_STYLES[regime]
        for stage in STAGES:
            selected = _group_rows(rows, stage, regime, "scale")
            x = np.asarray([int(row["scale"]) for row in selected], dtype=float)
            y = np.asarray([float(row["normalized_mean"]) for row in selected])
            low = np.asarray([float(row["normalized_ci_low"]) for row in selected])
            high = np.asarray([float(row["normalized_ci_high"]) for row in selected])
            axis.errorbar(
                _stage_x(x, stage), y, yerr=np.vstack((y - low, high - y)),
                color=style["rgb"], marker=style["marker"],
                linestyle=style["linestyle"] if stage == "primary" else "None",
                markerfacecolor=style["rgb"] if stage == "primary" else "white",
                markeredgecolor=style["rgb"], markeredgewidth=0.7, markersize=3.1,
                capsize=1.5, elinewidth=0.65, zorder=3,
            )
    axis.axhline(1.0, color=(0.25, 0.25, 0.25), linestyle=(0, (3, 2)), linewidth=0.6)
    axis.text(1750, 1.0, "漂移理论中心", ha="right", va="bottom", fontsize=5.0)
    axis.set_xscale("log", base=2)
    ticks = (25, 50, 100, 200, 400, 800, 1600)
    axis.set_xticks(ticks, [str(value) for value in ticks])
    axis.set_xlim(20, 1900)
    lows = [float(row["normalized_ci_low"]) for row in rows]
    highs = [float(row["normalized_ci_high"]) for row in rows]
    axis.set_ylim(max(0.0, min(lows) - 0.06), max(1.06, max(highs) + 0.04))
    axis.set_xlabel("容量尺度 $N$")
    axis.set_ylabel("归一化停止时间均值")
    axis.text(
        0.02, 0.03,
        r"漂移：$\overline{\tau}_N/(1.25N^{1.5})$" + "\n" + r"其余：$\overline{\tau}_N/N^2$",
        transform=axis.transAxes, ha="left", va="bottom", fontsize=5.0,
        bbox={"facecolor": "white", "edgecolor": (0.75, 0.75, 0.75), "linewidth": 0.4, "pad": 1.5},
    )
    axis.set_title("分区归一化均值", pad=3.0)
    _style_axis(axis)
    _panel_label(axis, "c")


def _draw_relative_width(axis: mpl.axes.Axes, rows: list[Mapping[str, str]]) -> None:
    for regime in REGIME_ORDER:
        style = REGIME_STYLES[regime]
        for stage in STAGES:
            selected = _group_rows(rows, stage, regime, "scale")
            x = np.asarray([int(row["scale"]) for row in selected], dtype=float)
            y = np.asarray([float(row["relative_interdecile_width"]) for row in selected])
            axis.plot(
                _stage_x(x, stage), y, color=style["rgb"], marker=style["marker"],
                linestyle=style["linestyle"] if stage == "primary" else "None",
                markerfacecolor=style["rgb"] if stage == "primary" else "white",
                markeredgecolor=style["rgb"], markeredgewidth=0.7, markersize=3.1,
                zorder=3,
            )
    axis.set_xscale("log", base=2)
    ticks = (25, 50, 100, 200, 400, 800, 1600)
    axis.set_xticks(ticks, [str(value) for value in ticks])
    axis.set_xlim(20, 1900)
    values = [float(row["relative_interdecile_width"]) for row in rows]
    axis.set_ylim(0.0, max(values) * 1.16)
    axis.set_xlabel("容量尺度 $N$")
    axis.set_ylabel(r"相对十分位宽 $R_N$")
    axis.text(0.98, 0.94, "扩散区：非退化宽度", transform=axis.transAxes, ha="right", va="top", fontsize=5.0)
    axis.annotate(
        "漂移区：相对集中",
        xy=(1500, min(values)), xytext=(600, max(values) * 0.42),
        arrowprops={"arrowstyle": "->", "linewidth": 0.55, "color": (0.25, 0.25, 0.25)},
        ha="center", va="center", fontsize=5.0,
    )
    axis.set_title("停止时间分布的相对宽度", pad=3.0)
    _style_axis(axis)
    _panel_label(axis, "d")


def render_figure(loaded: Mapping[str, Any], output_path: Path) -> str:
    font = _configure_matplotlib()
    figure = plt.figure(figsize=(FIGURE_WIDTH_MM / 25.4, FIGURE_HEIGHT_MM / 25.4))
    grid = figure.add_gridspec(
        2, 2, left=0.085, right=0.985, top=0.875, bottom=0.155,
        wspace=0.28, hspace=0.39, height_ratios=(0.88, 1.12),
    )
    theory_axis = figure.add_subplot(grid[0, 0])
    exponent_axis = figure.add_subplot(grid[0, 1])
    mean_axis = figure.add_subplot(grid[1, 0])
    width_axis = figure.add_subplot(grid[1, 1])
    _draw_theory_panel(theory_axis)
    _draw_effective_exponent(exponent_axis, loaded["adjacent"])
    _draw_normalized_means(mean_axis, loaded["cells"])
    _draw_relative_width(width_axis, loaded["cells"])

    regime_handles = [
        Line2D(
            [0], [0], color=REGIME_STYLES[key]["rgb"], marker=REGIME_STYLES[key]["marker"],
            linestyle=REGIME_STYLES[key]["linestyle"], markerfacecolor=REGIME_STYLES[key]["rgb"],
            markeredgewidth=0.7, markersize=3.4, label=REGIMES[key]["label"],
        )
        for key in REGIME_ORDER
    ]
    stage_handles = [
        Line2D([0], [0], color=(0.12, 0.12, 0.12), marker="o", linestyle="None", markerfacecolor=(0.12, 0.12, 0.12), markersize=3.4, label="主实验"),
        Line2D([0], [0], color=(0.12, 0.12, 0.12), marker="o", linestyle="None", markerfacecolor="white", markersize=3.4, label="独立种子重复"),
    ]
    figure.legend(regime_handles, [handle.get_label() for handle in regime_handles], loc="upper center", bbox_to_anchor=(0.535, 0.982), ncol=4, columnspacing=1.3, handlelength=2.2)
    figure.legend(stage_handles, [handle.get_label() for handle in stage_handles], loc="upper center", bbox_to_anchor=(0.535, 0.946), ncol=2, columnspacing=1.5, handlelength=1.1)

    gate_label = "全部预声明有限尺度门通过" if loaded["gates"]["passed"] else "存在预声明有限尺度门失败；仅作前渐近观察"
    figure.text(
        0.085, 0.073,
        "每单元 8,000 条独立轨迹、40 个不重叠区块；实心为主实验，空心为独立种子重复；误差线定义见图注。",
        ha="left", va="bottom", fontsize=5.1,
    )
    figure.text(
        0.085, 0.044,
        f"无步数截断、删失或排除；{gate_label}。数值结果只核查固定核的有限尺度形态，不替代理论证明。",
        ha="left", va="bottom", fontsize=5.1,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        output_path, dpi=FIGURE_DPI, facecolor="white", edgecolor="none",
        metadata={
            "Title": "漂移三分区的有限尺度数值核查",
            "Author": "",
            "Description": "Frozen two-stage finite-scale validation; one PNG only.",
            "Software": f"Python/matplotlib; Chinese font={font}",
        },
    )
    plt.close(figure)
    return font


def _png_properties(path: Path) -> dict[str, Any]:
    with path.open("rb") as stream:
        if stream.read(8) != b"\x89PNG\r\n\x1a\n":
            raise ValueError(f"not a PNG file: {path}")
        width = height = None
        pixels_per_meter = None
        while True:
            raw_length = stream.read(4)
            if len(raw_length) != 4:
                break
            length = struct.unpack(">I", raw_length)[0]
            chunk_type = stream.read(4)
            data = stream.read(length)
            stream.read(4)
            if chunk_type == b"IHDR":
                width, height = struct.unpack(">II", data[:8])
            elif chunk_type == b"pHYs" and len(data) == 9:
                x_ppm, y_ppm, unit = struct.unpack(">IIB", data)
                if unit == 1:
                    pixels_per_meter = (x_ppm, y_ppm)
            elif chunk_type == b"IEND":
                break
    if width is None or height is None:
        raise ValueError("PNG has no IHDR dimensions")
    dpi = None
    if pixels_per_meter is not None:
        dpi = tuple(value * 0.0254 for value in pixels_per_meter)
    return {"pixel_width": width, "pixel_height": height, "dpi": dpi, "bytes": path.stat().st_size}


def validate_rendered_png(path: Path) -> dict[str, Any]:
    properties = _png_properties(path)
    expected_width = round(FIGURE_WIDTH_MM / 25.4 * FIGURE_DPI)
    expected_height = round(FIGURE_HEIGHT_MM / 25.4 * FIGURE_DPI)
    checks = {
        "png_signature": True,
        "pixel_width_within_one": abs(properties["pixel_width"] - expected_width) <= 1,
        "pixel_height_within_one": abs(properties["pixel_height"] - expected_height) <= 1,
        "embedded_dpi_within_0.1": properties["dpi"] is not None and all(abs(value - FIGURE_DPI) <= 0.1 for value in properties["dpi"]),
        "nontrivial_file_size": properties["bytes"] > 100_000,
        "grayscale_only_style_contract": all(max(style["rgb"]) - min(style["rgb"]) < 1e-15 for style in REGIME_STYLES.values()),
        "redundant_regime_encodings": len({style["marker"] for style in REGIME_STYLES.values()}) == 4 and len({str(style["linestyle"]) for style in REGIME_STYLES.values()}) == 4,
    }
    result = {"pass": all(checks.values()), "checks": checks, **properties}
    if not result["pass"]:
        raise ValueError(f"rendered PNG QA failed: {result}")
    return result


def build_caption(loaded: Mapping[str, Any]) -> str:
    gate_text = (
        "全部预声明的实现、精度、独立重复与有限尺度形态门均通过。"
        if loaded["gates"]["passed"]
        else "至少一项预声明有限尺度门失败，故图中趋势只能解释为前渐近有限尺度观察。"
    )
    return (
        "**图｜漂移三分区的有限尺度数值核查。** 固定路由核由在节点 2 重叠的两条三元超边组成；"
        "基础核含 20 条等概率有序路由，仅将互逆跨超边路由 0→2→3 与 3→2→0 的概率分别改为 "
        "$0.05+0.40N^{-\\alpha}$ 与 $0.05-0.40N^{-\\alpha}$。"
        "**a，**理论分区由 $\\mathrm{Pe}_N=0.8N^{1-\\alpha}$ 给出：$\\alpha<1$ 为漂移主导、"
        "$\\alpha=1$ 为临界扩散、$\\alpha>1$ 为公平扩散；三组冻结实验取 $\\alpha=0.5,1,2$，"
        "并另设零漂移基线。**b，**相邻容量有效指数 "
        "$s_N=\\log(\\overline\\tau_{2N}/\\overline\\tau_N)/\\log 2$；误差线为以 40 个区块均值为"
        "重采样单位、10,000 次自助法并对每阶段 16 个相邻比较同时校正的 95% 区间。"
        "**c，**漂移组显示 $\\overline\\tau_N/(1.25N^{1.5})$，其余三组显示 "
        "$\\overline\\tau_N/N^2$；误差线为每阶段 20 个均值的 Bonferroni–Student-$t$ 同时 95% 区间。"
        "**d，**稳健相对十分位宽 $R_N=(q_{0.9}-q_{0.1})/(2q_{0.5})$，分位数按逐轨迹停止时间计算，"
        "不另构造推断区间。每个阶段含 20 个单元，每单元 8,000 条独立轨迹、40 个不重叠区块（每块 200 条）；"
        "容量网格为零漂移、临界与公平组 $N=25,50,100,200,400$，漂移组 $N=100,200,400,800,1600$。"
        "实心符号表示主实验，空心符号表示使用不相交随机种子的独立重复；两阶段分别呈现而未合并，阶段差使用 "
        "20 重 Bonferroni–Welch 同时区间核查。模拟无最大步数、无删失、无 NaN、无轨迹排除。"
        f"{gate_text} 本图仅核查一个固定高阶路由核的有限尺度形态，三分区结论由数学定理建立，数值图不替代理论证明。"
    )


def _write_json(path: Path, value: Mapping[str, Any]) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_output_manifest(path: Path, outputs: Iterable[Path]) -> None:
    path.write_text(
        "\n".join(f"{sha256_file(output)}  {output.name}" for output in outputs) + "\n",
        encoding="ascii",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument(
        "--output-dir", type=Path,
        default=Path(__file__).resolve().parent / "outputs" / "researchwrite" / "hypergraph-stopping-time" / "figures",
    )
    parser.add_argument(
        "--require-scientific-gates", action="store_true",
        help="return nonzero after rendering when a prespecified finite-scale scientific gate failed",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    paths = default_input_paths(args.project_root)
    loaded = validate_and_load_inputs(paths)
    audit = build_figure_audit(paths, loaded)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    png_path = output_dir / "fig_phase_scaling_closure.png"
    audit_path = output_dir / "fig_phase_scaling_closure_input_audit.json"
    caption_path = output_dir / "fig_phase_scaling_closure_caption.md"
    manifest_path = output_dir / "fig_phase_scaling_closure_SHA256SUMS.txt"

    # The frozen delivery contract permits one PNG image and no alternate image
    # exports. Refuse a mixed-format bundle instead of silently leaving stale
    # vector or TIFF variants beside the accepted raster.
    alternate_images = [png_path.with_suffix(suffix) for suffix in FORBIDDEN_ALTERNATE_IMAGE_SUFFIXES]
    present_alternates = [str(path) for path in alternate_images if path.exists()]
    if present_alternates:
        raise RuntimeError("PNG-only contract violated by existing alternate images: " + ", ".join(present_alternates))

    audit["figure_export"]["font"] = render_figure(loaded, png_path)
    audit["figure_export"]["render_qa"] = validate_rendered_png(png_path)
    audit["figure_export"]["output_path"] = _relative(png_path, args.project_root.resolve())
    _write_json(audit_path, audit)
    caption_path.write_text(build_caption(loaded) + "\n", encoding="utf-8")
    _write_output_manifest(manifest_path, (png_path, audit_path, caption_path))

    status = "PASS" if loaded["gates"]["passed"] else "PASS_WITH_FINITE_SCALE_GATE_FAILURE"
    print(
        json.dumps(
            {
                "status": status,
                "png": str(png_path),
                "audit": str(audit_path),
                "caption": str(caption_path),
                "manifest": str(manifest_path),
                "raw_cells": 40,
                "scientific_gates_pass": bool(loaded["gates"]["passed"]),
            },
            ensure_ascii=False,
        )
    )
    return int(args.require_scientific_gates and not loaded["gates"]["passed"])


if __name__ == "__main__":
    raise SystemExit(main())
