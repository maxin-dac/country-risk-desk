import os, pathlib

_ROOT = pathlib.Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(_ROOT / ".env", override=True)
except Exception:
    pass

try:
    import streamlit as st
    _STREAMLIT_SECRETS = st.secrets
except Exception:
    _STREAMLIT_SECRETS = {}

def env(key, default=None):
    value = os.getenv(key)
    if value:
        return value
    try:
        value = _STREAMLIT_SECRETS.get(key)
    except Exception:
        value = None
    return value if value else default

LLM_PROVIDER = "openrouter"
LLM_BASE_URL = "https://openrouter.ai/api/v1"
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
    "Political stability": "political stability violence security risk",
    "Control of corruption": "corruption control governance institutions",

    "CO2 per capita": "greenhouse gas emissions per capita climate",
    "Electricity access": "access to electricity electrification rate",
    "Women in workforce": "female labor force participation gender",

    "External debt": "external debt percent of GNI debt service",

    "Current account": "current account balance external deficit surplus",
    "Gov debt": "government public debt GDP fiscal sustainability",
    "Reserves": "foreign exchange reserves months of imports",
    "Unemployment": "unemployment rate labor market",

    "GDP growth": "real GDP growth rate economic activity outlook",
    "Inflation": "CPI consumer price index inflation rate",
    "Interest rate": "lending interest rate central bank monetary policy",
}

import os as _os
SEARCH_PROVIDER = _os.getenv("SEARCH_PROVIDER", "tavily")
