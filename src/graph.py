"""Orchestrateur deterministe - remplace l'agent LangGraph.
Aucun appel LLM. Generation par regles et extraction brute Tavily."""
import datetime
from . import config
from .csv_loader import get_stats
from .i18n import cname
from .web_search import search_web_context
from .alerts import generate_outlook


def build_report(country, indicator, lang):
    """Genere un brief complet de maniere deterministe.
    Retourne un dict au meme format que l'ancien rapport LLM."""
    from .csv_loader import load_csv
    df = load_csv(config.CSV_PATH)

    # 1. Donnees quantitatives Banque Mondiale
    stats = get_stats(df, country, indicator)
    if not stats.get("available"):
        return {"status": "error", "error": f"No data for {country} / {indicator}"}

    # 2. Recherche web Tavily (extraits bruts, pas de synthese)
    sources, search_error = search_web_context(
        cname(country, "en"),
        indicator,
        config.INDICATOR_HINTS.get(indicator, "")
    )

    # 3. Generation des risques/opportunites par regles
    outlook = generate_outlook(stats)

    # 4. Construction du contexte qualitatif = extraits bruts Tavily
    context_points = []
    for src in sources:
        excerpt = (src.get("excerpt") or src.get("content") or "").strip()
        if excerpt:
            context_points.append({
                "text": excerpt[:400] + ("..." if len(excerpt) > 400 else ""),
                "evidence": [{"source_id": src["id"], "quote": excerpt[:300]}],
            })

    context_points = context_points[:3]

    # 5. Limites automatiques
    limitations = []
    if not sources:
        limitations.append("No verified web source available for qualitative context." if lang == "en"
                           else "Aucune source web verifiee disponible pour le contexte qualitatif.")
    if search_error:
        limitations.append(f"Search: {search_error}")

    return {
        "status": "done",
        "title": f"Country Risk Desk - {country} - {indicator}",
        "country": country,
        "indicator": indicator,
        "lang": lang,
        "category": stats.get("category", ""),
        "stats": stats,
        "web_context_available": bool(sources),
        "confidence": "high" if sources else "low",
        "context": {"points": context_points},
        "outlook": outlook,
        "limitations": limitations,
        "sources": sources,
        "search_error": search_error,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
