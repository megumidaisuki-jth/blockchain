from pathlib import Path
import unittest

import numpy as np

from network_model import (
    HypergraphSpec,
    Route,
    build_kernel,
    perturb_route_probabilities,
    two_overlapping_triads_uniform,
    validate_phase_kernel,
)
from network_exact import enumerate_internal_states, solve_exact
from network_phase_validation import block_marginals, simulate_paired_proxy
from network_simulation import simulate_network, summarize_times, validate_initial
from network_topologies import (
    overlap_chain_triads,
    overlap_star_triads,
    random_connected_triads,
    shortest_route_kernel,
)


ROOT = Path(__file__).resolve().parent
PROJECT = ROOT / "outputs" / "researchwrite" / "hypergraph-stopping-time"


class AuthorityDocumentTests(unittest.TestCase):
    def test_contract_has_no_control_characters(self) -> None:
        text = (PROJECT / "12_correlated_hypergraph_network_model_and_theorem_contract.md").read_text(encoding="utf-8")
        bad = [ch for ch in text if ord(ch) < 32 and ch not in "\n\r\t"]
        self.assertEqual(bad, [])
        self.assertIn(r"\Gamma^{1/2}", text)
        self.assertEqual(text.count(r"\frac{\tau_N^{\mathrm{net}}}{N^2}"), 4)

    def test_required_network_references_are_unique(self) -> None:
        bib = (PROJECT / "sources" / "references.bib").read_text(encoding="utf-8")
        for doi in (
            "10.1109/TNSM.2024.3456229",
            "10.1145/3702248",
            "10.1137/15M1010737",
            "10.48550/arXiv.2512.11775",
            "10.48550/arXiv.2601.04835",
        ):
            self.assertEqual(bib.lower().count(doi.lower()), 1, doi)


