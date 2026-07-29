from pathlib import Path
import unittest
import warnings

import numpy as np

from network_topologies import overlap_chain_triads, overlap_star_triads, shortest_route_kernel
from higher_order_cross_topology import (
    build_scenarios,
    critical_kernel,
    kernel_diagnostics,
    run_exact_anchors,
    run_t18_validation,
    run_weakest_sensitivity,
    select_reversible_route_pair,
    simulate_paired_proxy_active,
    simultaneous_multiplier,
    summarize_paired_cell,
    summarize_sensitivity,
)


ROOT = Path(__file__).resolve().parents[2]


class T18ScenarioTests(unittest.TestCase):
    def test_reversible_pair_is_longest_and_cancels(self) -> None:
        kernel = shortest_route_kernel(overlap_chain_triads(4))
        forward, reverse = select_reversible_route_pair(kernel)
        self.assertEqual(len(kernel.routes[forward].edges), 4)
        np.testing.assert_array_equal(
            kernel.increments[forward], -kernel.increments[reverse]
        )
        self.assertAlmostEqual(
            float(kernel.probabilities[forward]),
            float(kernel.probabilities[reverse]),
            places=15,
        )

    def test_scenario_grid_has_36_unique_cells(self) -> None:
        scenarios = build_scenarios()
        self.assertEqual(len(scenarios), 36)
        self.assertEqual(len({item.cell_id for item in scenarios}), 36)
        self.assertEqual(
            {item.topology for item in scenarios}, {"chain", "star", "random"}
        )
        self.assertEqual(
            {item.regime for item in scenarios}, {"balanced", "positive", "negative"}
        )
        self.assertEqual({item.scale for item in scenarios}, {10, 20, 40, 80})
        self.assertEqual(len({item.seed for item in scenarios}), 36)

    def test_three_topology_families_have_distinct_intersection_degree_sequences(self) -> None:
        scenarios = build_scenarios()
        specs = {
            name: next(item.kernel.spec for item in scenarios if item.topology == name)
            for name in ("chain", "star", "random")
        }

        def intersection_degrees(spec):
            edge_sets = [set(edge) for edge in spec.edges]
            return sorted(
                sum(bool(edge & other) for j, other in enumerate(edge_sets) if i != j)
                for i, edge in enumerate(edge_sets)
            )

        self.assertEqual(intersection_degrees(specs["chain"]), [1, 1, 2, 2])
        self.assertEqual(intersection_degrees(specs["star"]), [3, 3, 3, 3])
        self.assertEqual(intersection_degrees(specs["random"]), [1, 1, 1, 3])

    def test_critical_kernel_rejects_invalid_sign(self) -> None:
        base = shortest_route_kernel(overlap_star_triads(4))
        with self.assertRaisesRegex(ValueError, "sign"):
            critical_kernel(base, 20, 2, 0.01)

    def test_critical_perturbation_has_exact_drift_and_second_moment(self) -> None:
        base = shortest_route_kernel(overlap_star_triads(4))
        forward, _ = select_reversible_route_pair(base)
        plus = critical_kernel(base, 40, +1, 0.01)
        minus = critical_kernel(base, 40, -1, 0.01)
        expected = 0.02 * base.increments[forward]
        np.testing.assert_allclose(40 * plus.drift, expected, atol=1e-13)
        np.testing.assert_allclose(40 * minus.drift, -expected, atol=1e-13)
        second0 = base.covariance + np.outer(base.drift, base.drift)
        second_plus = plus.covariance + np.outer(plus.drift, plus.drift)
        second_minus = minus.covariance + np.outer(minus.drift, minus.drift)
        np.testing.assert_allclose(second_plus, second0, atol=1e-13)
        np.testing.assert_allclose(second_minus, second0, atol=1e-13)

    def test_kernel_diagnostics_close_all_deterministic_gates(self) -> None:
        for scenario in build_scenarios():
            row = kernel_diagnostics(scenario)
            self.assertLessEqual(row["scaled_drift_error"], 1e-12)
            self.assertLessEqual(row["second_moment_error"], 1e-12)
            self.assertLessEqual(row["covariance_identity_error"], 1e-12)
            self.assertLessEqual(row["proxy_marginal_mean_error"], 1e-12)
            self.assertLessEqual(row["proxy_marginal_covariance_error"], 1e-12)
            self.assertGreater(row["minimum_probability"], 0.0)
            self.assertGreater(row["minimum_normal_variance"], 0.0)


