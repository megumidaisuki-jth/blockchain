import csv
from contextlib import redirect_stdout
import hashlib
import io
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest import mock

import numpy as np
from scipy.stats import t as student_t

from t12_positive_competition_validation import (
    T12CoupledSample,
    bonferroni_t_critical,
    build_scenarios,
    compare_replication_rows,
    closed_form_peripheral_moments,
    competition_theory,
    enumerate_peripheral_increment_law,
    gaussian_reference_quantiles,
    run_exact_anchors,
    run_replication_comparison,
    run_sensitivity,
    run_t12_validation,
    simulate_coupled_competition,
    summarize_cell,
)
from drift_experiments import simulate_drifted_hyperedge


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

    def test_stopping_time_marginal_matches_drifted_hyperedge(self):
        repetitions = 20_000
        coupled = simulate_coupled_competition(4, 8, 1.5, repetitions, seed=12004)
        independent = simulate_drifted_hyperedge(4, 8, 1.5, repetitions, seed=12005)
        coupled_values = coupled.stopping_times.astype(np.float64)
        independent_values = independent.astype(np.float64)
        se_coupled = coupled_values.std(ddof=1) / math.sqrt(repetitions)
        se_independent = independent_values.std(ddof=1) / math.sqrt(repetitions)
        self.assertLess(
            abs(coupled_values.mean() - independent_values.mean()),
            3.5 * math.sqrt(se_coupled**2 + se_independent**2),
        )


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
            nstar=120,
            seed=1,
            censored_count=0,
            generated_rows=20,
        )
        row = summarize_cell(sample, k=3, N=10, p_bias=1.5, blocks=5, comparisons=36)
        theory = competition_theory(3, 1.5)
        expected = (10 / theory.v - np.mean(sample.stopping_times)) / math.sqrt(10)
        self.assertAlmostEqual(row["scaled_correction"], expected)
        self.assertAlmostEqual(row["correction_ratio"], expected / theory.mean_correction_coefficient)
        block_means = sample.stopping_times.reshape(5, 4).mean(axis=1)
        block_ratios = (
            (10 / theory.v - block_means)
            / math.sqrt(10)
            / theory.mean_correction_coefficient
        )
        expected_se = block_ratios.std(ddof=1) / math.sqrt(5)
        expected_critical = student_t.ppf(1.0 - 0.05 / (2.0 * 36), df=4)
        self.assertAlmostEqual(row["block_standard_error"], expected_se, places=15)
        self.assertAlmostEqual(row["simultaneous_critical"], expected_critical, places=15)
        self.assertAlmostEqual(
            row["simultaneous_half_width"], expected_se * expected_critical, places=15
        )

    def test_replication_interval_is_centered_on_difference(self):
        result = compare_replication_rows(
            np.array([0.9, 1.0, 1.1, 1.0]),
            np.array([0.95, 1.05, 1.0, 1.0]),
            comparisons=36,
        )
        self.assertAlmostEqual(result["difference"], 0.0)
        self.assertLess(result["ci_low"], 0.0)
        self.assertGreater(result["ci_high"], 0.0)
        first = np.array([0.9, 1.0, 1.1, 1.0])
        second = np.array([0.95, 1.05, 1.0, 1.0])
        v1 = first.var(ddof=1) / first.size
        v2 = second.var(ddof=1) / second.size
        expected_df = (v1 + v2) ** 2 / (
            v1**2 / (first.size - 1) + v2**2 / (second.size - 1)
        )
        expected_se = math.sqrt(v1 + v2)
        expected_critical = student_t.ppf(1.0 - 0.05 / (2.0 * 36), df=expected_df)
        self.assertAlmostEqual(result["welch_standard_error"], expected_se, places=15)
        self.assertAlmostEqual(result["degrees_of_freedom"], expected_df, places=14)
        self.assertAlmostEqual(result["simultaneous_critical"], expected_critical, places=14)

    def test_statistics_reject_invalid_block_shapes_and_nonfinite_values(self):
        sample = T12CoupledSample(
            stopping_times=np.arange(10, dtype=float),
            martingale_at_nstar=np.zeros((10, 2)),
            local_proxy_times=np.zeros(10),
            terminal_balances=np.zeros((10, 3), dtype=int),
            nstar=1,
            seed=1,
            censored_count=0,
            generated_rows=10,
        )
        with self.assertRaises(ValueError):
            summarize_cell(sample, k=3, N=10, p_bias=1.5, blocks=3)
        with self.assertRaises(ValueError):
            summarize_cell(sample, k=3, N=10, p_bias=1.5, blocks=1)
        sample_with_nan = T12CoupledSample(
            stopping_times=np.array([1.0, np.nan]),
            martingale_at_nstar=np.zeros((2, 2)),
            local_proxy_times=np.zeros(2),
            terminal_balances=np.zeros((2, 3), dtype=int),
            nstar=1,
            seed=1,
            censored_count=0,
            generated_rows=2,
        )
        with self.assertRaises(ValueError):
            summarize_cell(sample_with_nan, k=3, N=10, p_bias=1.5, blocks=2)
        with self.assertRaises(ValueError):
            compare_replication_rows(np.array([1.0, np.nan]), np.array([1.0, 1.0]))

    def test_constant_blocks_and_gaussian_reference_are_stable_and_seeded(self):
        result = compare_replication_rows(
            np.ones(4), np.ones(4), comparisons=36
        )
        self.assertEqual(result["difference"], 0.0)
        self.assertEqual(result["ci_low"], 0.0)
        self.assertEqual(result["ci_high"], 0.0)
        self.assertTrue(math.isfinite(result["simultaneous_critical"]))
        reference = gaussian_reference_quantiles(3, 1.5, base_draws=100, seed=17)
        repeated = gaussian_reference_quantiles(3, 1.5, base_draws=100, seed=17)
        self.assertEqual(reference["reference_seed"], 17)
        self.assertEqual(reference["reference_sample_size"], 200)
        np.testing.assert_array_equal(reference["correction_ratio_quantiles"], repeated["correction_ratio_quantiles"])
        self.assertGreater(bonferroni_t_critical(40, comparisons=36), 0.0)

    def test_replication_rows_reject_mismatched_cell_identifiers(self):
        first = {"cell_id": "k3-p1.5-N40", "block_correction_ratios": np.ones(2)}
        second = {"cell_id": "k3-p1.5-N80", "block_correction_ratios": np.ones(2)}
        with self.assertRaisesRegex(ValueError, "replication cells must match"):
            compare_replication_rows(first, second)


