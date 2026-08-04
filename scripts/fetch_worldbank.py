import pathlib, time
import pandas as pd
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
BASE = "https://api.worldbank.org/v2"
INDS = {
        "External debt": ("DT.DOD.DECT.GN.ZS", "% GNI"),
"GDP growth": ("NY.GDP.MKTP.KD.ZG", "%"),
        "Inflation": ("FP.CPI.TOTL.ZG", "%"),
        "Interest rate": ("FR.INR.LEND", "%"),
        "Current account": ("BN.CAB.XOKA.GD.ZS", "% GDP"),
        "Gov debt": ("GC.DOD.TOTL.GD.ZS", "% GDP"),
        "Reserves": ("FI.RES.TOTL.MO", "months"),
        "Unemployment": ("SL.UEM.TOTL.ZS", "%")}
HEADERS = {"User-Agent": "country-risk-desk/1.2 (portfolio project)"}
DATA = ROOT / "data"
OUT = DATA / "macro_indicators.csv"
CATALOG = DATA / "countries.csv"
session = requests.Session()

def get_json(url, params):
    last = None
    for attempt in range(3):
        try:
            r = session.get(url, params=params, headers=HEADERS, timeout=90)
            r.raise_for_status()
            if "application/json" not in r.headers.get("content-type", ""):
                raise RuntimeError(f"Non-JSON response: {r.text[:120]}")
            return r.json()
        except Exception as e:
            last = e
            time.sleep(3 * (attempt + 1))
    if last is not None:
        raise last
    raise RuntimeError("get_json failed")

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
        raise RuntimeError(f"Country list incomplete ({len(out)}) — meta: {str(p[0])[:200]}")
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
    raise RuntimeError("No country list available")

def fetch_all_series(wb_ind):
    rows, page = [], 1
    while True:
        p = get_json(f"{BASE}/country/all/indicator/{wb_ind}",
                     {"format": "json", "date": "2000:2024", "per_page": 1000, "page": page})
        if not isinstance(p, list) or len(p) < 2:
            raise RuntimeError(f"Unexpected payload: {str(p)[:120]}")
        rows.extend(p[1] or [])
        pages = int((p[0] or {}).get("pages", 1))
        print(f"    page {page}/{pages}")
        if page >= pages:
            break
        page += 1
        time.sleep(1)
    return rows

def main():
    DATA.mkdir(exist_ok=True)
    countries = load_country_list()
    valid = {c["iso3"]: c for c in countries}
    print(f"{len(countries)} countries in catalog")

    existing = pd.read_csv(OUT) if OUT.exists() else pd.DataFrame()
    done = set(zip(existing.country, existing.indicator)) if not existing.empty else set()
    rows = existing.to_dict("records") if not existing.empty else []
    print(f"[INFO] {len(done)} country/indicator pairs already in CSV")
    fails = []
    for label, (wb_ind, unit) in INDS.items():
        missing = [iso for iso in valid if (iso, label) not in done]
        if not missing:
            print(f"[SKIP] {label}: all countries already fetched")
            continue
        try:
            series = fetch_all_series(wb_ind)
        except Exception as e:
            fails.append(label)
            print(f"[FAIL] {label}: {e}")
            continue
        per = {}
        for it in series:
            iso = it.get("countryiso3code") or (it.get("country") or {}).get("id")
            if iso in missing and it.get("value") is not None:
                per.setdefault(iso, []).append(it)
        matched = sum(len(v) for v in per.values())
        print(f"[INFO] {label}: {len(series)} items fetched, {matched} kept")
        if matched == 0:
            fails.append(label)
            print(f"[FAIL] {label}: zero rows matched — discarded, will retry next run")
            continue
        for iso in missing:
            for it in per.get(iso, []):
                rows.append({"country": iso, "indicator": label, "category": "Economic",
                             "date": f"{it['date']}-12-31", "value": it["value"], "unit": unit,
                             "region": valid[iso]["region_en"], "source": "World Bank"})
        time.sleep(2)
    df = pd.DataFrame(rows).drop_duplicates()
    df.to_csv(OUT, index=False)
    print(f"\n{len(df)} rows in {OUT}")
    print(f"{len(fails)} failures — re-run to retry" if fails else "All series complete")

if __name__ == "__main__":
    main()