# Dashboard app patch — Version 4

This patch replaces only `dashboard_app/`. It leaves the collection pipeline, configuration and source data unchanged.

## Install and run

From the project root in `.venv311`:

```bash
python -m pip install -r dashboard_app/requirements_dashboard.txt
python -m streamlit run dashboard_app/app.py
```

The app reads the existing connectivity prototype CSV outputs and optionally reads `features_monthly.parquet`, `features_daily.parquet`, `returns_monthly.parquet` and `returns_daily.parquet` from `data/analysis_ready/`. If those Parquet files are unavailable, the other dashboard pages remain usable.

## Version 4 changes

- Overview: asset-class context and selectable cross-theme comparison metric.
- Theme explorer: selectable aggregate market metric and cleaner research-facing table.
- Theme detail: broader metric selection, including positive/negative return breadth and return dispersion when present.
- Instrument detail: asset-class and instrument-type filters, theme memberships, selectable daily/monthly market features, history chart and CSV download.
- Metadata & definitions: separate area for theme/instrument master data, connectivity and macro mapping review fields, and feature definitions.
- Main research tables no longer carry most mapping-review and validation metadata.

## Interpretation guardrails

Theme performance remains a proxy based on currently mapped instruments, not a direct measure of underlying theme activity. Mappings remain proposed and require economic review. Macro availability lags are assumed, not historical release/vintage reconstruction. No conviction score or trade recommendation is produced.
\n\n## Version 5 regression exposures\n\nUse the **Regression exposures** page for instrument Fama–French estimates, theme factor summaries and pooled macro regression estimates. The app prefers `reports/fama_french/` and `reports/macro_regression/` outputs, falling back to bundled snapshots. Macro regressions are pooled panel estimates, **not** per-instrument exposures.\n
## Version 6 regression-exposure updates

- Fama–French instrument view now uses the same asset-class and instrument-type filters as Instrument detail, and adds a factor-coefficient chart for the selected instrument.
- Theme factor summaries retain the cross-theme selected-factor table/chart and add a separate selected-theme(s) section showing all factor exposures.
- Macro regressions are now estimated separately for each instrument, predictor, return measure and timing choice using the existing macro regression panel and manifest. Run from the project root:

```bash
python dashboard_app/estimate_macro_regressions_instrument_level.py
```

The estimator requires the project's existing `pandas`, `pyarrow`, `statsmodels` and `scipy` dependencies. It writes `reports/macro_regression/instrument_level_regression_results.csv` and a JSON summary, without overwriting the legacy pooled regression outputs. It uses a 36-month minimum, Newey–West/HAC standard errors (three lags), and Benjamini–Hochberg adjustment within each instrument and model type. Predictive macro values still use assumed release lags rather than historical vintages.

## Version 7 macro exposure views

The Macro panel regressions section now uses the same human-readable macro feature names as Macro monitor. It provides two complementary views: multiple selected macro exposures for one instrument, and one selected macro exposure compared across the currently filtered instruments. Coefficient charts are accompanied by tables containing sample size, HAC inference and BH-adjusted p-values. Coefficient magnitudes across differently scaled predictors should not be compared as if they shared a common unit.
