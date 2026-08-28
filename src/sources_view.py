"""Vue "resultats de recherche" des sources officielles (section 02).

Au lieu d'extraits bruts parfois decontextualises, presente chaque source
comme un resultat de moteur de recherche : titre + mots indexes + snippet
propre (si qualite suffisante) + lien a suivre.
"""
import html
import re

# Vocabulaire de risque utilise pour indexer les sources
RISK_VOCAB = [
    "inflation", "debt", "deficit", "fiscal", "reserves", "growth", "recession",
    "currency", "exchange rate", "balance of payments", "debt service", "default",
    "governance", "corruption", "political stability", "unemployment", "commodity",
    "credit rating", "austerity", "subsidies", "elections", "IMF", "World Bank",
    "outlook", "projection", "monetary policy", "interest rate", "exports", "imports",
]


def keywords(text, limit=6):
    low = (text or "").lower()
    return [w for w in RISK_VOCAB if w in low][:limit]


def clean_snippet(text, max_chars=240):
    """Snippet propre, ou '' si le texte est de mauvaise qualite."""
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(t) < 80:
        return ""
    low = t.lower()
    if low.startswith("image") or "no data" in low or "key data documentation" in low:
        return ""
    if sum(c.isalpha() for c in t) / max(1, len(t)) < 0.55:
        return ""
    m = re.match(r"(.{110,%d}?[.!?])\s" % max_chars, t + " ")
    s = m.group(1) if m else t[:max_chars]
    return s + ("..." if len(t) > len(s) else "")


def results_html(sources, lang):
    if not sources:
        return ('<div class="insufficient">'
                + ("No verified official source for this indicator."
                   if lang == "en"
                   else "Aucune source officielle verifiee pour cet indicateur.")
                + '</div>')
    out = []
    for s in sources:
        sid = html.escape(str(s.get("id", "")))
        title = html.escape(str(s.get("title", "")).strip()) or "(sans titre)"
        url = html.escape(str(s.get("url", "#")))
        dom = html.escape(str(s.get("domain", "")))
        raw = s.get("snippet") or s.get("content") or s.get("text") or ""
        snip = clean_snippet(raw)
        words = keywords(title + " " + str(raw))
        words_html = "".join(
            f'<span class="chip">{html.escape(w)}</span>' for w in words)
        out.append(
            '<div class="sr-item">'
            f'<div class="sr-line"><span class="chip">{sid}</span>'
            f'<a class="sr-title" href="{url}" target="_blank">{title}</a>'
            f'<span class="chip">{dom}</span></div>'
            + (f'<div class="sr-words">{words_html}</div>' if words_html else '')
            + (f'<p class="sr-snip">{html.escape(snip)}</p>' if snip else '')
            + '</div>')
    return "".join(out)
