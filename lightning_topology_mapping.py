"""Map public Lightning topology snapshots to the fixed route-kernel model.

The public snapshots provide topology and routing-policy metadata, not payment
flows or channel balances.  This module therefore builds real-topology,
synthetic-demand kernels only.
"""

from __future__ import annotations

from collections import deque
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Literal

import networkx as nx
import numpy as np

from network_model import HypergraphSpec, NetworkKernel, Route, build_kernel


DemandKind = Literal["uniform", "hotspot"]
AnchorMode = Literal["primary", "hub"]


_COMPRESSED_PUBKEY = re.compile(r"(?:02|03)[0-9a-fA-F]{64}\Z")


def load_snapshot(
    path: str | Path,
    *,
    expected_nodes: int,
    expected_edges: int,
) -> nx.Graph:
    """Load one curated GML snapshot and enforce its declared graph shape."""
    snapshot = Path(path)
    if not snapshot.is_file():
        raise ValueError(f"snapshot does not exist: {snapshot}")
    if type(expected_nodes) is not int or expected_nodes < 2:
        raise ValueError("expected_nodes must be an integer at least two")
    if type(expected_edges) is not int or expected_edges < 1:
        raise ValueError("expected_edges must be a positive integer")

    graph = nx.read_gml(snapshot)
    if graph.is_directed() or graph.is_multigraph():
        raise ValueError("curated snapshot must be a simple undirected graph")
    if graph.number_of_nodes() != expected_nodes or graph.number_of_edges() != expected_edges:
        raise ValueError(
            "declared snapshot shape does not match GML: "
            f"expected ({expected_nodes}, {expected_edges}), got "
            f"({graph.number_of_nodes()}, {graph.number_of_edges()})"
        )
    if nx.number_of_selfloops(graph):
        raise ValueError("snapshot contains self-loops")
    if any(not isinstance(node, str) or not node for node in graph.nodes):
        raise ValueError("snapshot node identifiers must be nonempty strings")
    for _, _, attributes in graph.edges(data=True):
        if "scid" not in attributes:
            raise ValueError("snapshot edge is missing scid")
        maximum = attributes.get("htlc_maximum_msat")
        if isinstance(maximum, str) and maximum.isdecimal():
            maximum = int(maximum)
            attributes["htlc_maximum_msat"] = maximum
        if isinstance(maximum, bool) or not isinstance(maximum, (int, np.integer)) or maximum <= 0:
            raise ValueError("snapshot edge has invalid htlc_maximum_msat")
    return graph


def load_mempool_channels_geo(
    path: str | Path,
    *,
    expected_records: int,
) -> tuple[nx.Graph, dict[str, int]]:
    """Load mempool.space's filtered geolocated channel-pair projection.

    The upstream endpoint groups ordered endpoint columns, so a pair can occur
    once in each orientation.  Exact reversed duplicates are canonicalized to
    one simple undirected edge and counted in returned metadata.
    """
    source = Path(path)
    if not source.is_file():
        raise ValueError(f"mempool projection does not exist: {source}")
    if type(expected_records) is not int or expected_records < 1:
        raise ValueError("expected_records must be a positive integer")
    records = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(records, list) or len(records) != expected_records:
        actual = len(records) if isinstance(records, list) else type(records).__name__
        raise ValueError(
            f"declared mempool record count does not match JSON: "
            f"expected {expected_records}, got {actual}"
        )

    graph = nx.Graph()
    node_attributes: dict[str, tuple[str, float, float]] = {}
    duplicate_count = 0
    for record_index, record in enumerate(records):
        if not isinstance(record, list) or len(record) != 8:
            raise ValueError(f"mempool record {record_index} must contain eight fields")
        endpoints: list[tuple[str, str, float, float]] = []
        for offset in (0, 4):
            public_key, alias, longitude, latitude = record[offset : offset + 4]
            if not isinstance(public_key, str) or not _COMPRESSED_PUBKEY.fullmatch(public_key):
                raise ValueError(f"mempool record {record_index} has invalid public key")
            public_key = public_key.lower()
            if alias is None:
                alias = ""
            if not isinstance(alias, str):
                raise ValueError(f"mempool record {record_index} has invalid node alias")
            if (
                isinstance(longitude, bool)
                or isinstance(latitude, bool)
                or not isinstance(longitude, (int, float))
                or not isinstance(latitude, (int, float))
                or not math.isfinite(float(longitude))
                or not math.isfinite(float(latitude))
                or not -180.0 <= float(longitude) <= 180.0
                or not -90.0 <= float(latitude) <= 90.0
            ):
                raise ValueError(f"mempool record {record_index} has invalid coordinates")
            attributes = (alias, float(longitude), float(latitude))
            if public_key in node_attributes and node_attributes[public_key] != attributes:
                raise ValueError(f"mempool node attributes conflict for {public_key}")
            node_attributes[public_key] = attributes
            endpoints.append((public_key, *attributes))

        left, right = sorted((endpoints[0][0], endpoints[1][0]))
        if left == right:
            raise ValueError(f"mempool record {record_index} contains a self-loop")
        if graph.has_edge(left, right):
            duplicate_count += 1
            continue
        graph.add_edge(left, right, scid=f"mempool:{left}:{right}")

    for public_key, (alias, longitude, latitude) in node_attributes.items():
        graph.add_node(
            public_key, alias=alias, longitude=longitude, latitude=latitude
        )
    components = list(nx.connected_components(graph))
    if not components:
        raise ValueError("mempool projection is empty")
    largest = _largest_component(graph)
    largest_graph = graph.subgraph(largest)
    metadata = {
        "record_count": len(records),
        "unique_undirected_pair_count": graph.number_of_edges(),
        "duplicate_undirected_pair_count": duplicate_count,
        "node_count": graph.number_of_nodes(),
        "edge_count": graph.number_of_edges(),
        "component_count": len(components),
        "largest_component_node_count": largest_graph.number_of_nodes(),
        "largest_component_edge_count": largest_graph.number_of_edges(),
    }
    return graph, metadata


