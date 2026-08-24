import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from src.web_search import search_web_context, format_sources
from src.prompts import build_messages
from src.llm import call_llm_json
from src.validation import validate_report

country = "Vietnam"
indicator = "Inflation"
hint = "CPI consumer price index"

print(f"--- 1. RECHERCHE WEB pour {country} / {indicator} ---")
sources, err = search_web_context(country, indicator, hint)
if err:
    print(f"Erreur recherche: {err}")
else:
    for s in sources:
        print(f"[{s['id']}] {s['domain']} - {s['title'][:60]}")
        print(f"    Contenu: {s['content'][:150]}...\n")

print("--- 2. APPEL LLM ---")
sources_text = format_sources(sources)
messages = build_messages(sources_text)
result, usage = call_llm_json(messages)

print("Reponse LLM brute:")
import json
print(json.dumps(result, indent=2, ensure_ascii=False))

print("\n--- 3. VALIDATION ---")
is_valid, errors = validate_report(result, sources)
if is_valid:
    print("SUCCES : Le rapport est valide !")
else:
    print("ECHEC : Le rapport a ete rejete pour les raisons suivantes :")
    for e in errors:
        print(f"  - {e}")
    
    # Affichage détaillé pour comprendre l'erreur
    print("\n--- DEBUG DES CITATIONS ---")
    for k in ["context", "outlook"]:
        section = result.get(k, {})
        if isinstance(section, dict):
            for sub_k in ["points", "risks", "opportunities"]:
                items = section.get(sub_k, [])
                for it in items:
                    for ev in it.get("evidence", []):
                        sid = ev.get("source_id")
                        quote = ev.get("quote", "")
                        source_content = next((s["content"] for s in sources if s["id"] == sid), "")
                        print(f"Source {sid} contient {len(source_content)} chars.")
                        print(f"Citation LLM ({len(quote)} chars): {quote[:100]}...")
