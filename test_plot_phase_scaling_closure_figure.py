import json
from pathlib import Path
import tempfile
import unittest

from plot_phase_scaling_closure_figure import (
    EXPECTED_ADJACENT_KEYS,
    EXPECTED_CELL_KEYS,
    REGIME_STYLES,
    build_figure_audit,
    default_input_paths,
    validate_and_load_inputs,
)


ROOT = Path(__file__).resolve().parent


class PhaseScalingClosureFigureTests(unittest.TestCase):
    def test_frozen_design_has_40_cells_and_32_adjacent_slopes(self) -> None:
        self.assertEqual(len(EXPECTED_CELL_KEYS), 40)
        self.assertEqual(len(EXPECTED_ADJACENT_KEYS), 32)

    def test_black_and_white_encoding_is_redundant(self) -> None:
        markers = {style["marker"] for style in REGIME_STYLES.values()}
        line_styles = {str(style["linestyle"]) for style in REGIME_STYLES.values()}
        self.assertEqual(len(markers), 4)
        self.assertEqual(len(line_styles), 4)
        for style in REGIME_STYLES.values():
            red, green, blue = style["rgb"]
            self.assertAlmostEqual(red, green)
            self.assertAlmostEqual(green, blue)

    def test_complete_frozen_inputs_pass_the_read_only_audit(self) -> None:
        paths = default_input_paths(ROOT)
        loaded = validate_and_load_inputs(paths)
        audit = build_figure_audit(paths, loaded)

        self.assertTrue(audit["data_integrity"]["pass"])
        self.assertEqual(audit["data_integrity"]["raw_cell_count"], 40)
        self.assertEqual(audit["design"]["cell_count"], 40)
        self.assertEqual(audit["design"]["trajectory_count_total"], 320000)
        self.assertEqual(audit["design"]["block_count_per_cell"], 40)
        self.assertEqual(audit["design"]["block_size"], 200)
        self.assertEqual(audit["figure_export"]["formats"], ["PNG"])

    def test_audit_report_is_json_serializable(self) -> None:
        paths = default_input_paths(ROOT)
        loaded = validate_and_load_inputs(paths)
        audit = build_figure_audit(paths, loaded)

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "audit.json"
            report.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
            restored = json.loads(report.read_text(encoding="utf-8"))
        self.assertTrue(restored["data_integrity"]["pass"])


if __name__ == "__main__":
    unittest.main()
