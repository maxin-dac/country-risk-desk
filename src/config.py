import os
import pathlib

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


CSV_PATH = env("CSV_PATH", "data/macro_indicators.csv")
BRIEFS_PATH = env("BRIEFS_PATH", "data/briefs.json")

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
