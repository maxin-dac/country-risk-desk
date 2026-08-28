"""Theme global - Country Risk Desk.

Le CSS vit dans assets/theme.css (source unique, editable sans Python).
Ce module le charge, l'enveloppe dans <style> et expose masthead().
"""
import pathlib

_CSS_PATH = pathlib.Path(__file__).resolve().parent.parent / "assets" / "theme.css"

CSS = "<style>\n" + (_CSS_PATH.read_text(encoding="utf-8") if _CSS_PATH.exists() else "") + "\n</style>"


def masthead(n_countries, n_indicators, today, model, lang, ticks=None):
    fr = lang == "fr"
    chips = "".join([
        f'<span class="mh-chip"><i style="background:var(--accent)"></i>'
        f'{("Engine", "Moteur")[fr]} · {model}</span>',
        f'<span class="mh-chip"><i style="background:var(--accent2)"></i>'
        f'{("Search", "Recherche")[fr]} · Tavily / DuckDuckGo</span>',
        f'<span class="mh-chip"><i style="background:var(--gold)"></i>'
        f'{("Data", "Donnees")[fr]} · WB + IMF WEO + WGI</span>',
        f'<span class="mh-chip"><i style="background:var(--opp)"></i>'
        f'{("100% free demo", "Demo 100 % gratuite")[fr]}</span>',
    ])
    _tk = " · ".join(ticks) if ticks else ""
    tickline = (f'<div class="mh-ticks"><div class="mh-ticks-track">{_tk}'
                f'&nbsp;&nbsp;·&nbsp;&nbsp;{_tk}</div></div>'
                if ticks else "")
    cov = (("COVERAGE" if not fr else "COUVERTURE") + " : "
           + str(n_countries) + (" COUNTRIES" if not fr else " PAYS")
           + " · " + str(n_indicators)
           + (" INDICATORS" if not fr else " INDICATEURS")
           + (" · OFFICIAL SOURCES" if not fr else " · SOURCES OFFICIELLES"))
    return f"""
<div class="masthead">
  <div class="mh-eyebrow">MACRO-INTELLIGENCE // {today}</div>
  <div class="mh-title-block">
    <div class="mh-title-main">COUNTRY RISK DESK</div>
  </div>
  <div class="mh-chips">{chips}</div>
  <div class="mh-cov">{cov}</div>
  {tickline}
</div>"""
