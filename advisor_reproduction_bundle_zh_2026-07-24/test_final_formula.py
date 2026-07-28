import math
import unittest

from drift_formula_final import predict_stopping_time


class FinalFormulaTests(unittest.TestCase):
    def test_k3_zero_drift_exact(self) -> None:
        for N in (10, 24, 64, 128):
            self.assertAlmostEqual(predict_stopping_time(3, N, 1.0), N * N, places=8)

    def test_rigorous_bounds(self) -> None:
        for k in (3, 4, 10, 25, 50):
            for N in (10, 32, 96, 128):
                for p in (0.30, 0.75, 1.25, 1.90):
                    prediction = predict_stopping_time(k, N, p)
                    self.assertGreaterEqual(prediction, N)
                    if p < 1:
                        upper = k * N / (2 * (1 - p))
                    else:
                        upper = k * (k - 1) * N / (2 * (p - 1))
                    self.assertLessEqual(prediction, upper)

    def test_continuity_near_zero_drift(self) -> None:
        for k in (4, 10, 30, 50):
            for N in (10, 64, 128):
                center = predict_stopping_time(k, N, 1.0)
                left = predict_stopping_time(k, N, 1.0 - 1e-8)
                right = predict_stopping_time(k, N, 1.0 + 1e-8)
                self.assertLess(abs(left / center - 1.0), 1e-5)
                self.assertLess(abs(right / center - 1.0), 1e-5)

    def test_predictions_are_finite(self) -> None:
        for k in range(3, 51):
            for N in (10, 32, 96, 128):
                for p in (0.30, 0.55, 0.95, 1.0, 1.05, 1.55, 1.90):
                    self.assertTrue(math.isfinite(predict_stopping_time(k, N, p)))


if __name__ == "__main__":
    unittest.main()
