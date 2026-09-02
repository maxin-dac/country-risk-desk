# -*- coding: utf-8 -*-
"""Orchestrateur de rafraichissement des donnees (GitHub Actions).
Fetch WB/WGI/IMF/extras -> extraction gouvernance -> filtre agregats
-> controles de coherence. Ne committe rien : le workflow s'en charge."""
import pathlib
import subprocess
import sys

import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

FETCHES = ["fetch_worldbank.py", "fetch_wgi.py", "fetch_imf.py",
           "fetch_risk_extras.py", "extract_wgi_governance.py"]

def run(script):
    print(f"\n=== {script} ===", flush=True)
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT)
    if r.returncode != 0:
        print(f"[WARN] {script} a echoue (code {r.returncode}) - on continue")

def main():
    before = pd.read_csv(DATA / "macro_indicators.csv", low_memory=False)
    n_before = len(before)

    for s in FETCHES:
        run(s)

    # Filtre defensif des agregats Banque mondiale (EAP, ECA, WLD...)
    allowed = set(pd.read_csv(DATA / "countries.csv")["iso3"])
    df = pd.read_csv(DATA / "macro_indicators.csv", low_memory=False)
    n_raw = len(df)
    df = df[df["country"].isin(allowed)]
    if n_raw - len(df):
        print(f"[OK] agregats filtres : {n_raw - len(df)} lignes")
        df.to_csv(DATA / "macro_indicators.csv", index=False)

    # Controles de coherence (le workflow echoue sinon -> pas de commit)
    n_after = len(df)
    inds = set(df["indicator"].unique())
    print(f"\n[check] lignes : {n_before} -> {n_after}")
    print(f"[check] indicateurs : {len(inds)}")
    if n_after < 0.8 * n_before:
        print("[FATAL] perte de plus de 20% des lignes - refresh aborte")
        sys.exit(1)
    need = {"Inflation", "GDP growth", "Reserves", "Gen gov debt",
            "Political stability", "Rule of law", "Regulatory quality"}
    missing = need - inds
    if missing:
        print(f"[FATAL] indicateurs manquants : {sorted(missing)}")
        sys.exit(1)
    print("[OK] refresh coherent")

if __name__ == "__main__":
    main()
