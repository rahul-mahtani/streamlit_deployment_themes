# Systematic Investment Research Dashboard — Streamlit deployment

This repository contains a deployment-focused copy of the V7 dashboard and only the
runtime data files it reads. It deliberately excludes local virtual environments,
raw collection data, pipeline scripts, temporary files and research-development
artefacts.

## Deploy on Streamlit Community Cloud

1. Push the contents of this folder to a GitHub repository.
2. In Streamlit Community Cloud, create an app from that repository and branch.
3. Set the **Main file path** to `dashboard_app/app.py`.
4. Select **Python 3.11** in the app's advanced settings.
5. Deploy.

## Runtime contents

- `dashboard_app/app.py`: V7 Streamlit application.
- `dashboard_app/fixtures/`: fallback snapshots used by the regression section
  if the corresponding legacy report files are unavailable.
- `config/`: instrument, theme and derived-feature metadata.
- `data/analysis_ready/`: monthly/daily features and returns read by the dashboard.
- `reports/connectivity_prototype/`: theme connectivity and macro-context outputs.
- `reports/fama_french/`: instrument factor coefficient and summary outputs.
- `reports/macro_regression/`: pooled baseline and instrument-level regression results.
- `requirements.txt`: deployment dependencies.

## Important notes

- The app reads files using paths relative to the repository root. Keep the folder
  structure unchanged.
- The instrument-level macro regression CSV is included, so the deployed app does
  not need to run the estimator during startup.
- This package does not include the raw data collection pipeline or credentials.
  It is a read-only dashboard snapshot; refreshing data requires a separate update
  and redeployment.
- Do not commit API keys, `.env` files, or Streamlit secrets.
- Before publishing, review the licensing/terms for each underlying data source and
  ensure you are comfortable redistributing the included derived datasets and
  regression outputs.
