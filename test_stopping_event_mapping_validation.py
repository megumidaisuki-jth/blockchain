import hashlib
import json
import unittest
from pathlib import Path

from stopping_event_mapping_validation import (
    RESULT_DIR,
    ROUTES,
    boundary_time,
    exhaustive_index_audit,
    first_rejection_time,
    illustrative_cases,
)


class StoppingEventMappingValidationTests(unittest.TestCase):
    def test_depletion_causing_payment_is_accepted_then_next_same_direction_rejects(self):
        sequence = (ROUTES[0], ROUTES[0])
        with self.assertRaises(ValueError):
            boundary_time((0, 1, 1, 1), sequence)
        self.assertEqual(boundary_time((1, 1, 1, 1), sequence), 1)
        self.assertEqual(first_rejection_time((1, 1, 1, 1), sequence), 2)

    def test_policy_can_reject_before_balance_boundary(self):
        sequence = (ROUTES[0], ROUTES[0])
        self.assertEqual(boundary_time((2, 2, 2, 2), sequence), 2)
        self.assertEqual(
            first_rejection_time(
                (2, 2, 2, 2), sequence, disabled_steps=frozenset({1})
            ),
            1,
        )

    def test_reverse_flow_can_restore_a_zero_direction(self):
        sequence = (ROUTES[0], ROUTES[1]) * 4
        self.assertEqual(boundary_time((1, 1, 1, 1), sequence), 1)
        self.assertIsNone(first_rejection_time((1, 1, 1, 1), sequence))

    def test_exhaustive_small_state_indexing_audit(self):
        audit = exhaustive_index_audit(max_scale=2, horizon=5)
        self.assertEqual(audit["violations"], 0)
        self.assertEqual(audit["sequences_checked"], 2 * 6**5)
        self.assertGreater(audit["boundary_hits_observed"], 0)
        self.assertGreater(audit["balance_rejections_observed"], 0)

    def test_published_artifacts_and_hashes(self):
        summary = json.loads((RESULT_DIR / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "PASS")
        self.assertTrue(all(summary["gates"].values()))
        self.assertEqual(len(illustrative_cases()), 3)
        lines = (RESULT_DIR / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        for line in lines:
            expected, name = line.split("  ", 1)
            path = RESULT_DIR / name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
        self.assertFalse(any(Path(RESULT_DIR).glob("*.svg")))
        self.assertFalse(any(Path(RESULT_DIR).glob("*.pdf")))


if __name__ == "__main__":
    unittest.main()