class T12ArtifactTests(unittest.TestCase):
    @staticmethod
    def _assert_manifest_complete(output: Path) -> None:
        manifest = output / "SHA256SUMS.txt"
        entries = {}
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest, name = line.split("  ", 1)
            entries[name] = digest
        expected_names = sorted(
            path.name for path in output.iterdir() if path.name != manifest.name
        )
        testcase = unittest.TestCase()
        testcase.assertEqual(list(entries), expected_names)
        testcase.assertNotIn(manifest.name, entries)
        for name, digest in entries.items():
            testcase.assertEqual(
                digest, hashlib.sha256((output / name).read_bytes()).hexdigest()
            )

    def test_quick_run_writes_hashed_complete_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "t12-quick"
            metadata = run_t12_validation(
                output,
                repetitions=200,
                blocks=20,
                quick=True,
                reference_base_draws=100,
            )
            self.assertEqual(metadata["row_counts"]["primary"], 36)
            self.assertEqual(metadata["row_counts"]["moments"], 9)
            self.assertTrue(metadata["deterministic_moment_gate_pass"])
            self.assertEqual(metadata["censored_count"], 0)
            self.assertFalse(metadata["precision_gate_applicable"])
            self.assertTrue((output / "SHA256SUMS.txt").exists())
            with (output / "t12-primary.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(
                [row["cell_id"] for row in rows],
                sorted(row["cell_id"] for row in rows),
            )
            self.assertTrue(all(json.loads(row["block_correction_ratios"]) for row in rows))
            parsed_metadata = json.loads(
                (output / "t12-run-metadata.json").read_text(encoding="utf-8")
            )
            self.assertEqual(parsed_metadata["row_counts"], metadata["row_counts"])
            self._assert_manifest_complete(output)

    def test_nonempty_output_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "t12-nonempty"
            output.mkdir(parents=True, exist_ok=True)
            (output / "sentinel.txt").write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(FileExistsError, "non-empty"):
                run_t12_validation(output, repetitions=200, blocks=20, quick=True)
            self.assertEqual(
                (output / "sentinel.txt").read_text(encoding="utf-8"), "preserve"
            )

    def test_exact_anchor_quick_mode_recovers_small_state_mean(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "t12-anchor"
            metadata = run_exact_anchors(
                output,
                N=2,
                repetitions=2000,
                blocks=20,
                parameter_pairs=((3, 1.5),),
            )
            self.assertEqual(metadata["row_count"], 1)
            self.assertLess(metadata["maximum_residual"], 1e-10)
            self.assertEqual(metadata["censored_count"], 0)
            with (output / "t12-exact-anchors.csv").open(
                encoding="utf-8", newline=""
            ) as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(int(row["comparisons"]), 9)
            self.assertAlmostEqual(
                float(row["simultaneous_half_width"]),
                float(row["block_standard_error"])
                * float(row["simultaneous_critical"]),
                places=14,
            )
            self._assert_manifest_complete(output)

    def test_replication_comparison_rejects_truncated_minimal_inputs(self):
        fields = (
            "cell_id",
            "k",
            "N",
            "p_bias",
            "seed",
            "repetitions",
            "blocks",
            "comparisons",
            "simultaneous_half_width",
            "block_correction_ratios",
        )

        def write_primary(path: Path, *, seed: int, N: int = 40) -> None:
            with path.open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
                writer.writeheader()
                writer.writerow(
                    {
                        "cell_id": "k3-p1.5-N40",
                        "k": 3,
                        "N": N,
                        "p_bias": 1.5,
                        "seed": seed,
                        "repetitions": 4,
                        "blocks": 4,
                        "comparisons": 36,
                        "simultaneous_half_width": 0.02,
                        "block_correction_ratios": json.dumps([0.9, 1.0, 1.1, 1.0]),
                    }
                )

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            primary = root / "primary.csv"
            replication = root / "replication.csv"
            write_primary(primary, seed=1)
            write_primary(replication, seed=2)
            with self.assertRaisesRegex(ValueError, "schema|canonical|36"):
                run_replication_comparison(primary, replication, root / "truncated")

    def test_replication_and_sensitivity_runners_write_handoff_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "first"
            second = root / "second"
            run_t12_validation(
                first,
                repetitions=200,
                blocks=20,
                master_seed=120,
                quick=True,
                reference_base_draws=50,
            )
            run_t12_validation(
                second,
                repetitions=200,
                blocks=20,
                master_seed=121,
                quick=True,
                reference_base_draws=50,
            )
            comparison = root / "comparison"
            comparison_metadata = run_replication_comparison(
                first / "t12-primary.csv",
                second / "t12-primary.csv",
                comparison,
            )
            self.assertEqual(comparison_metadata["row_count"], 36)
            self.assertTrue(comparison_metadata["seeds_disjoint"])
            self.assertTrue((comparison / "t12-failing-cells.txt").exists())
            self._assert_manifest_complete(comparison)

            def read_primary(path: Path):
                with path.open(encoding="utf-8", newline="") as handle:
                    reader = csv.DictReader(handle)
                    return tuple(reader.fieldnames or ()), list(reader)

            def write_primary(path: Path, fields, rows) -> None:
                with path.open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(
                        handle, fieldnames=fields, lineterminator="\n"
                    )
                    writer.writeheader()
                    writer.writerows(rows)

            fields, first_rows = read_primary(first / "t12-primary.csv")
            _, second_rows = read_primary(second / "t12-primary.csv")

            truncated_first = root / "truncated-first.csv"
            truncated_second = root / "truncated-second.csv"
            write_primary(truncated_first, fields, first_rows[:1])
            write_primary(truncated_second, fields, second_rows[:1])
            with self.assertRaisesRegex(ValueError, "canonical|36"):
                run_replication_comparison(
                    truncated_first,
                    truncated_second,
                    root / "truncated-comparison",
                )

            reduced_fields = tuple(field for field in fields if field != "mean_stopping_time")
            reduced_first_rows = [
                {field: row[field] for field in reduced_fields} for row in first_rows
            ]
            reduced_second_rows = [
                {field: row[field] for field in reduced_fields} for row in second_rows
            ]
            missing_first = root / "missing-first.csv"
            missing_second = root / "missing-second.csv"
            write_primary(missing_first, reduced_fields, reduced_first_rows)
            write_primary(missing_second, reduced_fields, reduced_second_rows)
            with self.assertRaisesRegex(ValueError, "schema"):
                run_replication_comparison(
                    missing_first,
                    missing_second,
                    root / "missing-comparison",
                )

            forged_first_rows = [dict(row) for row in first_rows]
            forged_second_rows = [dict(row) for row in second_rows]
            forged_first_rows[0]["cell_id"] = "forged-cell"
            forged_second_rows[0]["cell_id"] = "forged-cell"
            forged_first = root / "forged-first.csv"
            forged_second = root / "forged-second.csv"
            write_primary(forged_first, fields, forged_first_rows)
            write_primary(forged_second, fields, forged_second_rows)
            with self.assertRaisesRegex(ValueError, "canonical"):
                run_replication_comparison(
                    forged_first,
                    forged_second,
                    root / "forged-comparison",
                )

            comparisons_first_rows = [dict(row) for row in first_rows]
            comparisons_second_rows = [dict(row) for row in second_rows]
            for row in comparisons_first_rows + comparisons_second_rows:
                row["comparisons"] = "35"
            comparisons_first = root / "comparisons-first.csv"
            comparisons_second = root / "comparisons-second.csv"
            write_primary(comparisons_first, fields, comparisons_first_rows)
            write_primary(comparisons_second, fields, comparisons_second_rows)
            with self.assertRaisesRegex(ValueError, "comparisons.*36"):
                run_replication_comparison(
                    comparisons_first,
                    comparisons_second,
                    root / "comparisons-comparison",
                )

            shape_second_rows = [dict(row) for row in second_rows]
            shape_second_rows[0]["paths_per_block"] = "999"
            shape_second = root / "shape-second.csv"
            write_primary(shape_second, fields, shape_second_rows)
            with self.assertRaisesRegex(ValueError, "configuration"):
                run_replication_comparison(
                    first / "t12-primary.csv",
                    shape_second,
                    root / "shape-comparison",
                )

            reference_second_rows = [dict(row) for row in second_rows]
            reference_second_rows[0]["reference_sample_size"] = "999"
            reference_second = root / "reference-second.csv"
            write_primary(reference_second, fields, reference_second_rows)
            with self.assertRaisesRegex(ValueError, "configuration"):
                run_replication_comparison(
                    first / "t12-primary.csv",
                    reference_second,
                    root / "reference-comparison",
                )

            duplicate_seed_rows = [dict(row) for row in first_rows]
            duplicate_seed_rows[0]["seed"] = duplicate_seed_rows[1]["seed"]
            duplicate_seed = root / "duplicate-seed.csv"
            write_primary(duplicate_seed, fields, duplicate_seed_rows)
            with self.assertRaisesRegex(ValueError, "36 unique seeds"):
                run_replication_comparison(
                    duplicate_seed,
                    second / "t12-primary.csv",
                    root / "duplicate-seed-comparison",
                )

            overlapping_seed_rows = [dict(row) for row in second_rows]
            overlapping_seed_rows[0]["seed"] = first_rows[0]["seed"]
            overlapping_seed = root / "overlapping-seed.csv"
            write_primary(overlapping_seed, fields, overlapping_seed_rows)
            with self.assertRaisesRegex(ValueError, "disjoint"):
                run_replication_comparison(
                    first / "t12-primary.csv",
                    overlapping_seed,
                    root / "overlapping-seed-comparison",
                )

            cells_file = root / "selected.txt"
            cells_file.write_text("k3-p1.5-N40\n", encoding="utf-8")
            sensitivity = root / "sensitivity"
            sensitivity_metadata = run_sensitivity(
                sensitivity,
                cells_file=cells_file,
                repetitions=200,
                blocks=20,
                master_seed=122,
                reference_base_draws=50,
            )
            self.assertEqual(sensitivity_metadata["row_count"], 1)
            self.assertEqual(sensitivity_metadata["cell_ids"], ["k3-p1.5-N40"])
            self._assert_manifest_complete(sensitivity)

    def test_cli_explicit_zero_numeric_arguments_are_not_replaced_by_defaults(self):
        cases = (
            (
                "run_exact_anchors",
                ["--exact-anchors"],
                {"repetitions": 0, "blocks": 0},
            ),
            (
                "run_sensitivity",
                ["--sensitivity", "--cells-file", "cells.txt"],
                {"repetitions": 0, "blocks": 0, "reference_base_draws": 0},
            ),
            (
                "run_t12_validation",
                ["--quick"],
                {"repetitions": 0, "blocks": 0, "reference_base_draws": 0},
            ),
        )
        with tempfile.TemporaryDirectory() as temporary:
            for runner_name, mode_arguments, expected in cases:
                with self.subTest(runner=runner_name):
                    output = Path(temporary) / runner_name
                    arguments = [
                        *mode_arguments,
                        "--output",
                        str(output),
                        "--repetitions",
                        "0",
                        "--blocks",
                        "0",
                        "--reference-base-draws",
                        "0",
                    ]
                    with mock.patch(
                        f"t12_positive_competition_validation.{runner_name}",
                        return_value={"all_gates_pass": True, "model": "test"},
                    ) as runner, redirect_stdout(io.StringIO()):
                        from t12_positive_competition_validation import main

                        main(arguments)
                    for name, value in expected.items():
                        self.assertEqual(runner.call_args.kwargs[name], value)

    def test_cli_explicit_zero_numeric_arguments_fail_runner_validation(self):
        cases = (
            ["--exact-anchors", "--repetitions", "0"],
            ["--exact-anchors", "--repetitions", "2", "--blocks", "0"],
            ["--sensitivity", "--cells-file", "unused.txt", "--repetitions", "0"],
            [
                "--sensitivity",
                "--cells-file",
                "unused.txt",
                "--repetitions",
                "2",
                "--blocks",
                "0",
            ],
            [
                "--sensitivity",
                "--cells-file",
                "unused.txt",
                "--repetitions",
                "2",
                "--blocks",
                "2",
                "--reference-base-draws",
                "0",
            ],
            ["--quick", "--repetitions", "0"],
            ["--quick", "--repetitions", "2", "--blocks", "0"],
            [
                "--quick",
                "--repetitions",
                "2",
                "--blocks",
                "2",
                "--reference-base-draws",
                "0",
            ],
        )
        from t12_positive_competition_validation import main

        with tempfile.TemporaryDirectory() as temporary:
            for index, mode_arguments in enumerate(cases):
                with self.subTest(arguments=mode_arguments), self.assertRaises(ValueError):
                    main(
                        [
                            *mode_arguments,
                            "--output",
                            str(Path(temporary) / f"output-{index}"),
                        ]
                    )
