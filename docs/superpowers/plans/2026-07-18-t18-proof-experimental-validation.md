# T18 Proof and Cross-Topology Experimental Validation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Strengthen the T16–T18 proof chain with an exact critical-perturbation lemma and produce a reproducible, uncertainty-aware T18-A experiment across chain, star, and fixed-seed connected random hypergraphs.

**Architecture:** Keep the already frozen Task 6 evidence untouched. Add a separate T18 runner that consumes the existing topology, kernel, and paired-simulation interfaces. The runner creates three topology families, three drift regimes, and four capacity scales; it writes primary paired-mean comparisons, secondary summaries, configuration metadata, and SHA-256 hashes into a new evidence directory.

**Tech Stack:** Python 3.10+, NumPy, SciPy, `unittest`, Markdown, CSV, JSON, SHA-256.

## Global Constraints

- Main stop event remains the first balance coordinate equal to zero.
- Hypergraph, dimension, unit payment, exogenous route alphabet, and i.i.d. state-independent route probabilities remain fixed within each experiment.
- Topologies are four-triad chain, four-triad star, and `random_connected_triads(4, seed=7)`. Seed 7 is required because its hyperedge-intersection degree sequence `[1,1,1,3]` is distinct from the chain `[1,1,2,2]` and common-hub star `[3,3,3,3]`; the originally proposed seed 20260718 was rejected after exact-anchor QA showed it was chain-isomorphic.
- Scales are `N = 10, 20, 40, 80`; drift regimes are balanced and a reversible route-pair perturbation of `+0.01/N` or `-0.01/N`.
- The independent-edge proxy preserves every edge-block marginal but is not represented as routed traffic.
- Primary effect is `(T_correlated - T_proxy)/N**2`; family-wise 95% confidence intervals use a Bonferroni normal multiplier over all 36 primary cells.
- Report paired standard error, simultaneous interval, paired standardized effect, relative mean difference, raw means, nonidentical fraction, and route/covariance diagnostics.
- Full run uses 30,000 independent paired repetitions per cell; quick/test runs use smaller declared counts and may not support scientific conclusions.
- Existing `results/network` files and the frozen HTML audit are read-only.
- This workspace is not a Git repository; verification hashes and QA logs replace commit checkpoints.

---

### Task 1: Freeze the proof-to-experiment contract

**Files:**
- Modify: `outputs/researchwrite/hypergraph-stopping-time/13_correlated_network_proof_package.md`
- Create: `outputs/researchwrite/hypergraph-stopping-time/16_key_proof_and_t18_validation_2026-07-18.md`

**Interfaces:**
- Consumes: `NetworkKernel.drift`, `NetworkKernel.covariance`, and reversible route increments.
- Produces: a stated lemma for the `±a/N` route-pair perturbation and an explicit claim-status table.

- [ ] **Step 1: State the exact perturbation lemma**

  For a balanced base law with reverse increments `zeta` and `-zeta`, state and prove
  `N d_N^(±) = ±2 a zeta` and
  `Gamma_N^(±) = Gamma_0 - d_N^(±) d_N^(±,T)`.

- [ ] **Step 2: Check theorem dependencies**

  Verify that T16 uses finite-state reachability, T17A uses bounded increments and `N^alpha d_N -> beta`, T17B/C use the triangular-array FCLT plus exit-map continuity and uniform exponential moments, and T18a uses joint Gaussianity in addition to zero cross blocks.

- [ ] **Step 3: Record downgrade rules**

  Preserve the rule that numerical sign results are topology/demand-specific and that unsigned external probability review remains required before publication-readiness can become true.

### Task 2: Add test-first T18 scenario construction

**Files:**
- Create: `test_t18_cross_topology.py`
- Create: `t18_cross_topology_validation.py`

**Interfaces:**
- Consumes: `overlap_chain_triads`, `overlap_star_triads`, `random_connected_triads`, `shortest_route_kernel`, `perturb_route_probabilities`, `simulate_paired_proxy`.
- Produces: `select_reversible_route_pair(kernel) -> tuple[int, int]`, `build_scenarios() -> tuple[T18Scenario, ...]`, and `critical_kernel(base, scale, sign, amplitude) -> NetworkKernel`.

- [ ] **Step 1: Write failing route-pair and scenario tests**

```python
def test_reversible_pair_is_longest_and_cancels():
    kernel = shortest_route_kernel(overlap_chain_triads(4))
    forward, reverse = select_reversible_route_pair(kernel)
    assert len(kernel.routes[forward].edges) == 4
    np.testing.assert_array_equal(kernel.increments[forward], -kernel.increments[reverse])

def test_scenario_grid_has_36_unique_cells():
    scenarios = build_scenarios()
    assert len(scenarios) == 36
    assert len({item.cell_id for item in scenarios}) == 36
```

- [ ] **Step 2: Run the tests and verify RED**

  Run: `python -m unittest test_t18_cross_topology -v`
  Expected: import failure because `t18_cross_topology_validation.py` does not yet exist.

- [ ] **Step 3: Implement deterministic scenario construction**

  Use sorted route tuples; select a longest route with an equal-probability reverse; create balanced, positive, and negative kernels at each scale; derive a unique seed from topology, regime, and scale indices.

- [ ] **Step 4: Verify GREEN**

  Run: `python -m unittest test_t18_cross_topology -v`
  Expected: all Task 2 tests pass.

### Task 3: Verify the exact critical-perturbation identities

