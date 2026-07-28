# T12 Positive-Drift Competition Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove the fixed-positive-drift $\sqrt N$ competition limit and mean correction, then validate the discrete model with deterministic identities, coupled Monte Carlo, independent replication, and exact Markov anchors.

**Architecture:** A new standalone module will enumerate the peripheral increment law, expose the closed-form competition constants, simulate the free walk and first depletion on one shared increment stream, compute block-robust simultaneous intervals, and write hashed artifacts. Existing `drift_experiments.py` supplies only the already-tested symmetric-state exact Poisson solver; no frozen result or existing simulator is modified.

**Tech Stack:** Python 3, `unittest`, NumPy, SciPy (`integrate.quad`, `stats.t`), standard-library CSV/JSON/hashlib/argparse, Markdown proof and QA records.

## Global Constraints

- Work in `E:\newblockchain`; this directory is not a Git repository, so do not initialize Git and replace commit steps with test-output and SHA-256 checkpoints.
- Fixed theorem domain: `k >= 3`, `1 < p_bias <= 2`, fixed `k,p_bias` as `N -> infinity`.
- Formal grid: `k in {3,4,5}`, `p_bias in {1.25,1.50,2.00}`, `N in {40,80,160,320}`.
- Formal primary and independent-replication runs use 20,000 trajectories per cell and 40 non-overlapping blocks of 500.
- Exact anchors use `N=6`, the same nine `(k,p_bias)` pairs, 100,000 trajectories, and 100 blocks of 1,000.
- No trajectory censoring, time cap, post-hoc exclusion, or replacement of a failed cell.
- New outputs must never overwrite a non-empty directory.
- Preserve all existing result files and the frozen HTML with SHA-256 `babf45d3ee1ae1455dfbf8d6c6d78d05fb296b87fdec6aca2902dc4a9b4f88cb`.
- Finite-grid diagnostics do not prove the asymptotic theorem; external probability review remains unsigned.

---

## File Structure

- Create `t12_positive_competition_validation.py`: mathematical primitives, coupled simulator, statistics, exact anchors, artifact writers, CLI.
- Create `test_t12_positive_competition.py`: all new unit, integration, schema, and overwrite-protection tests.
- Create `outputs/researchwrite/hypergraph-stopping-time/17_t12_positive_competition_proof_and_validation.md`: complete proof and bounded numerical conclusions.
- Create `outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_t12_positive_competition.md`: RED/GREEN evidence, formal run metadata, independent recomputation, and hashes.
- Modify `outputs/researchwrite/hypergraph-stopping-time/06_theorem_proof_gap_register.md`: upgrade T12 only if every proof and computation gate passes.
- Modify `outputs/researchwrite/hypergraph-stopping-time/state.json`: remove only the T12 error-bound debt after all gates pass and recompute completion conservatively.
- Modify `README.md`: add authoritative T12 proof, result, and QA links.
- Create formal result directories exactly as specified in the approved design.

---

### Task 1: Exact Peripheral Increment Law and Competition Constants

**Files:**
- Create: `t12_positive_competition_validation.py`
- Create: `test_t12_positive_competition.py`

**Interfaces:**
- Produces: `CompetitionTheory`, `enumerate_peripheral_increment_law(k, p_bias)`, `closed_form_peripheral_moments(k, p_bias)`, `competition_theory(k, p_bias)`.
- Later tasks consume `CompetitionTheory.v`, `.tstar_per_capacity`, `.kappa`, `.gaussian_difference_scale`, and `.mean_correction_coefficient`.

- [ ] **Step 1: Write failing validation and moment tests**

