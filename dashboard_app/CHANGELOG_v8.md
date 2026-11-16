# Version 8 — strategist research workflow and evidence integration

## Navigation and research workflow
- Reorganised page labels around the research process: Research overview, Theme landscape, Theme deep dive, Theme evidence, Instrument detail, Instrument exposures, Macro monitor, Macro regimes, Connectivity & data quality, and Metadata & methodology.
- Updated the dashboard introduction to explain its role as a systematic research workspace.
- Added the latest confirmed macro regime, independent growth/inflation states and descriptive subgroup overlay to the Research overview.
- Added theme evidence coverage columns to the Theme landscape.

## New Theme evidence review
- Added a dedicated theme evidence page with five sections: evidence overview, macro sensitivities, equity-style factor context, performance across macro conditions, and economic thesis/mapped instruments.
- Reads the latest `reports/theme_evidence_aggregation/` outputs, with bundled CSV snapshots as a portable fallback.
- Reads `reports/instrument_exposure/theme_instrument_evidence_panel.csv` when present to show instrument roles, mapping caveats and empirical coverage.
- Preserves the four mapping-role scopes. Contextual comparators and alternative implementations are never silently combined with core exposures.
- Shows macro regression families separately, retains predictor IDs for auditability, and labels estimates in plain English.
- Keeps Fama–French factor exposures separate from macro sensitivities.
- Keeps regime-conditioned performance separate from regression evidence and displays sample depth and observation counts.
- Shows the original macro-to-theme transmission hypotheses and their evidence status.

## New Macro regimes view
- Added a dedicated regime-history page showing confirmed regime, candidate regime, growth and inflation states, composite scores, evidence quality and subgroup composition.
- Displays growth and inflation subgroup scores using plain-English labels.
- Explains that subgroup overlays are diagnostic descriptions and do not alter the confirmed four-quadrant regime.

## Interpretation and auditability
- Added plain-English labels for model families, mapping scopes, macro-regime dimensions, subgroup overlays and equity-style factors.
- Raw theme, feature, signal and instrument IDs remain available in detail tables and CSV downloads.
- No source data, research mappings, regression estimates, regime definitions or existing analytics are recalculated or overwritten by this dashboard patch.
