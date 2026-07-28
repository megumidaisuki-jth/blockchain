"""Reproducible experiments for the first-depletion time of a payment hyperedge.

Model
-----
There are k balances X_i(t) measured in units of a fixed payment amount sigma.
At each discrete transaction an ordered pair (sender, receiver) is sampled
uniformly from the k(k-1) pairs with distinct endpoints, and one unit is moved
from sender to receiver.  The process stops as soon as one balance reaches zero.

This script compares:
  * closed forms for k=2 and k=3;
  * exact finite-state Markov-chain solutions for small k and N;
  * vectorized Monte Carlo estimates with 95% confidence intervals;
  * rigorous potential-function bounds and an exact martingale identity.

All random-number streams are deterministically seeded.
"""

from __future__ import annotations

import argparse
import csv
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"


@dataclass(frozen=True)
class MonteCarloSummary:
    mean: float
    sd: float
    ci_low: float
    ci_high: float
    potential_rhs: float
    martingale_rel_gap: float


@dataclass(frozen=True)
class ExactMarkovResult:
    mean: float
    state_count: int
    lumped_state_count: int
    max_abs_residual: float


def positive_compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    """Yield all ordered positive integer compositions of total into parts."""
    if parts == 1:
        if total >= 1:
            yield (total,)
        return
    for first in range(1, total - parts + 2):
        for tail in positive_compositions(total - first, parts - 1):
            yield (first,) + tail


def exact_closed_form(k: int, initial: Sequence[int]) -> float | None:
    """Closed forms under uniform ordered-pair traffic for k=2 and k=3."""
    if any(x <= 0 for x in initial):
        return 0.0
    if k == 2:
        return float(initial[0] * initial[1])
    if k == 3:
        total = sum(initial)
        return float(3 * initial[0] * initial[1] * initial[2] / total)
    return None


def biased_gamblers_ruin_mean(total: int, start: int, p_up: float) -> float:
    """Exact k=2 mean exit time when X_1 rises with probability p_up."""
    if not 0 <= start <= total:
        raise ValueError("start must lie in [0,total]")
    if not 0.0 < p_up < 1.0:
        raise ValueError("p_up must lie in (0,1)")
    if start in (0, total):
        return 0.0
    q_down = 1.0 - p_up
    if math.isclose(p_up, q_down, rel_tol=0.0, abs_tol=1e-14):
        return float(start * (total - start))
    ratio = q_down / p_up
    return float(
        start / (q_down - p_up)
        - total
        / (q_down - p_up)
        * (1.0 - ratio**start)
        / (1.0 - ratio**total)
    )


def exact_markov_mean(k: int, N: int) -> ExactMarkovResult:
    """Solve (I-Q)u=1 on exact permutation-symmetry classes.

    Uniform traffic makes the chain strongly lumpable under permutations of
    participant labels.  Solving on sorted balance vectors is therefore exact,
    while being much smaller than the full composition state space.
    """
    total = k * N
    states = sorted({tuple(sorted(state)) for state in positive_compositions(total, k)})
    index = {state: idx for idx, state in enumerate(states)}
    probability = 1.0 / (k * (k - 1))
    rows: list[int] = []
    cols: list[int] = []
    values: list[float] = []

    for row, state in enumerate(states):
        rows.append(row)
        cols.append(row)
        values.append(1.0)
        for sender in range(k):
            if state[sender] == 1:
                # This transition reaches the absorbing boundary, where u=0.
                continue
            for receiver in range(k):
                if sender == receiver:
                    continue
                nxt = list(state)
                nxt[sender] -= 1
                nxt[receiver] += 1
                nxt.sort()
                rows.append(row)
                cols.append(index[tuple(nxt)])
                values.append(-probability)

    matrix = coo_matrix((values, (rows, cols)), shape=(len(states), len(states))).tocsr()
    rhs = np.ones(len(states), dtype=np.float64)
    solution = spsolve(matrix, rhs)
    residual = matrix @ solution - rhs
    equal_state = (N,) * k
    return ExactMarkovResult(
        mean=float(solution[index[equal_state]]),
        state_count=math.comb(total - 1, k - 1),
        lumped_state_count=len(states),
        max_abs_residual=float(np.max(np.abs(residual))),
    )


