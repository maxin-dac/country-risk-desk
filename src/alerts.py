# -*- coding: utf-8 -*-
"""Moteur d'alertes : règles de seuils déterministes + génération de risques/opportunités."""
import pandas as pd

# Règles de seuils : chaque règle définit un indicateur, une condition, et des libellés FR/EN
RULES = [
    # Règles macroéconomiques classiques
    dict(id="inflation_high", indicator="Inflation", cond=lambda v: v > 10, desc=True,
         en="Inflation above 10 %", fr="Inflation supérieure à 10 %"),
    dict(id="recession", indicator="GDP growth", cond=lambda v: v < 0, desc=False,
         en="Negative GDP growth", fr="Croissance du PIB négative"),
    dict(id="reserves_low", indicator="Reserves", cond=lambda v: v < 3, desc=False,
         en="Reserves below 3 months of imports", fr="Réserves sous 3 mois d'importations"),
    dict(id="debt_high", indicator="Gen gov debt", cond=lambda v: v > 90, desc=True,
         en="Government debt above 90 % of GDP", fr="Dette publique au-dessus de 90 % du PIB"),
    dict(id="ca_deficit", indicator="Current account", cond=lambda v: v < -5, desc=False,
         en="Current account deficit beyond -5 % of GDP", fr="Déficit courant au-delà de -5 % du PIB"),
    dict(id="unemp_high", indicator="Unemployment", cond=lambda v: v > 15, desc=True,
         en="Unemployment above 15 %", fr="Chômage supérieur à 15 %"),
    dict(id="youth_unemp_high", indicator="Youth unemployment", cond=lambda v: v > 25, desc=True,
         en="Youth unemployment above 25 %", fr="Chômage des jeunes supérieur à 25 %"),
    
    # Règles de gouvernance (WGI)
    dict(id="political_instability", indicator="Political stability", cond=lambda v: v < -1.0, desc=False,
         en="Political stability below -1.0", fr="Stabilité politique inférieure à -1,0"),
    dict(id="corruption_high", indicator="Control of corruption", cond=lambda v: v < -0.5, desc=False,
         en="Control of corruption below -0.5", fr="Maîtrise de la corruption inférieure à -0,5"),
    dict(id="gov_effectiveness_low", indicator="Government effectiveness", cond=lambda v: v < -0.5, desc=False,
         en="Government effectiveness below -0.5", fr="Efficacité du gouvernement inférieure à -0,5"),
    
    # Règles sociales
    dict(id="gini_high", indicator="Gini", cond=lambda v: v > 45, desc=True,
         en="Gini index above 45 (high inequality)", fr="Indice de Gini supérieur à 45 (inégalités élevées)"),
    
    # Règles de dette externe
    dict(id="external_debt_high", indicator="External debt", cond=lambda v: v > 60, desc=True,
         en="External debt above 60% of GNI", fr="Dette externe supérieure à 60 % du RNB"),
]

# Regles de risques pour generate_outlook (libelles avec valeur courante)
RISK_RULES = [
    dict(r, en=(lambda v, _r=r: f"{_r['en']} (value: {v:.1f})"),
            fr=(lambda v, _r=r: f"{_r['fr']} (valeur : {v:.1f})"))
    for r in RULES
]

