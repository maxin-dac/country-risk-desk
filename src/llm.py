import json, re, time
from openai import OpenAI
from . import config

def _client():
    headers = ({"HTTP-Referer": "https://github.com/maxin-dac/country-risk-desk", "X-Title": "Country Risk Desk"}
               if config.LLM_PROVIDER == "openrouter" else {})
    return OpenAI(base_url=config.LLM_BASE_URL, api_key=config.LLM_API_KEY or "na",
                  timeout=config.LLM_TIMEOUT, default_headers=headers)

def _parse(content):
    content = (content or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", content, re.DOTALL)
    return json.loads((m.group(1) if m else content).strip())

def call_llm_json(messages):
    kwargs = dict(model=config.LLM_MODEL, messages=messages,
                  temperature=config.LLM_TEMPERATURE, max_tokens=config.LLM_MAX_TOKENS)
    if config.LLM_PROVIDER in ("dashscope", "groq"):
        kwargs["response_format"] = {"type": "json_object"}
    last = None
    for attempt in range(2):
        try:
            r = _client().chat.completions.create(**kwargs)
            usage = ({"prompt_tokens": r.usage.prompt_tokens,
                      "completion_tokens": r.usage.completion_tokens} if r.usage else {})
            return _parse(r.choices[0].message.content or "{}"), usage
        except Exception as e:
            last = e
            if "429" in str(e) and attempt == 0:
                time.sleep(5)
                continue
            raise
    raise last