import os, pathlib

_ROOT = pathlib.Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env", override=True)
except Exception:
    pass

def env(key, default=None):
    return os.getenv(key, default)

LLM_PROVIDER = env("LLM_PROVIDER", "openrouter")
LLM_BASE_URL = env("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_API_KEY = env("LLM_API_KEY", "")
LLM_MODEL = env("LLM_MODEL", "qwen/qwen-2.5-7b-instruct:free")
LLM_TEMPERATURE = float(env("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(env("LLM_MAX_TOKENS", "1600"))
LLM_TIMEOUT = int(env("LLM_TIMEOUT", "60"))
TAVILY_API_KEY = env("TAVILY_API_KEY", "")
CSV_PATH = env("CSV_PATH", "data/macro_indicators.csv")
BRIEFS_PATH = env("BRIEFS_PATH", "data/briefs.json")
ALLOWED_SEARCH_DOMAINS = [d.strip() for d in env(
    "ALLOWED_SEARCH_DOMAINS",
    "reuters.com,bloomberg.com,imf.org,worldbank.org,ft.com").split(",") if d.strip()]
MAX_SEARCH_RESULTS = int(env("MAX_SEARCH_RESULTS", "3"))

INDICATOR_HINTS = {
    "GDP growth": "real GDP growth rate economic activity outlook",
    "Inflation": "CPI consumer price index inflation rate",
    "Interest rate": "lending interest rate central bank monetary policy",
}
