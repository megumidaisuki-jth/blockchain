import unittest
import networkx as nx
import numpy as np
from lightning_structural_sign_analysis import exact_sign_flip_pvalue, kernel_structure_metrics
from lightning_topology_mapping import build_snapshot_kernel


class StructuralSignAnalysisTests(unittest.TestCase):
    def test_exact_sign_flip_all_same_sign(self):
        self.assertEqual(exact_sign_flip_pvalue(np.arange(1.0, 9.0)), 2 / 256)

    def test_kernel_metrics_detect_zero_and_nonzero_drift(self):
        graph = nx.path_graph(("a", "b", "c", "d"))
        for index, edge in enumerate(graph.edges): graph.edges[edge]["scid"] = str(index)
        uniform, _ = build_snapshot_kernel(graph, demand_kind="uniform")
        hotspot, _ = build_snapshot_kernel(graph, demand_kind="hotspot")
        uniform_metrics = kernel_structure_metrics(uniform); hotspot_metrics = kernel_structure_metrics(hotspot)
        self.assertLess(uniform_metrics["maximum_absolute_drift"], 1e-14)
        self.assertGreater(hotspot_metrics["maximum_absolute_drift"], 0.0)
        self.assertGreater(uniform_metrics["multi_channel_probability"], 0.0)
        self.assertGreater(uniform_metrics["cross_covariance_frobenius"], 0.0)

    def test_exact_sign_flip_rejects_bad_input(self):
        with self.assertRaises(ValueError): exact_sign_flip_pvalue(np.array([]))


if __name__ == "__main__": unittest.main()
