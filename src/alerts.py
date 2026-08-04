"""Alertes seuil — calcul deterministe sur les dernieres valeurs Banque Mondiale."""
import pandas as pd

RULES = [
    dict(id="inflation_high", indicator="Inflation", cond=lambda v: v > 10, desc=True,
         en="Inflation above 10 %", fr="Inflation supérieure à 10 %"),
    dict(id="recession", indicator="GDP growth", cond=lambda v: v < 0, desc=False,
         en="Negative GDP growth", fr="Croissance du PIB négative"),
    dict(id="reserves_low", indicator="Reserves", cond=lambda v: v < 3, desc=False,
         en="Reserves below 3 months of imports", fr="Réserves sous 3 mois d'importations"),
    dict(id="debt_high", indicator="Gov debt", cond=lambda v: v > 90, desc=True,
         en="Government debt above 90 % of GDP", fr="Dette publique au-dessus de 90 % du PIB"),
    dict(id="ca_deficit", indicator="Current account", cond=lambda v: v < -5, desc=False,
         en="Current account deficit beyond -5 % of GDP", fr="Déficit courant au-delà de -5 % du PIB"),
    dict(id="unemp_high", indicator="Unemployment", cond=lambda v: v > 15, desc=True,
         en="Unemployment above 15 %", fr="Chômage supérieur à 15 %"),
    dict(id="electricity_low", indicator="Electricity access", cond=lambda v: v < 50, desc=False,
         en="Access to electricity below 50 %", fr="Accès à l'électricité sous 50 %"),
]


def compute_alerts(df):
    latest = df.sort_values("date").groupby(["country", "indicator"], as_index=False).tail(1)
    out = []
    for rule in RULES:
        sub = latest[latest.indicator == rule["indicator"]].dropna(subset=["value"])
        hit = sub[sub.value.astype(float).map(rule["cond"])]
        hit = hit.sort_values("value", ascending=not rule["desc"])
        out.append({**rule, "hits": [(r.country, float(r.value)) for r in hit.itertuples()]})
    return [a for a in out if a["hits"]]
