# Jumeau Power BI / Power BI twin

Modele en etoile genere par `scripts/export_powerbi.py`
(source de verite : `data/` + `src/alerts.py` + `src/i18n.py`).

| Table | Grain | Role |
|---|---|---|
| dim_country | 1 ligne / economie | noms EN/FR, region |
| dim_indicator | 1 ligne / indicateur | libelles, unite, pilier, sens, cadre de risque |
| dim_rules | 1 ligne / regle | operateur + seuil, libelles EN/FR (miroir de alerts.py) |
| dim_rating | 1 ligne / agence x pays | notation, perspective, date |
| fact_indicators | 1 ligne / pays x indicateur x date | valeurs publiees |
| fact_projections | 1 ligne / pays x indicateur x annee | projections FMI 2027-2031 |

Relations Power BI :
- fact_indicators -> dim_country (country/iso3), dim_indicator (indicator)
- fact_projections -> dim_country, dim_indicator
- dim_rating -> dim_country
- dim_rules -> dim_indicator

Regeneration : `python scripts/export_powerbi.py` apres chaque refresh mensuel.
Philosophie : aucun score - les seuils de dim_rules sont exactement ceux de `src/alerts.py`.
