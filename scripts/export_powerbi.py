# -*- coding: utf-8 -*-
"""Export Power BI v2 ("thin") : Python calcule tout, Power BI ne fait qu'afficher.
Zero DAX cote PBI ; cles iso3/indicator identiques partout (auto-detection des relations).
Sources de verite : data/*.csv + src/alerts.py + src/i18n.py + src/ratings.py + src/analytics.py.
"""
import pathlib, sys
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
DATA = ROOT / "data"
OUT = ROOT / "powerbi" / "data"
OUT.mkdir(parents=True, exist_ok=True)

from src.i18n import INDICATORS, RISK_ORDER, PILLARS, HIGHER_IS_WORSE, cname
from src.alerts import RULES, OPP_RULES
from src import ratings as rat
from src.analytics import _ORD

fact = pd.read_csv(DATA / "macro_indicators.csv", low_memory=False)
fact["value"] = pd.to_numeric(fact["value"], errors="coerce")
fact["date"] = pd.to_datetime(fact["date"], errors="coerce")
fact = fact.dropna(subset=["value", "date"])
countries = pd.read_csv(DATA / "countries.csv")

REGION_FR = {
    "East Asia & Pacific": "Asie de l'Est & Pacifique",
    "Europe & Central Asia": "Europe & Asie centrale",
    "Latin America & Caribbean": "Amerique latine & Caraibes",
    "Middle East & North Africa": "Moyen-Orient & Afrique du Nord",
    "South Asia": "Asie du Sud",
    "Sub-Saharan Africa": "Afrique subsaharienne",
}

# ---------------- dimensions ----------------
dim_c = countries[["iso3", "name_en", "region_en"]].copy()
dim_c["country_fr"] = [cname(i, "fr") for i in dim_c["iso3"]]
dim_c["region_fr"] = dim_c["region_en"].map(REGION_FR).fillna(dim_c["region_en"])
dim_c = dim_c.rename(columns={"name_en": "country_en"})
dim_c.to_csv(OUT / "pbi_countries.csv", index=False)

def _lab(k):
    v = INDICATORS.get(k)
    if isinstance(v, dict):
        return v["en"], v["fr"]
    if isinstance(v, tuple):
        return v
    return k, k

rows = []
for k in sorted(fact["indicator"].unique()):
    en, fr = _lab(k)
    u = fact.loc[fact.indicator == k, "unit"].mode()
    p = PILLARS.get(k, ("", ""))
    rows.append({"indicator": k, "label_en": en, "label_fr": fr,
                 "unit": u.iloc[0] if len(u) else "",
                 "pillar_en": p[0], "pillar_fr": p[1],
                 "higher_is_worse": k in HIGHER_IS_WORSE,
                 "in_risk_framework": k in RISK_ORDER})
pd.DataFrame(rows).to_csv(OUT / "pbi_indicators.csv", index=False)

# ---------------- dernieres valeurs + variations + tendance (calculees ici) ----------------
recs = []
for (c, i), d in fact.sort_values("date").groupby(["country", "indicator"]):
    d = d.sort_values("date")
    v1, d1 = float(d["value"].iloc[-1]), d["date"].iloc[-1]
    def _prev(days):
        p = d[d["date"] <= d1 - pd.Timedelta(days=days)]
        return float(p["value"].iloc[-1]) if len(p) else None
    v12, v3, v5 = _prev(365), _prev(91), _prev(1826)
    recs.append({
        "iso3": c, "indicator": i, "latest_value": v1,
        "latest_date": d1.strftime("%Y-%m-%d"),
        "change_12m_pct": (v1 - v12) / abs(v12) * 100 if v12 not in (None, 0) else None,
        "change_3m_pct": (v1 - v3) / abs(v3) * 100 if v3 not in (None, 0) else None,
        "trend_5y": (v1 - v5) if v5 is not None else None,
    })
lat = pd.DataFrame(recs)
lat = lat.merge(countries[["iso3", "region_en"]], on="iso3", how="left")
lat["regional_median"] = lat.groupby(["indicator", "region_en"])["latest_value"].transform("median")

def _pos(r, lang):
    v, m = r["latest_value"], r["regional_median"]
    if pd.isna(m):
        return "-"
    if v > m * 1.1:
        return "au-dessus de la mediane regionale" if lang == "fr" else "above regional median"
    if v < m * 0.9:
        return "sous la mediane regionale" if lang == "fr" else "below regional median"
    return "proche de la mediane regionale" if lang == "fr" else "near regional median"

def _sens(r, lang):
    t = r["trend_5y"]
    if t is None or abs(t) < 0.05:
        return "stable"
    hiw = r["indicator"] in HIGHER_IS_WORSE
    good = (t > 0 and not hiw) or (t < 0 and hiw)
    return ("en amelioration" if good else "en degradation") if lang == "fr" \
        else ("improving" if good else "worsening")

lat["position_fr"] = lat.apply(lambda r: _pos(r, "fr"), axis=1)
lat["position_en"] = lat.apply(lambda r: _pos(r, "en"), axis=1)
lat["trend_sens_fr"] = lat.apply(lambda r: _sens(r, "fr"), axis=1)
lat["trend_sens_en"] = lat.apply(lambda r: _sens(r, "en"), axis=1)
lat.drop(columns=["region_en"]).to_csv(OUT / "pbi_latest.csv", index=False)