```python
class T12TheoryTests(unittest.TestCase):
    def test_parameter_contract_rejects_noncompetition_domain(self):
        for args in ((2, 1.5), (3, 1.0), (3, 2.0001)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                competition_theory(*args)

    def test_enumeration_matches_closed_form_moments(self):
        for k in (3, 4, 5, 8):
            for p_bias in (1.01, 1.25, 1.5, 2.0):
                increments, probabilities = enumerate_peripheral_increment_law(k, p_bias)
                mean = probabilities @ increments
                raw_second = np.einsum("r,ri,rj->ij", probabilities, increments, increments)
                covariance = raw_second - np.outer(mean, mean)
                expected_mean, expected_covariance = closed_form_peripheral_moments(k, p_bias)
                np.testing.assert_allclose(mean, expected_mean, atol=1e-14, rtol=0.0)
                np.testing.assert_allclose(covariance, expected_covariance, atol=1e-14, rtol=0.0)
                self.assertAlmostEqual(
                    covariance[0, 0] - covariance[0, 1], 2.0 / (k - 1), places=14
                )

    def test_k3_gaussian_max_and_correction_are_exact(self):
        theory = competition_theory(3, 1.5)
        self.assertAlmostEqual(theory.kappa, 1.0 / math.sqrt(math.pi), places=12)
        expected = theory.kappa * math.sqrt(3.0 / 0.5) / theory.v
        self.assertAlmostEqual(theory.mean_correction_coefficient, expected, places=13)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -m unittest -v test_t12_positive_competition.T12TheoryTests
```

Expected: import failure for missing `t12_positive_competition_validation`.

- [ ] **Step 3: Implement the minimal theory API**

Use one event row per possible directed transfer and calculate probabilities from the model contract:

```python
@dataclass(frozen=True)
class CompetitionTheory:
    k: int
    p_bias: float
    delta: float
    peripheral_count: int
    v: float
    tstar_per_capacity: float
    kappa: float
    gaussian_difference_scale: float
    mean_correction_coefficient: float

def _validate_parameters(k: int, p_bias: float) -> None:
    if isinstance(k, bool) or not isinstance(k, (int, np.integer)) or k < 3:
        raise ValueError("k must be an integer at least 3")
    if not (1.0 < p_bias <= 2.0):
        raise ValueError("p_bias must lie in (1,2]")

def closed_form_peripheral_moments(k: int, p_bias: float):
    _validate_parameters(k, p_bias)
    delta = p_bias - 1.0
    v = 2.0 * delta / (k * (k - 1))
    m = k - 1
    mean = np.full(m, -v, dtype=np.float64)
    covariance = np.full((m, m), -2.0 / (k * (k - 1)) - v * v)
    np.fill_diagonal(covariance, 2.0 / k - v * v)
    return mean, covariance

def enumerate_peripheral_increment_law(k: int, p_bias: float):
    _validate_parameters(k, p_bias)
    m = k - 1
    pair_probability = 2.0 / (k * (k - 1))
    rows, probabilities = [], []
    for r in range(m):
        toward = np.zeros(m)
        toward[r] = -1.0
        away = -toward
        rows.extend((toward, away))
        probabilities.extend(
            (pair_probability * p_bias / 2.0,
             pair_probability * (2.0 - p_bias) / 2.0)
        )
    for left in range(m):
        for right in range(left + 1, m):
            increment = np.zeros(m)
            increment[left], increment[right] = -1.0, 1.0
            rows.extend((increment, -increment))
            probabilities.extend((pair_probability / 2.0, pair_probability / 2.0))
    return np.asarray(rows), np.asarray(probabilities)

def gaussian_max_mean(count: int) -> float:
    if isinstance(count, bool) or not isinstance(count, (int, np.integer)) or count < 1:
        raise ValueError("count must be a positive integer")
    if count == 1:
        return 0.0
    def integrand(x: float) -> float:
        cdf = ndtr(x)
        return 1.0 - cdf**count - (1.0 - cdf)**count
    return float(quad(integrand, 0.0, np.inf, epsabs=1e-12)[0])

def competition_theory(k: int, p_bias: float) -> CompetitionTheory:
    _validate_parameters(k, p_bias)
    delta = p_bias - 1.0
    v = 2.0 * delta / (k * (k - 1))
    kappa = gaussian_max_mean(k - 1)
    scale = math.sqrt(k / delta)
    return CompetitionTheory(
        k=k, p_bias=p_bias, delta=delta, peripheral_count=k - 1,
        v=v, tstar_per_capacity=1.0 / v, kappa=kappa,
        gaussian_difference_scale=scale,
        mean_correction_coefficient=kappa * scale / v,
    )
```

