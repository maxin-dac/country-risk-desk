"""Moteur de regles deterministes - genere risques et opportunites a partir des donnees Banque Mondiale."""

# Risques : seuils negatifs a surveiller
RISK_RULES = [
    dict(id="inflation_high", indicator="Inflation",
         cond=lambda v: v > 10,
         en=lambda v: f"Inflation critically high at {v:.1f}%, eroding purchasing power and real wages.",
         fr=lambda v: f"Inflation critique a {v:.1f}%, erodant le pouvoir d'achat et les salaires reels."),
    dict(id="recession", indicator="GDP growth",
         cond=lambda v: v < 0,
         en=lambda v: f"Economic contraction: GDP fell by {v:.1f}%, signaling recession.",
         fr=lambda v: f"Contraction economique : le PIB a recule de {v:.1f}%, signe de recession."),
    dict(id="reserves_low", indicator="Reserves",
         cond=lambda v: v < 3,
         en=lambda v: f"Reserves cover only {v:.1f} months of imports, exposing the currency to external shocks.",
         fr=lambda v: f"Les reserves ne couvrent que {v:.1f} mois d'importations, exposant la monnaie aux chocs externes."),
    dict(id="debt_high", indicator="Gov debt",
         cond=lambda v: v > 90,
         en=lambda v: f"Government debt at {v:.1f}% of GDP, limiting fiscal space and raising refinancing risk.",
         fr=lambda v: f"Dette publique a {v:.1f}% du PIB, limitant la marge de manouvre budgetaire et le risque de refinancement."),
    dict(id="ca_deficit", indicator="Current account",
         cond=lambda v: v < -5,
         en=lambda v: f"Current account deficit of {v:.1f}% of GDP, requiring sustained foreign capital inflows.",
         fr=lambda v: f"Deficit courant de {v:.1f}% du PIB, necessitant des flux de capitaux etrangers soutenus."),
    dict(id="unemp_high", indicator="Unemployment",
         cond=lambda v: v > 15,
         en=lambda v: f"Unemployment at {v:.1f}%, indicating labor market distress and social pressure.",
         fr=lambda v: f"Chomage a {v:.1f}%, signalant un marche du travail en difficulte et une pression sociale."),
    dict(id="electricity_low", indicator="Electricity access",
         cond=lambda v: v < 50,
         en=lambda v: f"Only {v:.1f}% of population has electricity access, a major infrastructure gap.",
         fr=lambda v: f"Seulement {v:.1f}% de la population a acces a l'electricite, un deficit infrastructurel majeur."),
    dict(id="ext_debt_high", indicator="External debt",
         cond=lambda v: v > 80,
         en=lambda v: f"External debt at {v:.1f}% of GNI, creating vulnerability to exchange rate and rate shocks.",
         fr=lambda v: f"Dette externe a {v:.1f}% du RNB, creant une vulnerabilite au taux de change et aux taux."),
    dict(id="political_instability", indicator="Political stability",
         cond=lambda v: v < -1.0,
         en=lambda v: f"Political stability index at {v:.2f}, indicating institutional fragility.",
         fr=lambda v: f"Indice de stabilite politique a {v:.2f}, signalant une fragilite institutionnelle."),
    dict(id="corruption_high", indicator="Control of corruption",
         cond=lambda v: v < -0.5,
         en=lambda v: f"Control of corruption at {v:.2f}, undermining business environment and fiscal efficiency.",
         fr=lambda v: f"Controle de la corruption a {v:.2f}, affectant le climat des affaires et l'efficacite budgetaire."),
]

