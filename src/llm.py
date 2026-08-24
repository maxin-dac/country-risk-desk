import json, re
from litellm import completion
from . import config

def _parse(content):
    content = (content or "").strip()
    candidates = [content]
    candidates.extend(m.group(1).strip() for m in re.finditer(
        r"```(?:json)?\s*(.*?)```", content, re.DOTALL | re.IGNORECASE))
    decoder = json.JSONDecoder()
    for start, char in enumerate(content):
        if char == "{":
            try:
                candidates.append(content[start:])
                break
            except Exception:
                pass
    try:
        raw = next((candidate for candidate in candidates if _is_json_object(candidate, decoder)), None)
        if raw is None:
            raise json.JSONDecodeError("No JSON object found", content, 0)
        report = decoder.raw_decode(raw.strip())[0]
        if not isinstance(report, dict):
            return {"error": "LLM response is not a JSON object", "raw": content}
        return _normalize_report(report)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from LLM", "raw": content}


def _is_json_object(value, decoder):
    try:
        parsed, _ = decoder.raw_decode(value.strip())
        return isinstance(parsed, dict)
    except json.JSONDecodeError:
        return False


def _clean_items(items):
    if not isinstance(items, list):
        return []
    cleaned = []
    for item in items:
        if isinstance(item, str) and item.strip():
            item = {"text": item}
        if not isinstance(item, dict):
            continue
        text = next((item.get(key) for key in ("text", "claim", "description", "summary")
                     if str(item.get(key, "")).strip()), "")
        if not str(text).strip():
            continue
        normalized = dict(item)
        normalized["text"] = str(text).strip()
        if "evidence" not in normalized:
            normalized["evidence"] = item.get("proof", item.get("sources", []))
        if not isinstance(normalized["evidence"], list):
            normalized["evidence"] = []
        normalized["evidence"] = [
            evidence if isinstance(evidence, dict)
            else {"source_id": evidence, "quote": ""}
            for evidence in normalized["evidence"]]
        cleaned.append(normalized)
    return cleaned


def _normalize_report(report):
    context = report.get("context")
    if not isinstance(context, dict):
        context = {}
    outlook = report.get("outlook")
    if not isinstance(outlook, dict):
        outlook = {}
    context["points"] = _clean_items(context.get("points", context.get("claims")))
    outlook["risks"] = _clean_items(outlook.get("risks", outlook.get("risques")))
    outlook["opportunities"] = _clean_items(
        outlook.get("opportunities", outlook.get("opportunites", outlook.get("opportunités"))))
    outlook["uncertainties"] = (outlook.get("uncertainties")
                                 if isinstance(outlook.get("uncertainties"), list)
                                 else [])
    report["context"] = context
    report["outlook"] = outlook
    report.setdefault("web_context_available", False)
    return report

def call_llm_json(messages):
    model_name = config.LLM_MODEL.removeprefix("openrouter/")
    primary_model = f"openrouter/{model_name}"
    fallbacks = ["openrouter/meta-llama/llama-3-70b-instruct"]

    kwargs = {
        "model": primary_model,
        "messages": messages,
        "temperature": config.LLM_TEMPERATURE,
        "max_tokens": config.LLM_MAX_TOKENS,
        "api_key": config.LLM_API_KEY,  # <--- C'EST CETTE LIGNE QUI MANQUAIT !
        "fallbacks": fallbacks,
    }

    kwargs["extra_headers"] = {
        "HTTP-Referer": "https://github.com/maxin-dac/country-risk-desk",
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
        # Si TOUS les fallbacks échouent, on retourne une erreur propre
        return {"error": f"LLM call failed after fallbacks: {str(e)}"}, {}
