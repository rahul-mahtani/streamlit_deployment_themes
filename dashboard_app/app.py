from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Systematic Research Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent


def find_output_dir() -> Path | None:
    candidates = [
        ROOT / "reports" / "connectivity_prototype",
        ROOT / "connectivity_prototype",
        ROOT / "reports" / "connectivity_mapping_prototype",
        ROOT / "connectivity_mapping_patch" / "outputs",
    ]
    required = "theme_monthly_aggregate_panel.csv"
    for candidate in candidates:
        if (candidate / required).exists():
            return candidate
    # Search only a few expected parent levels; avoid crawling virtual environments.
    for parent in [ROOT / "reports", ROOT]:
        if parent.exists():
            for path in parent.glob("**/" + required):
                if any(part.startswith(".") or part in {".venv", ".venv311", "venv", "node_modules"} for part in path.parts):
                    continue
                return path.parent
    return None


def read_csv(path: Path, required: bool = False) -> pd.DataFrame:
    if not path.exists():
        if required:
            raise FileNotFoundError(str(path))
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def load_data(output_dir: Path) -> dict:
    instrument_master_path = ROOT / "config" / "instrument_master.csv"
    instrument_master = read_csv(instrument_master_path)

    analysis_dir = ROOT / "data" / "analysis_ready"
    def read_parquet_optional(filename: str) -> pd.DataFrame:
        path = analysis_dir / filename
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_parquet(path)
        except Exception:
            return pd.DataFrame()

    def read_optional_evidence(filename: str) -> pd.DataFrame:
        # Prefer live project outputs; use bundled snapshots for portability when absent.
        candidates = [
            ROOT / "reports" / "theme_evidence_aggregation" / filename,
            APP_DIR / "fixtures" / "theme_evidence_aggregation" / filename,
        ]
        for candidate in candidates:
            if candidate.exists():
                return read_csv(candidate)
        return pd.DataFrame()

    def read_instrument_evidence() -> pd.DataFrame:
        candidates = [
            ROOT / "reports" / "instrument_exposure" / "theme_instrument_evidence_panel.csv",
            ROOT / "config" / "theme_instrument_mapping_v2_reviewed.csv",
        ]
        for candidate in candidates:
            if candidate.exists():
                return read_csv(candidate)
        return pd.DataFrame()

    data = {
        "features_monthly": read_parquet_optional("features_monthly.parquet"),
        "features_daily": read_parquet_optional("features_daily.parquet"),
        "returns_monthly": read_parquet_optional("returns_monthly.parquet"),
        "returns_daily": read_parquet_optional("returns_daily.parquet"),
        "instrument_master": instrument_master,
        "aggregate": read_csv(output_dir / "theme_monthly_aggregate_panel.csv", required=True),
        "watchlist": read_csv(output_dir / "theme_research_watchlist_latest.csv"),
        "completed_watchlist": read_csv(output_dir / "theme_research_watchlist_latest_completed_month.csv"),
        "instrument_detail": read_csv(output_dir / "theme_instrument_monthly_detail.csv"),
        "asset_class": read_csv(output_dir / "theme_asset_class_monthly_panel.csv"),
        "macro_context": read_csv(output_dir / "theme_macro_context_monthly.csv"),
        "coverage": read_csv(output_dir / "theme_connectivity_coverage_matrix.csv"),
        "feature_availability": read_csv(output_dir / "theme_macro_feature_availability.csv"),
        "missingness": read_csv(output_dir / "macro_feature_missingness_by_feature.csv"),
        "manifest_reconciliation": read_csv(output_dir / "macro_feature_manifest_reconciliation.csv"),
        "regime_monthly": read_csv(ROOT / "reports" / "macro_regime" / "macro_regime_monthly.csv"),
        "regime_subgroups": read_csv(ROOT / "reports" / "macro_signals" / "macro_signal_subgroup_scores.csv"),
        "theme_evidence_profile": read_optional_evidence("theme_evidence_profile.csv"),
        "theme_macro_agg": read_optional_evidence("theme_macro_exposure_aggregation.csv"),
        "theme_factor_agg": read_optional_evidence("theme_factor_exposure_aggregation.csv"),
        "theme_regime_ref": read_optional_evidence("theme_regime_performance_reference.csv"),
        "theme_signal_links": read_optional_evidence("theme_macro_signal_links.csv"),
        "theme_instrument_evidence": read_instrument_evidence(),
        "instrument_regime_performance": read_csv(
            ROOT / "reports" / "regime_conditioned_performance" / "instrument_regime_performance.csv"
        ) if (ROOT / "reports" / "regime_conditioned_performance" / "instrument_regime_performance.csv").exists()
        else read_csv(APP_DIR / "fixtures" / "instrument_regime_performance.csv"),
    }
    for key in ["aggregate", "watchlist", "completed_watchlist", "instrument_detail",
                "asset_class", "macro_context", "feature_availability", "missingness",
                "features_monthly", "features_daily", "returns_monthly", "returns_daily",
                "regime_monthly", "regime_subgroups", "theme_evidence_profile", "theme_macro_agg",
                "theme_factor_agg", "theme_regime_ref", "theme_signal_links",
                "theme_instrument_evidence", "instrument_regime_performance"]:
        df = data[key]
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        if "month" in df.columns:
            df["month"] = pd.to_datetime(df["month"].astype(str) + "-01", errors="coerce")
        for col in ["data_as_of_date", "feature_observation_date", "panel_data_as_of_date",
                    "latest_observation_date", "first_observation_date", "latest_market_data_as_of_date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
    return data


# User-facing labels: keep source feature IDs in detail tables and downloads for auditability.
FEATURE_STEMS = {
    "baa10y": "Baa corporate bond spread over 10-year Treasuries",
    "bamlc0a0cm": "US investment-grade corporate bond spread",
    "bamlc0a4cbbb": "US BBB corporate bond spread",
    "bamlh0a0hym2": "US high-yield corporate bond spread",
    "ces0500000003": "Average hourly earnings",
    "cfnai": "Chicago Fed National Activity Index",
    "consumer_sentiment": "Consumer sentiment",
    "cpi_core": "Core CPI inflation",
    "cpi_headline": "Headline CPI inflation",
    "csushpinsa": "US house prices",
    "dcoilwtico": "WTI crude oil price",
    "dexjpus": "USD/JPY exchange rate",
    "dexuseu": "EUR/USD exchange rate",
    "dexusuk": "GBP/USD exchange rate",
    "dtwexbgs": "Broad trade-weighted US dollar index",
    "dff": "Effective federal funds rate",
    "fedfunds": "Federal funds rate",
    "dfii10": "10-year US real Treasury yield",
    "dgorder": "Durable goods orders",
    "dgs2": "2-year US Treasury yield",
    "dgs3mo": "3-month US Treasury bill yield",
    "dgs5": "5-year US Treasury yield",
    "dgs10": "10-year US Treasury yield",
    "dgs30": "30-year US Treasury yield",
    "dhhngsp": "US natural gas price",
    "houst": "US housing starts",
    "indpro": "US industrial production",
    "initial_claims": "Initial unemployment claims",
    "payems": "Nonfarm payroll employment",
    "pce_core": "Core PCE inflation",
    "pce_headline": "Headline PCE inflation",
    "permit": "US building permits",
    "real_gdp": "Real US GDP",
    "rsafs": "US retail sales excluding food services",
    "t10y2y": "10-year minus 2-year Treasury yield spread",
    "t10y3m": "10-year minus 3-month Treasury yield spread",
    "t10yie": "10-year US breakeven inflation rate",
    "t5yie": "5-year US breakeven inflation rate",
    "unemployment_rate": "US unemployment rate",
    "vixcls": "CBOE VIX equity-market volatility index",
}


def feature_base_id(feature_id: str) -> str:
    feature_id = str(feature_id)
    return feature_id[len("diff1__"):] if feature_id.startswith("diff1__") else feature_id


def feature_label(feature_id: str) -> str:
    fid = str(feature_id)
    base = feature_base_id(fid)
    # Handle compound transformations before the more general suffixes.
    exact = {
        "cfnai_3obs_average": "Chicago Fed National Activity Index — three-observation average",
        "initial_claims_4obs_average": "Initial unemployment claims — four-observation average",
        "unemployment_rate_change_3m_pp": "Change in US unemployment rate over three months (percentage points)",
        "fedfunds_change_1obs_pp": "Federal funds rate — one-period change (percentage points)",
        "real_gdp_qoq_annualised_pct": "Real US GDP growth — quarter over quarter, annualised",
        "consumer_sentiment_level": "University of Michigan consumer sentiment index",
        "consumer_sentiment_yoy_pct": "Consumer sentiment — year-over-year change",
        "reported_real_gdp_growth_saar_pct": "Reported real GDP growth — seasonally adjusted annual rate",
        "totresns_13obs_change_pct": "Federal Reserve total reserve balances — 13-observation change",
        "trade_balance_12obs_change": "Trade balance — 12-observation change",
    }
    if base in exact:
        label = exact[base]
    else:
        suffixes = [
            ("_zscore_252obs", " — one-year z-score"),
            ("_3m_annualised_pct", " — latest three months, annualised"),
            ("_6m_annualised_pct", " — latest six months, annualised"),
            ("_annualised_pct", " — annualised growth"),
            ("_yoy_pct", " — year-over-year growth"),
            ("_mom_pct", " — monthly growth"),
            ("_21obs_change_pct", " — about one-month percentage change"),
            ("_1obs_change_pct", " — one-period percentage change"),
            ("_change_21obs", " — change over about one month"),
            ("_level_pct", ""),
            ("_level", ""),
            ("_change_3m_pp", " — three-month change in percentage points"),
            ("_4obs_average", " — four-observation average"),
        ]
        stem = base
        suffix_label = ""
        for suffix, desc in suffixes:
            if stem.endswith(suffix):
                stem = stem[:-len(suffix)]
                suffix_label = desc
                break
        stem_label = None
        for prefix in sorted(FEATURE_STEMS, key=len, reverse=True):
            if stem == prefix:
                stem_label = FEATURE_STEMS[prefix]
                break
        if stem_label is None:
            # Features whose names include a semantic suffix before the common suffix.
            aliases = {
                "cpi_core": "Core CPI inflation", "cpi_headline": "Headline CPI inflation",
                "pce_core": "Core PCE inflation", "pce_headline": "Headline PCE inflation",
                "t10y2y": "10-year minus 2-year Treasury yield spread",
                "t10y3m": "10-year minus 3-month Treasury yield spread",
            }
            stem_label = aliases.get(stem, stem.replace("_", " ").capitalize())
        label = stem_label + suffix_label
    if fid.startswith("diff1__"):
        return "Change in " + label[0].lower() + label[1:]
    return label


FEATURE_CATEGORIES = {
    "Inflation and prices": ("cpi_", "pce_"),
    "Growth and demand": ("real_gdp", "indpro", "dgorder", "rsafs", "cfnai", "consumer_sentiment"),
    "Labour market": ("ces050", "payems", "initial_claims", "unemployment_rate"),
    "Interest rates and yield curve": ("dgs", "dff_", "fedfunds", "t10y", "dfii10", "t5yie", "t10yie"),
    "Credit conditions": ("baa10y", "baml"),
    "Currencies and US dollar": ("dex", "dtwexbgs"),
    "Commodities and energy": ("dcoilwtico", "dhhngsp"),
    "Housing": ("houst", "permit", "csushpinsa"),
    "Market risk and financial conditions": ("vixcls",),
}


def feature_category(feature_id: str) -> str:
    base = feature_base_id(feature_id).lower()
    for category, prefixes in FEATURE_CATEGORIES.items():
        if any(base.startswith(prefix) for prefix in prefixes):
            return category
    return "Other macro indicators"


def fmt_pct(value, digits=1):
    if pd.isna(value):
        return "—"
    return f"{value:.{digits}f}%"


def fmt_num(value, digits=2):
    if pd.isna(value):
        return "—"
    return f"{value:.{digits}f}"


def fmt_metric(value, metric):
    if pd.isna(value):
        return "—"
    if metric in {"RET_M_ADJ", "MOM_1M", "MOM_3M", "MOM_6M", "MOM_12M",
                  "ACTIVE_RET_M_ADJ", "MDD_M_12M", "REL_PERF_M_12"}:
        return f"{value:.2%}"
    if metric in {"VOL_M_12M", "TE_M_36"}:
        return f"{value:.2%}"
    return f"{value:.2f}"


def get_metric_cols(metric):
    return {
        "Monthly return": ("RET_M_ADJ", "Monthly adjusted return"),
        "1-month momentum": ("MOM_1M", "1-month momentum"),
        "3-month momentum": ("MOM_3M", "3-month momentum"),
        "6-month momentum": ("MOM_6M", "6-month momentum"),
        "12-month momentum": ("MOM_12M", "12-month momentum"),
        "12-month volatility": ("VOL_M_12M", "12-month volatility"),
        "12-month max drawdown": ("MDD_M_12M", "12-month maximum drawdown"),
        "Active return": ("ACTIVE_RET_M_ADJ", "Monthly active return"),
        "36-month beta": ("BETA_M_36", "36-month beta"),
        "36-month correlation": ("CORR_M_36", "36-month correlation"),
        "36-month tracking error": ("TE_M_36", "36-month tracking error"),
        "12-month relative performance": ("REL_PERF_M_12", "12-month relative performance"),
    }[metric]



AGGREGATE_METRICS = {
    "Monthly return": "RET_M_ADJ", "1-month momentum": "MOM_1M",
    "3-month momentum": "MOM_3M", "6-month momentum": "MOM_6M",
    "12-month momentum": "MOM_12M", "12-month volatility": "VOL_M_12M",
    "12-month max drawdown": "MDD_M_12M", "Active return": "ACTIVE_RET_M_ADJ",
    "36-month beta": "BETA_M_36", "36-month correlation": "CORR_M_36",
    "36-month tracking error": "TE_M_36", "12-month relative performance": "REL_PERF_M_12",
}
FEATURE_LABELS = {
    "RET_D_ADJ": "Daily adjusted return", "LOGRET_D_ADJ": "Daily log return",
    "VOL_D_21D": "21-day annualised volatility", "VOL_D_63D": "63-day annualised volatility",
    "DD_D": "Current drawdown", "MDD_D_252D": "252-day maximum drawdown",
    "ACTIVE_RET_D_ADJ": "Daily active return", "BETA_D_252": "252-day beta",
    "CORR_D_252": "252-day correlation", "TE_D_252": "252-day tracking error",
    "REL_PERF_D_63": "63-day relative performance",
    "RET_M_ADJ": "Monthly adjusted return", "MOM_1M": "1-month momentum",
    "MOM_3M": "3-month momentum", "MOM_6M": "6-month momentum",
    "MOM_12M": "12-month momentum", "VOL_M_12M": "12-month volatility",
    "MDD_M_12M": "12-month maximum drawdown", "ACTIVE_RET_M_ADJ": "Monthly active return",
    "BETA_M_36": "36-month beta", "CORR_M_36": "36-month correlation",
    "TE_M_36": "36-month tracking error", "REL_PERF_M_12": "12-month relative performance",
}
def readable_feature_name(fid):
    return FEATURE_LABELS.get(str(fid), str(fid).replace("_", " ").title())
def combine_feature_panels(features, returns):
    frames=[x.copy() for x in (features, returns) if x is not None and not x.empty]
    if not frames: return pd.DataFrame()
    result=frames[0]
    for frame in frames[1:]:
        keys=[c for c in ["date","instrument_id"] if c in result.columns and c in frame.columns]
        if len(keys)==2:
            cols=keys+[c for c in frame.columns if c not in result.columns and c not in keys]
            result=result.merge(frame[cols],on=keys,how="outer",validate="one_to_one")
    if "date" in result: result["date"]=pd.to_datetime(result["date"],errors="coerce")
    return result
def format_market_value(value, fid):
    if pd.isna(value): return "—"
    if any(x in str(fid) for x in ["RET_","MOM_","VOL_","MDD_","DD_","ACTIVE_RET","TE_","REL_PERF"]): return f"{value:.2%}"
    return f"{value:.2f}"

THEME_EVIDENCE_SCOPE_LABELS = {
    "primary_only": "Core mapped exposures only",
    "primary_plus_secondary": "Core and supplementary exposures",
    "context_only": "Contextual comparators (separate from core exposure)",
    "alternative_only": "Alternative implementations (not additive exposures)",
}
MODEL_FAMILY_LABELS = {
    "A": "Absolute return · contemporaneous macro data",
    "B": "Benchmark-relative return · contemporaneous macro data",
    "C": "Absolute return · lagged macro data",
    "D": "Benchmark-relative return · lagged macro data",
}
SAMPLE_DEPTH_LABELS = {
    "INSUFFICIENT": "Very limited (<12 months)",
    "LIMITED": "Limited (12–23 months)",
    "MODERATE": "Moderate (24–35 months)",
    "LONGER_HISTORY": "Longer history (36+ months)",
}
EXPECTED_DIRECTION_LABELS = {
    "mixed": "Mixed; depends on the underlying driver",
    "conditional_positive": "Conditionally positive",
    "conditional_negative": "Conditionally negative",
    "conditional": "Conditional; depends on the transmission channel",
}
REGIME_DIMENSION_LABELS = {
    "confirmed_regime": "Confirmed overall macro regime",
    "growth_state": "Growth environment",
    "inflation_state": "Inflation environment",
    "subgroup_overlay": "Combined growth and inflation detail",
    "growth_subgroup_overlay": "Growth-sector composition",
    "inflation_subgroup_overlay": "Headline versus underlying inflation",
}
REGIME_LABELS = {
    "MIXED_OR_TRANSITIONAL": "Mixed or transitional conditions",
    "INSUFFICIENT_EVIDENCE": "Insufficient evidence to classify",
    "INSUFFICIENT_SUBGROUP_DATA": "Insufficient subgroup data",
    "INCOMPLETE_SUBGROUP_DIAGNOSTICS": "Incomplete subgroup diagnostics",
    "IMPROVING": "Improving",
    "WEAKENING": "Weakening",
    "EASING": "Easing",
    "RISING": "Rising",
    "NEUTRAL": "Neutral",
    "ALL_ELIGIBLE_MONTHS": "All eligible months (baseline)",
    "BROAD_BASED_IMPROVEMENT": "Broad-based improvement",
    "BROAD_WEAKNESS_WITH_HOUSING_INDUSTRIAL_STRENGTH": "Broad weakness, with housing and industry stronger",
    "BROAD_DEMAND_AND_HOUSING_WEAKNESS_WITH_INDUSTRIAL_STRENGTH": "Demand and housing weakness, with industry stronger",
    "BROAD_DEMAND_AND_INDUSTRIAL_WEAKNESS_WITH_HOUSING_STRENGTH": "Demand and industry weakness, with housing stronger",
    "CROSS_AXIS_SUBGROUP_DIVERGENCE": "Growth and inflation signals diverge",
    "GROWTH_SUBGROUP_DIVERGENCE": "Growth sectors send mixed signals",
    "HEADLINE_CORE_ALIGNED_EASING": "Headline and underlying inflation easing together",
    "HEADLINE_CORE_DIVERGENCE": "Headline and underlying inflation diverge",
    "INFLATION_HEADLINE_CORE_DIVERGENCE": "Headline and underlying inflation diverge",
    "MIXED_SUBGROUP_SIGNALS": "Mixed signals across subgroups",
    "NO_MAJOR_SUBGROUP_DIVERGENCE": "No major subgroup divergence",
    "BROAD_DEMAND_AND_INDUSTRIAL_STRENGTH_WITH_HOUSING_WEAKNESS": "Demand and industry stronger, with housing weaker",
}
FACTOR_GROUP_LABELS = {
    "core_us_equity_exposure": "Core US equity factor estimates",
    "supplementary_non_us_or_global_exposure": "Supplementary non-US / global factor estimates",
}
FACTOR_LABELS = {
    "Mkt-RF": "Equity market sensitivity (market excess return)",
    "SMB": "Smaller versus larger companies",
    "HML": "Value versus growth stocks",
    "RMW": "More versus less profitable companies",
    "CMA": "Conservative versus aggressive investment",
    "Mom": "Momentum",
    "const": "Regression intercept",
}
SUBGROUP_LABELS = {
    "broad_growth": "Broad growth",
    "consumer_demand": "Consumer demand",
    "housing_activity": "Housing activity",
    "industrial_activity": "Industrial activity",
    "core_inflation": "Underlying (core) inflation",
    "headline_inflation": "Headline inflation",
}


def plain_label(value, mapping=None):
    value = str(value)
    if mapping and value in mapping:
        return mapping[value]
    return value.replace("_", " ").replace("-", " ").strip().capitalize()


def human_macro_feature(feature_id):
    """Readable label for regression feature IDs, preserving the raw ID in tables."""
    value = str(feature_id)
    label = feature_label(value)
    # Feature IDs not in the legacy macro monitor catalogue often start with a source series.
    if label == value or label.replace(" ", "_").lower() == value.lower():
        cleaned = value.replace("diff1__", "First difference of ")
        cleaned = cleaned.replace("_change_21obs", " change over approximately one month")
        cleaned = cleaned.replace("_level", " level")
        cleaned = cleaned.replace("_pct", " (percent)")
        cleaned = cleaned.replace("_pp", " (percentage points)")
        cleaned = cleaned.replace("_saar", " seasonally adjusted annual rate")
        cleaned = cleaned.replace("_qoq", " quarter-on-quarter")
        cleaned = cleaned.replace("_yoy", " year-on-year")
        cleaned = cleaned.replace("_mom", " month-on-month")
        cleaned = cleaned.replace("_", " ")
        label = cleaned.strip().capitalize()
    return label


def fmt_share(value, digits=0):
    if pd.isna(value):
        return "—"
    return f"{100 * float(value):.{digits}f}%"


def fmt_return(value, digits=2):
    if pd.isna(value):
        return "—"
    return f"{100 * float(value):.{digits}f}%"


def infer_asset_class(instrument_type):
    """Map the existing instrument master type to a broad dashboard asset class."""
    value = str(instrument_type).strip().lower()
    if not value or value == "nan":
        return "Unclassified"
    if "equity" in value or "sector etf" in value or "thematic etf" in value:
        return "Equities"
    if "bond" in value or "fixed income" in value:
        return "Fixed income"
    if "commodity" in value or "gold etc" in value or "gold" in value:
        return "Commodities"
    if "currency" in value or "fx " in value or value.startswith("fx"):
        return "FX & currencies"
    if "reit" in value or "real estate" in value:
        return "Real estate"
    return "Other / review"


@st.cache_data(show_spinner=False)
def cached_load_data(output_dir_str: str) -> dict:
    return load_data(Path(output_dir_str))


out_dir = find_output_dir()

st.title("Systematic Investment Research")
st.caption("A systematic research workspace for exploring macro conditions, investment themes, instrument exposures and historical evidence.")

if out_dir is None:
    st.error("Could not find the connectivity prototype output files.")
    st.markdown(
        "Expected to find `theme_monthly_aggregate_panel.csv` in "
        "`reports/connectivity_prototype/` (or in a `connectivity_prototype/` folder at the project root)."
    )
    st.markdown("Run the prototype first from the project root:")
    st.code("python connectivity_mapping_patch/scripts/run_connectivity_prototype.py", language="bash")
    st.stop()

try:
    data = cached_load_data(str(out_dir))
except Exception as exc:
    st.error(f"Could not load dashboard data: {exc}")
    st.stop()

aggregate = data["aggregate"]
coverage = data["coverage"]
watchlist = data["watchlist"]
completed_watchlist = data["completed_watchlist"]
macro_context = data["macro_context"]
instrument_detail = data["instrument_detail"]
asset_class = data["asset_class"]
instrument_master = data["instrument_master"]
feature_availability = data["feature_availability"]
missingness = data["missingness"]
features_monthly = data.get("features_monthly", pd.DataFrame())
features_daily = data.get("features_daily", pd.DataFrame())
returns_monthly = data.get("returns_monthly", pd.DataFrame())
returns_daily = data.get("returns_daily", pd.DataFrame())

# Enrich instrument-level history with metadata from the existing instrument master.
# This makes broad filters independent of the theme-level asset-class aggregates.
if not instrument_detail.empty and not instrument_master.empty and "instrument_id" in instrument_master.columns:
    metadata_cols = [c for c in [
        "instrument_id", "yahoo_symbol_candidate", "instrument_type", "region",
        "exposure_description", "trading_currency_or_quote", "benchmark_or_reference",
        "research_use", "priority", "status", "validation_status"
    ] if c in instrument_master.columns]
    metadata = instrument_master[metadata_cols].drop_duplicates("instrument_id")
    instrument_detail = instrument_detail.merge(metadata, on="instrument_id", how="left", suffixes=("", "_master"))
    if "instrument_type" in instrument_detail.columns:
        instrument_detail["asset_class_category"] = instrument_detail["instrument_type"].map(infer_asset_class)
    else:
        instrument_detail["asset_class_category"] = "Unclassified"

if aggregate.empty:
    st.error("The monthly aggregate panel is empty.")
    st.stop()

aggregate["theme_id"] = aggregate["theme_id"].astype(str)
theme_ids = sorted(aggregate["theme_id"].dropna().unique().tolist())
theme_names = {}
if not coverage.empty and {"theme_id", "theme_name"}.issubset(coverage.columns):
    theme_names = coverage.drop_duplicates("theme_id").set_index("theme_id")["theme_name"].to_dict()

def display_theme(theme_id):
    return f"{theme_names.get(theme_id, theme_id)} ({theme_id})"


def display_instrument(instrument_id):
    rows = instrument_master.loc[instrument_master.get("instrument_id", pd.Series(index=instrument_master.index, dtype=str)).astype(str).eq(str(instrument_id))] if not instrument_master.empty else pd.DataFrame()
    if rows.empty:
        return str(instrument_id)
    row = rows.iloc[0]
    symbol = row.get("yahoo_symbol_candidate")
    description = row.get("exposure_description")
    parts = [str(x) for x in [symbol, description] if pd.notna(x) and str(x).strip()]
    return f"{' — '.join(parts)} ({instrument_id})" if parts else str(instrument_id)

latest_date = aggregate["date"].max()
latest_panel = aggregate.loc[aggregate["date"].eq(latest_date)].copy()
latest_asof = latest_panel["data_as_of_date"].max() if "data_as_of_date" in latest_panel else pd.NaT
partial_count = int(latest_panel.get("period_status", pd.Series(dtype=str)).eq("PARTIAL_MONTH").sum())

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Choose a view",
        ["Research overview", "Macro monitor", "Macro regimes",
         "Theme landscape", "Theme deep dive", "Theme evidence",
         "Instrument detail", "Instrument exposures",
         "Connectivity & data quality", "Metadata & methodology"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"Data folder: `{out_dir.relative_to(ROOT) if out_dir.is_relative_to(ROOT) else out_dir}`")
    st.caption(f"Latest panel period: {latest_date:%Y-%m}")
    st.caption(f"Data as of: {latest_asof:%d %b %Y}" if pd.notna(latest_asof) else "Data as-of date unavailable")
    if partial_count:
        st.warning(f"{partial_count} themes in the latest panel are marked as partial-month.")

if page == "Research overview":
    st.subheader("Executive snapshot")
    st.caption("A high-level snapshot of the current cross-theme landscape, highlighting recent changes in momentum, relative market conditions and data coverage. Its objective is to help orient research and identify areas worth investigating further, rather than generate investment recommendations.")
    st.info("Descriptive research only. Theme performance is a proxy based on currently mapped instruments; mappings remain under review.")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Themes covered", f"{len(theme_ids)}")
    c2.metric("Latest panel period", f"{latest_date:%b %Y}")
    c3.metric("Partial-month themes", f"{partial_count}")
    c4.metric("Themes with macro links", f"{int(coverage['has_macro_feature_links'].astype(str).str.lower().eq('true').sum()) if 'has_macro_feature_links' in coverage else '—'}")
    regime_monthly = data.get("regime_monthly", pd.DataFrame())
    if not regime_monthly.empty:
        latest_regime = regime_monthly.sort_values("month").iloc[-1]
        st.markdown("### Current macro backdrop")
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Confirmed regime", plain_label(latest_regime.get("confirmed_regime"), REGIME_LABELS))
        r2.metric("Growth environment", plain_label(latest_regime.get("growth_state"), REGIME_LABELS))
        r3.metric("Inflation environment", plain_label(latest_regime.get("inflation_state"), REGIME_LABELS))
        r4.metric("Subgroup detail", plain_label(latest_regime.get("subgroup_overlay"), REGIME_LABELS))
        st.caption(f"Regime data through {pd.Timestamp(latest_regime['month']):%B %Y}. The confirmed regime follows the existing two-month confirmation rule; subgroup descriptions are diagnostic overlays, not additional regime classifications.")

    st.markdown("### Largest recent changes in 3-month momentum")
    hist_dates = sorted(aggregate["date"].dropna().unique())
    if len(hist_dates) >= 2 and "MOM_3M_median" in aggregate:
        current_date, previous_date = hist_dates[-1], hist_dates[-2]
        current = aggregate.loc[aggregate["date"].eq(current_date), ["theme_id", "MOM_3M_median"]].copy()
        previous = aggregate.loc[aggregate["date"].eq(previous_date), ["theme_id", "MOM_3M_median"]].copy()
        current["MOM_3M_median"] = pd.to_numeric(current["MOM_3M_median"], errors="coerce")
        previous["MOM_3M_median"] = pd.to_numeric(previous["MOM_3M_median"], errors="coerce")
        movers = current.merge(previous, on="theme_id", how="left", suffixes=("_latest", "_previous"))
        movers["change"] = movers["MOM_3M_median_latest"] - movers["MOM_3M_median_previous"]
        movers["theme_name"] = movers["theme_id"].map(theme_names).fillna(movers["theme_id"])
        up, down = st.columns(2)
        with up:
            st.markdown(f"**Momentum improving** · {pd.Timestamp(current_date):%b %Y} vs {pd.Timestamp(previous_date):%b %Y}")
            st.dataframe(movers.sort_values("change", ascending=False).head(5)[["theme_name", "MOM_3M_median_latest", "change"]].rename(columns={"MOM_3M_median_latest": "Latest 3-month momentum", "change": "Change vs prior month"}), use_container_width=True, hide_index=True)
        with down:
            st.markdown("**Momentum weakening**")
            st.dataframe(movers.sort_values("change", ascending=True).head(5)[["theme_name", "MOM_3M_median_latest", "change"]].rename(columns={"MOM_3M_median_latest": "Latest 3-month momentum", "change": "Change vs prior month"}), use_container_width=True, hide_index=True)
    else:
        st.info("At least two monthly observations are needed to calculate recent changes.")

    st.markdown("### Current cross-theme landscape")
    latest = latest_panel.copy()
    latest["theme_name"] = latest["theme_id"].map(theme_names).fillna(latest["theme_id"])
    asset_options = ["All asset classes"]
    if not asset_class.empty and "asset_class" in asset_class:
        asset_options += sorted(asset_class["asset_class"].dropna().astype(str).unique().tolist())
    selected_asset_class = st.selectbox("Asset-class context", asset_options)
    overview_metric = st.selectbox("Comparison metric", ["3-month momentum", "Monthly return"])
    metric_col = "MOM_3M_median" if overview_metric == "3-month momentum" else "RET_M_ADJ_median"
    if selected_asset_class != "All asset classes" and not asset_class.empty and "asset_class" in asset_class:
        ac = asset_class.loc[asset_class["asset_class"].astype(str).eq(selected_asset_class)].copy()
        if "date" in ac: ac = ac.loc[ac["date"].eq(ac["date"].max())]
        if metric_col in ac:
            latest = ac[["theme_id", metric_col]].merge(latest[["theme_id", "theme_name"]], on="theme_id", how="left")
    if metric_col in latest:
        latest[metric_col] = pd.to_numeric(latest[metric_col], errors="coerce")
        latest = latest.dropna(subset=[metric_col]).sort_values(metric_col)
        if not latest.empty:
            st.bar_chart(latest.set_index("theme_name")[[metric_col]].rename(columns={metric_col: overview_metric}), use_container_width=True)
        else: st.info("No observations are available for this metric and filter.")
    else: st.info(f"{overview_metric} is not present in the current aggregate output.")
    context_cols = [c for c in ["theme_name", "period_status", "eligible_return_coverage_pct", "breadth_positive_return_pct", "latest_feature_availability_pct"] if c in latest.columns]
    if context_cols: st.dataframe(latest[context_cols], use_container_width=True, hide_index=True)
    st.caption("Recent changes are changes in historical metrics, not forecasts. The latest partial month can affect interpretation.")

elif page == "Theme landscape":
    st.subheader("Theme explorer")
    st.caption("Screen and compare the full theme universe using market metrics, data coverage, macro-feature links and mapping-review status. Its objective is to help identify themes for deeper investigation and distinguish stronger observations from areas where evidence is limited.")
    filt1, filt2, filt3 = st.columns(3)
    with filt1:
        priority_choices = sorted(coverage["initial_priority"].dropna().unique()) if "initial_priority" in coverage else []
        selected_priorities = st.multiselect("Priority", priority_choices, default=priority_choices)
    with filt2:
        statuses = sorted(coverage["connectivity_review_status"].dropna().unique()) if "connectivity_review_status" in coverage else []
        selected_statuses = st.multiselect("Mapping status", statuses, default=statuses)
    with filt3:
        macro_filter = st.selectbox("Macro context", ["All", "Mapped", "No mapped features"])
    view = latest_panel.merge(coverage, on="theme_id", how="left", suffixes=("", "_coverage"))
    evidence_profile = data.get("theme_evidence_profile", pd.DataFrame())
    if not evidence_profile.empty and "theme_id" in evidence_profile:
        view = view.merge(evidence_profile, on="theme_id", how="left", suffixes=("", "_evidence"))
    if selected_priorities and "initial_priority" in view:
        view = view.loc[view["initial_priority"].isin(selected_priorities)]
    if selected_statuses and "connectivity_review_status" in view:
        view = view.loc[view["connectivity_review_status"].isin(selected_statuses)]
    if macro_filter == "Mapped" and "has_macro_feature_links" in view:
        view = view.loc[view["has_macro_feature_links"].astype(str).str.lower().eq("true")]
    elif macro_filter == "No mapped features" and "has_macro_feature_links" in view:
        view = view.loc[view["has_macro_feature_links"].astype(str).str.lower().eq("false")]
    view["theme_name"] = view["theme_id"].map(theme_names).fillna(view["theme_id"])
    selected_metric = st.selectbox("Market metric", list(AGGREGATE_METRICS.keys()), index=2)
    metric_col = f"{AGGREGATE_METRICS[selected_metric]}_median"
    st.markdown(f"### {selected_metric} across selected themes")
    if metric_col in view.columns:
        chart_view = view[["theme_name", metric_col]].copy()
        chart_view[metric_col] = pd.to_numeric(chart_view[metric_col], errors="coerce")
        chart_view = chart_view.dropna(subset=[metric_col]).sort_values(metric_col, ascending=True)
        if not chart_view.empty:
            st.bar_chart(chart_view.set_index("theme_name")[[metric_col]].rename(columns={metric_col: selected_metric}),
                         use_container_width=True)
        else:
            st.info("No observations are available for this metric under the selected filters.")
    else:
        st.info("The selected metric is not available in the current theme panel.")
    display_cols = ["theme_name", "theme_id", "period_status", "mapped_resolved_instrument_count",
                    "eligible_return_count", "eligible_return_coverage_pct", metric_col,
                    f"{AGGREGATE_METRICS[selected_metric]}_coverage_pct", "breadth_positive_return_pct",
                    "latest_feature_availability_pct", "primary_links", "secondary_links",
                    "context_links", "alternative_links", "macro_regression_covered_instruments",
                    "factor_covered_instruments"]
    st.dataframe(view[[c for c in display_cols if c in view.columns]], use_container_width=True, hide_index=True)
    st.download_button("Download filtered theme table", view.to_csv(index=False).encode("utf-8"), "theme_explorer.csv", "text/csv")

elif page == "Theme deep dive":
    st.subheader("Theme detail")
    st.caption("Examine an individual theme through its historical market metrics, mapped instrument composition and associated macroeconomic context. Its objective is to make the evidence, coverage limitations and mapping assumptions behind each theme transparent.")
    theme = st.selectbox("Theme", theme_ids, format_func=display_theme)
    cov_row = coverage.loc[coverage["theme_id"].eq(theme)].head(1) if not coverage.empty else pd.DataFrame()
    hist = aggregate.loc[aggregate["theme_id"].eq(theme)].sort_values("date").copy()
    if not cov_row.empty:
        row = cov_row.iloc[0]
        st.markdown(f"### {row.get('theme_name', theme)}")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Resolved instruments", int(row.get("resolved_instrument_count", 0)))
        k2.metric("Eligible returns (latest)", int(row.get("latest_eligible_return_count", 0)))
        k3.metric("Return coverage", fmt_pct(pd.to_numeric(row.get("latest_eligible_return_coverage_pct"), errors="coerce")))
        k4.metric("Macro feature availability", fmt_pct(pd.to_numeric(row.get("latest_feature_availability_pct"), errors="coerce")))
        with st.expander("Connectivity and timing caveats", expanded=True):
            st.write(f"**Mapping status:** {row.get('connectivity_review_status', 'Not available')}")
            st.write(f"**Macro context:** {row.get('macro_context_status', 'Not available')}")
            st.write(f"**Interpretation:** mapped instrument performance proxy; not a direct measure of underlying theme activity.")
            st.write(f"**Timing:** {row.get('timing_caveat', 'Timing caveat unavailable')}")
    st.info("For a fuller assessment of structural mappings, instrument macro sensitivities, equity-style factor context and regime-conditioned returns, use the Theme evidence review page.")
    extra_metrics = {"Positive-return breadth": "breadth_positive_return_pct",
                     "Negative-return breadth": "breadth_negative_return_pct",
                     "Return dispersion (IQR)": "RET_M_ADJ_iqr"}
    metric = st.selectbox("Historical metric", list(AGGREGATE_METRICS.keys()) + list(extra_metrics.keys()), index=2)
    col = extra_metrics[metric] if metric in extra_metrics else AGGREGATE_METRICS[metric]
    chart_cols = [col] if col in hist.columns else [c for c in [f"{col}_median", f"{col}_p25", f"{col}_p75"] if c in hist.columns]
    if chart_cols:
        chart = hist[["date"] + chart_cols].copy()
        for c in chart_cols:
            chart[c] = pd.to_numeric(chart[c], errors="coerce")
        chart = chart.set_index("date").sort_index()
        chart.columns = ["Median" if c.endswith("_median") else ("25th percentile" if c.endswith("_p25") else ("75th percentile" if c.endswith("_p75") else readable_feature_name(c))) for c in chart.columns]
        st.line_chart(chart, use_container_width=True)
    st.markdown("### Instrument composition and latest observations")
    latest_detail = instrument_detail.loc[instrument_detail["theme_id"].eq(theme)].copy()
    if not latest_detail.empty:
        latest_detail = latest_detail.loc[latest_detail["date"].eq(latest_detail["date"].max())]
        latest_detail["Instrument"] = latest_detail["instrument_id"].map(display_instrument)
        show_cols = [c for c in ["Instrument", "instrument_id", "membership_basis", "RET_M_ADJ", "MOM_3M",
                                  "MOM_6M", "MOM_12M", "VOL_M_12M", "data_as_of_date"] if c in latest_detail.columns]
        st.dataframe(latest_detail[show_cols].rename(columns={"instrument_id":"Instrument ID", "membership_basis":"Membership basis", "RET_M_ADJ":"Monthly return", "MOM_3M":"3-month momentum", "MOM_6M":"6-month momentum", "MOM_12M":"12-month momentum", "VOL_M_12M":"12-month volatility", "data_as_of_date":"Market data as of"}), use_container_width=True, hide_index=True)
    else:
        st.info("No instrument detail is available for this theme.")
    st.markdown("### Macro context")
    macro = macro_context.loc[macro_context["theme_id"].eq(theme)].copy()
    if not macro.empty:
        macro["feature_label"] = macro["feature_id"].astype(str).map(feature_label) + " · " + macro["mapping_role"].astype(str)
        features = sorted(macro["feature_label"].dropna().unique())
        selected_feature = st.selectbox("Macro feature", features)
        selected = macro.loc[macro["feature_label"].eq(selected_feature)].sort_values("date")
        selected["value"] = pd.to_numeric(selected["value"], errors="coerce")
        selected_chart = selected.dropna(subset=["value"]).set_index("date")[["value"]].rename(columns={"value": "Value"})
        if not selected_chart.empty:
            st.line_chart(selected_chart, use_container_width=True)
        st.dataframe(selected[[c for c in ["date", "feature_observation_date", "panel_data_as_of_date",
                                           "feature_id", "mapping_role", "value"] if c in selected.columns]].tail(24),
                     use_container_width=True, hide_index=True)
        st.caption("Macro values use assumed availability lags, not historical release/vintage reconstruction.")
    else:
        st.warning("No mapped macro features are available for this theme.")

elif page == "Instrument detail":
    st.subheader("Instrument detail")
    st.caption("Inspect an individual instrument's market history, derived features, performance and relationship to mapped themes. Its objective is to provide the underlying security-level context behind aggregate theme observations.")
    if instrument_detail.empty:
        st.warning("Instrument-detail file is not available.")
    else:
        st.write("Filter by asset class and instrument type, then inspect theme memberships and market history.")
        classes = sorted(instrument_detail.get("asset_class_category", pd.Series("Unclassified", index=instrument_detail.index)).fillna("Unclassified").astype(str).unique())
        selected_classes = st.multiselect("Asset class", classes, default=classes)
        filtered = instrument_detail.loc[instrument_detail.get("asset_class_category", pd.Series("Unclassified", index=instrument_detail.index)).fillna("Unclassified").astype(str).isin(selected_classes)].copy()
        if "instrument_type" in filtered:
            types = sorted(filtered["instrument_type"].dropna().astype(str).unique())
            selected_types = st.multiselect("Instrument type", types, default=types)
            filtered = filtered.loc[filtered["instrument_type"].astype(str).isin(selected_types)]
        instruments = sorted(filtered["instrument_id"].dropna().astype(str).unique())
        if not instruments: st.warning("No instruments match the selected filters.")
        else:
            selected_instrument = st.selectbox("Instrument", instruments, format_func=display_instrument)
            rows = filtered.loc[filtered["instrument_id"].astype(str).eq(selected_instrument)].copy().sort_values(["theme_id", "date"])
            if not rows.empty:
                meta = rows.iloc[-1]
                metadata_cols = [c for c in ["yahoo_symbol_candidate", "instrument_type", "asset_class_category", "region", "trading_currency_or_quote", "benchmark_or_reference", "research_use"] if c in rows]
                cards = st.columns(4)
                for i, col in enumerate(metadata_cols[:4]):
                    value = meta.get(col); cards[i].metric(col.replace("_", " ").title(), "—" if pd.isna(value) else str(value))
            st.markdown("### Theme memberships")
            theme_options = sorted(rows["theme_id"].dropna().astype(str).unique())
            theme_filter = st.multiselect("Theme membership", theme_options, default=theme_options, format_func=display_theme)
            memberships = rows.loc[rows["theme_id"].astype(str).isin(theme_filter)]
            latest_memberships = memberships.loc[memberships["date"].eq(memberships["date"].max())] if "date" in memberships else memberships
            latest_memberships = latest_memberships.copy()
            latest_memberships["Theme"] = latest_memberships["theme_id"].map(theme_names).fillna(latest_memberships["theme_id"])
            if "membership_basis" in latest_memberships:
                latest_memberships["Exposure role"] = latest_memberships["membership_basis"].map(lambda x: plain_label(x))
            membership_cols = [c for c in ["Theme", "theme_id", "Exposure role", "RET_M_ADJ", "MOM_3M", "data_as_of_date"] if c in latest_memberships]
            st.dataframe(latest_memberships[membership_cols].rename(columns={"theme_id":"Theme ID", "RET_M_ADJ":"Monthly return", "MOM_3M":"3-month momentum", "data_as_of_date":"Market data as of"}), use_container_width=True, hide_index=True)

            st.markdown("### Performance across macro conditions")
            st.caption("Historical instrument returns grouped by the macro condition known at the end of the preceding month. These are descriptive conditional associations, not causal effects or forecasts. Instrument-level results are independent of theme membership; duplicate mapping rows are removed for this view.")
            instrument_regime = data.get("instrument_regime_performance", pd.DataFrame())
            if instrument_regime.empty:
                st.info("Instrument-level regime-conditioned performance is unavailable. Run the regime-conditioned performance build to populate reports/regime_conditioned_performance/instrument_regime_performance.csv.")
            else:
                ir = instrument_regime.loc[instrument_regime["entity_id"].astype(str).eq(selected_instrument)].copy()
                if ir.empty:
                    st.info("No regime-conditioned performance observations are available for this instrument.")
                else:
                    ir = ir.drop_duplicates(["classification_dimension", "classification_label"])
                    dims = sorted(ir["classification_dimension"].dropna().unique(),
                                  key=lambda x: REGIME_DIMENSION_LABELS.get(x, str(x)))
                    chosen_dim = st.selectbox("Macro classification", dims,
                                              format_func=lambda x: REGIME_DIMENSION_LABELS.get(x, plain_label(x)),
                                              key="instrument_regime_dimension")
                    iv = ir.loc[ir["classification_dimension"].eq(chosen_dim)].copy()
                    iv["observation_count"] = pd.to_numeric(iv["observation_count"], errors="coerce")
                    iv["Macro condition"] = iv["classification_label"].map(lambda x: REGIME_LABELS.get(str(x), plain_label(x)))
                    baseline = iv.loc[iv["classification_label"].eq("ALL_ELIGIBLE_MONTHS")]
                    conditional = iv.loc[~iv["classification_label"].eq("ALL_ELIGIBLE_MONTHS")].copy()
                    if not baseline.empty:
                        br = baseline.iloc[0]
                        b1, b2, b3 = st.columns(3)
                        b1.metric("Baseline annualised return", fmt_return(br.get("baseline_annualised_arithmetic_return", br.get("annualised_arithmetic_return"))))
                        b2.metric("Baseline annualised volatility", fmt_return(br.get("baseline_annualised_volatility", br.get("annualised_volatility"))))
                        b3.metric("Baseline months", int(br.get("observation_count", 0)))
                    if not conditional.empty:
                        show = conditional[[c for c in ["Macro condition", "observation_count", "sample_depth",
                            "annualised_arithmetic_return", "annualised_return_vs_baseline",
                            "annualised_volatility", "annualised_downside_deviation",
                            "positive_month_hit_rate", "fifth_percentile_monthly_return",
                            "conditional_tail_mean_5pct"] if c in conditional.columns]].copy()
                        show = show.rename(columns={"observation_count":"Months observed", "sample_depth":"Sample depth",
                            "annualised_arithmetic_return":"Annualised return (arithmetic)",
                            "annualised_return_vs_baseline":"Difference vs baseline (annualised)",
                            "annualised_volatility":"Annualised volatility",
                            "annualised_downside_deviation":"Annualised downside deviation",
                            "positive_month_hit_rate":"Positive-month hit rate",
                            "fifth_percentile_monthly_return":"5th percentile monthly return",
                            "conditional_tail_mean_5pct":"Worst 5% average monthly return"})
                        pct_cols = [c for c in show.columns if c not in ["Macro condition", "Months observed", "Sample depth"]]
                        for col in pct_cols:
                            show[col] = pd.to_numeric(show[col], errors="coerce").map(lambda x: f"{x:.1%}" if pd.notna(x) else "—")
                        st.dataframe(show, use_container_width=True, hide_index=True)
                        shallow = conditional.loc[conditional["observation_count"].lt(12)]
                        if not shallow.empty:
                            st.warning(f"{len(shallow)} condition(s) have fewer than 12 monthly observations. Treat conditional returns as highly indicative only.")
                        chart = conditional[["Macro condition", "annualised_arithmetic_return"]].copy()
                        chart["annualised_arithmetic_return"] = pd.to_numeric(chart["annualised_arithmetic_return"], errors="coerce")
                        chart = chart.dropna(subset=["annualised_arithmetic_return"]).sort_values("annualised_arithmetic_return")
                        if not chart.empty:
                            st.markdown("**Annualised return by macro condition**")
                            st.bar_chart(chart.set_index("Macro condition")[["annualised_arithmetic_return"]].rename(columns={"annualised_arithmetic_return":"Annualised return"}), use_container_width=True)
                        st.download_button("Download instrument regime evidence", iv.to_csv(index=False).encode("utf-8"),
                                            f"{selected_instrument}_regime_performance.csv", "text/csv")
                    else:
                        st.info("No conditional observations are available for this classification.")
                    st.caption("Annualised return is arithmetic (12 × mean monthly return), not compounded CAGR. The tail statistics remain monthly. Return-to-volatility is not a Sharpe ratio.")
            st.markdown("### Market feature history")
            frequency = st.radio("Frequency", ["Monthly", "Daily"], horizontal=True)
            feature_data = combine_feature_panels(features_monthly if frequency == "Monthly" else features_daily,
                                                  returns_monthly if frequency == "Monthly" else returns_daily)
            if feature_data.empty:
                st.info("Analysis-ready feature/return panels are not available. Run the market feature pipeline to populate data/analysis_ready.")
            elif "instrument_id" not in feature_data:
                st.warning("The analysis-ready panel does not contain instrument_id.")
            else:
                history = feature_data.loc[feature_data["instrument_id"].astype(str).eq(selected_instrument)].copy()
                excluded = {"date", "instrument_id", "symbol", "source", "retrieved_at_utc", "instrument_type", "region"}
                options = [c for c in history.columns if c not in excluded and pd.api.types.is_numeric_dtype(history[c])]
                if not options: st.info("No numeric market features are available for this instrument.")
                else:
                    selected_feature = st.selectbox("Market feature", options, format_func=readable_feature_name)
                    history[selected_feature] = pd.to_numeric(history[selected_feature], errors="coerce")
                    valid = history.dropna(subset=[selected_feature]).sort_values("date")
                    if not valid.empty:
                        latest_row = valid.iloc[-1]; latest_date = latest_row.get("date", pd.NaT)
                        c1,c2,c3=st.columns(3)
                        c1.metric("Latest value", format_market_value(latest_row[selected_feature], selected_feature))
                        c2.metric("Observation date", latest_date.strftime("%d %b %Y") if pd.notna(latest_date) else "—")
                        c3.metric("Observations", f"{len(valid):,}")
                        st.line_chart(valid.set_index("date")[[selected_feature]].rename(columns={selected_feature: readable_feature_name(selected_feature)}), use_container_width=True)
                        st.dataframe(valid[["date",selected_feature]].sort_values("date",ascending=False),use_container_width=True,hide_index=True)
                        st.download_button("Download feature history",valid[["date","instrument_id",selected_feature]].to_csv(index=False).encode(),f"{selected_instrument}_{selected_feature}.csv","text/csv")
                    else: st.warning("No non-missing observations are available for this feature.")
            st.download_button("Download theme memberships", memberships.to_csv(index=False).encode(), "instrument_theme_memberships.csv", "text/csv")


elif page == "Instrument exposures":
    st.subheader("Regression exposures")
    st.caption("Review estimated sensitivities of instruments and mapped themes to equity risk factors and macroeconomic variables. Its objective is to provide a structured view of historical exposures and their statistical uncertainty; estimates are exploratory associations, not causal effects or validated forecasts.")
    st.caption("Estimated coefficients from the project's existing regression outputs. These are statistical sensitivities, not conviction scores.")
    regdir = ROOT / "reports"
    ff = read_csv(regdir / "fama_french" / "fama_french_6factor_coefficients.csv")
    ff_summary = read_csv(regdir / "fama_french" / "fama_french_6factor_etf_summary.csv")
    macro = read_csv(regdir / "macro_regression" / "single_predictor_regression_results.csv")
    if ff.empty:
        ff = read_csv(APP_DIR / "fixtures" / "ff_coefficients.csv")
        st.info("Using bundled Fama–French coefficient snapshot; replace with refreshed local regression outputs when available.")
    if ff_summary.empty:
        ff_summary = read_csv(APP_DIR / "fixtures" / "ff_summary.csv")
    if macro.empty:
        macro = read_csv(APP_DIR / "fixtures" / "macro_pooled_results.csv")
        st.info("Using bundled macro-regression snapshot; replace with refreshed local results when available.")
    instrument_meta = instrument_detail.drop_duplicates("instrument_id", keep="last").copy() if "instrument_id" in instrument_detail else pd.DataFrame()
    tabs = st.tabs(["Instrument Fama–French", "Theme factor summaries", "Macro panel regressions", "Methodology & coverage"])
    eligible = ff_summary.loc[ff_summary["status"].eq("estimated"), "instrument_id"].astype(str).unique() if not ff_summary.empty else []
    ff_ok = ff.loc[ff["instrument_id"].astype(str).isin(eligible) & ff["term"].ne("const")].copy()

    with tabs[0]:
        st.caption("View the estimated six-factor equity-risk profile for one instrument, including coefficient estimates and model diagnostics. Use this view to understand the direction and magnitude of an instrument's historical factor sensitivities.")
        st.markdown("**Six-factor exposures by instrument**")
        st.caption("Filters mirror Instrument detail: asset class, instrument type and instrument selection.")
        filtered_meta = instrument_meta.copy()
        if not filtered_meta.empty:
            classes = sorted(filtered_meta.get("asset_class_category", pd.Series("Unclassified", index=filtered_meta.index)).fillna("Unclassified").astype(str).unique())
            selected_classes = st.multiselect("Asset class", classes, default=classes, key="ff_asset_classes")
            filtered_meta = filtered_meta.loc[filtered_meta.get("asset_class_category", pd.Series("Unclassified", index=filtered_meta.index)).fillna("Unclassified").astype(str).isin(selected_classes)]
            if "instrument_type" in filtered_meta:
                types = sorted(filtered_meta["instrument_type"].dropna().astype(str).unique())
                selected_types = st.multiselect("Instrument type", types, default=types, key="ff_instrument_types")
                filtered_meta = filtered_meta.loc[filtered_meta["instrument_type"].astype(str).isin(selected_types)]
        available_ids = set(ff["instrument_id"].dropna().astype(str))
        if not filtered_meta.empty:
            available_ids &= set(filtered_meta["instrument_id"].dropna().astype(str))
        ids = sorted(available_ids)
        if not ids:
            st.info("No Fama–French estimates match the selected instrument filters.")
        else:
            chosen = st.selectbox("Instrument", ids, format_func=display_instrument, key="ff_instrument")
            subset = ff.loc[ff["instrument_id"].astype(str).eq(chosen)].copy()
            factor_rows = subset.loc[subset["term"].ne("const")].copy()
            if not factor_rows.empty:
                st.markdown("**Factor exposure profile**")
                chart = factor_rows.set_index("term")[["coefficient"]].rename(columns={"coefficient": "Estimated exposure"})
                st.bar_chart(chart, use_container_width=True)
                st.caption("Bars show estimated factor coefficients. Positive and negative values indicate the direction of estimated sensitivity; scale depends on factor and return units.")
            st.markdown("**Coefficient estimates and inference**")
            st.dataframe(subset, use_container_width=True, hide_index=True)
            if not ff_summary.empty:
                st.markdown("**Model diagnostics**")
                st.dataframe(ff_summary.loc[ff_summary["instrument_id"].astype(str).eq(chosen)], use_container_width=True, hide_index=True)
            st.download_button("Download instrument coefficients", subset.to_csv(index=False).encode(), "instrument_ff_exposures.csv", "text/csv")

    with tabs[1]:
        st.caption("Compare the distribution of instrument-level factor coefficients across themes using medians, interquartile ranges and coverage. These are summaries of mapped instruments, not regressions estimated directly on theme returns.")
        st.markdown("**Mapped-instrument distribution of factor coefficients**")
        st.caption("Median and IQR across eligible instruments; not a regression on theme returns. A mapped instrument may belong to multiple themes.")
        memberships = instrument_detail[["theme_id", "instrument_id"]].drop_duplicates() if {"theme_id","instrument_id"}.issubset(instrument_detail.columns) else pd.DataFrame()
        if memberships.empty or ff_ok.empty:
            st.warning("Theme-instrument memberships or eligible Fama–French estimates are unavailable.")
        else:
            joined = memberships.merge(ff_ok, on="instrument_id", how="inner")
            grouped = joined.groupby(["theme_id","term"], as_index=False).agg(
                median_coefficient=("coefficient","median"),
                q25=("coefficient",lambda x:x.quantile(.25)),
                q75=("coefficient",lambda x:x.quantile(.75)),
                eligible_instruments=("instrument_id","nunique"))
            denominators = memberships.groupby("theme_id")["instrument_id"].nunique().rename("mapped_instruments")
            grouped = grouped.join(denominators,on="theme_id")
            grouped["coverage_pct"] = 100*grouped["eligible_instruments"]/grouped["mapped_instruments"]

            st.markdown("**All themes compared by selected factor**")
            factor = st.selectbox("Factor", sorted(grouped["term"].unique()), format_func=lambda x: FACTOR_LABELS.get(str(x), str(x)), key="ff_theme_factor")
            min_n = st.number_input("Minimum eligible instruments",min_value=1,max_value=56,value=2,key="ff_theme_min_n")
            display = grouped.loc[grouped["term"].eq(factor)&grouped["eligible_instruments"].ge(min_n)].sort_values("median_coefficient",ascending=False).copy()
            display["Theme"] = display["theme_id"].map(theme_names).fillna(display["theme_id"])
            display["Factor"] = display["term"].map(lambda x: FACTOR_LABELS.get(str(x), str(x)))
            st.dataframe(display[[c for c in ["Theme", "theme_id", "Factor", "median_coefficient", "q25", "q75", "eligible_instruments", "mapped_instruments", "coverage_pct"] if c in display.columns]].rename(columns={"theme_id":"Theme ID", "median_coefficient":"Median loading", "q25":"25th percentile", "q75":"75th percentile", "eligible_instruments":"Instruments with estimates", "mapped_instruments":"Mapped instruments", "coverage_pct":"Coverage (%)"}),use_container_width=True,hide_index=True)
            if not display.empty:
                st.bar_chart(display.set_index("Theme")["median_coefficient"])
            st.download_button("Download all theme factor summaries",grouped.to_csv(index=False).encode(),"theme_ff_exposure_summary.csv","text/csv")

            st.divider()
            st.markdown("**Selected theme(s): full factor exposure profiles**")
            all_themes = sorted(grouped["theme_id"].dropna().astype(str).unique())
            selected_themes = st.multiselect("Theme selection", all_themes, default=all_themes[:1], format_func=display_theme, key="ff_theme_profile_selection")
            profile_min_n = st.number_input("Minimum eligible instruments per theme-factor", min_value=1, max_value=56, value=2, key="ff_theme_profile_min_n")
            profile = grouped.loc[grouped["theme_id"].astype(str).isin(selected_themes) & grouped["eligible_instruments"].ge(profile_min_n)].copy()
            if profile.empty:
                st.info("No theme-factor estimates meet the selected coverage threshold.")
            else:
                profile = profile.copy()
                profile["Theme"] = profile["theme_id"].map(theme_names).fillna(profile["theme_id"])
                profile["Factor"] = profile["term"].map(lambda x: FACTOR_LABELS.get(str(x), str(x)))
                st.dataframe(profile[[c for c in ["Theme", "theme_id", "Factor", "median_coefficient", "q25", "q75", "eligible_instruments", "mapped_instruments", "coverage_pct"] if c in profile.columns]].rename(columns={"theme_id":"Theme ID", "median_coefficient":"Median loading", "q25":"25th percentile", "q75":"75th percentile", "eligible_instruments":"Instruments with estimates", "mapped_instruments":"Mapped instruments", "coverage_pct":"Coverage (%)"}),use_container_width=True,hide_index=True)
                pivot = profile.pivot(index="Factor", columns="Theme", values="median_coefficient")
                st.markdown("**Median factor exposures by selected theme**")
                st.bar_chart(pivot, use_container_width=True)
                st.download_button("Download selected theme profiles",profile.to_csv(index=False).encode(),"selected_theme_ff_profiles.csv","text/csv")

    with tabs[2]:
        st.caption("Explore multiple macro sensitivities for one instrument, or compare one selected macro sensitivity across a filtered group of instruments. The objective is to examine historical associations and their uncertainty at instrument level.")
        st.markdown("**Instrument-level macro regressions**")
        macro_instrument = read_csv(regdir / "macro_regression" / "instrument_level_regression_results.csv")
        if macro_instrument.empty:
            st.warning("Instrument-level estimates have not yet been generated. Run the included estimator from the project root:")
            st.code("python dashboard_app/estimate_macro_regressions_instrument_level.py", language="bash")
            st.caption("This uses the existing macro regression panel and predictor manifest. It does not overwrite the legacy pooled results.")
            with st.expander("Legacy pooled panel results (historical baseline)"):
                st.caption("These are pooled panel associations with instrument fixed effects—not instrument-specific exposures.")
                if not macro.empty:
                    legacy = macro.copy()
                    legacy["Model"] = legacy["model_family"].map({
                        "A":"Absolute return · contemporaneous",
                        "B":"Relative return · contemporaneous",
                        "C":"Absolute return · predictive",
                        "D":"Relative return · predictive",
                    }).fillna(legacy["model_family"])
                    legacy["Macro indicator"] = legacy["feature_id"].map(feature_label)
                    st.dataframe(legacy[["Model","Macro indicator","coefficient","p_value","p_value_bh","status"]],use_container_width=True,hide_index=True)
        else:
            st.caption("Separate time-series regressions for each instrument and macro predictor. Coefficients are associations, not causal effects or validated forecasts.")
            family_labels = {
                "A":"Absolute return · contemporaneous",
                "B":"Relative return · contemporaneous",
                "C":"Absolute return · predictive (lagged/as-of)",
                "D":"Relative return · predictive (lagged/as-of)",
            }
            macro_instrument["Model"] = macro_instrument["model_family"].map(family_labels).fillna(macro_instrument["model_family"])
            macro_instrument["Macro indicator"] = macro_instrument["feature_id"].map(feature_label)
            macro_instrument["Transformation"] = macro_instrument["feature_id"].astype(str).str.startswith("diff1__").map({True:"First difference",False:"Level"})
            macro_instrument["Macro series name"] = macro_instrument["feature_id"].map(feature_label)
            macro_instrument["Instrument label"] = macro_instrument["instrument_id"].astype(str)
            if "symbol" in macro_instrument:
                macro_instrument["Instrument label"] = macro_instrument.apply(
                    lambda r: f"{r['symbol']} ({r['instrument_id']})" if pd.notna(r.get("symbol")) and str(r.get("symbol")) else str(r["instrument_id"]), axis=1
                )
            classes = sorted(instrument_meta.get("asset_class_category", pd.Series(dtype=str)).dropna().astype(str).unique())
            selected_macro_classes = st.multiselect("Asset class", classes, default=classes, key="macro_asset_classes")
            meta_filter = instrument_meta.loc[instrument_meta.get("asset_class_category", pd.Series(index=instrument_meta.index,dtype=str)).fillna("Unclassified").astype(str).isin(selected_macro_classes)] if not instrument_meta.empty else pd.DataFrame()
            types = sorted(meta_filter.get("instrument_type",pd.Series(dtype=str)).dropna().astype(str).unique())
            selected_macro_types = st.multiselect("Instrument type",types,default=types,key="macro_instrument_types")
            if not meta_filter.empty and "instrument_type" in meta_filter:
                meta_filter=meta_filter.loc[meta_filter["instrument_type"].astype(str).isin(selected_macro_types)]
            ids = sorted(meta_filter.get("instrument_id",pd.Series(dtype=str)).dropna().astype(str).unique())
            eligible_macro = macro_instrument.loc[macro_instrument["instrument_id"].astype(str).isin(ids) & macro_instrument["status"].eq("success")].copy()
            model_choices = list(family_labels.values())
            selected_model = st.selectbox("Regression type", model_choices, key="macro_model_type")
            model_data = eligible_macro.loc[eligible_macro["Model"].eq(selected_model)].copy()

            st.markdown("### Multiple macro exposures for one instrument")
            st.caption("Compare several macro indicators for a selected instrument. Coefficients are shown in their native scales; compare magnitudes cautiously across differently scaled predictors.")
            instrument_options = sorted(model_data["instrument_id"].astype(str).unique())
            if instrument_options:
                selected_instrument = st.selectbox(
                    "Instrument", instrument_options,
                    format_func=lambda x: next((v for v in model_data.loc[model_data["instrument_id"].eq(x),"Instrument label"].dropna().unique()),x),
                    key="macro_single_instrument",
                )
                one = model_data.loc[model_data["instrument_id"].astype(str).eq(selected_instrument)].copy()
                indicators = sorted(one["Macro indicator"].dropna().unique())
                chosen_indicators = st.multiselect("Macro indicators", indicators, default=indicators[:8], key="macro_one_instrument_indicators")
                one = one.loc[one["Macro indicator"].isin(chosen_indicators)]
                transforms = sorted(one["Transformation"].dropna().unique())
                chosen_transforms = st.multiselect("Predictor transformations", transforms, default=transforms, key="macro_one_instrument_transform")
                one = one.loc[one["Transformation"].isin(chosen_transforms)]
                if not one.empty:
                    one["Chart label"] = one["Macro indicator"] + " · " + one["Transformation"]
                    one_chart = one.sort_values("coefficient").set_index("Chart label")[["coefficient"]].rename(columns={"coefficient":"Coefficient"})
                    st.bar_chart(one_chart, use_container_width=True)
                    st.dataframe(one[["Macro indicator","Macro series name","Transformation","observations","coefficient","hac_standard_error","t_statistic","p_value","bh_adjusted_p_value","r_squared","warning"]].rename(columns={
                        "Macro indicator":"Macro indicator","Macro series name":"Source series","observations":"Observations",
                        "coefficient":"Coefficient","hac_standard_error":"HAC standard error","t_statistic":"t-statistic",
                        "p_value":"p-value","bh_adjusted_p_value":"BH-adjusted p-value","r_squared":"R-squared","warning":"Notes"
                    }),use_container_width=True,hide_index=True)
                    st.download_button("Download selected instrument exposures",one.to_csv(index=False).encode(),"selected_instrument_macro_exposures.csv","text/csv")
                else:
                    st.info("Select at least one macro indicator and transformation.")
            else:
                st.info("No successful instrument-level estimates match the current filters.")

            st.divider()
            st.markdown("### One macro exposure across multiple instruments")
            st.caption("Compare the estimated coefficient for one macro indicator across the instruments that pass the current filters.")
            if not model_data.empty:
                indicator_options = sorted(model_data["Macro indicator"].dropna().unique())
                selected_indicator = st.selectbox("Macro indicator", indicator_options, key="macro_group_indicator")
                indicator_rows = model_data.loc[model_data["Macro indicator"].eq(selected_indicator)].copy()
                transformation_options = sorted(indicator_rows["Transformation"].dropna().unique())
                selected_transformation = st.selectbox("Transformation",transformation_options,key="macro_group_transform")
                indicator_rows=indicator_rows.loc[indicator_rows["Transformation"].eq(selected_transformation)]
                instrument_labels=indicator_rows[["instrument_id","Instrument label"]].drop_duplicates().set_index("instrument_id")["Instrument label"].to_dict()
                indicator_rows["Chart label"]=indicator_rows["instrument_id"].astype(str).map(instrument_labels)
                indicator_rows=indicator_rows.sort_values("coefficient")
                if not indicator_rows.empty:
                    st.bar_chart(indicator_rows.set_index("Chart label")[["coefficient"]].rename(columns={"coefficient":"Coefficient"}),use_container_width=True)
                    st.dataframe(indicator_rows[["Instrument label","observations","coefficient","hac_standard_error","t_statistic","p_value","bh_adjusted_p_value","r_squared","warning"]].rename(columns={
                        "Instrument label":"Instrument","observations":"Observations","coefficient":"Coefficient",
                        "hac_standard_error":"HAC standard error","t_statistic":"t-statistic","p_value":"p-value",
                        "bh_adjusted_p_value":"BH-adjusted p-value","r_squared":"R-squared","warning":"Notes"
                    }),use_container_width=True,hide_index=True)
                    st.download_button("Download cross-instrument exposure comparison",indicator_rows.to_csv(index=False).encode(),"macro_exposure_across_instruments.csv","text/csv")
            else:
                st.info("No successful instrument-level estimates match the current filters.")
            st.caption("BH adjustment is performed across eligible predictor tests separately for each instrument and regression type. Models with fewer than 36 observations or constant predictors are excluded. Predictive macro values use assumed release lags, not historical vintages.")
    with tabs[3]:
        st.caption("Review the model specifications, estimation thresholds, multiple-testing adjustments and timing assumptions behind the regression outputs. This section explains how to interpret the estimates and their limitations.")
        st.markdown("**Fama–French**: six-factor monthly regressions with Mkt-RF, SMB, HML, RMW, CMA and Mom; HAC/Newey–West standard errors. Instrument estimates require at least 48 observations. The coefficient file includes t-statistics, confidence intervals and Benjamini–Hochberg adjusted p-values.")
        st.markdown("**Macro**: separate instrument-level single-predictor OLS regressions; Newey–West/HAC standard errors with three lags; minimum 36 monthly observations. Four model types distinguish absolute/relative returns and contemporaneous/predictive macro observations. BH correction is applied within each instrument and model type.")
        st.markdown("**Timing caveat**: predictive macro values use configured assumed release lags, not historical publication calendars or data vintages. Results are exploratory associations, not causal effects or validated forecasts.")
        if not ff_summary.empty:
            st.dataframe(ff_summary.groupby("status",dropna=False).size().rename("instruments").reset_index(),hide_index=True)
        if not macro.empty:
            st.caption("Legacy pooled macro results are retained separately in the report files and are not used as instrument exposures.")

elif page == "Macro monitor":
    st.subheader("Macro monitor")
    st.caption("Track the historical values, observation dates and data completeness of macroeconomic indicators linked to the research themes. Its objective is to show the macro context available to the research process while making assumed availability timing and missing observations visible.")
    st.info("Explore the historical path and freshness of macro indicators mapped to themes. Availability lags are assumed; this is not historical release-vintage reconstruction.")
    if macro_context.empty:
        st.warning("Macro-context time-series file is missing.")
    else:
        macro = macro_context.copy()
        macro["feature_id"] = macro["feature_id"].astype(str)
        macro["feature_name"] = macro["feature_id"].map(feature_label)
        macro["category"] = macro["feature_id"].map(feature_category)
        macro["value"] = pd.to_numeric(macro["value"], errors="coerce")
        categories = sorted(macro["category"].dropna().unique().tolist())
        selected_categories = st.multiselect("Macro category", categories, default=categories)
        filtered = macro.loc[macro["category"].isin(selected_categories)].copy()
        feature_options = filtered[["feature_id", "feature_name"]].drop_duplicates().sort_values("feature_name")
        feature_ids = feature_options["feature_id"].tolist()
        if not feature_ids:
            st.warning("No macro features match the selected categories.")
        else:
            selected_feature_id = st.selectbox("Individual macro feature", feature_ids, format_func=feature_label)
            selected_rows = filtered.loc[filtered["feature_id"].eq(selected_feature_id)].copy()
            # A feature can be mapped to multiple themes. The value history is shown once per date;
            # theme-level links and statuses are shown separately below.
            series = selected_rows.sort_values(["date", "theme_id"]).drop_duplicates("date", keep="last").sort_values("date")
            nonmissing = series.dropna(subset=["value"])
            latest_row = nonmissing.iloc[-1] if not nonmissing.empty else None
            previous_row = nonmissing.iloc[-2] if len(nonmissing) > 1 else None
            k1, k2, k3, k4 = st.columns(4)
            k1.metric("Latest value", fmt_num(latest_row["value"]) if latest_row is not None else "—",
                      delta=fmt_num(latest_row["value"] - previous_row["value"]) if latest_row is not None and previous_row is not None else None)
            latest_obs = latest_row.get("feature_observation_date") if latest_row is not None else pd.NaT
            k2.metric("Latest observation", pd.to_datetime(latest_obs).strftime("%d %b %Y") if pd.notna(latest_obs) else "—")
            k3.metric("Non-missing observations", f"{len(nonmissing)} / {len(series)}")
            miss_pct = 100 * (1 - len(nonmissing) / len(series)) if len(series) else float("nan")
            k4.metric("Missing in displayed history", fmt_pct(miss_pct))
            st.markdown(f"### {feature_label(selected_feature_id)}")
            st.caption(f"Feature ID: `{selected_feature_id}` · Category: {feature_category(selected_feature_id)}")
            chart = series[["date", "value"]].dropna().set_index("date").sort_index()
            if not chart.empty:
                chart = chart.rename(columns={"value": feature_label(selected_feature_id)})
                st.line_chart(chart, use_container_width=True)
            else:
                st.warning("No non-missing historical values are available for this feature.")
            with st.expander("Historical observations", expanded=True):
                history_cols = ["date", "value", "feature_observation_date", "panel_data_as_of_date", "period_status", "timing_method", "assumption_status"]
                history = series[[c for c in history_cols if c in series.columns]].sort_values("date", ascending=False)
                st.dataframe(history, use_container_width=True, hide_index=True)
                st.download_button("Download feature history", history.to_csv(index=False).encode("utf-8"), f"{selected_feature_id}_history.csv", "text/csv")
            st.markdown("### Theme mappings for this feature")
            mappings = feature_availability.loc[feature_availability["feature_id"].astype(str).eq(selected_feature_id)].copy() if not feature_availability.empty else pd.DataFrame()
            if not mappings.empty:
                mappings["feature_name"] = mappings["feature_id"].astype(str).map(feature_label)
                mappings = mappings.rename(columns={"latest_value": "Latest value", "latest_observation_date": "Latest observation date", "missing_pct": "Missing (%)"})
                cols = [c for c in ["theme_id", "feature_name", "mapping_role", "Latest observation date", "Latest value", "Missing (%)"] if c in mappings.columns]
                st.dataframe(mappings[cols], use_container_width=True, hide_index=True)
            else:
                st.caption("No feature-level mapping-availability records were found for this feature.")

    st.markdown("### Feature-level missingness across the macro dataset")
    if not missingness.empty:
        miss = missingness.copy()
        miss["feature_name"] = miss["feature_id"].astype(str).map(feature_label)
        miss["category"] = miss["feature_id"].astype(str).map(feature_category)
        categories = sorted(miss["category"].dropna().unique().tolist())
        selected_miss_categories = st.multiselect("Missingness category", categories, default=categories, key="missingness_category")
        miss = miss.loc[miss["category"].isin(selected_miss_categories)]
        search = st.text_input("Search feature names or IDs")
        if search:
            mask = miss[["feature_name", "feature_id"]].astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
            miss = miss.loc[mask]
        if "missing_pct" in miss:
            miss["missing_pct"] = pd.to_numeric(miss["missing_pct"], errors="coerce")
            miss = miss.sort_values("missing_pct", ascending=False)
        show_cols = [c for c in ["feature_name", "feature_id", "category", "feature_transform", "observations_expected", "observations_available", "observations_missing", "missing_pct", "latest_observation_date", "latest_value", "availability_assumption"] if c in miss.columns]
        st.dataframe(miss[show_cols], use_container_width=True, hide_index=True)
        st.download_button("Download missingness report", miss[show_cols].to_csv(index=False).encode("utf-8"), "macro_feature_missingness.csv", "text/csv")

elif page == "Theme evidence":
    st.subheader("Theme evidence review")
    st.caption("Bring together the structural investment thesis, estimated instrument sensitivities, equity-style factor context and realised performance. The purpose is to assess how coherent and well-supported a theme is—not to generate an automatic conviction score.")
    profile = data.get("theme_evidence_profile", pd.DataFrame())
    macro_agg = data.get("theme_macro_agg", pd.DataFrame())
    factor_agg = data.get("theme_factor_agg", pd.DataFrame())
    regime_ref = data.get("theme_regime_ref", pd.DataFrame())
    signal_links = data.get("theme_signal_links", pd.DataFrame())
    instrument_links = data.get("theme_instrument_evidence", pd.DataFrame())

    if profile.empty or macro_agg.empty:
        st.warning("Theme evidence aggregation files were not found. Build the theme evidence aggregation or restore the bundled snapshots in dashboard_app/fixtures.")
    else:
        st.markdown("### Cross-theme evidence coverage")
        st.caption("Use this table to understand where the research dataset is deeper or thinner. Coverage counts are not a measure of theme attractiveness or evidence quality by themselves.")
        profile_view = profile.copy()
        profile_view["Theme"] = profile_view["theme_id"].map(theme_names).fillna(profile_view["theme_id"])
        profile_cols = [c for c in ["Theme", "theme_id", "unique_mapped_instruments", "primary_links", "secondary_links", "context_links", "alternative_links", "macro_regression_covered_instruments", "factor_covered_instruments", "theme_regime_performance_rows", "low_confidence_links", "medium_confidence_links"] if c in profile_view.columns]
        st.dataframe(profile_view[profile_cols].rename(columns={"theme_id":"Theme ID", "unique_mapped_instruments":"Mapped instruments", "primary_links":"Core exposures", "secondary_links":"Supplementary exposures", "context_links":"Contextual comparators", "alternative_links":"Alternative implementations", "macro_regression_covered_instruments":"With macro estimates", "factor_covered_instruments":"With factor estimates", "theme_regime_performance_rows":"Regime-performance rows", "low_confidence_links":"Low-confidence links", "medium_confidence_links":"Medium-confidence links"}), use_container_width=True, hide_index=True)
        st.download_button("Download cross-theme evidence coverage", profile_view[profile_cols].to_csv(index=False).encode("utf-8"), "cross_theme_evidence_coverage.csv", "text/csv")
        theme = st.selectbox("Investment theme", theme_ids, format_func=display_theme, key="evidence_theme")
        p = profile.loc[profile["theme_id"].astype(str).eq(str(theme))].head(1)
        theme_macro = macro_agg.loc[macro_agg["theme_id"].astype(str).eq(str(theme))].copy()
        theme_factor = factor_agg.loc[factor_agg["theme_id"].astype(str).eq(str(theme))].copy() if not factor_agg.empty else pd.DataFrame()
        theme_regime = regime_ref.loc[(regime_ref["entity_type"].eq("theme")) & (regime_ref["theme_id"].astype(str).eq(str(theme)))].copy() if not regime_ref.empty else pd.DataFrame()
        theme_signals = signal_links.loc[signal_links["theme_id"].astype(str).eq(str(theme))].copy() if not signal_links.empty else pd.DataFrame()
        theme_instruments = instrument_links.loc[instrument_links["theme_id"].astype(str).eq(str(theme))].copy() if not instrument_links.empty else pd.DataFrame()

        if not p.empty:
            pr = p.iloc[0]
            st.markdown(f"### {display_theme(theme)}")
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Mapped instruments", int(pr.get("unique_mapped_instruments", 0)))
            k2.metric("Core exposures", int(pr.get("primary_links", 0)))
            k3.metric("Supplementary exposures", int(pr.get("secondary_links", 0)))
            k4.metric("With macro estimates", int(pr.get("macro_regression_covered_instruments", 0)))
            k5.metric("With factor estimates", int(pr.get("factor_covered_instruments", 0)))
            st.caption("Counts describe mapped research proxies, not validated constituents of an investable portfolio.")

        tabs = st.tabs(["Evidence overview", "Macro sensitivities", "Equity-style factor context", "Performance across macro conditions", "Economic thesis & mapped instruments"])
        with tabs[0]:
            if not p.empty:
                pr = p.iloc[0]
                left, right = st.columns(2)
                with left:
                    st.markdown("**How the theme is represented**")
                    role_rows = pd.DataFrame({
                        "Exposure role": ["Core exposure", "Supplementary exposure", "Contextual comparator", "Alternative implementation"],
                        "Mapped links": [pr.get("primary_links", 0), pr.get("secondary_links", 0), pr.get("context_links", 0), pr.get("alternative_links", 0)],
                    })
                    role_rows["Mapped links"] = pd.to_numeric(role_rows["Mapped links"], errors="coerce").fillna(0)
                    st.bar_chart(role_rows.set_index("Exposure role"), use_container_width=True)
                with right:
                    st.markdown("**Evidence availability**")
                    coverage_rows = pd.DataFrame({
                        "Evidence layer": ["Macro regression estimates", "Equity-style factor estimates", "Regime-conditioned performance"],
                        "Instruments / rows": [pr.get("macro_regression_covered_instruments", 0), pr.get("factor_covered_instruments", 0), pr.get("theme_regime_performance_rows", 0)],
                    })
                    coverage_rows["Instruments / rows"] = pd.to_numeric(coverage_rows["Instruments / rows"], errors="coerce").fillna(0)
                    st.bar_chart(coverage_rows.set_index("Evidence layer"), use_container_width=True)
                st.warning("Structural mappings remain candidate proxies and are not yet validated. The aggregation does not upgrade their evidence status.")
                st.write(f"**Mapping status:** {plain_label(pr.get('mapping_statuses', 'Not available'))}")
                st.write(f"**Structural evidence status:** {plain_label(pr.get('evidence_statuses', 'Not available'))}")
                st.write(f"**Mapping confidence:** {int(pr.get('low_confidence_links', 0))} low-confidence links; {int(pr.get('medium_confidence_links', 0))} medium-confidence links.")
                st.caption(str(pr.get("aggregation_caveat", "Cross-instrument summaries are descriptive and unweighted.")))
            else:
                st.info("Theme-level evidence profile is not available for this theme.")
            if not theme_macro.empty:
                st.markdown("**Where macro evidence is concentrated**")
                summary = (theme_macro.loc[theme_macro["scope"].eq("primary_plus_secondary")]
                           .groupby("model_family", dropna=False)
                           .agg(successful_estimates=("successful_instrument_estimates", "sum"),
                                significant_estimates=("bh_significant_instrument_estimates_5pct", "sum"))
                           .reset_index())
                summary["Model specification"] = summary["model_family"].map(MODEL_FAMILY_LABELS)
                st.dataframe(summary[["Model specification", "successful_estimates", "significant_estimates"]], use_container_width=True, hide_index=True)

        with tabs[1]:
            st.markdown("**Estimated macro sensitivity across mapped instruments**")
            st.caption("Coefficients summarise separate instrument-level regressions. They are not portfolio weights, causal effects or forecasts. Compare coefficients only for the same predictor and transformation; different predictors may have different units.")
            if theme_macro.empty:
                st.info("No macro exposure aggregation is available for this theme.")
            else:
                c1, c2, c3 = st.columns(3)
                scopes = [x for x in ["primary_only", "primary_plus_secondary", "context_only", "alternative_only"] if x in theme_macro["scope"].unique()]
                scope = c1.selectbox("Instrument scope", scopes, index=scopes.index("primary_plus_secondary") if "primary_plus_secondary" in scopes else 0, format_func=lambda x: THEME_EVIDENCE_SCOPE_LABELS.get(x, x), key="evidence_macro_scope")
                families = [x for x in ["A", "B", "C", "D"] if x in theme_macro["model_family"].unique()]
                family = c2.selectbox("Regression question", families, format_func=lambda x: MODEL_FAMILY_LABELS.get(x, x), key="evidence_macro_family")
                timing_values = sorted(theme_macro["predictor_timing"].dropna().unique())
                timing = c3.selectbox("Macro data timing", timing_values, key="evidence_macro_timing")
                filtered = theme_macro.loc[(theme_macro["scope"].eq(scope)) & (theme_macro["model_family"].eq(family)) & (theme_macro["predictor_timing"].eq(timing))].copy()
                filtered["feature_label"] = filtered["feature_id"].map(human_macro_feature)
                features = sorted(filtered[["feature_id", "feature_label"]].drop_duplicates().to_dict("records"), key=lambda x: x["feature_label"])
                feature_options = [x["feature_id"] for x in features]
                if feature_options:
                    selected_feature = st.selectbox("Macro indicator / transformation", feature_options, format_func=lambda x: human_macro_feature(x), key="evidence_macro_feature")
                    selected = filtered.loc[filtered["feature_id"].eq(selected_feature)].copy()
                    selected["successful_instrument_estimates"] = pd.to_numeric(selected["successful_instrument_estimates"], errors="coerce")
                    selected["bh_significant_instrument_estimates_5pct"] = pd.to_numeric(selected["bh_significant_instrument_estimates_5pct"], errors="coerce")
                    selected["positive_coefficient_share"] = pd.to_numeric(selected["positive_coefficient_share"], errors="coerce")
                    selected["negative_coefficient_share"] = pd.to_numeric(selected["negative_coefficient_share"], errors="coerce")
                    row = selected.iloc[0] if not selected.empty else None
                    if row is not None:
                        a, b, c, d = st.columns(4)
                        a.metric("Successful instrument estimates", int(row["successful_instrument_estimates"]))
                        b.metric("BH-significant estimates", int(row["bh_significant_instrument_estimates_5pct"]))
                        c.metric("Positive coefficient share", fmt_share(row["positive_coefficient_share"]))
                        d.metric("Median coefficient", fmt_num(row.get("median_coefficient"), 4))
                        st.caption(f"Median observations per instrument: {fmt_num(row.get('median_observations'), 0)} · Median R-squared: {fmt_num(row.get('median_r_squared'), 3)} · Median adjusted p-value: {fmt_num(row.get('median_adjusted_p_value'), 3)}")
                    display = selected[[c for c in ["feature_id", "mapped_instrument_count", "successful_instrument_estimates", "bh_significant_instrument_estimates_5pct", "positive_coefficient_share", "negative_coefficient_share", "median_coefficient", "coefficient_p25", "coefficient_p75", "median_observations", "median_r_squared", "median_adjusted_p_value"] if c in selected.columns]].copy()
                    display = display.rename(columns={"feature_id":"Source feature ID", "mapped_instrument_count":"Mapped instruments", "successful_instrument_estimates":"Successful estimates", "bh_significant_instrument_estimates_5pct":"BH-significant estimates", "positive_coefficient_share":"Positive sign share", "negative_coefficient_share":"Negative sign share", "median_coefficient":"Median coefficient", "coefficient_p25":"25th percentile", "coefficient_p75":"75th percentile", "median_observations":"Median observations", "median_r_squared":"Median R-squared", "median_adjusted_p_value":"Median BH-adjusted p-value"})
                    display.insert(0, "Macro indicator", human_macro_feature(selected_feature))
                    st.dataframe(display, use_container_width=True, hide_index=True)
                    st.download_button("Download selected macro evidence", selected.to_csv(index=False).encode("utf-8"), f"{theme}_macro_evidence.csv", "text/csv")
                # Compact evidence breadth view across predictors; not a ranking of coefficient magnitudes.
                st.markdown("**Where statistically significant estimates occur**")
                breadth = filtered.groupby("feature_id", dropna=False).agg(significant_estimates=("bh_significant_instrument_estimates_5pct", "sum"), successful_estimates=("successful_instrument_estimates", "sum")).reset_index()
                breadth["Macro indicator"] = breadth["feature_id"].map(human_macro_feature)
                breadth = breadth.sort_values(["significant_estimates", "successful_estimates"], ascending=False).head(15)
                if not breadth.empty:
                    st.bar_chart(breadth.set_index("Macro indicator")[["significant_estimates"]], use_container_width=True)
                    st.dataframe(breadth[["Macro indicator", "significant_estimates", "successful_estimates"]].rename(columns={"significant_estimates":"BH-significant estimates", "successful_estimates":"Successful estimates"}), use_container_width=True, hide_index=True)
                st.caption("BH means Benjamini–Hochberg adjustment for multiple testing. Counts are instrument-level tests, not independent theme-level tests. Significance alone does not establish economic importance.")

        with tabs[2]:
            st.markdown("**Equity-style and market factor context**")
            st.caption("These estimates help describe equity-style exposures that may accompany a theme. They are not macro sensitivities, alpha estimates or a substitute for the macro regressions.")
            if theme_factor.empty:
                st.info("No factor exposure aggregation is available for this theme.")
            else:
                c1, c2, c3 = st.columns(3)
                fscopes = [x for x in ["primary_only", "primary_plus_secondary", "context_only"] if x in theme_factor["scope"].unique()]
                fscope = c1.selectbox("Instrument scope", fscopes, index=fscopes.index("primary_plus_secondary") if "primary_plus_secondary" in fscopes else 0, format_func=lambda x: THEME_EVIDENCE_SCOPE_LABELS.get(x, x), key="evidence_factor_scope")
                groups = sorted(theme_factor["factor_analysis_group"].dropna().unique())
                fgroup = c2.selectbox("Factor coverage group", groups, format_func=lambda x: FACTOR_GROUP_LABELS.get(x, plain_label(x)), key="evidence_factor_group")
                regions = sorted(theme_factor.loc[theme_factor["factor_analysis_group"].eq(fgroup), "region"].dropna().unique())
                region = c3.selectbox("Region", regions, key="evidence_factor_region") if regions else None
                fview = theme_factor.loc[(theme_factor["scope"].eq(fscope)) & (theme_factor["factor_analysis_group"].eq(fgroup))]
                if region is not None:
                    fview = fview.loc[fview["region"].eq(region)]
                fview = fview.copy()
                fview["Factor"] = fview["feature_id"].map(lambda x: FACTOR_LABELS.get(str(x), str(x)))
                st.dataframe(fview[[c for c in ["Factor", "instruments_with_factor_rows", "estimated_instrument_count", "bh_significant_instrument_count_5pct", "positive_loading_share", "negative_loading_share", "median_loading", "loading_p25", "loading_p75"] if c in fview.columns]].rename(columns={"instruments_with_factor_rows":"Instruments with estimates", "estimated_instrument_count":"Estimated instruments", "bh_significant_instrument_count_5pct":"BH-significant loadings", "positive_loading_share":"Positive loading share", "negative_loading_share":"Negative loading share", "median_loading":"Median loading", "loading_p25":"25th percentile", "loading_p75":"75th percentile"}), use_container_width=True, hide_index=True)
                st.caption("Factor loadings should be interpreted within the selected factor group and region. Coverage is incomplete for some themes and instruments.")

        with tabs[3]:
            st.markdown("**Historical returns under different macro conditions**")
            st.caption("The regime observed at the end of month t is assigned to returns in month t+1. These are historical conditional associations, not causal effects or expected returns. Full theme portfolios include all mapped instruments; exclusive portfolios include instruments mapped to exactly one core theme.")
            if theme_regime.empty:
                st.info("No regime-conditioned theme performance is available.")
            else:
                c1, c2 = st.columns(2)
                portfolio = c1.selectbox("Theme return construction", sorted(theme_regime["portfolio_type"].dropna().unique()), format_func=lambda x: "All mapped instruments" if x == "full" else "Exclusive core-theme instruments", key="evidence_regime_portfolio")
                dimensions = sorted(theme_regime["classification_dimension"].dropna().unique(), key=lambda x: REGIME_DIMENSION_LABELS.get(x, x))
                dimension = c2.selectbox("Macro classification", dimensions, format_func=lambda x: REGIME_DIMENSION_LABELS.get(x, plain_label(x)), key="evidence_regime_dimension")
                rv = theme_regime.loc[(theme_regime["portfolio_type"].eq(portfolio)) & (theme_regime["classification_dimension"].eq(dimension))].copy()
                rv["classification_label_readable"] = rv["classification_label"].map(lambda x: REGIME_LABELS.get(str(x), plain_label(x)))
                rv["observation_count"] = pd.to_numeric(rv["observation_count"], errors="coerce")
                baseline = rv.loc[rv["classification_label"].eq("ALL_ELIGIBLE_MONTHS")]
                conditional = rv.loc[~rv["classification_label"].eq("ALL_ELIGIBLE_MONTHS")].copy()
                if not baseline.empty:
                    br = baseline.iloc[0]
                    x1, x2, x3 = st.columns(3)
                    x1.metric("Eligible baseline months", int(br["observation_count"]))
                    x2.metric("Baseline annualised return", fmt_return(br.get("baseline_annualised_arithmetic_return", br.get("annualised_arithmetic_return"))))
                    x3.metric("Baseline annualised volatility", fmt_return(br.get("baseline_annualised_volatility", br.get("annualised_volatility"))))
                if not conditional.empty:
                    conditional["sample_depth_readable"] = conditional["sample_depth"].map(lambda x: SAMPLE_DEPTH_LABELS.get(str(x), plain_label(x)))
                    show = conditional[[c for c in ["classification_label_readable", "observation_count", "sample_depth_readable", "annualised_arithmetic_return", "annualised_return_vs_baseline", "annualised_volatility", "annualised_downside_deviation", "positive_month_hit_rate", "fifth_percentile_monthly_return", "conditional_tail_mean_5pct"] if c in conditional.columns]].rename(columns={"classification_label_readable":"Macro condition", "observation_count":"Months observed", "sample_depth_readable":"Sample depth", "annualised_arithmetic_return":"Annualised return (arithmetic)", "annualised_return_vs_baseline":"Difference vs baseline (annualised)", "annualised_volatility":"Annualised volatility", "annualised_downside_deviation":"Annualised downside deviation", "positive_month_hit_rate":"Positive-month hit rate", "fifth_percentile_monthly_return":"5th percentile monthly return", "conditional_tail_mean_5pct":"Worst 5% average monthly return"}).copy()
                    pct_cols = [c for c in show.columns if c not in ["Macro condition", "Months observed", "Sample depth"]]
                    for col in pct_cols:
                        show[col] = pd.to_numeric(show[col], errors="coerce").map(lambda x: f"{x:.1%}" if pd.notna(x) else "—")
                    st.dataframe(show, use_container_width=True, hide_index=True)
                    chart = conditional[["classification_label_readable", "annualised_arithmetic_return"]].copy()
                    chart["annualised_arithmetic_return"] = pd.to_numeric(chart["annualised_arithmetic_return"], errors="coerce")
                    chart = chart.dropna(subset=["annualised_arithmetic_return"]).sort_values("annualised_arithmetic_return")
                    if not chart.empty:
                        st.markdown("**Annualised return by macro condition**")
                        st.bar_chart(chart.set_index("classification_label_readable")[["annualised_arithmetic_return"]].rename(columns={"annualised_arithmetic_return":"Annualised return"}), use_container_width=True)
                    shallow = conditional.loc[conditional["observation_count"].lt(12)]
                    if not shallow.empty:
                        st.warning(f"{len(shallow)} displayed condition(s) have fewer than 12 observations. Treat these statistics as descriptive only; avoid ranking or drawing strong conclusions from them.")
                    st.download_button("Download regime-conditioned theme evidence", rv.to_csv(index=False).encode("utf-8"), f"{theme}_regime_performance.csv", "text/csv")
                else:
                    st.info("No conditional observations are available for this classification and portfolio construction.")
                st.caption("Annualised return in the source is arithmetic (12 × mean monthly return), not compounded CAGR. Return-to-volatility is not Sharpe; no risk-free rate is deducted.")

        with tabs[4]:
            st.markdown("**Macro drivers and economic transmission**")
            if not theme_signals.empty:
                signal_view = theme_signals.copy()
                signal_view["Expected direction"] = signal_view["expected_impact_direction"].map(lambda x: EXPECTED_DIRECTION_LABELS.get(str(x), plain_label(x)))
                signal_view["Evidence status"] = signal_view["evidence_status"].map(lambda x: plain_label(x))
                cols = [c for c in ["signal_group", "signal_id", "Expected direction", "transmission_mechanism", "investment_horizon", "Evidence status", "interpretation_note"] if c in signal_view.columns]
                signal_view = signal_view.rename(columns={"signal_group":"Macro driver group", "signal_id":"Source signal ID", "transmission_mechanism":"Economic transmission", "investment_horizon":"Indicative horizon", "interpretation_note":"Interpretation"})
                st.dataframe(signal_view[[c for c in ["Macro driver group", "Source signal ID", "Expected direction", "Economic transmission", "Indicative horizon", "Evidence status", "Interpretation"] if c in signal_view.columns]], use_container_width=True, hide_index=True)
                st.warning("These macro-to-theme relationships are structural hypotheses. They should be reviewed against the economic mechanism and evidence; they are not established causal links.")
            else:
                st.info("No macro signal-to-theme relationships are currently mapped to this theme.")
            st.markdown("**Mapped instruments and their roles**")
            if not theme_instruments.empty:
                show = theme_instruments.copy()
                show["Exposure role"] = show.get("portfolio_role", show.get("exposure_role", pd.Series(index=show.index, dtype=str))).map(lambda x: plain_label(x))
                show["Instrument"] = show.apply(lambda r: f"{r.get('yahoo_symbol_candidate', r.get('instrument_id', ''))} ({r.get('instrument_id', '')})", axis=1)
                show["Mapping confidence"] = show.get("mapping_confidence", pd.Series(index=show.index, dtype=str))
                cols = [c for c in ["Instrument", "Exposure role", "exposure_class", "Mapping confidence", "evidence_status", "exposure_description", "key_caveat", "macro_successful_models", "macro_bh_significant_rows_5pct", "fama_french_factor_rows"] if c in show.columns]
                st.dataframe(show[cols].rename(columns={"exposure_class":"Exposure type", "evidence_status":"Structural evidence status", "exposure_description":"Why it is mapped", "key_caveat":"Key caveat", "macro_successful_models":"Successful macro models", "macro_bh_significant_rows_5pct":"BH-significant macro estimates", "fama_french_factor_rows":"Factor estimates"}), use_container_width=True, hide_index=True)
            else:
                st.info("Detailed instrument mapping evidence is unavailable. The reviewed mapping file remains available under Definitions & methodology.")

elif page == "Macro regimes":
    st.subheader("Macro regimes and economic composition")
    st.caption("Understand the broad growth and inflation backdrop, then look beneath the headline regime to see whether its component indicators are aligned or sending mixed signals. The existing four-quadrant regime classification is preserved; subgroup overlays are descriptive diagnostics, not additional regimes.")
    regime_monthly = data.get("regime_monthly", pd.DataFrame())
    subgroup_scores = data.get("regime_subgroups", pd.DataFrame())
    if regime_monthly.empty:
        st.warning("Macro regime history is unavailable. Run the existing macro regime build to populate reports/macro_regime/macro_regime_monthly.csv.")
    else:
        regime_monthly = regime_monthly.sort_values("month").copy()
        latest = regime_monthly.iloc[-1]
        a, b, c, d = st.columns(4)
        a.metric("Confirmed macro regime", plain_label(latest.get("confirmed_regime"), REGIME_LABELS))
        b.metric("Growth state", plain_label(latest.get("growth_state"), REGIME_LABELS))
        c.metric("Inflation state", plain_label(latest.get("inflation_state"), REGIME_LABELS))
        d.metric("Evidence quality", plain_label(latest.get("evidence_quality")))
        st.caption(f"Latest month: {pd.Timestamp(latest['month']):%B %Y} · {int(latest.get('required_confirmation_months', 2))} consecutive eligible months required for confirmation · threshold ±{float(latest.get('threshold', 0.5)):.2f}.")
        tabs = st.tabs(["Regime history", "Growth and inflation scores", "Subgroup composition", "How to interpret the engine"])
        with tabs[0]:
            st.markdown("**Confirmed regime and independent macro axes**")
            hist = regime_monthly.set_index("month")
            chart_cols = [c for c in ["growth_score", "inflation_score"] if c in hist.columns]
            if chart_cols:
                st.line_chart(hist[chart_cols], use_container_width=True)
            display = regime_monthly[[c for c in ["month", "confirmed_regime", "candidate_regime", "growth_state", "inflation_state", "evidence_quality", "candidate_persistence_months", "overall_regime_persistence_months"] if c in regime_monthly.columns]].copy()
            for col in ["confirmed_regime", "candidate_regime", "growth_state", "inflation_state", "evidence_quality"]:
                if col in display:
                    display[col] = display[col].map(lambda x: REGIME_LABELS.get(str(x), plain_label(x)))
            st.dataframe(display.sort_values("month", ascending=False), use_container_width=True, hide_index=True)
            st.caption("Candidate regimes are provisional. The confirmed regime follows the existing two-consecutive-month confirmation rule and is not backfilled from subgroup descriptions.")
        with tabs[1]:
            st.markdown("**Growth and inflation composite scores**")
            st.caption("Scores are standardised composite indicators. The engine uses the configured ±0.50 thresholds, eligibility/coverage checks and confirmation rules; the score is not a direct GDP or CPI forecast.")
            score = regime_monthly.set_index("month")[[c for c in ["growth_score", "inflation_score"] if c in regime_monthly.columns]]
            if not score.empty:
                st.line_chart(score, use_container_width=True)
            cov = regime_monthly[[c for c in ["month", "growth_source_coverage", "growth_available_subgroups", "growth_total_subgroups", "inflation_source_coverage", "inflation_available_subgroups", "inflation_total_subgroups"] if c in regime_monthly.columns]].copy()
            st.dataframe(cov.sort_values("month", ascending=False), use_container_width=True, hide_index=True)
        with tabs[2]:
            st.markdown("**What is driving the broad growth and inflation readings?**")
            if subgroup_scores.empty:
                st.info("Subgroup score history is unavailable.")
            else:
                sg = subgroup_scores.copy()
                sg["subgroup_label"] = sg["subgroup_id"].map(lambda x: SUBGROUP_LABELS.get(str(x), plain_label(x)))
                axis_options = [x for x in ["growth", "inflation"] if x in sg["signal_group"].unique()]
                axis = st.selectbox("Macro axis", axis_options, format_func=lambda x: "Growth and demand" if x == "growth" else "Inflation", key="regime_subgroup_axis")
                axis_rows = sg.loc[sg["signal_group"].eq(axis)].copy()
                available_subgroups = sorted(axis_rows["subgroup_id"].dropna().unique())
                selected_subgroups = st.multiselect("Subgroups", available_subgroups, default=available_subgroups, format_func=lambda x: SUBGROUP_LABELS.get(str(x), plain_label(x)), key="regime_subgroups_selected")
                axis_rows = axis_rows.loc[axis_rows["subgroup_id"].isin(selected_subgroups)]
                if not axis_rows.empty:
                    pivot = axis_rows.pivot_table(index="date", columns="subgroup_label", values="subgroup_score", aggfunc="mean").sort_index()
                    st.line_chart(pivot, use_container_width=True)
                    latest_sg = axis_rows.loc[axis_rows["date"].eq(axis_rows["date"].max())].copy()
                    st.dataframe(latest_sg[[c for c in ["subgroup_label", "subgroup_score", "subgroup_coverage", "subgroup_available_features", "subgroup_total_features"] if c in latest_sg.columns]].rename(columns={"subgroup_label":"Economic component", "subgroup_score":"Latest score", "subgroup_coverage":"Data coverage", "subgroup_available_features":"Available indicators", "subgroup_total_features":"Configured indicators"}), use_container_width=True, hide_index=True)
                latest_row = regime_monthly.iloc[-1]
                if axis == "growth":
                    st.info(f"Latest growth composition: {REGIME_LABELS.get(str(latest_row.get('growth_subgroup_overlay')), plain_label(latest_row.get('growth_subgroup_overlay')))}. This describes disagreement across growth components; it does not replace the growth state.")
                elif axis == "inflation":
                    st.info(f"Latest inflation composition: {REGIME_LABELS.get(str(latest_row.get('inflation_subgroup_overlay')), plain_label(latest_row.get('inflation_subgroup_overlay')))}. Headline and core measures can diverge because of volatile components and underlying price pressures.")
        with tabs[3]:
            st.markdown("**Methodology and limitations**")
            st.markdown("- Growth and inflation are assessed separately before being combined into the existing four-quadrant regime framework.\n- The engine retains its configured ±0.50 thresholds, coverage eligibility rules and two-consecutive-month confirmation.\n- Growth subgroup composition describes broad growth, consumer demand, housing activity and industrial activity.\n- Inflation subgroup composition compares headline and core inflation.\n- Subgroup overlays are explanatory labels only; they do not alter the confirmed regime.\n- Early history has limited subgroup coverage, so missing/insufficient classifications should not be interpreted as neutral conditions.")
            st.caption("See the macro regime diagnostics and transition reports for the underlying engine audit trail.")

elif page == "Connectivity & data quality":
    st.subheader("Connectivity and data quality")
    st.caption("Assess how themes connect to instruments and macro features, and review the coverage and integrity of the underlying research panels. Its objective is to expose mapping gaps, unresolved candidates and data-quality limitations before drawing conclusions from the dashboard.")
    if not coverage.empty:
        status_counts = coverage.get("connectivity_review_status", pd.Series(dtype=str)).value_counts().rename_axis("status").reset_index(name="themes")
        c1, c2, c3 = st.columns(3)
        c1.metric("Themes with coverage records", f"{len(coverage):,}")
        c2.metric("Themes with macro links", f"{int(coverage.get('has_macro_feature_links', pd.Series(dtype=bool)).astype(str).str.lower().eq('true').sum())}")
        c3.metric("Unresolved generic candidates", f"{int(pd.to_numeric(coverage.get('unresolved_generic_instrument_count', pd.Series(dtype=float)), errors='coerce').fillna(0).sum())}")
        st.markdown("### Coverage matrix")
        st.dataframe(coverage, use_container_width=True, hide_index=True)
        st.markdown("### Review status")
        st.dataframe(status_counts, use_container_width=True, hide_index=True)
        st.download_button("Download coverage matrix", coverage.to_csv(index=False).encode("utf-8"),
                           "theme_connectivity_coverage_matrix.csv", "text/csv")
    st.markdown("### Aggregate panel integrity")
    duplicate_keys = int(aggregate.duplicated(["theme_id", "date"]).sum()) if {"theme_id", "date"}.issubset(aggregate.columns) else -1
    st.metric("Duplicate theme-month keys", duplicate_keys)
    if duplicate_keys == 0:
        st.success("No duplicate theme-month keys found in the loaded aggregate panel.")
    else:
        st.warning("Duplicate theme-month keys exist or the required key columns are missing.")
    st.markdown("### Asset-class breakdown")
    if not asset_class.empty:
        chosen = st.selectbox("Theme for asset-class breakdown", theme_ids, format_func=display_theme, key="asset_theme")
        asset_rows = asset_class.loc[asset_class["theme_id"].eq(chosen)].copy()
        if "date" in asset_rows:
            asset_rows = asset_rows.loc[asset_rows["date"].eq(asset_rows["date"].max())]
        st.dataframe(asset_rows, use_container_width=True, hide_index=True)
    st.caption("No conviction score is calculated. All current theme mappings remain proposed and require economic review.")


elif page == "Metadata & methodology":
    st.subheader("Metadata & definitions")
    st.caption("Consult the reference classifications, mapping records and definitions that underpin the dashboard's research outputs. Its objective is to make the universe, feature construction and theme-to-instrument relationships auditable and easier to review.")
    theme_meta = read_csv(ROOT / "config" / "theme_data_mapping.csv")
    instrument_meta = read_csv(ROOT / "config" / "instrument_master.csv")
    feature_meta = read_csv(ROOT / "config" / "derived_features_catalog.csv")
    tabs = st.tabs(["Theme metadata", "Instrument metadata", "Connectivity review", "Feature definitions"])
    with tabs[0]:
        st.caption("Review theme definitions, mapped data inputs and related classification fields used to organise the research universe.")
        if not theme_meta.empty:
            st.dataframe(theme_meta,use_container_width=True,hide_index=True)
            st.download_button("Download theme metadata",theme_meta.to_csv(index=False).encode(),"theme_metadata.csv","text/csv")
        else: st.info("Theme metadata file was not found.")
    with tabs[1]:
        st.caption("Review the instrument universe and its identifiers, classifications and other reference attributes.")
        if not instrument_meta.empty:
            st.dataframe(instrument_meta,use_container_width=True,hide_index=True)
            st.download_button("Download instrument metadata",instrument_meta.to_csv(index=False).encode(),"instrument_metadata.csv","text/csv")
        else: st.info("Instrument master was not found.")
    with tabs[2]:
        st.caption("Inspect theme-to-instrument and theme-to-macro connectivity decisions, including mapping review status and feature availability.")
        if not coverage.empty:
            st.dataframe(coverage,use_container_width=True,hide_index=True)
            st.download_button("Download connectivity review",coverage.to_csv(index=False).encode(),"connectivity_review.csv","text/csv")
        if not feature_availability.empty:
            st.markdown("**Macro feature mapping status and availability**")
            st.dataframe(feature_availability,use_container_width=True,hide_index=True)
            st.download_button("Download macro mapping review",feature_availability.to_csv(index=False).encode(),"macro_mapping_review.csv","text/csv")
    with tabs[3]:
        st.caption("Consult the definitions, transformations and metadata for derived market and macro features used throughout the dashboard.")
        if not feature_meta.empty:
            st.dataframe(feature_meta,use_container_width=True,hide_index=True)
            st.download_button("Download feature definitions",feature_meta.to_csv(index=False).encode(),"feature_definitions.csv","text/csv")
        else: st.info("Derived feature catalogue was not found.")

st.divider()
st.caption("Prototype dashboard · uses local project outputs · no live data fetches · no trade recommendations")