def snapshot_sha256(path: str | Path) -> str:
    """Return the lowercase SHA-256 of a snapshot file."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _largest_component(graph: nx.Graph) -> set[str]:
    components = list(nx.connected_components(graph))
    if not components:
        raise ValueError("snapshot graph is empty")
    return set(min(components, key=lambda part: (-len(part), tuple(sorted(part)))))


def extract_connected_subgraph(
    graph: nx.Graph,
    snapshot_digest: str,
    *,
    mode: AnchorMode,
    node_count: int = 31,
) -> nx.Graph:
    """Select a deterministic connected induced subgraph from the largest component."""
    if graph.is_directed() or graph.is_multigraph():
        raise ValueError("graph must be simple and undirected")
    if type(node_count) is not int or node_count < 2:
        raise ValueError("node_count must be an integer at least two")
    try:
        digest_bytes = bytes.fromhex(snapshot_digest)
    except ValueError as error:
        raise ValueError("snapshot_digest must be a 64-character SHA-256 hex string") from error
    if len(digest_bytes) != 32 or len(snapshot_digest) != 64:
        raise ValueError("snapshot_digest must be a 64-character SHA-256 hex string")
    if mode not in ("primary", "hub"):
        raise ValueError("mode must be 'primary' or 'hub'")

    component_nodes = _largest_component(graph)
    if len(component_nodes) < node_count:
        raise ValueError("largest component is smaller than requested node_count")
    component = graph.subgraph(component_nodes)
    ordered_nodes = tuple(sorted(component.nodes))
    if mode == "primary":
        anchor_digest = hashlib.sha256(digest_bytes + b"primary").digest()
        anchor = ordered_nodes[int.from_bytes(anchor_digest, "big") % len(ordered_nodes)]
    else:
        maximum_degree = max(dict(component.degree()).values())
        anchor = min(node for node, degree in component.degree() if degree == maximum_degree)

    selected: list[str] = []
    seen = {anchor}
    queue = deque([anchor])
    while queue and len(selected) < node_count:
        current = queue.popleft()
        selected.append(current)
        for neighbor in sorted(component.neighbors(current)):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    if len(selected) != node_count:
        raise ValueError("deterministic BFS could not fill the requested subgraph")
    extracted = component.subgraph(selected).copy()
    if not nx.is_connected(extracted):
        raise AssertionError("BFS-induced subgraph must be connected")
    return extracted


def graph_to_hypergraph_spec(graph: nx.Graph) -> tuple[HypergraphSpec, tuple[str, ...]]:
    """Map each simple LN channel to a binary hyperedge with balanced capacity units."""
    if graph.is_directed() or graph.is_multigraph():
        raise ValueError("graph must be simple and undirected")
    if graph.number_of_nodes() < 2 or graph.number_of_edges() < 1:
        raise ValueError("graph must contain at least two nodes and one edge")
    if not nx.is_connected(graph):
        raise ValueError("graph must be connected")
    node_ids = tuple(sorted(graph.nodes))
    if any(not isinstance(node, str) for node in node_ids):
        raise ValueError("graph node identifiers must be strings")
    node_index = {node: index for index, node in enumerate(node_ids)}
    ordered_edges = sorted(
        (
            min(left, right),
            max(left, right),
            str(attributes.get("scid", "")),
        )
        for left, right, attributes in graph.edges(data=True)
    )
    edges = tuple((node_index[left], node_index[right]) for left, right, _ in ordered_edges)
    return HypergraphSpec(edges=edges, capacity_units=(2,) * len(edges)), node_ids


def _ordered_edge_indices(graph: nx.Graph, node_index: dict[str, int]) -> dict[frozenset[str], int]:
    ordered_edges = sorted(
        (
            min(left, right),
            max(left, right),
            str(attributes.get("scid", "")),
        )
        for left, right, attributes in graph.edges(data=True)
    )
    return {
        frozenset((left, right)): edge_index
        for edge_index, (left, right, _) in enumerate(ordered_edges)
    }


def _od_mass(graph: nx.Graph, source: str, target: str, demand_kind: DemandKind) -> float:
    node_count = graph.number_of_nodes()
    uniform = 1.0 / (node_count * (node_count - 1))
    if demand_kind == "uniform":
        return uniform
    degrees = dict(graph.degree())
    denominator = math.fsum(degrees.values()) - degrees[source]
    if denominator <= 0:
        raise ValueError("hotspot demand requires positive non-source degree mass")
    return 0.8 * uniform + 0.2 * degrees[target] / (node_count * denominator)


def _cross_channel_covariance_max(covariance: np.ndarray, edge_count: int) -> float:
    if edge_count < 2:
        return 0.0
    cross = covariance.copy()
    for edge_index in range(edge_count):
        block = slice(2 * edge_index, 2 * edge_index + 2)
        cross[block, block] = 0.0
    return float(np.max(np.abs(cross)))


def build_snapshot_kernel(
    graph: nx.Graph,
    *,
    demand_kind: DemandKind,
) -> tuple[NetworkKernel, dict[str, int | float | str]]:
    """Build an atomic shortest-route kernel for transparent synthetic demand."""
    if demand_kind not in ("uniform", "hotspot"):
        raise ValueError("demand_kind must be 'uniform' or 'hotspot'")
    spec, node_ids = graph_to_hypergraph_spec(graph)
    node_index = {node: index for index, node in enumerate(node_ids)}
    edge_indices = _ordered_edge_indices(graph, node_index)

    routes: list[Route] = []
    probabilities: list[float] = []
    for source in node_ids:
        for target in node_ids:
            if source == target:
                continue
            paths = sorted(tuple(path) for path in nx.all_shortest_paths(graph, source, target))
            pair_mass = _od_mass(graph, source, target, demand_kind)
            route_mass = pair_mass / len(paths)
            for path in paths:
                edges = tuple(
                    edge_indices[frozenset((left, right))]
                    for left, right in zip(path, path[1:])
                )
                routes.append(Route(tuple(node_index[node] for node in path), edges))
                probabilities.append(route_mass)

    probability_vector = np.asarray(probabilities, dtype=np.float64)
    correction = 1.0 - math.fsum(float(value) for value in probability_vector)
    probability_vector[-1] += correction
    kernel = build_kernel(spec, routes, probability_vector)
    route_lengths = np.fromiter((len(route.edges) for route in kernel.routes), dtype=np.int64)
    metadata: dict[str, int | float | str] = {
        "node_count": graph.number_of_nodes(),
        "channel_count": graph.number_of_edges(),
        "route_count": len(kernel.routes),
        "multi_channel_route_count": int(np.count_nonzero(route_lengths > 1)),
        "maximum_route_length": int(route_lengths.max()),
        "demand_kind": demand_kind,
        "probability_sum": float(kernel.probabilities.sum()),
        "maximum_absolute_drift": float(np.max(np.abs(kernel.drift))),
        "cross_channel_covariance_max_abs": _cross_channel_covariance_max(
            kernel.covariance, len(spec.edges)
        ),
    }
    return kernel, metadata


def build_interpolated_snapshot_kernel(
    graph: nx.Graph,
    *,
    hotspot_weight: float,
) -> tuple[NetworkKernel, dict[str, int | float | str]]:
    """Interpolate demand probabilities between uniform and hotspot kernels.

    The route set and every route increment remain fixed. Only route
    probabilities change, which makes the kernel drift affine in
    ``hotspot_weight`` and isolates the demand-imbalance axis.
    """
    if isinstance(hotspot_weight, (bool, np.bool_)) or not isinstance(
        hotspot_weight, (int, float, np.integer, np.floating)
    ):
        raise ValueError("hotspot_weight must be a finite real number in [0, 1]")
    weight = float(hotspot_weight)
    if not math.isfinite(weight) or not 0.0 <= weight <= 1.0:
        raise ValueError("hotspot_weight must be a finite real number in [0, 1]")
    uniform, _ = build_snapshot_kernel(graph, demand_kind="uniform")
    hotspot, _ = build_snapshot_kernel(graph, demand_kind="hotspot")
    if uniform.routes != hotspot.routes or not np.array_equal(
        uniform.increments, hotspot.increments
    ):
        raise AssertionError("uniform and hotspot kernels must share routes and increments")
    probabilities = (1.0 - weight) * uniform.probabilities + weight * hotspot.probabilities
    probabilities[-1] += 1.0 - math.fsum(float(value) for value in probabilities)
    kernel = build_kernel(uniform.spec, uniform.routes, probabilities)
    route_lengths = np.fromiter((len(route.edges) for route in kernel.routes), dtype=np.int64)
    metadata: dict[str, int | float | str] = {
        "node_count": graph.number_of_nodes(), "channel_count": graph.number_of_edges(),
        "route_count": len(kernel.routes), "multi_channel_route_count": int(np.count_nonzero(route_lengths > 1)),
        "maximum_route_length": int(route_lengths.max()), "demand_kind": "interpolated",
        "hotspot_weight": weight, "probability_sum": float(kernel.probabilities.sum()),
        "maximum_absolute_drift": float(np.max(np.abs(kernel.drift))),
        "cross_channel_covariance_max_abs": _cross_channel_covariance_max(kernel.covariance, len(kernel.spec.edges)),
    }
    return kernel, metadata
