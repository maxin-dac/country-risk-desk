"""Mode comparaison — graphiques Plotly et tableau croise."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.i18n import cname, iname, t

COLORS = ["#4cc9f0", "#f72585", "#b5e48c", "#ffd166", "#ef476f", "#06d6a0",
          "#118ab2", "#f4a261", "#9b5de5", "#e63946", "#2a9d8f", "#e9c46a"]

IND_ORDER = ["GDP growth", "Inflation", "Interest rate", "Current account",
             "Gov debt", "External debt", "Reserves", "Unemployment"]


def _latest(df):
    return df.sort_values("date").groupby(["country", "indicator"], as_index=False).tail(1)


def _layout(fig, title):
    fig.update_layout(
        height=300, margin=dict(l=8, r=8, t=34, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#d7e2ec", size=11), showlegend=False,
        title=dict(text=title, font=dict(size=13, color="#9fb3c8")),
        xaxis=dict(showgrid=False, dtick=4),
        yaxis=dict(gridcolor="rgba(255,255,255,.08)", zerolinecolor="rgba(255,255,255,.15)"),
    )
    return fig


def line_chart(df, indicator, countries, lang):
    fig = go.Figure()
    sub = df[(df.indicator == indicator) & (df.country.isin(countries))].copy()
    sub["year"] = pd.to_datetime(sub["date"]).dt.year
    for i, c in enumerate(countries):
        d = sub[sub.country == c].sort_values("year")
        if d.empty:
            continue
        fig.add_trace(go.Scatter(x=d.year, y=d.value, mode="lines",
                                 line=dict(color=COLORS[i % len(COLORS)], width=2)))
    return _layout(fig, iname(indicator, lang))


def latest_pivot(df, countries, lang):
    lat = _latest(df)
    sub = lat[lat.country.isin(countries)]
    piv = sub.pivot(index="country", columns="indicator", values="value")
    piv = piv.reindex([c for c in countries if c in set(piv.index)])
    piv.index = [f"{cname(c, lang)} ({c})" for c in piv.index]
    return piv[[c for c in IND_ORDER if c in piv.columns]]


def positioning_scatter(df, countries, lang):
    lat = _latest(df)
    xs, ys, names, cols = [], [], [], []
    for i, c in enumerate(countries):
        g = lat[(lat.country == c) & (lat.indicator == "GDP growth")].value
        n = lat[(lat.country == c) & (lat.indicator == "Inflation")].value
        if len(g) and len(n):
            xs.append(float(g.iloc[0]))
            ys.append(float(n.iloc[0]))
            names.append(cname(c, lang))
            cols.append(COLORS[i % len(COLORS)])
    fig = go.Figure(go.Scatter(x=xs, y=ys, mode="markers+text", text=names,
                               textposition="top center",
                               textfont=dict(color="#d7e2ec", size=10),
                               marker=dict(size=11, color=cols)))
    fig.add_hline(y=5, line_dash="dash", line_color="rgba(220,38,38,.5)")
    fig.add_vline(x=0, line_dash="dash", line_color="rgba(220,38,38,.5)")
    fig.update_layout(xaxis_title=t("axis_growth", lang), yaxis_title=t("axis_inflation", lang))
    return _layout(fig, t("compare_map", lang))


def render_compare(df, countries, lang):
    if len(countries) < 2:
        st.info(t("compare_hint", lang))
        return
    chips = " ".join(
        f'<span class="chip" style="border-left:4px solid {COLORS[i % len(COLORS)]}">{cname(c, lang)}</span>'
        for i, c in enumerate(countries))
    st.markdown(f"<div style='margin:.5rem 0'>{chips}</div>", unsafe_allow_html=True)
    inds = [i for i in IND_ORDER if i in set(df.indicator)]
    for start in range(0, len(inds), 2):
        pair = inds[start:start + 2]
        cols = st.columns(len(pair))
        for j, ind in enumerate(pair):
            with cols[j]:
                st.plotly_chart(line_chart(df, ind, countries, lang), use_container_width=True)
    st.markdown(f"<h3>{t('compare_latest', lang)}</h3>", unsafe_allow_html=True)
    st.dataframe(latest_pivot(df, countries, lang).style.format("{:.1f}", na_rep="—"),
                 use_container_width=True)
    st.markdown(f"<h3>{t('compare_map', lang)}</h3>", unsafe_allow_html=True)
    st.plotly_chart(positioning_scatter(df, countries, lang), use_container_width=True)
