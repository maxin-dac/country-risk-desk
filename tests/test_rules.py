"""Tests unitaires - regles d'alertes, scoring et tendances."""
import pandas as pd

from src import alerts as al


def _df(rows):
    return pd.DataFrame(
        [dict(country=c, indicator=i, date=d, value=v,
              region="Test", unit="", category="", source="")
         for c, i, d, v in rows])


# ---------- Alertes ----------
def test_inflation_high():
    df = _df([("FRA", "Inflation", "2024-12-31", 12.0),
              ("DEU", "Inflation", "2024-12-31", 2.0)])
    hits = {a["id"]: [c for c, _ in a["hits"]] for a in al.compute_alerts(df)}
    assert hits.get("inflation_high") == ["FRA"]


def test_reserves_low():
    df = _df([("ARG", "Reserves", "2024-12-31", 2.1),
              ("CHE", "Reserves", "2024-12-31", 20.0)])
    hits = {a["id"]: [c for c, _ in a["hits"]] for a in al.compute_alerts(df)}
    assert hits.get("reserves_low") == ["ARG"]


def test_no_alert_below_threshold():
    df = _df([("DEU", "Inflation", "2024-12-31", 2.0)])
    assert all(a["id"] != "inflation_high" for a in al.compute_alerts(df))


def test_generate_outlook_risk_and_opp():
    out = al.generate_outlook({"available": True, "indicator": "Inflation",
                               "latest_value": 15.0})
    assert any(r["rule_id"] == "inflation_high" for r in out["risks"])
    out2 = al.generate_outlook({"available": True, "indicator": "Inflation",
                                "latest_value": 2.0})
    assert any(r["rule_id"] == "inflation_low" for r in out2["opportunities"])


# ---------- Scoring ----------
# ---------- Tendance ----------
def test_trend_5y_in_stats():
    from src.csv_loader import get_stats
    dates = pd.to_datetime([f"{y}-12-31" for y in range(2015, 2025)])
    df = pd.DataFrame({"country": ["TST"] * 10, "indicator": ["Inflation"] * 10,
                       "date": dates, "value": [10 + i for i in range(10)],
                       "region": "Test", "unit": "%", "category": "", "source": ""})
    st_ = get_stats(df, "TST", "Inflation")
    assert st_.get("trend_5y_norm", 0) > 0
