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

<!-- RULES:START -->
## Règles de seuils (généré automatiquement depuis `src/alerts.py`)

### Signaux de risque (RULES)

| id | Indicateur | Condition | Libellé FR |
|---|---|---|---|
| inflation_high | Inflation | `dict(id="inflation_high", indicator="Inflation", cond=v > 10, desc=True,
         en="Inflation above 10 %", fr="Inflation supérieure à 10 %")` | Inflation supérieure à 10 % |
| recession | GDP growth | `dict(id="recession", indicator="GDP growth", cond=v < 0, desc=False,
         en="Negative GDP growth", fr="Croissance du PIB négative")` | Croissance du PIB négative |
| reserves_low | Reserves | `dict(id="reserves_low", indicator="Reserves", cond=v < 3, desc=False,
         en="Reserves below 3 months of imports", fr="Réserves sous 3 mois d'importations")` | Réserves sous 3 mois d'importations |
| debt_high | Gen gov debt | `dict(id="debt_high", indicator="Gen gov debt", cond=v > 90, desc=True,
         en="Government debt above 90 % of GDP", fr="Dette publique au-dessus de 90 % du PIB")` | Dette publique au-dessus de 90 % du PIB |
| ca_deficit | Current account | `dict(id="ca_deficit", indicator="Current account", cond=v < -5, desc=False,
         en="Current account deficit beyond -5 % of GDP", fr="Déficit courant au-delà de -5 % du PIB")` | Déficit courant au-delà de -5 % du PIB |
| unemp_high | Unemployment | `dict(id="unemp_high", indicator="Unemployment", cond=v > 15, desc=True,
         en="Unemployment above 15 %", fr="Chômage supérieur à 15 %")` | Chômage supérieur à 15 % |
| youth_unemp_high | Youth unemployment | `dict(id="youth_unemp_high", indicator="Youth unemployment", cond=v > 25, desc=True,
         en="Youth unemployment above 25 %", fr="Chômage des jeunes supérieur à 25 %")` | Chômage des jeunes supérieur à 25 % |
| political_instability | Political stability | `dict(id="political_instability", indicator="Political stability", cond=v < -1.0, desc=False,
         en="Political stability below -1.0", fr="Stabilité politique inférieure à -1,0")` | Stabilité politique inférieure à -1,0 |
| corruption_high | Control of corruption | `dict(id="corruption_high", indicator="Control of corruption", cond=v < -0.5, desc=False,
         en="Control of corruption below -0.5", fr="Maîtrise de la corruption inférieure à -0,5")` | Maîtrise de la corruption inférieure à -0,5 |
| gov_effectiveness_low | Government effectiveness | `dict(id="gov_effectiveness_low", indicator="Government effectiveness", cond=v < -0.5, desc=False,
         en="Government effectiveness below -0.5", fr="Efficacité du gouvernement inférieure à -0,5")` | Efficacité du gouvernement inférieure à -0,5 |
| gini_high | Gini | `dict(id="gini_high", indicator="Gini", cond=v > 45, desc=True,
         en="Gini index above 45 (high inequality)", fr="Indice de Gini supérieur à 45 (inégalités élevées)")` | Indice de Gini supérieur à 45 (inégalités élevées) |
| external_debt_high | External debt | `dict(id="external_debt_high", indicator="External debt", cond=v > 60, desc=True,
         en="External debt above 60% of GNI", fr="Dette externe supérieure à 60 % du RNB")` | Dette externe supérieure à 60 % du RNB |
| fiscal_deficit | Fiscal balance | `dict(id="fiscal_deficit", indicator="Fiscal balance", cond=v < -5, desc=False,
             en="Fiscal deficit beyond -5 % of GDP", fr="D\u00e9ficit budg\u00e9taire au-del\u00e0 de -5 % du PIB")` | Déficit budgétaire au-delà de -5 % du PIB |
| rule_of_law_low | Rule of law | `dict(id="rule_of_law_low", indicator="Rule of law", cond=v < -0.5, desc=False,
             en="Rule of law below -0.5", fr="État de droit inférieur à -0,5")` | État de droit inférieur à -0,5 |
| regulatory_quality_low | Regulatory quality | `dict(id="regulatory_quality_low", indicator="Regulatory quality", cond=v < -0.5, desc=False,
             en="Regulatory quality below -0.5", fr="Qualité réglementaire inférieure à -0,5")` | Qualité réglementaire inférieure à -0,5 |

### Signaux d'opportunité (OPP_RULES)

