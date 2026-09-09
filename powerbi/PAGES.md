# Construction des 4 pages (Power BI Desktop)

Preparation commune :
- Dans dim_country, mettre la colonne name_en en categorie de donnees "Country/Region"
  (Modeling > Data Category) pour activer la carte choroplethe.
- Slicer d'agence : dim_rating[agency], selection unique, syncronise sur toutes les pages.

## Page 1 - Brief pays
| Visuel | Champs |
|---|---|
| Slicer pays | dim_country[name_fr] |
| Slicer indicateur | dim_indicator[label_fr] |
| Cartes notation | [Selected Rating], [Selected Outlook], [Selected Rating Date] |
| Cartes constat | [Latest Value], [Latest Date], [Change 12m (%)], [Regional Median], [Trend 5y] |
| Courbe historique | fact_indicators[date] en X, [Value] en Y |
| Courbe projections | fact_projections[year] en X, [Projection Value] en Y |
| Curseur scenario | slicer du parametre what-if "Scenario Value" |
| Cartes scenario | [New Risks (Scenario)], [Cleared Risks (Scenario)], [New Opportunities (Scenario)], [Lost Opportunities (Scenario)] |
| Table risques | dim_rules[label_fr], filtre visuel [Rule Triggered] = 1 et dim_rules[side] = "risk" |
| Table opportunites | dim_rules[label_fr], filtre visuel [Rule Triggered] = 1 et dim_rules[side] = "opportunity" |

## Page 2 - Comparaison
| Visuel | Champs |
|---|---|
| Slicer pays (multi, max 12) | dim_country[name_fr] |
| Slicer indicateur (mono) | dim_indicator[label_fr] |
| Courbes par pays | X = annee(fact_indicators[date]), Y = [Value], legende = dim_country[name_fr] |
| Matrice dernieres valeurs | Lignes = dim_country[name_fr], colonnes = dim_indicator[label_fr], valeurs = [Latest Value] |
| Nuage croissance x inflation | X = [GDP Growth Latest], Y = [Inflation Latest], details = dim_country[name_fr] |
| Bar chart signaux | dim_country[name_fr] en X, [Total Signals (All Indicators)] en Y |

## Page 3 - Vue globale
| Visuel | Champs |
|---|---|
| Cartes synthese | [Rated Countries], [Investment Grade Countries], [Speculative Countries], [Default Countries], [Unrated Countries] |
| Carte choroplethe | Location = dim_country[name_en], legende/couleur = [Selected Category] |
| Bar chart distribution | dim_rating[Rating Category] en X, nombre de pays en Y |
| Table divergences | Lignes = dim_country[name_fr] ; colonnes = [S&P Rating], [Moody's Rating], [Fitch Rating], [Notch Gap], [Opposite Outlooks] ; filtre visuel [Has Divergence] = 1 |

## Page 4 - Suivi des seuils
| Visuel | Champs |
|---|---|
| Matrice pays x regle | Lignes = dim_country[name_fr], colonnes = dim_rules[rule_id], valeurs = [Rule Triggered] |
| Mise en forme conditionnelle | Fond des cellules = [Rule Color] (rouge = risque franchi, vert = opportunite) |
| Slicers | dim_rules[side], dim_indicator[label_fr] |
| Carte total | [Active Signals] |

Regles d'or :
- Aucun visuel n'affiche de score : uniquement valeurs publiees, decomptes de regles, notations d'agences.
- Chaque page porte un titre rappelant la source et la date d'instantane des notations (2026-09-01).
