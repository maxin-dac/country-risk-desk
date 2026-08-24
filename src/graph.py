import datetime
from typing import Any, Dict, List, Optional, TypedDict
from langgraph.graph import END, StateGraph
from . import config
from .csv_loader import format_stats, get_stats
from .i18n import cname
from .llm import call_llm_json
from .prompts import build_messages
from .validation import validate_report
from .web_search import format_sources, search_web_context

class State(TypedDict, total=False):
    country: str; indicator: str; lang: str
    status: str; error: Optional[str]
    stats: Dict[str, Any]; stats_text: str
    sources: List[Dict]; sources_text: str; search_error: Optional[str]
    draft: Optional[Dict]; validation_error: Optional[str]; retries: int
    usage: Dict[str, int]; final_report: Optional[Dict]

def build_agent(df):
    def n_input(s):
        if s["country"] not in set(df.country.unique()):
            return {"status": "error", "error": f"Country not covered: {s['country']}"}
        if s["indicator"] not in set(df.indicator.unique()):
            return {"status": "error", "error": f"Indicator not covered: {s['indicator']}"}
        return {"status": "ok", "retries": 0}

    def n_csv(s):
        stats = get_stats(df, s["country"], s["indicator"])
        if not stats.get("available"):
            return {"status": "error", "error": "No CSV data for this country/indicator"}
        return {"status": "ok", "stats": stats, "stats_text": format_stats(stats)}

    def n_search(s):
        sources, err = search_web_context(cname(s["country"], "en"), s["indicator"],
                                          config.INDICATOR_HINTS.get(s["indicator"], ""))
        return {"sources": sources, "search_error": err, "sources_text": format_sources(sources)}

    def n_generate(s):
        msgs = build_messages(cname(s["country"], "en"), s["indicator"], s.get("sources_text", ""),
                              s.get("lang", "en"), s.get("validation_error"))
        try:
            draft, usage = call_llm_json(msgs)
            u = dict(s.get("usage") or {})
            for k, v in usage.items():
                u[k] = u.get(k, 0) + v
            return {"draft": draft, "usage": u, "validation_error": None}
        except Exception as e:
            return {"draft": None, "validation_error": f"LLM/JSON error: {e}",
                    "retries": s.get("retries", 0) + 1}

    def n_validate(s):
        if not s.get("draft"):
            return {"status": "invalid", "retries": s.get("retries", 0) + 1,
                    "validation_error": "No draft to validate"}
        ok, errors = validate_report(s["draft"], s.get("sources", []))
        return ({"status": "validated", "validation_error": None} if ok else
                {"status": "invalid", "validation_error": "; ".join(errors),
                 "retries": s.get("retries", 0) + 1})

    def n_finalize(s):
        st_, d = s.get("stats", {}), s.get("draft") or {}
        return {"status": "done", "final_report": {
            "status": "done", "title": f"Country Risk Desk - {s['country']} - {s['indicator']}",
            "country": s["country"], "indicator": s["indicator"], "lang": s.get("lang", "en"),
            "category": st_.get("category", ""), "stats": st_,
            "web_context_available": d.get("web_context_available", False),
            "confidence": d.get("confidence", "low"),
            "context": d.get("context", {"points": []}),
            "outlook": d.get("outlook", {"risks": [], "opportunities": [], "uncertainties": []}),
            "limitations": d.get("limitations", []),
            "sources": s.get("sources", []), "search_error": s.get("search_error"),
            "usage": s.get("usage", {}),
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}}

    def n_fallback(s):
        st_ = s.get("stats", {})
        limits = ["No verified web source available.", "Qualitative context not generated.",
                  "Outlook not generated."]
        if s.get("search_error"):
            limits.append(f"Search: {s['search_error']}")
        if s.get("validation_error"):
            limits.append(f"Validation: {s['validation_error']}")
        return {"status": "done_degraded", "final_report": {
            "status": "done_degraded",
            "title": f"Country Risk Desk - {s.get('country', '?')} - {s.get('indicator', '?')}",
            "country": s.get("country", ""), "indicator": s.get("indicator", ""),
            "lang": s.get("lang", "en"), "category": st_.get("category", ""), "stats": st_,
            "web_context_available": False, "confidence": "low",
            "context": {"points": []},
            "outlook": {"risks": [], "opportunities": [], "uncertainties": ["Insufficient information"]},
            "limitations": limits, "sources": [], "usage": s.get("usage", {}),
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}}

    def n_error(s):
        return {"status": "error",
                "final_report": {"status": "error", "error": s.get("error", "Unknown error")}}

    g = StateGraph(State)
    for name, fn in [("input", n_input), ("csv", n_csv), ("search", n_search),
                     ("generate", n_generate), ("validate", n_validate),
                     ("finalize", n_finalize), ("fallback", n_fallback), ("error", n_error)]:
        g.add_node(name, fn)
    g.set_entry_point("input")
    g.add_conditional_edges("input", lambda s: "err" if s["status"] == "error" else "next",
                            {"err": "error", "next": "csv"})
    g.add_conditional_edges("csv", lambda s: "err" if s["status"] == "error" else "next",
                            {"err": "error", "next": "search"})
    g.add_conditional_edges("search", lambda s: "gen" if s.get("sources") else "fb",
                            {"gen": "generate", "fb": "fallback"})
    g.add_conditional_edges("generate",
                            lambda s: "val" if s.get("draft") is not None
                            else ("gen" if s.get("retries", 0) < 2 else "fb"),
                            {"val": "validate", "gen": "generate", "fb": "fallback"})
    g.add_conditional_edges("validate",
                            lambda s: "fin" if s["status"] == "validated"
                            else ("gen" if s.get("retries", 0) < 2 else "fb"),
                            {"fin": "finalize", "gen": "generate", "fb": "fallback"})
    g.add_edge("finalize", END)
    g.add_edge("fallback", END)
    g.add_edge("error", END)
    return g.compile()