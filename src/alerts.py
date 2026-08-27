import pandas as pd
"""Moteur de regles deterministes - risques et opportunites par pilier."""

RISK_RULES = [
    # Externe & souverain
    dict(id="reserves_low", indicator="Reserves", cond=lambda v: v < 3,
         en=lambda v: f"Reserves cover only {v:.1f} months of imports: transfer and convertibility risk.",
         fr=lambda v: f"Les reserves ne couvrent que {v:.1f} mois d'importations : risque de transfert et de convertibilite."),
    dict(id="ca_deficit", indicator="Current account", cond=lambda v: v < -5,
         en=lambda v: f"Current account deficit of {v:.1f}% of GDP: structural need for external financing.",
         fr=lambda v: f"Deficit courant de {v:.1f}% du PIB : besoin structurel de financement externe."),
    dict(id="ext_debt_high", indicator="External debt", cond=lambda v: v > 80,
         en=lambda v: f"External debt at {v:.1f}% of GNI: high exposure to exchange-rate and rate shocks.",
         fr=lambda v: f"Dette externe a {v:.1f}% du RNB : forte exposition aux chocs de change et de taux."),
    dict(id="debt_service_high", indicator="Debt service", cond=lambda v: v > 25,
         en=lambda v: f"Debt service absorbs {v:.1f}% of exports: restructuring risk on external obligations.",
         fr=lambda v: f"Le service de la dette absorbe {v:.1f}% des exports : risque de restructuration des obligations externes."),
    # Macro-economique
    dict(id="inflation_high", indicator="Inflation", cond=lambda v: v > 10,
         en=lambda v: f"Inflation at {v:.1f}%: erosion of purchasing power and monetary instability.",
         fr=lambda v: f"Inflation a {v:.1f}% : erosion du pouvoir d'achat et instabilite monetaire."),
    dict(id="recession", indicator="GDP growth", cond=lambda v: v < 0,
         en=lambda v: f"GDP contraction of {v:.1f}%: recession risk materialized.",
         fr=lambda v: f"Contraction du PIB de {v:.1f}% : risque de recession materialise."),
    dict(id="debt_high", indicator="Gov debt", cond=lambda v: v > 90,
         en=lambda v: f"Government debt at {v:.1f}% of GDP: limited fiscal space, refinancing risk.",
         fr=lambda v: f"Dette publique a {v:.1f}% du PIB : marge budgetaire limitee, risque de refinancement."),
    dict(id="unemp_high", indicator="Unemployment", cond=lambda v: v > 15,
         en=lambda v: f"Unemployment at {v:.1f}%: labor-market distress and social pressure.",
         fr=lambda v: f"Chomage a {v:.1f}% : marche du travail en difficulte et pression sociale."),
    # Politique & institutionnel
    dict(id="pol_instability", indicator="Political stability", cond=lambda v: v < -1.0,
         en=lambda v: f"Political stability at {v:.2f}: institutional fragility and policy uncertainty.",
         fr=lambda v: f"Stabilite politique a {v:.2f} : fragilite institutionnelle et incertitude sur les politiques."),
    dict(id="rule_of_law_low", indicator="Rule of law", cond=lambda v: v < -0.5,
         en=lambda v: f"Rule of law at {v:.2f}: legal insecurity, expropriation risk for investors.",
         fr=lambda v: f"Etat de droit a {v:.2f} : insecurite juridique, risque d'expropriation pour les investisseurs."),
    dict(id="reg_quality_low", indicator="Regulatory quality", cond=lambda v: v < -0.5,
         en=lambda v: f"Regulatory quality at {v:.2f}: unpredictable business environment.",
         fr=lambda v: f"Qualite reglementaire a {v:.2f} : environnement des affaires imprevisible."),
    dict(id="corruption_high", indicator="Control of corruption", cond=lambda v: v < -0.5,
         en=lambda v: f"Control of corruption at {v:.2f}: governance and fiscal-efficiency risk.",
         fr=lambda v: f"Controle de la corruption a {v:.2f} : risque de gouvernance et d'efficacite budgetaire."),
    # Social & structurel
    dict(id="gini_high", indicator="Gini", cond=lambda v: v > 45,
         en=lambda v: f"Gini at {v:.0f}: high inequality, latent social-contestation risk.",
         fr=lambda v: f"Gini a {v:.0f} : inegalites elevees, risque latent de contestation sociale."),
    dict(id="youth_unemp_high", indicator="Youth unemployment", cond=lambda v: v > 25,
         en=lambda v: f"Youth unemployment at {v:.1f}%: structural instability risk.",
         fr=lambda v: f"Chomage des jeunes a {v:.1f}% : risque structurel d'instabilite."),
    dict(id="dependency_high", indicator="Dependency ratio", cond=lambda v: v > 80,
         en=lambda v: f"Dependency ratio at {v:.0f}%: demographic pressure on public finances.",
         fr=lambda v: f"Ratio de dependance a {v:.0f}% : pression demographique sur les finances publiques."),
    dict(id="commodity_high", indicator="Commodity dependence", cond=lambda v: v > 60,
         en=lambda v: f"{v:.0f}% of merchandise exports are commodities: terms-of-trade vulnerability.",
         fr=lambda v: f"{v:.0f}% des exports de marchandises sont des matieres premieres : vulnerabilite aux termes de l'echange."),
]

