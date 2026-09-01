"""Notation souveraine - proxy deterministe + sources officielles + echo web.

Proxy : 6 drivers documentes (ancres publiques), projection echelle S&P.
Officiel : data/sovereign_ratings.csv (scripts/fetch_ratings.py, CC BY-SA).
Live : extraction heuristique DuckDuckGo, sans cle.
"""
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "sovereign_ratings.csv"

NOTCHES = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-",
           "BB+", "BB", "BB-", "B+", "B", "B-", "CCC+", "CCC", "CCC-", "CC", "C", "D"]
MOODY_EQ = {"AAA": "Aaa", "AA+": "Aa1", "AA": "Aa2", "AA-": "Aa3", "A+": "A1",
            "A": "A2", "A-": "A3", "BBB+": "Baa1", "BBB": "Baa2", "BBB-": "Baa3",
            "BB+": "Ba1", "BB": "Ba2", "BB-": "Ba3", "B+": "B1", "B": "B2",
            "B-": "B3", "CCC+": "Caa1", "CCC": "Caa2", "CCC-": "Caa3",
            "CC": "Ca", "C": "C", "D": "C"}

WEIGHTS = {"Gen gov debt": .25, "Fiscal balance": .15, "Reserves": .20,
           "Inflation": .15, "GDP growth": .10, "Political stability": .15}


def _band(v, bands):
    for mx, sc in bands:
        if v <= mx:
            return sc
    return 100


def _stress(key, v):
    if key == "Gen gov debt":
        return _band(v, [(40, 0), (60, 20), (80, 40), (100, 60), (130, 80), (1e9, 100)])
    if key == "Fiscal balance":
        return _band(-v, [(-2, 0), (0, 20), (2, 40), (4, 60), (6, 80), (1e9, 100)])
    if key == "Reserves":
        return _band(-v, [(-8, 0), (-6, 15), (-4.5, 30), (-3, 55), (-2, 75), (1e9, 100)])
    if key == "Inflation":
        return _band(abs(v), [(3, 0), (5, 20), (8, 40), (12, 60), (25, 80), (1e9, 100)])
    if key == "GDP growth":
        return _band(-v, [(-4, 0), (-2, 15), (0, 35), (1, 55), (3, 75), (1e9, 100)])
    if key == "Political stability":
        return _band(-v, [(-1, 0), (0, 20), (0.5, 40), (1, 60), (1.5, 80), (1e9, 100)])
    return 50


def _latest(df, iso, ind):
    sub = df[(df["country"] == iso) & (df["indicator"] == ind)]
    if sub.empty:
        return None
    vc = "value" if "value" in sub.columns else "latest_value"
    dc = "date" if "date" in sub.columns else "latest_date"
    sub = sub.dropna(subset=[vc]).sort_values(dc)
    return float(sub[vc].iloc[-1]) if not sub.empty else None


def proxy_rating(df, iso):
    drivers, acc, wsum = [], 0.0, 0.0
    for key, w in WEIGHTS.items():
        v = _latest(df, iso, key)
        if v is None:
            continue
        s = _stress(key, v)
        drivers.append({"key": key, "value": round(v, 2), "stress": s, "weight": w})
        acc += s * w
        wsum += w
    if wsum < 0.4:
        return None
    composite = acc / wsum
    idx = min(len(NOTCHES) - 1, round(composite / 100 * (len(NOTCHES) - 1)))
    letter = NOTCHES[idx]
    return {"letter": letter, "moody": MOODY_EQ[letter],
            "composite": round(composite, 1),
            "coverage": len(drivers), "drivers": drivers}


def official_rating(iso):
    if not DATA.exists():
        return None
    try:
        with open(DATA, encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r.get("iso") == iso:
                    return r
    except Exception:
        return None


_NOTCH = r"\b(?:AAA|AA[+-]|AA|A[+-]|A|BBB[+-]|BBB|BB[+-]|BB|B[+-]|B|CCC[+-]|CCC|CC|SD|C|D)\b"
_MOODY = r"\b(?:Aaa|Aa[123]|A[123]|Baa[123]|Ba[123]|B[123]|Caa[123]|Ca|C)\b"


def live_ratings(country_name, timeout=8):
    """Echo web des notations via DuckDuckGo (sans cle, heuristique)."""
    import requests
    q = f'"{country_name}" sovereign credit rating S&P Moody\'s Fitch'
    try:
        r = requests.post("https://html.duckduckgo.com/html/", data={"q": q},
                          headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                          timeout=timeout)
        txt = r.text
    except Exception:
        return []
    out = []
    for sn in re.findall(r'result__snippet[^>]*>(.*?)</', txt, re.S):
        clean = re.sub(r"<[^>]+>", "", sn)
        for agency, alt in (("S&P", _NOTCH), ("Fitch", _NOTCH), ("Moody", _MOODY)):
            i = clean.find(agency)
            if i == -1:
                continue
            m = re.search(alt, clean[i:i + 60])
            if m:
                out.append({"agency": agency if agency != "Moody" else "Moody's",
                            "letter": m.group(0)})
    seen, uniq = set(), []
    for o in out:
        if o["agency"] not in seen:
            seen.add(o["agency"])
            uniq.append(o)
    return uniq[:3]


def country_rating(df, iso):
    return {"proxy": proxy_rating(df, iso),
            "official": official_rating(iso), "live": []}