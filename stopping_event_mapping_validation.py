"""Executable checks for the stopping-event/real-failure semantics contract.

The mathematical model stops immediately after an accepted unit route first
places any directed balance on the boundary.  A protocol rejection is instead
checked against the pre-route state.  This module keeps those two clocks
separate and exhaustively checks the indexing claim on small channel systems.
"""

from __future__ import annotations

import csv
import hashlib
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parent
RESULT_DIR = ROOT / "results" / "stopping-event-mapping-validation"


@dataclass(frozen=True)
class UnitRoute:
    name: str
    consumed: tuple[int, ...]
    received: tuple[int, ...]


ROUTES = (
    UnitRoute("c0_forward", (0,), (1,)),
    UnitRoute("c0_reverse", (1,), (0,)),
    UnitRoute("c1_forward", (2,), (3,)),
    UnitRoute("c1_reverse", (3,), (2,)),
    UnitRoute("path_forward", (0, 2), (1, 3)),
    UnitRoute("path_reverse", (1, 3), (0, 2)),
)


def apply_unit_route(state: Sequence[int], route: UnitRoute) -> tuple[int, ...]:
    """Apply one accepted unit route; reject negative post-states."""
    updated = list(state)
    for index in route.consumed:
        updated[index] -= 1
    for index in route.received:
        updated[index] += 1
    if min(updated) < 0:
        raise ValueError("route is not balance-feasible in the pre-route state")
    return tuple(updated)


def boundary_time(
    initial_state: Sequence[int], route_sequence: Iterable[UnitRoute]
) -> int | None:
    """Return the 1-based post-update first-boundary time used by the paper."""
    state = tuple(initial_state)
    if min(state) <= 0:
        raise ValueError("the S0 contract requires a strictly positive initial state")
    for step, route in enumerate(route_sequence, start=1):
        if any(state[index] < 1 for index in route.consumed):
            raise ValueError("paper process was continued beyond an infeasible route")
        state = apply_unit_route(state, route)
        if min(state) == 0:
            return step
    return None


def first_rejection_time(
    initial_state: Sequence[int],
    route_sequence: Iterable[UnitRoute],
    *,
    disabled_steps: frozenset[int] = frozenset(),
) -> int | None:
    """Return the first pre-update rejection while allowing reverse restoration."""
    state = tuple(initial_state)
    for step, route in enumerate(route_sequence, start=1):
        if step in disabled_steps or any(
            state[index] < 1 for index in route.consumed
        ):
            return step
        state = apply_unit_route(state, route)
    return None


def exhaustive_index_audit(max_scale: int = 3, horizon: int = 6) -> dict[str, int]:
    """Check that a balance-only rejection never occurs at or before boundary hit."""
    checked = 0
    boundary_observed = 0
    rejection_observed = 0
    violations = 0
    for scale in range(1, max_scale + 1):
        initial = (scale, scale, scale, scale)
        for route_ids in itertools.product(range(len(ROUTES)), repeat=horizon):
            sequence = tuple(ROUTES[index] for index in route_ids)
            checked += 1

            # Compute the paper clock only up to its first boundary.
            state = initial
            tau = None
            for step, route in enumerate(sequence, start=1):
                if any(state[index] < 1 for index in route.consumed):
                    break
                pre_state = state
                state = apply_unit_route(state, route)
                if min(state) == 0:
                    # The depletion-causing route was feasible before execution.
                    if not all(
                        pre_state[index] >= 1 for index in route.consumed
                    ):
                        violations += 1
                    tau = step
                    boundary_observed += 1
                    break

            rho = first_rejection_time(initial, sequence)
            if rho is not None:
                rejection_observed += 1
            if tau is not None and rho is not None and rho <= tau:
                violations += 1

    if violations:
        raise RuntimeError(f"stopping-event indexing violations: {violations}")

    return {
        "max_scale": max_scale,
        "horizon": horizon,
        "route_alphabet_size": len(ROUTES),
        "sequences_checked": checked,
        "boundary_hits_observed": boundary_observed,
        "balance_rejections_observed": rejection_observed,
        "violations": violations,
    }


def illustrative_cases() -> list[dict[str, object]]:
    """Construct witnesses for later, earlier, and absent real-style rejection."""
    forward = ROUTES[0]
    reverse = ROUTES[1]
    cases = []

    sequence = (forward, forward)
    cases.append(
        {
            "case": "balance_rejection_after_boundary",
            "initial_scale": 1,
            "route_sequence": "c0_forward,c0_forward",
            "model_boundary_time": boundary_time((1, 1, 1, 1), sequence),
            "first_rejection_time": first_rejection_time(
                (1, 1, 1, 1), sequence
            ),
            "relation": "rejection_after_boundary",
        }
    )

    sequence = (forward, forward)
    cases.append(
        {
            "case": "policy_rejection_before_boundary",
            "initial_scale": 2,
            "route_sequence": "c0_forward,c0_forward",
            "model_boundary_time": boundary_time((2, 2, 2, 2), sequence),
            "first_rejection_time": first_rejection_time(
                (2, 2, 2, 2), sequence, disabled_steps=frozenset({1})
            ),
            "relation": "rejection_before_boundary",
        }
    )

    sequence = (forward, reverse) * 4
    cases.append(
        {
            "case": "reverse_flow_restores_boundary",
            "initial_scale": 1,
            "route_sequence": ",".join(route.name for route in sequence),
            "model_boundary_time": boundary_time((1, 1, 1, 1), sequence),
            "first_rejection_time": first_rejection_time(
                (1, 1, 1, 1), sequence
            ),
            "relation": "no_rejection_within_horizon",
        }
    )
    return cases


def write_artifacts(result_dir: Path = RESULT_DIR) -> dict[str, object]:
    result_dir.mkdir(parents=True, exist_ok=True)
    audit = exhaustive_index_audit()
    cases = illustrative_cases()

    cases_path = result_dir / "mapping-cases.csv"
    with cases_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(cases[0]))
        writer.writeheader()
        writer.writerows(cases)

    summary = {
        "status": "PASS",
        "scope": "semantic/indexing validation; not empirical Lightning failure calibration",
        "proposition": (
            "Under the ideal unit-route contract, the route that first reaches "
            "zero is accepted from a strictly positive pre-route state; any "
            "balance-only rejection is strictly later if it occurs."
        ),
        "exhaustive_audit": audit,
        "illustrative_case_count": len(cases),
        "gates": {
            "no_indexing_violations": audit["violations"] == 0,
            "later_rejection_witness": cases[0]["first_rejection_time"]
            > cases[0]["model_boundary_time"],
            "earlier_policy_failure_witness": cases[1]["first_rejection_time"]
            < cases[1]["model_boundary_time"],
            "reverse_restoration_witness": cases[2]["first_rejection_time"] is None,
        },
    }
    summary_path = result_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    manifest_path = result_dir / "SHA256SUMS.txt"
    manifest_lines = []
    for path in (cases_path, summary_path):
        manifest_lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    manifest_path.write_text("\n".join(manifest_lines) + "\n", encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(write_artifacts(), ensure_ascii=False, indent=2))