# Regles miroir d'opportunites (seuils favorables)
OPP_RULES = [
    dict(id="inflation_low", indicator="Inflation", cond=lambda v: v < 3,
         en=lambda v: f"Inflation contained below 3 % (value: {v:.1f})",
         fr=lambda v: f"Inflation contenue sous 3 % (valeur : {v:.1f})"),
    dict(id="growth_strong", indicator="GDP growth", cond=lambda v: v > 5,
         en=lambda v: f"Strong GDP growth above 5 % (value: {v:.1f})",
         fr=lambda v: f"Croissance du PIB soutenue au-dessus de 5 % (valeur : {v:.1f})"),
    dict(id="reserves_high", indicator="Reserves", cond=lambda v: v > 6,
         en=lambda v: f"Comfortable reserves above 6 months of imports (value: {v:.1f})",
         fr=lambda v: f"Réserves confortables au-dessus de 6 mois d'importations (valeur : {v:.1f})"),
    dict(id="debt_low", indicator="Gen gov debt", cond=lambda v: v < 40,
         en=lambda v: f"Government debt below 40 % of GDP (value: {v:.1f})",
         fr=lambda v: f"Dette publique sous 40 % du PIB (valeur : {v:.1f})"),
    dict(id="ca_surplus", indicator="Current account", cond=lambda v: v > 3,
         en=lambda v: f"Current account surplus above 3 % of GDP (value: {v:.1f})",
         fr=lambda v: f"Excédent courant au-dessus de 3 % du PIB (valeur : {v:.1f})"),
    dict(id="unemp_low", indicator="Unemployment", cond=lambda v: v < 5,
         en=lambda v: f"Low unemployment below 5 % (value: {v:.1f})",
         fr=lambda v: f"Chômage faible sous 5 % (valeur : {v:.1f})"),
    dict(id="youth_unemp_low", indicator="Youth unemployment", cond=lambda v: v < 12,
         en=lambda v: f"Youth unemployment below 12 % (value: {v:.1f})",
         fr=lambda v: f"Chômage des jeunes sous 12 % (valeur : {v:.1f})"),
    dict(id="pol_stability_high", indicator="Political stability", cond=lambda v: v > 0.5,
         en=lambda v: f"Strong political stability above 0.5 (value: {v:.2f})",
         fr=lambda v: f"Stabilité politique solide au-dessus de 0,5 (valeur : {v:.2f})"),
    dict(id="corruption_ctrl_high", indicator="Control of corruption", cond=lambda v: v > 0.5,
         en=lambda v: f"Good control of corruption above 0.5 (value: {v:.2f})",
         fr=lambda v: f"Maîtrise de la corruption solide au-dessus de 0,5 (valeur : {v:.2f})"),
    dict(id="gov_eff_high", indicator="Government effectiveness", cond=lambda v: v > 0.5,
         en=lambda v: f"Effective government above 0.5 (value: {v:.2f})",
         fr=lambda v: f"Efficacité du gouvernement solide au-dessus de 0,5 (valeur : {v:.2f})"),
    dict(id="gini_low", indicator="Gini", cond=lambda v: v < 35,
         en=lambda v: f"Low inequality (Gini below 35, value: {v:.1f})",
         fr=lambda v: f"Inégalités contenues (Gini sous 35, valeur : {v:.1f})"),
    dict(id="ext_debt_low", indicator="External debt", cond=lambda v: v < 30,
         en=lambda v: f"External debt below 30 % of GNI (value: {v:.1f})",
         fr=lambda v: f"Dette externe sous 30 % du RNB (valeur : {v:.1f})"),
]

def generate_outlook(stats):
    if not stats.get("available"):
        return {"risks": [], "opportunities": [], "uncertainties": []}
    v = stats.get("latest_value")
    ind = stats.get("indicator")
    risks, opps, uncs = [], [], []
    for rule in RISK_RULES:
        if rule["indicator"] == ind and rule["cond"](v):
            risks.append({"text_en": rule["en"](v), "text_fr": rule["fr"](v),
                          "rule_id": rule["id"], "value": v})
    for rule in OPP_RULES:
        if rule["indicator"] == ind and rule["cond"](v):
            opps.append({"text_en": rule["en"](v), "text_fr": rule["fr"](v),
                         "rule_id": rule["id"], "value": v})
    if stats.get("change_12m_pct") is None and stats.get("change_3m_pct") is None:
        uncs.append({"text_en": "Limited historical data to assess the trend.",
                     "text_fr": "Donnees historiques limitees pour evaluer la tendance."})
    if stats.get("regional_median") is None:
        uncs.append({"text_en": "Regional comparison unavailable for this indicator.",
                     "text_fr": "Comparaison regionale indisponible pour cet indicateur."})
    return {"risks": risks, "opportunities": opps, "uncertainties": uncs}



