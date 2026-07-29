"""Deterministic hypergraph families and shortest-route demand kernels."""

from collections import deque
import math
from numbers import Real
from typing import Mapping

import numpy as np

from network_model import HypergraphSpec, NetworkKernel, Route, build_kernel


def _validate_edge_count(edge_count: int) -> None:
    if not isinstance(edge_count, int) or isinstance(edge_count, bool) or edge_count < 2:
        raise ValueError("edge_count must be an integer at least two")


def overlap_chain_triads(edge_count: int) -> HypergraphSpec:
    """Return triads joined successively through one shared node."""
    _validate_edge_count(edge_count)
    edges = tuple((2 * j, 2 * j + 1, 2 * j + 2) for j in range(edge_count))
    return HypergraphSpec(edges, (3,) * edge_count)


def overlap_star_triads(edge_count: int) -> HypergraphSpec:
    """Return triads sharing one common hub node."""
    _validate_edge_count(edge_count)
    edges = tuple((0, 2 * j + 1, 2 * j + 2) for j in range(edge_count))
    return HypergraphSpec(edges, (3,) * edge_count)


def random_connected_triads(edge_count: int, seed: int) -> HypergraphSpec:
    """Return a seeded connected family grown by one-node triad overlaps."""
    _validate_edge_count(edge_count)
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    rng = np.random.default_rng(seed)
    edges = [(0, 1, 2)]
    existing = [0, 1, 2]
    next_node = 3
    for _ in range(1, edge_count):
        connector = int(rng.choice(existing))
        edges.append((connector, next_node, next_node + 1))
        existing.extend((next_node, next_node + 1))
        next_node += 2
    return HypergraphSpec(tuple(edges), (3,) * edge_count)


def _shortest_routes(spec: HypergraphSpec, source: int, target: int) -> tuple[Route, ...]:
    queue = deque([(source, (source,), ())])
    shortest_depth: int | None = None
    routes: set[Route] = set()
    while queue:
        current, used_nodes, used_edges = queue.popleft()
        if shortest_depth is not None and len(used_edges) >= shortest_depth:
            continue
        for edge_index, edge in enumerate(spec.edges):
            if edge_index in used_edges or current not in edge:
                continue
            for neighbor in sorted(edge):
                if neighbor in used_nodes:
                    continue
                next_nodes = used_nodes + (neighbor,)
                next_edges = used_edges + (edge_index,)
                depth = len(next_edges)
                if neighbor == target:
                    if shortest_depth is None:
                        shortest_depth = depth
                    if depth == shortest_depth:
                        routes.add(Route(next_nodes, next_edges))
                elif shortest_depth is None or depth < shortest_depth:
                    queue.append((neighbor, next_nodes, next_edges))
    if not routes:
        raise ValueError(f"no hypergraph route from {source} to {target}")
    return tuple(sorted(routes, key=lambda route: (route.edges, route.nodes)))


def shortest_route_kernel(
    spec: HypergraphSpec,
    demand: Mapping[tuple[int, int], float] | None = None,
) -> NetworkKernel:
    """Split ordered-pair demand uniformly over all shortest route ties."""
    nodes = tuple(sorted({node for edge in spec.edges for node in edge}))
    node_set = set(nodes)
    if demand is None:
        mass = 1.0 / (len(nodes) * (len(nodes) - 1))
        demand_items = [
            ((source, target), mass)
            for source in nodes
            for target in nodes
            if source != target
        ]
    else:
        if not isinstance(demand, Mapping):
            raise ValueError("demand must be a mapping")
        demand_items = []
        for pair, supplied_mass in demand.items():
            if not isinstance(pair, tuple) or len(pair) != 2:
                raise ValueError("demand keys must be ordered node pairs")
            source, target = pair
            if source not in node_set or target not in node_set:
                raise ValueError("demand references an invalid node")
            if source == target:
                raise ValueError("demand endpoints must be distinct")
            if (
                isinstance(supplied_mass, (bool, np.bool_))
                or not isinstance(supplied_mass, Real)
                or not math.isfinite(float(supplied_mass))
                or supplied_mass <= 0
            ):
                raise ValueError("demand mass must be positive and finite")
            demand_items.append(((source, target), float(supplied_mass)))
        if not math.isclose(
            math.fsum(item[1] for item in demand_items),
            1.0,
            rel_tol=0.0,
            abs_tol=1e-14,
        ):
            raise ValueError("demand mass must sum to one within 1e-14")

    routes: list[Route] = []
    probabilities: list[float] = []
    for (source, target), pair_mass in sorted(demand_items):
        tied_routes = _shortest_routes(spec, source, target)
        routes.extend(tied_routes)
        probabilities.extend([pair_mass / len(tied_routes)] * len(tied_routes))
    return build_kernel(spec, routes, np.asarray(probabilities, dtype=np.float64))
