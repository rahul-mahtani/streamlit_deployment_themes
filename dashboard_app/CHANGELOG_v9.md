# Dashboard v9 changes

- Reordered navigation so Macro monitor and Macro regimes appear immediately after Research overview, ahead of theme and instrument research pages.
- Added a selected-metric chart to Theme landscape. The chart responds to the same priority, mapping-status and macro-context filters as the table.
- Changed Theme evidence > Performance across macro conditions to foreground annualised arithmetic conditional returns and annualised differences versus the eligible-month baseline. Monthly tail statistics remain explicitly labelled as monthly.
- Added Instrument detail > Performance across macro conditions, using the instrument-level regime performance output. Duplicate rows arising from multiple theme memberships are removed because the underlying instrument/condition performance is the same. Includes conditional annualised returns, annualised risk, baseline comparisons, sample depth, chart and CSV download.
- Added a bundled instrument regime-performance snapshot as fallback; live reports take precedence.

Annualised arithmetic return is 12 times the mean monthly return, not compounded CAGR. Conditional results with fewer than 12 observations are flagged as highly indicative only. All regime-conditioned results use the existing one-month lag convention.
