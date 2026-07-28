# Real-topology validation figure contract

- Core conclusion: Historical (2020–2023) and current-2026 filtered Lightning projections both show mixed-sign finite-grid effects; independent reruns are broadly consistent, while pooled post-primary sensitivity achieves the prespecified precision target.
- Archetype: quantitative grid.
- Target/output: manuscript-ready double-column figure; Python; 183 mm wide; editable SVG/PDF plus 600 dpi TIFF and PNG preview.
- Panel a: pooled effect estimates and simultaneous confidence intervals for the 48 historical cells.
- Panel b: pooled effect estimates and simultaneous confidence intervals for the 16 current-2026 cells.
- Panel c: replication-versus-formal effect estimates with identity line, reporting correlation and direct replication gate.
- Panel d: simultaneous interval half-widths by analysis layer against the 0.03 precision target.
- Hero evidence: panels a–b.
- Validation evidence: panel c.
- Controls/robustness: panel d.
- Statistics: paired common-random-number mean differences; block-based simultaneous intervals; direct formal/replication comparison via Welch intervals with multiplicity adjustment; pooled result is explicitly post-primary sensitivity.
- Source data: immutable CSV outputs in the corresponding `results/lightning-*` directories; no observations excluded.
- Reviewer risk: the 2026 graph is a filtered, geolocated, high-capacity projection and not the full Lightning Network; pooled estimates must not be presented as replacing the separately frozen primary and replication analyses.
