# 🛰 Country Risk Desk

> French version: [README.fr.md](README.fr.md)

Macro-financial country risk analysis tool, based exclusively on official data and documented rules.

Bilingual interface 🇫🇷/🇬🇧 · 217 economies · 16 indicators · sovereign ratings from S&P, Moody's, and Fitch · official sources.

![overview](assets/overview.jpeg)

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Streamlit-1.45%2B-FF4B4B?style=flat&logo=streamlit&logoColor=white" alt="Streamlit" />
  <img src="https://img.shields.io/badge/pandas-2.x-150458?style=flat&logo=pandas&logoColor=white" alt="pandas" />
  <img src="https://img.shields.io/badge/Plotly-5.x-636AFD?style=flat&logo=plotly&logoColor=white" alt="Plotly" />
  <img src="https://img.shields.io/badge/openpyxl-Excel-107C41?style=flat&logo=microsoftexcel&logoColor=white" alt="openpyxl" />
  <img src="https://img.shields.io/badge/World_Bank-WDI-00693E?style=flat&logo=database&logoColor=white" alt="World Bank WDI" />
  <img src="https://img.shields.io/badge/World_Bank-WGI_2024-1F8B4C?style=flat&logo=database&logoColor=white" alt="World Bank WGI" />
  <img src="https://img.shields.io/badge/IMF-WEO_Apr_2026-003C71?style=flat&logo=database&logoColor=white" alt="IMF WEO" />
  <img src="https://img.shields.io/badge/Ratings-S%26P_%7C_Moody's_%7C_Fitch-0057B8?style=flat&logo=bookstack&logoColor=white" alt="Sovereign ratings" />
  <img src="https://img.shields.io/badge/CI-GitHub_Actions-2088FF?style=flat&logo=githubactions&logoColor=white" alt="CI" />
  <img src="https://img.shields.io/badge/Bilingual-FR_%7C_EN-008080?style=flat&logo=translate&logoColor=white" alt="Bilingual" />
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat&logo=opensourceinitiative&logoColor=white" alt="License" />
</p>

## Purpose of the application

Country Risk Desk provides a structured analysis brief for each of the 217 covered economies, based on any of the 16 available macroeconomic and governance indicators:

| Ref | Section | Content |
| --- | --- | --- |
| - | Sovereign rating | Long-term foreign currency ratings from S&P Global Ratings, Moody's, and Fitch Ratings, along with their outlook and decision date; "Unrated" is shown when the country is not rated |
| 01 | Key figures | Latest published value and reference date, 3- and 12-month changes, position relative to the regional median, 5-year trend, and progression chart |
| - | Scenario analysis | Interactive slider: tests a hypothetical indicator value and shows which threshold-based risks/opportunities would trigger or clear (deterministic comparison, not a forecast) |
| 02 | 12-month risks | Signals triggered by explicit thresholds (e.g., inflation > 10%, reserves < 3 months of imports, debt > 90% of GDP) |
| 03 | 12-month opportunities | Symmetrical signals triggered when trends cross thresholds in a favorable direction |
| 04 | IMF Projections | Trajectory from WEO outlooks (April 2026) for 2027-2031, compared against the 12-month trend |

## Three reading modes

- **Country brief** - the structured report described above; exportable to PDF (French or English), CSV, and Excel formats.
- **Compare** - up to 12 countries simultaneously: indicator charts with units, table of the latest published values, growth × inflation positioning.
- **Dashboard** - map of sovereign ratings by agency, rating distribution, summary of covered countries (rated countries, investment grade, speculative grade, default or withdrawn, unrated countries), and threshold monitoring; each entry links to the relevant country brief.

## Data sources

