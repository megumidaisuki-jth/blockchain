import unittest

import networkx as nx
import numpy as np

from lightning_mapping_simulation import simulate_paired_proxy_compiled
from lightning_current_2026_preflight import plan_formal_repetitions
from lightning_pooled_sensitivity import pooled_block_summary
from lightning_real_topology_comparison import welch_block_comparison
from lightning_real_topology_formal import block_difference_summary
from lightning_real_topology_preflight import summarize_preflight_cell
from lightning_topology_mapping import build_snapshot_kernel
from network_phase_validation import simulate_paired_proxy


class LightningMappingSimulationTests(unittest.TestCase):
    @staticmethod
    def path_kernel():
        graph = nx.path_graph(("a", "b", "c", "d"))
        for index, edge in enumerate(graph.edges):
            graph.edges[edge]["scid"] = str(index)
        return build_snapshot_kernel(graph, demand_kind="uniform")[0]

    def test_compiled_simulator_is_reproducible_and_n1_exact(self):
        kernel = self.path_kernel()
        first = simulate_paired_proxy_compiled(kernel, scale=1, repetitions=100, seed=19)
        second = simulate_paired_proxy_compiled(kernel, scale=1, repetitions=100, seed=19)
        np.testing.assert_array_equal(first.correlated_times, second.correlated_times)
        np.testing.assert_array_equal(first.proxy_times, second.proxy_times)
        np.testing.assert_array_equal(first.correlated_times, np.ones(100, dtype=np.int64))
        self.assertTrue(np.all(first.proxy_times >= 1))

    def test_compiled_marginals_match_reference_simulator(self):
        kernel = self.path_kernel()
        repetitions = 5_000
        compiled = simulate_paired_proxy_compiled(
            kernel, scale=4, repetitions=repetitions, seed=20260722
        )
        reference = simulate_paired_proxy(
            kernel, scale=4, repetitions=repetitions, seed=20260723
        )
        for left, right in (
            (compiled.correlated_times, reference.correlated_times),
            (compiled.proxy_times, reference.proxy_times),
        ):
            combined_se = np.sqrt(
                left.var(ddof=1) / repetitions + right.var(ddof=1) / repetitions
            )
            self.assertLess(abs(left.mean() - right.mean()), 4.0 * combined_se)

    def test_compiled_simulator_rejects_invalid_arguments(self):
        kernel = self.path_kernel()
        for scale, repetitions, seed in ((0, 10, 1), (1, 1, 1), (1, 10, True)):
            with self.assertRaises(ValueError):
                simulate_paired_proxy_compiled(
                    kernel, scale=scale, repetitions=repetitions, seed=seed
                )

    def test_preflight_summary_uses_paired_difference_and_scale(self):
        correlated = np.array([12, 14, 16, 18], dtype=np.int64)
        proxy = np.array([10, 12, 14, 16], dtype=np.int64)
        summary = summarize_preflight_cell(
            correlated, proxy, scale=2, comparisons=1
        )
        self.assertEqual(summary["mean_difference"], 2.0)
        self.assertEqual(summary["normalized_mean_difference"], 0.5)
        self.assertEqual(summary["paired_standard_error"], 0.0)
        self.assertEqual(summary["normalized_ci_low"], 0.5)
        self.assertEqual(summary["normalized_ci_high"], 0.5)
        with self.assertRaises(ValueError):
            summarize_preflight_cell(correlated, proxy[:-1], scale=2)

    def test_formal_block_summary_uses_nonoverlapping_blocks(self):
        correlated = np.array([5, 7, 9, 11, 20, 22, 24, 26], dtype=np.int64)
        proxy = np.array([1, 3, 5, 7, 12, 14, 16, 18], dtype=np.int64)
        blocks, summary = block_difference_summary(
            correlated, proxy, scale=2, block_size=4, comparisons=1
        )
        np.testing.assert_allclose(blocks, np.array([1.0, 2.0]))
        self.assertEqual(summary["block_count"], 2)
        self.assertEqual(summary["block_mean_difference"], 1.5)
        self.assertGreater(summary["block_ci_halfwidth"], 0.0)
        with self.assertRaises(ValueError):
            block_difference_summary(
                correlated, proxy, scale=2, block_size=3, comparisons=1
            )

    def test_replication_comparison_uses_welch_block_interval(self):
        formal = np.array([1.0, 2.0, 3.0, 4.0])
        replication = np.array([1.5, 2.5, 3.5, 4.5])
        summary = welch_block_comparison(formal, replication, comparisons=1)
        self.assertEqual(summary["formal_mean"], 2.5)
        self.assertEqual(summary["replication_mean"], 3.0)
        self.assertEqual(summary["difference_replication_minus_formal"], 0.5)
        self.assertTrue(summary["contains_zero"])
        self.assertGreater(summary["simultaneous_ci_halfwidth"], 0.0)
        identical = welch_block_comparison(
            np.ones(4), np.ones(4), comparisons=1
        )
        self.assertEqual(identical["simultaneous_ci_low"], 0.0)
        self.assertEqual(identical["simultaneous_ci_high"], 0.0)
        with self.assertRaises(ValueError):
            welch_block_comparison(formal, replication[:-1], comparisons=1)

    def test_current_preflight_plan_uses_worst_block_halfwidth(self):
        self.assertEqual(
            plan_formal_repetitions(0.06, pilot_repetitions=2_000), 20_000
        )
        self.assertEqual(
            plan_formal_repetitions(0.12, pilot_repetitions=2_000), 32_000
        )
        with self.assertRaises(ValueError):
            plan_formal_repetitions(0.0, pilot_repetitions=2_000)

    def test_pooled_sensitivity_combines_independent_equal_blocks(self):
        summary = pooled_block_summary(
            np.array([1.0, 2.0]), np.array([3.0, 4.0]), comparisons=1
        )
        self.assertEqual(summary["pooled_block_count"], 4)
        self.assertEqual(summary["pooled_mean_difference"], 2.5)
        self.assertGreater(summary["pooled_ci_halfwidth"], 0.0)
        with self.assertRaises(ValueError):
            pooled_block_summary(
                np.array([1.0, 2.0]), np.array([3.0]), comparisons=1
            )


if __name__ == "__main__":
    unittest.main()
