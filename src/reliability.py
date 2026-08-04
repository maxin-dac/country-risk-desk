"""Score de fiabilite par source — deterministe et explicable."""
from datetime import datetime, timezone
from urllib.parse import urlparse

INSTITUTIONAL = ("imf.org", "worldbank.org")
PREMIUM_PRESS = ("reuters.com", "bloomberg.com", "ft.com")


def domain_of(src):
    try:
        host = urlparse(src.get("url") or "").netloc.lower()
    except Exception:
        host = ""
    if host.startswith("www."):
        host = host[4:]
    return host or (src.get("domain") or "").lower()


def _in(host, domains):
    return any(host == d or host.endswith("." + d) for d in domains)


def days_since(src):
    for key in ("published_date", "date", "published", "published_at"):
        value = src.get(key)
        if not value:
            continue
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return max(0, (datetime.now(timezone.utc) - dt).days)
        except Exception:
            continue
    return None


def quote_counts(report):
    counts = {}
    for key in ("context", "risks", "opportunities", "uncertainties"):
        for item in report.get(key) or []:
            if isinstance(item, dict):
                sid = item.get("src") or item.get("source_id")
                if sid:
                    counts[sid] = counts.get(sid, 0) + 1
    return counts


def source_score(src, quote_count=0):
    host = domain_of(src)
    authority = 40 if _in(host, INSTITUTIONAL) else 35 if _in(host, PREMIUM_PRESS) else 20
    age = days_since(src)
    recency = 30 if age is not None and age <= 90 else 20 if age is not None and age <= 365 else 10
    grounding = 30 if quote_count >= 2 else 15 if quote_count == 1 else 0
    return min(100, authority + recency + grounding)


def score_band(score):
    return "high" if score >= 75 else "good" if score >= 50 else "limited"
