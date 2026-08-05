# 🛰 Country Risk Desk

> **Problème** : l'analyse du risque pays oscille entre deux extrêmes difficiles à concilier: des données macro brutes sans contexte, ou des analyses qualitatives non vérifiées (hallucinations, sources approximatives). Les analystes ont besoin des deux : des chiffres fiables **et** un contexte sourcé, sans payer un terminal propriétaire.  
> **Solution** : un desk open source et bilingue qui combine **13 indicateurs de la Banque Mondiale** (217 économies, 2000–2024) avec un **contexte qualitatif issu de sources de confiance** (Reuters, Bloomberg, FMI, Banque Mondiale, FT). Un agent LangGraph rédige chaque brief, puis une couche de validation contrôle chaque affirmation contre des citations verbatim : **tout ce qui n'est pas fondé est retiré avant affichage**. Sans clé, sans inscription, sans attente.

<p align="left">
  <img src="https://img.shields.io/badge/Python_3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangGraph" />
  <img src="https://img.shields.io/badge/Plotly-636AFD?style=for-the-badge&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="pandas" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions" />
  <img src="https://img.shields.io/badge/LLM-Groq-F55036?style=for-the-badge" alt="LLM Groq" />
  <img src="https://img.shields.io/badge/Web_Search-Tavily-00B4D8?style=for-the-badge" alt="Web Search Tavily" />
  <img src="https://img.shields.io/badge/Data-World_Bank-00693E?style=for-the-badge" alt="Data World Bank" />
  <img src="https://img.shields.io/badge/Bilingual-FR_|_EN-008080?style=for-the-badge" alt="Bilingual FR EN" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License" />
</p>

<p align="left">
  <a href="https://country-risk-desk.streamlit.app/">
    <img src="https://img.shields.io/badge/▶_Démo_en_ligne-0A2C3A?style=for-the-badge" alt="Démo en ligne" />
  </a>
</p>

![Aperçu](image.png)

🇬 English : [README.md](README.md)

---

## En résumé

- **Ce que ça fait** : génère des briefs macro-financiers pour 217 économies — lecture quantitative Banque Mondiale, contexte qualitatif vérifié et cité verbatim, risques & opportunités à 12 mois synthétisés par un LLM **contrôlé affirmation par affirmation**.
- **Compétences mobilisées** : IA agentique (LangGraph), LLM fondé & validation de citations, recherche web restreinte aux domaines de confiance, data engineering, CI/CD, UX bilingue, export PDF.
- **Démo** : [country-risk-desk.streamlit.app](https://country-risk-desk.streamlit.app/)
- **Stack** : Python · Streamlit · LangGraph · Groq · Tavily · Plotly · pandas · GitHub Actions · World Bank API

## Ce que contient un brief

| # | Section | Source |
|---|---|---|
| 01 | Lecture quantitative : dernière valeur, variations, médiane régionale + courbe 2000–2024 | Banque Mondiale (WDI + WGI) |
| 02 | Contexte qualitatif : affirmations vérifiées, chacune étayée par une citation verbatim | Reuters, Bloomberg, FMI, Banque Mondiale, FT |
| 03 | Risques à 12 mois | synthèse LLM fondée |
| 04 | Opportunités à 12 mois | synthèse LLM fondée |
| 05 | Incertitudes | — |
| 06 | Sources citées, cliquables et validées par domaine | — |

**13 indicateurs** : croissance, inflation, taux d'intérêt, compte courant, dette publique, dette externe, réserves, chômage · GES/hab., accès à l'électricité, femmes dans la population active, stabilité politique, contrôle de la corruption.

## Trois lectures du desk

- **Brief pays** — rapport structuré, exportable en PDF dans les deux langues.
- **Comparaison** — jusqu'à 12 pays côte à côte : courbes interactives, tableau des dernières valeurs, carte de positionnement croissance × inflation.
- **Alertes seuil** — inflation > 10 %, réserves < 3 mois d'importations, dette > 90 % du PIB… ; un clic saute vers le pays.

## L'honnêteté par conception

- Pas de source vérifiée → « Information insuffisante ». Le système **n'invente jamais** d'analyse.
- Chaque affirmation qualitative affiche son identifiant de source (`S1`, `S2`…) et la citation exacte sur laquelle elle a été contrôlée.
- Une couche de validation croise la sortie du LLM avec les sources récupérées ; les affirmations non fondées sont retirées avant affichage.
- Provenance affichée, jamais masquée ; les valeurs Banque Mondiale manquantes sont affichées comme telles.

## Deux modes, zéro contrainte visiteur

- **Bibliothèque instantanée** — données et briefs pré-calculés rafraîchis chaque mois par GitHub Actions ; l'ouverture d'un brief est immédiate.
- **Recherche en direct** — à la demande, un agent LangGraph recherche (Tavily, domaines de confiance), rédige (LLM via Groq), valide chaque affirmation et met en cache 24 h. Les clés restent côté serveur.

## Lancer en local

```bash
git clone https://github.com/maxin-dac/country-risk-desk.git
cd country-risk-desk
pip install -r requirements.txt
# .env avec vos propres clés (jamais commité) :
#   TAVILY_API_KEY=...  LLM_BASE_URL=...  LLM_API_KEY=...  LLM_MODEL=...
streamlit run app.py
```

## Architecture

```text
country-risk-desk/
├── app.py                  # entrée Streamlit mince (état, caches, orchestration)
├── src/
│   ├── graph.py            # agent LangGraph : recherche → rédaction → validation → assemblage
│   ├── web_search.py       # recherche Tavily, restreinte aux domaines de confiance
│   ├── llm.py              # client compatible OpenAI (Groq / OpenRouter / DashScope)
│   ├── validation.py       # vérification des citations et des domaines
│   ├── csv_loader.py       # stats Banque Mondiale (dernière valeur, deltas, médiane régionale)
│   ├── alerts.py           # moteur d'alertes seuil
│   ├── compare.py          # graphiques de comparaison (Plotly)
│   ├── pdf_export.py       # export PDF bilingue
│   ├── i18n.py             # chaînes FR/EN ; noms de pays et d'indicateurs (CLDR via Babel)
│   ├── ui_render.py        # rendu HTML des briefs
│   └── ui_theme.py         # design system (CSS, bandeau)
├── scripts/
│   ├── fetch_worldbank.py  # collecte Banque Mondiale par lots (217 économies × 13 indicateurs)
│   └── generate_library.py # pré-calcul mensuel des briefs
└── .github/workflows/      # rafraîchissement mensuel + auto-commit
```

## Limites

- La couverture qualitative dépend de la disponibilité des médias de confiance par pays ; une couverture faible est signalée comme insuffisante, jamais comblée artificiellement.
- La dette publique et les indices de gouvernance ont une couverture Banque Mondiale plus lacunaire.
- Les quotas des niveaux gratuits LLM/recherche peuvent ralentir la génération en direct en cas d'usage intensif.

## Feuille de route

Indicateurs v2 : Gini, IDE, transferts de migrants, dépendance aux matières premières · alertes poussées · notes de scénario.

---

## Auteur

**Maxime NDACLEU** — Data Analyst & Business Intelligence Analyst

<p align="left">
  <a href="https://github.com/maxin-dac">
    <img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
  </a>
  <a href="https://www.linkedin.com/in/maximendacleu">
    <img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" />
  </a>
</p>

---

## Licence

Projet distribué sous licence MIT. Données © Banque Mondiale ; extraits © leurs éditeurs respectifs, cités avec attribution à des fins d'analyse.
