"""Import World Governance Indicators (WGI) from a manually downloaded Excel file.

Expected file:
    data/WGI.xlsx

This script extracts:
    - Rule of law
    - Regulatory quality

and merges them into:
    data/macro_indicators.csv

It supports both long and wide WGI formats.
"""
import re
import pathlib

import pandas as pd

CSV_PATH = pathlib.Path("data/macro_indicators.csv")
WGI_PATHS = [
    pathlib.Path("data/WGI.xlsx"),
    pathlib.Path("WGI.xlsx"),
]

TARGETS = {
    "Rule of law": {
        "sheet_keywords": ["rule", "law", "rl"],
        "indicator_keywords": ["rule of law"],
        "category": "Political & institutional",
        "unit": "index",
    },
    "Political stability": {
        "sheet_keywords": ["political stability"],
        "indicator_keywords": ["political stability"],
        "category": "Political & institutional",
        "unit": "index",
    },
    "Control of corruption": {
        "sheet_keywords": ["control of corruption"],
        "indicator_keywords": ["control of corruption"],
        "category": "Political & institutional",
        "unit": "index",
    },
    "Regulatory quality": {
        "sheet_keywords": ["regulatory", "quality", "rq"],
        "indicator_keywords": ["regulatory quality"],
        "category": "Political & institutional",
        "unit": "index",
    },
}

SOURCE = "World Bank (WGI)"


def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", str(s).lower()).strip()


def find_wgi_path():
    for p in WGI_PATHS:
        if p.exists():
            return p
    return None


def year_from_col(c):
    s = str(c)
    m = re.search(r"(19|20)\d{2}", s)
    if not m:
        return None
    y = int(m.group(0))
    if 1990 <= y <= 2035:
        return y
    return None


def read_sheet_with_header_detection(xls, sheet):
    """Try several header rows and keep the most plausible dataframe."""
    best = None
    best_score = -1

    for header in range(0, 10):
        try:
            df = xls.parse(sheet, header=header)
        except Exception:
            continue

        if df.empty:
            continue

        cols_norm = [norm(c) for c in df.columns]
        year_cols = [c for c in df.columns if year_from_col(c)]

        score = 0
        score += sum("country" in c for c in cols_norm)
        score += sum(c in ("code", "country code", "iso3", "iso 3") for c in cols_norm)
        score += sum("year" == c or c.endswith(" year") for c in cols_norm)
        score += sum("estimate" in c or "value" in c for c in cols_norm)
        score += min(len(year_cols), 5)

        if score > best_score:
            best = df
            best_score = score

    return best


def find_col(df, candidates):
    cols = list(df.columns)
    norm_map = {norm(c): c for c in cols}

    for cand in candidates:
        c = norm(cand)
        if c in norm_map:
            return norm_map[c]

    for c in cols:
        nc = norm(c)
        for cand in candidates:
            if norm(cand) in nc:
                return c

    return None


def detect_iso_col(df):
    """Find ISO3/country code column."""
    candidates = [
        "code", "country code", "iso3", "iso 3", "country.id",
        "country id", "economy code", "wbcode"
    ]
    col = find_col(df, candidates)
    if col is not None:
        return col

    # Fallback: inspect columns values looking for 3-letter uppercase codes
    for c in df.columns:
        s = df[c].dropna().astype(str).head(500)
        if len(s) == 0:
            continue
        ratio = s.str.fullmatch(r"[A-Z]{3}").mean()
        if ratio > 0.5:
            return c

    return None


def detect_year_col(df):
    return find_col(df, ["year"])


def detect_value_col(df):
    # Prefer "Estimate", avoid rank/lower/upper/std columns
    preferred = ["estimate", "value"]
    for c in df.columns:
        nc = norm(c)
        if any(p in nc for p in preferred):
            if not any(bad in nc for bad in ["rank", "lower", "upper", "std", "standard", "number", "num"]):
                return c
    return None


def detect_indicator_col(df):
    return find_col(df, ["indicator", "indicator name", "series", "series name"])


def sheet_target(sheet_name):
    ns = norm(sheet_name)
    for target, spec in TARGETS.items():
        kws = spec["sheet_keywords"]
        if all(k in ns for k in kws if len(k) > 2):
            return target

    # More permissive fallbacks
    if "rule" in ns and "law" in ns:
        return "Rule of law"
    if "regulatory" in ns and "quality" in ns:
        return "Regulatory quality"
    if ns in ("pv",):
        return "Political stability"
    if ns in ("cc",):
        return "Control of corruption"
    if ns in ("rl", "ruleoflaw", "rule law"):
        return "Rule of law"
    if ns in ("rq", "regulatoryquality", "reg quality"):
        return "Regulatory quality"

    return None