def simulate_uniform_hyperedge(
    k: int, N: int, repetitions: int, seed: int
) -> tuple[np.ndarray, np.ndarray]:
    """Vectorized simulation; returns stopping times and terminal balances."""
    rng = np.random.default_rng(seed)
    balances = np.full((repetitions, k), N, dtype=np.int32)
    stopping_times = np.zeros(repetitions, dtype=np.int32)
    active = np.arange(repetitions, dtype=np.int64)

    while active.size:
        count = active.size
        sender = rng.integers(0, k, size=count)
        receiver_raw = rng.integers(0, k - 1, size=count)
        receiver = receiver_raw + (receiver_raw >= sender)

        balances[active, sender] -= 1
        balances[active, receiver] += 1
        stopping_times[active] += 1

        depleted = balances[active, sender] == 0
        active = active[~depleted]

    return stopping_times, balances


def simulate_biased_k2(
    total: int, start: int, p_up: float, repetitions: int, seed: int
) -> np.ndarray:
    rng = np.random.default_rng(seed)
    positions = np.full(repetitions, start, dtype=np.int32)
    stopping_times = np.zeros(repetitions, dtype=np.int32)
    active = np.arange(repetitions, dtype=np.int64)
    while active.size:
        steps = np.where(rng.random(active.size) < p_up, 1, -1)
        positions[active] += steps
        stopping_times[active] += 1
        absorbed = (positions[active] == 0) | (positions[active] == total)
        active = active[~absorbed]
    return stopping_times


def summarize_uniform(
    times: np.ndarray, terminal_balances: np.ndarray, N: int
) -> MonteCarloSummary:
    sample = times.astype(np.float64)
    mean = float(np.mean(sample))
    sd = float(np.std(sample, ddof=1))
    half_width = 1.959963984540054 * sd / math.sqrt(sample.size)
    deviations = terminal_balances.astype(np.float64) - N
    terminal_potential = np.sum(deviations * deviations, axis=1)
    potential_rhs = float(np.mean(terminal_potential) / 2.0)
    martingale_rel_gap = abs(mean - potential_rhs) / mean
    return MonteCarloSummary(
        mean=mean,
        sd=sd,
        ci_low=mean - half_width,
        ci_high=mean + half_width,
        potential_rhs=potential_rhs,
        martingale_rel_gap=martingale_rel_gap,
    )


def summarize_times(times: np.ndarray) -> tuple[float, float, float, float]:
    sample = times.astype(np.float64)
    mean = float(np.mean(sample))
    sd = float(np.std(sample, ddof=1))
    half_width = 1.959963984540054 * sd / math.sqrt(sample.size)
    return mean, sd, mean - half_width, mean + half_width


def bounds(k: int, N: int) -> tuple[float, float]:
    lower = k * N * N / (2.0 * (k - 1))
    upper = k * (k - 1) * N * N / 2.0
    return lower, upper


def deterministic_seed(k: int, N: int, tag: int) -> int:
    return 20260715 + 1_000_003 * tag + 10_007 * k + 101 * N


def write_csv(path: Path, rows: Iterable[dict], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def configure_plots() -> None:
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 220,
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "legend.fontsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
        }
    )


def run_closed_form_validation(repetitions: int) -> list[dict]:
    rows: list[dict] = []
    for k in (2, 3):
        for N in (2, 3, 5, 8, 12, 20, 30):
            times, terminal = simulate_uniform_hyperedge(
                k, N, repetitions, deterministic_seed(k, N, 1)
            )
            summary = summarize_uniform(times, terminal, N)
            exact = exact_closed_form(k, (N,) * k)
            lower, upper = bounds(k, N)
            assert exact is not None
            rows.append(
                {
                    "experiment": "closed_form",
                    "k": k,
                    "N": N,
                    "repetitions": repetitions,
                    "mc_mean": summary.mean,
                    "mc_sd": summary.sd,
                    "ci_low": summary.ci_low,
                    "ci_high": summary.ci_high,
                    "exact_mean": exact,
                    "relative_error": abs(summary.mean - exact) / exact,
                    "lower_bound": lower,
                    "upper_bound": upper,
                    "potential_rhs": summary.potential_rhs,
                    "martingale_rel_gap": summary.martingale_rel_gap,
                    "state_count": "",
                    "lumped_state_count": "",
                    "linear_residual": "",
                }
            )
    return rows


