# 🛰 Country Risk Desk

**Briefs macro-financiers pays, fondés sur des sources vérifiées.**  
Bilingue 🇫🇷/🇬🇧 · Sans clé, sans inscription, sans attente.

[![Live demo](https://img.shields.io/badge/▶_Live_demo-0A2C3A?style=for-the-badge)](https://country-risk-desk.streamlit.app)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logo=langchain&logoColor=white)
![LiteLLM](https://img.shields.io/badge/LiteLLM-00D2FF?style=flat&logo=server&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-636AFD?style=flat&logo=plotly&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=flat&logo=pandas&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white)
![LLM](https://img.shields.io/badge/LLM-OpenRouter-F55036?style=flat&logo=openai&logoColor=white)
![Tavily](https://img.shields.io/badge/Web_Search-Tavily-00B4D8?style=flat&logo=search&logoColor=white)
![World Bank](https://img.shields.io/badge/Data-World_Bank-00693E?style=flat&logo=database&logoColor=white)
![Bilingual](https://img.shields.io/badge/Bilingual-FR_|_EN-008080?style=flat&logo=translate&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat&logo=opensourceinitiative&logoColor=white)
![Brief overview](assets/screenshot-brief.png)

---

## Ce que fait l'application

Choisissez l'une des **217 économies** et l'un des **13 indicateurs** :

- **Noyau macro** — croissance du PIB, inflation, taux d'intérêt, compte courant, dette publique, dette externe, réserves, chômage
- **ESG & gouvernance** — émissions de GES par habitant, accès à l'électricité, femmes dans la population active, stabilité politique, contrôle de la corruption

| # | Section | Source |
|---|---------|--------|
| 01 | Lecture quantitative : dernière valeur, variations, médiane régionale + **courbe de progression 2000–2024** | Banque Mondiale (WDI + WGI) |
| 02 | Contexte qualitatif : affirmations vérifiées, chacune étayée par une **citation verbatim** | Reuters, Bloomberg, FMI, Banque Mondiale, FT |
| 03 | Risques à 12 mois | synthèse LLM fondée |
| 04 | Opportunités à 12 mois | synthèse LLM fondée |
| 05 | Incertitudes | — |
| 06 | Sources citées, cliquables et validées par domaine | — |

### Trois lectures du desk

- **Brief pays** — le rapport structuré ci-dessus, exportable en PDF dans les deux langues.
- **Comparaison** — jusqu'à 12 pays côte à côte : courbes interactives par indicateur, tableau des dernières valeurs, carte de positionnement croissance × inflation.
- **Alertes seuil** — pays franchissant les seuils d'analyste (inflation > 10 %, réserves < 3 mois d'importations, dette > 90 % du PIB…) ; un clic saute vers le pays.

## L'honnêteté par conception

- **Pas de source vérifiée → « Information insuffisante ».** Le système n'invente jamais d'analyse.
- Chaque affirmation qualitative affiche son identifiant de source (`S1`, `S2`…) et la citation exacte sur laquelle elle a été contrôlée.
- Une couche de validation croise la sortie du LLM avec les sources récupérées ; les affirmations non fondées sont retirées avant affichage.
- La provenance des données est affichée, jamais masquée ; les valeurs manquantes de la Banque Mondiale sont affichées comme telles.

## Deux modes, zéro contrainte visiteur

- **Bibliothèque instantanée** — les données et les briefs pré-calculés sont rafraîchis **chaque mois par GitHub Actions** et commités dans ce dépôt. L'ouverture d'un brief est immédiate ; rien ne s'exécute côté visiteur.
- **Recherche en direct** — à la demande, un agent LangGraph effectue une recherche web restreinte à des domaines de confiance (Tavily), rédige le brief (LLM via LiteLLM avec fallbacks OpenRouter), valide chaque affirmation et met le résultat en cache pendant 24 h. Les clés restent côté serveur ; le visiteur ne fournit rien.

## Architecture

```text
country-risk-desk/
├── app.py                  # entrée Streamlit mince (état, caches, orchestration)
── src/
│ ├── ui_render.py          # rendu HTML des briefs
│ ├── ui_theme.py           # design system (CSS, bandeau)
│ ├── i18n.py               # chaînes FR/EN ; noms de pays et d'indicateurs (CLDR via Babel)
│ ├── graph.py              # agent LangGraph : recherche → rédaction → validation → assemblage
│ ├── web_search.py         # recherche Tavily, restreinte aux domaines de confiance
│ ├── llm.py                # routeur LiteLLM (OpenRouter)
│ ├── validation.py         # vérification des citations et des domaines
│ ├── csv_loader.py         # statistiques Banque Mondiale (dernière valeur, deltas, médiane régionale)
│ ├── alerts.py             # moteur d'alertes seuil
│ ├── compare.py            # graphiques de comparaison (Plotly)
│ └── pdf_export.py         # export PDF bilingue
── scripts/
│ ├── fetch_worldbank.py    # récupération Banque Mondiale par lots (217 économies × 13 indicateurs)
│ └── generate_library.py   # pré-calcul mensuel des briefs
── .github/workflows/       # rafraîchissement mensuel + auto-commit
└── assets/                 # captures d'écran et images
```

https://country-risk-desk.streamlit.app/

## Lancer en local

```bash
git clone https://github.com/maxin-dac/country-risk-desk.git
cd country-risk-desk
pip install -r requirements.txt

# .env avec vos propres clés (jamais commité) :
#   TAVILY_API_KEY=...
#   LLM_PROVIDER=openrouter
#   LLM_API_KEY=...
#   LLM_MODEL=meta-llama/llama-3.1-8b-instruct
#   LLM_BASE_URL=https://openrouter.ai/api/v1

streamlit run app.py
```

## Limites

- La couverture qualitative dépend de la disponibilité des médias de confiance par pays ; une couverture faible est signalée comme insuffisante, jamais comblée artificiellement.
- La dette publique et les indices de gouvernance ont une couverture Banque Mondiale plus lacunaire.
- Les quotas des niveaux gratuits LLM/recherche peuvent ralentir la génération en direct en cas d'usage intensif.

## Feuille de route

Indicateurs v2 : Gini, IDE, transferts de migrants, dépendance aux matières premières · alertes poussées · notes de scénario.

---

## Auteur

**Maxime NDACLEU** - Data Analyst & Business Intelligence Analyst

<p align="left">
  <a href="https://github.com/maxin-dac">
  </a>
  <a href="https://www.linkedin.com/in/maximendacleu">
  </a>
</p>

---

## Licence

Projet distribué sous licence MIT. Données © Banque Mondiale ; extraits © leurs éditeurs respectifs, cités avec attribution à des fins d'analyse.
