"""Tests unitaires - regles d'alertes, scoring et tendances."""
import pandas as pd

from src import alerts as al
from src import risk_scoring as rs


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
def test_subscore_bounds():
    assert rs._subscore("Inflation", 2.0) == 0.0
    assert rs._subscore("Inflation", 20.0) == 100.0
    assert abs(rs._subscore("Inflation", 11.0) - 50.0) < 1.0


def test_subscore_inverse_direction():
    assert rs._subscore("Reserves", 8.0) == 0.0
    assert rs._subscore("Reserves", 1.5) == 100.0


def test_subscore_clamps():
    assert rs._subscore("Inflation", 500.0) == 100.0
    assert rs._subscore("Reserves", -5.0) == 100.0


def test_label_for():
    assert rs.label_for(10)[0] == "Low"
    assert rs.label_for(45)[0] == "Moderate"
    assert rs.label_for(60)[0] == "Elevated"
    assert rs.label_for(90)[0] == "Critical"


def test_country_scores_ordering():
    df = _df([
        ("RIS", "Inflation", "2024-12-31", 25.0),
        ("RIS", "Reserves", "2024-12-31", 1.0),
        ("SAF", "Inflation", "2024-12-31", 2.0),
        ("SAF", "Reserves", "2024-12-31", 10.0),
    ])
    sc = rs.country_scores(df)
    assert sc["RIS"]["overall"] > sc["SAF"]["overall"]


# ---------- Tendance ----------
def test_trend_5y_in_stats():
    from src.csv_loader import get_stats
    dates = pd.to_datetime([f"{y}-12-31" for y in range(2015, 2025)])
    df = pd.DataFrame({"country": ["TST"] * 10, "indicator": ["Inflation"] * 10,
                       "date": dates, "value": [10 + i for i in range(10)],
                       "region": "Test", "unit": "%", "category": "", "source": ""})
    st_ = get_stats(df, "TST", "Inflation")
    assert st_.get("trend_5y_norm", 0) > 0