def run_biased_k2_validation(repetitions: int) -> list[dict]:
    rows: list[dict] = []
    total = 40
    start = 20
    for p_up in (0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65):
        times = simulate_biased_k2(
            total,
            start,
            p_up,
            repetitions,
            deterministic_seed(2, int(round(p_up * 100)), 2),
        )
        mean, sd, ci_low, ci_high = summarize_times(times)
        exact = biased_gamblers_ruin_mean(total, start, p_up)
        rows.append(
            {
                "p_up": p_up,
                "total_units": total,
                "start_units": start,
                "repetitions": repetitions,
                "mc_mean": mean,
                "mc_sd": sd,
                "ci_low": ci_low,
                "ci_high": ci_high,
                "exact_mean": exact,
                "relative_error": abs(mean - exact) / exact,
            }
        )
    return rows


def run_markov_validation(repetitions: int) -> list[dict]:
    grid = {4: (2, 3, 4, 5, 6, 8, 10), 5: (2, 3, 4, 5, 6), 6: (2, 3, 4)}
    rows: list[dict] = []
    for k, values in grid.items():
        for N in values:
            exact = exact_markov_mean(k, N)
            times, terminal = simulate_uniform_hyperedge(
                k, N, repetitions, deterministic_seed(k, N, 3)
            )
            summary = summarize_uniform(times, terminal, N)
            lower, upper = bounds(k, N)
            rows.append(
                {
                    "experiment": "markov_exact",
                    "k": k,
                    "N": N,
                    "repetitions": repetitions,
                    "mc_mean": summary.mean,
                    "mc_sd": summary.sd,
                    "ci_low": summary.ci_low,
                    "ci_high": summary.ci_high,
                    "exact_mean": exact.mean,
                    "relative_error": abs(summary.mean - exact.mean) / exact.mean,
                    "lower_bound": lower,
                    "upper_bound": upper,
                    "potential_rhs": summary.potential_rhs,
                    "martingale_rel_gap": summary.martingale_rel_gap,
                    "state_count": exact.state_count,
                    "lumped_state_count": exact.lumped_state_count,
                    "linear_residual": exact.max_abs_residual,
                }
            )
    return rows


def run_scaling_experiment(repetitions: int) -> tuple[list[dict], dict[tuple[int, int], np.ndarray]]:
    rows: list[dict] = []
    saved_times: dict[tuple[int, int], np.ndarray] = {}
    for k in (2, 3, 4, 5, 6, 8, 10, 15, 20):
        for N in (5, 10, 20, 40):
            times, terminal = simulate_uniform_hyperedge(
                k, N, repetitions, deterministic_seed(k, N, 4)
            )
            summary = summarize_uniform(times, terminal, N)
            lower, upper = bounds(k, N)
            rows.append(
                {
                    "k": k,
                    "N": N,
                    "repetitions": repetitions,
                    "mc_mean": summary.mean,
                    "mc_sd": summary.sd,
                    "ci_low": summary.ci_low,
                    "ci_high": summary.ci_high,
                    "normalized_mean": summary.mean / (N * N),
                    "normalized_ci_low": summary.ci_low / (N * N),
                    "normalized_ci_high": summary.ci_high / (N * N),
                    "lower_bound": lower,
                    "upper_bound": upper,
                    "lower_normalized": lower / (N * N),
                    "upper_normalized": upper / (N * N),
                    "potential_rhs": summary.potential_rhs,
                    "martingale_rel_gap": summary.martingale_rel_gap,
                }
            )
            if N == 20 and k in (2, 3, 5, 10, 20):
                saved_times[(k, N)] = times.copy()
    return rows, saved_times


def make_survival_rows(saved_times: dict[tuple[int, int], np.ndarray]) -> list[dict]:
    rows: list[dict] = []
    normalized_grid = np.linspace(0.0, 4.0, 161)
    for (k, N), times in sorted(saved_times.items()):
        normalized = times / (N * N)
        for value in normalized_grid:
            rows.append(
                {
                    "k": k,
                    "N": N,
                    "normalized_time": float(value),
                    "survival_probability": float(np.mean(normalized > value)),
                }
            )
    return rows


def empirical_discrete_min_mean(single_edge_times: np.ndarray, edge_count: int) -> float:
    """Plug-in estimate sum_t S(t)^m for m independent integer-valued times."""
    maximum = int(np.max(single_edge_times))
    counts = np.bincount(single_edge_times, minlength=maximum + 1)
    # S(t)=P(T>t).  The reverse cumulative count excludes mass at t.
    survival_counts = np.cumsum(counts[::-1])[::-1] - counts
    survival = survival_counts / single_edge_times.size
    return float(np.sum(survival**edge_count))


