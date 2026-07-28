"""Deterministic checks for the hyperedge stopping-time implementation."""

import math
import unittest

import numpy as np

from run_experiments import (
    biased_gamblers_ruin_mean,
    bounds,
    exact_closed_form,
    exact_markov_mean,
    positive_compositions,
)


class FormulaTests(unittest.TestCase):
    def test_positive_composition_count(self) -> None:
        for total, parts in ((8, 3), (12, 4), (15, 5)):
            states = list(positive_compositions(total, parts))
            self.assertEqual(len(states), math.comb(total - 1, parts - 1))
            self.assertTrue(all(sum(state) == total for state in states))
            self.assertTrue(all(min(state) >= 1 for state in states))

    def test_closed_forms_are_recovered_by_markov_solver(self) -> None:
        for k in (2, 3):
            for N in (1, 2, 3, 5, 8):
                expected = exact_closed_form(k, (N,) * k)
                actual = exact_markov_mean(k, N)
                self.assertIsNotNone(expected)
                self.assertAlmostEqual(actual.mean, expected, places=10)
                self.assertLess(actual.max_abs_residual, 1e-10)

    def test_biased_formula_satisfies_poisson_recurrence(self) -> None:
        total = 20
        for p_up in (0.3, 0.45, 0.5, 0.7):
            q_down = 1.0 - p_up
            values = [biased_gamblers_ruin_mean(total, x, p_up) for x in range(total + 1)]
            self.assertEqual(values[0], 0.0)
            self.assertEqual(values[-1], 0.0)
            residuals = [
                values[x] - 1.0 - p_up * values[x + 1] - q_down * values[x - 1]
                for x in range(1, total)
            ]
            self.assertLess(float(np.max(np.abs(residuals))), 1e-9)

    def test_closed_forms_obey_rigorous_bounds(self) -> None:
        for k in (2, 3):
            for N in (1, 2, 10, 50):
                lower, upper = bounds(k, N)
                exact = exact_closed_form(k, (N,) * k)
                self.assertIsNotNone(exact)
                self.assertLessEqual(lower, exact)
                self.assertLessEqual(exact, upper)


if __name__ == "__main__":
    unittest.main()
