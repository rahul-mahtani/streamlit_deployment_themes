# V9 standalone deployment package

This folder is intended to replace the previous standalone V7 Streamlit deployment
repository. It contains its own copies of the dashboard's runtime data and does not
reference the original research project directory.

## Replace the existing GitHub repository

1. Download and extract this ZIP. Keep the extracted folder as a standalone folder,
   for example `~/Downloads/systematic_research_dashboard_streamlit_deployment_v9`.
2. Open Terminal and enter the extracted folder:

   ```bash
   cd ~/Downloads/systematic_research_dashboard_streamlit_deployment_v9
   ```

3. Confirm that this is the deployment repository and inspect its contents:

   ```bash
   ls
   git status
   ```

   If this extracted folder is not already a Git clone, do not run `git push` from it.
   Instead, either clone the existing GitHub repository and copy these folder contents
   into that clone, or initialise/connect this folder to the existing remote as
   described below.

## Recommended method: update the existing local Git clone

If your V7 deployment repository is already cloned locally:

1. Back up the V7 folder or create a branch:

   ```bash
   git branch backup-v7
   ```

2. Copy the **contents** of this V9 folder into the existing V7 Git clone, replacing
   files and preserving the `.git/` directory in the clone.
3. From the existing clone, review and commit:

   ```bash
   git status
   git diff --stat
   git add -A
   git status
   git commit -m "Upgrade Streamlit dashboard to V9"
   git push origin main
   ```

   Replace `main` if the deployment uses a different branch.

`git add -A` is intentional here: it stages additions, modifications and deletions,
so obsolete V7 dashboard files are removed from the repository too. Review `git status`
before committing. Do not commit `.env`, secrets, local virtual environments or caches.

## Alternative: use this folder as the Git clone

If you want this exact extracted folder to be the local repository, clone the existing
GitHub repository into a separate folder, then copy the V9 package contents into that
clone. This preserves the remote configuration and Git history.

Do not initialise a new unrelated Git repository if the goal is to update the existing
Streamlit deployment.

## Validate before pushing

```bash
python -m pytest dashboard_app -q
python -m streamlit run dashboard_app/app.py
```

The Streamlit Cloud app should continue to use the same repository, branch and main file
path (`dashboard_app/app.py`). A push to the configured branch should trigger redeployment.

## Included data dependencies

The package includes the runtime copies of:
- instrument/theme metadata;
- daily and monthly analysis-ready market panels;
- connectivity/theme market and macro-context outputs;
- Fama-French and instrument-level macro regression results;
- monthly macro regime and subgroup histories;
- instrument regime-conditioned performance;
- integrated instrument and theme evidence aggregation outputs.

It does not include raw collection data, API credentials, the research pipeline or a
local Python environment.
