# Architecture & methodologie - Country Risk Desk

Outil d'analyse risque pays 100 % deterministe (aucun LLM): chaque chiffre
affiche est tracable vers une source officielle, chaque jugement derive d'une
regle ou d'un seuil documente ci-dessous.

## Sources de donnees

| Source | Contenu | Fraicheur | Script |
|---|---|---|---|
| Banque Mondiale (WDI) | 13 series macro/sociales | 2000-2024 | `scripts/fetch_worldbank.py` |
| Banque Mondiale (WGI) | 4 indicateurs de gouvernance | 1996-2024 | `scripts/fetch_wgi.py` (fichier `data/WGI.xlsx`) |
| FMI WEO (Excel officiel) | Solde budgetaire, dette brute generale + projections | 1980-2031 | `scripts/fetch_imf.py` (fichier `data/WEOAll.xlsx`) |
| Calcul interne | Service de la dette = TDS / exports de biens & services | idem WDI | `scripts/fetch_risk_extras.py` |
| Web qualitatif | Extraits verifies (Tavily, repli DuckDuckGo) | temps reel | `src/web_search.py` |

Rafraichissement complet: executer les scripts ci-dessus dans l'ordre, puis
commiter les CSV.

## Cadre de risque: 4 piliers, 17 indicateurs

La liste blanche `RISK_ORDER` (src/i18n.py) est la source de verite du brief,
de la comparaison et des exports.

| Pilier (poids) | Indicateurs |
|---|---|
| Externe & souverain (30 %) | Reserves, Compte courant, Dette externe, Service de la dette |
| Macro-economique (30 %) | Croissance PIB, Inflation, Solde budgetaire, Dette brute generale, Chomage |
| Politique & institutionnel (20 %) | Stabilite politique, Controle de la corruption, Etat de droit, Qualite reglementaire |
| Social & structurel (20 %) | Gini, Chomage des jeunes, Ratio de dependance, Dependance matieres premieres |

## Scoring agrege (0-100, plus eleve = plus risque)

1. Sous-score par indicateur: interpolation lineaire entre ancre "meilleure" et
   ancre "pire", bornee a [0, 100] (`src/risk_scoring.ANCHORS`).
   Ex.: Inflation 2 % -> 0 ; 20 % -> 100. Reserves 8 mois -> 0 ; 1,5 mois -> 100.
2. Score pilier = moyenne des sous-scores disponibles.
3. Score global = moyenne ponderee (30/30/20/20).
4. Lecture: < 35 Faible ; 35-54 Modere ; 55-69 Eleve ; >= 70 Critique.

Le score est explicable: chaque pilier se decompose en sous-scores issus de
donnees observees; aucun apprentissage automatique.

## Regles d'alerte (bandeau + risques du brief)

Seuils binaires documentes dans `src/alerts.py` (RISK_RULES / OPP_RULES /
RULES), ex.: inflation > 10 %, reserves < 3 mois d'imports, dette generale >
90 % PIB, solde budgetaire < -5 % PIB, etat de droit < -0,5.

## Dynamique

- Tendance 5 ans: pente de regression lineaire normalisee par la mediane
  (`trend_5y_norm` dans `src/csv_loader.get_stats`); libelle
  amelioration/deterioration selon la directionnalite de risque
  (`HIGHER_IS_WORSE`).
- Projections FMI 2027-2031: section 06 du brief + detection de divergence si
  la tendance 12 mois s'inverse dans la trajectoire projetee.

## Cartographie du code

| Module | Role |
|---|---|
| `src/csv_loader.py` | Chargement CSV + statistiques (derniere valeur, variations, tendance) |
| `src/alerts.py` | Regles de risque/opportunite + bandeau d'alertes |
| `src/risk_scoring.py` | Sous-scores, score agrege, Top 10, libelles |
| `src/projections.py` | Trajectoire FMI, sparkline, divergence |
| `src/dashboard.py` | Carte choroplethe, distribution, evolution temporelle |
| `src/compare.py` | Mode comparaison (series, tableau, positionnement) |
| `src/web_search.py` | Recherche qualitative multi-fournisseurs + extraits propres |
| `src/plot_theme.py` | Theme des visuels + unites (source de verite) |
| `src/watchlist.py` | Liste de suivi persistante (JSON) |
| `src/i18n.py` | FR/EN, RISK_ORDER, piliers |

## Documentation

- `docs/API.md`: reference generee par `python scripts/build_docs.py`
- HTML optionnel: `pip install pdoc && pdoc src -o docs/html`