OPP_RULES = [
    dict(id="reserves_strong", indicator="Reserves", cond=lambda v: v > 12,
         en=lambda v: f"Reserves cover {v:.1f} months of imports: strong external buffer.",
         fr=lambda v: f"Les reserves couvrent {v:.1f} mois d'importations : tampon externe solide."),
    dict(id="ca_surplus", indicator="Current account", cond=lambda v: v > 3,
         en=lambda v: f"Current account surplus of {v:.1f}% of GDP: external position supportive.",
         fr=lambda v: f"Excedent courant de {v:.1f}% du PIB : position externe favorable."),
    dict(id="strong_growth", indicator="GDP growth", cond=lambda v: v > 5,
         en=lambda v: f"Robust growth of {v:.1f}%: strong momentum and investment appeal.",
         fr=lambda v: f"Croissance robuste de {v:.1f}% : dynamisme fort et attrait pour l'investissement."),
    dict(id="low_inflation", indicator="Inflation", cond=lambda v: 0 < v < 3,
         en=lambda v: f"Inflation anchored at {v:.1f}%: macroeconomic stability.",
         fr=lambda v: f"Inflation ancree a {v:.1f}% : stabilite macroeconomique."),
    dict(id="rule_of_law_high", indicator="Rule of law", cond=lambda v: v > 0.5,
         en=lambda v: f"Rule of law at {v:.2f}: strong legal protection for investors.",
         fr=lambda v: f"Etat de droit a {v:.2f} : protection juridique solide pour les investisseurs."),
    dict(id="reg_quality_high", indicator="Regulatory quality", cond=lambda v: v > 0.5,
         en=lambda v: f"Regulatory quality at {v:.2f}: predictable and supportive business rules.",
         fr=lambda v: f"Qualite reglementaire a {v:.2f} : regles du jeu previsibles et favorables."),
    dict(id="low_unemp", indicator="Unemployment", cond=lambda v: v < 5,
         en=lambda v: f"Unemployment at {v:.1f}%: tight labor market supporting demand.",
         fr=lambda v: f"Chomage a {v:.1f}% : marche du travail tendu soutenant la demande."),
    dict(id="youth_unemp_low", indicator="Youth unemployment", cond=lambda v: v < 12,
         en=lambda v: f"Youth unemployment at {v:.1f}%: social cohesion supportive.",
         fr=lambda v: f"Chomage des jeunes a {v:.1f}% : cohesion sociale favorable."),
    dict(id="commodity_low", indicator="Commodity dependence", cond=lambda v: v < 15,
         en=lambda v: f"Only {v:.0f}% of exports are commodities: diversified export base.",
         fr=lambda v: f"Seulement {v:.0f}% des exports sont des matieres premieres : base exportatrice diversifiee."),
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


RULES = [
    dict(id="inflation_high", indicator="Inflation", cond=lambda v: v > 10, desc=True,
         en="Inflation above 10 %", fr="Inflation superieure a 10 %"),
    dict(id="recession", indicator="GDP growth", cond=lambda v: v < 0, desc=False,
         en="Negative GDP growth", fr="Croissance du PIB negative"),
    dict(id="reserves_low", indicator="Reserves", cond=lambda v: v < 3, desc=False,
         en="Reserves below 3 months of imports", fr="Reserves sous 3 mois d'importations"),
    dict(id="debt_high", indicator="Gov debt", cond=lambda v: v > 90, desc=True,
         en="Government debt above 90 % of GDP", fr="Dette publique au-dessus de 90 % du PIB"),
    dict(id="debt_service_high", indicator="Debt service", cond=lambda v: v > 25, desc=True,
         en="Debt service above 25 % of exports", fr="Service de la dette au-dessus de 25 % des exports"),
    dict(id="ca_deficit", indicator="Current account", cond=lambda v: v < -5, desc=False,
         en="Current account deficit beyond -5 % of GDP", fr="Deficit courant au-dela de -5 % du PIB"),
    dict(id="unemp_high", indicator="Unemployment", cond=lambda v: v > 15, desc=True,
         en="Unemployment above 15 %", fr="Chomage superieur a 15 %"),
    dict(id="youth_unemp_high", indicator="Youth unemployment", cond=lambda v: v > 25, desc=True,
         en="Youth unemployment above 25 %", fr="Chomage des jeunes superieur a 25 %"),
    dict(id="rule_of_law_low", indicator="Rule of law", cond=lambda v: v < -1.0, desc=False,
         en="Rule of law below -1.0", fr="Etat de droit sous -1,0"),
]


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

if "RISK_RULES" in globals():
    RISK_RULES += [
        dict(id="fiscal_deficit", indicator="Fiscal balance", cond=lambda v: v < -5,
             en=lambda v: f"Fiscal deficit of {abs(v):.1f}% of GDP: sustained consolidation needed.",
             fr=lambda v: f"Deficit budgetaire de {abs(v):.1f}% du PIB : assainissement soutenu necessaire."),
        dict(id="ggdebt_high", indicator="Gen gov debt", cond=lambda v: v > 90,
             en=lambda v: f"General government debt at {v:.1f}% of GDP: high refinancing risk.",
             fr=lambda v: f"Dette publique generale a {v:.1f}% du PIB : risque de refinancement eleve."),
    ]
if "OPP_RULES" in globals():
    OPP_RULES += [
        dict(id="fiscal_surplus", indicator="Fiscal balance", cond=lambda v: v > 1,
             en=lambda v: f"Fiscal surplus of {v:.1f}% of GDP: comfortable policy space.",
             fr=lambda v: f"Excedent budgetaire de {v:.1f}% du PIB : marge de manouvre confortable."),
        dict(id="ggdebt_low", indicator="Gen gov debt", cond=lambda v: v < 40,
             en=lambda v: f"General government debt at {v:.1f}% of GDP: solid fiscal position.",
             fr=lambda v: f"Dette publique generale a {v:.1f}% du PIB : position budgetaire solide."),
    ]
if "RULES" in globals():
    RULES += [
        dict(id="fiscal_deficit", indicator="Fiscal balance", cond=lambda v: v < -5, desc=False,
             en="Fiscal deficit beyond -5 % of GDP", fr="Deficit budgetaire au-dela de -5 % du PIB"),
        dict(id="ggdebt_high", indicator="Gen gov debt", cond=lambda v: v > 90, desc=True,
             en="General government debt above 90 % of GDP", fr="Dette publique generale au-dessus de 90 % du PIB"),
    ]
