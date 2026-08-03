import pathlib, sys, time
import pandas as pd
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://api.worldbank.org/v2"
INDS = {"GDP growth": ("NY.GDP.MKTP.KD.ZG", "%"),
        "Inflation": ("FP.CPI.TOTL.ZG", "%"),
        "Interest rate": ("FR.INR.LEND", "%")}
HEADERS = {"User-Agent": "pestel-risk-desk/1.0 (portfolio project)"}
DATA = ROOT / "data"
OUT = DATA / "macro_indicators.csv"
CATALOG = DATA / "countries.csv"
session = requests.Session()

def get_json(url, params):
    last = None
    for attempt in range(3):
        try:
            r = session.get(url, params=params, headers=HEADERS, timeout=60)
            r.raise_for_status()
            if "application/json" not in r.headers.get("content-type", ""):
                raise RuntimeError(f"Non-JSON response: {r.text[:120]}")
            return r.json()
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    raise last

def fetch_country_list():
    p = get_json(f"{BASE}/country", {"format": "json", "per_page": 400})
    if not isinstance(p, list) or len(p) < 2 or not isinstance(p[1], list):
        raise RuntimeError(f"Unexpected country list payload: {str(p)[:200]}")
    out = []
    for c in p[1]:
        iso3 = c.get("iso3Code") or c.get("id")
        region = c.get("region") or {}
        if region.get("id") == "NA" or not iso3:
            continue
        out.append({"iso3": iso3,
                "name_en": (c.get("name") or "").strip(),
                "region_en": (region.get("value") or "").strip()})
    if len(out) < 150:
        meta = str(p[0])[:200] if p else ""
        sample = str(p[1][:1])[:300] if p[1] else "empty"
        raise RuntimeError(f"Country list incomplete ({len(out)}) — meta: {meta} — sample: {sample}")
    return out

def load_country_list():
    try:
        countries = fetch_country_list()
        pd.DataFrame(countries).to_csv(CATALOG, index=False)
        return countries
    except Exception as e:
        print(f"[WARN] live country list failed: {e}")
        if CATALOG.exists():
            try:
                df = pd.read_csv(CATALOG, dtype=str).fillna("")
            except Exception:
                df = pd.DataFrame()
            if not df.empty:
                countries = [{"iso3": r.iso3, "name_en": r.name_en, "region_en": r.region_en}
                             for r in df.itertuples()]
                if countries:
                    print(f"[OK] using committed catalog ({len(countries)} countries)")
                    return countries
    raise RuntimeError("No country list available (live fetch failed, no committed catalog)")

def fetch_series(wb_code, wb_ind):
    p = get_json(f"{BASE}/country/{wb_code}/indicator/{wb_ind}",
                 {"format": "json", "date": "2000:2024", "per_page": 300})
    if not isinstance(p, list) or len(p) < 2:
        raise RuntimeError(f"Unexpected payload: {str(p)[:120]}")
    return p[1] or []

def main():
    DATA.mkdir(exist_ok=True)
    countries = load_country_list()
    print(f"{len(countries)} countries in catalog")

    existing = pd.read_csv(OUT) if OUT.exists() else pd.DataFrame()
    done = set(zip(existing.country, existing.indicator)) if not existing.empty else set()
    rows = existing.to_dict("records") if not existing.empty else []
    fails = []
    for c in countries:
        for label, (wb_ind, unit) in INDS.items():
            if (c["iso3"], label) in done:
                continue
            try:
                series = fetch_series(c["iso3"], wb_ind)
            except Exception as e:
                fails.append((c["iso3"], label, str(e)))
                print(f"[FAIL] {c['iso3']} | {label}: {e}")
                continue
            n = 0
            for it in series:
                if it.get("value") is None:
                    continue
                rows.append({"country": c["iso3"], "indicator": label, "category": "Economic",
                             "date": f"{it['date']}-12-31", "value": it["value"], "unit": unit,
                             "region": c["region_en"], "source": "World Bank"})
                n += 1
            print(f"[OK]   {c['iso3']} | {label}: {n} rows")
            time.sleep(0.5)
    df = pd.DataFrame(rows)
    df.to_csv(OUT, index=False)
    print(f"\n{len(df)} rows in {OUT}")
    print(f"{len(fails)} failures — re-run to retry them" if fails else "All series complete")

if __name__ == "__main__":
    main()