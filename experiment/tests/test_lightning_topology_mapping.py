import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import networkx as nx
import numpy as np

from lightning_topology_mapping import (
    build_snapshot_kernel,
    build_interpolated_snapshot_kernel,
    extract_connected_subgraph,
    graph_to_hypergraph_spec,
    load_mempool_channels_geo,
    load_snapshot,
)


class LightningTopologyMappingTests(unittest.TestCase):
    @staticmethod
    def fixture_graph() -> nx.Graph:
        graph = nx.Graph()
        for node in range(40):
            graph.add_node(f"n{node:02d}")
        for node in range(39):
            graph.add_edge(
                f"n{node:02d}",
                f"n{node + 1:02d}",
                scid=f"{node}x0x0/0",
                htlc_maximum_msat=1_000_000,
            )
        for node in range(1, 40):
            graph.add_edge(
                "n00",
                f"n{node:02d}",
                scid=f"hub-{node}/0",
                htlc_maximum_msat=1_000_000,
            )
        return graph

    def test_load_snapshot_checks_declared_shape(self):
        graph = self.fixture_graph()
        first_edge = next(iter(graph.edges))
        graph.edges[first_edge]["htlc_maximum_msat"] = "9997550000"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.gml"
            nx.write_gml(graph, path)
            loaded = load_snapshot(
                path,
                expected_nodes=graph.number_of_nodes(),
                expected_edges=graph.number_of_edges(),
            )
            self.assertEqual(loaded.number_of_nodes(), 40)
            self.assertEqual(loaded.edges[first_edge]["htlc_maximum_msat"], 9_997_550_000)
            with self.assertRaisesRegex(ValueError, "declared snapshot shape"):
                load_snapshot(path, expected_nodes=39, expected_edges=graph.number_of_edges())

    def test_load_mempool_projection_canonicalizes_reversed_pairs(self):
        a = "02" + "11" * 32
        b = "03" + "22" * 32
        c = "02" + "33" * 32
        rows = [
            [a, "a", 1.0, 2.0, b, "b", 3.0, 4.0],
            [b, "b", 3.0, 4.0, a, "a", 1.0, 2.0],
            [b, "b", 3.0, 4.0, c, "c", 5.0, 6.0],
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "channels-geo.json"
            path.write_text(json.dumps(rows), encoding="utf-8")
            graph, metadata = load_mempool_channels_geo(path, expected_records=3)
            self.assertEqual(graph.number_of_nodes(), 3)
            self.assertEqual(graph.number_of_edges(), 2)
            self.assertEqual(metadata["duplicate_undirected_pair_count"], 1)
            self.assertEqual(metadata["largest_component_node_count"], 3)
            self.assertEqual(graph.edges[a, b]["scid"], f"mempool:{a}:{b}")
            rows[0][0] = "not-a-pubkey"
            path.write_text(json.dumps(rows), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "public key"):
                load_mempool_channels_geo(path, expected_records=3)

    def test_subgraph_selection_is_deterministic_for_fixed_digest(self):
        graph = self.fixture_graph()
        digest = hashlib.sha256(b"fixed snapshot").hexdigest()
        primary = extract_connected_subgraph(graph, digest, mode="primary", node_count=31)
        repeated = extract_connected_subgraph(graph.copy(), digest, mode="primary", node_count=31)
        hub = extract_connected_subgraph(graph, digest, mode="hub", node_count=31)
        self.assertEqual(sorted(primary.nodes), sorted(repeated.nodes))
        self.assertEqual(sorted(primary.edges), sorted(repeated.edges))
        self.assertEqual(primary.number_of_nodes(), 31)
        self.assertTrue(nx.is_connected(primary))
        self.assertIn("n00", hub)
        with self.assertRaisesRegex(ValueError, "mode"):
            extract_connected_subgraph(graph, digest, mode="unknown", node_count=31)

    def test_graph_maps_to_sorted_binary_hyperedges(self):
        graph = nx.Graph()
        graph.add_edge("b", "c", scid="2")
        graph.add_edge("a", "b", scid="1")
        spec, node_ids = graph_to_hypergraph_spec(graph)
        self.assertEqual(node_ids, ("a", "b", "c"))
        self.assertEqual(spec.edges, ((0, 1), (1, 2)))
        self.assertEqual(spec.capacity_units, (2, 2))

    def test_uniform_kernel_is_conservative_and_zero_drift(self):
        graph = nx.cycle_graph(6)
        graph = nx.relabel_nodes(graph, {node: f"n{node}" for node in graph})
        for index, edge in enumerate(graph.edges):
            graph.edges[edge]["scid"] = str(index)
        kernel, metadata = build_snapshot_kernel(graph, demand_kind="uniform")
        self.assertTrue(np.allclose(kernel.increments.sum(axis=1), 0.0))
        self.assertTrue(np.allclose(kernel.drift, 0.0, atol=1e-14, rtol=0.0))
        self.assertAlmostEqual(float(kernel.probabilities.sum()), 1.0, places=14)
        self.assertEqual(metadata["demand_kind"], "uniform")
        self.assertGreater(metadata["multi_channel_route_count"], 0)
        self.assertGreater(metadata["cross_channel_covariance_max_abs"], 0.0)

    def test_hotspot_kernel_is_normalized_and_records_nonzero_drift(self):
        graph = nx.Graph()
        graph.add_edges_from((("a", "b"), ("b", "c"), ("b", "d"), ("d", "e")))
        for index, edge in enumerate(graph.edges):
            graph.edges[edge]["scid"] = str(index)
        kernel, metadata = build_snapshot_kernel(graph, demand_kind="hotspot")
        self.assertAlmostEqual(float(kernel.probabilities.sum()), 1.0, places=14)
        self.assertGreater(float(np.max(np.abs(kernel.drift))), 0.0)
        self.assertEqual(metadata["demand_kind"], "hotspot")
        with self.assertRaisesRegex(ValueError, "demand_kind"):
            build_snapshot_kernel(graph, demand_kind="observed")

    def test_interpolated_kernel_has_fixed_routes_and_affine_drift(self):
        graph = nx.path_graph(("a", "b", "c", "d"))
        for index, edge in enumerate(graph.edges):
            graph.edges[edge]["scid"] = str(index)
        uniform, _ = build_snapshot_kernel(graph, demand_kind="uniform")
        hotspot, _ = build_snapshot_kernel(graph, demand_kind="hotspot")
        middle, metadata = build_interpolated_snapshot_kernel(graph, hotspot_weight=0.25)
        self.assertEqual(middle.routes, uniform.routes)
        self.assertTrue(np.array_equal(middle.increments, uniform.increments))
        self.assertTrue(np.allclose(middle.drift, 0.75 * uniform.drift + 0.25 * hotspot.drift, atol=1e-14, rtol=0.0))
        self.assertAlmostEqual(metadata["hotspot_weight"], 0.25)
        with self.assertRaises(ValueError):
            build_interpolated_snapshot_kernel(graph, hotspot_weight=True)


if __name__ == "__main__":
    unittest.main()
