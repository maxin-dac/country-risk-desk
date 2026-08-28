# 🛰 Country Risk Desk

**Desk de risque pays macro-financier 100 % déterministe.**
Bilingue 🇫🇷/🇬🇧 · 226 économies · 17 indicateurs · 4 piliers · sources officielles uniquement.

> **Version anglaise :** [README.md](README.md)

<p align="left">
<img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Streamlit-1.45%2B-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
<img src="https://img.shields.io/badge/pandas-2.x-150458?style=flat&logo=pandas&logoColor=white" alt="pandas" />
<img src="https://img.shields.io/badge/NumPy-1.26%2B-013243?style=flat&logo=numpy&logoColor=white" alt="NumPy" />
<img src="https://img.shields.io/badge/Plotly-5.x-636AFD?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
<img src="https://img.shields.io/badge/openpyxl-Excel-107C41?style=flat&logo=microsoftexcel&logoColor=white" alt="openpyxl" />
<img src="https://img.shields.io/badge/World_Bank-WDI-00693E?style=flat&logo=database&logoColor=white" alt="World Bank WDI" />
<img src="https://img.shields.io/badge/World_Bank-WGI_2024-1F8B4C?style=flat&logo=database&logoColor=white" alt="World Bank WGI" />
<img src="https://img.shields.io/badge/IMF-WEO_Apr_2026-003C71?style=flat&logo=database&logoColor=white" alt="IMF WEO" />
<img src="https://img.shields.io/badge/Tavily-recherche_optionnelle-00B4D8?style=flat&logo=search&logoColor=white" alt="Tavily" />
<img src="https://img.shields.io/badge/DuckDuckGo-DE5833?style=flat&logo=duckduckgo&logoColor=white" alt="DuckDuckGo" />
<img src="https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white" alt="CI" />
<img src="https://img.shields.io/badge/Bilingual-FR_%7C_EN-008080?style=flat&logo=translate&logoColor=white" alt="Bilingual" />
<img src="https://img.shields.io/badge/License-MIT-yellow?style=flat&logo=opensourceinitiative&logoColor=white" alt="License" />
</p>

![Aperçu](assets/aperçu.jpeg)

## Ce que fait l’application

Choisissez l’une des **226 économies** et l’un des **17 indicateurs de risque**, et obtenez un brief complet et sourcé :

| # | Section | Contenu |
|---|---------|---------|
| — | **Score de risque** | Score agrégé 0-100 (4 piliers, pondérations 30/30/20/20), rang mondial, barres par pilier |
| 01 | Constat chiffré | Dernière valeur + date, variations 3/12 mois, médiane régionale, tendance 5 ans, courbe fusionnée |
| 02 | Contexte — sources officielles | Vue « moteur de recherche » : titres vérifiés, mots indexés, snippet propre si qualité suffisante, liens à suivre |
| 03 | Risques à 12 mois | Règles de seuils déterministes (inflation > 10 %, réserves < 3 mois d’imports, dette > 90 % PIB…) |
| 04 | Opportunités à 12 mois | Règles miroir d’opportunité |
| 05 | Incertitudes | Explicites quand l’information est mince — jamais inventées |
| 06 | Projections FMI | Trajectoire WEO (avril 2026) 2027-2031 + détection de divergence vs tendance 12 mois |
| 07 | Sources & limites | Bibliographie cliquable (FMI, Banque Mondiale, WGI) + limites honnêtes |

## Trois lectures du desk

- **Brief pays** - le rapport structuré ci-dessus ; exportable en **PDF (FR/EN)**, **CSV**, **Excel**.
- **Comparaison** - jusqu’à 12 pays : courbes par indicateur avec unités, tableau des dernières valeurs, positionnement croissance × inflation, classement par risque relatif.
- **Vue globale** - carte choroplèthe du risque, distribution des scores à catégories cliquables, Top 10, alertes seuil (rouges, un clic → brief du pays).

## Provenance des données

| Source | Contenu |
|--------|---------|
| Banque Mondiale WDI | 13 séries macro/sociales, 2000-2024 |
| Banque Mondiale WGI 2024 | Stabilité politique, corruption, état de droit, qualité réglementaire |
| FMI WEO (avril 2026) | Solde budgétaire, dette brute générale - historique + projections 2027-2031 |
| Calcul interne | Service de la dette externe (TDS / exports de biens & services) |

## Honnêteté & explicabilité par conception

- Chaque jugement est une règle ou un seuil documenté - voir `docs/ARCHITECTURE.md`.
- Pas de source vérifiée → *« Information insuffisante »*, jamais comblé artificiellement.
- Valeurs FMI / Banque Mondiale manquantes affichées comme manquantes.

## Live demo

<a href="https://country-risk-desk.streamlit.app/" target="_blank"><img src="https://img.shields.io/badge/▶_Live_Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo" /></a> sur **Streamlit Cloud**

<a href="https://country-risk-desk.onrender.com/" target="_blank"><img src="https://img.shields.io/badge/▶_Live_Demo-0A2C3A?style=for-the-badge&logo=render&logoColor=white" alt="Live Demo" /></a> sur **Render**

## Lancer en local

    git clone https://github.com/maxin-dac/country-risk-desk.git
    cd country-risk-desk
    pip install -r requirements.txt
    streamlit run app.py

## Structure du projet

```bash
    country-risk-desk/
    ├── app.py               # entrée Streamlit (brief / comparaison / vue globale)
    ├── src/
    │   ├── csv_loader.py    # chargement CSV + stats (variations, médiane, tendance 5 ans)
    │   ├── risk_scoring.py  # sous-scores, score agrégé, Top 10
    │   ├── alerts.py        # moteur d’alertes seuil
    │   ├── projections.py   # trajectoire FMI + divergence
    │   ├── dashboard.py     # choroplèthe, distribution, vue globale
    │   ├── compare.py       # graphiques & tableaux de comparaison
    │   ├── sources_view.py  # rendu « résultats de recherche » de la section 02
    │   ├── web_search.py    # recherche qualifiée Tavily / DuckDuckGo
    │   ├── graph.py         # assemblage déterministe des briefs
    │   ├── ui_render.py     # rendu HTML des briefs
    │   ├── ui_theme.py      # design system + masthead
    │   ├── plot_theme.py    # thème Plotly + unités (source de vérité)
    │   ├── i18n.py          # FR/EN, RISK_ORDER, unités
    │   └── pdf_export.py    # export PDF bilingue
    ├── scripts/             # récupération des données (BM, WGI, FMI) + générateur de doc
    ├── data/                # CSV/XLSX commités (rafraîchissables)
    ├── docs/                # ARCHITECTURE.md + API.md
    ├── tests/               # pytest (règles & scoring)
    └── assets/              # theme.css + captures
```

## Rafraîchir les données

```bash
    python scripts/fetch_worldbank.py
    python scripts/fetch_wgi.py
    python scripts/fetch_imf.py
    python scripts/fetch_risk_extras.py
```

## Documentation & tests

- `docs/ARCHITECTURE.md` - piliers, ancres, pondérations, règles, sources.
- `docs/API.md` - référence : `python scripts/build_docs.py`.
- `pytest` - tests unitaires des règles et du scoring.

## Auteur

**Maxime NDACLEU** - Data Analyst & Business Intelligence Analyst

<p>
<a href="https://github.com/maxin-dac"><img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="https://www.linkedin.com/in/maximendacleu"><img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
</p>

## Licence

MIT. Données © Banque Mondiale / FMI ; extraits © leurs éditeurs respectifs, cités avec attribution à des fins d’analyse.