class NetworkKernelTests(unittest.TestCase):
    def test_hypergraph_spec_rejects_duplicate_participants(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate participants"):
            HypergraphSpec(edges=((0, 0, 1),), capacity_units=(3,))

    def test_two_triad_kernel_matches_frozen_diagnostics(self) -> None:
        kernel = two_overlapping_triads_uniform()
        self.assertEqual(kernel.increments.shape, (20, 6))
        np.testing.assert_allclose(kernel.drift, 0.0, atol=1e-15)
        for edge_index in range(2):
            block = kernel.edge_slice(edge_index)
            np.testing.assert_array_equal(kernel.increments[:, block].sum(axis=1), 0)
        cross = kernel.covariance[kernel.edge_slice(0), kernel.edge_slice(1)]
        self.assertAlmostEqual(float(np.linalg.norm(cross, ord="fro")), 0.6, places=12)
        positive = np.linalg.eigvalsh(kernel.covariance)
        positive = positive[positive > 1e-12]
        np.testing.assert_allclose(positive, [0.3, 0.5, 0.5, 1.5], atol=1e-12)

    def test_reverse_route_cancels_increment(self) -> None:
        kernel = two_overlapping_triads_uniform()
        lookup = {(r.nodes, r.edges): x for r, x in zip(kernel.routes, kernel.increments)}
        for route, increment in zip(kernel.routes, kernel.increments):
            reverse = (tuple(reversed(route.nodes)), tuple(reversed(route.edges)))
            np.testing.assert_array_equal(lookup[reverse], -increment)

    def test_invalid_routes_are_rejected(self) -> None:
        spec = HypergraphSpec(edges=((0, 1, 2), (2, 3, 4)), capacity_units=(3, 3))
        with self.assertRaisesRegex(ValueError, "repeats a hyperedge"):
            build_kernel(spec, (Route((0, 1, 2), (0, 0)),), np.array([1.0]))
        with self.assertRaisesRegex(ValueError, "not contained"):
            build_kernel(spec, (Route((0, 4), (0,)),), np.array([1.0]))
        with self.assertRaisesRegex(ValueError, "sum to one"):
            build_kernel(spec, (Route((0, 1), (0,)),), np.array([0.9]))

    def test_phase_kernel_rejects_degenerate_faces(self) -> None:
        spec = HypergraphSpec(edges=((0, 1, 2),), capacity_units=(3,))
        kernel = build_kernel(
            spec,
            (Route((0, 1), (0,)), Route((1, 0), (0,))),
            np.array([0.5, 0.5]),
        )
        with self.assertRaisesRegex(ValueError, "normal variance"):
            validate_phase_kernel(kernel)

    def test_single_edge_routes_have_zero_cross_covariance(self) -> None:
        spec = HypergraphSpec(edges=((0, 1), (2, 3)), capacity_units=(2, 2))
        routes = (
            Route((0, 1), (0,)), Route((1, 0), (0,)),
            Route((2, 3), (1,)), Route((3, 2), (1,)),
        )
        kernel = build_kernel(spec, routes, np.full(4, 0.25))
        np.testing.assert_allclose(
            kernel.covariance[kernel.edge_slice(0), kernel.edge_slice(1)],
            0.0,
            atol=1e-15,
        )


class ExactNetworkTests(unittest.TestCase):
    def test_product_composition_state_count(self) -> None:
        kernel = two_overlapping_triads_uniform()
        self.assertEqual(len(enumerate_internal_states(kernel.spec, 1)), 1)
        self.assertEqual(len(enumerate_internal_states(kernel.spec, 2)), 100)
        self.assertEqual(len(enumerate_internal_states(kernel.spec, 3)), 784)

    def test_n1_stops_after_one_route(self) -> None:
        result = solve_exact(two_overlapping_triads_uniform(), 1, survival_horizon=3)
        self.assertEqual(result.state_count, 1)
        self.assertAlmostEqual(result.mean, 1.0, places=14)
        np.testing.assert_allclose(result.survival, [1.0, 0.0, 0.0, 0.0])

    def test_exact_survival_obeys_public_probability_invariants(self) -> None:
        result = solve_exact(
            two_overlapping_triads_uniform(), 3, survival_horizon=3
        )
        survival = result.survival
        self.assertTrue(np.isfinite(survival).all())
        self.assertTrue(np.all((0.0 <= survival) & (survival <= 1.0)))
        self.assertTrue(np.all(np.diff(survival) <= 0.0))

        from network_exact import _normalize_survival_probabilities

        invalid_sequences = (
            ("non-finite", [1.0, np.nan], "finite"),
            ("above one", [1.0, 1.0 + 2e-12], "range"),
            ("below zero", [1.0, -2e-12], "range"),
            ("material increase", [0.5, 0.5 + 2e-12], "non-increasing"),
            (
                "cumulative material increase",
                [0.5, 0.5 + 0.75e-12, 0.5 + 1.5e-12],
                "non-increasing",
            ),
        )
        for label, values, message in invalid_sequences:
            with self.subTest(label=label), self.assertRaisesRegex(
                ValueError, message
            ):
                _normalize_survival_probabilities(np.asarray(values))

        np.testing.assert_array_equal(
            _normalize_survival_probabilities(
                np.asarray([0.5, 0.5 + 0.5e-12, 0.5 + 1.0e-12])
            ),
            [0.5, 0.5, 0.5],
        )

    def test_small_network_poisson_residual_and_absorption(self) -> None:
        result = solve_exact(two_overlapping_triads_uniform(), 2, survival_horizon=20)
        self.assertEqual(result.state_count, 100)
        self.assertLess(result.max_abs_residual, 1e-10)
        self.assertTrue(result.all_states_reach_boundary)
        self.assertGreater(result.mean, 1.0)

    def test_single_triad_recovers_known_n_squared_mean(self) -> None:
        spec = HypergraphSpec(edges=((0, 1, 2),), capacity_units=(3,))
        routes = tuple(Route((i, j), (0,)) for i in range(3) for j in range(3) if i != j)
        kernel = build_kernel(spec, routes, np.full(6, 1.0 / 6.0))
        self.assertAlmostEqual(solve_exact(kernel, 2).mean, 4.0, places=12)

    def test_noninternal_initial_state_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "internal state"):
            solve_exact(two_overlapping_triads_uniform(), 2, initial=(0, 3, 3, 2, 2, 2))

    def test_float_initial_coordinates_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "integer|internal state"):
            solve_exact(two_overlapping_triads_uniform(), 1, initial=(1.0,) * 6)

    def test_boolean_initial_coordinates_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "integer|internal state"):
            solve_exact(two_overlapping_triads_uniform(), 1, initial=(True,) * 6)


