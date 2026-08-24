from urllib.parse import urlparse
import pandas as pd
from tavily import TavilyClient
from . import config

TIERS = {"reuters.com": 3, "bloomberg.com": 3, "imf.org": 3, "worldbank.org": 3,
         "oecd.org": 2, "ft.com": 2, "economist.com": 2}

def _domain(url):
    n = urlparse(url).netloc.lower()
    return n[4:] if n.startswith("www.") else n

def _recent(d, days=180):
    if not d:
        return False
    p = pd.to_datetime(d, errors="coerce", utc=True)
    return bool(not pd.isna(p) and (pd.Timestamp.now(tz="UTC") - p).days <= days)

def search_web_context(country_en, indicator, hint=""):
    if not config.TAVILY_API_KEY:
        return [], "Missing Tavily API key"
    q = f"{country_en} {indicator} {hint} macroeconomic analysis latest official data outlook".strip()
    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    try:
        try:
            raw = client.search(query=q, search_depth="advanced", max_results=8,
                                include_domains=config.ALLOWED_SEARCH_DOMAINS, days=180)
        except TypeError:
            raw = client.search(query=q, search_depth="advanced", max_results=8,
                                include_domains=config.ALLOWED_SEARCH_DOMAINS)
    except Exception as e:
        return [], f"Search error: {e}"
    scored, seen = [], set()
    for it in (raw.get("results") or []):
        url = it.get("url")
        if not url or url in seen:
            continue
        dom = _domain(url)
        matching_dom = next((d for d in config.ALLOWED_SEARCH_DOMAINS if d in dom), None)
        if not matching_dom:
            continue
        seen.add(url)
        tier_dom = next((d for d in TIERS if dom == d or dom.endswith("." + d)), None)
        rank = TIERS.get(tier_dom, 1) * 10 + (5 if _recent(it.get("published_date")) else 0) + float(it.get("score") or 0)
        scored.append((rank, {"title": it.get("title", ""), "url": url, "domain": dom,
                              "published_date": it.get("published_date"),
                              "content": (it.get("content") or "")[:2000]}))
    scored.sort(key=lambda x: x[0], reverse=True)
    sources = [dict(s, id=f"S{i}") for i, (_, s) in enumerate(scored[:config.MAX_SEARCH_RESULTS], 1)]
    return (sources, None) if sources else ([], "No quality source found in allowed domains")

def format_sources(sources):
    return "\n\n".join(
        f"[{s['id']}] {s['domain']} ({s.get('published_date') or 'date unknown'})\n"
        f"Title: {s['title']}\nURL: {s['url']}\nExcerpt: {s['content']}"
        for s in sources) or "No web source."