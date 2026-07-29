import json
from pathlib import Path
import tempfile
import unittest

from plot_higher_order_cross_topology import (
    build_input_audit,
    default_input_paths,
    validate_and_load_inputs,
)


ROOT = Path(__file__).resolve().parents[2]


class T18HigherOrderFigureTests(unittest.TestCase):
    def test_frozen_inputs_pass_and_cover_the_full_design(self) -> None:
        paths = default_input_paths(ROOT)
        loaded = validate_and_load_inputs(paths)
        audit = build_input_audit(paths, loaded)

        self.assertEqual(audit["primary_grid"]["row_count"], 36)
        self.assertEqual(audit["primary_grid"]["topologies"], ["chain", "random", "star"])
        self.assertEqual(audit["primary_grid"]["regimes"], ["balanced", "negative", "positive"])
        self.assertEqual(audit["primary_grid"]["scales"], [10, 20, 40, 80])
        self.assertEqual(audit["primary_grid"]["repetitions"], [30000])
        self.assertEqual(audit["primary_grid"]["positive_simultaneous_intervals"], 36)
        self.assertEqual(audit["exact_anchors"]["row_count"], 3)
        self.assertEqual(audit["weakest_cell_sensitivity"]["row_count"], 1)
        self.assertTrue(audit["weakest_cell_sensitivity"]["all_interval_lower_bounds_positive"])
        self.assertFalse(audit["provenance"]["rejected_seed_inputs_used"])

    def test_rejected_seed_path_is_refused_before_reading(self) -> None:
        paths = default_input_paths(ROOT)
        paths["primary_csv"] = ROOT / "results" / "t18-cross-topology-rejected-seed20260718" / "t18-primary-effects.csv"

        with self.assertRaisesRegex(ValueError, "rejected-seed"):
            validate_and_load_inputs(paths)

    def test_audit_report_is_json_serializable(self) -> None:
        paths = default_input_paths(ROOT)
        loaded = validate_and_load_inputs(paths)
        audit = build_input_audit(paths, loaded)

        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "audit.json"
            report.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
            restored = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual(restored["contract_status"], "PASS")


if __name__ == "__main__":
    unittest.main()
