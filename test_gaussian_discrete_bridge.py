import csv
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np

from gaussian_discrete_bridge_validation import (
    CORRELATED_MOVES,
    PROXY_MOVES,
    extrapolate_limit,
    independent_brownian_mean,
    move_moments,
    solve_exact_mean,
)


class GaussianDiscreteBridgeTests(unittest.TestCase):
    def test_increment_moments_match_theory(self):
        correlated_mean, correlated_covariance = move_moments(CORRELATED_MOVES)
        proxy_mean, proxy_covariance = move_moments(PROXY_MOVES)
        np.testing.assert_allclose(correlated_mean, np.zeros(2), atol=1e-15)
        np.testing.assert_allclose(proxy_mean, np.zeros(2), atol=1e-15)
        np.testing.assert_allclose(
            correlated_covariance,
            np.array([[2.0 / 3.0, 1.0 / 3.0], [1.0 / 3.0, 2.0 / 3.0]]),
            atol=1e-15,
        )
        np.testing.assert_allclose(proxy_covariance, np.diag([2.0 / 3.0] * 2), atol=1e-15)

    def test_n1_exact_sign_reversal(self):
        correlated, correlated_residual, _, _ = solve_exact_mean(1, CORRELATED_MOVES)
        proxy, proxy_residual, _, _ = solve_exact_mean(1, PROXY_MOVES)
        self.assertAlmostEqual(correlated, 1.0)
        self.assertAlmostEqual(proxy, 9.0 / 8.0)
        self.assertLess(correlated - proxy, 0.0)
        self.assertEqual(correlated_residual, 0.0)
        self.assertEqual(proxy_residual, 0.0)

    def test_n2_difference_is_positive(self):
        correlated, _, _, _ = solve_exact_mean(2, CORRELATED_MOVES)
        proxy, _, _, _ = solve_exact_mean(2, PROXY_MOVES)
        self.assertAlmostEqual(correlated / 4.0, 0.941860465116279, places=14)
        self.assertAlmostEqual(proxy / 4.0, 0.9321428571428572, places=14)

    def test_independent_brownian_series_is_stable(self):
        coarse = independent_brownian_mean(500)
        fine = independent_brownian_mean(1000)
        self.assertLess(abs(fine - coarse), 2e-9)
        self.assertAlmostEqual(fine, 0.8840562391846724, places=12)

    def test_extrapolation_recovers_known_intercept(self):
        scales = np.array([8, 16, 32, 64], dtype=int)
        x = 1.0 / scales.astype(float) ** 2
        values = 0.75 + 2.0 * x - 3.0 * x**2
        limit, _ = extrapolate_limit(scales, values, minimum_scale=8)
        self.assertAlmostEqual(limit, 0.75, places=13)

    def test_published_artifacts_and_manifest_are_consistent(self):
        output = Path(__file__).resolve().parent / "results" / "discrete-gaussian-bridge"
        with (output / "metadata.json").open(encoding="utf-8") as handle:
            metadata = json.load(handle)
        with (output / "discrete-gaussian-bridge-exact.csv").open(
            newline="", encoding="utf-8"
        ) as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 9)
        self.assertEqual(
            [int(row["scale"]) for row in rows],
            [1, 2, 4, 8, 16, 32, 64, 128, 256],
        )
        self.assertTrue(metadata["all_gates_pass"])
        for line in (output / "SHA256SUMS").read_text(encoding="ascii").splitlines():
            expected, name = line.split(None, 1)
            actual = hashlib.sha256((output / name.strip()).read_bytes()).hexdigest()
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
