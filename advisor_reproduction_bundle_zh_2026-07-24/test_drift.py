"""Deterministic tests for the drifted hyperedge formulas."""

import unittest

from drift_experiments import exact_drifted_markov_mean, leading_strong_drift
from run_experiments import exact_closed_form, exact_markov_mean


class DriftFormulaTests(unittest.TestCase):
    def test_zero_bias_reduces_to_uniform_chain(self) -> None:
        for k in (3, 4, 5):
            for N in (2, 3, 5):
                drifted, _, residual = exact_drifted_markov_mean(k, N, 1.0)
                uniform = exact_markov_mean(k, N).mean
                self.assertAlmostEqual(drifted, uniform, places=9)
                self.assertLess(residual, 1e-9)

    def test_k3_zero_bias_recovers_closed_form(self) -> None:
        for N in (1, 2, 4, 8):
            drifted, _, _ = exact_drifted_markov_mean(3, N, 1.0)
            self.assertAlmostEqual(drifted, exact_closed_form(3, (N, N, N)), places=9)

    def test_drift_upper_bounds_hold_for_exact_small_chains(self) -> None:
        for k in (3, 4, 5):
            for N in (2, 4, 6):
                for p_bias in (0.3, 0.6, 1.4, 1.7):
                    exact, _, _ = exact_drifted_markov_mean(k, N, p_bias)
                    self.assertLessEqual(exact, leading_strong_drift(k, N, p_bias) + 1e-9)


if __name__ == "__main__":
    unittest.main()
