# Nature figure contract

## Core conclusion

The frozen v4 predictor reproduces hyperedge stopping times across every integer
\(k=3,\ldots,50\), remains accurate across capacity and drift regimes, and
keeps the large-sample Bonferroni-normal uncertainty-aware error below 5% on
all 2,112 validation scenarios.

## Figure archetype

Quantitative grid with an asymmetric hero panel in the main figure.

## Target and export

- Target: Nature-family two-column manuscript figures.
- Backend: Python/matplotlib only.
- Final width: 183 mm (7.2 in); dense journal text at 7–8 pt.
- Primary format: editable SVG.
- Secondary formats: PDF, 600 dpi TIFF, 300 dpi PNG preview.
- White background; Arial/Helvetica/DejaVu Sans fallback.

## Evidence hierarchy

### Figure 1 — principal validation

- a: formula-versus-simulation parity for all 2,112 observations (hero evidence);
- b: maximum and 95th-percentile point error for every integer \(k\);
- c: empirical cumulative distributions of point and uncertainty-aware error;
- d: error distributions by validation source, showing confirmatory robustness.

### Figure 2 — parameter landscape

- six aligned heatmaps show absolute relative error over \(k\) and \(p\) at
  \(N=10,14,28,56,112,128\);
- every source observation appears once; blank cells are genuinely untested
  parameter combinations, not excluded results.

### Figure 3 — stopping-time scaling

- formula curves and independent Monte Carlo points are compared across \(k\)
  for representative negative, zero and positive drift;
- panels separate capacity scales to avoid hiding the \(N^2\)-to-\(N\)
  crossover on one axis.

### Figure 4 — uncertainty audit

- a: uncertainty-aware error versus point error for all scenarios;
- b: the 20 largest conservative upper bounds as a forest-style audit;
- c: signed-error distribution across drift regimes;
- d: compact acceptance metrics with predeclared thresholds.

## Statistics and integrity

- Data: 2,112 unique scenarios; 48 integer \(k\) values; no missing numeric
  outputs and no duplicate parameter triples.
- Point error: \(|\widehat T-\overline T_{\mathrm{MC}}|/\overline T_{\mathrm{MC}}\).
- Conservative upper error: worst relative discrepancy between the prediction
  and the endpoints of a Bonferroni-normal simultaneous interval.
- The simultaneous interval is a large-sample normal approximation, not a
  distribution-free finite-sample guarantee.
- No rows are discarded. Dense point clouds are rasterized inside vector
  output to preserve file size without changing the observations.

## Reviewer risks addressed

- The \(k\geq4\) formula is labelled an empirical crossover approximation, not
  a theorem.
- \(k=3\) is identified as the exact finite-state numerical solution.
- Figure legends state the sample count, error definition and interval type.
- Boundary and weak-drift confirmation data are visually distinguished from
  the internal blind grid while keeping a consistent palette.
