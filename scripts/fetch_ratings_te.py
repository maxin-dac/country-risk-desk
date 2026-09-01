# -*- coding: utf-8 -*-
"""Fetch notations souveraines depuis Trading Economics (source publique fiable)."""
import csv
import datetime
import pathlib
import re
import sys
import requests
from bs4 import BeautifulSoup

URL = "https://tradingeconomics.com/country-list/rating"
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "sovereign_ratings.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def fetch_trading_economics():
    """Parse Trading Economics (S&P ratings publiques)."""
    try:
        r = requests.get(URL, headers=HEADERS, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"[!] Fetch Trading Economics echoue: {e}")
        return None
    
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table")
    if not table:
        print("[!] Table introuvable")
        return None
    
    rows = []
    for tr in table.find_all("tr")[1:]:
        cols = tr.find_all(["td", "th"])
        if len(cols) < 3:
            continue
        
        country = cols[0].get_text(strip=True)
        rating = cols[1].get_text(strip=True)
        
        if country and rating and re.match(r"^[A-Z]", rating):
            rows.append({
                "country": country,
                "sp": rating,
                "moodys": "",
                "fitch": "",
            })
    
    return rows if rows else None

def main():
    print(f"[>] Fetch: {URL}")
    rows = fetch_trading_economics()
    
    if not rows:
        print("[X] Fetch echoue - utilisez les notations manuelles")
        sys.exit(1)
    
    # TODO: ajouter mapping ISO3 + Moody's/Fitch
    print(f"[OK] {len(rows)} notations S&P recuperees")
    print("[!] Mapping ISO3 et Moody's/Fitch a completer manuellement")

if __name__ == "__main__":
    main()
