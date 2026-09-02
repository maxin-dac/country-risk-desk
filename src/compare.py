"""Mode comparaison - graphiques Plotly et tableau croise."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.i18n import RISK_ORDER, cname, iname, t
from src.plot_theme import apply_theme, unit_suffix

COLORS = ["#4cc9f0", "#f72585", "#b5e48c", "#ffd166", "#ef476f", "#06d6a0",
          "#118ab2", "#f4a261", "#9b5de5", "#e63946", "#2a9d8f", "#e9c46a"]

IND_ORDER = list(RISK_ORDER)


def _latest(df):
    return df.sort_values("date").groupby(["country", "indicator"], as_index=False).tail(1)


def line_chart(df, indicator, countries, lang):
    fig = go.Figure()
    sub = df[(df.indicator == indicator) & (df.country.isin(countries))].copy()
    sub["year"] = pd.to_datetime(sub["date"], errors="coerce").dt.year
    for i, c in enumerate(countries):
        d = sub[sub.country == c].sort_values("year")
        if d.empty:
            continue
        fig.add_trace(go.Scatter(
            x=d.year, y=d.value, mode="lines",
            name=cname(c, lang),
            line=dict(color=COLORS[i % len(COLORS)], width=2.2),
        ))
    fig.update_layout(showlegend=True,
                      legend=dict(orientation="h", yanchor="bottom", y=-0.25,
                                  xanchor="center", x=0.5,
                                  font=dict(color="#9fb3c8", size=10)))
    return apply_theme(fig, title=iname(indicator, lang),
                       unit=unit_suffix(indicator, lang))


def latest_pivot(df, countries, lang, latest=None):
    lat = latest if latest is not None else _latest(df)
    sub = lat[lat.country.isin(countries)]
    piv = sub.pivot(index="country", columns="indicator", values="value")
    piv = piv.reindex([c for c in countries if c in set(piv.index)])
    piv.index = [f"{cname(c, lang)} ({c})" for c in piv.index]
    # Colonnes avec unites (sans doublon si le nom en contient deja une)
    def _lab(ind):
        base = iname(ind, lang)
        u = unit_suffix(ind, lang)
        return base if u and base.endswith(u) else base + u
    piv = piv[[c for c in piv.columns if c in RISK_ORDER]]
    piv = piv.rename(columns={c: _lab(c) for c in piv.columns})
    return piv[[c for c in [_lab(i) for i in IND_ORDER
                            if i in df.indicator.unique()]
                if c in piv.columns]]


def positioning_scatter(df, countries, lang, latest=None):
    lat = latest if latest is not None else _latest(df)
    xs, ys, names, cols = [], [], [], []
    for i, c in enumerate(countries):
        g = lat[(lat.country == c) & (lat.indicator == "GDP growth")].value
        n = lat[(lat.country == c) & (lat.indicator == "Inflation")].value
        if len(g) and len(n):
            xs.append(float(g.iloc[0]))
            ys.append(float(n.iloc[0]))
            names.append(cname(c, lang))
            cols.append(COLORS[i % len(COLORS)])
    fig = go.Figure(go.Scatter(
        x=xs, y=ys, mode="markers+text", text=names,
        textposition="top center",
        textfont=dict(color="#d7e2ec", size=10),
        marker=dict(size=11, color=cols, opacity=0.85,
                    line=dict(color="rgba(255,255,255,.4)", width=1)),
    ))
    fig.add_hline(y=5, line_dash="dash", line_color="rgba(220,38,38,.5)")
    fig.add_vline(x=0, line_dash="dash", line_color="rgba(220,38,38,.5)")
    return apply_theme(fig,
                       title=t("compare_map", lang),
                       unit="(%)")


def render_compare(df, countries, lang):
    if len(countries) < 2:
        st.info(t("compare_hint", lang))
        return
    # Calculer latest une seule fois, partagé par _signal_counts, latest_pivot et positioning_scatter
    latest = _latest(df)
    chips = " ".join(
        f'<span class="chip" style="border-left:4px solid {COLORS[i % len(COLORS)]}">'
        f'{cname(c, lang)}</span>'
        for i, c in enumerate(countries))
    st.markdown(f"<div style='margin:.5rem 0'>{chips}</div>", unsafe_allow_html=True)
    sig_counts = _signal_counts(latest, countries)
    ranked = sorted(countries, key=lambda c: sig_counts.get(c, 0), reverse=True)
    row = " \u00b7 ".join(
        f"{cname(c, lang)}: <b>{sig_counts.get(c, 0)}</b> "
        + ("signaux" if lang == "fr" else "signals")
        for c in ranked)
    st.markdown("#### " + ("Signaux de seuils actifs (d\u00e9croissant)" if lang == "fr"
                           else "Active threshold signals (descending)"))
    st.markdown(row, unsafe_allow_html=True)
    st.caption(("Nombre de r\u00e8gles document\u00e9es d\u00e9clench\u00e9es par les derni\u00e8res valeurs "
                "publi\u00e9es \u2014 d\u00e9compte factuel, pas un score."
                if lang == "fr" else
                "Number of documented rules triggered by the latest published values "
                "\u2014 a factual count, not a score."))
    inds = [i for i in IND_ORDER if i in set(df.indicator)]
    for start in range(0, len(inds), 2):
        pair = inds[start:start + 2]
        cols = st.columns(len(pair))
        for j, ind in enumerate(pair):
            with cols[j]:
                st.plotly_chart(line_chart(df, ind, countries, lang),
                                width='stretch')
    st.markdown(f"<h3>{t('compare_latest', lang)}</h3>", unsafe_allow_html=True)
    st.dataframe(_dedup(latest_pivot(df, countries, lang, latest=latest)).style.format("{:.1f}", na_rep="-"),
                 width='stretch')
    st.markdown(f"<h3>{t('compare_map', lang)}</h3>", unsafe_allow_html=True)
    st.plotly_chart(positioning_scatter(df, countries, lang, latest=latest), width='stretch')


def _dedup(df):
    """Rend les noms de colonnes uniques (securite pivot)."""
    if df.columns.is_unique:
        return df
    seen = {}
    cols = []
    for col in df.columns:
        if col in seen:
            seen[col] += 1
            cols.append(f"{col} ({seen[col]})")
        else:
            seen[col] = 1
            cols.append(col)
    df = df.copy()
    df.columns = cols
    return df


def _signal_counts(latest, countries):
    """Nombre de regles de seuils declenchees par les dernieres valeurs publiees.
    Accepte un DataFrame 'latest' pré-calculé pour éviter le groupby redondant.
    Decompte factuel et documente - pas un score."""
    from .alerts import RULES
    out = {}
    for c in countries:
        sub = latest[latest.country == c]
        n = 0
        for rule in RULES:
            v = pd.to_numeric(sub[sub.indicator == rule["indicator"]]["value"], errors="coerce")
            n += int(v.map(rule["cond"]).fillna(False).sum())
        out[c] = n
    return out
