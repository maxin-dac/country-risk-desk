"""Dashboard global : carte, distribution, evolution temporelle des scores."""
import pandas as pd
import plotly.graph_objects as go

from .plot_theme import apply_theme, unit_suffix
from .risk_scoring import country_scores, label_for


def world_map(scores, lang):
    fig = go.Figure(data=go.Choropleth(
        locations=list(scores.keys()),
        z=[s["overall"] for s in scores.values()],
        text=[f"{iso}: {s['overall']:.0f}{unit_suffix('Risk score')}"
              for iso, s in scores.items()],
        colorscale=[
            [0, "#2ecc71"], [0.35, "#f1c40f"], [0.55, "#e67e22"],
            [0.70, "#e74c3c"], [1, "#8b0000"],
        ],
        reversescale=False,
        marker_line_color="rgba(159,179,200,.25)",
        marker_line_width=0.5,
        colorbar=dict(
            title=dict(text="Risk" + unit_suffix("Risk score"),
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
