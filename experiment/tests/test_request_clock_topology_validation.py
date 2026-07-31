import hashlib
import json
import unittest

import numpy as np

from request_clock_topology_validation import (
    FIGURE_PATH,
    HORIZONS,
    RESULT_DIR,
    TOPOLOGY_ORDER,
    build_equal_capital_kernels,
    equal_node_budget_initial,
    ordered_pair_route_groups,
    simulate_matched_request_clock,
    summarize_request_clock_sample,
)


class EqualCapitalDesignTests(unittest.TestCase):
    def test_topologies_match_nodes_capital_and_demand(self):
        kernels = build_equal_capital_kernels()
        self.assertEqual(tuple(kernels), TOPOLOGY_ORDER)
        for kernel in kernels.values():
            nodes = sorted({node for edge in kernel.spec.edges for node in edge})
            self.assertEqual(nodes, list(range(9)))
            self.assertEqual(len(kernel.spec.edges), 4)
            self.assertEqual(sum(kernel.spec.capacity_units), 36)
            self.assertLessEqual(float(np.max(np.abs(kernel.drift))), 1e-14)
            groups = ordered_pair_route_groups(kernel)
            self.assertEqual(len(groups), 72)
            for pair, route_ids in groups.items():
                self.assertNotEqual(pair[0], pair[1])
                pair_mass = float(kernel.probabilities[list(route_ids)].sum())
                self.assertAlmostEqual(pair_mass, 1.0 / 72.0, places=14)

    def test_every_node_locks_exactly_four_scale_units(self):
        scale = 7
        for kernel in build_equal_capital_kernels().values():
            initial = equal_node_budget_initial(kernel, scale)
            node_totals = {node: 0 for node in range(9)}
            for value, (_, node) in zip(initial, kernel.spec.coordinates):
                node_totals[node] += int(value)
            self.assertEqual(set(node_totals.values()), {4 * scale})
            self.assertEqual(int(initial.sum()), 36 * scale)
            for edge_index, capacity in enumerate(kernel.spec.capacity_units):
                self.assertEqual(
                    int(initial[kernel.edge_slice(edge_index)].sum()),
                    scale * capacity,
                )


class RequestClockSimulationTests(unittest.TestCase):
    def test_first_failure_is_strictly_after_first_zero(self):
        sample = simulate_matched_request_clock(
            build_equal_capital_kernels(),
            scale=2,
            repetitions=240,
            seed=314159,
            max_requests=200000,
        )
        for topology in TOPOLOGY_ORDER:
            self.assertTrue(np.all(sample.failure_times[topology] > sample.hit_times[topology]))
            self.assertTrue(np.all(sample.lead_times(topology) >= 1))
        self.assertEqual(sample.censored_count, 0)
        self.assertEqual(sample.indexing_violations, 0)

    def test_simulation_is_reproducible(self):
        kernels = build_equal_capital_kernels()
        first = simulate_matched_request_clock(
            kernels, scale=2, repetitions=120, seed=2718, max_requests=200000
        )
        second = simulate_matched_request_clock(
            kernels, scale=2, repetitions=120, seed=2718, max_requests=200000
        )
        for topology in TOPOLOGY_ORDER:
            np.testing.assert_array_equal(first.hit_times[topology], second.hit_times[topology])
            np.testing.assert_array_equal(
                first.failure_times[topology], second.failure_times[topology]
            )

    def test_warning_probabilities_are_monotone(self):
        sample = simulate_matched_request_clock(
            build_equal_capital_kernels(),
            scale=2,
            repetitions=400,
            seed=1618,
            max_requests=200000,
        )
        summary = summarize_request_clock_sample(sample, scale=2, blocks=20)
        for topology in TOPOLOGY_ORDER:
            probabilities = [
                summary["cells"][topology][f"risk_h{h}"] for h in HORIZONS
            ]
            self.assertTrue(all(0.0 <= value <= 1.0 for value in probabilities))
            self.assertTrue(
                all(left <= right for left, right in zip(probabilities, probabilities[1:]))
            )
            self.assertGreaterEqual(summary["cells"][topology]["lead_mean"], 1.0)


class PublishedArtifactTests(unittest.TestCase):
    def test_published_results_and_png_are_hashed(self):
        metadata = json.loads(
            (RESULT_DIR / "request-clock-metadata.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metadata["status"], "PASS")
        self.assertTrue(all(metadata["gates"].values()))
        self.assertEqual(metadata["design"]["node_count"], 9)
        self.assertEqual(metadata["design"]["per_node_capital_units"], "4*N")
        self.assertTrue(FIGURE_PATH.exists())
        self.assertEqual(FIGURE_PATH.suffix.lower(), ".png")
        lines = (RESULT_DIR / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
        self.assertGreaterEqual(len(lines), 6)
        for line in lines:
            expected, relative = line.split("  ", 1)
            path = RESULT_DIR.parent.parent / relative
            self.assertTrue(path.exists(), relative)
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
        self.assertFalse(any(RESULT_DIR.glob("*.svg")))
        self.assertFalse(any(RESULT_DIR.glob("*.pdf")))


if __name__ == "__main__":
    unittest.main()
