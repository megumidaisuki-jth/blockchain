from pathlib import Path
import unittest

import numpy as np

from network_model import two_overlapping_triads_uniform
from network_phase_scaling_closure import (
    AMPLITUDE,
    BLOCK_COUNT,
    FULL_REPETITIONS,
    REGIMES,
    build_phase_kernel,
    cell_seed,
    find_reverse_route_pair,
    kernel_diagnostics,
    normalizer,
    simulate_network_chunked,
    summarize_cell,
)
from network_exact import solve_exact


ROOT = Path(__file__).resolve().parent


class FrozenPhaseContractTests(unittest.TestCase):
    def test_contract_exists_and_freezes_amplitude_before_results(self) -> None:
        contract = ROOT / "outputs" / "researchwrite" / "hypergraph-stopping-time" / "41_phase_scaling_and_higher_order_figure_contract_2026-07-28.md"
        text = contract.read_text(encoding="utf-8")
        self.assertIn("a=0.40", text)
        self.assertIn("每单元 8 000 条独立轨迹", text)
        self.assertIn("不设最大步数", text)

    def test_frozen_grid_has_twenty_cells_per_stage(self) -> None:
        self.assertEqual(sum(len(regime.scales) for regime in REGIMES), 20)
        self.assertEqual(FULL_REPETITIONS, 8000)
        self.assertEqual(BLOCK_COUNT, 40)
        self.assertEqual(FULL_REPETITIONS % BLOCK_COUNT, 0)

    def test_route_pair_is_exact_reverse(self) -> None:
        base = two_overlapping_triads_uniform()
        forward, reverse = find_reverse_route_pair(base)
        self.assertEqual(base.routes[forward].nodes, (0, 2, 3))
        self.assertEqual(base.routes[reverse].nodes, (3, 2, 0))
        np.testing.assert_array_equal(base.increments[forward], -base.increments[reverse])

    def test_kernel_contract_is_exact_on_every_frozen_cell(self) -> None:
        for regime in REGIMES:
            for scale in regime.scales:
                with self.subTest(regime=regime.key, scale=scale):
                    kernel = build_phase_kernel(regime, scale)
                    diagnostics = kernel_diagnostics(regime, scale, kernel)
                    self.assertTrue(diagnostics["deterministic_gate_pass"])
                    self.assertLessEqual(diagnostics["probability_sum_error"], 1e-14)
                    self.assertGreater(diagnostics["minimum_probability"], 0.0)
                    if regime.alpha is not None:
                        self.assertLessEqual(diagnostics["scaled_drift_error"], 1e-12)
                        self.assertLessEqual(diagnostics["raw_second_moment_error"], 1e-12)
                        self.assertLessEqual(diagnostics["covariance_identity_error"], 1e-12)

    def test_stage_seeds_are_disjoint_and_deterministic(self) -> None:
        primary = {
            cell_seed(0, regime.regime_id, scale)
            for regime in REGIMES
            for scale in regime.scales
        }
        replication = {
            cell_seed(1, regime.regime_id, scale)
            for regime in REGIMES
            for scale in regime.scales
        }
        self.assertEqual(len(primary), 20)
        self.assertEqual(len(replication), 20)
        self.assertTrue(primary.isdisjoint(replication))

    def test_normalizers_match_theory(self) -> None:
        drift = next(regime for regime in REGIMES if regime.alpha == 0.5)
        critical = next(regime for regime in REGIMES if regime.alpha == 1.0)
        self.assertAlmostEqual(normalizer(drift, 100), 1.25 * 100 ** 1.5)
        self.assertEqual(normalizer(critical, 100), 10000.0)
        self.assertEqual(AMPLITUDE, 0.40)

    def test_cell_summary_uses_nonoverlapping_blocks(self) -> None:
        regime = next(regime for regime in REGIMES if regime.alpha == 1.0)
        values = np.arange(1, 81, dtype=np.int64)
        summary, blocks = summarize_cell(
            regime=regime,
            scale=10,
            stopping_times=values,
            boundary_coordinates=np.zeros_like(values, dtype=np.int32),
            stage="unit-test",
            seed=1,
            block_count=8,
            family_size=1,
        )
        self.assertEqual(len(blocks), 8)
        self.assertEqual(sum(block["block_size"] for block in blocks), 80)
        self.assertAlmostEqual(summary["mean_tau"], 40.5)
        self.assertEqual(summary["censored_count"], 0)

    def test_chunked_simulator_is_reproducible_and_exact_at_n1(self) -> None:
        kernel = two_overlapping_triads_uniform()
        first = simulate_network_chunked(kernel, 1, 500, seed=1728, chunk_steps=17)
        second = simulate_network_chunked(kernel, 1, 500, seed=1728, chunk_steps=17)
        np.testing.assert_array_equal(first.stopping_times, np.ones(500, dtype=np.int64))
        np.testing.assert_array_equal(first.stopping_times, second.stopping_times)
        np.testing.assert_array_equal(first.boundary_coordinates, second.boundary_coordinates)

    def test_chunked_simulator_matches_small_exact_mean(self) -> None:
        kernel = two_overlapping_triads_uniform()
        exact = solve_exact(kernel, 2).mean
        sample = simulate_network_chunked(kernel, 2, 30000, seed=2026072802, chunk_steps=31)
        values = sample.stopping_times.astype(float)
        standard_error = values.std(ddof=1) / np.sqrt(values.size)
        self.assertLessEqual(abs(values.mean() - exact), 4.0 * standard_error)


if __name__ == "__main__":
    unittest.main()
