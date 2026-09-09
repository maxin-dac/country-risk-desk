# -*- coding: utf-8 -*-
"""Export du schema en etoile du jumeau Power BI.
Sources de verite : data/*.csv + src/alerts.py (regles) + src/i18n.py (libelles).
Sortie : powerbi/data/*.csv - a regenerer apres chaque refresh mensuel.
"""
import inspect
import pathlib
import re
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data"
OUT = ROOT / "powerbi" / "data"
OUT.mkdir(parents=True, exist_ok=True)

# ---------------- dim_country ----------------
countries = pd.read_csv(DATA / "countries.csv")
try:
    from src.i18n import cname
    countries["name_fr"] = [cname(c, "fr") for c in countries["iso3"]]
except Exception:
    countries["name_fr"] = countries["name_en"]
countries.to_csv(OUT / "dim_country.csv", index=False)
print(f"[OK] dim_country.csv : {len(countries)} economies")

# ---------------- fact_indicators ----------------
from src.i18n import INDICATORS, RISK_ORDER, PILLARS, HIGHER_IS_WORSE
from src import alerts

fact = pd.read_csv(DATA / "macro_indicators.csv", low_memory=False)
f = fact[["country", "indicator", "date", "value"]].copy()
f["value"] = pd.to_numeric(f["value"], errors="coerce")
f = f.dropna(subset=["value"])
f.to_csv(OUT / "fact_indicators.csv", index=False)
print(f"[OK] fact_indicators.csv : {len(f):,} lignes")

# ---------------- dim_indicator ----------------
rows = []
for k in sorted(f["indicator"].unique()):
    lab = INDICATORS.get(k)
    if isinstance(lab, dict):
        en, fr = lab["en"], lab["fr"]
    elif isinstance(lab, tuple):
        en, fr = lab
    else:
        en, fr = k, k
    cat = fact.loc[fact.indicator == k, "category"]
    unit = fact.loc[fact.indicator == k, "unit"]
    cat_v = cat.mode()
    unit_v = unit.mode()
    pil = PILLARS.get(k, ("", ""))
    rows.append({
        "indicator": k, "label_en": en, "label_fr": fr,
        "category": cat_v.iloc[0] if len(cat_v) else "",
        "unit": unit_v.iloc[0] if len(unit_v) else "",
        "pillar_en": pil[0] if isinstance(pil, tuple) else pil,
        "pillar_fr": pil[1] if isinstance(pil, tuple) and len(pil) > 1 else pil,
        "higher_is_worse": k in HIGHER_IS_WORSE,
        "in_risk_framework": k in RISK_ORDER,
    })
pd.DataFrame(rows).to_csv(OUT / "dim_indicator.csv", index=False)
print(f"[OK] dim_indicator.csv : {len(rows)} indicateurs")

# ---------------- dim_rating (3 agences unpivotees) ----------------
allr = []
for path, agency in [("ratings_sp.csv", "S&P"),
                     ("ratings_moodys.csv", "Moody's"),
                     ("ratings_fitch.csv", "Fitch")]:
    p = DATA / path
    if not p.exists():
        print(f"[!] {path} absent"); continue
    df = pd.read_csv(p)
    def col(cands, default=""):
        for c in cands:
            if c in df.columns:
                return df[c]
        return pd.Series([default] * len(df))
    allr.append(pd.DataFrame({
        "agency": agency,
        "country": col(["iso3", "country", "code"]),
        "rating": col(["rating", "grade", "long_term"]),
        "outlook": col(["outlook", "trend"]),
        "date": col(["date", "updated", "snapshot"]),
    }))
if allr:
    dr = pd.concat(allr, ignore_index=True)
    dr = dr.dropna(subset=["country"])
    dr.to_csv(OUT / "dim_rating.csv", index=False)
    print(f"[OK] dim_rating.csv : {len(dr)} notations")

# ---------------- fact_projections ----------------
p = DATA / "imf_projections.csv"
if p.exists():
    proj = pd.read_csv(p)
    year_cols = [c for c in proj.columns if re.fullmatch(r"\d{4}", str(c))]
    if year_cols:
        proj = proj.melt(id_vars=[c for c in proj.columns if c not in year_cols],
                         value_vars=year_cols, var_name="year", value_name="value")
    proj["value"] = pd.to_numeric(proj["value"], errors="coerce")
    proj = proj.dropna(subset=["value"])
    keep = [c for c in ["country", "indicator", "year", "value"] if c in proj.columns]
    proj[keep].to_csv(OUT / "fact_projections.csv", index=False)
    print(f"[OK] fact_projections.csv : {len(proj):,} lignes")

# ---------------- dim_rules (seuils lus depuis alerts.py) ----------------
def op_threshold(rule):
    try:
        src = inspect.getsource(rule["cond"])
        m = re.search(r"v\s*(>|<)\s*(-?\d+(?:\.\d+)?)", src)
        if m:
            return m.group(1), float(m.group(2))
    except Exception:
        pass
    return None, None

def _clean(s):
    return re.sub(r"\s*\(va\w+[^)]*\)\s*$", "", s).strip()

rules = []
for side, lst in (("risk", alerts.RULES), ("opportunity", alerts.OPP_RULES)):
    for r in lst:
        op, thr = op_threshold(r)
        probe = (thr + (1 if op == ">" else -1)) if thr is not None else 0
        en = r["en"] if isinstance(r["en"], str) else _clean(r["en"](probe))
        fr = r["fr"] if isinstance(r["fr"], str) else _clean(r["fr"](probe))
        rules.append({"rule_id": r["id"], "side": side, "indicator": r["indicator"],
                      "operator": op, "threshold": thr,
                      "label_en": en, "label_fr": fr})
pd.DataFrame(rules).to_csv(OUT / "dim_rules.csv", index=False)
print(f"[OK] dim_rules.csv : {len(rules)} regles (risk + opportunity)")

print("\n=== Schema en etoile Power BI exporte dans powerbi/data/ ===")
