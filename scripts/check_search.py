import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import config
from src.web_search import search_web_context

print("Tavily key set:", bool(config.TAVILY_API_KEY))
sources, err = search_web_context("Vietnam", "Inflation", "CPI consumer price index inflation rate")
print("Error:", err)
for s in sources:
    print(f"[{s['id']}] {s['domain']} — {s['title'][:80]}")