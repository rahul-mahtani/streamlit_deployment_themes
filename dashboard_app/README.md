# Systematic Investment Research Dashboard

The dashboard provides a strategist-facing interface to explore market themes, macro conditions, instrument behaviour and the evidence behind estimated relationships.

## Run

From the project root:

```bash
.venv311/bin/python -m streamlit run dashboard_app/app.py
```

## Navigation

The research flow begins with the Research overview, followed by Macro monitor and Macro regimes, then moves into Theme landscape, Theme deep dive, Theme evidence, Instrument detail and Instrument exposures. Connectivity & data quality and Metadata & methodology provide supporting audit context.

## Data sources

- Market and theme panels are read from the project's existing reports and `data/analysis_ready/` outputs.
- Theme evidence prefers live files in `reports/theme_evidence_aggregation/`, with portable snapshots under `dashboard_app/fixtures/theme_evidence_aggregation/` as fallback.
- Instrument-level regime performance prefers `reports/regime_conditioned_performance/instrument_regime_performance.csv`, with a bundled fixture fallback.
- Macro regime history and subgroup scores are read from `reports/macro_regime/` and `reports/macro_signals/`.

## Interpretation

The dashboard is a research and exploration tool, not an automated recommendation engine. Structural mappings, regression sensitivities and realised conditional performance are separate evidence types. Regression associations are not causal. Regime-conditioned results are historical descriptions using the existing one-month lag convention. Annualised arithmetic returns are 12 times mean monthly returns, not compounded CAGR. Thin samples are flagged and should not be used to rank strategies.

For installation and v9 changes, see `DASHBOARD_REVAMP_V9_INSTALL.md` and `CHANGELOG_v9.md`.
