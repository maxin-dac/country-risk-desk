"""Dashboard global : carte, distribution, evolution temporelle des scores."""
import pandas as pd
import plotly.graph_objects as go

from .plot_theme import apply_theme, unit_suffix
from .risk_scoring import country_scores, label_for


def world_map(scores, lang):
    fig = go.Figure(data=go.Choropleth(
        locations=list(scores.keys()),
        z=[s["overall"] for s in scores.values()],
        text=[f"{iso}: {s['overall']:.0f}{unit_suffix('Risk score', lang)}"
              for iso, s in scores.items()],
        colorscale=[
            [0, "#2ecc71"], [0.35, "#f1c40f"], [0.55, "#e67e22"],
            [0.70, "#e74c3c"], [1, "#8b0000"],
        ],
        reversescale=False,
        marker_line_color="rgba(159,179,200,.25)",
        marker_line_width=0.5,
        colorbar=dict(
            title=dict(text=("Risk" if lang == "en" else "Risque") + unit_suffix("Risk score", lang),
                       font=dict(color="#9fb3c8", size=11)),
            thickness=20, len=0.5, tick0=0, dtick=20,
            tickfont=dict(color="#9fb3c8", size=10),
        ),
    ))
    fig.update_layout(
        geo=dict(
            showframe=False, showcoastlines=True,
            projection_type="natural earth",
            bgcolor="rgba(0,0,0,0)",
            landcolor="rgba(40,50,60,.5)",
            lakecolor="rgba(0,0,0,0)",
            countrycolor="rgba(159,179,200,.25)",
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#d7e2ec", size=11),
        margin=dict(l=0, r=0, t=40, b=0),
        title=dict(
            text="World risk distribution" if lang == "en"
                 else "Distribution mondiale du risque",
            font=dict(size=14, color="#9fb3c8"), x=0.02),
    )
    return fig


def score_distribution(scores, lang):
    vals = [s["overall"] for s in scores.values()]
    fig = go.Figure(data=go.Histogram(
        x=vals, nbinsx=20,
        marker_color="rgba(76, 201, 240, 0.75)",
        marker_line_color="rgba(76, 201, 240, 1)",
        marker_line_width=1, opacity=0.85,
    ))
    for thresh, color, label in [
        (35, "#2ecc71", "Low" if lang == "en" else "Faible"),
        (55, "#f1c40f", "Moderate" if lang == "en" else "Modere"),
        (70, "#e67e22", "Elevated" if lang == "en" else "Eleve"),
    ]:
        fig.add_vline(x=thresh, line_dash="dash", line_color=color, opacity=0.6,
                      annotation_text=label, annotation_font_color=color,
                      annotation_font_size=10, annotation_position="top right")
    return apply_theme(fig,
                       title="Score distribution" if lang == "en"
                             else "Distribution des scores",
                       unit=unit_suffix("Risk score", lang))


def temporal_comparison(df, lang):
    periods = ["2020-12-31", "2022-12-31", "2024-12-31"]
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    snapshots = {}
    for period in periods:
        target = pd.to_datetime(period)
        subset = df[(df.date <= target + pd.DateOffset(months=6))
                    & (df.date >= target - pd.DateOffset(months=6))]
        if subset.empty:
            continue
        latest = (subset.sort_values("date")
                  .groupby(["country", "indicator"], as_index=False).tail(1))
        snapshots[period] = latest
    if len(snapshots) < 2:
        return None, {}
    period_scores = {p: country_scores(s) for p, s in snapshots.items()}
    common = set(period_scores[list(period_scores.keys())[0]].keys())
    for sc in period_scores.values():
        common &= set(sc.keys())
    if not common:
        return None, period_scores
    first, last = list(period_scores.keys())[0], list(period_scores.keys())[-1]
    variations = []
    for c in common:
        s1 = period_scores[first][c]["overall"]
        s2 = period_scores[last][c]["overall"]
        variations.append((c, s1, s2, s2 - s1))
    variations.sort(key=lambda x: abs(x[3]), reverse=True)
    return variations[:20], period_scores


# ==== Couche notations souveraines ====
_NOTCH_ORD = {
    "AAA": 0, "AA+": 1, "AA": 2, "AA-": 3, "A+": 4, "A": 5, "A-": 6,
    "BBB+": 7, "BBB": 8, "BBB-": 9, "BB+": 10, "BB": 11, "BB-": 12,
    "B+": 13, "B": 14, "B-": 15, "CCC+": 16, "CCC": 17, "CCC-": 18,
    "CC": 19, "C": 20, "D": 21, "SD": 21, "RD": 21,
    "Aaa": 0, "Aa1": 1, "Aa2": 2, "Aa3": 3, "A1": 4, "A2": 5, "A3": 6,
    "Baa1": 7, "Baa2": 8, "Baa3": 9, "Ba1": 10, "Ba2": 11, "Ba3": 12,
    "B1": 13, "B2": 14, "B3": 15, "Caa1": 16, "Caa2": 17, "Caa3": 18,
    "Ca": 19, "C": 20,
}


def _rating_ord(v):
    return _NOTCH_ORD.get((v or "").strip())


def world_map_ratings(layer, lang):
    import plotly.graph_objects as go
    from src import ratings as rat
    rows = rat._load()
    iso, z, txt = [], [], []
    for code, r in rows.items():
        outl = None
        if layer == "S&P":
            ordv, lab = _rating_ord(r.get("sp_r")), (r.get("sp_r") or "")
            outl = r.get("sp_o")
        elif layer == "Moody's":
            ordv, lab = _rating_ord(r.get("mo_r")), (r.get("mo_r") or "")
            outl = r.get("mo_o")
        elif layer == "Fitch":
            ordv, lab = _rating_ord(r.get("fi_r")), (r.get("fi_r") or "")
            outl = r.get("fi_o")
        else:
            vals = [_rating_ord(r.get(k)) for k in ("sp_r", "mo_r", "fi_r")]
            vals = [v for v in vals if v is not None]
            ordv = round(sum(vals) / len(vals)) if vals else None
            lab = "/".join((r.get(k) or "-") for k in ("sp_r", "mo_r", "fi_r"))
        iso.append(code)
        z.append(ordv)
        txt.append(f"{code} · {lab or 'Non classe'}" + (f" · {outl}" if outl else ""))
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


def rating_vs_score(scores, lang):
    import plotly.graph_objects as go
    from src import ratings as rat
    rows = rat._load()
    x, y, tt = [], [], []
    for code, s in scores.items():
        r = rows.get(code)
        if not r:
            continue
        vals = [_rating_ord(r.get(k)) for k in ("sp_r", "mo_r", "fi_r")]
        vals = [v for v in vals if v is not None]
        if not vals:
            continue
        x.append(sum(vals) / len(vals))
        y.append(s["overall"])
        tt.append(code)
    fig = go.Figure(go.Scatter(
        x=x, y=y, mode="markers", text=tt,
        marker=dict(size=9, color=y, colorscale="RdYlGn_r",
                    line=dict(width=1, color="rgba(255,255,255,.35)")),
        hovertemplate="%{text} · consensus %{x:.1f} · score %{y:.0f}<extra></extra>"))
    fig.update_layout(
        title=("Score desk vs consensus des agences" if lang == "fr"
               else "Desk score vs agency consensus"),
        xaxis_title=("Consensus agences (0 = AAA, 21 = D)" if lang == "fr"
                     else "Agency consensus (0 = AAA, 21 = D)"),
        yaxis_title=("Score de risque desk" if lang == "fr" else "Desk risk score"),
        margin=dict(l=50, r=20, t=40, b=50), height=420,
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig
