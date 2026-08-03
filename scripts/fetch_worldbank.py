import pathlib, sys, time
import pandas as pd
import requests

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.i18n import COUNTRIES

BASE = "https://api.worldbank.org/v2"
INDS = {"Inflation": ("FP.CPI.TOTL.ZG", "%"),
        "Interest rate": ("FR.INR.LEND", "%"),
        "GDP growth": ("NY.GDP.MKTP.KD.ZG", "%")}
HEADERS = {"User-Agent": "pestel-risk-desk/1.0 (portfolio project)"}

def fetch(wb_code, wb_ind, retries=3):
    url = f"{BASE}/country/{wb_code}/indicator/{wb_ind}"
    last = None
    for attempt in range(retries):
        try:
            r = requests.get(url, params={"format": "json", "date": "2000:2026", "per_page": 300},
                             headers=HEADERS, timeout=20)
            r.raise_for_status()
            ctype = r.headers.get("content-type", "")
            if "application/json" not in ctype:
                raise RuntimeError(f"Non-JSON response ({ctype}): {r.text[:120]}")
            p = r.json()
            if not isinstance(p, list) or len(p) < 2:
                raise RuntimeError(f"Unexpected payload: {str(p)[:120]}")
            return p[1] or []
        except Exception as e:
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise last

def main():
    rows, fails = [], []
    for iso3, (_, _, wb, region) in COUNTRIES.items():
        for label, (wb_ind, unit) in INDS.items():
            try:
                series = fetch(wb, wb_ind)
            except Exception as e:
                fails.append((iso3, label, str(e)))
                print(f"[FAIL] {iso3} | {label}: {e}")
                continue
            n = 0
            for it in series:
                if it.get("value") is None:
                    continue
                rows.append({"country": iso3, "indicator": label, "category": "Economic",
                             "date": f"{it['date']}-12-31", "value": it["value"], "unit": unit,
                             "region": region, "source": "World Bank"})
                n += 1
            print(f"[OK]   {iso3} | {label}: {n} rows")
            time.sleep(0.3)
    df = pd.DataFrame(rows)
    out = ROOT / "data" / "macro_indicators.csv"
    out.parent.mkdir(exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\n{len(df)} rows written to {out}")
    print(f"{len(fails)} failures" if fails else "All series fetched")

if __name__ == "__main__":
    main()