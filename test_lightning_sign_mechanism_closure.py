import hashlib
import json
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from lightning_sign_mechanism_closure import (
    exact_sign_flip_pvalue,
    linear_slope_weights,
    t_summary,
)


ROOT = Path(__file__).resolve().parent
RESULT = ROOT / "results" / "lightning-sign-mechanism-closure"


class SignMechanismClosureTests(unittest.TestCase):
    def test_linear_slope_weights_recover_affine_slope(self):
        weights = np.asarray((0.0, 0.25, 0.5, 0.75, 1.0))
        response = 2.5 - 0.4 * weights
        self.assertAlmostEqual(float(linear_slope_weights() @ response), -0.4)

    def test_t_summary_and_exact_sign_flip_are_deterministic(self):
        summary = t_summary(np.full(8, -0.25), comparisons=4)
        self.assertEqual(summary["n_blocks"], 8)
        self.assertEqual(summary["ci_low"], -0.25)
        self.assertEqual(summary["ci_high"], -0.25)
        self.assertEqual(exact_sign_flip_pvalue(np.arange(1.0, 5.0)), 2 / 16)

    def test_invalid_statistics_inputs_are_rejected(self):
        with self.assertRaises(ValueError):
            t_summary(np.array([1.0]), comparisons=1)
        with self.assertRaises(ValueError):
            exact_sign_flip_pvalue(np.array([]))

    def test_published_artifacts_and_manifest_are_consistent(self):
        metadata = json.loads((RESULT / "metadata.json").read_text(encoding="utf-8"))
        self.assertEqual(metadata["status"], "PASS")
        self.assertTrue(all(metadata["gates"].values()))
        self.assertEqual(metadata["cell_count"], 80)
        self.assertEqual(metadata["block_row_count"], 3200)
        self.assertEqual(metadata["date_cluster_count"], 4)
        self.assertEqual(metadata["negative_date_slope_count"], 4)
        self.assertAlmostEqual(metadata["date_cluster_exact_sign_flip_p_two_sided"], 0.125)
        self.assertTrue(metadata["original_formal_slope_precision_gate_pass"])
        self.assertFalse(metadata["original_replication_slope_precision_gate_pass"])
        lines = (RESULT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 6)
        for line in lines:
            expected, name = line.split("  ", 1)
            self.assertEqual(hashlib.sha256((RESULT / name).read_bytes()).hexdigest(), expected)
        self.assertEqual([path.suffix for path in RESULT.glob("*.png")], [".png"])
        self.assertFalse(any(RESULT.glob("*.svg")))
        self.assertFalse(any(RESULT.glob("*.pdf")))
        self.assertFalse(any(RESULT.glob("*.tif*")))

    def test_raw_checkpoints_reconstruct_all_published_blocks(self):
        maximum_error = 0.0
        for stage in ("formal", "replication"):
            stage_root = ROOT / "results" / f"lightning-drift-interpolation-{stage}"
            cells = pd.read_csv(stage_root / f"drift-interpolation-{stage}.csv")
            published = pd.read_csv(stage_root / f"drift-interpolation-{stage}-blocks.csv")
            published_groups = {
                cell_id: frame.sort_values("block_index")["normalized_mean_difference"].to_numpy(float)
                for cell_id, frame in published.groupby("cell_id", sort=False)
            }
            self.assertEqual(len(cells), 40)
            for row in cells.itertuples(index=False):
                with np.load(stage_root / row.raw_file, allow_pickle=False) as checkpoint:
                    differences = (
                        checkpoint["correlated_times"].astype(float)
                        - checkpoint["proxy_times"].astype(float)
                    ) / (40.0**2)
                reconstructed = differences.reshape(40, 914).mean(axis=1)
                maximum_error = max(
                    maximum_error,
                    float(np.max(np.abs(reconstructed - published_groups[row.cell_id]))),
                )
        self.assertLessEqual(maximum_error, 2e-15)


if __name__ == "__main__":
    unittest.main()