def rows_from_long(df, target=None):
    iso_col = detect_iso_col(df)
    year_col = detect_year_col(df)
    value_col = detect_value_col(df)
    indicator_col = detect_indicator_col(df)

    if iso_col is None or year_col is None or value_col is None:
        return []

    out = []

    work = df.copy()

    if target is None and indicator_col is not None:
        # Combined sheet: filter rows by indicator label
        for tname, spec in TARGETS.items():
            kws = spec["indicator_keywords"]
            mask = work[indicator_col].astype(str).str.lower().apply(
                lambda x: any(k in x for k in kws)
            )
            sub = work[mask]
            for _, row in sub.iterrows():
                out.append((tname, row.get(iso_col), row.get(year_col), row.get(value_col)))
        return out

    if target is None:
        return []

    for _, row in work.iterrows():
        out.append((target, row.get(iso_col), row.get(year_col), row.get(value_col)))

    return out


def rows_from_wide(df, target=None):
    if target is None:
        return []

    iso_col = detect_iso_col(df)
    if iso_col is None:
        return []

    year_cols = [c for c in df.columns if year_from_col(c)]
    if not year_cols:
        return []

    out = []
    for _, row in df.iterrows():
        iso3 = row.get(iso_col)
        for c in year_cols:
            y = year_from_col(c)
            v = row.get(c)
            out.append((target, iso3, y, v))
    return out


def main():
    wgi_path = find_wgi_path()
    if wgi_path is None:
        print("ERROR: WGI file not found.")
        print("Please save it as data/WGI.xlsx")
        return

    if not CSV_PATH.exists():
        print(f"ERROR: {CSV_PATH} not found.")
        return

    print(f"Using WGI file: {wgi_path}")

    df_main = pd.read_csv(CSV_PATH, dtype={"region": str})
    valid_countries = set(df_main["country"].dropna().astype(str).unique())
    region_map = dict(zip(df_main.country, df_main.region))

    xls = pd.ExcelFile(wgi_path)
    print("Sheets:", xls.sheet_names)

    raw_rows = []

    for sheet in xls.sheet_names:
        target = sheet_target(sheet)
        df = read_sheet_with_header_detection(xls, sheet)

        if df is None or df.empty:
            continue

        print(f"Reading sheet '{sheet}' -> target={target}")

        # Try long format first
        part = rows_from_long(df, target=target)

        # If long format fails, try wide format
        if not part:
            part = rows_from_wide(df, target=target)

        print(f"  extracted raw rows: {len(part)}")
        raw_rows.extend(part)

    new_rows = []
    for target, iso3, year, value in raw_rows:
        if target not in TARGETS:
            continue

        iso3 = str(iso3).strip().upper()
        if iso3 not in valid_countries:
            continue

        try:
            y = int(float(year))
        except Exception:
            continue

        if y < 1990 or y > 2035:
            continue

        v = pd.to_numeric(value, errors="coerce")
        if pd.isna(v):
            continue

        spec = TARGETS[target]
        new_rows.append({
            "country": iso3,
            "indicator": target,
            "category": spec["category"],
            "date": f"{y}-12-31",
            "value": float(v),
            "unit": spec["unit"],
            "region": region_map.get(iso3, ""),
            "source": SOURCE,
        })

    if not new_rows:
        print("\nWARNING: no WGI rows imported.")
        print("Please run the diagnostic below and send the output:")
        print("python - << 'PYEOF'")
        print("import pandas as pd; xls=pd.ExcelFile('data/WGI.xlsx');")
        print("print(xls.sheet_names)")
        print("for s in xls.sheet_names:")
        print("    df=xls.parse(s, nrows=5)")
        print("    print('---', s, '---'); print(list(df.columns)); print(df.head())")
        print("PYEOF")
        return

    df_new = pd.DataFrame(new_rows)
    df_new = df_new.drop_duplicates(subset=["country", "indicator", "date"], keep="last")

    names = sorted(df_new["indicator"].unique())
    keep = df_main[~df_main["indicator"].isin(names)]
    df_out = pd.concat([keep, df_new], ignore_index=True)
    df_out.to_csv(CSV_PATH, index=False)

    print(f"\nCSV updated: {len(df_out)} rows (+{len(df_new)} WGI rows)")
    print("Coverage:")
    for name in names:
        sub = df_out[df_out["indicator"] == name]
        print(f"  - {name}: {sub['country'].nunique()} countries, "
              f"{sub['date'].min()} -> {sub['date'].max()}")

    print("\nDone.")


if __name__ == "__main__":
    main()