class NetworkSimulationTests(unittest.TestCase):
    def test_n1_all_trajectories_stop_at_one(self) -> None:
        sample = simulate_network(two_overlapping_triads_uniform(), 1, 200, seed=20260717)
        np.testing.assert_array_equal(sample.stopping_times, np.ones(200, dtype=np.int64))

    def test_seed_is_reproducible(self) -> None:
        kernel = two_overlapping_triads_uniform()
        first = simulate_network(kernel, 2, 500, seed=17)
        second = simulate_network(kernel, 2, 500, seed=17)
        np.testing.assert_array_equal(first.stopping_times, second.stopping_times)
        np.testing.assert_array_equal(first.boundary_coordinates, second.boundary_coordinates)

    def test_mc_interval_covers_n2_exact_mean(self) -> None:
        kernel = two_overlapping_triads_uniform()
        exact = solve_exact(kernel, 2).mean
        summary = summarize_times(simulate_network(kernel, 2, 30000, seed=2026071702).stopping_times)
        self.assertLessEqual(summary.ci_low, exact)
        self.assertGreaterEqual(summary.ci_high, exact)

    def test_nonpositive_initial_balance_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "strictly positive"):
            simulate_network(two_overlapping_triads_uniform(), 2, 20, seed=1, initial=(0, 3, 3, 2, 2, 2))

    def test_noninteger_and_boolean_initial_balances_are_rejected(self) -> None:
        kernel = two_overlapping_triads_uniform()
        with self.assertRaisesRegex(ValueError, "integer"):
            simulate_network(kernel, 1, 20, seed=1, initial=(1.0,) * 6)
        with self.assertRaisesRegex(ValueError, "integer"):
            simulate_network(kernel, 1, 20, seed=1, initial=(True,) * 6)

    def test_nonpositive_or_noninteger_scale_is_rejected(self) -> None:
        kernel = two_overlapping_triads_uniform()
        for scale in (0, -1, 1.5, True):
            with self.subTest(scale=scale), self.assertRaisesRegex(ValueError, "positive integer"):
                simulate_network(kernel, scale, 20, seed=1)

    def test_int32_overflow_is_rejected_before_balances_are_allocated(self) -> None:
        kernel = two_overlapping_triads_uniform()
        overflow_scale = np.iinfo(np.int32).max // 3 + 1
        with self.assertRaisesRegex(ValueError, "int32"):
            simulate_network(kernel, overflow_scale, 20, seed=1)
        with self.assertRaisesRegex(ValueError, "int32"):
            simulate_network(
                kernel,
                overflow_scale,
                20,
                seed=1,
                initial=(overflow_scale,) * 6,
            )

    def test_explicit_initial_values_outside_int32_range_are_rejected_before_conversion(self) -> None:
        kernel = two_overlapping_triads_uniform()
        initial = (2**63 - 1, 2**63 - 1, 5, 2**63 - 1, 2**63 - 1, 5)
        with self.assertRaisesRegex(ValueError, "int32|range"):
            validate_initial(kernel, 1, initial)
        with self.assertRaisesRegex(ValueError, "int32|range"):
            simulate_network(kernel, 1, 20, seed=1, initial=initial)


