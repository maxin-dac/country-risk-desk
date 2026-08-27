"""Aggregate country-risk scoring (0-100, higher = riskier). Deterministic and explainable."""
import pandas as pd

from .i18n import cname

# indicator -> (higher_is_worse, best_value, worst_value)
ANCHORS = {
    "Inflation": (True, 2.0, 20.0),
    "GDP growth": (False, 5.0, -3.0),
    "Reserves": (False, 8.0, 1.5),
    "Current account": (False, 3.0, -8.0),
    "Gov debt": (True, 40.0, 130.0),
    "Gen gov debt": (True, 40.0, 130.0),
    "External debt": (True, 30.0, 100.0),
    "Debt service": (True, 5.0, 35.0),
    "Fiscal balance": (False, 1.0, -8.0),
    "Unemployment": (True, 4.0, 25.0),
    "Youth unemployment": (True, 10.0, 40.0),
    "Political stability": (False, 1.0, -2.0),
    "Rule of law": (False, 1.0, -2.0),
    "Regulatory quality": (False, 1.0, -2.0),
    "Control of corruption": (False, 1.0, -2.0),
    "Gini": (True, 30.0, 55.0),
    "Dependency ratio": (True, 50.0, 95.0),
    "Commodity dependence": (True, 10.0, 70.0),
}

PILLAR_WEIGHTS = {
    "External & sovereign": 0.30,
    "Macroeconomic": 0.30,
    "Political & institutional": 0.20,
    "Social & structural": 0.20,
}

PILLAR_OF = {
    "Reserves": "External & sovereign", "Current account": "External & sovereign",
    "External debt": "External & sovereign", "Debt service": "External & sovereign",
    "GDP growth": "Macroeconomic", "Inflation": "Macroeconomic",
    "Gov debt": "Macroeconomic", "Gen gov debt": "Macroeconomic",
    "Fiscal balance": "Macroeconomic", "Unemployment": "Macroeconomic",
    "Political stability": "Political & institutional",
    "Rule of law": "Political & institutional",
    "Regulatory quality": "Political & institutional",
    "Control of corruption": "Political & institutional",
    "Gini": "Social & structural", "Youth unemployment": "Social & structural",
    "Dependency ratio": "Social & structural",
    "Commodity dependence": "Social & structural",
}

_PILLAR_FR = {
    "External & sovereign": "Externe & souverain",
    "Macroeconomic": "Macro-economique",
    "Political & institutional": "Politique & institutionnel",
    "Social & structural": "Social & structurel",
}


def _subscore(indicator, value):
    if indicator not in ANCHORS or value is None or pd.isna(value):
        return None
    hiw, best, worst = ANCHORS[indicator]
    span = (worst - best) if hiw else (best - worst)
    if not span:
        return None
    raw = (value - best) / span * 100 if hiw else (best - value) / span * 100
    return max(0.0, min(100.0, raw))


def country_scores(df):
    """Return {country: {overall, pillars, details, coverage}}."""
    latest = (df.dropna(subset=["value"]).sort_values("date")
              .groupby(["country", "indicator"], as_index=False).tail(1))
    out = {}
    for country, grp in latest.groupby("country"):
        pillars, details = {}, []
        for _, row in grp.iterrows():
            ind = row["indicator"]
            sub = _subscore(ind, row["value"])
            if sub is None or ind not in PILLAR_OF:
                continue
            pillars.setdefault(PILLAR_OF[ind], []).append(sub)
            details.append((ind, float(row["value"]), sub))
        if not pillars:
            continue
        pil_scores = {p: sum(v) / len(v) for p, v in pillars.items()}
        wsum = sum(PILLAR_WEIGHTS.get(p, 0.2) for p in pil_scores)
        overall = sum(sc * PILLAR_WEIGHTS.get(p, 0.2)
                      for p, sc in pil_scores.items()) / (wsum or 1)
        out[country] = {"overall": overall, "pillars": pil_scores,
                        "details": details, "coverage": len(details)}
    return out


def label_for(score):
    if score < 35:
        return "Low", "Faible"
    if score < 55:
        return "Moderate", "Modere"
    if score < 70:
        return "Elevated", "Eleve"
    return "Critical", "Critique"


def score_html(country, scores, lang):
    s = scores.get(country)
    if not s:
        return ""
    lab = label_for(s["overall"])
    lab_txt = lab[1] if lang == "fr" else lab[0]
    order = sorted(scores.items(), key=lambda kv: kv[1]["overall"], reverse=True)
    pos = [c for c, _ in order].index(country) + 1
    o = s["overall"]
    color = ("#2ecc71" if o < 35 else "#f1c40f" if o < 55
             else "#e67e22" if o < 70 else "#e74c3c")
    rows = ""
    for p in ("External & sovereign", "Macroeconomic",
              "Political & institutional", "Social & structural"):
        v = s["pillars"].get(p)
        if v is None:
            continue
        pname = _PILLAR_FR[p] if lang == "fr" else p
        rows += (f'<div style="margin:.35rem 0">'
                 f'<div style="display:flex;justify-content:space-between;'
                 f'font-size:.72rem;color:#9fb3c4">'
                 f'<span>{pname}</span><span>{v:.0f}/100</span></div>'
                 f'<div style="background:rgba(255,255,255,.08);border-radius:4px;height:6px">'
                 f'<div style="width:{min(100, v):.0f}%;height:6px;border-radius:4px;'
                 f'background:{color}"></div></div></div>')
    title = "Score de risque pays" if lang == "fr" else "Country risk score"
    rank_txt = (f"rang de risque {pos}/{len(order)}"
                if lang == "fr" else f"risk rank {pos}/{len(order)}")
    return (f'<div class="brief" style="border-left:4px solid {color}">'
            f'<h3>{title}</h3>'
            f'<div style="display:flex;align-items:baseline;gap:1rem;flex-wrap:wrap">'
            f'<span style="font-size:2.2rem;font-weight:800;color:{color}">'
            f'{o:.0f}/100</span>'
            f'<span style="color:{color};font-weight:700">{lab_txt}</span>'
            f'<span style="color:#9fb3c4;font-size:.8rem">{rank_txt}</span></div>'
            f'{rows}</div>')


def top_risk_html(scores, lang, n=10):
    """Classement des n pays les plus risques (score decroissant)."""
    order = sorted(scores.items(),
                   key=lambda kv: kv[1]["overall"], reverse=True)[:n]
    rows = ""
    for i, (iso, s) in enumerate(order, 1):
        o = s["overall"]
        lab = label_for(o)
        lab_txt = lab[1] if lang == "fr" else lab[0]
        color = ("#2ecc71" if o < 35 else "#f1c40f" if o < 55
                 else "#e67e22" if o < 70 else "#e74c3c")
        rows += (f'<tr style="border-bottom:1px solid rgba(159,179,200,.15)">'
                 f'<td style="padding:.3rem .5rem;color:#9fb3c4">{i}</td>'
                 f'<td style="padding:.3rem .5rem">{cname(iso, lang)} '
                 f'<span style="color:#9fb3c4">({iso})</span></td>'
                 f'<td style="padding:.3rem .5rem;color:{color};font-weight:700">'
                 f'{o:.0f}/100</td>'
                 f'<td style="padding:.3rem .5rem;color:{color}">{lab_txt}</td></tr>')
    return ('<table style="width:100%;border-collapse:collapse;font-size:.85rem">'
            + rows + '</table>')
