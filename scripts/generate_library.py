import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from src import config
from src.csv_loader import load_csv
from src.graph import build_agent

FEATURED = ["VNM", "BRA", "EGY", "IND", "IDN", "MEX", "TUR", "ZAF", "NGA", "ARG",
            "USA", "CHN", "DEU", "FRA", "GBR", "JPN", "KOR", "SAU", "ARE", "RUS"]
OUT = pathlib.Path(__file__).resolve().parent.parent / "data" / "briefs.json"

def main():
    df = load_csv(config.CSV_PATH)
    agent = build_agent(df)
    briefs = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for country in FEATURED:
        for indicator in sorted(df[df.country == country].indicator.unique()):
            for lang in ("en", "fr"):
                key = f"{country}|{indicator}|{lang}"
                if key in briefs and briefs[key].get("status") in ("done", "done_degraded"):
                    print(f"[SKIP] {key}")
                    continue
                r = agent.invoke({"country": country, "indicator": indicator,
                                  "lang": lang}).get("final_report", {})
                if r.get("status") in ("done", "done_degraded"):
                    r.pop("stats", None)  # figures come from CSV at display time
                    briefs[key] = r
                    print(f"[OK]   {key}: {r.get('status')}, {len(r.get('sources', []))} sources")
                else:
                    print(f"[FAIL] {key}: {r.get('error')}")
    OUT.write_text(json.dumps(briefs, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(briefs)} briefs in {OUT}")

if __name__ == "__main__":
    main()