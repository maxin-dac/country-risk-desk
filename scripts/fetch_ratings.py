# -*- coding: utf-8 -*-
"""Rafraichit data/sovereign_ratings.csv (S&P / Moody's / Fitch).
Source : Wikipedia + repli gracieux si fetch echoue.
"""
import csv
import datetime
import pathlib
import re
import sys

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERREUR: pip install requests beautifulsoup4")
    sys.exit(1)

URL = "https://en.wikipedia.org/wiki/List_of_countries_by_credit_rating"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "sovereign_ratings.csv"
FALLBACK = pathlib.Path(__file__).resolve().parent / "ratings_fallback.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def _parse_wikipedia():
    """Parse la page Wikipedia des notations souveraines."""
    try:
        r = requests.get(URL, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[!] Fetch Wikipedia echoue: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", {"class": "wikitable"})
    if not table:
        print("[!] Table des notations introuvable")
        return None

    rows = []
    for tr in table.find_all("tr")[1:]:
        cols = tr.find_all(["td", "th"])
        if len(cols) < 4:
            continue

        country = cols[0].get_text(strip=True)
        if not country or country in ["Country", "Nation"]:
            continue

        sp, moodys, fitch = "", "", ""
        for col in cols[1:]:
            text = col.get_text(strip=True)
            if "S&P" in text or "Standard" in text:
                sp = text.split(":")[-1].strip() if ":" in text else text
            elif "Moody" in text:
                moodys = text.split(":")[-1].strip() if ":" in text else text
            elif "Fitch" in text:
                fitch = text.split(":")[-1].strip() if ":" in text else text

        if sp or moodys or fitch:
            rows.append({
                "country": country,
                "sp": sp,
                "moodys": moodys,
                "fitch": fitch,
            })

    return rows if rows else None


def _load_fallback():
    """Charge le fichier de repli si le fetch echoue."""
    if not FALLBACK.exists():
        return None
    try:
        with open(FALLBACK, encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception:
        return None


def _iso_from_name(name):
    """Tente de trouver le code ISO3 depuis le nom du pays."""
    try:
        import pycountry
        matches = pycountry.countries.search_fuzzy(name)
        return matches[0].alpha_3 if matches else None
    except Exception:
        return None


def main():
    print(f"[>] Fetch: {URL}")
    rows = _parse_wikipedia()

    if not rows:
        print("[!] Utilisation du fichier de repli")
        rows = _load_fallback()

    if not rows:
        print("[X] Aucune donnee disponible")
        sys.exit(1)

    enriched = []
    for r in rows:
        iso = _iso_from_name(r["country"])
        if iso:
            r["iso"] = iso
            r["updated"] = datetime.date.today().isoformat()
            enriched.append(r)

    if not enriched:
        print("[X] Aucun pays avec code ISO trouve")
        sys.exit(1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["iso", "country", "sp", "moodys", "fitch", "updated"])
        writer.writeheader()
        writer.writerows(enriched)

    print(f"[OK] {len(enriched)} notations souveraines -> {OUT}")


if __name__ == "__main__":
    main()
