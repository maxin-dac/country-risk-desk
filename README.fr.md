> 🇫🇷 Français | [🇬🇧 English](README.md)

# 🛰 Country Risk Desk

**Briefs macro-financiers pays, fondés sur des sources vérifiées.**
Bilingue 🇫🇷/🇬🇧 · Sans clé, sans inscription, sans attente.

[![Live demo](https://img.shields.io/badge/▶_Live_demo-0A2C3A?style=for-the-badge)](https://maxin-dac-country-risk-desk.streamlit.app)
![Python](https://img.shields.io/badge/Python_3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![pandas](https://img.shields.io/badge/pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)
![Groq](https://img.shields.io/badge/LLM-Groq-F55036?style=for-the-badge)
![Tavily](https://img.shields.io/badge/Web_Search-Tavily-00B4D8?style=for-the-badge)
![World Bank](https://img.shields.io/badge/Data-World_Bank-00693E?style=for-the-badge)
![Bilingual](https://img.shields.io/badge/Bilingual-FR_|_EN-008080?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

![Aperçu](image-1.png)

---

## Ce que fait l'application

Choisissez un pays et un indicateur macro — **croissance du PIB**, **inflation**, **taux d'intérêt**.
Le desk assemble un brief structuré :

| # | Section | Source |
|---|---------|--------|
| 01 | Lecture quantitative : dernière valeur, variations à 3/12 mois, positionnement par rapport à la médiane régionale | Banque Mondiale |
| 02 | Contexte qualitatif : affirmations vérifiées, chacune étayée par une **citation verbatim** | Reuters, Bloomberg, FMI, Banque Mondiale, FT |
| 03 | Risques à 12 mois | synthèse LLM fondée |
| 04 | Opportunités à 12 mois | synthèse LLM fondée |
| 05 | Incertitudes | — |
| 06 | Sources citées, cliquables et validées par domaine | — |

Un clic exporte le brief complet en **PDF**, dans les deux langues.

## L'honnêteté par conception

- **Pas de source vérifiée → « Information insuffisante ».** Le système n'invente jamais d'analyse.
- Chaque affirmation qualitative affiche son identifiant de source (`S1`, `S2`…) et la citation exacte sur laquelle elle a été contrôlée.
- Une couche de validation croise la sortie du LLM avec les sources récupérées ; les affirmations non fondées sont retirées avant affichage.
- La provenance des données est affichée, jamais masquée.

## Deux modes, zéro contrainte visiteur

- **Bibliothèque instantanée** — les données et les briefs pré-calculés sont rafraîchis **chaque mois par GitHub Actions** et commités dans ce dépôt. L'ouverture d'un brief est immédiate ; rien ne s'exécute côté visiteur.
- **Recherche en direct** — à la demande, un agent LangGraph effectue une recherche web restreinte à des domaines de confiance (Tavily), rédige le brief (LLM via Groq), valide chaque affirmation et met le résultat en cache pendant 24 h. Les clés restent côté serveur ; le visiteur ne fournit rien.

## Architecture

    app.py                  entrée Streamlit mince (état, caches, orchestration)
    src/
      ui_render.py          rendu HTML des briefs
      ui_theme.py           design system (CSS, bandeau)
      i18n.py               chaînes FR/EN, noms de pays et d'indicateurs
      graph.py              agent LangGraph : recherche → rédaction → validation → assemblage
      web_search.py         recherche Tavily, restreinte aux domaines de confiance
      llm.py                client compatible OpenAI (Groq / OpenRouter / DashScope)
      validation.py         vérification des citations et des domaines
      csv_loader.py         statistiques Banque Mondiale (dernière valeur, deltas, médiane régionale)
      pdf_export.py         export PDF bilingue
    scripts/
      fetch_worldbank.py    récupération Banque Mondiale par lots (~200 économies, incrémental)
      generate_library.py   pré-calcul mensuel des briefs
    .github/workflows/      rafraîchissement mensuel + auto-commit

## Lancer en local

    git clone https://github.com/maxin-dac/pestel-risk-desk.git
    cd pestel-risk-desk
    pip install -r requirements.txt
    # .env avec vos propres clés (jamais commité) :
    #   TAVILY_API_KEY=...  LLM_BASE_URL=...  LLM_API_KEY=...  LLM_MODEL=...
    streamlit run app.py

## Limites

- La couverture qualitative dépend de la disponibilité des médias de confiance pour chaque pays ; une couverture faible est signalée comme insuffisante, jamais comblée artificiellement.
- Les quotas des niveaux gratuits LLM/recherche peuvent ralentir la génération en direct en cas d'usage intensif.

## Feuille de route

- Élargir le jeu d'indicateurs (dette, commerce, énergie) · couche ESG · alertes pays.

---

*Source de données © Banque Mondiale ; extraits © leurs éditeurs respectifs, cités avec attribution à des fins d'analyse.*

---

## Auteur

**Maxime NDACLEU** — Data Analyst & Business Intelligence Analyst

<p>
  <a href="https://github.com/maxin-dac"><img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a>
  <a href="https://www.linkedin.com/in/maximendacleu"><img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
</p>
