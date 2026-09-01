"""Notation souveraine : S&P / Moody's / Fitch (donnees publiees, CSV par agence).
Aucun calcul : chaque tuile affiche note + perspective + date telles que publiees."""
import csv
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"
_FILES = {"sp": "ratings_sp.csv", "mo": "ratings_moodys.csv", "fi": "ratings_fitch.csv"}
AGENCIES = [("sp", "S&P"), ("fi", "Fitch"), ("mo", "Moody's")]

_cache = None


def _load():
    global _cache
    if _cache is None:
        _cache = {}
        for key, fn in _FILES.items():
            p = DATA / fn
            if not p.exists():
                continue
            with open(p, encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    iso = (r.get("iso") or "").strip()
                    if not iso:
                        continue
                    row = _cache.setdefault(iso, {"country": r.get("country", "")})
                    row[key + "_r"] = (r.get("rating") or "").strip()
                    row[key + "_o"] = (r.get("outlook") or "").strip()
                    row[key + "_d"] = (r.get("date") or "").strip()
    return _cache


def country_ratings(iso):
    return _load().get(iso)


def country_rating(df, iso):
    return country_ratings(iso) or {}


def _out_cls(o):
    ol = (o or "").lower()
    return "withdrawn" if "withdrawn" in ol else ol


def rating_card(iso, lang):
    row = country_ratings(iso) or {}
    un = "Unrated" if lang == "en" else "Non class\u00e9"
    title = "Sovereign ratings" if lang == "en" else "Notation souveraine"
    tiles = []
    for key, name in AGENCIES:
        r = (row.get(key + "_r") or "").strip()
        o = (row.get(key + "_o") or "").strip()
        d = (row.get(key + "_d") or "").strip()
        if r:
            o_html = (f'<span class="ro out-{_out_cls(o)}">{o}</span>' if o
                      else '<span class="ro out-none">&mdash;</span>')
            tiles.append(
                f'<div class="rate-tile has"><div class="ag">{name}</div>'
                f'<div class="rt">{r}</div>{o_html}<div class="rd">{d}</div></div>')
        else:
            tiles.append(
                f'<div class="rate-tile no"><div class="ag">{name}</div>'
                f'<div class="rt none">{un}</div><div class="rd">&mdash;</div></div>')
    src = ("Source: Wikipedia - List of countries by credit rating (snapshot 2026-09-01)."
           if lang == "en" else
           "Source : Wikipedia - List of countries by credit rating (instantan\u00e9 2026-09-01).")
    return ('<div class="brief rating"><h3>' + title + '</h3>'
            '<div class="rate-grid">' + "".join(tiles) + '</div>'
            '<div class="rate-src">' + src + '</div></div>')
