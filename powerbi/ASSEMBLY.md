# Guide d'assemblage du jumeau Power BI

## Prérequis

- Power BI Desktop (gratuit, Windows)
- Les 6 CSV dans `powerbi/data/` (générés par `scripts/export_powerbi.py`)

## Étape 1 : Importer les données

1. Ouvrir Power BI Desktop
2. **Get Data > Text/CSV**
3. Importer chaque CSV :
   - `dim_country.csv`
   - `dim_indicator.csv`
   - `dim_rules.csv`
   - `dim_rating.csv`
   - `fact_indicators.csv`
   - `fact_projections.csv`

## Étape 2 : Créer le modèle de données (relations)

Dans la vue **Model**, créer les relations :

| De | Vers | Colonne | Type |
|---|---|---|---|
| fact_indicators[country] | dim_country[iso3] | Many-to-One | Active |
| fact_indicators[indicator] | dim_indicator[indicator] | Many-to-One | Active |
| fact_projections[country] | dim_country[iso3] | Many-to-One | Active |
| fact_projections[indicator] | dim_indicator[indicator] | Many-to-One | Active |
| dim_rating[country] | dim_country[iso3] | Many-to-One | Active |
| dim_rules[indicator] | dim_indicator[indicator] | Many-to-One | Active |

## Étape 3 : Copier les mesures DAX

1. Ouvrir `powerbi/measures.dax`
2. Dans Power BI, pour chaque mesure :
   - Clic droit sur une table > **New Measure**
   - Coller la formule DAX
   - Renommer selon le nom de la mesure

**Ordre recommandé** :
1. Mesures de base (`Latest Value`, `Latest Date`, etc.)
2. Mesures de signaux (`Risk Signals`, `Opportunity Signals`)
3. Paramètre what-if (voir Étape 4)
4. Mesures de scénarios (`New Risks`, `Cleared Risks`)
5. Mesures de lecture croisée (`Notch Gap`, `Opposite Outlooks`)

## Étape 4 : Créer le paramètre what-if (scénarios)

1. **Modeling > New Parameter > What-If Parameter**
2. Configuration :
   - **Name** : `Scenario Value`
   - **Data type** : Decimal number
   - **Minimum** : -100
   - **Maximum** : 200
   - **Increment** : 1
   - **Default** : 0
3. Cliquer **OK**
4. La table `Scenario Value` apparaît avec un slider

## Étape 5 : Construire les pages

### Page 1 : Brief pays

- **Slicer** : pays (dim_country) + indicateur (dim_indicator)
- **Cartes** : Latest Value, Latest Date, Change 12m (%)
- **Graphique** : courbe de l'indicateur sur 5 ans
- **Tableau** : risques et opportunités déclenchés (filtrer dim_rules sur side = "risk" ou "opportunity")
- **Curseur what-if** : Scenario Value + cartes New Risks / Cleared Risks

### Page 2 : Comparaison

- **Slicer multi** : pays (max 12)
- **Graphiques** : courbes par indicateur (facette par indicateur)
- **Matrice** : pays × indicateurs (valeurs = Latest Value)
- **Nuage de points** : GDP growth vs Inflation
- **Cartes** : Total Signals (All Indicators) par pays

### Page 3 : Vue globale

- **Carte choroplèthe** : notations par agence (slicer S&P/Moody's/Fitch)
- **Histogramme** : distribution des notations (investment grade vs spec)
- **Tableau** : pays avec divergences (filtrer `Has Divergence = 1`)
- **Cartes** : Notch Gap moyen, Opposite Outlooks

### Page 4 : Suivi des seuils

- **Matrice** : règles × pays (valeurs = 1 si seuil franchi, 0 sinon)
- **Slicer** : indicateur, side (risk/opportunity)
- **Mise en forme conditionnelle** : rouge si seuil franchi

## Étape 6 : Publier

1. **File > Publish > Publish to Power BI**
2. Choisir le workspace
3. Obtenir le lien public : **File > Share > Publish to web**

## Cohérence avec l'app Streamlit

- **Mêmes règles** : `dim_rules.csv` = `src/alerts.py` (32 règles)
- **Mêmes données** : CSV régénérés par `scripts/export_powerbi.py` après chaque refresh mensuel
- **Même philosophie** : zéro score, décomptes factuels de signaux documentés
