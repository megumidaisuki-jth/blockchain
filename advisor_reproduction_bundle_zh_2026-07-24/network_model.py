"""Route-correlated increment kernel for fixed hypergraph payment channels."""

from dataclasses import dataclass
import math
from numbers import Real
from typing import Sequence

import numpy as np


@dataclass(frozen=True)
class HypergraphSpec:
    edges: tuple[tuple[int, ...], ...]
    capacity_units: tuple[int, ...]

    def __post_init__(self) -> None:
        if not self.edges:
            raise ValueError("hypergraph must contain at least one edge")
        if len(self.edges) != len(self.capacity_units):
            raise ValueError("edge and capacity counts must match")
        for edge in self.edges:
            if len(set(edge)) < 2:
                raise ValueError("each edge must contain at least two distinct nodes")
            if len(set(edge)) != len(edge):
                raise ValueError("each edge must not contain duplicate participants")
        for capacity in self.capacity_units:
            if type(capacity) is not int or capacity <= 0:
                raise ValueError("each capacity must be a positive Python integer")

    @property
    def coordinates(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (edge_index, node)
            for edge_index, edge in enumerate(self.edges)
            for node in edge
        )

    def edge_slice(self, edge_index: int) -> slice:
        if edge_index < 0 or edge_index >= len(self.edges):
            raise IndexError("hyperedge index out of range")
        start = sum(len(edge) for edge in self.edges[:edge_index])
        return slice(start, start + len(self.edges[edge_index]))


@dataclass(frozen=True)
class Route:
    nodes: tuple[int, ...]
    edges: tuple[int, ...]


@dataclass(frozen=True)
class NetworkKernel:
    spec: HypergraphSpec
    routes: tuple[Route, ...]
    probabilities: np.ndarray
    increments: np.ndarray
    drift: np.ndarray
    covariance: np.ndarray

    def edge_slice(self, edge_index: int) -> slice:
        return self.spec.edge_slice(edge_index)


def _validate_route(spec: HypergraphSpec, route: Route) -> None:
    if not route.edges:
        raise ValueError("route must contain at least one hyperedge")
    if len(route.nodes) != len(route.edges) + 1:
        raise ValueError("route must alternate nodes and hyperedges")
    if len(set(route.nodes)) != len(route.nodes):
        raise ValueError("route repeats a node")
    if len(set(route.edges)) != len(route.edges):
        raise ValueError("route repeats a hyperedge")
    for left, edge_index, right in zip(route.nodes, route.edges, route.nodes[1:]):
        if edge_index < 0 or edge_index >= len(spec.edges):
            raise ValueError("route references an invalid hyperedge")
        if left == right:
            raise ValueError("route hop endpoints must be distinct")
        edge = spec.edges[edge_index]
        if left not in edge or right not in edge:
            raise ValueError("route hop endpoints are not contained in its hyperedge")


def route_increment(spec: HypergraphSpec, route: Route) -> np.ndarray:
    """Return the unit balance-coordinate increment induced by one route."""
    _validate_route(spec, route)
    increment = np.zeros(len(spec.coordinates), dtype=np.int8)
    coordinate_index = {coordinate: index for index, coordinate in enumerate(spec.coordinates)}
    for left, edge_index, right in zip(route.nodes, route.edges, route.nodes[1:]):
        increment[coordinate_index[(edge_index, left)]] -= 1
        increment[coordinate_index[(edge_index, right)]] += 1
    return increment


