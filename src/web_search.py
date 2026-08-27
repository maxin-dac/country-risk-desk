"""Web search (Tavily / DuckDuckGo) with homogeneous excerpts and freshness-aware ranking."""
import datetime
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
_BOILER_RE = re.compile(
    r"(listed below are items related|list of |related items|see also|external links?"
    r"|retrieved from|last updated|table of contents|cookie|newsletter|sign in|log in)",
    re.I,
)
_JUNK_RE = re.compile(
    r"(col-(xs|sm|md|lg)-\d+|jcr[\w:]+|<[/!]?\w+|class=|href=|&nbsp;|&amp;|\{\{|\}\})",
    re.I,
)


def _domain(url):
    n = urlparse(url).netloc.lower()
    return n[4:] if n.startswith("www.") else n


def _age_days(d):
    if not d:
        return None
    p = pd.to_datetime(d, errors="coerce", utc=True)
    if pd.isna(p):
        return None
    return (pd.Timestamp.now(tz="UTC") - p).days


def _year_hint(text):
    years = [int(y) for y in re.findall(r"(?:19|20)\d{2}", text or "")]
    return max(years) if years else None


def _freshness(it, now_year):
    """Score 0-3. Uses published_date when available, else the most recent year mentioned."""
    age = _age_days(it.get("published_date"))
    if age is not None:
        if age <= 365:
            return 3, age
        if age <= 730:
            return 2, age
        if age <= 1095:
            return 1, age
        return 0, age
    yh = _year_hint((it.get("title") or "") + " " + (it.get("content") or "")[:300])
    if yh is None:
        return 0, None
    gap = now_year - yh
    if gap <= 1:
        return 3, None
    if gap <= 2:
        return 2, None
    if gap <= 3:
        return 1, None
    return 0, None


def _clean_text(text):
    text = (text or "").replace("\r", "")
    text = re.sub(r"[ \t]+", " ", text)
    out = []
    for ln in text.split("\n"):
        ln = ln.strip()
        ln = re.sub(r"^#{1,6}\s*", "", ln)
        ln = re.sub(r"^\d{1,2}[.)]\s+", "", ln)
        low = ln.lower()
        if (not ln or low in _BOILER or _JUNK_RE.search(ln)
                or _BOILER_RE.search(low) or ln.count("|") >= 2):
            continue
        if len(ln) < 25 and not ln.endswith((".", "!", "?")):
            continue
        out.append(ln)
    return re.sub(r"\s{2,}", " ", " ".join(out)).strip()


def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if len(s.strip()) >= 40]


def _is_prose(sent):
    if sent.count("|") >= 2:
        return False
    words = re.findall(r"[A-Za-z]+", sent)
    nums = re.findall(r"\d+(?:[.,]\d+)?", sent)
    if len(words) < 8:
        return False
    if len(nums) * 2 > len(words):
        return False
    return True


def make_excerpt(content, terms, max_chars=560):
    sents = [s for s in _sentences(_clean_text(content)) if _is_prose(s)]
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
def _search_tavily(q, start_date):
    from tavily import TavilyClient
    client = TavilyClient(api_key=config.TAVILY_API_KEY)
    try:
        raw = client.search(query=q, search_depth="advanced", max_results=10,
                            include_domains=config.ALLOWED_SEARCH_DOMAINS,
                            start_date=start_date)
    except TypeError:
        raw = client.search(query=q, search_depth="advanced", max_results=10,
                            include_domains=config.ALLOWED_SEARCH_DOMAINS)
    return [{"url": r.get("url"), "title": r.get("title"), "content": r.get("content"),
             "published_date": r.get("published_date")} for r in (raw.get("results") or [])]


def _search_duckduckgo(q):
    try:
        from ddgs import DDGS
    except ImportError:
        from duckduckgo_search import DDGS
    try:
        res = DDGS().text(q, max_results=12, timelimit="y")
    except TypeError:
        res = DDGS().text(q, max_results=12)
    return [{"url": r.get("href"), "title": r.get("title"), "content": r.get("body"),
             "published_date": None} for r in (res or [])]


def search_web_context(country_en, indicator, hint=""):
    provider = str(getattr(config, "SEARCH_PROVIDER", "tavily")).lower()
    if provider == "tavily" and not config.TAVILY_API_KEY:
        provider = "duckduckgo"

    now = datetime.date.today()
    q = (f"{country_en} {indicator} {hint} official statistics data figures "
         f"IMF World Bank outlook {now.year} {now.year - 1}").strip()
    start_date = (pd.Timestamp.now(tz="UTC") - pd.DateOffset(months=18)).strftime("%Y-%m-%d")

    try:
        items = _search_duckduckgo(q) if provider == "duckduckgo" else _search_tavily(q, start_date)
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
        fres, age = _freshness(it, now.year)
        title = it.get("title") or ""
        yr_bonus = 15 if (str(now.year) in title or str(now.year - 1) in title) else 0
        # Freshness dominates (x100); domain prestige is secondary (x10)
        rank = fres * 100 + TIERS.get(tier_dom, 1) * 10 + yr_bonus
        scored.append((rank, {
            "title": title.strip(), "url": url, "domain": dom,
            "published_date": it.get("published_date"), "age_days": age,
            "content": _clean_text(it.get("content"))[:2000],
            "excerpt": make_excerpt(it.get("content"), terms),
        }))

    # Drop stale sources (older than 3 years, or year hint 4+ years old) when fresher ones remain
    def _stale(x):
        d = x[1]
        if d.get("age_days") is not None:
            return d["age_days"] > 1095
        yh = _year_hint(d["title"] + " " + d["content"][:300])
        return yh is not None and yh <= now.year - 4

    fresh = [x for x in scored if not _stale(x)]
    if len(fresh) >= 2:
        scored = fresh

    scored.sort(key=lambda x: x[0], reverse=True)
    sources = [dict(s, id=f"S{i}") for i, (_, s) in enumerate(scored[:config.MAX_SEARCH_RESULTS], 1)]
    return (sources, None) if sources else ([], "No quality source found in allowed domains")


def format_sources(sources):
    return "\n\n".join(
        f"[{s['id']}] {s['domain']} ({s.get('published_date') or 'date unknown'})\n"
        f"Title: {s['title']}\nURL: {s['url']}\nExcerpt: {s.get('excerpt') or s['content']}"
        for s in sources) or "No web source."