class NetworkPhaseTests(unittest.TestCase):
    def test_topology_families_are_connected_and_reproducible(self) -> None:
        chain = overlap_chain_triads(3)
        star = overlap_star_triads(3)
        self.assertEqual(chain.edges, ((0, 1, 2), (2, 3, 4), (4, 5, 6)))
        self.assertEqual(star.edges, ((0, 1, 2), (0, 3, 4), (0, 5, 6)))
        self.assertEqual(random_connected_triads(4, seed=7), random_connected_triads(4, seed=7))
        self.assertAlmostEqual(float(shortest_route_kernel(chain).probabilities.sum()), 1.0, places=14)

    def test_polynomial_perturbation_has_declared_drift(self) -> None:
        base = two_overlapping_triads_uniform()
        forward = next(i for i, r in enumerate(base.routes) if r.nodes == (0, 2, 3))
        reverse = next(i for i, r in enumerate(base.routes) if r.nodes == (3, 2, 0))
        perturbed = perturb_route_probabilities(base, 25, 0.5, forward, reverse, amplitude=0.01)
        expected = 2.0 * 0.01 * base.increments[forward] / (25 ** 0.5)
        np.testing.assert_allclose(perturbed.drift, expected, atol=1e-14)

    def test_independent_proxy_preserves_each_edge_marginal(self) -> None:
        kernel = two_overlapping_triads_uniform()
        marginals = block_marginals(kernel)
        for edge_index, (increments, probabilities) in enumerate(marginals):
            block = kernel.edge_slice(edge_index)
            mean = probabilities @ increments
            centered = increments - mean
            covariance = centered.T @ (centered * probabilities[:, None])
            np.testing.assert_allclose(mean, kernel.drift[block], atol=1e-14)
            np.testing.assert_allclose(covariance, kernel.covariance[block, block], atol=1e-14)

    def test_paired_proxy_is_reproducible_and_nonidentical(self) -> None:
        first = simulate_paired_proxy(two_overlapping_triads_uniform(), 10, 2000, seed=7717)
        second = simulate_paired_proxy(two_overlapping_triads_uniform(), 10, 2000, seed=7717)
        np.testing.assert_array_equal(first.correlated_times, second.correlated_times)
        np.testing.assert_array_equal(first.proxy_times, second.proxy_times)
        self.assertGreater(np.mean(first.correlated_times != first.proxy_times), 0.1)

    def test_disconnected_default_demand_is_rejected(self) -> None:
        spec = HypergraphSpec(edges=((0, 1), (2, 3)), capacity_units=(2, 2))
        with self.assertRaisesRegex(ValueError, "no hypergraph route"):
            shortest_route_kernel(spec)

    def test_perturbation_rejects_equal_or_invalid_indices(self) -> None:
        base = two_overlapping_triads_uniform()
        with self.assertRaisesRegex(ValueError, "distinct"):
            perturb_route_probabilities(base, 25, 0.5, 0, 0, amplitude=0.01)
        with self.assertRaisesRegex(ValueError, "index"):
            perturb_route_probabilities(base, 25, 0.5, -1, 2, amplitude=0.01)


class NetworkEvidenceTests(unittest.TestCase):
    def test_quick_run_has_required_metadata(self) -> None:
        from network_phase_validation import run_validation

        output = ROOT / ".tmp" / "network-validation-test"
        metadata = run_validation(output, quick=True)
        self.assertEqual(metadata["model"], "network-first-depletion")
        self.assertEqual(
            metadata["stop_event"], "first balance coordinate equal to zero"
        )
        for key in ("seed", "python", "numpy", "scipy", "config_sha256", "files"):
            self.assertIn(key, metadata)
        self.assertEqual(len(metadata["files"]), 7)
        self.assertTrue(all(Path(path).exists() for path in metadata["files"]))
