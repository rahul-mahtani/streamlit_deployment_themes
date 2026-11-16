from pathlib import Path
import pandas as pd

def test_aggregate_panel_has_core_columns():
    path = Path(__file__).parent / "fixtures" / "theme_monthly_aggregate_panel.csv"
    df = pd.read_csv(path)
    assert {"theme_id", "date", "period_status", "MOM_3M_median"}.issubset(df.columns)
    assert not df.duplicated(["theme_id", "date"]).any()
