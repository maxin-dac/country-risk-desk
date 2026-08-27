"""IMF WEO projections (2027-2031): trajectory reading + divergence detection."""
import pathlib

import pandas as pd

PROJ_PATH = pathlib.Path("data/imf_projections.csv")

# Indicators for which a rise is a deterioration
HIGHER_IS_WORSE = {
    "Inflation", "Gen gov debt", "Gov debt", "External debt", "Debt service",
    "Unemployment", "Youth unemployment", "Gini", "Dependency ratio",
    "Commodity dependence",
}

_cache = {}


def _load():
    if "df" not in _cache:
        if PROJ_PATH.exists():
            _cache["df"] = pd.read_csv(PROJ_PATH)
        else:
            _cache["df"] = pd.DataFrame(
                columns=["country", "indicator", "year", "value", "unit"])
    return _cache["df"]


def get_series(country, indicator):
    df = _load()
    s = df[(df.country == country) & (df.indicator == indicator)]
    if s.empty:
        return {}, ""
    unit = str(s.iloc[0].get("unit", ""))
    return dict(zip(s.year.astype(int), s.value.astype(float))), unit


def _sparkline(series, unit):
    years = sorted(series)
    if len(years) < 2:
        return ""
    vals = [series[y] for y in years]
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    w, h = 560, 110
    xs = [10 + i * (w - 20) / (len(years) - 1) for i in range(len(years))]
    ys = [h - 18 - (v - lo) / span * (h - 36) for v in vals]
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in zip(xs, ys))
    dots = "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="#4cc9f0">'
        f'<title>{yr}: {v:.1f} {unit}</title></circle>'
        for x, y, yr, v in zip(xs, ys, years, vals))
    labels = "".join(
        f'<text x="{x:.1f}" y="{h - 4}" font-size="9" fill="#8fa8bd" '
        f'text-anchor="middle">{yr}</text>'
        for x, yr in zip(xs, years))
    return (f'<svg viewBox="0 0 {w} {h}" style="width:100%;max-width:640px">'
            f'<polyline points="{pts}" fill="none" stroke="#4cc9f0" '
            f'stroke-width="2"/>{dots}{labels}</svg>')


def projections_html(country, indicator, lang, latest_value=None,
                     change_12m=None, unit=""):
    series, punit = get_series(country, indicator)
    unit = unit or punit
    if not series:
        return ('<div class="insufficient">'
                + ("No IMF projection available for this indicator."
                   if lang == "en"
                   else "Pas de projection FMI disponible pour cet indicateur.")
                + '</div>')
    years = sorted(series)
    first, last = years[0], years[-1]
    v0, v1 = series[first], series[last]
    delta = v1 - v0
    rising_good = indicator not in HIGHER_IS_WORSE
    trend = "flat" if abs(delta) < 0.5 else ("up" if delta > 0 else "down")

    if lang == "fr":
        if trend == "flat":
            reading = f"Trajectoire FMI stable : autour de {v1:.1f} {unit} d'ici {last}."
        elif (delta > 0) == rising_good:
            reading = (f"Trajectoire FMI en amelioration : {v0:.1f} ({first}) "
                       f"-> {v1:.1f} {unit} ({last}).")
        else:
            reading = (f"Trajectoire FMI en deterioration : {v0:.1f} ({first}) "
                       f"-> {v1:.1f} {unit} ({last}).")
    else:
        if trend == "flat":
            reading = f"IMF trajectory stable: around {v1:.1f} {unit} by {last}."
        elif (delta > 0) == rising_good:
            reading = (f"IMF trajectory improving: {v0:.1f} ({first}) "
                       f"-> {v1:.1f} {unit} ({last}).")
        else:
            reading = (f"IMF trajectory deteriorating: {v0:.1f} ({first}) "
                       f"-> {v1:.1f} {unit} ({last}).")

    divergence = ""
    if change_12m is not None and abs(change_12m) > 2 and abs(delta) > 2:
        if (change_12m > 0) != (delta > 0):
            divergence = (
                " Divergence : la tendance recente (12 mois) s'inverse dans la "
                "trajectoire FMI - retournement attendu."
                if lang == "fr" else
                " Divergence: the recent 12-month trend reverses in the IMF "
                "trajectory - a turning point is expected.")

    chips = " · ".join(f"{yr}: {series[yr]:.1f}" for yr in years)
    return (f'<p class="kv">{reading}{divergence}</p>'
            f'<div class="deltaline" style="margin:.4rem 0">{chips} {unit}</div>'
            + _sparkline(series, unit))
