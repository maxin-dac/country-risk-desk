import datetime, io, json, pathlib
import streamlit as st
from src import config
from src import dashboard
from src import ratings as rat
from src.alerts import compute_alerts
from src.compare import line_chart, render_compare
from src.csv_loader import get_stats, load_csv
from src.i18n import INDICATORS, RISK_ORDER, cname, iname, t
from src.pdf_export import generate_pdf_bytes
from src.risk_scoring import country_scores, score_html, top_risk_html
from src.ui_render import report_html
from src.ui_theme import CSS, masthead

st.set_page_config(page_title="Country Risk Desk", page_icon="\U0001f6f0", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def get_df():
    return load_csv(config.CSV_PATH)


@st.cache_data(show_spinner=False)
def get_briefs():
    p = pathlib.Path(config.BRIEFS_PATH)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


@st.cache_data(show_spinner=False)
def get_scores():
    return country_scores(load_csv(config.CSV_PATH))


def render_dashboard(df, alerts, lang):
    st.markdown("### " + ("Tableau de bord risque global" if lang == "fr" else "Global risk dashboard"))
    scores = get_scores()
    with st.expander("World risk map" if lang == "en" else "Carte mondiale du risque", expanded=True):
        st.plotly_chart(dashboard.world_map(scores, lang), width="stretch")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.plotly_chart(dashboard.score_distribution(scores, lang), width="stretch")
    with col2:
        st.markdown("#### " + ("Summary" if lang == "en" else "Synthese"))
        vals = [s["overall"] for s in scores.values()]
        cats = [
            ("low", "Low risk (< 35)" if lang == "en" else "Risque faible (< 35)",
             lambda v: v < 35),
            ("mod", "Moderate (35-54)" if lang == "en" else "Modere (35-54)",
             lambda v: 35 <= v < 55),
            ("high", "Elevated (55-69)" if lang == "en" else "Eleve (55-69)",
             lambda v: 55 <= v < 70),
            ("crit", "Critical (>= 70)" if lang == "en" else "Critique (>= 70)",
             lambda v: v >= 70),
        ]
        st.metric("Total countries" if lang == "en" else "Total pays", len(vals))
        for _key, _label, _cond in cats:
            _n = sum(1 for v in vals if _cond(v))
            _active = st.session_state.get("dash_filter") == _key
            if st.button(f"{_label} : {_n}", key=f"dash_cat_{_key}",
                         type="primary" if _active else "secondary"):
                st.session_state["dash_filter"] = None if _active else _key
    _flt = st.session_state.get("dash_filter")
    if _flt:
        _cond = {c[0]: c[2] for c in cats}[_flt]
        _members = sorted(
            ((iso, s["overall"]) for iso, s in scores.items() if _cond(s["overall"])),
            key=lambda kv: kv[1], reverse=True)
        _lab = {c[0]: c[1] for c in cats}[_flt]
        st.markdown(f"##### {_lab} - {len(_members)}")
        for _i in range(0, len(_members), 6):
            _cols = st.columns(6)
            for _j, (_iso, _sc) in enumerate(_members[_i:_i + 6]):
                _cols[_j].button(
                    f"{cname(_iso, lang)} \u00b7 {_sc:.0f}",
                    key=f"dash_m_{_flt}_{_iso}",
                    on_click=lambda i2=_iso: st.session_state.update(
                        {"country_sel": i2, "mode_sel": "brief"}))
    st.markdown("#### " + ("Top 10 riskiest countries" if lang == "en" else "Top 10 pays les plus risques"))
    st.markdown(top_risk_html(scores, lang), unsafe_allow_html=True)
    if alerts:
        st.markdown('<div class="alerts-red-flag"></div>', unsafe_allow_html=True)
        st.markdown("#### " + t("alerts_title", lang))
        for a in alerts:
            label = a["fr"] if lang == "fr" else a["en"]
            st.markdown(f"**{label}** \u00b7 {len(a['hits'])}")
            top = a["hits"][:8]
            cols = st.columns(len(top))
            for i, (iso, v) in enumerate(top):
                cols[i].button(
                    f"{cname(iso, lang)} \u00b7 {v:.0f}",
                    key=f"al_{a['id']}_{iso}",
                    on_click=lambda i2=iso: st.session_state.update(
                        {"country_sel": i2, "mode_sel": "brief"}))
            if len(a["hits"]) > 8:
                rest = " \u00b7 ".join(
                    f"{cname(i2, lang)} ({v2:.0f})" for i2, v2 in a["hits"][8:])
                st.caption(rest)


def assemble_report(df, briefs, country, indicator, lang):
    stats = get_stats(df, country, indicator)
    if not stats.get("available"):
        return {"status": "error", "error": f"No data for {country} / {indicator}"}
    qual = briefs.get(f"{country}|{indicator}|{lang}") or {}
    return {
        "status": "done" if qual else "done_numeric",
        "title": f"Country Risk Desk - {country} - {indicator}",
        "country": country, "indicator": indicator, "lang": lang,
        "category": stats.get("category", ""),
        "stats": stats,
        "web_context_available": False,
        "confidence": qual.get("confidence", "low"),
        "context": {"points": []},
        "outlook": qual.get("outlook", {"risks": [], "opportunities": [], "uncertainties": []}),
        "limitations": qual.get("limitations", []),
        "sources": qual.get("sources", []),
        "generated_at": qual.get("generated_at", ""),
    }


# ---- Main ----
df = get_df()
briefs = get_briefs()
today = datetime.date.today().isoformat()

with st.sidebar:
    st.markdown(f"### {t('params', 'en')} / {t('params', 'fr')}")
    lang = st.selectbox(
        "Langue / Language", ["fr", "en"],
        format_func=lambda x: "\U0001f1eb\U0001f1f7 Fran\u00e7ais" if x == "fr" else "\U0001f1ec\U0001f1e7 English")
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
             today, "deterministic", lang, ticks),
    unsafe_allow_html=True)

alerts = compute_alerts(df)

if mode == "brief":
    st.markdown(score_html(country, get_scores(), lang), unsafe_allow_html=True)
    st.markdown(rat.rating_card(country, lang), unsafe_allow_html=True)
    report = assemble_report(df, briefs, country, indicator, lang)
    html_all = report_html(report, lang)
    marker = '<div class="brief ctx">'
    if report.get("status") != "error" and marker in html_all:
        head, _, rest = html_all.partition(marker)
        with st.container():
            st.markdown('<div class="fused-flag"></div>', unsafe_allow_html=True)
            st.markdown(head, unsafe_allow_html=True)
            fig = line_chart(df, indicator, [country], lang)
            fig.update_layout(title=dict(text=f"{iname(indicator, lang)} - {cname(country, lang)}"))
            st.plotly_chart(fig, width="stretch")
        st.markdown(marker + rest, unsafe_allow_html=True)
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
            "Download data (CSV)" if lang == "en" else "Telecharger les donnees (CSV)",
            series.to_csv(index=False),
            f"country_risk_{country}_{indicator}.csv",
            "text/csv")
        _xb = io.BytesIO()
        series.to_excel(_xb, index=False)
        st.download_button(
            "Download data (Excel)" if lang == "en" else "Telecharger les donnees (Excel)",
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
