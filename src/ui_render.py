"""Rendu HTML des briefs (sections 01 a 07) et formatage des statistiques."""
import html
from src.i18n import t
from src.projections import projections_html


def fmt_stats(s, lang):
    if not s.get("available"):
        return t("insufficient", lang), ""
    big = (f"{s['latest_value']:.2f} {s.get('unit', '')} "
           f"<small style='font-size:.45em;color:var(--muted)'>({s['latest_date']})</small>")
    parts = []
    if s.get("change_3m_pct") is not None:
        a = "\u25b2" if s["change_3m_pct"] > 0 else "\u25bc" if s["change_3m_pct"] < 0 else "\u25c6"
        parts.append(f"{a} {s['change_3m_pct']:+.1f}% {t('d3', lang)}")
    if s.get("change_12m_pct") is not None:
        parts.append(f"{s['change_12m_pct']:+.1f}% {t('d12', lang)}")
    if s.get("regional_median") is not None:
        parts.append(f"{t('reg_median', lang)}: {s['regional_median']:.2f} {s.get('unit', '')} - "
                     f"{t('pos_' + s['regional_position'], lang)}")
    tr = s.get("trend_5y_norm")
    if tr is not None:
        from src.risk_scoring import HIGHER_IS_WORSE
        worse = s.get("indicator") in HIGHER_IS_WORSE
        if abs(tr) < 0.02:
            lab = "stable"
        elif (tr > 0) == worse:
            lab = "en deterioration" if lang == "fr" else "deteriorating"
        else:
            lab = "en amelioration" if lang == "fr" else "improving"
        parts.append(("Tendance 5 ans : " if lang == "fr" else "5-yr trend: ") + lab)
    return big, " \u00b7 ".join(parts)


def evidence_html(items, lang, kind="", empty_msg=None):
    if not items:
        return f'<div class="insufficient">{empty_msg or t("insufficient", lang)}</div>'
    out = []
    for it in items:
        if isinstance(it, str):
            out.append(f'<p class="kv">{html.escape(it)}</p>')
            continue
        if "text_en" in it and "text_fr" in it:
            text = html.escape(it["text_fr"] if lang == "fr" else it["text_en"])
            rule_tag = f'<span class="chip {kind}">rule:{it.get("rule_id", "")}</span>'
            out.append(f'<p class="kv">{rule_tag} {text}</p>')
        else:
            ids = html.escape(", ".join(e.get("source_id", "") for e in it.get("evidence", [])))
            text = html.escape(str(it.get("text", "")))
            out.append(f'<p class="kv"><span class="chip {kind}">{ids}</span> {text}</p>')
    return " ".join(out)


def _unc_text(u, lang):
    if isinstance(u, dict):
        return (u.get("text_fr" if lang == "fr" else "text_en")
                or u.get("text_en") or u.get("text_fr") or "")
    return str(u)


def report_html(r, lang, chart=""):
    if r.get("status") == "error":
        return f'<div class="insufficient">{t("error", lang)} - {html.escape(str(r.get("error", "")))}</div>'

    out = r.get("outlook", {})
    big, deltas = fmt_stats(r.get("stats", {}), lang)

    ctx = evidence_html(r.get("context", {}).get("points", []), lang)

    risks = evidence_html(
        out.get("risks", []), lang, "risk",
        empty_msg=("No risk signal triggered for this indicator (thresholds not crossed)."
                   if lang == "en" else
                   "Aucun signal de risque declenche pour cet indicateur (seuils non franchis)."))

    opps = evidence_html(
        out.get("opportunities", []), lang, "opp",
        empty_msg=("No opportunity signal triggered for this indicator (thresholds not crossed)."
                   if lang == "en" else
                   "Aucune opportunite majeure detectee pour cet indicateur (seuils non franchis)."))

    uncer_items = out.get("uncertainties", [])
    if uncer_items:
        uncer_html = " ".join(
            f"<li>{html.escape(_unc_text(u, lang))}</li>"
            for u in uncer_items
        )
    else:
        uncer_html = f"<li>{t('insufficient', lang)}</li>"

    srcs = " ".join(
        f'<li class="src">[{html.escape(s["id"])}] '
        f'<a href="{html.escape(s["url"])}" target="_blank">'
        f'{html.escape(s["title"])}</a> '
        f'<span class="chip">{html.escape(s["domain"])}</span></li>'
        for s in r.get("sources", [])
    ) or f'<div class="insufficient">{t("no_sources", lang)}</div>'

    lims = " ".join(
        f"<li>{html.escape(str(x))}</li>"
        for x in r.get("limitations", [])
    )
    lims_html = (f'<h3 style="margin-top:1rem">{t("sec_limits", lang)}</h3><ul>{lims}</ul>'
                 if lims else "")

    st_ = r.get("stats") or {}
    proj_html = projections_html(
        r.get("country", ""), r.get("indicator", ""), lang,
        latest_value=st_.get("latest_value"),
        change_12m=st_.get("change_12m_pct"),
        unit=st_.get("unit", ""))

    return f"""
<div class="brief data"><h3>01 \u00b7 {t('sec_constat', lang)}</h3>
<div class="bignum">{big}</div>  <div class="deltaline">{deltas}</div>{chart}</div>
<div class="brief ctx"><h3>02 \u00b7 {t('sec_context', lang)}</h3>{ctx}</div>
<div class="brief risk"><h3>03 \u00b7 {t('sec_risks', lang)}</h3>{risks}</div>
<div class="brief opp"><h3>04 \u00b7 {t('sec_opps', lang)}</h3>{opps}</div>
<div class="brief"><h3>05 \u00b7 {t('uncertainties', lang)}</h3><ul>{uncer_html}</ul></div>
<div class="brief proj"><h3>06 \u00b7 {t('sec_proj', lang)}</h3>{proj_html}</div>
<div class="brief"><h3>07 \u00b7 {t('sec_sources', lang)}</h3><ul>{srcs}</ul>{lims_html}</div>"""