Implement `gaussian_max_mean` with the same convergent integral already used in `drift_experiments.py`, but keep the new module self-contained so artifact hashes capture the complete formal calculation.

- [ ] **Step 4: Run theory tests to GREEN and run existing drift tests**

```powershell
python -m unittest -v test_t12_positive_competition.T12TheoryTests
python -m unittest -v test_drift
```

Expected: all selected tests pass with no warnings.

- [ ] **Step 5: Record checkpoint hash**

```powershell
Get-FileHash -Algorithm SHA256 t12_positive_competition_validation.py,test_t12_positive_competition.py
```

Record the two hashes in the eventual QA log; do not create a Git repository.

---

### Task 2: Coupled Free-Walk and First-Depletion Simulator

**Files:**
- Modify: `t12_positive_competition_validation.py`
- Modify: `test_t12_positive_competition.py`

**Interfaces:**
- Consumes: `competition_theory(k, p_bias)`.
- Produces: `T12CoupledSample` and `simulate_coupled_competition(k, N, p_bias, repetitions, seed)`.

- [ ] **Step 1: Write failing simulator tests**

```python
class T12CoupledSimulationTests(unittest.TestCase):
    def test_simulator_is_reproducible_conservative_and_uncensored(self):
        first = simulate_coupled_competition(3, 8, 1.5, 500, seed=12001)
        second = simulate_coupled_competition(3, 8, 1.5, 500, seed=12001)
        np.testing.assert_array_equal(first.stopping_times, second.stopping_times)
        np.testing.assert_array_equal(first.martingale_at_nstar, second.martingale_at_nstar)
        np.testing.assert_array_equal(first.terminal_balances.sum(axis=1), np.full(500, 24))
        self.assertTrue(np.all(first.stopping_times >= 1))
        self.assertEqual(first.censored_count, 0)
        self.assertTrue(np.all(np.min(first.terminal_balances, axis=1) == 0))

    def test_local_proxy_uses_the_same_deterministic_time_martingale(self):
        sample = simulate_coupled_competition(4, 6, 2.0, 200, seed=12002)
        theory = competition_theory(4, 2.0)
        expected = 6.0 / theory.v + np.min(sample.martingale_at_nstar, axis=1) / theory.v
        np.testing.assert_allclose(sample.local_proxy_times, expected, atol=0.0, rtol=0.0)
        self.assertEqual(sample.nstar, math.floor(6.0 / theory.v))
```

- [ ] **Step 2: Verify RED**

```powershell
python -m unittest -v test_t12_positive_competition.T12CoupledSimulationTests
```

Expected: missing `T12CoupledSample` or `simulate_coupled_competition`.

- [ ] **Step 3: Implement exact shared-stream simulation**

Define the result contract:

```python
@dataclass(frozen=True)
class T12CoupledSample:
    stopping_times: np.ndarray
    martingale_at_nstar: np.ndarray
    local_proxy_times: np.ndarray
    terminal_balances: np.ndarray
    nstar: int
    seed: int
    censored_count: int
    generated_rows: int
```

The loop must draw events for every row until `nstar` even if it has already depleted, because `martingale_at_nstar` belongs to the free extension. After `nstar`, draw only rows whose first depletion has not occurred. Record first depletion once, retain balances at that first depletion in `terminal_balances`, and never impose a maximum step count.

Implement the core loop as follows; `_draw_transfers` copies the exact vectorized pair/direction logic from `simulate_drifted_hyperedge` and returns integer sender/receiver arrays of length `count`:

