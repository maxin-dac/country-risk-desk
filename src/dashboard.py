"""Dashboard global : notations souveraines (donnees factuelles des agences)."""
import plotly.graph_objects as go
from . import ratings as rat

_NOTCH_ORD = {
    "AAA": 0, "AA+": 1, "AA": 2, "AA-": 3, "A+": 4, "A": 5, "A-": 6,
    "BBB+": 7, "BBB": 8, "BBB-": 9, "BB+": 10, "BB": 11, "BB-": 12,
    "B+": 13, "B": 14, "B-": 15, "CCC+": 16, "CCC": 17, "CCC-": 18,
    "CC": 19, "C": 20, "D": 21, "SD": 21, "RD": 21, "WD": 21,
    "Aaa": 0, "Aa1": 1, "Aa2": 2, "Aa3": 3, "A1": 4, "A2": 5, "A3": 6,
    "Baa1": 7, "Baa2": 8, "Baa3": 9, "Ba1": 10, "Ba2": 11, "Ba3": 12,
    "B1": 13, "B2": 14, "B3": 15, "Caa1": 16, "Caa2": 17, "Caa3": 18,
    "Ca": 19,
}


def _rating_ord(v):
    return _NOTCH_ORD.get((v or "").strip())


def _key(layer):
    return {"S&P": "sp", "Moody's": "mo", "Fitch": "fi"}.get(layer, "sp")


def world_map_ratings(layer, lang):
    rows = rat.load()
    k = _key(layer)
    iso, z, txt = [], [], []
    for code, r in rows.items():
        lab = (r.get(k + "_r") or "").strip()
        if not lab:
            continue
        ordv = _rating_ord(lab)
        if ordv is None:
            continue
        outl = (r.get(k + "_o") or "").strip()
        dat = (r.get(k + "_d") or "").strip()
        iso.append(code)
        z.append(ordv)
        txt.append(f"{code} \u00b7 {lab}" + (f" \u00b7 {outl}" if outl else "")
                   + (f" \u00b7 {dat}" if dat else ""))
    fig = go.Figure(go.Choropleth(
        locations=iso, z=z, text=txt, locationmode="ISO-3",
        colorscale="RdYlGn_r", zmin=0, zmax=21,
        hovertemplate="%{text}<extra></extra>"))
    fig.update_traces(colorbar=dict(
        tickvals=[0, 3, 6, 9, 12, 15, 18, 21],
        ticktext=["AAA", "AA-", "A-", "BBB-", "BB-", "B-", "CCC-", "D"]))
    fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=520,
                      geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False))
    return fig


def rating_distribution(layer, lang):
    rows = rat.load()
    k = _key(layer)
    ords = [_rating_ord((r.get(k + "_r") or "").strip()) for r in rows.values()
            if (r.get(k + "_r") or "").strip()]
    ords = [o for o in ords if o is not None]
    fig = go.Figure(go.Histogram(
        x=ords, nbinsx=22,
        marker_color="rgba(76,201,240,0.75)",
        marker_line_color="rgba(76,201,240,1)",
        marker_line_width=1, opacity=0.85))
    fig.update_layout(
        xaxis=dict(tickvals=[0, 3, 6, 9, 12, 15, 18, 21],
                   ticktext=["AAA", "AA-", "A-", "BBB-", "BB-", "B-", "CCC-", "D"],
                   tickfont=dict(size=11, color="#9fb3c8"),
                   showgrid=False),
        yaxis=dict(tickfont=dict(size=10, color="#9fb3c8")),
        title=dict(text=(f"Rating distribution ({layer})" if lang == "en"
                         else f"Distribution des notations ({layer})"),
                   font=dict(size=14, color="#9fb3c8")),
        margin=dict(l=40, r=20, t=50, b=70), height=460,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig

def grade_summary(df, layer):
    rows = rat.load()
    k = _key(layer)
    ig = spec = defw = unrated = 0
    for c in (df.country.unique() if df is not None else []):
        r = rows.get(c)
        v = ((r.get(k + "_r") or "").strip()) if r else ""
        if not v:
            unrated += 1
            continue
        o = _rating_ord(v)
        if o is None:
            defw += 1
        elif o <= 9:
            ig += 1
        elif o <= 20:
            spec += 1
        else:
            defw += 1
    return {"rated": ig + spec + defw, "ig": ig, "spec": spec,
            "def": defw, "unrated": unrated}
