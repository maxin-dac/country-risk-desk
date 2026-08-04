from typing import List, Optional

SCHEMA = '''{
  "web_context_available": boolean,
  "confidence": "high" | "medium" | "low",
  "context": {"points": [{"text": string, "evidence": [{"source_id": string, "quote": string}]}]},
  "outlook": {"risks": [{"text": string, "evidence": [{"source_id": string, "quote": string}]}],
              "opportunities": [{"text": string, "evidence": [{"source_id": string, "quote": string}]}],
              "uncertainties": [string]},
  "limitations": [string]
}'''

SYSTEM = f'''You are a country-risk analyst. You produce strictly factual country-risk briefs.
Use ONLY the provided web source excerpts. Strict prohibitions:
- Never invent facts, figures, dates, institutions, events or URLs.
- Never use internal knowledge to fill gaps. Never extrapolate.
- Never write a qualitative statement without exact evidence.
- Never put URLs inside "text" fields.
Evidence rules:
- Every point must carry at least one evidence item with a valid source_id and a quote.
- "quote" must be an EXACT substring of the provided source excerpt.
- You may translate the idea into the output language inside "text"; the quote stays verbatim.
- If sources do not support any point, return empty lists and web_context_available=false.
Output: valid JSON only, no markdown, no commentary.
Schema:
{SCHEMA}'''

def build_messages(country, indicator, sources_text, lang="en",
                   validation_error: Optional[str] = None) -> List[dict]:
    out_lang = "French" if lang == "fr" else "English"
    user = (f"Country: {country}\nIndicator: {indicator}\n"
            f"Output language for 'text' fields: {out_lang}\n\n"
            f"PROVIDED WEB SOURCES:\n{sources_text}\n\n"
            "Produce only the qualitative sections. Do not produce figures.\n")
    if validation_error:
        user += f"\nValidation errors to fix:\n{validation_error}\nReturn corrected JSON.\n"
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]