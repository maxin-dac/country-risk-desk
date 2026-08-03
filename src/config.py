import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

env = lambda k, d="": os.getenv(k, d)

LLM_PROVIDER = env("LLM_PROVIDER", "openrouter")
LLM_BASE_URL = env("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_API_KEY = env("LLM_API_KEY", "")
LLM_MODEL = env("LLM_MODEL", "qwen/qwen-2.5-7b-instruct:free")
LLM_TEMPERATURE = float(env("LLM_TEMPERATURE", "0.1"))
LLM_MAX_TOKENS = int(env("LLM_MAX_TOKENS", "900"))
LLM_TIMEOUT = int(env("LLM_TIMEOUT", "40"))

TAVILY_API_KEY = env("TAVILY_API_KEY")
MAX_SEARCH_RESULTS = int(env("MAX_SEARCH_RESULTS", "3"))
CSV_PATH = env("CSV_PATH", "data/macro_indicators.csv")

ALLOWED_SEARCH_DOMAINS = ["reuters.com", "bloomberg.com", "imf.org", "worldbank.org",
                          "oecd.org", "ft.com", "economist.com"]
PRIMARY_SOURCE_DOMAINS = ALLOWED_SEARCH_DOMAINS[:4]

BRIEFS_PATH = env("BRIEFS_PATH", "data/briefs.json")

INDICATOR_HINTS = {
    "Inflation": "CPI consumer price index inflation rate",
    "Policy rate": "policy interest rate central bank monetary policy",
    "GDP growth": "real GDP growth economic outlook",
}