```python
def simulate_coupled_competition(k, N, p_bias, repetitions, seed):
    theory = competition_theory(k, p_bias)
    if isinstance(N, bool) or not isinstance(N, (int, np.integer)) or N < 1:
        raise ValueError("N must be a positive integer")
    if isinstance(repetitions, bool) or repetitions < 2:
        raise ValueError("repetitions must be an integer at least 2")
    rng = np.random.default_rng(seed)
    balances = np.full((repetitions, k), N, dtype=np.int64)
    terminal = np.empty_like(balances)
    stopping_times = np.zeros(repetitions, dtype=np.int64)
    stopped = np.zeros(repetitions, dtype=bool)
    nstar = math.floor(N / theory.v)
    martingale_at_nstar = None
    generated_rows = 0
    step = 0
    all_rows = np.arange(repetitions, dtype=np.int64)
    while step < nstar or np.any(~stopped):
        step += 1
        active = all_rows if step <= nstar else np.flatnonzero(~stopped)
        sender, receiver = _draw_transfers(rng, k, p_bias, active.size)
        balances[active, sender] -= 1
        balances[active, receiver] += 1
        generated_rows += int(active.size)
        newly_local = (~stopped[active]) & (balances[active, sender] == 0)
        newly = active[newly_local]
        stopping_times[newly] = step
        terminal[newly] = balances[newly]
        stopped[newly] = True
        if step == nstar:
            martingale_at_nstar = (
                balances[:, 1:].astype(np.float64) - (N - theory.v * nstar)
            ).copy()
    if martingale_at_nstar is None:
        raise RuntimeError("deterministic reference time was not recorded")
    local_proxy = N / theory.v + np.min(martingale_at_nstar, axis=1) / theory.v
    return T12CoupledSample(
        stopping_times=stopping_times,
        martingale_at_nstar=martingale_at_nstar,
        local_proxy_times=local_proxy,
        terminal_balances=terminal,
        nstar=nstar,
        seed=seed,
        censored_count=int(np.count_nonzero(stopping_times == 0)),
        generated_rows=generated_rows,
    )
```

At `nstar`, calculate the centered peripheral martingale exactly as

```python
martingale_at_nstar = balances[:, 1:].astype(float) - (N - theory.v * nstar)
local_proxy_times = N / theory.v + np.min(martingale_at_nstar, axis=1) / theory.v
```

Use the same pair/direction sampling semantics as `simulate_drifted_hyperedge`, but copy the small event-draw logic rather than calling that stopping-only simulator.

- [ ] **Step 4: Verify GREEN and cross-check marginal stopping times**

```powershell
python -m unittest -v test_t12_positive_competition.T12CoupledSimulationTests
python -m unittest -v test_t12_positive_competition
```

Add a deterministic-seed distributional cross-check using 20,000 paths against `simulate_drifted_hyperedge`; require the two independent sample means to differ by less than `3.5 * sqrt(se1**2 + se2**2)`.

- [ ] **Step 5: Record performance checkpoint**

Run a non-formal benchmark without writing results:

```powershell
Measure-Command { python -c "from t12_positive_competition_validation import simulate_coupled_competition; simulate_coupled_competition(5,320,1.25,2000,12003)" }
```

Record elapsed seconds in the QA log. Performance may change implementation strategy, but must not change random-law semantics, formal grid, repetitions, or stopping rule.

---

### Task 3: Block-Robust Statistics and Gaussian Reference Diagnostics

**Files:**
- Modify: `t12_positive_competition_validation.py`
- Modify: `test_t12_positive_competition.py`

**Interfaces:**
- Consumes: `T12CoupledSample`, `CompetitionTheory`.
- Produces: `T12Scenario`, `build_scenarios`, `bonferroni_t_critical`, `summarize_cell`, `gaussian_reference_quantiles`, `compare_replication_rows`.

- [ ] **Step 1: Write failing scenario and statistics tests**

