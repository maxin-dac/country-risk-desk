# Construction du .pbix (10 minutes, zero DAX)

1. Power BI Desktop > Obtenir les donnees > Texte/CSV : importer les 10 tables pbi_*.csv.
2. Locale d'import : en-US (Options > Parametres regionaux). Formats dd/MM/yyyy sur les colonnes de date.
3. Ne creer AUCUNE relation manuelle : auto-detection par noms de colonnes (iso3, indicator). Verifier dans la vue Modele.
4. Glisser-deposer, rien d'autre :

| Page | Visuel | Champs |
|---|---|---|
| Lecture pays | slicers | pbi_countries[country_fr], pbi_indicators[label_fr] |
| | cartes | pbi_latest[latest_value] (Somme), [latest_date] (Max), [change_12m_pct] (Somme), [trend_sens_fr] (Premier), [position_fr] (Premier) |
| | courbe historique | pbi_history[date] + [value] (Somme) |
| | courbe projections | pbi_projections[year] + [value] (Somme) |
| | table risques | pbi_signals[label_fr], filtre visuel side = risk |
| | table opportunites | pbi_signals[label_fr], filtre visuel side = opportunity |
| Comparaison | slicer pays multi | pbi_countries[country_fr] |
| | matrice | lignes country_fr, colonnes label_fr, valeurs latest_value |
| | nuage de points | pbi_position[gdp_growth_latest] / [inflation_latest], details iso3 |
| | bar signaux | pbi_counts[iso3] + [n_total] |
| Vue globale | slicer agence | pbi_ratings_long[agency] |
| | carte choroplethe | lieu pbi_countries[country_en], legende pbi_ratings_long[category_fr] |
| | bar distribution | pbi_ratings_long[category_fr], nombre de iso3 |
| | table divergences | pbi_ratings_wide, filtre visuel has_divergence = 1 |
| Suivi seuils | matrice | lignes pbi_countries[country_fr], colonnes pbi_signals[rule_id], valeurs Nombre de rule_id |
| | slicers | pbi_signals[side], pbi_indicators[label_fr] |

Un canvas blanc = CSV vide ou slicer hors page : verifiable en une ligne de pandas, jamais un mystere.
