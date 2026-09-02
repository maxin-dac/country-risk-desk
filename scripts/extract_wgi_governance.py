# -*- coding: utf-8 -*-
"""Extrait Rule of law + Regulatory quality depuis l'extrait officiel WGI.xlsx
(feuilles rl/rq) et les injecte dans macro_indicators.csv. Idempotent."""
import pathlib
import pandas as pd

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def main():
    csv_path = DATA / "macro_indicators.csv"
    df = pd.read_csv(csv_path, low_memory=False)
    countries = pd.read_csv(DATA / "countries.csv")
    regions = dict(zip(countries["iso3"], countries["region_en"]))
    macro_countries = set(df["country"].unique())

    ps = df[df.indicator == "Political stability"].iloc[0]
    cat_pol, src_wgi, unit_idx = ps["category"], ps["source"], ps["unit"]

    new_rows = []
    for sheet, name in [("rl", "Rule of law"), ("rq", "Regulatory quality")]:
        w = pd.read_excel(DATA / "WGI.xlsx", sheet_name=sheet)
        w = w[["Economy (code)", "Year",
               "Governance estimate (approx. -2.5 to +2.5)"]].copy()
        w.columns = ["iso3", "year", "value"]
        w = w.dropna(subset=["value", "iso3"])
        w = w[w["iso3"].isin(macro_countries)]
        w = w[w["year"] >= 2000]
        for _, r in w.iterrows():
            new_rows.append({
                "country": r["iso3"], "indicator": name,
                "category": cat_pol, "date": f"{int(r['year'])}-12-31",
                "value": float(r["value"]), "unit": unit_idx,
                "region": regions.get(r["iso3"], ""), "source": src_wgi,
            })
        print(f"[OK] {name} : {len([x for x in new_rows if x['indicator'] == name])} lignes")

    if new_rows:
        df = df[~df["indicator"].isin(["Rule of law", "Regulatory quality"])]
        out = pd.concat([df, pd.DataFrame(new_rows, columns=list(df.columns))],
                        ignore_index=True)
        out.to_csv(csv_path, index=False)
        print(f"[OK] macro_indicators.csv : +{len(new_rows)} lignes")

if __name__ == "__main__":
    main()
