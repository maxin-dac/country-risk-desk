import pathlib
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
    "Political stability": ("Political stability", "Stabilité politique"),
    "Control of corruption": ("Control of corruption", "Contrôle de la corruption"),

    "CO2 per capita": ("GHG emissions per capita", "Émissions GES par habitant"),
    "Electricity access": ("Access to electricity", "Accès à l'électricité"),
    "Women in workforce": ("Women in labor force", "Femmes dans la population active"),

    "External debt": ("External debt", "Dette externe"),

    "Interest rate": ("Interest rate", "Taux d'interet"),

    "Current account": ("Current account balance", "Solde du compte courant"),
    "Gov debt": ("Government debt", "Dette publique"),
    "Reserves": ("Total reserves", "Réserves totales"),
    "Unemployment": ("Unemployment rate", "Taux de chômage"),

    "Inflation": ("Inflation", "Inflation"),
    "Policy rate": ("Policy rate", "Taux directeur"),
    "GDP growth": ("GDP growth", "Croissance du PIB"),
}

# UI strings -> (en, fr)
STR = {

    "mode": ("Mode", "Mode"),
    "mode_brief": ("Country brief", "Brief pays"),
    "mode_compare": ("Comparison", "Comparaison"),
    "countries_sel": ("Countries (max 12)", "Pays (12 max)"),
    "compare_hint": ("Select at least two countries to compare.", "Sélectionnez au moins deux pays à comparer."),
    "compare_latest": ("Latest values", "Dernières valeurs"),
    "compare_map": ("Positioning: growth vs inflation", "Positionnement : croissance vs inflation"),
    "axis_growth": ("GDP growth (%)", "Croissance PIB (%)"),
    "axis_inflation": ("Inflation (%)", "Inflation (%)"),

    "alerts_title": ("Threshold alerts", "Alertes seuil"),


    "eyebrow": ("Macro-intelligence // Country Risk Desk - Session of", "Macro-intelligence // Country Risk Desk - Session du"),
    "title_a": ("Country Risk", "Risque Pays"),
    "title_b": ("Desk", "Desk"),
    "st_llm": ("Model", "Modèle"),
    "st_search": ("Search", "Recherche"),
    "st_data": ("Data", "Données"),
    "st_mode": ("100% free demo", "Démo 100 % gratuite"),
    "coverage": ("Coverage", "Couverture"),
    "countries_w": ("countries", "pays"),
    "indicators_w": ("indicators", "indicateurs"),
    "official_only": ("official sources", "sources officielles"),
    "params": ("Brief parameters", "Paramètres du brief"),
    "country": ("Country", "Pays"),
    "indicator": ("Macro indicator", "Indicateur macro"),
    "generate": ("Generate brief", "Générer le brief"),
    "cache_note": ("1 brief = 1 search + 1 LLM call · 24h cache · verbatim citations required",
                   "1 brief = 1 recherche + 1 appel LLM · cache 24 h · citations verbatim obligatoires"),
    "searching": ("Fetching sources · calling model · validating citations…",
                  "Recherche de sources · appel du modèle · validation des citations…"),
    "sec_constat": ("Figures - Data (Latest from World Bank)", "Constat chiffré - Données (Les plus récentes de la Banque mondiale)"),
    "sec_context": ("Qualitative context - verified sources", "Contexte qualitatif - sources vérifiées"),
    "sec_risks": ("12-month risks", "Risques à 12 mois"),
    "sec_opps": ("12-month opportunities", "Opportunités à 12 mois"),
    "sec_sources": ("Cited sources", "Sources citées"),
    "sec_limits": ("Limitations", "Limites"),
    "insufficient": ("Insufficient information - no verified source available",
                     "Information insuffisante - aucune source vérifiée disponible"),
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
    "live": ("Run live search", "Lancer la recherche en direct"),
    "live_note": ("Server-side keys - visitors need nothing.",
                  "Clés côté serveur - rien à fournir côté visiteur."),
    "no_keys": ("Server keys missing (Tavily / LLM).",
                "Clés serveur manquantes (Tavily / LLM)."),
    "live_done": ("Live brief - cached 24 h", "Brief en direct - caché 24 h"),
}


def t(key, lang="en"):
    return STR[key][1 if lang == "fr" else 0]

def cname(iso3, lang="en"):
    if iso3 in COUNTRIES:
        return COUNTRIES[iso3][1 if lang == "fr" else 0]
    return _country_names(lang).get(iso3) or _country_names("en").get(iso3, iso3)

def iname(key, lang="en"):
    return INDICATORS[key][1 if lang == "fr" else 0]

_COUNTRY_CACHE = {}

def _country_names(lang="en"):
    global _COUNTRY_CACHE
    if lang in _COUNTRY_CACHE:
        return _COUNTRY_CACHE[lang]
    names = {}
    try:
        from babel import Locale
        import pycountry
        terr = Locale("fr" if lang == "fr" else "en").territories
        for c in pycountry.countries:
            if c.alpha_2 in terr:
                names[c.alpha_3] = terr[c.alpha_2]
    except Exception:
        pass
    import csv
    p = pathlib.Path(__file__).resolve().parent.parent / "data" / "countries.csv"
    try:
        with open(p, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                iso = (row.get("iso3") or "").strip()
                if iso:
                    names.setdefault(iso, (row.get("name_en") or iso).strip())
    except Exception:
        pass
    _COUNTRY_CACHE[lang] = names
    return names
