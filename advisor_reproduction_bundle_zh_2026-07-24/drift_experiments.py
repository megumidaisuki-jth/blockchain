"""Exact and Monte Carlo checks for a legally parameterized drifted hyperedge.

One distinguished participant is node 0.  An unordered pair is sampled
uniformly.  If the pair contains node 0, funds move toward node 0 with
probability p_bias/2 and away with probability 1-p_bias/2.  Pairs not
containing node 0 are oriented uniformly.  Thus p_bias must lie in [0, 2].
"""

from __future__ import annotations

import csv
import math
from pathlib import Path
from typing import Iterator

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import spsolve
from scipy.special import ndtr


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


def positive_compositions(total: int, parts: int) -> Iterator[tuple[int, ...]]:
    if parts == 1:
        yield (total,)
        return
    for first in range(1, total - parts + 2):
        for tail in positive_compositions(total - first, parts - 1):
            yield (first,) + tail


def canonical(state: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    return (state[0],) + tuple(sorted(state[1:]))


def exact_drifted_markov_mean(k: int, N: int, p_bias: float) -> tuple[float, int, float]:
    if not 0.0 <= p_bias <= 2.0:
        raise ValueError("p_bias must lie in [0,2]")
    total = k * N
    states = sorted({canonical(state) for state in positive_compositions(total, k)})
    index = {state: idx for idx, state in enumerate(states)}
    pair_probability = 2.0 / (k * (k - 1))
    theta = p_bias / 2.0
    rows: list[int] = []
    cols: list[int] = []
    data: list[float] = []

    def add_transition(row: int, state: tuple[int, ...], sender: int, receiver: int, probability: float) -> None:
        if probability == 0.0 or state[sender] == 1:
            return
        nxt = list(state)
        nxt[sender] -= 1
        nxt[receiver] += 1
        rows.append(row)
        cols.append(index[canonical(nxt)])
        data.append(-probability)

    for row, state in enumerate(states):
        rows.append(row)
        cols.append(row)
        data.append(1.0)

        for peripheral in range(1, k):
            add_transition(row, state, peripheral, 0, pair_probability * theta)
            add_transition(row, state, 0, peripheral, pair_probability * (1.0 - theta))

        for left in range(1, k):
            for right in range(left + 1, k):
                add_transition(row, state, left, right, pair_probability / 2.0)
                add_transition(row, state, right, left, pair_probability / 2.0)

    matrix = coo_matrix((data, (rows, cols)), shape=(len(states), len(states))).tocsr()
    rhs = np.ones(len(states))
    solution = spsolve(matrix, rhs)
    residual = float(np.max(np.abs(matrix @ solution - rhs)))
    return float(solution[index[(N,) * k]]), len(states), residual


def simulate_drifted_hyperedge(
    k: int, N: int, p_bias: float, repetitions: int, seed: int
) -> np.ndarray:
    if not 0.0 <= p_bias <= 2.0:
        raise ValueError("p_bias must lie in [0,2]")
    rng = np.random.default_rng(seed)
    balances = np.full((repetitions, k), N, dtype=np.int32)
    times = np.zeros(repetitions, dtype=np.int32)
    active = np.arange(repetitions, dtype=np.int64)
    theta = p_bias / 2.0

    while active.size:
        count = active.size
        first = rng.integers(0, k, size=count)
        second_raw = rng.integers(0, k - 1, size=count)
        second = second_raw + (second_raw >= first)
        sender = first.copy()
        receiver = second.copy()

        star = (first == 0) | (second == 0)
        if np.any(star):
            other = np.where(first[star] == 0, second[star], first[star])
            toward_zero = rng.random(np.count_nonzero(star)) < theta
            sender[star] = np.where(toward_zero, other, 0)
            receiver[star] = np.where(toward_zero, 0, other)

        balances[active, sender] -= 1
        balances[active, receiver] += 1
        times[active] += 1
        depleted = balances[active, sender] == 0
        active = active[~depleted]

    return times


def summarize(times: np.ndarray) -> tuple[float, float, float, float]:
    values = times.astype(float)
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    half = 1.959963984540054 * sd / math.sqrt(values.size)
    return mean, sd, mean - half, mean + half


def leading_strong_drift(k: int, N: int, p_bias: float) -> float:
    delta = p_bias - 1.0
    if delta < 0:
        return k * N / (2.0 * abs(delta))
    if delta > 0:
        return k * (k - 1) * N / (2.0 * delta)
    return math.inf


def gaussian_max_mean(count: int) -> float:
    """E[max of count iid standard normal variables]."""
    if count == 1:
        return 0.0

    def integrand(x: float) -> float:
        cdf = ndtr(x)
        return 1.0 - cdf**count - (1.0 - cdf) ** count

    return float(quad(integrand, 0.0, np.inf, epsabs=1e-12)[0])


def refined_positive_drift(k: int, N: int, p_bias: float) -> float:
    delta = p_bias - 1.0
    if delta <= 0:
        raise ValueError("refined formula is for positive drift")
    leading = leading_strong_drift(k, N, p_bias)
    correction_ratio = gaussian_max_mean(k - 1) * math.sqrt(k / (delta * N))
    return leading * (1.0 - correction_ratio)


def write_csv(name: str, rows: list[dict]) -> None:
    RESULTS.mkdir(exist_ok=True)
    with (RESULTS / name).open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=tuple(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def exact_validation() -> list[dict]:
    rows: list[dict] = []
    repetitions = 30_000
    for k in (3, 4, 5):
        N = 8
        for p_bias in (0.4, 0.7, 1.0, 1.3, 1.6):
            exact, state_count, residual = exact_drifted_markov_mean(k, N, p_bias)
            times = simulate_drifted_hyperedge(
                k, N, p_bias, repetitions, 801_001 + 1000 * k + int(100 * p_bias)
            )
            mean, sd, low, high = summarize(times)
            rows.append(
                {
                    "k": k,
                    "N": N,
                    "p_bias": p_bias,
                    "repetitions": repetitions,
                    "exact_mean": exact,
                    "mc_mean": mean,
                    "mc_sd": sd,
                    "ci_low": low,
                    "ci_high": high,
                    "relative_error": abs(mean - exact) / exact,
                    "lumped_state_count": state_count,
                    "linear_residual": residual,
                }
            )
    return rows


def strong_drift_validation() -> list[dict]:
    rows: list[dict] = []
    repetitions = 10_000
    for k in (3, 5):
        for N in (20, 40, 80, 160, 320):
            for p_bias in (0.5, 1.5):
                times = simulate_drifted_hyperedge(
                    k, N, p_bias, repetitions, 802_003 + 1000 * k + 10 * N + int(100 * p_bias)
                )
                mean, sd, low, high = summarize(times)
                leading = leading_strong_drift(k, N, p_bias)
                refined = refined_positive_drift(k, N, p_bias) if p_bias > 1 else leading
                rows.append(
                    {
                        "k": k,
                        "N": N,
                        "p_bias": p_bias,
                        "repetitions": repetitions,
                        "mc_mean": mean,
                        "mc_sd": sd,
                        "ci_low": low,
                        "ci_high": high,
                        "leading_asymptotic": leading,
                        "leading_relative_error": abs(mean - leading) / mean,
                        "refined_asymptotic": refined,
                        "refined_relative_error": abs(mean - refined) / mean,
                        "peclet_center": abs(p_bias - 1.0) * N,
                        "peclet_peripheral": abs(p_bias - 1.0) * N / (k - 1),
                    }
                )
    return rows


def weak_drift_scaling() -> list[dict]:
    rows: list[dict] = []
    for k in (3, 4):
        for eta in (-2.0, -1.0, 0.0, 1.0, 2.0):
            for N in (5, 10, 20):
                p_bias = 1.0 + eta / N
                exact, state_count, residual = exact_drifted_markov_mean(k, N, p_bias)
                rows.append(
                    {
                        "k": k,
                        "N": N,
                        "eta": eta,
                        "p_bias": p_bias,
                        "exact_mean": exact,
                        "normalized_mean": exact / (N * N),
                        "lumped_state_count": state_count,
                        "linear_residual": residual,
                    }
                )
    return rows


def make_figure(exact_rows: list[dict], strong_rows: list[dict], weak_rows: list[dict]) -> None:
    FIGURES.mkdir(exist_ok=True)
    plt.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 220,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.22,
        }
    )
    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.2))

    ax = axes[0]
    for k, marker in ((3, "o"), (4, "s"), (5, "^")):
        subset = [r for r in exact_rows if r["k"] == k]
        ax.scatter(
            [r["exact_mean"] for r in subset],
            [r["mc_mean"] for r in subset],
            marker=marker,
            label=f"k={k}",
        )
    maximum = max(r["exact_mean"] for r in exact_rows)
    ax.plot([0, maximum], [0, maximum], "--", color="0.35", linewidth=1)
    ax.set_xlabel("Exact Markov mean")
    ax.set_ylabel("Monte Carlo mean")
    ax.set_title("(a) Exact drifted chain")
    ax.legend(frameon=False)

    ax = axes[1]
    for k, marker in ((3, "o"), (5, "s")):
        subset = [r for r in strong_rows if r["k"] == k and r["p_bias"] > 1]
        ax.plot(
            [r["N"] for r in subset],
            [r["mc_mean"] / r["leading_asymptotic"] for r in subset],
            marker=marker,
            label=f"simulation/leading, k={k}",
        )
        ax.plot(
            [r["N"] for r in subset],
            [r["refined_asymptotic"] / r["leading_asymptotic"] for r in subset],
            linestyle="--",
            label=f"refined/leading, k={k}",
        )
    ax.set_xscale("log", base=2)
    ax.set_xlabel("N")
    ax.set_ylabel("Ratio to leading positive-drift time")
    ax.set_title("(b) Positive-drift competition correction")
    ax.legend(frameon=False, fontsize=8)

    ax = axes[2]
    for eta, marker in ((-2.0, "o"), (-1.0, "s"), (0.0, "^"), (1.0, "D"), (2.0, "v")):
        subset = [r for r in weak_rows if r["k"] == 3 and r["eta"] == eta]
        ax.plot(
            [r["N"] for r in subset],
            [r["normalized_mean"] for r in subset],
            marker=marker,
            label=rf"$\eta={eta:g}$",
        )
    ax.set_xscale("log", base=2)
    ax.set_xticks((5, 10, 20), labels=("5", "10", "20"))
    ax.set_xlabel("N with p = 1 + eta/N")
    ax.set_ylabel(r"Exact mean / $N^2$")
    ax.set_title("(c) Weak-drift scaling, k=3")
    ax.legend(frameon=False, fontsize=8)

    fig.tight_layout()
    fig.savefig(FIGURES / "fig6-drift-validation.png", bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    exact_rows = exact_validation()
    strong_rows = strong_drift_validation()
    weak_rows = weak_drift_scaling()
    write_csv("drift-exact-validation.csv", exact_rows)
    write_csv("drift-strong-asymptotic.csv", strong_rows)
    write_csv("drift-weak-scaling.csv", weak_rows)
    make_figure(exact_rows, strong_rows, weak_rows)

    print("max exact-vs-MC relative error", max(r["relative_error"] for r in exact_rows))
    print("max linear residual", max(r["linear_residual"] for r in exact_rows + weak_rows))
    positive = [r for r in strong_rows if r["p_bias"] > 1]
    print("positive leading max relative error", max(r["leading_relative_error"] for r in positive))
    print("positive refined max relative error", max(r["refined_relative_error"] for r in positive))
    print("strong negative max relative error", max(r["leading_relative_error"] for r in strong_rows if r["p_bias"] < 1))


if __name__ == "__main__":
    main()