```python
class T12StatisticsTests(unittest.TestCase):
    def test_formal_grid_has_36_unique_cells_and_disjoint_seeds(self):
        first = build_scenarios(master_seed=2026071812)
        second = build_scenarios(master_seed=2026071813)
        self.assertEqual(len(first), 36)
        self.assertEqual(len({row.cell_id for row in first}), 36)
        self.assertEqual({row.k for row in first}, {3, 4, 5})
        self.assertEqual({row.p_bias for row in first}, {1.25, 1.5, 2.0})
        self.assertEqual({row.N for row in first}, {40, 80, 160, 320})
        self.assertTrue({row.seed for row in first}.isdisjoint({row.seed for row in second}))

    def test_block_summary_reproduces_declared_ratio_and_interval(self):
        sample = T12CoupledSample(
            stopping_times=np.arange(101, 121),
            martingale_at_nstar=np.zeros((20, 2)),
            local_proxy_times=np.arange(100, 120, dtype=float),
            terminal_balances=np.zeros((20, 3), dtype=int),
            nstar=120, seed=1, censored_count=0, generated_rows=20,
        )
        row = summarize_cell(sample, k=3, N=10, p_bias=1.5, blocks=5, comparisons=36)
        theory = competition_theory(3, 1.5)
        expected = (10 / theory.v - np.mean(sample.stopping_times)) / math.sqrt(10)
        self.assertAlmostEqual(row["scaled_correction"], expected)
        self.assertAlmostEqual(row["correction_ratio"], expected / theory.mean_correction_coefficient)
        self.assertGreater(row["simultaneous_half_width"], 0.0)

    def test_replication_interval_is_centered_on_difference(self):
        result = compare_replication_rows(
            np.array([0.9, 1.0, 1.1, 1.0]),
            np.array([0.95, 1.05, 1.0, 1.0]),
            comparisons=36,
        )
        self.assertAlmostEqual(result["difference"], 0.0)
        self.assertLess(result["ci_low"], 0.0)
        self.assertGreater(result["ci_high"], 0.0)
```

- [ ] **Step 2: Verify RED**

```powershell
python -m unittest -v test_t12_positive_competition.T12StatisticsTests
```

Expected: missing scenario/statistics interfaces.

- [ ] **Step 3: Implement block statistics exactly**

Use `student_t.ppf(1 - 0.05 / (2 * comparisons), df=blocks-1)` for the within-run simultaneous critical value. Construct block correction ratios from each contiguous 500-path block; calculate the standard error from the 40 block values, not from repeated time points.

For replication, use Welch's standard error and Satterthwaite degrees of freedom on the two sets of 40 block ratios:

```python
se2 = s1 * s1 / n1 + s2 * s2 / n2
df = se2 * se2 / ((s1*s1/n1)**2/(n1-1) + (s2*s2/n2)**2/(n2-1))
critical = student_t.ppf(1.0 - 0.05/(2.0*comparisons), df=df)
```

Generate target Gaussian quantiles with 1,000,000 base standard-normal draws and their antithetic negatives, fixed reference seed `2026071814`, eigenvalue decomposition of `B/v`, and no use in pass/fail inference. Store the reference sample size and seed in metadata.

- [ ] **Step 4: Verify GREEN and arithmetic edge cases**

```powershell
python -m unittest -v test_t12_positive_competition.T12StatisticsTests
python -m unittest -v test_t12_positive_competition
```

Add tests that reject repetitions not divisible by blocks, blocks below 2, non-finite arrays, constant block values without emitting SciPy precision-loss warnings, and mismatched replication cells.

---

### Task 4: Artifact Pipeline, Exact Anchors, and Overwrite Protection

**Files:**
- Modify: `t12_positive_competition_validation.py`
- Modify: `test_t12_positive_competition.py`

**Interfaces:**
- Produces: `run_t12_validation`, `run_exact_anchors`, `run_replication_comparison`, `run_sensitivity`, and CLI modes `--formal`, `--exact-anchors`, `--compare`, `--sensitivity`, `--quick`.

