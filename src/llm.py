import json, re
from litellm import completion
from . import config

def _parse(content):
    content = (content or "").strip()
    m = re.search(r"`(?:json)?\s*(.*?)`", content, re.DOTALL)
    try:
        return json.loads((m.group(1) if m else content).strip())
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from LLM", "raw": content}

def call_llm_json(messages):
    # 1. Modèle principal basé sur votre config
    primary_model = f"{config.LLM_PROVIDER}/{config.LLM_MODEL}"
    
    # 2. Fallbacks intelligents : si le primaire échoue (ex: 429), on essaie les suivants
    fallbacks = []
    if config.LLM_PROVIDER == "groq":
        fallbacks = [f"openrouter/{config.LLM_MODEL}", "openrouter/meta-llama/llama-3-70b-instruct"]
    elif config.LLM_PROVIDER == "openrouter":
        fallbacks = [f"groq/{config.LLM_MODEL}", "openrouter/meta-llama/llama-3-70b-instruct"]
    else:
        fallbacks = ["openrouter/meta-llama/llama-3-70b-instruct"]

    kwargs = {
        "model": primary_model,
        "messages": messages,
        "temperature": config.LLM_TEMPERATURE,
        "max_tokens": config.LLM_MAX_TOKENS,
        "fallbacks": fallbacks,  # <--- La magie de la résilience est ici
    }

    # Format JSON natif pour les providers qui le supportent
    if config.LLM_PROVIDER in ("groq", "openai", "openrouter"):
        kwargs["response_format"] = {"type": "json_object"}

    # Headers personnalisés pour OpenRouter (bonne pratique)
    if config.LLM_PROVIDER == "openrouter":
        kwargs["extra_headers"] = {
            "HTTP-": "https://github.com/maxin-dac/country-risk-desk",
            "X-Title": "Country Risk Desk"
        }

    try:
        response = completion(**kwargs)
        
        usage = {
            "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
            "completion_tokens": getattr(response.usage, "completion_tokens", 0)
        }
        
        raw_content = response.choices[0].message.content or "{}"
        return _parse(raw_content), usage
        
    except Exception as e:
        # Si TOUS les fallbacks échouent, on retourne une erreur propre au lieu de crasher
        return {"error": f"LLM call failed after fallbacks: {str(e)}"}, {}
