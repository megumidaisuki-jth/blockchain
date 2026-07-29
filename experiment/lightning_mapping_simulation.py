"""Compiled exact-discrete paired simulation for real-topology kernels."""

from __future__ import annotations

from dataclasses import dataclass

from numba import njit
import numpy as np

from network_model import NetworkKernel
from network_phase_validation import block_marginals
from network_simulation import initial_balances


@dataclass(frozen=True)
class CompiledPairedProxySample:
    correlated_times: np.ndarray
    proxy_times: np.ndarray
    seed: int


@njit(cache=True)
def _simulate_compiled(
    starting: np.ndarray,
    route_increments: np.ndarray,
    route_cdf: np.ndarray,
    marginal_increments: np.ndarray,
    marginal_cdfs: np.ndarray,
    marginal_counts: np.ndarray,
    repetitions: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray]:
    np.random.seed(seed)
    coordinate_count = starting.size
    edge_count = marginal_counts.size
    correlated_times = np.zeros(repetitions, dtype=np.int64)
    proxy_times = np.zeros(repetitions, dtype=np.int64)

    for repetition in range(repetitions):
        correlated = starting.copy()
        proxy = starting.copy()
        correlated_active = True
        proxy_active = True
        while correlated_active or proxy_active:
            uniforms = np.random.random(edge_count)
            if correlated_active:
                route_index = np.searchsorted(route_cdf, uniforms[0], side="right")
                for coordinate in range(coordinate_count):
                    correlated[coordinate] += route_increments[route_index, coordinate]
                correlated_times[repetition] += 1
                for coordinate in range(coordinate_count):
                    if correlated[coordinate] == 0:
                        correlated_active = False
                        break

            if proxy_active:
                for edge_index in range(edge_count):
                    choice = 0
                    count = marginal_counts[edge_index]
                    while (
                        choice + 1 < count
                        and uniforms[edge_index] > marginal_cdfs[edge_index, choice]
                    ):
                        choice += 1
                    proxy[2 * edge_index] += marginal_increments[edge_index, choice, 0]
                    proxy[2 * edge_index + 1] += marginal_increments[edge_index, choice, 1]
                proxy_times[repetition] += 1
                for coordinate in range(coordinate_count):
                    if proxy[coordinate] == 0:
                        proxy_active = False
                        break
    return correlated_times, proxy_times


def _dense_marginals(
    kernel: NetworkKernel,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    marginals = block_marginals(kernel)
    maximum_choices = max(len(increments) for increments, _ in marginals)
    edge_count = len(marginals)
    increments = np.zeros((edge_count, maximum_choices, 2), dtype=np.int8)
    cdfs = np.ones((edge_count, maximum_choices), dtype=np.float64)
    counts = np.empty(edge_count, dtype=np.int64)
    for edge_index, (edge_increments, probabilities) in enumerate(marginals):
        count = len(edge_increments)
        counts[edge_index] = count
        increments[edge_index, :count] = edge_increments
        cdf = np.cumsum(probabilities)
        cdf[-1] = 1.0
        cdfs[edge_index, :count] = cdf
    return increments, cdfs, counts


def simulate_paired_proxy_compiled(
    kernel: NetworkKernel,
    *,
    scale: int,
    repetitions: int,
    seed: int,
) -> CompiledPairedProxySample:
    """Simulate exact route and independent-marginal processes in compiled loops.

    Each trajectory consumes one shared vector of uniforms per active time step.
    The first uniform selects the correlated route and each edge-specific uniform
    selects that proxy edge's exact marginal increment.
    """
    if type(scale) is not int or scale <= 0:
        raise ValueError("scale must be a positive integer")
    if type(repetitions) is not int or repetitions <= 1:
        raise ValueError("repetitions must be an integer greater than one")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise ValueError("seed must be an integer")
    if any(len(edge) != 2 for edge in kernel.spec.edges):
        raise ValueError("compiled real-topology simulator requires binary edges")

    starting = initial_balances(kernel, scale).astype(np.int32, copy=False)
    route_cdf = np.cumsum(kernel.probabilities)
    route_cdf[-1] = 1.0
    marginal_increments, marginal_cdfs, marginal_counts = _dense_marginals(kernel)
    correlated_times, proxy_times = _simulate_compiled(
        starting,
        kernel.increments,
        route_cdf,
        marginal_increments,
        marginal_cdfs,
        marginal_counts,
        repetitions,
        seed,
    )
    return CompiledPairedProxySample(correlated_times, proxy_times, seed)