- [ ] **Step 1: Write failing artifact tests**

```python
class T12ArtifactTests(unittest.TestCase):
    def test_quick_run_writes_hashed_complete_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "t12-quick"
            metadata = run_t12_validation(output, repetitions=200, blocks=20, quick=True)
            self.assertEqual(metadata["row_counts"]["primary"], 36)
            self.assertEqual(metadata["row_counts"]["moments"], 9)
            self.assertTrue(metadata["deterministic_moment_gate_pass"])
            self.assertEqual(metadata["censored_count"], 0)
            self.assertTrue((output / "SHA256SUMS.txt").exists())

    def test_nonempty_output_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "t12-nonempty"
            output.mkdir(parents=True, exist_ok=True)
            (output / "sentinel.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "non-empty"):
                run_t12_validation(output, repetitions=200, blocks=20, quick=True)
            self.assertEqual((output / "sentinel.txt").read_text(encoding="utf-8"), "preserve")

    def test_exact_anchor_quick_mode_recovers_small_state_mean(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "t12-anchor"
            metadata = run_exact_anchors(
                output, N=2, repetitions=2000, blocks=20,
                parameter_pairs=((3, 1.5),),
            )
            self.assertEqual(metadata["row_count"], 1)
            self.assertLess(metadata["maximum_residual"], 1e-10)
```

- [ ] **Step 2: Verify RED**

```powershell
python -m unittest -v test_t12_positive_competition.T12ArtifactTests
```

Expected: missing runner interfaces.

- [ ] **Step 3: Implement schemas and runners**

Write deterministic-order CSVs:

- `t12-primary.csv`: 36 cell summaries plus gate fields;
- `t12-moment-diagnostics.csv`: nine `(k,p)` moment checks, reused across `N`;
- `t12-run-metadata.json`: configuration, software versions, seeds, counts, runtime, thresholds, files;
- `SHA256SUMS.txt`: hashes of every other artifact in the directory.

Exact-anchor output uses `t12-exact-anchors.csv`, metadata, and manifest. Import `exact_drifted_markov_mean` from `drift_experiments`; use the new coupled simulator for Monte Carlo. Build the nine-comparison Student-$t$ interval from 100 block means and store whether it contains the exact mean.

Replication comparison reads two primary CSVs, verifies identical cell IDs/configuration and disjoint seeds, and writes `t12-replication-comparison.csv` plus metadata and manifest without editing either run directory.

The output guard must be:

```python
def _prepare_output(output: Path) -> None:
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
```

- [ ] **Step 4: Verify GREEN and CLI parsing**

```powershell
python -m unittest -v test_t12_positive_competition.T12ArtifactTests
python -m unittest -v test_t12_positive_competition
python -m py_compile t12_positive_competition_validation.py test_t12_positive_competition.py
```

Expected: all T12 tests pass; compilation produces no output.

- [ ] **Step 5: Run full regression before expensive work**

```powershell
python -m unittest -v
```

Expected: all existing and new tests pass. If any frozen test fails, stop before formal simulation.

---

### Task 5: Formal Runs, Independent Replication, Exact Anchors, and Conditional Sensitivity

**Files:**
- Create: `results/t12-positive-competition/*`
- Create: `results/t12-positive-competition-replication/*`
- Create: `results/t12-positive-competition-replication-comparison/*`
- Create: `results/t12-positive-competition-exact-anchors/*`
- Conditionally create: `results/t12-positive-competition-sensitivity/*`

**Interfaces:**
- Consumes only the Task 4 CLI and approved constants.
- Produces frozen numerical evidence; no code changes are allowed during a formal run without discarding the affected run directory as rejected evidence and rerunning from scratch into a fresh directory.

- [ ] **Step 1: Run exact anchors before the large grid**

