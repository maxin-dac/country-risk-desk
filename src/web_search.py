# -*- coding: utf-8 -*-
"""Recherche web contextuelle multi-sources pour Country Risk Desk.
Sources :
  1. DuckDuckGo (requetes ciblees, extraction robuste)
  2. FMI / Banque Mondiale (pages de donnees officielles)
  3. Presse economique reconnue
"""
import datetime
import re
from urllib.parse import urlparse
from typing import List, Dict, Optional, Tuple
import pandas as pd


# Domaines de confiance par tiers
TIER_3 = [  # Institutions internationales
    "imf.org", "worldbank.org", "oecd.org", "ecb.europa.eu", "bis.org",
    "unctad.org", "ilo.org", "afdb.org", "adb.org"
]
TIER_2 = [  # Presse economique
    "reuters.com", "bloomberg.com", "ft.com", "economist.com",
    "wsj.com", "lemonde.fr", "lesechos.fr", "latribune.fr",
    "medias24.com", "lveco.com", "agenceecofin.com"
]
TIER_1 = [  # Autres sources fiables
    "countryeconomy.com", "tradingeconomics.com", "ceicdata.com"
]

ALL_TRUSTED = TIER_3 + TIER_2 + TIER_1


def _domain(url: str) -> str:
    try:
        n = urlparse(url).netloc.lower()
        return n[4:] if n.startswith("www.") else n
    except Exception:
        return ""


def _clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_ddg_results(html: str) -> List[Dict]:
    results = []
    url_pattern = r'<a[^>]+class="result__url"[^>]+href="([^"]+)"[^>]*>([^<]+)</a>'
    snip_pattern = r'<a[^>]+class="result__snippet"[^>]+href="([^"]+)"[^>]*>(.*?)</a>'
    urls = re.findall(url_pattern, html, re.I)
    snippets = re.findall(snip_pattern, html, re.I)
    for i, (url, domain) in enumerate(urls):
        if i < len(snippets):
            _, snippet_html = snippets[i]
            snippet = _clean_html(snippet_html)
            if url.startswith("//"):
                url = "https:" + url
            elif not url.startswith("http"):
                continue
            results.append({"url": url, "title": domain.strip(),
                            "content": snippet, "published_date": None})
    if not results:
        pattern = (r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>'
                   r'.*?<div[^>]+class="result__snippet"[^>]*>(.*?)</div>')
        for url, title_html, snippet_html in re.findall(pattern, html, re.I | re.S)[:10]:
            title = _clean_html(title_html)
            snippet = _clean_html(snippet_html)
            if len(snippet) > 50:
                results.append({"url": url, "title": title,
                                "content": snippet, "published_date": None})
    return results


def _search_ddg(query: str, max_results: int = 12) -> List[Dict]:
    import requests
    try:
        r = requests.post(
            "https://html.duckduckgo.com/html/",
            data={"q": query},
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
            timeout=15,
        )
        if r.status_code == 200:
            return _extract_ddg_results(r.text)[:max_results]
    except Exception as e:
        print(f"[DDG] Erreur: {e}")
    # Fallback lite
    try:
        import requests
        r = requests.get("https://lite.duckduckgo.com/lite/",
                         params={"q": query},
                         headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                         timeout=15)
        if r.status_code == 200:
            blocks = re.split(r'<a\s+rel="nofollow"\s+href="([^"]+)"[^>]*>([^<]+)</a>', r.text)
            items = []
            for i in range(1, len(blocks) - 1, 4):
                url, title = blocks[i], re.sub(r"<[^>]+>", "", blocks[i + 1]).strip()
                snip = re.sub(r"<[^>]+>", "", blocks[i + 2]).strip()
                if url.startswith("//"):
                    url = "https:" + url
                if url.startswith("http") and len(snip) > 30:
                    items.append({"url": url, "title": title,
                                  "content": snip, "published_date": None})
            return items[:max_results]
    except Exception as e:
        print(f"[DDG lite] Erreur: {e}")
    return []


def _search_institutional(country_en: str, indicator: str) -> List[Dict]:
    results = []
    year = datetime.date.today().year
    imf_queries = [
        f"site:imf.org {country_en} Article IV {year}",
        f"site:imf.org {country_en} {indicator} outlook",
        f"site:imf.org {country_en} economic survey",
    ]
    for q in imf_queries:
        try:
            for it in _search_ddg(q, max_results=3):
                if "imf.org" in it.get("url", ""):
                    results.append(it)
        except Exception:
            pass
    wb_queries = [
        f"site:worldbank.org {country_en} overview {year}",
        f"site:worldbank.org {country_en} {indicator}",
        f"site:worldbank.org {country_en} economic update",
    ]
    for q in wb_queries:
        try:
            for it in _search_ddg(q, max_results=3):
                if "worldbank.org" in it.get("url", ""):
                    results.append(it)
        except Exception:
            pass
    return results


