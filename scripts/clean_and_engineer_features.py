import pathlib
import pandas as pd
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

IN_PANEL = DATA / "risk_panel.csv"
OUT_FINAL = DATA / "risk_panel_final.csv"

def main():
    print("🧹 Nettoyage et Feature Engineering du Panel de Risque...\n")
    
    # 1. Chargement
    df = pd.read_csv(IN_PANEL, low_memory=False)
    print(f"📥 Chargé : {df.shape[0]} lignes, {df.shape[1]} colonnes")
    
    # 2. Filtrage temporel (Optionnel mais fortement recommandé)
    # Les données d'avant 2000 sont souvent structurellement différentes (chocs pétroliers, changement de méthodologie FMI).
    # Pour un modèle de risque moderne, on se concentre sur 2000-2031.
    df = df[df['year'] >= 2000].copy()
    print(f"✂️  Filtré (>= 2000) : {df.shape[0]} lignes")

    # 3. Fusion des indicateurs redondants (Le "Golden Record")
    # On priorise 'Gen gov debt' (FMI, plus complet) sur 'Gov debt' (WB, souvent vide)
    if 'Gen gov debt' in df.columns and 'Gov debt' in df.columns:
        df['Gov Debt (% GDP)'] = df['Gen gov debt'].fillna(df['Gov debt'])
        df = df.drop(columns=['Gen gov debt', 'Gov debt'])
        print("🔗 Fusionné : 'Gen gov debt' et 'Gov debt' -> 'Gov Debt (% GDP)'")

    # Idem pour la croissance si besoin, ou l'inflation
    # df['Inflation (%)'] = df['Inflation'].fillna(df.get('Inflation_WB', np.nan))

    # 4. Suppression des indicateurs non pertinents pour le risque souverain (Optionnel)
    cols_to_drop = [
        # 'Women in workforce', 
        # 'CO2 per capita',
        'Gini' # Trop de données manquantes (20%)
    ]
    existing_to_drop = [c for c in cols_to_drop if c in df.columns]
    if existing_to_drop:
        df = df.drop(columns=existing_to_drop)
        print(f"🗑️  Supprimé (bruit / hors sujet) : {existing_to_drop}")

    # 5. Gestion des valeurs manquantes (Imputation intelligente)
    # Pour les données macro, on forward-fill (remplit avec la dernière valeur connue) 
    # mais on limite à 2 ans max pour ne pas propager une vieille donnée obsolète.
    df = df.sort_values(by=['country', 'year'])
    
    cols_to_impute = [c for c in df.columns if c not in ['country', 'year', 'region']]
    
    print("🩹 Imputation des valeurs manquantes (Forward Fill limité à 2 ans)...")
    for col in cols_to_impute:
        # On groupe par pays pour ne pas remplir avec les données d'un autre pays
        df[col] = df.groupby('country')[col].transform(lambda x: x.ffill(limit=2))
        # Petit backfill pour les premières années si nécessaire
        df[col] = df.groupby('country')[col].transform(lambda x: x.bfill(limit=1))

    # 6. Feature Engineering : Création de ratios de risque composites
    print("⚙️  Création de variables dérivées de risque...")
    
    # Ratio de pression de la dette (si on a les deux données)
    if 'Debt service' in df.columns and 'Exports' in df.columns: # Note: ajuster le nom exact si différent
        pass # À adapter selon les noms exacts de vos colonnes
    
    # Score de vulnérabilité budgétaire simple (plus le déficit et la dette sont hauts, plus le score est haut)
    # On normalise d'abord grossièrement pour l'exemple
    if 'Fiscal balance' in df.columns and 'Gov Debt (% GDP)' in df.columns:
        # Un déficit négatif est mauvais, une dette élevée est mauvaise
        df['Fiscal_Stress_Index'] = (
            (df['Gov Debt (% GDP)'] / 100).clip(upper=1.5) + 
            (df['Fiscal balance'].abs() / 20).clip(upper=1.0)
        )
        print("   [+] Créé : 'Fiscal_Stress_Index' (indicateur composite de stress budgétaire)")

    # 7. Nettoyage final et tri
    df = df.sort_values(by=['country', 'year']).reset_index(drop=True)
    
    # Sauvegarde
    df.to_csv(OUT_FINAL, index=False)
    
    print(f"\n{'='*60}")
    print(f"✅ PANEL FINAL SAUVEGARDÉ : {OUT_FINAL.name}")
    print(f"{'='*60}")
    print(f"📏 Dimensions finales : {df.shape[0]:,} lignes x {df.shape[1]} colonnes")
    print(f"📅 Période active    : {int(df['year'].min())} à {int(df['year'].max())}")
    
    # Vérification finale des trous
    missing_pct = df[cols_to_impute].isnull().mean().sort_values(ascending=False)
    print(f"\n📊 Taux de valeurs manquantes résiduelles (Top 5) :")
    for col, pct in missing_pct.head(5).items():
        print(f"   - {col:30s} : {pct*100:5.1f}%")

if __name__ == "__main__":
    main()