def compute_alerts(df):
    """Bandeau d'alertes global - version defensive (ne plante jamais)."""
    out = []
    if df is None or "value" not in df.columns:
        return out
    latest = df.sort_values("date").groupby(["country", "indicator"], as_index=False).tail(1)
    for rule in RULES:
        sub = latest.loc[latest["indicator"] == rule["indicator"]].dropna(subset=["value"]).copy()
        if sub.empty:
            continue
        nums = pd.to_numeric(sub["value"], errors="coerce")
        mask = nums.map(rule["cond"]).fillna(False).astype(bool).values
        hit = sub.loc[mask].copy()
        if hit.empty:
            continue
        hit["_sort"] = pd.to_numeric(hit["value"], errors="coerce")
        hit = hit.sort_values("_sort", ascending=not rule["desc"])
        out.append({**rule,
                    "hits": [(r["country"], float(r["value"])) for _, r in hit.iterrows()]})
    return [a for a in out if a["hits"]]

# Regles budgetaires (solde budgetaire) - sans doublon avec debt_high/debt_low
if "RISK_RULES" in globals():
    RISK_RULES += [
        dict(id="fiscal_deficit", indicator="Fiscal balance", cond=lambda v: v < -5,
             en=lambda v: f"Fiscal deficit of {abs(v):.1f}% of GDP: sustained consolidation needed.",
             fr=lambda v: f"D\u00e9ficit budg\u00e9taire de {abs(v):.1f}% du PIB : assainissement soutenu n\u00e9cessaire."),
    ]
if "OPP_RULES" in globals():
    OPP_RULES += [
        dict(id="fiscal_surplus", indicator="Fiscal balance", cond=lambda v: v > 1,
             en=lambda v: f"Fiscal surplus of {v:.1f}% of GDP: comfortable policy space.",
             fr=lambda v: f"Exc\u00e9dent budg\u00e9taire de {v:.1f}% du PIB : marge de man\u0153uvre confortable."),
    ]
if "RULES" in globals():
    RULES += [
        dict(id="fiscal_deficit", indicator="Fiscal balance", cond=lambda v: v < -5, desc=False,
             en="Fiscal deficit beyond -5 % of GDP", fr="D\u00e9ficit budg\u00e9taire au-del\u00e0 de -5 % du PIB"),
    ]

# -- REINTRO-RULES-WGI2 : regles pour Rule of law + Regulatory quality --
if "RULES" in globals() and not any(r["id"] == "rule_of_law_low" for r in RULES):
    RULES += [
        dict(id="rule_of_law_low", indicator="Rule of law", cond=lambda v: v < -0.5, desc=False,
             en="Rule of law below -0.5", fr="État de droit inférieur à -0,5"),
        dict(id="regulatory_quality_low", indicator="Regulatory quality", cond=lambda v: v < -0.5, desc=False,
             en="Regulatory quality below -0.5", fr="Qualité réglementaire inférieure à -0,5"),
    ]
    RISK_RULES += [
        dict(id="rule_of_law_low", indicator="Rule of law", cond=lambda v: v < -0.5,
             en=lambda v: f"Rule of law at {v:.2f}: weak legal enforcement.",
             fr=lambda v: f"État de droit à {v:.2f} : application du droit fragile."),
        dict(id="regulatory_quality_low", indicator="Regulatory quality", cond=lambda v: v < -0.5,
             en=lambda v: f"Regulatory quality at {v:.2f}: weak policy framework.",
             fr=lambda v: f"Qualité réglementaire à {v:.2f} : cadre politique fragile."),
    ]
    OPP_RULES += [
        dict(id="rule_of_law_high", indicator="Rule of law", cond=lambda v: v > 0.5,
             en=lambda v: f"Strong rule of law at {v:.2f}: solid legal enforcement.",
             fr=lambda v: f"État de droit solide à {v:.2f} : application du droit fiable."),
        dict(id="regulatory_quality_high", indicator="Regulatory quality", cond=lambda v: v > 0.5,
             en=lambda v: f"Strong regulatory quality at {v:.2f}: sound policy framework.",
             fr=lambda v: f"Qualité réglementaire solide à {v:.2f} : cadre politique sain."),
    ]