def _build_queries(country_en: str, indicator: str, hint: str = "") -> List[str]:
    year = datetime.date.today().year
    terms = [country_en, indicator]
    if hint:
        terms.append(hint)
    base = " ".join(f'"{t}"' if " " in t else t for t in terms)
    return [
        f'({base}) (site:imf.org OR site:worldbank.org OR site:oecd.org) {year}',
        f'({base}) (outlook OR forecast OR risk) {year} OR {year - 1}',
        f'"{country_en}" economic analysis {indicator} {year}',
        f'"{country_en}" {indicator} statistics data figures',
    ]


def _age_days(d: Optional[str]) -> Optional[int]:
    if not d:
        return None
    try:
        p = pd.to_datetime(d, errors="coerce", utc=True)
        if pd.isna(p):
            return None
        return (pd.Timestamp.now(tz="UTC") - p).days
    except Exception:
        return None


def _year_hint(text: str) -> Optional[int]:
    years = [int(y) for y in re.findall(r"(?:19|20)\d{2}", text or "")]
    return max(years) if years else None


def _freshness_score(item: Dict, now_year: int) -> Tuple[int, Optional[int]]:
    age = _age_days(item.get("published_date"))
    if age is not None:
        if age <= 365: return 3, age
        if age <= 730: return 2, age
        if age <= 1095: return 1, age
        return 0, age
    yh = _year_hint((item.get("title") or "") + " " + (item.get("content") or "")[:300])
    if yh is None:
        return 0, None
    gap = now_year - yh
    if gap <= 1: return 3, None
    if gap <= 2: return 2, None
    if gap <= 3: return 1, None
    return 0, None


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if len(s.strip()) >= 40]


def _is_prose(sent: str) -> bool:
    if sent.count("|") >= 2:
        return False
    words = re.findall(r"[A-Za-z]+", sent)
    nums = re.findall(r"\d+(?:[.,]\d+)?", sent)
    if len(words) < 8:
        return False
    if len(nums) * 2 > len(words):
        return False
    return True


def make_excerpt(content: str, terms: List[str], max_chars: int = 560) -> str:
    sents = [s for s in _sentences(content) if _is_prose(s)]
    if not sents:
        return ""
    def score(s):
        low = s.lower()
        return sum(1 for t in terms if t and t in low)
    hit = [s for s in sents if score(s) > 0]
    pick = (hit or sents)[:3]
    excerpt = " ".join(pick)
    if len(excerpt) > max_chars:
        excerpt = excerpt[:max_chars].rsplit(" ", 1)[0].rstrip(",;:") + "..."
    return excerpt


def search_web_context(country_en: str, indicator: str, hint: str = "") -> Tuple[List[Dict], Optional[str]]:
    now = datetime.date.today()
    institutional = _search_institutional(country_en, indicator)
    queries = _build_queries(country_en, indicator, hint)
    raw_items = []
    for q in queries:
        raw_items.extend(_search_ddg(q, max_results=8))
    all_items = institutional + raw_items
    seen, unique_items = set(), []
    for it in all_items:
        url = it.get("url")
        if url and url not in seen:
            seen.add(url)
            unique_items.append(it)
    if not unique_items:
        return [], "No web source found"
    terms = [w.lower() for w in re.split(r"\W+", f"{country_en} {indicator} {hint}") if len(w) > 3]
    scored = []
    for it in unique_items:
        url = it.get("url")
        dom = _domain(url)
        if not any(d == dom or dom.endswith("." + d) for d in ALL_TRUSTED):
            continue
        fres, age = _freshness_score(it, now.year)
        if any(d == dom or dom.endswith("." + d) for d in TIER_3):
            tier_score = 30
        elif any(d == dom or dom.endswith("." + d) for d in TIER_2):
            tier_score = 20
        else:
            tier_score = 10
        title = it.get("title") or ""
        yr_bonus = 15 if (str(now.year) in title or str(now.year - 1) in title) else 0
        rank = fres * 100 + tier_score + yr_bonus
        scored.append((rank, {
            "title": title.strip(), "url": url, "domain": dom,
            "published_date": it.get("published_date"), "age_days": age,
            "content": it.get("content", "")[:2000],
            "excerpt": make_excerpt(it.get("content", ""), terms),
        }))
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
    sources = [dict(s, id=f"S{i}") for i, (_, s) in enumerate(scored[:6], 1)]
    return (sources, None) if sources else ([], "No quality source found")


def format_sources(sources: List[Dict]) -> str:
    if not sources:
        return "No web source."
    return "\n\n".join(
        f"[{s['id']}] {s['domain']} ({s.get('published_date') or 'date unknown'})\n"
        f"Title: {s['title']}\nURL: {s['url']}\n"
        f"Excerpt: {s.get('excerpt') or s['content']}"
        for s in sources
    )
