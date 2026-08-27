"""Fetch the remaining country-risk indicators from World Bank (idempotent)."""
import json
import pathlib
import urllib.request

import pandas as pd

CSV_PATH = pathlib.Path("data/macro_indicators.csv")

EXTRAS = {
    "External debt": ("DT.DOD.DECT.GN.ZS", "External & sovereign", "%", "World Bank (WDI)"),
    "Debt service": ("DT.TDS.DECT.XP.ZS", "External & sovereign", "%", "World Bank (WDI)"),
    "Rule of law": ("RL.EST.INDEX", "Political & institutional", "index", "World Bank (WGI)"),
    "Regulatory quality": ("RQ.EST.INDEX", "Political & institutional", "index", "World Bank (WGI)"),
}


def get_json(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


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
    df_old = pd.read_csv(CSV_PATH, dtype={"region": str})
    region_map = dict(zip(df_old.country, df_old.region))
    keep = df_old[~df_old.indicator.isin(EXTRAS)]
    new_rows = []
    for name, (code, category, unit, source) in EXTRAS.items():
        print(f"Fetching {name} ({code})...")
        try:
            rows = fetch_series(code)
        except Exception as e:
            print(f"  ! error: {e}")
            continue
        n = 0
        for rec in rows:
            iso3 = (rec.get("countryiso3code") or "").strip()
            val = rec.get("value")
            date = rec.get("date")
            if not iso3 or val is None or not date:
                continue
            d = str(date)
            if len(d) == 4:
                d += "-12-31"
            new_rows.append({"country": iso3, "indicator": name, "category": category,
                             "date": d, "value": float(val), "unit": unit,
                             "region": region_map.get(iso3, ""), "source": source})
            n += 1
        print(f"  -> {n} rows")
    df_new = pd.DataFrame(new_rows)
    df = pd.concat([keep, df_new], ignore_index=True) if len(df_new) else keep
    df.to_csv(CSV_PATH, index=False)
    print(f"CSV updated: {len(df)} rows (+{len(df_new)})")
    for name in EXTRAS:
        print(f"  - {name}: {df.loc[df.indicator == name, 'country'].nunique()} countries")


if __name__ == "__main__":
    main()
