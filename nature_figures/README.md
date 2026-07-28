# Nature-style figure bundle

This folder contains the submission-grade redraw of the stopping-time
experiments.

## Figures

| Figure | Main purpose |
|---|---|
| figure1_overall_validation | Primary formula-versus-simulation validation |
| figure2_error_landscape | Error heatmaps across \(N\), \(p\) and \(k\) |
| figure3_stopping_time_scaling | Capacity, hyperedge-size and drift scaling |
| figure4_uncertainty_audit | Worst-case intervals and acceptance criteria |

Each figure is available in:

- svg/ — primary editable vector artwork;
- pdf/ — manuscript-ready vector PDF;
- tiff/ — 600 dpi LZW-compressed raster;
- png/ — 300 dpi preview.

Additional material:

- FIGURE_LEGENDS.md — self-contained Nature-style legends;
- FIGURE_CONTRACT.md — claim, evidence map and reviewer-risk contract;
- QA_NOTES.md — data integrity, statistical definitions and export audit;
- source_data/ — source data for every quantitative panel;
- make_nature_figures.py — fully reproducible Python/matplotlib source.

Run from the project root:

    $env:TEMP='E:\newblockchain\.tmp'
    $env:TMP='E:\newblockchain\.tmp'
    $env:MPLCONFIGDIR='E:\newblockchain\.tmp\matplotlib'
    python nature_figures\make_nature_figures.py