# ---------------- signaux declenches (une ligne = un signal) ----------------
sig = []
for r in lat.itertuples():
    for side, rules in (("risk", RULES), ("opportunity", OPP_RULES)):
        for rule in rules:
            if rule["indicator"] == r.indicator and bool(rule["cond"](r.latest_value)):
                en = rule["en"] if isinstance(rule["en"], str) else rule["en"](r.latest_value)
                fr = rule["fr"] if isinstance(rule["fr"], str) else rule["fr"](r.latest_value)
                sig.append({"iso3": r.iso3, "indicator": r.indicator, "side": side,
                            "rule_id": rule["id"], "label_en": en, "label_fr": fr,
                            "value": r.latest_value})
sig = pd.DataFrame(sig, columns=["iso3", "indicator", "side", "rule_id", "label_en", "label_fr", "value"])
sig.to_csv(OUT / "pbi_signals.csv", index=False)

cnt = sig.groupby(["iso3", "side"]).size().unstack(fill_value=0)
for col in ("risk", "opportunity"):
    if col not in cnt.columns:
        cnt[col] = 0
cnt = cnt.reindex(countries["iso3"], fill_value=0).reset_index(names="iso3")
cnt["n_total"] = cnt["risk"] + cnt["opportunity"]
cnt = cnt.rename(columns={"risk": "n_risks", "opportunity": "n_opps"})
cnt[["iso3", "n_risks", "n_opps", "n_total"]].to_csv(OUT / "pbi_counts.csv", index=False)

# ---------------- positionnement croissance x inflation (pre-pivote) ----------------
piv = lat.pivot(index="iso3", columns="indicator", values="latest_value")
pos = pd.DataFrame({"iso3": piv.index,
                    "gdp_growth_latest": piv.get("GDP growth"),
                    "inflation_latest": piv.get("Inflation")}).dropna(subset=["gdp_growth_latest", "inflation_latest"])
pos.to_csv(OUT / "pbi_position.csv", index=False)

# ---------------- notations : long + wide + categories + divergences ----------------
def _cat(r):
    r = (r or "").strip()
    if not r:
        return "Unrated", "Non note"
    if r in ("D", "SD", "RD"):
        return "Default / withdrawn", "Defaut / retire"
    return ("Investment grade", "Investment grade") if _ORD.get(r, 99) <= 9 else ("Speculative", "Speculatif")

long_r, wide = [], {}
for iso, r in rat._load().items():
    wide.setdefault(iso, {"iso3": iso})
    ords = {}
    for agency, pre in (("S&P", "sp"), ("Moody's", "mo"), ("Fitch", "fi")):
        rt = (r.get(f"{pre}_r") or "").strip()
        ol = (r.get(f"{pre}_o") or "").strip()
        dt = (r.get(f"{pre}_d") or "").strip()
        d = pd.to_datetime(dt, errors="coerce")
        dto = d.strftime("%Y-%m-%d") if pd.notna(d) else dt
        en, fr = _cat(rt)
        long_r.append({"iso3": iso, "agency": agency, "rating": rt, "outlook": ol,
                       "date_iso": dto, "category_en": en, "category_fr": fr})
        wide[iso].update({f"{pre}_rating": rt, f"{pre}_outlook": ol, f"{pre}_date": dto,
                          f"{pre}_category_fr": fr})
        if rt and _ORD.get(rt) is not None and _ORD.get(rt) < 21:
            ords[agency] = _ORD[rt]
    kinds_en, kinds_fr = [], []
    if len(ords) >= 2:
        ig = {k: v <= 9 for k, v in ords.items()}
        outs = {(r.get(f"{p}_o") or "").strip() for p in ("sp_o", "mo_o", "fi_o")}
        if len(set(ig.values())) > 1:
            kinds_en.append("Investment vs speculative"); kinds_fr.append("Investment vs speculatif")
        elif max(ords.values()) - min(ords.values()) >= 2:
            kinds_en.append("Gap >= 2 notches"); kinds_fr.append("Ecart >= 2 crans")
        if "Positive" in outs and "Negative" in outs:
            kinds_en.append("Opposite outlooks"); kinds_fr.append("Perspectives opposees")
    wide[iso]["notch_gap"] = (max(ords.values()) - min(ords.values())) if len(ords) >= 2 else None
    wide[iso]["divergence_en"] = " + ".join(kinds_en)
    wide[iso]["divergence_fr"] = " + ".join(kinds_fr)
    wide[iso]["has_divergence"] = 1 if kinds_en else 0
pd.DataFrame(long_r).to_csv(OUT / "pbi_ratings_long.csv", index=False)
pd.DataFrame(list(wide.values())).to_csv(OUT / "pbi_ratings_wide.csv", index=False)

# ---------------- historique + projections ----------------
h = fact[["country", "indicator", "date", "value"]].rename(columns={"country": "iso3"})
h["date"] = h["date"].dt.strftime("%Y-%m-%d")
h.to_csv(OUT / "pbi_history.csv", index=False)

p = DATA / "imf_projections.csv"
if p.exists():
    proj = pd.read_csv(p)
    if {"year", "value"}.issubset(proj.columns):
        # deja au format long : pas de melt
        proj = proj.rename(columns={"country": "iso3"})
    else:
        # format large (colonnes annees) : melt
        yc = [c for c in proj.columns if str(c).isdigit()]
        proj = proj.melt(id_vars=[c for c in proj.columns if c not in yc],
                         value_vars=yc, var_name="year", value_name="value")
        proj = proj.rename(columns={"country": "iso3"})
    proj["value"] = pd.to_numeric(proj["value"], errors="coerce")
    proj = proj.dropna(subset=["value"])
    proj[["iso3", "indicator", "year", "value"]].to_csv(OUT / "pbi_projections.csv", index=False)

print("[OK] export thin Power BI :")
for f in sorted(OUT.glob("pbi_*.csv")):
    print(f"     - {f.name} : {len(pd.read_csv(f)):,} lignes")