```powershell
python t12_positive_competition_validation.py --exact-anchors --output results/t12-positive-competition-exact-anchors --N 6 --repetitions 100000 --blocks 100
```

Expected gates: nine rows, all residuals below `1e-10`, all exact means inside the nine-comparison simultaneous intervals, zero censoring.

- [ ] **Step 2: Independently recompute anchor arithmetic and manifest**

Use a read-only PowerShell check to parse metadata, recompute every listed SHA-256, and confirm `anchor_gate_pass=true`. If any check fails, diagnose before the formal grid.

- [ ] **Step 3: Run the primary formal grid**

```powershell
python t12_positive_competition_validation.py --formal --output results/t12-positive-competition --repetitions 20000 --blocks 40 --master-seed 2026071812
```

Expected: 36 primary rows, nine moment rows, maximum deterministic error below `1e-12`, zero censoring, maximum simultaneous correction-ratio half-width at most `0.03`.

- [ ] **Step 4: Run the disjoint-seed replication**

```powershell
python t12_positive_competition_validation.py --formal --output results/t12-positive-competition-replication --repetitions 20000 --blocks 40 --master-seed 2026071813
```

Expected: same structural gates, disjoint cell seeds, no byte-identity requirement.

- [ ] **Step 5: Compare the two formal runs**

```powershell
python t12_positive_competition_validation.py --compare --primary results/t12-positive-competition/t12-primary.csv --replication results/t12-positive-competition-replication/t12-primary.csv --output results/t12-positive-competition-replication-comparison
```

Expected: 36 matched cells and every simultaneous 95% Welch interval for the correction-ratio difference contains zero.

- [ ] **Step 6: Trigger sensitivity only when declared gates require it**

If the maximum primary half-width exceeds `0.03` or a replication interval excludes zero, select exactly the union of those predeclared failing cells and run:

```powershell
python t12_positive_competition_validation.py --sensitivity --cells-file results/t12-positive-competition-replication-comparison/t12-failing-cells.txt --output results/t12-positive-competition-sensitivity --repetitions 100000 --blocks 100 --master-seed 2026071815
```

Do not run sensitivity when both gates pass. Preserve the original rows either way.

- [ ] **Step 7: Independently verify all formal artifacts**

Check row counts, parameter grids, seed disjointness, block sizes, interval arithmetic, quantile ordering, zero censoring, manifests, JSON parsing, and absence of `NaN`/`Inf`. Record exact maxima and any failed gate; do not round a failed value into a pass.

---

### Task 6: Complete the Mathematical Proof Package

**Files:**
- Create: `outputs/researchwrite/hypergraph-stopping-time/17_t12_positive_competition_proof_and_validation.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/06_theorem_proof_gap_register.md`

**Interfaces:**
- Consumes the approved design, exact algebra from Task 1, and formal results from Task 5.
- Produces the internal T12 theorem statement, complete proof, and strict claim boundary.

- [ ] **Step 1: Write the theorem with all quantifiers and definitions**

State fixed `k >= 3`, fixed `p in (1,2]`, `v`, `t_N^*`, `B`, `G`, and `H`, followed by distribution convergence, every-fixed-`q` absolute moment convergence, and the equivalent mean expansions from the approved spec.

- [ ] **Step 2: Prove the local process limit**

Write the deterministic-time multivariate CLT and, for each fixed compact window, bound the local centered increment maximum. An acceptable explicit inequality is

\[
\Pr\!\left(
\max_{|j|\le C\sqrt N}
\|M(n_N+j)-M(n_N)\|_\infty>\varepsilon\sqrt N
\right)
\le 2k\exp(-c_{C,\varepsilon}\sqrt N),
\]

after splitting forward/backward increments and applying a bounded-difference maximal inequality. Include all floor errors as `O(1)/sqrt(N)`.

- [ ] **Step 3: Prove exit-map continuity and remove the center coordinate**