class T18StatisticsTests(unittest.TestCase):
    def test_active_pairing_is_reproducible_and_skips_absorbed_rows(self) -> None:
        kernel = shortest_route_kernel(overlap_chain_triads(4))
        first = simulate_paired_proxy_active(kernel, 10, 2000, seed=9918)
        second = simulate_paired_proxy_active(kernel, 10, 2000, seed=9918)
        np.testing.assert_array_equal(first.correlated_times, second.correlated_times)
        np.testing.assert_array_equal(first.proxy_times, second.proxy_times)
        self.assertLess(first.random_row_count, first.naive_random_row_count)
        self.assertGreater(np.mean(first.correlated_times != first.proxy_times), 0.1)

    def test_active_pairing_n1_stops_all_paths_after_one_step(self) -> None:
        kernel = shortest_route_kernel(overlap_chain_triads(4))
        sample = simulate_paired_proxy_active(kernel, 1, 200, seed=18)
        np.testing.assert_array_equal(sample.correlated_times, np.ones(200, dtype=np.int64))
        self.assertTrue(np.all(sample.proxy_times >= 1))

    def test_paired_summary_uses_declared_simultaneous_multiplier(self) -> None:
        correlated = np.array([12, 14, 16, 18], dtype=np.int64)
        proxy = np.array([10, 11, 15, 16], dtype=np.int64)
        row = summarize_paired_cell(correlated, proxy, scale=2, multiplier=3.0)
        expected = float(np.mean((correlated - proxy) / 4.0))
        self.assertAlmostEqual(row["mean_difference"], expected, places=15)
        self.assertAlmostEqual(
            row["ci_high"] - row["mean_difference"],
            3.0 * row["paired_standard_error"],
            places=15,
        )
        self.assertAlmostEqual(
            row["mean_difference"] - row["ci_low"],
            3.0 * row["paired_standard_error"],
            places=15,
        )

    def test_simultaneous_multiplier_is_more_conservative_than_pointwise(self) -> None:
        self.assertGreater(simultaneous_multiplier(36), 1.959963984540054)

    def test_sensitivity_summary_reports_path_and_block_t_intervals(self) -> None:
        correlated = np.arange(101, 121, dtype=np.int64)
        proxy = np.arange(81, 101, dtype=np.int64)
        row = summarize_sensitivity(correlated, proxy, scale=2, blocks=5)
        self.assertEqual(row["repetitions"], 20)
        self.assertEqual(row["blocks"], 5)
        self.assertAlmostEqual(row["mean_difference"], 5.0, places=15)
        self.assertGreater(row["path_t_ci_low"], 0.0)
        self.assertGreater(row["block_t_ci_low"], 0.0)

    def test_sensitivity_summary_handles_constant_differences_without_warning(self) -> None:
        proxy = np.arange(20, 40, dtype=np.int64)
        correlated = proxy + 8
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            row = summarize_sensitivity(correlated, proxy, scale=2, blocks=5)
        self.assertEqual(caught, [])
        self.assertEqual(row["difference_skewness"], 0.0)
        self.assertEqual(row["difference_excess_kurtosis"], 0.0)

    def test_quick_run_writes_complete_hashed_artifacts(self) -> None:
        output = ROOT / ".tmp" / "t18-cross-topology-test"
        metadata = run_t18_validation(output, quick=True)
        self.assertEqual(metadata["row_counts"]["primary_effects"], 36)
        self.assertEqual(metadata["row_counts"]["kernel_diagnostics"], 36)
        self.assertTrue(metadata["deterministic_gates_pass"])
        self.assertFalse(metadata["precision_gate_applicable"])
        self.assertEqual(metadata["simulation_algorithm"], "active-union paired uniforms")
        self.assertLess(metadata["maximum_random_row_fraction"], 1.0)
        self.assertEqual(len(metadata["files"]), 4)
        self.assertTrue(all(Path(path).exists() for path in metadata["files"]))
        manifest = (output / "SHA256SUMS.txt").read_text(encoding="utf-8")
        self.assertIn("t18-primary-effects.csv", manifest)
        self.assertIn("t18-kernel-diagnostics.csv", manifest)
        self.assertIn("t18-run-metadata.json", manifest)

    def test_weakest_sensitivity_runner_writes_declared_artifacts(self) -> None:
        output = ROOT / ".tmp" / "t18-weakest-sensitivity-test"
        metadata = run_weakest_sensitivity(
            output, repetitions=200, blocks=20, seed=202607189998
        )
        self.assertEqual(metadata["cell_id"], "star-balanced-N80")
        self.assertEqual(metadata["repetitions"], 200)
        self.assertEqual(metadata["blocks"], 20)
        self.assertEqual(len(metadata["files"]), 3)
        self.assertTrue(all(Path(path).exists() for path in metadata["files"]))

    def test_exact_anchor_runner_recovers_n1_identity(self) -> None:
        output = ROOT / ".tmp" / "t18-exact-anchor-test"
        metadata = run_exact_anchors(
            output,
            scale=1,
            repetitions=200,
            topology_names=("chain",),
        )
        self.assertTrue(metadata["all_gates_pass"])
        self.assertEqual(metadata["row_count"], 1)
        self.assertEqual(len(metadata["files"]), 3)


if __name__ == "__main__":
    unittest.main()
