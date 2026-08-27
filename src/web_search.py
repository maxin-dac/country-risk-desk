"""Web search with multiple providers (Tavily / DuckDuckGo) and homogeneous excerpts."""
import re
from urllib.parse import urlparse

import pandas as pd

from . import config

TIERS = {"reuters.com": 3, "bloomberg.com": 3, "imf.org": 3, "worldbank.org": 3,
         "oecd.org": 2, "ft.com": 2, "economist.com": 2}

_BOILER = {
    "press release", "read more", "see more", "share", "subscribe", "newsletter",
    "home", "search", "menu", "download", "print", "email", "cookies",
    "privacy policy", "terms of use", "contact us", "about us", "sign in",
}
_JUNK_RE = re.compile(
    r"(col-(xs|sm|md|lg)-\d+|jcr[\w:]+|<[/!]?\w+|class=|href=|&nbsp;|&amp;|\{\{|\}\})",
    re.I,
)


def _domain(url):
    n = urlparse(url).netloc.lower()
    return n[4:] if n.startswith("www.") else n


def _recent(d, days=180):
    if not d:
        return False
    p = pd.to_datetime(d, errors="coerce", utc=True)
    return bool(not pd.isna(p) and (pd.Timestamp.now(tz="UTC") - p).days <= days)


def _clean_text(text):
    """Strip page chrome (CSS classes, nav fragments, boilerplate) from raw content."""
    text = (text or "").replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    out = []
    for ln in text.split("\n"):
        ln = ln.strip()
        ln = re.sub(r"^#{1,6}\s*", "", ln)          # markdown headings
        ln = re.sub(r"^\d{1,2}[.)]\s+", "", ln)     # doc numbering like "11."
        low = ln.lower()
        if not ln or low in _BOILER or _JUNK_RE.search(ln):
            continue
        if len(ln) < 25 and not ln.endswith((".", "!", "?")):
            continue
        out.append(ln)
    return re.sub(r"\s{2,}", " ", " ".join(out)).strip()


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if len(s.strip()) >= 40]


def make_excerpt(content, terms, max_chars=560):
    """Homogeneous excerpt: 1-3 most relevant sentences, original order kept."""
    sents = _sentences(_clean_text(content))
    if not sents:
        return ""

    def score(s):
        low = s.lower()
        return sum(1 for t in terms if t and t in low)

    hit = [s for s in sents if score(s) > 0]
    pick = (hit or sents)[:3]
    excerpt = " ".join(pick)
    if len(excerpt) > max_chars:
        excerpt = excerpt[:max_chars].rsplit(" ", 1)[0].rstrip(",;:") + " ..."
    return excerpt


# ------------------------------------------------------------ providers
def _search_tavily(q):
    from tavily import TavilyClient
    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    try:
        raw = client.search(query=q, search_depth="advanced", max_results=8,
                            include_domains=config.ALLOWED_SEARCH_DOMAINS, days=180)
    except TypeError:
        raw = client.search(query=q, search_depth="advanced", max_results=8,
                            include_domains=config.ALLOWED_SEARCH_DOMAINS)
    return [{"url": r.get("url"), "title": r.get("title"), "content": r.get("content"),
             "published_date": r.get("published_date")} for r in (raw.get("results") or [])]


def _search_duckduckgo(q):
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS
    res = DDGS().text(q, max_results=10)
    return [{"url": r.get("href"), "title": r.get("title"), "content": r.get("body"),
             "published_date": None} for r in (res or [])]


def search_web_context(country_en, indicator, hint=""):
    provider = str(getattr(config, "SEARCH_PROVIDER", "tavily")).lower()
    if provider == "tavily" and not config.TAVILY_API_KEY:
        provider = "duckduckgo"

    q = f"{country_en} {indicator} {hint} official statistics data figures IMF World Bank outlook".strip()

    try:
        items = _search_duckduckgo(q) if provider == "duckduckgo" else _search_tavily(q)
    except Exception as e:
        return [], f"Search error ({provider}): {e}"

    terms = [w.lower() for w in re.split(r"\W+", f"{country_en} {indicator} {hint}") if len(w) > 3]

    scored, seen = [], set()
    for it in items:
        url = it.get("url")
        if not url or url in seen:
            continue
        dom = _domain(url)
        if provider != "tavily" and not any(d == dom or dom.endswith("." + d)
                                            for d in config.ALLOWED_SEARCH_DOMAINS):
            continue
        seen.add(url)
        tier_dom = next((d for d in TIERS if dom == d or dom.endswith("." + d)), None)
        rank = TIERS.get(tier_dom, 1) * 10 + (5 if _recent(it.get("published_date")) else 0)
        scored.append((rank, {
            "title": (it.get("title") or "").strip(), "url": url, "domain": dom,
            "published_date": it.get("published_date"),
            "content": _clean_text(it.get("content"))[:2000],
            "excerpt": make_excerpt(it.get("content"), terms),
        }))

    scored.sort(key=lambda x: x[0], reverse=True)
    sources = [dict(s, id=f"S{i}") for i, (_, s) in enumerate(scored[:config.MAX_SEARCH_RESULTS], 1)]
    return (sources, None) if sources else ([], "No quality source found in allowed domains")


def format_sources(sources):
    return "\n\n".join(
        f"[{s['id']}] {s['domain']} ({s.get('published_date') or 'date unknown'})\n"
        f"Title: {s['title']}\nURL: {s['url']}\nExcerpt: {s.get('excerpt') or s['content']}"
        for s in sources) or "No web source."