Use tightness of the rescaled exit time plus compact local convergence. The limiting coordinate paths `G_r-vs` have unique strict zero crossings. Bound center depletion before `t_N^*+C sqrt(N)` by `C_1 exp(-c_1 N)` because its deterministic balance is order `N` throughout that window.

- [ ] **Step 4: Prove uniform integrability**

Derive early and late bounds on `P(|(tau_N-t_N^*)/sqrt(N)| > x)`. Split `x` into the Gaussian window `1 <= x <= c sqrt(N)` and the far late tail. Use the T11 geometric tail beyond `2t_N^*`. Integrate the tail identity

\[
\mathbb E|Y_N|^q=q\int_0^\infty x^{q-1}\Pr(|Y_N|>x)\,dx
\]

to obtain uniform integrability for every fixed `q>0`.

- [ ] **Step 5: Derive the Gaussian extremum coefficient without false independence**

Project `G` onto the mean-zero peripheral subspace, show its covariance equals `(gamma-c)/v` times the covariance of `Z-bar(Z)1`, and use `E bar(G)=0` plus symmetry to get `E min(G)=-kappa_m sqrt((gamma-c)/v)`. Substitute `gamma-c=2/(k-1)` and `v=2(p-1)/(k(k-1))`.

- [ ] **Step 6: Add numerical evidence with bounded wording**

Report exact anchors, formal uncertainty, independent replication, local-proxy diagnostics, and any sensitivity outcome. Explicitly say that simulation checks implementation and finite-grid alignment but does not establish the theorem.

- [ ] **Step 7: Update T12 status conditionally**

Only if Tasks 1–5 pass, change T12 from `C` to `A — internally closed, external review unsigned`, replace the old strong-approximation plan with the completed local-CLT proof route, and preserve the external-review requirement.

---

### Task 7: Project QA, State Update, and Final Verification

**Files:**
- Create: `outputs/researchwrite/hypergraph-stopping-time/qa_logs/2026-07-18_t12_positive_competition.md`
- Modify: `outputs/researchwrite/hypergraph-stopping-time/state.json`
- Modify: `README.md`

**Interfaces:**
- Consumes every prior task artifact.
- Produces the final internal handoff without changing `publication_readiness` to true.

- [ ] **Step 1: Write the QA record**

Include every RED failure and GREEN command, benchmark time, exact-anchor gates, both formal runtimes, precision maximum, replication results, sensitivity decision, deterministic errors, independent arithmetic checks, test count, file hashes, and protected-evidence hashes.

- [ ] **Step 2: Update state conservatively**

Remove `positive_drift_competition_error_not_bounded` only if the proof and all mandatory gates pass. Keep `publication_readiness=false`, keep external-review debts, set `last_completed` to `t12_positive_drift_competition_proof_and_validation`, and recompute `submission_completion_percent` from the same checklist used in document 15 rather than assigning an arbitrary number.

- [ ] **Step 3: Update README authoritative links**

Add links to document 17, the T12 QA log, primary/replication/comparison/exact result directories, and state that T12 is internally closed but externally unsigned. Do not describe the finite grid as proof.

- [ ] **Step 4: Run final technical verification**

```powershell
python -m py_compile t12_positive_competition_validation.py test_t12_positive_competition.py
python -m unittest -v
```

Expected: compilation succeeds silently and every test passes with no warning or error.

- [ ] **Step 5: Run final document and evidence verification**

Parse every changed JSON as UTF-8; resolve local Markdown links in `README.md`, documents 06/17, and the T12 QA log; scan for control characters and stale T12-C wording; recompute every formal manifest; verify the 11 previously protected result hashes and frozen HTML hash; confirm `publication_readiness=false` and external signatures remain absent.

- [ ] **Step 6: Apply the completion boundary**

If any mandatory mathematical, exact-anchor, precision, replication, manifest, regression, or protected-evidence gate fails, leave T12 at C and document the failure. If all pass, report T12 as internally closed only; do not mark the publication goal complete and do not start manuscript writing in this task.
