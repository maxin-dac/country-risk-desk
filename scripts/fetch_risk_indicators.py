"""Fetch additional country-risk indicators from World Bank and merge into the CSV."""
import json
import pathlib
import urllib.request

import pandas as pd

CSV_PATH = pathlib.Path("data/macro_indicators.csv")

NEW_INDICATORS = {
    "Debt service":         ("DT.TDS.DECT.XP.ZS", "External & sovereign", "%", "World Bank (WDI)"),
    "Rule of law":          ("RL.EST.INDEX", "Political & institutional", "index", "World Bank (WGI)"),
    "Regulatory quality":   ("RQ.EST.INDEX", "Political & institutional", "index", "World Bank (WGI)"),
    "Gini":                 ("SI.POV.GINI", "Social & structural", "index", "World Bank (WDI)"),
    "Youth unemployment":   ("SL.UEM.1524.ZS", "Social & structural", "%", "World Bank (WDI)"),
    "Dependency ratio":     ("SP.POP.DPND", "Social & structural", "%", "World Bank (WDI)"),
    "Commodity dependence": ("TX.VAL.FUEL.ZS.UN", "Social & structural", "%", "World Bank (WDI)"),
}


def get_json(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


def country_map():
    cmap = {}
    for page in (1, 2):
        data = get_json(f"https://api.worldbank.org/v2/country?format=json&per_page=300&page={page}")
        rows = data[1] if isinstance(data, list) and len(data) > 1 else []
        if not rows:
            break
        for c in rows:
            if c.get("iso3c") and c.get("id"):
                cmap[c["iso3c"]] = (c.get("region") or {}).get("value", "")
    return cmap


def fetch_series(code):
    out, page = [], 1
    while True:
        url = (f"https://api.worldbank.org/v2/country/all/indicator/{code}"
               f"?date=2000:2024&format=json&per_page=5000&page={page}")
        data = get_json(url)
        rows = data[1] if isinstance(data, list) and len(data) > 1 else []
        if not rows:
            break
        out += rows
        pages = (data[0] or {}).get("pages", 1)
        if page >= pages:
            break
        page += 1
    return out


def main():
    cmap = country_map()
    df_old = pd.read_csv(CSV_PATH)
    keep = df_old[~df_old.indicator.isin(NEW_INDICATORS)]
    new_rows = []
    for name, (code, category, unit, source) in NEW_INDICATORS.items():
        print(f"Fetching {name} ({code})...")
        for rec in fetch_series(code):
            iso3 = (rec.get("countryiso3code") or "").strip()
            val = rec.get("value")
            date = rec.get("date")
            if not iso3 or val is None or not date:
                continue
            d = str(date)
            if len(d) == 4:
                d += "-12-31"
            new_rows.append({
                "country": iso3, "indicator": name, "category": category,
                "date": d, "value": float(val), "unit": unit,
                "region": cmap.get(iso3, ""), "source": source,
            })
    df_new = pd.DataFrame(new_rows)
    df = pd.concat([keep, df_new], ignore_index=True)
    df.to_csv(CSV_PATH, index=False)
    print(f"Done. {len(df_new)} new rows added. Total: {len(df)} rows.")


if __name__ == "__main__":
    main()