| id | Indicateur | Condition |
|---|---|---|
| inflation_low | Inflation | `dict(id="inflation_low", indicator="Inflation", cond=v < 3,
         en=f"Inflation contained below 3 % (value: {v:.1f})",
         fr=f"Inflation contenue sous 3 % (valeur : {v:.1f})")` |
| growth_strong | GDP growth | `dict(id="growth_strong", indicator="GDP growth", cond=v > 5,
         en=f"Strong GDP growth above 5 % (value: {v:.1f})",
         fr=f"Croissance du PIB soutenue au-dessus de 5 % (valeur : {v:.1f})")` |
| reserves_high | Reserves | `dict(id="reserves_high", indicator="Reserves", cond=v > 6,
         en=f"Comfortable reserves above 6 months of imports (value: {v:.1f})",
         fr=f"Réserves confortables au-dessus de 6 mois d'importations (valeur : {v:.1f})")` |
| debt_low | Gen gov debt | `dict(id="debt_low", indicator="Gen gov debt", cond=v < 40,
         en=f"Government debt below 40 % of GDP (value: {v:.1f})",
         fr=f"Dette publique sous 40 % du PIB (valeur : {v:.1f})")` |
| ca_surplus | Current account | `dict(id="ca_surplus", indicator="Current account", cond=v > 3,
         en=f"Current account surplus above 3 % of GDP (value: {v:.1f})",
         fr=f"Excédent courant au-dessus de 3 % du PIB (valeur : {v:.1f})")` |
| unemp_low | Unemployment | `dict(id="unemp_low", indicator="Unemployment", cond=v < 5,
         en=f"Low unemployment below 5 % (value: {v:.1f})",
         fr=f"Chômage faible sous 5 % (valeur : {v:.1f})")` |
| youth_unemp_low | Youth unemployment | `dict(id="youth_unemp_low", indicator="Youth unemployment", cond=v < 12,
         en=f"Youth unemployment below 12 % (value: {v:.1f})",
         fr=f"Chômage des jeunes sous 12 % (valeur : {v:.1f})")` |
| pol_stability_high | Political stability | `dict(id="pol_stability_high", indicator="Political stability", cond=v > 0.5,
         en=f"Strong political stability above 0.5 (value: {v:.2f})",
         fr=f"Stabilité politique solide au-dessus de 0,5 (valeur : {v:.2f})")` |
| corruption_ctrl_high | Control of corruption | `dict(id="corruption_ctrl_high", indicator="Control of corruption", cond=v > 0.5,
         en=f"Good control of corruption above 0.5 (value: {v:.2f})",
         fr=f"Maîtrise de la corruption solide au-dessus de 0,5 (valeur : {v:.2f})")` |
| gov_eff_high | Government effectiveness | `dict(id="gov_eff_high", indicator="Government effectiveness", cond=v > 0.5,
         en=f"Effective government above 0.5 (value: {v:.2f})",
         fr=f"Efficacité du gouvernement solide au-dessus de 0,5 (valeur : {v:.2f})")` |
| gini_low | Gini | `dict(id="gini_low", indicator="Gini", cond=v < 35,
         en=f"Low inequality (Gini below 35, value: {v:.1f})",
         fr=f"Inégalités contenues (Gini sous 35, valeur : {v:.1f})")` |
| ext_debt_low | External debt | `dict(id="ext_debt_low", indicator="External debt", cond=v < 30,
         en=f"External debt below 30 % of GNI (value: {v:.1f})",
         fr=f"Dette externe sous 30 % du RNB (valeur : {v:.1f})")` |
| fiscal_surplus | Fiscal balance | `dict(id="fiscal_surplus", indicator="Fiscal balance", cond=v > 1,
             en=f"Fiscal surplus of {v:.1f}% of GDP: comfortable policy space.",
             fr=f"Exc\u00e9dent budg\u00e9taire de {v:.1f}% du PIB : marge de man\u0153uvre confortable.")` |
| rule_of_law_high | Rule of law | `dict(id="rule_of_law_high", indicator="Rule of law", cond=v > 0.5,
             en=f"Strong rule of law at {v:.2f}: solid legal enforcement.",
             fr=f"État de droit solide à {v:.2f} : application du droit fiable.")` |
| regulatory_quality_high | Regulatory quality | `dict(id="regulatory_quality_high", indicator="Regulatory quality", cond=v > 0.5,
             en=f"Strong regulatory quality at {v:.2f}: sound policy framework.",
             fr=f"Qualité réglementaire solide à {v:.2f} : cadre politique sain.")` |
<!-- RULES:END -->