**Files:**
- Modify: `test_t18_cross_topology.py`
- Modify: `t18_cross_topology_validation.py`

**Interfaces:**
- Consumes: `critical_kernel`.
- Produces: diagnostics `scaled_drift_error`, `second_moment_error`, and `covariance_identity_error` for every non-balanced cell.

- [ ] **Step 1: Write failing identity tests**

```python
def test_critical_perturbation_has_exact_scaled_drift_and_second_moment():
    base = shortest_route_kernel(overlap_star_triads(4))
    fwd, rev = select_reversible_route_pair(base)
    plus = critical_kernel(base, 40, +1, 0.01)
    expected = 0.02 * base.increments[fwd]
    np.testing.assert_allclose(40 * plus.drift, expected, atol=1e-13)
    second0 = base.covariance + np.outer(base.drift, base.drift)
    second1 = plus.covariance + np.outer(plus.drift, plus.drift)
    np.testing.assert_allclose(second1, second0, atol=1e-13)
```

- [ ] **Step 2: Run and verify RED for missing diagnostics**

  Run: `python -m unittest test_t18_cross_topology -v`
  Expected: failure because identity diagnostics are absent.

- [ ] **Step 3: Implement identity diagnostics and deterministic gates**

  Fail the run if any identity error exceeds `1e-12`, any probability is nonpositive, any edge marginal is not preserved by the proxy within `1e-12`, or any normal variance is degenerate.

- [ ] **Step 4: Run and verify GREEN**

  Run: `python -m unittest test_t18_cross_topology -v`
  Expected: all tests pass.

### Task 4: Add statistical summaries and artifact writing

**Files:**
- Modify: `test_t18_cross_topology.py`
- Modify: `t18_cross_topology_validation.py`

**Interfaces:**
- Produces: `summarize_paired_cell(...) -> dict` and `run_t18_validation(output, quick=False) -> dict`.

- [ ] **Step 1: Write failing summary tests**

```python
def test_paired_summary_uses_declared_simultaneous_multiplier():
    correlated = np.array([12, 14, 16, 18], dtype=np.int64)
    proxy = np.array([10, 11, 15, 16], dtype=np.int64)
    row = summarize_paired_cell(correlated, proxy, scale=2, multiplier=3.0)
    assert row['mean_difference'] == np.mean((correlated - proxy) / 4)
    assert row['ci_high'] - row['mean_difference'] == 3.0 * row['paired_standard_error']
```

- [ ] **Step 2: Run and verify RED**

  Run: `python -m unittest test_t18_cross_topology -v`
  Expected: failure because summary/artifact functions are absent.

- [ ] **Step 3: Implement statistics and atomic outputs**

  Compute the Bonferroni multiplier with `scipy.stats.norm.ppf(1 - 0.05/(2*36))`; write `t18-primary-effects.csv`, `t18-kernel-diagnostics.csv`, `t18-run-metadata.json`, and `SHA256SUMS.txt` atomically.

- [ ] **Step 4: Add a quick-run artifact test**

  Assert 36 primary rows, 36 diagnostic rows, unique seeds, declared repetition count, resolvable file paths, and manifest agreement.

- [ ] **Step 5: Verify GREEN and regressions**

  Run: `python -m unittest test_t18_cross_topology test_network_model -v`
  Expected: all tests pass.

### Task 5: Execute and freeze the full experiment

**Files:**
- Create: `results/t18-cross-topology/t18-primary-effects.csv`
- Create: `results/t18-cross-topology/t18-kernel-diagnostics.csv`
- Create: `results/t18-cross-topology/t18-run-metadata.json`
- Create: `results/t18-cross-topology/SHA256SUMS.txt`

- [ ] **Step 1: Run the full experiment**

  Run: `python t18_cross_topology_validation.py --output results/t18-cross-topology`
  Expected: exit code 0, 36 primary rows, 36 diagnostic rows, and all deterministic gates pass.

- [ ] **Step 2: Rerun to a separate directory**

  Run: `python t18_cross_topology_validation.py --output results/t18-cross-topology-replication`
  Expected: CSV hashes match the primary run; metadata differs only in runtime and absolute output paths.

- [ ] **Step 3: Check precision and state conclusions conservatively**

  Treat a sign as resolved only when its simultaneous interval excludes zero. Report unresolved cells and do not replace them with point-estimate signs.

### Task 6: Final proof, code, and evidence QA

**Files:**
- Modify: `outputs/researchwrite/hypergraph-stopping-time/16_key_proof_and_t18_validation_2026-07-18.md`
- Create: `outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_key_proof_and_t18_validation.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/state.json`
- Modify: `README.md`

- [ ] **Step 1: Run all tests**

  Run: `python -m unittest -v`
  Expected: zero failures and zero errors.

- [ ] **Step 2: Verify artifact schema, counts, finiteness, confidence arithmetic, and hashes**

  Independently parse both CSVs and JSON; recompute every confidence endpoint and every SHA-256 digest.

- [ ] **Step 3: Verify old frozen evidence did not change**

  Compare the five protected Task 6 CSV hashes against their recorded values in the prior QA log.

- [ ] **Step 4: Update project state without overstating readiness**

  Mark T18-A as run only if all deterministic and reproducibility gates pass. Keep `publication_readiness=false` while external probability review, institutional novelty search, and real LN mapping remain incomplete.

- [ ] **Step 5: Record the exact remaining proof boundary**

  Distinguish internal mathematical closure, computational cross-validation, and external independent proof certification.
