# -*- coding: utf-8 -*-
"""Notation souveraine - donnees officielles des agences, telles quelles.

Source : Wikipedia, "List of countries by credit rating" (instantane 2026-09-01).
Aucun calcul, aucun proxy : chaque cellule = note / perspective / date publiees.
"""
import csv
import pathlib

DATA = pathlib.Path(__file__).resolve().parent.parent / "data" / "agency_ratings.csv"

AGENCIES = [
    ("sp", "S&P"),
    ("fi", "Fitch"),
    ("mo", "Moody's"),
    ("db", "DBRS Morningstar"),
    ("sc", "Scope Ratings"),
    ("jc", "JCR"),
    ("cc", "China Chengxin"),
    ("ce", "CareEdge"),
]

_OUT_FR = {"Negative": "Negative", "Positive": "Positive", "Stable": "Stable",
           "Withdrawn": "Retiree", "Ratings withdrawn": "Retiree"}

_cache = None


def _load():
    global _cache
    if _cache is None:
        _cache = {}
        if DATA.exists():
            with open(DATA, encoding="utf-8") as f:
                for r in csv.DictReader(f):
                    _cache[r["iso"]] = r
    return _cache


def country_ratings(iso):
    return _load().get(iso)


def _out(v, lang):
    v = (v or "").strip()
    if not v:
        return None
    if lang == "fr":
        return _OUT_FR.get(v, v)
    return v


def rating_card(iso, lang):
    row = country_ratings(iso) or {}
    un = "Unrated" if lang == "en" else "Non classe"
    title = "Sovereign ratings" if lang == "en" else "Notation souveraine"
    tiles = []
    for key, name in AGENCIES:
        r = (row.get(key + "_r") or "").strip()
        o = (row.get(key + "_o") or "").strip()
        d = (row.get(key + "_d") or "").strip()
        if r:
            o_txt = _out(o, lang)
            o_cls = (o or "none").lower().replace(" ", "").replace("ratingswithdrawn", "withdrawn")
            o_html = ('<span class="ro out-' + o_cls + '">' + o_txt + "</span>"
                      if o_txt else '<span class="ro out-none">&mdash;</span>')
            tiles.append(
                '<div class="rate-tile has"><div class="ag">' + name + "</div>"
                '<div class="rt">' + r + "</div>" + o_html +
                '<div class="rd">' + d + "</div></div>")
        else:
            tiles.append(
                '<div class="rate-tile no"><div class="ag">' + name + "</div>"
                '<div class="rt none">' + un + '</div><div class="rd">&mdash;</div></div>')
    src = ("Source: Wikipedia &mdash; List of countries by credit rating "
           "(snapshot 2026-09-01). Ratings, outlooks and dates as published by each agency."
           if lang == "en" else
           "Source : Wikip&eacute;dia &mdash; List of countries by credit rating "
           "(instantan&eacute; 2026-09-01). Notes, perspectives et dates telles que "
           "publi&eacute;es par chaque agence.")
    return ('<div class="brief rating"><h3>' + title + "</h3>"
            '<div class="rate-grid">' + "".join(tiles) + "</div>"
            '<div class="rate-src">' + src + "</div></div>")


def country_rating(df, iso):
    """Alias pour app.py : dict de notations du pays (jamais None)."""
    return country_ratings(iso) or {}
