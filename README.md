# Systematic Investment Research Dashboard — Streamlit deployment (V9)

This is a **standalone deployment repository** for the V9 strategist-facing dashboard.
It includes the dashboard application and the runtime data snapshots it reads. It does
not depend on the original research project directory or on local pipeline scripts.

## Deploy on Streamlit Community Cloud

1. Create or use a GitHub repository for this folder.
2. Push the contents of this folder to the deployment branch.
3. In Streamlit Community Cloud, create an app from that repository and branch.
4. Set **Main file path** to `dashboard_app/app.py`.
5. Select **Python 3.11** in the app's advanced settings.
6. Deploy.

For an existing V7 deployment, replace the repository contents with this V9 package,
commit and push. Keep the existing repository, branch and Streamlit app settings unless
you intentionally want a separate deployment.

## Runtime contents

- `dashboard_app/`: V9 Streamlit application, tests, documentation and fallback snapshots.
- `config/`: instrument, theme and derived-feature metadata.
- `data/analysis_ready/`: daily and monthly feature/return panels.
- `reports/connectivity_prototype/`: theme-level market, macro-context and connectivity outputs.
- `reports/fama_french/`: instrument factor coefficients and summary.
- `reports/macro_regression/`: pooled and instrument-level macro regression outputs.
- `reports/macro_regime/`: monthly macro regime classifications.
- `reports/macro_signals/`: monthly macro subgroup scores.
- `reports/regime_conditioned_performance/`: instrument conditional performance.
- `reports/instrument_exposure/`: integrated instrument and theme-instrument evidence panels.
- `reports/theme_evidence_aggregation/`: theme-level macro, factor, mapping and regime evidence.
- `requirements.txt`: deployment dependencies.

The dashboard uses paths relative to this repository root. Preserve the directory structure.

## Data refresh model

This is a **read-only deployment snapshot**. It does not run the research pipelines or
collect new market/macro data at app startup. To refresh the dashboard:

1. Rebuild the relevant outputs in the research project.
2. Copy the refreshed, dashboard-required files into the corresponding folders here.
3. Run the dashboard checks.
4. Commit and push the updated snapshot.

The V9 app includes fallback fixtures for theme-evidence tables and instrument
regime-conditioned performance. The macro-regime monthly and subgroup-score files
are included as runtime report files and must be refreshed together when updating the
regime engine outputs.

## Local checks

From this folder, using Python 3.11:

```bash
python -m pip install -r requirements.txt
python -m pytest dashboard_app -q
python -m streamlit run dashboard_app/app.py
```

The Streamlit Community Cloud entry point is `dashboard_app/app.py`.

## Security and data governance

- Do not commit `.env` files, API keys, credentials or `.streamlit/secrets.toml`.
- Do not commit local virtual environments, caches or temporary files.
- Review the licensing and redistribution terms for the underlying data sources and
  derived datasets before publishing the repository.
- This dashboard presents research evidence and historical associations; it does not
  generate validated forecasts or investment recommendations.