# Opportunites : seuils positifs a valoriser
OPP_RULES = [
    dict(id="strong_growth", indicator="GDP growth",
         cond=lambda v: v > 5,
         en=lambda v: f"Robust growth of {v:.1f}% signals strong economic momentum and investment appeal.",
         fr=lambda v: f"Croissance robuste de {v:.1f}% signalant un dynamisme economique et un attrait pour l'investissement."),
    dict(id="low_inflation", indicator="Inflation",
         cond=lambda v: 0 < v < 3,
         en=lambda v: f"Stable inflation at {v:.1f}% preserves purchasing power and anchors expectations.",
         fr=lambda v: f"Inflation stable a {v:.1f}% preservant le pouvoir d'achat et ancrant les anticipations."),
    dict(id="ca_surplus", indicator="Current account",
         cond=lambda v: v > 3,
         en=lambda v: f"Current account surplus of {v:.1f}% of GDP, building external buffers.",
         fr=lambda v: f"Excedent courant de {v:.1f}% du PIB, constituant des tampons externes."),
    dict(id="low_unemp", indicator="Unemployment",
         cond=lambda v: v < 5,
         en=lambda v: f"Tight labor market at {v:.1f}% unemployment, supporting domestic demand.",
         fr=lambda v: f"Marche du travail tendu a {v:.1f}% de chomage, soutenant la demande interieure."),
    dict(id="electricity_high", indicator="Electricity access",
         cond=lambda v: v > 95,
         en=lambda v: f"Near-universal electricity access ({v:.1f}%) supports productive capacity.",
         fr=lambda v: f"Acces quasi universel a l'electricite ({v:.1f}%) soutenant la capacite productive."),
    dict(id="reserves_strong", indicator="Reserves",
         cond=lambda v: v > 12,
         en=lambda v: f"Reserves cover {v:.1f} months of imports, providing strong external buffer.",
         fr=lambda v: f"Les reserves couvrent {v:.1f} mois d'importations, offrant un tampon externe solide."),
    dict(id="political_stability", indicator="Political stability",
         cond=lambda v: v > 0.5,
         en=lambda v: f"Political stability index at {v:.2f}, supporting policy predictability.",
         fr=lambda v: f"Indice de stabilite politique a {v:.2f}, soutenant la previsibilite des politiques."),
    dict(id="corruption_control", indicator="Control of corruption",
         cond=lambda v: v > 0.5,
         en=lambda v: f"Strong control of corruption ({v:.2f}), improving business climate.",
         fr=lambda v: f"Fort controle de la corruption ({v:.2f}), ameliorant le climat des affaires."),
    dict(id="women_workforce", indicator="Women in workforce",
         cond=lambda v: v > 55,
         en=lambda v: f"Women represent {v:.1f}% of labor force, indicating inclusive labor market.",
         fr=lambda v: f"Les femmes representent {v:.1f}% de la population active, indiquant un marche du travail inclusif."),
    dict(id="low_co2", indicator="CO2 per capita",
         cond=lambda v: v < 2,
         en=lambda v: f"Low emissions at {v:.1f} t CO2/capita, limiting transition risk.",
         fr=lambda v: f"Faibles emissions a {v:.1f} t CO2/hab., limitant le risque de transition."),
]


def generate_outlook(stats):
    """Genere les listes de risques, opportunites et incertitudes a partir des stats."""
    if not stats.get("available"):
        return {"risks": [], "opportunities": [], "uncertainties": []}

    v = stats.get("latest_value")
    ind = stats.get("indicator")
    risks, opps, uncs = [], [], []

    # Risques
    for rule in RISK_RULES:
        if rule["indicator"] == ind and rule["cond"](v):
            risks.append({
                "text_en": rule["en"](v),
                "text_fr": rule["fr"](v),
                "rule_id": rule["id"],
                "value": v,
            })

    # Opportunites
    for rule in OPP_RULES:
        if rule["indicator"] == ind and rule["cond"](v):
            opps.append({
                "text_en": rule["en"](v),
                "text_fr": rule["fr"](v),
                "rule_id": rule["id"],
                "value": v,
            })

    # Incertitudes : donnees anciennes ou manquantes
    if stats.get("change_12m_pct") is None and stats.get("change_3m_pct") is None:
        uncs.append({
            "text_en": "Limited historical data available to assess the trend.",
            "text_fr": "Donnees historiques limitees pour evaluer la tendance.",
        })
    if stats.get("regional_median") is None:
        uncs.append({
            "text_en": "Regional comparison unavailable for this indicator.",
            "text_fr": "Comparaison regionale indisponible pour cet indicateur.",
        })

    return {"risks": risks, "opportunities": opps, "uncertainties": uncs}


# --- API legacy pour compatibilite avec compute_alerts (bandeau d'alertes global) ---
RULES = [
    dict(id="inflation_high", indicator="Inflation", cond=lambda v: v > 10, desc=True,
         en="Inflation above 10 %", fr="Inflation superieure a 10 %"),
    dict(id="recession", indicator="GDP growth", cond=lambda v: v < 0, desc=False,
         en="Negative GDP growth", fr="Croissance du PIB negative"),
    dict(id="reserves_low", indicator="Reserves", cond=lambda v: v < 3, desc=False,
         en="Reserves below 3 months of imports", fr="Reserves sous 3 mois d'importations"),
    dict(id="debt_high", indicator="Gov debt", cond=lambda v: v > 90, desc=True,
         en="Government debt above 90 % of GDP", fr="Dette publique au-dessus de 90 % du PIB"),
    dict(id="ca_deficit", indicator="Current account", cond=lambda v: v < -5, desc=False,
         en="Current account deficit beyond -5 % of GDP", fr="Deficit courant au-dela de -5 % du PIB"),
    dict(id="unemp_high", indicator="Unemployment", cond=lambda v: v > 15, desc=True,
         en="Unemployment above 15 %", fr="Chomage superieur a 15 %"),
    dict(id="electricity_low", indicator="Electricity access", cond=lambda v: v < 50, desc=False,
         en="Access to electricity below 50 %", fr="Acces a l'electricite sous 50 %"),
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
