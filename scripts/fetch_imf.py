"""Fetch IMF WEO from the official Excel database.
Handles multi-sheet files (cover page first) and the 2025+ format with subject codes.
"""
import datetime
import io
import pathlib
import urllib.request

import pandas as pd

CSV_PATH = pathlib.Path("data/macro_indicators.csv")
PROJ_PATH = pathlib.Path("data/imf_projections.csv")
LOCAL_XLSX = pathlib.Path("data/WEOAll.xlsx")

BROWSER = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

CATEGORY = "Macroeconomic"
SOURCE = "IMF (WEO)"

# WEO subject code -> (our name, merge historical?, unit)
CODES = {
    "GGXCNL_NGDP": ("Fiscal balance", True, "% GDP"),
    "GGXWDG_NGDP": ("Gen gov debt", True, "% GDP"),
    "NGDP_RPCH": ("GDP growth", False, "%"),
    "PCPIPCH": ("Inflation", False, "%"),
}


def _match(code, desc):
    code = str(code).strip()
    parts = code.split(".")
    if len(parts) == 3 and len(parts[1]) > 2:
        code = parts[1]  # SERIES_CODE form: ISO.INDICATOR.FREQ
    d = " ".join(str(desc).lower().split())
    if code in CODES:
        return CODES[code]
    if "net lending" in d and "percent of gdp" in d:
        return CODES["GGXCNL_NGDP"]
    if "gross debt" in d and "percent of gdp" in d:
        return CODES["GGXWDG_NGDP"]
    if "constant prices" in d and "percent change" in d:
        return CODES["NGDP_RPCH"]
    if "inflation" in d and "average" in d:
        return CODES["PCPIPCH"]
    return None


def _pick_sheet(xls):
    for n in xls.sheet_names:
        low = n.lower()
        if "countr" in low and "group" not in low:
            return n
    best, best_score = None, -1
    for n in xls.sheet_names:
        head = xls.parse(n, nrows=2)
        score = sum(1 for c in head.columns if str(c).strip().isdigit())
        if score > best_score:
            best, best_score = n, score
    return best


def _find_col(df, names):
    lower = {str(c).strip().lower(): c for c in df.columns}
    for n in names:
        if n in lower:
            return lower[n]
    return None


def load_weo_df():
    if LOCAL_XLSX.exists() and LOCAL_XLSX.read_bytes()[:4] == b"PK\x03\x04":
        print(f"Using local database: {LOCAL_XLSX}")
        xls = pd.ExcelFile(LOCAL_XLSX)
    else:
        now = datetime.date.today()
        xls = None
        for year in (now.year, now.year - 1):
            for seq, tag in (("01", "Apr"), ("02", "Oct")):
                url = f"https://www.imf.org/external/pubs/ft/weo/{year}/{seq}/weodata/WEO{year}{tag}All.xlsx"
                try:
                    print(f"Downloading {url} ...")
                    req = urllib.request.Request(url, headers=BROWSER)
                    with urllib.request.urlopen(req, timeout=180) as r:
                        data = r.read()
                    if data[:4] != b"PK\x03\x04":
                        continue
                    LOCAL_XLSX.write_bytes(data)
                    xls = pd.ExcelFile(io.BytesIO(data))
                    break
                except Exception as e:
                    print(f"  ! {e}")
            if xls:
                break
        if xls is None:
            return None
    sheet = _pick_sheet(xls)
    print(f"Sheets: {xls.sheet_names} -> using '{sheet}'")
    return xls.parse(sheet)


def main():
    now_year = datetime.date.today().year
    df_main = pd.read_csv(CSV_PATH, dtype={"region": str})
    region_map = dict(zip(df_main.country, df_main.region))
    valid = set(df_main.country.unique())

    weo = load_weo_df()
    if weo is None:
        print("ERROR: could not load the WEO database.")
        return

    weo.columns = [str(c).strip() for c in weo.columns]
    iso3_col = _find_col(weo, ["iso3"])
    code_col = _find_col(weo, ["indicator.id", "weo subject code", "subject code", "series code", "series id"])
    desc_col = _find_col(weo, ["indicator", "subject descriptor", "series name", "description"])
    if not iso3_col:
        for c in weo.columns:
            s = weo[c].dropna().astype(str).head(300)
            if len(s) and s.str.fullmatch(r"[A-Z]{3}").mean() > 0.9:
                iso3_col = c
                break
    if not code_col:
        for c in weo.columns:
            s = weo[c].dropna().astype(str).head(300)
            if s.str.contains("NGDP_RPCH|GGXCNL|GGXWDG|PCPIPCH", regex=True).any():
                code_col = c
                break
    print(f"Columns detected: iso3={iso3_col}, code={code_col}, desc={desc_col}")
    if not iso3_col or not (code_col or desc_col):
        print("ERROR: columns not recognized. Found:", list(weo.columns)[:20])
        return

    year_cols = [c for c in weo.columns if str(c).isdigit() and 1980 <= int(str(c)) <= now_year + 6]
    print(f"Rows: {len(weo)} | year columns: {len(year_cols)}")

    hist_names = ["Fiscal balance", "Gen gov debt"]
    keep = df_main[~df_main.indicator.isin(hist_names)]
    hist_rows, proj_rows = [], []
    matched = 0

    for _, row in weo.iterrows():
        m = _match(row.get(code_col) if code_col else "", row.get(desc_col) if desc_col else "")
        if not m:
            continue
        matched += 1
        name, merge_hist, unit = m
        iso3 = str(row[iso3_col]).strip()
        if iso3 not in valid:
            continue
        for yc in year_cols:
            v = pd.to_numeric(row.get(yc), errors="coerce")
            if pd.isna(v):
                continue
            y = int(str(yc))
            if y > now_year:
                proj_rows.append({"country": iso3, "indicator": name, "year": y,
                                  "value": float(v), "unit": unit, "source": SOURCE})
            elif merge_hist:
                hist_rows.append({"country": iso3, "indicator": name, "category": CATEGORY,
                                  "date": f"{y}-12-31", "value": float(v), "unit": unit,
                                  "region": region_map.get(iso3, ""), "source": SOURCE})

    if matched == 0:
        print("WARNING: nothing matched. Sample codes/descriptors:")
        if code_col:
            print(weo[code_col].dropna().unique()[:30])
        if desc_col:
            print(weo[desc_col].dropna().unique()[:20])
        return

    df_hist = pd.DataFrame(hist_rows)
    df = pd.concat([keep, df_hist], ignore_index=True) if len(df_hist) else keep
    df.to_csv(CSV_PATH, index=False)
    print(f"Main CSV updated: {len(df)} rows (+{len(df_hist)} IMF historical)")

    df_proj = pd.DataFrame(proj_rows)
    if len(df_proj):
        df_proj.to_csv(PROJ_PATH, index=False)
        print(f"Projections written: {len(df_proj)} rows -> {PROJ_PATH}")

    print("\nCoverage report (historical):")
    for name in hist_names:
        print(f"  - {name}: {df.loc[df.indicator == name, 'country'].nunique()} countries")
    if len(df_proj):
        print("Coverage report (projections):")
        for name in sorted(df_proj.indicator.unique()):
            sub = df_proj[df_proj.indicator == name]
            print(f"  - {name}: {sub.country.nunique()} countries, {sub.year.min()}-{sub.year.max()}")


if __name__ == "__main__":
    main()
