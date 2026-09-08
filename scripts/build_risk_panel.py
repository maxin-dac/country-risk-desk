import pathlib
import pandas as pd
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


IN_MAIN = DATA / "macro_indicators.csv"
IN_PROJ = DATA / "imf_projections.csv"


OUT_PANEL = DATA / "risk_panel.csv"

def load_long_format(filepath):
    """Charge un CSV au format long et le nettoie."""
    if not filepath.exists():
        return pd.DataFrame()
    
    print(f"📥 Chargement de {filepath.name}...")
    df = pd.read_csv(filepath, low_memory=False)
    
    
    df['indicator'] = df['indicator'].astype(str).str.strip()
    
    
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['year'] = df['date'].dt.year
    elif 'year' in df.columns:
        df['year'] = pd.to_numeric(df['year'], errors='coerce')
        
    
    df = df.dropna(subset=['value', 'year', 'country', 'indicator'])
    
    return df

def main():
    print("🏗️  Construction du Panel de Risque Pays...\n")
    
    
    df_main = load_long_format(IN_MAIN)
    df_proj = load_long_format(IN_PROJ)
    
    if df_main.empty:
        print("❌ ERREUR: macro_indicators.csv est vide ou introuvable.")
        return
        
    
    if not df_proj.empty:
        print(f"🔗 Fusion des données historiques et des projections FMI...")
        df = pd.concat([df_main, df_proj], ignore_index=True)
    else:
        df = df_main
        
    print(f"📊 Total de lignes avant pivot: {len(df):,}")
    
    
    df = df.drop_duplicates(subset=['country', 'year', 'indicator'], keep='first')
    
    
    meta_cols = ['country']
    if 'region' in df.columns:
        meta_cols.append('region')
    
    country_meta = df[meta_cols].drop_duplicates().set_index('country')
    
    
    print("🔄 Pivot des données (format Long -> Large)...")
    panel = df.pivot_table(
        index=['country', 'year'], 
        columns='indicator', 
        values='value', 
        aggfunc='first'
    ).reset_index()
    
    
    panel = panel.merge(country_meta, left_on='country', right_index=True, how='left')
    
    
    base_cols = ['country', 'year']
    if 'region' in panel.columns:
        base_cols.insert(1, 'region')
        
    indicator_cols = [c for c in panel.columns if c not in base_cols]
    panel = panel[base_cols + sorted(indicator_cols)]
    
    
    panel = panel.sort_values(by=['country', 'year']).reset_index(drop=True)
    
    
    panel.to_csv(OUT_PANEL, index=False)
    
    
    n_countries = panel['country'].nunique()
    min_year = int(panel['year'].min())
    max_year = int(panel['year'].max())
    n_indicators = len(indicator_cols)
    
    print(f"\n{'='*60}")
    print(f"✅ PANEL SAUVEGARDÉ : {OUT_PANEL.name}")
    print(f"{'='*60}")
    print(f"📏 Dimensions      : {panel.shape[0]:,} lignes (Pays/Années) x {panel.shape[1]} colonnes")
    print(f"🌍 Pays couverts   : {n_countries}")
    print(f"📅 Période         : {min_year} à {max_year}")
    print(f"📈 Indicateurs     : {n_indicators} variables de risque")
    
    
    print(f"\n📊 COMPLÉTUDE DES DONNÉES (Top 15 indicateurs les plus remplis) :")
    print("-" * 60)
    
    
    completeness = (1 - panel[indicator_cols].isnull().mean()).sort_values(ascending=False)
    
    for ind, pct in completeness.head(15).items():
        bar = "█" * int(pct * 20) + "░" * (20 - int(pct * 20))
        print(f"  {ind:30s} |{bar}| {pct*100:5.1f}%")
        
    print(f"\n⚠️  Indicateurs avec < 50% de données (à surveiller) :")
    low_data = completeness[completeness < 0.50]
    if low_data.empty:
        print("  Aucun ! La couverture est excellente.")
    else:
        for ind, pct in low_data.items():
            print(f"  - {ind:30s} ({pct*100:.1f}%)")
            
    print(f"\n💡 Conseil : Pour les modèles, utilisez les indicateurs > 70% de complétude.")

if __name__ == "__main__":
    main()