def run_independent_network_experiment(
    base_repetitions: int, direct_repetitions: int
) -> list[dict]:
    """Validate E[min_e T_e]=sum_t prod_e S_e(t) for independent edges."""
    k, N = 5, 20
    base_times, _ = simulate_uniform_hyperedge(
        k, N, base_repetitions, deterministic_seed(k, N, 5)
    )
    rows: list[dict] = []
    for edge_count in (1, 2, 5, 10):
        predicted = empirical_discrete_min_mean(base_times, edge_count)
        direct_times, _ = simulate_uniform_hyperedge(
            k,
            N,
            direct_repetitions * edge_count,
            deterministic_seed(k, N, 50 + edge_count),
        )
        minima = direct_times.reshape(direct_repetitions, edge_count).min(axis=1)
        mean, sd, ci_low, ci_high = summarize_times(minima)
        rows.append(
            {
                "k": k,
                "N": N,
                "edge_count": edge_count,
                "base_repetitions": base_repetitions,
                "direct_repetitions": direct_repetitions,
                "survival_product_mean": predicted,
                "direct_mc_mean": mean,
                "direct_mc_sd": sd,
                "ci_low": ci_low,
                "ci_high": ci_high,
                "relative_error": abs(mean - predicted) / predicted,
            }
        )
    return rows


def plot_closed_and_biased(closed_rows: list[dict], biased_rows: list[dict]) -> None:
    configure_plots()
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.2))

    ax = axes[0]
    markers = {2: "o", 3: "s"}
    for k in (2, 3):
        subset = [row for row in closed_rows if row["k"] == k]
        exact = np.array([row["exact_mean"] for row in subset])
        mc = np.array([row["mc_mean"] for row in subset])
        yerr = np.vstack(
            [
                mc - np.array([row["ci_low"] for row in subset]),
                np.array([row["ci_high"] for row in subset]) - mc,
            ]
        )
        ax.errorbar(
            exact,
            mc,
            yerr=yerr,
            fmt=markers[k],
            capsize=2,
            label=f"k={k} Monte Carlo",
        )
    maximum = max(row["exact_mean"] for row in closed_rows)
    ax.plot([1, maximum], [1, maximum], "--", color="0.3", linewidth=1.2, label="exact = Monte Carlo")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("Exact mean stopping time")
    ax.set_ylabel("Monte Carlo mean (95% CI)")
    ax.set_title("(a) Closed forms: equal initial balances")
    ax.legend(frameon=False)

    ax = axes[1]
    p_values = np.array([row["p_up"] for row in biased_rows])
    exact_values = np.array([row["exact_mean"] for row in biased_rows])
    mc_values = np.array([row["mc_mean"] for row in biased_rows])
    yerr = np.vstack(
        [
            mc_values - np.array([row["ci_low"] for row in biased_rows]),
            np.array([row["ci_high"] for row in biased_rows]) - mc_values,
        ]
    )
    ax.plot(p_values, exact_values, "-", linewidth=1.8, label="gambler's-ruin formula")
    ax.errorbar(p_values, mc_values, yerr=yerr, fmt="o", capsize=3, label="Monte Carlo (95% CI)")
    ax.axvline(0.5, linestyle=":", color="0.35", linewidth=1)
    ax.set_xlabel("p = P(node 1 balance increases)")
    ax.set_ylabel("Mean stopping time")
    ax.set_title("(b) Biased k=2 channel (M=40, x=20)")
    ax.legend(frameon=False)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig1-closed-form-validation.png", bbox_inches="tight")
    plt.close(fig)


