"""Dashboard global : carte des notations souveraines (S&P / Moody's / Fitch).
Aucun score ni consensus calcule par l'application."""
import plotly.graph_objects as go
from . import ratings as rat

_NOTCH_ORD = {
    "AAA": 0, "AA+": 1, "AA": 2, "AA-": 3, "A+": 4, "A": 5, "A-": 6,
    "BBB+": 7, "BBB": 8, "BBB-": 9, "BB+": 10, "BB": 11, "BB-": 12,
    "B+": 13, "B": 14, "B-": 15, "CCC+": 16, "CCC": 17, "CCC-": 18,
    "CC": 19, "C": 20, "D": 21, "SD": 21, "RD": 21,
    "Aaa": 0, "Aa1": 1, "Aa2": 2, "Aa3": 3, "A1": 4, "A2": 5, "A3": 6,
    "Baa1": 7, "Baa2": 8, "Baa3": 9, "Ba1": 10, "Ba2": 11, "Ba3": 12,
    "B1": 13, "B2": 14, "B3": 15, "Caa1": 16, "Caa2": 17, "Caa3": 18,
    "Ca": 19,
}


def _rating_ord(v):
    return _NOTCH_ORD.get((v or "").strip())


def _layer_keys(layer):
    return {"S&P": ("sp_r", "sp_o", "sp_d"),
            "Moody's": ("mo_r", "mo_o", "mo_d"),
            "Fitch": ("fi_r", "fi_o", "fi_d")}.get(layer, ("sp_r", "sp_o", "sp_d"))


def world_map_ratings(layer, lang):
    kr, ko, kd = _layer_keys(layer)
    rows = rat._load()
    iso, z, txt = [], [], []
    for code, r in rows.items():
        lab = (r.get(kr) or "").strip()
        if not lab:
            continue
        ordv = _rating_ord(lab)
        if ordv is None:
            continue
        outl = (r.get(ko) or "").strip()
        date = (r.get(kd) or "").strip()
        parts = [f"{code} \u00b7 {lab}"]
        if outl:
            parts.append(outl)
        if date:
            parts.append(date)
        iso.append(code)
        z.append(ordv)
        txt.append(" \u00b7 ".join(parts))
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
