import html

from src.i18n import t

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

def report_html(r, lang, chart=""):
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
<div class="bignum">{big}</div><div class="deltaline">{deltas}</div>{chart}</div>
<div class="brief ctx"><h3>02 · {t('sec_context', lang)}</h3>{ctx}</div>
<div class="brief risk"><h3>03 · {t('sec_risks', lang)}</h3>{risks}</div>
<div class="brief opp"><h3>04 · {t('sec_opps', lang)}</h3>{opps}</div>
<div class="brief"><h3>05 · {t('uncertainties', lang)}</h3><ul>{uncer}</ul></div>
<div class="brief"><h3>06 · {t('sec_sources', lang)}</h3><ul>{srcs}</ul>{lims_html}</div>"""