def build_kernel(
    spec: HypergraphSpec,
    routes: Sequence[Route],
    probabilities: np.ndarray,
) -> NetworkKernel:
    """Build the drift and covariance kernel for a finite route distribution."""
    route_tuple = tuple(routes)
    probability_vector = np.asarray(probabilities, dtype=np.float64)
    if probability_vector.ndim != 1:
        raise ValueError("route probabilities must be one-dimensional")
    if len(probability_vector) != len(route_tuple):
        raise ValueError("route probabilities must match route count")
    if not np.all(np.isfinite(probability_vector)) or np.any(probability_vector <= 0.0):
        raise ValueError("route probabilities must be strictly positive")
    if not np.isclose(probability_vector.sum(), 1.0, rtol=0.0, atol=1e-14):
        raise ValueError("route probabilities must sum to one within 1e-14")
    increments = np.stack([route_increment(spec, route) for route in route_tuple])
    drift = probability_vector @ increments
    centered = increments - drift
    covariance = centered.T @ (centered * probability_vector[:, None])
    return NetworkKernel(
        spec=spec,
        routes=route_tuple,
        probabilities=probability_vector,
        increments=increments,
        drift=drift,
        covariance=covariance,
    )


def perturb_route_probabilities(
    base: NetworkKernel,
    scale: int,
    alpha: float,
    forward_index: int,
    reverse_index: int,
    amplitude: float,
) -> NetworkKernel:
    """Apply an opposite polynomial probability perturbation to two routes."""
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    if isinstance(alpha, (bool, np.bool_)) or not isinstance(alpha, Real):
        raise ValueError("alpha must be finite and nonnegative")
    if not math.isfinite(float(alpha)) or alpha < 0:
        raise ValueError("alpha must be finite and nonnegative")
    if isinstance(amplitude, (bool, np.bool_)) or not isinstance(amplitude, Real):
        raise ValueError("amplitude must be finite and positive")
    if not math.isfinite(float(amplitude)) or amplitude <= 0:
        raise ValueError("amplitude must be finite and positive")
    if (
        isinstance(forward_index, (bool, np.bool_))
        or not isinstance(forward_index, (int, np.integer))
        or isinstance(reverse_index, (bool, np.bool_))
        or not isinstance(reverse_index, (int, np.integer))
    ):
        raise ValueError("route index must be an integer")
    if forward_index == reverse_index:
        raise ValueError("route indices must be distinct")
    if not (0 <= forward_index < len(base.routes)) or not (
        0 <= reverse_index < len(base.routes)
    ):
        raise ValueError("route index is out of range")

    delta = float(amplitude) * scale ** (-float(alpha))
    probabilities = base.probabilities.copy()
    probabilities[forward_index] += delta
    probabilities[reverse_index] -= delta
    if not np.all(np.isfinite(probabilities)) or np.any(probabilities <= 0):
        raise ValueError("perturbation leaves the probability simplex")
    return build_kernel(base.spec, base.routes, probabilities)


def validate_phase_kernel(kernel: NetworkKernel, variance_tolerance: float = 1e-12) -> None:
    """Require every balance coordinate to have non-degenerate normal variance."""
    degenerate = np.flatnonzero(np.diag(kernel.covariance) <= variance_tolerance)
    if len(degenerate):
        coordinates = tuple(kernel.spec.coordinates[index] for index in degenerate)
        raise ValueError(f"normal variance is degenerate for coordinates {coordinates}")


def two_overlapping_triads_uniform() -> NetworkKernel:
    """Return the frozen uniform two-triad route distribution."""
    spec = HypergraphSpec(edges=((0, 1, 2), (2, 3, 4)), capacity_units=(3, 3))
    left, right = {0, 1}, {3, 4}
    routes: list[Route] = []
    for source in range(5):
        for target in range(5):
            if source == target:
                continue
            if source in left and target in right:
                route = Route((source, 2, target), (0, 1))
            elif source in right and target in left:
                route = Route((source, 2, target), (1, 0))
            elif source in spec.edges[0] and target in spec.edges[0]:
                route = Route((source, target), (0,))
            elif source in spec.edges[1] and target in spec.edges[1]:
                route = Route((source, target), (1,))
            else:
                raise AssertionError((source, target))
            routes.append(route)
    return build_kernel(spec, routes, np.full(len(routes), 1.0 / len(routes)))
