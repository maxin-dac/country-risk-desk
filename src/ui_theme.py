"""Theme global - Country Risk Desk.
Le CSS vit dans assets/theme.css (source unique, editable sans Python).
Ce module le charge, l'enveloppe dans <style> et expose masthead().
"""
import pathlib as _pl

_CSS_PATH = _pl.Path(__file__).resolve().parent.parent / "assets" / "theme.css"
_raw = _CSS_PATH.read_text(encoding="utf-8") if _CSS_PATH.exists() else ""
CSS = "<style>\n" + _raw + "\n</style>"


def masthead(n_countries, n_indicators, today, model, lang, ticks=None):
    fr = lang == "fr"
    chips = " ".join([
        f'<span class="mh-chip"><i style="background:var(--accent)"></i>'
        f'{("Engine", "Moteur")[fr]} \u00b7 {model}</span>',
        f'<span class="mh-chip"><i style="background:var(--gold)"></i>'
        f'{("Data", "Données")[fr]} \u00b7 WB + IMF WEO + WGI</span>',
        f'<span class="mh-chip"><i style="background:var(--opp)"></i>'
        f'{("Ratings", "Notations")[fr]} \u00b7 8 agencies</span>',
        f'<span class="mh-chip"><i style="background:var(--opp)"></i>'
        f'{("100% free demo", "Demo 100 % gratuite")[fr]}</span>',
    ])
    _tk = " \u00b7 ".join(ticks) if ticks else ""
    tickline = (f'<div class="mh-ticks"><div class="mh-ticks-track">{_tk}'
                f'&nbsp;&nbsp;\u00b7&nbsp;&nbsp;{_tk}</div></div>'
                if ticks else "")
    cov = (("COVERAGE" if not fr else "COUVERTURE") + " : "
           + str(n_countries) + (" COUNTRIES" if not fr else " PAYS")
           + " \u00b7 " + str(n_indicators)
           + (" INDICATORS" if not fr else " INDICATEURS")
           + (" \u00b7 OFFICIAL SOURCES" if not fr else " \u00b7 SOURCES OFFICIELLES"))
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
