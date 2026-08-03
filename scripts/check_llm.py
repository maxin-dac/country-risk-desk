import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from src import config
from src.llm import call_llm_json

print("Provider:", config.LLM_PROVIDER, "| Model:", config.LLM_MODEL)
result, usage = call_llm_json([{"role": "user", "content": 'Return exactly this JSON: {"ok": true}'}])
print("Response:", result)
print("Usage:", usage)