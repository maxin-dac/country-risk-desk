import datetime, io, json, pathlib
import streamlit as st
from src import config
from src import dashboard
from src import ratings as rat
from src import analytics
from src.alerts import compute_alerts, generate_outlook
from src.compare import line_chart, render_compare
from src.csv_loader import get_stats, load_csv
from src.i18n import INDICATORS, RISK_ORDER, cname, iname, t
from src.pdf_export import generate_pdf_bytes
from src.ui_render import report_html
from src.ui_theme import CSS, masthead

st.set_page_config(page_title="Country Risk Desk", page_icon="\U0001f6f0", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def get_df():
    return load_csv(config.CSV_PATH)


def render_dashboard(df, alerts, lang):
    st.markdown("### " + ("Global macroeconomic dashboard" if lang == "en"
                          else "Tableau de bord macroeconomique global"))
    map_layer = st.radio(("Rating agency" if lang == "en" else "Agence de notation"),
                         ["S&P", "Moody's", "Fitch"],
                         horizontal=True, key="map_layer")
    with st.expander("World map of sovereign ratings" if lang == "en"
                     else "Carte mondiale des notations souveraines", expanded=True):
        st.plotly_chart(dashboard.world_map_ratings(map_layer, lang), width="stretch")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(dashboard.rating_distribution(map_layer, lang), width="stretch")
    with col2:
        st.markdown("#### " + ("Summary" if lang == "en" else "Synth\u00e8se"))
        g = dashboard.grade_summary(df, map_layer)
        st.metric("Rated countries" if lang == "en" else "Pays not\u00e9s", g["rated"])
        st.metric("Investment grade", g["ig"])
        st.metric("Speculative grade", g["spec"])
        st.metric("Default / withdrawn" if lang == "en" else "D\u00e9faut / retir\u00e9", g["def"])
        st.metric("Not rated" if lang == "en" else "Non not\u00e9s", g["unrated"])
        st.caption(
            f"Notations : {map_layer}. Source : Wikipedia, instantane 2026-09-01."
            if lang == "fr" else
            f"Ratings: {map_layer}. Source: Wikipedia, snapshot 2026-09-01.")
    if alerts:
        st.markdown("#### " + ("Reference threshold monitor" if lang == "en"
                               else "Suivi des seuils de reference"))
        st.caption(
            "Seuils indicatifs appliques aux donnees officielles : le franchissement d'un seuil est une lecture factuelle, non un jugement sur le pays."
            if lang == "fr" else
            "Indicative thresholds applied to official data: crossing a threshold is a factual reading, not a judgement on the country.")
        for a in alerts:
            label = a["fr"] if lang == "fr" else a["en"]
            with st.expander(f"{label} \u00b7 {len(a['hits'])}"):
                for _i in range(0, len(a["hits"]), 4):
                    _cols = st.columns(4)
                    for _j, (_iso, _v) in enumerate(a["hits"][_i:_i + 4]):
                        _cols[_j].button(
                            f"{cname(_iso, lang)} \u00b7 {_v:.0f}",
                            key=f"al_{a['id']}_{_iso}",
                            on_click=lambda i2=_iso: st.session_state.update(
                                {"country_sel": i2, "mode_sel": "brief"}))


    st.markdown("#### " + ("Cross-agency reading - S&P / Moody's / Fitch divergences" if lang == "en"
                          else "Lecture croisee des agences - divergences S&P / Moody's / Fitch"))
    analytics.render_divergences(lang)


def assemble_report(df, country, indicator, lang):
    stats = get_stats(df, country, indicator)
    if not stats.get("available"):
        return {"status": "error", "error": f"No data for {country} / {indicator}"}
    return {
        "status": "done_numeric",
        "title": f"Country Risk Desk - {country} - {indicator}",
        "country": country, "indicator": indicator, "lang": lang,
        "category": stats.get("category", ""),
        "stats": stats,
        "outlook": generate_outlook(stats),
        "limitations": [],
        "sources": [],
        "generated_at": "",
    }


# ---- Main ----
df = get_df()
today = datetime.date.today().isoformat()

with st.sidebar:
    st.markdown(f"### {t('params', 'en')} / {t('params', 'fr')}")
    lang = st.selectbox(
        "Langue / Language", ["fr", "en"],
        format_func=lambda x: "\U0001f1eb\U0001f1f7 Fran\u00e7ais" if x == "fr"
        else "\U0001f1ec\U0001f1e7 English")
    mode = st.radio(
        t("mode", lang), ["brief", "compare", "dashboard"],
        horizontal=True,
        format_func=lambda m: (t("mode_brief", lang) if m == "brief"
                               else t("mode_dashboard", lang) if m == "dashboard"
                               else t("mode_compare", lang)),
        key="mode_sel")
    st.markdown("---")
    if mode == "brief":
        country = st.selectbox(
            t("country", lang), sorted(df.country.unique()),
            format_func=lambda c: f"{cname(c, lang)} ({c})",
            key="country_sel")
        avail = set(df[df.country == country].indicator.unique())
        ordered = [i for i in RISK_ORDER if i in avail]
        indicator = st.selectbox(
            t("indicator", lang), ordered,
            format_func=lambda x: iname(x, lang) if x in INDICATORS else x)
    elif mode == "compare":
        allc = sorted(df.country.unique())
        countries = st.multiselect(
            t("countries_sel", lang), allc,
            default=[c for c in ("MAR", "USA", "DEU") if c in allc],
            max_selections=12,
            format_func=lambda c: f"{cname(c, lang)} ({c})")

ticks = [f"<b>{c}</b> {cname(c, lang).upper()}"
         for c in sorted(df.country.unique())[:16]]
st.markdown(
    masthead(df.country.nunique(),
             len([i for i in RISK_ORDER if i in set(df.indicator)]),
             today, ("deterministic" if lang == "en" else "d\u00e9terministe"), lang, ticks),
    unsafe_allow_html=True)

alerts = compute_alerts(df)

if mode == "brief":
    st.markdown(rat.rating_card(country, lang), unsafe_allow_html=True)
    report = assemble_report(df, country, indicator, lang)
    html_all = report_html(report, lang)
    if report.get("status") != "error":
        i0 = html_all.find('<div class="brief')
        i1 = html_all.find('<div class="brief', i0 + 1) if i0 != -1 else -1
        if i1 != -1:
            with st.container():
                st.markdown('<div class="fused-flag"></div>', unsafe_allow_html=True)
                st.markdown(html_all[:i1], unsafe_allow_html=True)
                fig = line_chart(df, indicator, [country], lang)
                fig.update_layout(title=dict(text=f"{iname(indicator, lang)} - {cname(country, lang)}"))
                st.plotly_chart(fig, width="stretch")
            analytics.render_scenario(df, country, indicator, get_stats(df, country, indicator), lang)
            st.markdown(html_all[i1:], unsafe_allow_html=True)
        else:
            st.markdown(html_all, unsafe_allow_html=True)
            analytics.render_scenario(df, country, indicator, get_stats(df, country, indicator), lang)
    else:
        st.markdown(html_all, unsafe_allow_html=True)
    if report.get("status") != "error":
        try:
            st.download_button(
                t("export", lang),
                generate_pdf_bytes(report, lang),
                f"pestel_{country}_{indicator}.pdf".lower(),
                "application/pdf")
        except Exception as e:
            st.warning(f"{t('pdf_fail', lang)}: {e}")
        series = df[(df.country == country) & (df.indicator == indicator)]
        st.download_button(
            "Download data (CSV)" if lang == "en" else "T\u00e9l\u00e9charger les donn\u00e9es (CSV)",
            series.to_csv(index=False),
            f"country_risk_{country}_{indicator}.csv",
            "text/csv")
        _xb = io.BytesIO()
        series.to_excel(_xb, index=False)
        st.download_button(
            "Download data (Excel)" if lang == "en" else "T\u00e9l\u00e9charger les donn\u00e9es (Excel)",
            _xb.getvalue(),
            f"country_risk_{country}_{indicator}.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif mode == "compare":
    render_compare(df, countries, lang)
else:
    render_dashboard(df, alerts, lang)

st.sidebar.markdown("""
<div style="margin-top:3rem;padding-top:1.5rem;border-top:1px solid rgba(148,163,184,.2);
text-align:center;color:#8fa3b8;font-size:.75rem;">
<p style="margin:0 0 .75rem 0;font-weight:600;letter-spacing:.05em;">\u00a9 2026 Maxime NDACLEU</p>
<div style="display:flex;justify-content:center;gap:1.25rem;">
<a href="https://github.com/maxin-dac" target="_blank" style="color:#8fa3b8;">GitHub</a>
<a href="https://www.linkedin.com/in/maximendacleu" target="_blank" style="color:#8fa3b8;">LinkedIn</a>
</div></div>
""", unsafe_allow_html=True)
