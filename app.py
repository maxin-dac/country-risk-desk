import datetime, json, pathlib
import streamlit as st

from src import config
from src.csv_loader import get_stats, load_csv
from src.graph import build_report
from src.alerts import compute_alerts
from src.compare import line_chart, render_compare
from src.i18n import INDICATORS, cname, iname, t
from src.pdf_export import generate_pdf_bytes
from src.ui_render import report_html
from src.ui_theme import CSS, masthead

st.set_page_config(page_title="Country Risk Desk", page_icon="🛰", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)
st.markdown("""<style>
[data-testid="stVerticalBlock"] > div:has(.alerts-flag){display:none}
[data-testid="stVerticalBlock"] > div:has(.alerts-flag) + div{
  background:rgba(220,38,38,.10);
  border:1px solid rgba(220,38,38,.35);
  border-radius:.75rem;
  padding:.25rem .75rem;
}
</style>""", unsafe_allow_html=True)

st.markdown("""<style>
section[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#10202e 0%,#0b1620 100%);
  border-right:1px solid rgba(76,201,240,.22);
}
section[data-testid="stSidebar"] > div{background:transparent}
section[data-testid="stSidebar"] h3{
  color:#e6edf3;
  border-bottom:2px solid rgba(76,201,240,.35);
  padding-bottom:.45rem;
  margin-bottom:.6rem;
}
section[data-testid="stSidebar"] label{
  text-transform:uppercase;
  letter-spacing:.08em;
  font-size:.68rem;
  font-weight:700;
  color:#8fd0f4;
}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div,
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] > div{
  background:rgba(255,255,255,.06);
  border:1px solid rgba(159,179,200,.35);
  border-radius:.55rem;
}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div:focus-within,
section[data-testid="stSidebar"] [data-testid="stMultiSelect"] > div:focus-within{
  border-color:#4cc9f0;
}
.stButton button{
  border-radius:.55rem;
  border:1px solid rgba(76,201,240,.4);
  background:rgba(76,201,240,.08);
  color:#d7e2ec;
  font-weight:600;
}
.stButton button:hover{background:rgba(76,201,240,.18);border-color:#4cc9f0}
::-webkit-scrollbar{width:8px;height:8px}
::-webkit-scrollbar-thumb{background:rgba(159,179,200,.35);border-radius:4px}
h3{color:#cfe8f7}
</style>""", unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def get_df():
    return load_csv(config.CSV_PATH)


@st.cache_data(show_spinner=False)
def get_briefs():
    p = pathlib.Path(config.BRIEFS_PATH)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


@st.cache_data(ttl=86400, show_spinner=False)
def _live(country, indicator, lang, _day):
    return build_report(country, indicator, lang)


def live_report(country, indicator, lang):
    day = datetime.date.today().isoformat()
    r = _live(country, indicator, lang, day)
    if r.get("status") != "done":
        _live.clear()
    return r


def assemble_report(df, briefs, country, indicator, lang):
    stats = get_stats(df, country, indicator)
    if not stats.get("available"):
        return {"status": "error", "error": f"No data for {country} / {indicator}"}
    qual = briefs.get(f"{country}|{indicator}|{lang}") or {}
    return {
        "status": "done" if qual else "done_numeric",
        "title": f"Country Risk Desk - {country} - {indicator}",
        "country": country, "indicator": indicator, "lang": lang,
        "category": stats.get("category", ""), "stats": stats,
        "web_context_available": qual.get("web_context_available", False),
        "confidence": qual.get("confidence", "low"),
        "context": qual.get("context", {"points": []}),
        "outlook": qual.get("outlook", {"risks": [], "opportunities": [], "uncertainties": []}),
        "limitations": qual.get("limitations", []),
        "sources": qual.get("sources", []),
        "generated_at": qual.get("generated_at", ""),
    }


df = get_df()
briefs = get_briefs()
today = datetime.date.today().isoformat()

with st.sidebar:
    st.markdown(f"### {t('params', 'en')} / {t('params', 'fr')}")
    lang = st.selectbox("Langue / Language", ["fr", "en"],
                        format_func=lambda x: "🇫🇷 Français" if x == "fr" else "🇬🇧 English")
    mode = st.radio(t("mode", lang), ["brief", "compare"], horizontal=True,
                    format_func=lambda m: t("mode_brief", lang) if m == "brief" else t("mode_compare", lang))
    if mode == "brief":
        country = st.selectbox(t("country", lang), sorted(df.country.unique()),
                               format_func=lambda c: f"{cname(c, lang)} ({c})", key="country_sel")
        inds = sorted(df[df.country == country].indicator.unique())
        indicator = st.selectbox(t("indicator", lang), inds,
                                 format_func=lambda x: iname(x, lang) if x in INDICATORS else x)
        go_live = st.button(t("live", lang))
    else:
        allc = sorted(df.country.unique())
        countries = st.multiselect(t("countries_sel", lang), allc,
                                   default=[c for c in ("MAR", "USA", "DEU") if c in allc],
                                   max_selections=12,
                                   format_func=lambda c: f"{cname(c, lang)} ({c})")

if mode == "brief":
    sel_key = f"{country}|{indicator}|{lang}"
    if go_live:
        if not config.TAVILY_API_KEY:
            st.warning("Tavily API key missing - only quantitative data available." if lang == "en"
                       else "Cle API Tavily manquante - seules les donnees quantitatives sont disponibles.")
        with st.spinner(t("searching", lang)):
            st.session_state.live = {"key": sel_key,
                                     "report": live_report(country, indicator, lang)}
        st.rerun()

ticks = [f"<b>{c}</b> {cname(c, lang).upper()}" for c in sorted(df.country.unique())[:16]]
st.markdown(masthead(df.country.nunique(), df.indicator.nunique(), today,
                     "deterministic", lang, ticks), unsafe_allow_html=True)

alerts = compute_alerts(df)
if alerts:
    st.markdown('<div class="alerts-flag"></div>', unsafe_allow_html=True)
    with st.expander(f"⚠ {t('alerts_title', lang)} - {sum(len(a['hits']) for a in alerts)}", expanded=False):
        for a in alerts:
            label = a["fr"] if lang == "fr" else a["en"]
            st.markdown(f"**{label}** · {len(a['hits'])}")
            top = a["hits"][:8]
            cols = st.columns(len(top))
            for i, (iso, v) in enumerate(top):
                cols[i].button(f"{cname(iso, lang)} · {v:.0f}", key=f"al_{a['id']}_{iso}",
                               on_click=lambda i2=iso: st.session_state.update({"country_sel": i2}))
            if len(a["hits"]) > 8:
                rest = " · ".join(f"{cname(i2, lang)} ({v2:.0f})" for i2, v2 in a["hits"][8:])
                st.caption(rest)

if mode == "brief":
    live = st.session_state.get("live")
    is_live = bool(live and live["key"] == sel_key)
    report = live["report"] if is_live else assemble_report(df, briefs, country, indicator, lang)
    if is_live:
        st.caption(t("live_done", lang))
    html_all = report_html(report, lang)
    marker = '<div class="brief ctx">'
    if report.get("status") != "error" and marker in html_all:
        head, _, rest = html_all.partition(marker)
        st.markdown(head, unsafe_allow_html=True)
        fig = line_chart(df, indicator, [country], lang)
        fig.update_layout(title=dict(text=f"{iname(indicator, lang)} - {cname(country, lang)}"))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(marker + rest, unsafe_allow_html=True)
    else:
        st.markdown(html_all, unsafe_allow_html=True)
    if report.get("status") != "error":
        try:
            st.download_button(t("export", lang), generate_pdf_bytes(report, lang),
                               f"pestel_{country}_{indicator}.pdf".lower(), "application/pdf")
        except Exception as e:
            st.warning(f"{t('pdf_fail', lang)}: {e}")
else:
    render_compare(df, countries, lang)

# ==========================================
# SIDEBAR FOOTER : Copyright & Social Links
# ==========================================
st.sidebar.markdown("""
<div style="
    margin-top: 3rem; 
    padding-top: 1.5rem; 
    border-top: 1px solid rgba(143, 208, 244, 0.2); 
    text-align: center; 
    color: #8fd0f4; 
    font-size: 0.75rem; 
    font-family: sans-serif;
">
    <p style="margin: 0 0 0.75rem 0; font-weight: 600; letter-spacing: 0.05em; opacity: 0.9;">© 2026 Maxime NDACLEU</p>
    <div style="display: flex; justify-content: center; gap: 1.25rem;">
        <a href="https://github.com/maxin-dac" target="_blank" style="color: #8fd0f4; text-decoration: none;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
        </a>
        <a href="https://www.linkedin.com/in/maximendacleu" target="_blank" style="color: #8fd0f4; text-decoration: none;">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)
