import unittest
import numpy as np
from lightning_drift_interpolation_formal import linear_slope_weights, summarize_anchor_slope
from lightning_drift_interpolation_comparison import pooled_summary


class DriftInterpolationTests(unittest.TestCase):
    def test_linear_weights_recover_slope(self):
        x=np.array([0,.25,.5,.75,1.]); w=linear_slope_weights()
        self.assertAlmostEqual(float(w@np.ones(5)),0.0)
        self.assertAlmostEqual(float(w@(2+3*x)),3.0)

    def test_block_slope_summary(self):
        x=np.array([0,.25,.5,.75,1.])[:,None]
        matrix=1+2*x+np.zeros((5,40))
        slopes,summary=summarize_anchor_slope(matrix)
        self.assertTrue(np.allclose(slopes,2.0))
        self.assertAlmostEqual(summary["slope"],2.0)
        self.assertAlmostEqual(summary["slope_ci_halfwidth"],0.0)

    def test_pooled_summary_combines_eighty_blocks(self):
        summary=pooled_summary(np.full(40,-0.1),np.full(40,-0.1))
        self.assertAlmostEqual(summary["pooled_slope"],-0.1)
        self.assertAlmostEqual(summary["pooled_ci_halfwidth"],0.0)
        self.assertTrue(summary["pooled_precision_gate_pass"])


if __name__=="__main__": unittest.main()
