import datetime, html, json, pathlib
import streamlit as st

from src import config
from src.csv_loader import get_stats, load_csv
from src.graph import build_agent
from src.i18n import INDICATORS, cname, iname, t
from src.pdf_export import generate_pdf_bytes
from src.ui_theme import CSS, masthead

st.set_page_config(page_title="PESTEL Risk Desk", page_icon="\U0001F6F0", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_df():
    return load_csv(config.CSV_PATH)

@st.cache_data(show_spinner=False)
def get_briefs():
    p = pathlib.Path(config.BRIEFS_PATH)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

@st.cache_resource(show_spinner=False)
def get_agent():
    return build_agent(get_df())

@st.cache_data(ttl=86400, show_spinner=False)
def _live(country, indicator, lang, _day):
    return get_agent().invoke({"country": country, "indicator": indicator,
                               "lang": lang}).get("final_report", {})

def live_report(country, indicator, lang):
    day = datetime.date.today().isoformat()
    r = _live(country, indicator, lang, day)
    if r.get("status") != "done":
        _live.clear(country, indicator, lang, day)
    return r

def assemble_report(df, briefs, country, indicator, lang):
    stats = get_stats(df, country, indicator)
    if not stats.get("available"):
        return {"status": "error", "error": f"No CSV data for {country} / {indicator}"}
    qual = briefs.get(f"{country}|{indicator}|{lang}") or {}
    return {
        "status": "done" if qual else "done_numeric",
        "title": f"PESTEL — {country} — {indicator}",
        "country": country, "indicator": indicator, "lang": lang,
        "category": stats.get("category", ""), "stats": stats,
        "web_context_available": qual.get("web_context_available", False),
        "confidence": qual.get("confidence", "low"),
        "context": qual.get("context", {"points": []}),
        "outlook": qual.get("outlook", {"risques": [], "opportunities": [], "uncertainties": []}),
        "limitations": qual.get("limitations", []),
        "sources": qual.get("sources", []),
        "generated_at": qual.get("generated_at", ""),
    }

def fmt_stats(s, lang):
    if not s.get("available"):
        return t("insufficient", lang), ""
    big = (f"{s['latest_value']:.2f} {s.get('unit', '')} "
           f"<small style='font-size:.45em;color:var(--muted)'>({s['latest_date']})</small>")
    parts = []
    if s.get("change_3m_pct") is not None:
        a = "▲" if s["change_3m_pct"] > 0 else "▼" if s["change_3m_pct"] < 0 else "◆"
        parts.append(f"{a} {s['change_3m_pct']:+.1f}% {t('d3', lang)}")
    if s.get("change_12m_pct") is not None:
        parts.append(f"{s['change_12m_pct']:+.1f}% {t('d12', lang)}")
    if s.get("regional_median") is not None:
        parts.append(f"{t('reg_median', lang)}: {s['regional_median']:.2f} {s.get('unit', '')} — "
                     f"{t('pos_' + s['regional_position'], lang)}")
    return big, " · ".join(parts)

def evidence_html(items, lang, kind=""):
    if not items:
        return f'<div class="insufficient">{t("insufficient", lang)}</div>'
    out = []
    for it in items:
        ids = html.escape(", ".join(e.get("source_id", "") for e in it.get("evidence", [])))
        text = html.escape(str(it.get("text", "")))
        quotes = "".join(f'<div class="evidence">“{html.escape(str(e.get("quote", "")))}”</div>'
                         for e in it.get("evidence", []))
        out.append(f'<p class="kv"><span class="chip {kind}">{ids}</span>{text}</p>{quotes}')
    return "".join(out)

def report_html(r, lang):
    if r.get("status") == "error":
        return f'<div class="insufficient">{t("error", lang)} — {html.escape(str(r.get("error", "")))}</div>'
    out = r.get("outlook", {})
    big, deltas = fmt_stats(r.get("stats", {}), lang)
    ctx = evidence_html(r.get("context", {}).get("points", []), lang)
    risks = evidence_html(out.get("risks", []), lang, "risk")
    opps = evidence_html(out.get("opportunities", []), lang, "opp")
    uncer = "".join(f"<li>{html.escape(str(u))}</li>" for u in out.get("uncertainties", [])) \
        or f"<li>{t('insufficient', lang)}</li>"
    srcs = "".join(
        f'<li class="src">[{html.escape(s["id"])}] <a href="{html.escape(s["url"])}" target="_blank">'
        f'{html.escape(s["title"])}</a> <span class="chip">{html.escape(s["domain"])}</span></li>'
        for s in r.get("sources", [])) or f'<div class="insufficient">{t("no_sources", lang)}</div>'
    lims = "".join(f"<li>{html.escape(str(x))}</li>" for x in r.get("limitations", []))
    lims_html = f'<h3 style="margin-top:1rem">{t("sec_limits", lang)}</h3><ul>{lims}</ul>' if lims else ""
    return f"""
<div class="brief data"><h3>01 · {t('sec_constat', lang)}</h3>
<div class="bignum">{big}</div><div class="deltaline">{deltas}</div></div>
<div class="brief ctx"><h3>02 · {t('sec_context', lang)}</h3>{ctx}</div>
<div class="brief risk"><h3>03 · {t('sec_risks', lang)}</h3>{risks}</div>
<div class="brief opp"><h3>04 · {t('sec_opps', lang)}</h3>{opps}</div>
<div class="brief"><h3>05 · {t('uncertainties', lang)}</h3><ul>{uncer}</ul></div>
<div class="brief"><h3>06 · {t('sec_sources', lang)}</h3><ul>{srcs}</ul>{lims_html}</div>"""

df = get_df()
briefs = get_briefs()
today = datetime.date.today().isoformat()

with st.sidebar:
    st.markdown(f"### {t('params', 'en')} / {t('params', 'fr')}")
    lang = st.selectbox("Langue / Language", ["fr", "en"],
                        format_func=lambda x: "🇫🇷 Français" if x == "fr" else "🇬 English")
    country = st.selectbox(t("country", lang), sorted(df.country.unique()),
                           format_func=lambda c: f"{cname(c, lang)} ({c})")
    inds = sorted(df[df.country == country].indicator.unique())
    indicator = st.selectbox(t("indicator", lang), inds,
                             format_func=lambda x: iname(x, lang) if x in INDICATORS else x)
    go_live = st.button(t("live", lang))

sel_key = f"{country}|{indicator}|{lang}"

if go_live:
    if not (config.TAVILY_API_KEY and config.LLM_API_KEY):
        st.warning(t("no_keys", lang))
    else:
        with st.spinner(t("searching", lang)):
            st.session_state.live = {"key": sel_key,
                                     "report": live_report(country, indicator, lang)}
        st.rerun()

live = st.session_state.get("live")
is_live = bool(live and live["key"] == sel_key)
report = live["report"] if is_live else assemble_report(df, briefs, country, indicator, lang)

ticks = [f"<b>{c}</b> {cname(c, lang).upper()}" for c in sorted(df.country.unique())[:16]]
st.markdown(masthead(df.country.nunique(), df.indicator.nunique(), today,
                     config.LLM_MODEL, lang, ticks), unsafe_allow_html=True)

if is_live:
    st.caption(t("live_done", lang))
st.markdown(report_html(report, lang), unsafe_allow_html=True)


if report.get("status") != "error":
    try:
        st.download_button(t("export", lang), generate_pdf_bytes(report, lang),
                           f"pestel_{country}_{indicator}.pdf".lower(), "application/pdf")
    except Exception as e:
        st.warning(f"{t('pdf_fail', lang)}: {e}")