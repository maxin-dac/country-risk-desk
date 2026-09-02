# API interne - Country Risk Desk

Reference generee automatiquement : `python scripts/build_docs.py`.

## `src.csv_loader`

Chargement et statistiques des series macro (CSV unique).

Fonctions publiques:
    load_csv(path): DataFrame valide et type (date, valeur, codes).
    get_stats(df, country, indicator): derniere valeur (+date), variations
        3/12 mois, mediane regionale, position relative, tendance 5 ans.
    format_stats(stats): serialization texte (logs, exports).

### `format_stats(st_)`

Serialiser les statistiques en texte lisible (logs, exports).

### `get_stats(df, country, indicator)`

Statistiques du couple pays/indicateur.

Returns:
    dict: latest_value/latest_date, change_3m_pct, change_12m_pct,
    regional_median, regional_position, trend_5y_norm (pente 5 ans
    normalisee par la mediane), unit_display.

### `load_csv(path)`

Lire le CSV macro, valider les colonnes requises, typer date/valeur.


## `src.alerts`

Moteur d'alertes : règles de seuils déterministes + génération de risques/opportunités.

### `compute_alerts(df)`

Bandeau d'alertes global — version défensive (ne plante jamais).

### `generate_outlook(stats)`

_Pas de docstring._


## `src.risk_scoring`

_Import impossible: No module named 'src.risk_scoring'_

## `src.projections`

IMF WEO projections (2027-2031): trajectory reading + divergence detection.

### `get_series(country, indicator)`

_Pas de docstring._

### `projections_html(country, indicator, lang, change_12m=None, unit='')`

_Pas de docstring._


## `src.dashboard`

Dashboard global : notations souveraines (donnees factuelles des agences).

### `grade_summary(df, layer)`

_Pas de docstring._

### `rating_distribution(layer, lang)`

_Pas de docstring._

### `world_map_ratings(layer, lang)`

_Pas de docstring._


## `src.watchlist`

_Import impossible: No module named 'src.watchlist'_

## `src.plot_theme`

Theme centralise pour tous les graphiques Plotly.

- Fond transparent, sans contour
- Unites affichees dans le titre du visuel (pas de titres d'axes)

### `apply_theme(fig, title='', unit=None, y_indicator=None)`

Theme transparent + unite dans le titre.

### `unit_suffix(indicator, lang='en')`

_Pas de docstring._


## `src.compare`

Mode comparaison - graphiques Plotly et tableau croise.

### `latest_pivot(df, countries, lang, latest=None)`

_Pas de docstring._

### `line_chart(df, indicator, countries, lang)`

_Pas de docstring._

### `positioning_scatter(df, countries, lang, latest=None)`

_Pas de docstring._

### `render_compare(df, countries, lang)`

_Pas de docstring._


## `src.web_search`

_Import impossible: No module named 'src.web_search'_

## `src.i18n`

Internationalisation FR/EN: pays, indicateurs, libelles UI.

RISK_ORDER est la liste blanche des indicateurs du cadre de risque
(source de verite partagee par le brief, la comparaison et les exports).
UNITS/plot_theme portent les unites affichees dans les titres de visuels.

### `cname(iso3, lang='en')`

_Pas de docstring._

### `iname(key, lang='en')`

_Pas de docstring._

### `t(key, lang='en')`

_Pas de docstring._

### `uname(unit, lang)`

_Pas de docstring._


## `src.ui_render`

Rendu HTML des briefs (sections 01 a 04) et formatage des statistiques.

### `evidence_html(items, lang, kind='', empty_msg=None)`

_Pas de docstring._

### `fmt_stats(s, lang)`

_Pas de docstring._

### `report_html(r, lang, chart='')`

_Pas de docstring._