| Source | Content |
| --- | --- |
| World Bank - WDI | Macroeconomic and social series, 2000-2024 |
| IMF - WEO (April 2026) | Fiscal balance, general government gross debt: historical and 2027-2031 projections |
| Rating agencies | Ratings, outlooks, and dates sourced from Wikipedia via [List of countries by credit rating](https://en.wikipedia.org/wiki/List_of_countries_by_credit_rating) (accessed on September 1, 2026), verified against agency publications |

## Methodological principles

- The application does not compute any proprietary ratings or scores: it presents official publications and signals derived from documented thresholds, available in `docs/ARCHITECTURE.md`.
- No missing value is estimated or filled: missing data is displayed as missing; an unrated country is shown as unrated.
- Every signal mentions the specific rule and threshold that triggered it; every brief cites its sources and dates.
- Agency ratings are reproduced without interpretation or aggregation.

## Assumed limitations

- Macroeconomic series come from annual or irregular vintages: cross-country comparisons use each country's latest available value, not a synchronized date.
- Sovereign ratings correspond to a snapshot (September 1, 2026); only a manual revision of the CSV files updates them.
- WGI indicators are statistical estimates with confidence intervals; the application displays the point estimate.
- The application produces no aggregate score and no ranking: it is an analysis aid, not a credit opinion.

## Live demonstrations

<a href="https://country-risk-desk.streamlit.app/" target="_blank"><img src="https://img.shields.io/badge/▶_Live_Demo-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Live Demo" /></a> on Streamlit Cloud

<a href="https://country-risk-desk.onrender.com/" target="_blank"><img src="https://img.shields.io/badge/▶_Live_Demo-0A2C3A?style=for-the-badge&logo=render&logoColor=white" alt="Live Demo" /></a> on Render

## Local installation

```bash
git clone https://github.com/maxin-dac/country-risk-desk.git
cd country-risk-desk
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```text
country-risk-desk/
├── app.py               # Streamlit entry point (brief / compare / dashboard)
├── src/
│   ├── csv_loader.py    # CSV loading + statistics (changes, median, trend)
│   ├── ratings.py       # Sovereign ratings reading (S&P, Moody's, Fitch)
│   ├── alerts.py        # Threshold rules: risk and opportunity signals
│   ├── projections.py   # IMF trajectory + trend comparison
│   ├── dashboard.py     # Ratings map, distribution, summary
│   ├── compare.py       # Comparison charts and tables
│   ├── ui_render.py     # HTML rendering for briefs
│   ├── ui_theme.py      # Design system + masthead
│   ├── plot_theme.py    # Plotly theme and units (single source of truth)
│   ├── i18n.py          # EN/FR labels, indicator order, units
│   └── pdf_export.py    # Bilingual PDF export
├── scripts/             # fetch (BM, WGI, FMI), panneaux de données & générateur de doc
├── data/                # CSV/XLSX versionnés, notations, countries.csv, panneaux intermédiaires
├── docs/                # ARCHITECTURE.md + API.md
├── tests/               # pytest (threshold rules)
└── assets/              # theme.css + screenshots
```

## Data refresh

```bash
python scripts/fetch_worldbank.py
python scripts/fetch_wgi.py
python scripts/fetch_imf.py
python scripts/fetch_risk_extras.py
```

Sovereign ratings are updated by reviewing the `data/ratings_sp.csv`, `data/ratings_moodys.csv`, and `data/ratings_fitch.csv` files, using a new snapshot of the Wikipedia page and agency publications.
The Rule of law and Regulatory quality indicators are extracted from the official `WGI.xlsx` extract (sheets `rl`/`rq`).

## Documentation and tests

- `docs/ARCHITECTURE.md` - indicators, anchors, threshold rules, sources.
- `docs/API.md` - reference generated by `python scripts/build_docs.py`.
- `pytest` - unit tests for threshold rules.

## Author

Maxime NDACLEU - Data Analyst & Business Intelligence Analyst

<p align="left">
<a href="https://github.com/maxin-dac"><img src="https://img.shields.io/badge/GitHub-maxin--dac-181717?style=flat&logo=github&logoColor=white" alt="GitHub" /></a>
<a href="https://www.linkedin.com/in/maximendacleu"><img src="https://img.shields.io/badge/LinkedIn-maximendacleu-0A66C2?style=flat&logo=linkedin&logoColor=white" alt="LinkedIn" /></a>
</p>

## License

MIT. Series are provided by the World Bank and the IMF; ratings belong to their respective agencies and are reproduced for informational purposes only.
