# ISO3 -> (en, fr, world_bank_code, region)
COUNTRIES = {
    "VNM": ("Vietnam", "Vietnam", "VN", "East Asia & Pacific"),
    "BRA": ("Brazil", "Brésil", "BR", "Latin America & Caribbean"),
    "EGY": ("Egypt", "Égypte", "EG", "Middle East & North Africa"),
    "IND": ("India", "Inde", "IN", "South Asia"),
    "IDN": ("Indonesia", "Indonésie", "ID", "East Asia & Pacific"),
    "MEX": ("Mexico", "Mexique", "MX", "Latin America & Caribbean"),
    "TUR": ("Türkiye", "Turquie", "TR", "Europe & Central Asia"),
    "ZAF": ("South Africa", "Afrique du Sud", "ZA", "Sub-Saharan Africa"),
    "NGA": ("Nigeria", "Nigéria", "NG", "Sub-Saharan Africa"),
    "ARG": ("Argentina", "Argentine", "AR", "Latin America & Caribbean"),
    "CHL": ("Chile", "Chili", "CL", "Latin America & Caribbean"),
    "COL": ("Colombia", "Colombie", "CO", "Latin America & Caribbean"),
    "PER": ("Peru", "Pérou", "PE", "Latin America & Caribbean"),
    "POL": ("Poland", "Pologne", "PL", "Europe & Central Asia"),
    "THA": ("Thailand", "Thaïlande", "TH", "East Asia & Pacific"),
    "MYS": ("Malaysia", "Malaisie", "MY", "East Asia & Pacific"),
    "PHL": ("Philippines", "Philippines", "PH", "East Asia & Pacific"),
    "KEN": ("Kenya", "Kenya", "KE", "Sub-Saharan Africa"),
    "MAR": ("Morocco", "Maroc", "MA", "Middle East & North Africa"),
    "SAU": ("Saudi Arabia", "Arabie saoudite", "SA", "Middle East & North Africa"),
}

# CSV key -> (en, fr)
INDICATORS = {
    "Inflation": ("Inflation", "Inflation"),
    "Policy rate": ("Policy rate", "Taux directeur"),
    "GDP growth": ("GDP growth", "Croissance du PIB"),
}

# UI strings -> (en, fr)
STR = {
    "eyebrow": ("Macro-intelligence // PESTEL — Session of", "Macro-intelligence // PESTEL — Session du"),
    "title_a": ("Country Risk", "Risque Pays"),
    "title_b": ("Desk", "Desk"),
    "st_llm": ("Model", "Modèle"),
    "st_search": ("Search", "Recherche"),
    "st_data": ("Data", "Données"),
    "st_mode": ("100% free demo", "Démo 100 % gratuite"),
    "coverage": ("Coverage", "Couverture"),
    "countries_w": ("countries", "pays"),
    "indicators_w": ("indicators", "indicateurs"),
    "official_only": ("official sources only", "sources officielles uniquement"),
    "params": ("Brief parameters", "Paramètres du brief"),
    "country": ("Country", "Pays"),
    "indicator": ("Macro indicator", "Indicateur macro"),
    "generate": ("Generate brief", "Générer le brief"),
    "cache_note": ("1 brief = 1 search + 1 LLM call · 24h cache · verbatim citations required",
                   "1 brief = 1 recherche + 1 appel LLM · cache 24 h · citations verbatim obligatoires"),
    "searching": ("Fetching sources · calling model · validating citations…",
                  "Recherche de sources · appel du modèle · validation des citations…"),
    "sec_constat": ("Figures — CSV data (World Bank)", "Constat chiffré — données CSV (Banque mondiale)"),
    "sec_context": ("Qualitative context — verified sources", "Contexte qualitatif — sources vérifiées"),
    "sec_risks": ("12-month risks", "Risques à 12 mois"),
    "sec_opps": ("12-month opportunities", "Opportunités à 12 mois"),
    "sec_sources": ("Cited sources", "Sources citées"),
    "sec_limits": ("Limitations", "Limites"),
    "insufficient": ("Insufficient information — no verified source available",
                     "Information insuffisante — aucune source vérifiée disponible"),
    "no_sources": ("No verified web source", "Aucune source web vérifiée"),
    "export": ("Export brief (PDF)", "Exporter le brief (PDF)"),
    "pdf_fail": ("PDF export unavailable", "Export PDF indisponible"),
    "d3": ("over 3 months", "sur 3 mois"),
    "d12": ("over 12 months", "sur 12 mois"),
    "reg_median": ("Regional median", "Médiane régionale"),
    "pos_above": ("above the median", "au-dessus de la médiane"),
    "pos_below": ("below the median", "en dessous de la médiane"),
    "pos_near": ("near the median", "proche de la médiane"),
    "confidence": ("Confidence", "Confiance"),
    "generated": ("Generated on", "Généré le"),
    "fact_rule": ("No claim without verified evidence", "Aucune affirmation sans preuve vérifiée"),
    "not_advice": ("Not investment advice", "Ne constitue pas un conseil en investissement"),
    "uncertainties": ("Uncertainties", "Incertitudes"),
    "error": ("Error", "Erreur"),
    "library_note": ("Pre-computed briefs · no key · no wait · auto-refreshed monthly",
                     "Briefs pré-calculés · sans clé · sans attente · rafraîchis chaque mois"),
}


def t(key, lang="en"):
    return STR[key][1 if lang == "fr" else 0]

def cname(iso3, lang="en"):
    return COUNTRIES[iso3][1 if lang == "fr" else 0]

def iname(key, lang="en"):
    return INDICATORS[key][1 if lang == "fr" else 0]