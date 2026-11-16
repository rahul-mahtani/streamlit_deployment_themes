from pathlib import Path
import ast
import pandas as pd

APP_DIR = Path(__file__).resolve().parent
FIXTURES = APP_DIR / "fixtures" / "theme_evidence_aggregation"


def test_dashboard_app_parses():
    ast.parse((APP_DIR / "app.py").read_text())


def test_theme_evidence_fixture_schemas_and_theme_keys():
    profile = pd.read_csv(FIXTURES / "theme_evidence_profile.csv")
    macro = pd.read_csv(FIXTURES / "theme_macro_exposure_aggregation.csv")
    factor = pd.read_csv(FIXTURES / "theme_factor_exposure_aggregation.csv")
    regime = pd.read_csv(FIXTURES / "theme_regime_performance_reference.csv")
    links = pd.read_csv(FIXTURES / "theme_macro_signal_links.csv")

    assert {"theme_id", "primary_links", "secondary_links", "context_links", "alternative_links"}.issubset(profile.columns)
    assert {"theme_id", "scope", "feature_id", "model_family", "median_coefficient", "bh_significant_instrument_estimates_5pct"}.issubset(macro.columns)
    assert {"theme_id", "scope", "feature_id", "median_loading"}.issubset(factor.columns)
    assert {"entity_type", "theme_id", "classification_dimension", "classification_label", "observation_count", "sample_depth"}.issubset(regime.columns)
    assert {"theme_id", "signal_id", "transmission_mechanism", "evidence_status"}.issubset(links.columns)

    theme_ids = set(profile["theme_id"].astype(str))
    assert theme_ids
    assert theme_ids.issubset(set(macro["theme_id"].astype(str)))
    # Factor coverage is intentionally incomplete for some themes; do not require every theme to appear.
    assert set(factor["theme_id"].astype(str)).issubset(theme_ids)
    assert theme_ids.issubset(set(regime.loc[regime["entity_type"].eq("theme"), "theme_id"].astype(str)))


def test_theme_evidence_scopes_remain_separate():
    macro = pd.read_csv(FIXTURES / "theme_macro_exposure_aggregation.csv", usecols=["scope"])
    expected = {"primary_only", "primary_plus_secondary", "context_only", "alternative_only"}
    assert expected.issubset(set(macro["scope"].dropna().astype(str)))


def test_instrument_regime_fixture_schema_and_unique_instrument_condition_metrics():
    instrument = pd.read_csv(APP_DIR / "fixtures" / "instrument_regime_performance.csv")
    required = {"entity_type", "entity_id", "classification_dimension", "classification_label",
                "observation_count", "annualised_arithmetic_return",
                "annualised_return_vs_baseline", "annualised_volatility"}
    assert required.issubset(instrument.columns)
    instrument = instrument.loc[instrument["entity_type"].eq("instrument")]
    # Metrics are repeated by theme membership but should agree for each instrument/condition.
    grouped = instrument.groupby(["entity_id", "classification_dimension", "classification_label"])
    assert grouped["annualised_arithmetic_return"].nunique(dropna=True).max() <= 1
    assert grouped["observation_count"].nunique(dropna=True).max() <= 1
