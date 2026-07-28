# Figure QA notes

## Data integrity

- Input rows: 2,112.
- Unique parameter triples: 2,112.
- Hyperedge coverage: all 48 integers from \(k=3\) through \(k=50\).
- Capacity values: \(N=10,14,28,56,112,128\).
- Validation sources: 1,710 internal blind scenarios, 18 fresh precision
  confirmations and 384 boundary/weak-drift confirmations.
- Missing or non-finite plotted values: 0.
- Figs. 1, 2 and 4 use all observations.
- Fig. 3 uses a declared representative subset:
  \(N\in\{14,56,112\}\),
  \(p\in\{0.325,0.94,1,1.06,1.875\}\), all \(k\), plus a fixed-\(N=56\)
  drift profile for \(k\in\{3,10,30,50\}\). The purpose is curve legibility,
  not accuracy selection.

## Statistical definitions

- Experimental unit: one distinct \((k,N,p)\) simulation scenario.
- Point error:
  \[
  |\widehat T-\overline T_{\mathrm{MC}}|/\overline T_{\mathrm{MC}}.
  \]
- Signed error:
  \[
  (\widehat T-\overline T_{\mathrm{MC}})/\overline T_{\mathrm{MC}}.
  \]
- Monte Carlo centre: arithmetic trajectory mean.
- Monte Carlo spread: sample standard deviation; standard error is
  \(s/\sqrt n\).
- Simultaneous interval: large-sample normal interval with Bonferroni
  correction across 2,130 tests.
- Hypothesis tests and P values: not applicable; none reported.

## Visual and export checks

- Backend: Python/matplotlib only.
- Declared final width: 7.2 in (182.9 mm), Nature-family double-column size.
- Font family: Arial/Helvetica with DejaVu Sans fallback.
- Smallest explicit text: 5.8 pt.
- Panel labels: bold lowercase letters.
- Primary format: SVG with text preserved as editable text nodes.
- Secondary exports: PDF, 600 dpi LZW-compressed TIFF and 300 dpi PNG.
- Colour: restrained blue/teal/violet families; red is reserved for criteria
  and callouts. No rainbow colour map is used.
- Dense scatter marks are rasterized inside vector figures; axes, labels and
  annotations remain vector.
- Image integrity: all panels are quantitative line art; no photographs,
  microscopy crops, local contrast adjustments or pseudocolour transformations
  are present.
- Automated static preflight: 14 PASS, 0 WARN, 0 FAIL.

## Interpretation limit

The figures validate a discrete parameter grid. They do not establish a
uniform mathematical error theorem over every continuous \(p\), every integer
\(N\), arbitrary flow matrices or variable transaction amounts. For
\(k\geq4\), frozen v4 is an empirically validated crossover approximation;
\(k=3\) uses the exact finite-state numerical solution.