def plot_markov(markov_rows: list[dict]) -> None:
    configure_plots()
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.2))
    colors = {4: "C0", 5: "C1", 6: "C2"}
    markers = {4: "o", 5: "s", 6: "^"}

    ax = axes[0]
    for k in (4, 5, 6):
        subset = [row for row in markov_rows if row["k"] == k]
        exact = np.array([row["exact_mean"] for row in subset])
        mc = np.array([row["mc_mean"] for row in subset])
        ax.scatter(exact, mc, marker=markers[k], color=colors[k], label=f"k={k}")
    maximum = max(row["exact_mean"] for row in markov_rows)
    ax.plot([0, maximum], [0, maximum], "--", color="0.3", linewidth=1.2)
    ax.set_xlabel("Exact Markov-chain mean")
    ax.set_ylabel("Monte Carlo mean")
    ax.set_title("(a) Exact finite-state solver vs simulation")
    ax.legend(frameon=False)

    ax = axes[1]
    for k in (4, 5, 6):
        subset = [row for row in markov_rows if row["k"] == k]
        n_values = np.array([row["N"] for row in subset])
        normalized = np.array([row["exact_mean"] / (row["N"] ** 2) for row in subset])
        ax.plot(n_values, normalized, marker=markers[k], color=colors[k], label=f"k={k}")
        lower = k / (2 * (k - 1))
        ax.axhline(lower, color=colors[k], linestyle=":", linewidth=0.9, alpha=0.7)
    ax.set_xlabel("Initial units per participant, N")
    ax.set_ylabel(r"Exact mean / $N^2$")
    ax.set_title("(b) Quadratic scaling and rigorous lower bounds")
    ax.legend(frameon=False)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig2-markov-validation.png", bbox_inches="tight")
    plt.close(fig)


def plot_scaling(scaling_rows: list[dict]) -> None:
    configure_plots()
    fig, axes = plt.subplots(1, 2, figsize=(11.2, 4.3))
    ks = (2, 3, 4, 5, 6, 8, 10, 15, 20)

    ax = axes[0]
    for k in ks:
        subset = [row for row in scaling_rows if row["k"] == k]
        n_values = np.array([row["N"] for row in subset])
        normalized = np.array([row["normalized_mean"] for row in subset])
        ax.plot(n_values, normalized, marker="o", markersize=3.5, linewidth=1.2, label=f"k={k}")
    ax.set_xscale("log", base=2)
    ax.set_xticks((5, 10, 20, 40), labels=("5", "10", "20", "40"))
    ax.set_xlabel("Initial units per participant, N")
    ax.set_ylabel(r"Monte Carlo mean / $N^2$")
    ax.set_title("(a) Diffusive scaling collapse")
    ax.legend(ncol=3, frameon=False)

    ax = axes[1]
    subset40 = [row for row in scaling_rows if row["N"] == 40]
    k_values = np.array([row["k"] for row in subset40])
    means = np.array([row["normalized_mean"] for row in subset40])
    lower = np.array([row["lower_normalized"] for row in subset40])
    ci_low = np.array([row["normalized_ci_low"] for row in subset40])
    ci_high = np.array([row["normalized_ci_high"] for row in subset40])
    ax.fill_between(k_values, ci_low, ci_high, alpha=0.18, label="Monte Carlo 95% CI")
    ax.plot(k_values, means, "o-", linewidth=1.7, label=r"estimated $a_k$")
    ax.plot(k_values, lower, "--", linewidth=1.3, label=r"rigorous lower bound $k/[2(k-1)]$")
    ax.set_xlabel("Number of participants, k")
    ax.set_ylabel(r"Mean stopping time / $N^2$")
    ax.set_title("(b) Dependence on hyperedge size (N=40)")
    ax.legend(frameon=False)

    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig3-scaling-and-bounds.png", bbox_inches="tight")
    plt.close(fig)


def plot_survival(survival_rows: list[dict]) -> None:
    configure_plots()
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    for k in (2, 3, 5, 10, 20):
        subset = [row for row in survival_rows if row["k"] == k]
        x = [row["normalized_time"] for row in subset]
        y = [row["survival_probability"] for row in subset]
        ax.step(x, y, where="post", linewidth=1.5, label=f"k={k}")
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 1.01)
    ax.set_xlabel(r"Normalized time, $t/N^2$")
    ax.set_ylabel(r"Empirical survival probability, $P(\tau>t)$")
    ax.set_title("First-depletion survival curves (N=20)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig4-survival-curves.png", bbox_inches="tight")
    plt.close(fig)


