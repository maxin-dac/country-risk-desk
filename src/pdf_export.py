import html
from io import BytesIO

from xhtml2pdf import pisa

from .i18n import COUNTRIES, INDICATORS, cname, iname, t


def _items(items, color, lang):
    if not items:
        return f'<p class="insufficient">{t("insufficient", lang)}</p>'
    out = []
    for it in items:
        ids = ", ".join(e.get("source_id", "") for e in it.get("evidence", []))
        q = "".join(f'<blockquote>“{html.escape(str(e.get("quote", "")))}”</blockquote>'
                    for e in it.get("evidence", []))
        out.append(f'<p><span class="chip" style="border-color:{color};color:{color}">'
                   f'{html.escape(ids)}</span> {html.escape(str(it.get("text", "")))}</p>{q}')
    return "".join(out)


def generate_pdf_bytes(r, lang="en"):
    if r.get("status") == "error":
        doc = f"<h1>{t('error', lang)}</h1><p>{html.escape(str(r.get('error', '')))}</p>"
    else:
        s, out = r.get("stats", {}), r.get("outlook", {})
        c, i = r.get("country", ""), r.get("indicator", "")
        c_label = f"{cname(c, lang)} ({c})" if c in COUNTRIES else c
        i_label = iname(i, lang) if i in INDICATORS else i
        big = (f"{s.get('latest_value', 0):.2f} {s.get('unit', '')} ({s.get('latest_date', '')})"
               if s.get("available") else t("insufficient", lang))
        deltas = " · ".join(x for x in [
            f"{s.get('change_3m_pct'):+.1f}% {t('d3', lang)}" if s.get("change_3m_pct") is not None else None,
            f"{s.get('change_12m_pct'):+.1f}% {t('d12', lang)}" if s.get("change_12m_pct") is not None else None,
            (f"{t('reg_median', lang)}: {s.get('regional_median'):.2f} {s.get('unit', '')} — "
             f"{t('pos_' + s.get('regional_position', 'near'), lang)}")
            if s.get("regional_median") is not None else None,
        ] if x)
        srcs = "".join(
            f'<li>[{html.escape(x["id"])}] <a href="{html.escape(x["url"])}">'
            f'{html.escape(x["title"])}</a> — {html.escape(x["domain"])}</li>'
            for x in r.get("sources", [])) or f"<li>{t('no_sources', lang)}</li>"
        uncer = "".join(f"<li>{html.escape(str(u))}</li>" for u in out.get("uncertainties", [])) \
            or f"<li>{t('insufficient', lang)}</li>"
        lims = "".join(f"<li>{html.escape(str(x))}</li>" for x in r.get("limitations", [])) or "<li>—</li>"
        ctx_points = r.get("context", {}).get("points", [])
        doc = f"""<!doctype html><html lang="{lang}"><head><meta charset="utf-8">
<style>
@page {{size: a4; margin: 1.8cm 1.6cm;}}
body {{font-family: Helvetica, Arial, sans-serif; font-size: 10px; color: #14201B; line-height: 1.5;}}
.mono, .eyebrow, h2, .chip, blockquote, footer {{font-family: Courier, monospace;}}
header {{border-bottom: 2px solid #14201B; padding-bottom: 6px; margin-bottom: 12px;}}
.eyebrow {{font-size: 8px; color: #5C6F66; text-transform: uppercase;}}
h1 {{font-size: 20px; text-transform: uppercase; margin: 4px 0 2px;}}
h2 {{font-size: 9px; color: #5C6F66; text-transform: uppercase; border-bottom: 1px solid #D8DED9; padding-bottom: 3px; margin-top: 14px;}}
.bignum {{font-family: Courier, monospace; font-size: 20px; color: #0E7490;}}
.chip {{font-size: 7px; border: 1px solid #C4CCC6; padding: 1px 5px; margin-right: 4px;}}
blockquote {{border-left: 2px solid #B98A1F; background-color: #FBF6E9; margin: 4px 0 8px; padding: 4px 8px; font-style: italic; font-size: 8px; color: #5C6F66;}}
.insufficient {{border: 1px dashed #B98A1F; color: #8A6A14; padding: 6px 10px; font-size: 8px; text-transform: uppercase;}}
a {{color: #0E7490;}}
ul {{margin: 6px 0; padding-left: 16px;}}
footer {{margin-top: 16px; border-top: 1px solid #D8DED9; padding-top: 6px; font-size: 7px; color: #5C6F66;}}
</style></head><body>
<header>
<div class="eyebrow">Macro-intelligence // PESTEL</div>
<h1>PESTEL — {html.escape(c_label)} — {html.escape(i_label)}</h1>
<div class="eyebrow">{t('generated', lang)} {html.escape(r.get('generated_at', ''))} · {t('confidence', lang)}: {html.escape(str(r.get('confidence', '')))}</div>
</header>
<h2>01 · {t('sec_constat', lang)}</h2>
<div class="bignum">{html.escape(big)}</div><p class="mono">{html.escape(deltas)}</p>
<h2>02 · {t('sec_context', lang)}</h2>{_items(ctx_points, '#B98A1F', lang)}
<h2>03 · {t('sec_risks', lang)}</h2>{_items(out.get('risks', []), '#C24135', lang)}
<h2>04 · {t('sec_opps', lang)}</h2>{_items(out.get('opportunities', []), '#1E8A5B', lang)}
<h2>05 · {t('uncertainties', lang)}</h2><ul>{uncer}</ul>
<h2>06 · {t('sec_sources', lang)}</h2><ul>{srcs}</ul>
<h2>{t('sec_limits', lang)}</h2><ul>{lims}</ul>
<footer>{t('fact_rule', lang)} · {t('not_advice', lang)}</footer>
</body></html>"""
    buf = BytesIO()
    pisa.CreatePDF(doc, dest=buf, encoding="utf-8")
    return buf.getvalue()