"""Vue "resultats de recherche" des sources officielles (section 02)."""
import html
import re

# (motif de matching, label EN, label FR) - ordre = priorite
VOCAB = [
    ("debt service", "debt service", "service de la dette"),
    ("debt", "debt", "dette"),
    ("deficit", "deficit", "deficit"),
    ("fiscal", "fiscal", "budgetaire"),
    ("inflation", "inflation", "inflation"),
    ("reserves", "reserves", "reserves"),
    ("recession", "recession", "recession"),
    ("growth", "growth", "croissance"),
    ("exchange rate", "exchange rate", "taux de change"),
    ("currency", "currency", "monnaie"),
    ("balance of payments", "balance of payments", "balance des paiements"),
    ("default", "default", "defaut"),
    ("governance", "governance", "gouvernance"),
    ("corruption", "corruption", "corruption"),
    ("political stability", "political stability", "stabilite politique"),
    ("unemployment", "unemployment", "chomage"),
    ("commodity", "commodity", "matieres premieres"),
    ("credit rating", "credit rating", "notation"),
    ("austerity", "austerity", "austerite"),
    ("subsid", "subsidies", "subventions"),
    ("election", "elections", "elections"),
    ("imf", "IMF", "FMI"),
    ("world bank", "World Bank", "Banque mondiale"),
    ("outlook", "outlook", "perspectives"),
    ("projection", "projection", "projections"),
    ("monetary policy", "monetary policy", "politique monetaire"),
    ("interest rate", "interest rate", "taux d'interet"),
    ("export", "exports", "exportations"),
    ("import", "imports", "importations"),
]


def keywords(text, lang="en", limit=6):
    low = (text or "").lower()
    out = []
    for motif, en, fr in VOCAB:
        if motif in low:
            out.append(fr if lang == "fr" else en)
        if len(out) >= limit:
            break
    return out


def clean_snippet(text, max_chars=240):
    t = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(t) < 80:
        return ""
    low = t.lower()
    if low.startswith("image") or "no data" in low or "key data documentation" in low:
        return ""
    if sum(c.isalpha() for c in t) / max(1, len(t)) < 0.55:
        return ""
    m = re.match(r"(.{110,%d}?[.!?])\s" % max_chars, t + " ")
    sn = m.group(1) if m else t[:max_chars]
    return sn + ("..." if len(t) > len(sn) else "")


def results_html(sources, lang):
    if not sources:
        return ('<div class="insufficient">'
                + ("No verified official source for this indicator."
                   if lang == "en"
                   else "Aucune source officielle verifiee pour cet indicateur.")
                + '</div>')
    out = []
    for src in sources:
        sid = html.escape(str(src.get("id", "")))
        title = html.escape(str(src.get("title", "")).strip()) or "(sans titre)"
        url = html.escape(str(src.get("url", "#")))
        dom = html.escape(str(src.get("domain", "")))
        raw = src.get("snippet") or src.get("content") or src.get("text") or ""
        snip = clean_snippet(raw)
        words = keywords(title + " " + str(raw), lang)
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