def plot_network(network_rows: list[dict]) -> None:
    configure_plots()
    fig, ax = plt.subplots(figsize=(7.2, 4.5))
    edge_counts = np.array([row["edge_count"] for row in network_rows])
    predicted = np.array([row["survival_product_mean"] for row in network_rows])
    direct = np.array([row["direct_mc_mean"] for row in network_rows])
    yerr = np.vstack(
        [
            direct - np.array([row["ci_low"] for row in network_rows]),
            np.array([row["ci_high"] for row in network_rows]) - direct,
        ]
    )
    ax.plot(edge_counts, predicted, "s-", linewidth=1.7, label=r"$\sum_t S(t)^m$")
    ax.errorbar(
        edge_counts,
        direct,
        yerr=yerr,
        fmt="o",
        capsize=3,
        label="direct independent-network simulation (95% CI)",
    )
    ax.set_xticks(edge_counts)
    ax.set_xlabel("Number of independent identical hyperedges, m")
    ax.set_ylabel("Mean time to first hyperedge depletion")
    ax.set_title("Network-level survival aggregation (k=5, N=20)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "fig5-network-aggregation.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="Run a faster smoke-test-sized experiment")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    if args.quick:
        closed_reps, biased_reps, markov_reps, scaling_reps = 4_000, 4_000, 3_000, 2_000
        network_base_reps, network_direct_reps = 4_000, 2_000
    else:
        closed_reps, biased_reps, markov_reps, scaling_reps = 50_000, 50_000, 30_000, 20_000
        network_base_reps, network_direct_reps = 50_000, 20_000

    started = time.perf_counter()
    closed_rows = run_closed_form_validation(closed_reps)
    biased_rows = run_biased_k2_validation(biased_reps)
    markov_rows = run_markov_validation(markov_reps)
    scaling_rows, saved_times = run_scaling_experiment(scaling_reps)
    survival_rows = make_survival_rows(saved_times)
    network_rows = run_independent_network_experiment(network_base_reps, network_direct_reps)

    validation_fields = (
        "experiment",
        "k",
        "N",
        "repetitions",
        "mc_mean",
        "mc_sd",
        "ci_low",
        "ci_high",
        "exact_mean",
        "relative_error",
        "lower_bound",
        "upper_bound",
        "potential_rhs",
        "martingale_rel_gap",
        "state_count",
        "lumped_state_count",
        "linear_residual",
    )
    write_csv(RESULTS_DIR / "closed-form-validation.csv", closed_rows, validation_fields)
    write_csv(
        RESULTS_DIR / "biased-k2-validation.csv",
        biased_rows,
        (
            "p_up",
            "total_units",
            "start_units",
            "repetitions",
            "mc_mean",
            "mc_sd",
            "ci_low",
            "ci_high",
            "exact_mean",
            "relative_error",
        ),
    )
    write_csv(RESULTS_DIR / "markov-validation.csv", markov_rows, validation_fields)
    write_csv(
        RESULTS_DIR / "scaling-results.csv",
        scaling_rows,
        tuple(scaling_rows[0].keys()),
    )
    write_csv(
        RESULTS_DIR / "survival-curves.csv",
        survival_rows,
        ("k", "N", "normalized_time", "survival_probability"),
    )
    write_csv(
        RESULTS_DIR / "network-aggregation.csv",
        network_rows,
        tuple(network_rows[0].keys()),
    )

    plot_closed_and_biased(closed_rows, biased_rows)
    plot_markov(markov_rows)
    plot_scaling(scaling_rows)
    plot_survival(survival_rows)
    plot_network(network_rows)

    all_validation = closed_rows + markov_rows
    summary = {
        "runtime_seconds": time.perf_counter() - started,
        "max_closed_form_relative_error": max(row["relative_error"] for row in closed_rows),
        "max_markov_relative_error": max(row["relative_error"] for row in markov_rows),
        "max_biased_k2_relative_error": max(row["relative_error"] for row in biased_rows),
        "fraction_exact_values_inside_mc_95ci": float(
            np.mean(
                [row["ci_low"] <= row["exact_mean"] <= row["ci_high"] for row in all_validation]
            )
        ),
        "max_martingale_relative_gap": max(
            row["martingale_rel_gap"] for row in all_validation + scaling_rows
        ),
        "max_linear_system_residual": max(row["linear_residual"] for row in markov_rows),
        "max_network_aggregation_relative_error": max(
            row["relative_error"] for row in network_rows
        ),
        "mc_95ci_bound_violation_count": sum(
            (row["ci_high"] < row["lower_bound"]) or (row["ci_low"] > row["upper_bound"])
            for row in all_validation + scaling_rows
        ),
    }
    write_csv(RESULTS_DIR / "experiment-summary.csv", [summary], tuple(summary.keys()))
    print("Experiment summary")
    for key, value in summary.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
