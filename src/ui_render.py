"""Rendu HTML des briefs (sections dynamiques) et formatage des statistiques."""
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


def evidence_html(items, lang, kind=""):
    if not items:
        return ""
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


def report_html(r, lang, chart=""):
    if r.get("status") == "error":
        return f'<div class="insufficient">{t("error", lang)} - {html.escape(str(r.get("error", "")))}</div>'
    out = r.get("outlook", {})
    big, deltas = fmt_stats(r.get("stats", {}), lang)
    risks = evidence_html(out.get("risks", []), lang, "risk")
    opps = evidence_html(out.get("opportunities", []), lang, "opp")
    st_ = r.get("stats") or {}
    proj_html = projections_html(r.get("country", ""), r.get("indicator", ""), lang,
                                 latest_value=st_.get("latest_value"),
                                 change_12m=st_.get("change_12m_pct"),
                                 unit=st_.get("unit", ""))
    sections = [("sec_constat",
                 f'<div class="bignum">{big}</div> <div class="deltaline">{deltas}</div>{chart}',
                 "data")]
    if out.get("risks"):
        sections.append(("sec_risks", risks, "risk"))
    if out.get("opportunities"):
        sections.append(("sec_opps", opps, "opp"))
    sections.append(("sec_proj", proj_html, "proj"))
    return "".join(
        f'<div class="brief {cls}"><h3>{i:02d} \u00b7 {t(key, lang)}</h3>{body}</div>'
        for i, (key, body, cls) in enumerate(sections, 1))
