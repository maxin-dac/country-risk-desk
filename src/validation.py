import re
from difflib import SequenceMatcher

def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip().lower()

def _is_similar(quote, source_content, threshold=0.80):
    """Vérifie si la citation est similaire à au moins 80% d'un extrait de la source."""
    q = _norm(quote)
    s = _norm(source_content)
    if len(q) < 10:
        return False
    # Chemin rapide : correspondance exacte
    if q in s:
        return True
    
    # Fuzzy matching : on fait glisser une fenêtre sur le texte source
    q_len = len(q)
    best_ratio = 0
    for i in range(max(0, len(s) - q_len - 30)):
        window = s[i:i + q_len + 30]
        ratio = SequenceMatcher(None, q, window).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
        if best_ratio >= threshold:
            return True
    return best_ratio >= threshold

def _check_items(items, by_id, label, errors):
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return
    for i, it in enumerate(items):
        if not isinstance(it, dict) or not str(it.get("text", " ")).strip():
            errors.append(f"{label}[{i}].text empty or invalid")
            continue
        ev = it.get("evidence")
        if not isinstance(ev, list) or not ev:
            errors.append(f"{label}[{i}].evidence must contain at least one proof")
            continue
        for j, e in enumerate(ev):
            sid, q = (e or {}).get("source_id"), (e or {}).get("quote", " ")
            if sid not in by_id:
                errors.append(f"{label}[{i}].evidence[{j}].source_id invalid: {sid}")
            elif len(_norm(q)) < 15:
                errors.append(f"{label}[{i}].evidence[{j}].quote too short")
            elif not _is_similar(q, by_id[sid].get("content", " ")):
                errors.append(f"{label}[{i}].evidence[{j}].quote not sufficiently similar to source {sid}")

def validate_report(report, sources):
    errors = []
    if not isinstance(report, dict):
        return False, ["Report is not an object"]
    for k in ("web_context_available", "context", "outlook"):
        if k not in report:
            errors.append(f"Missing key: {k}")
    by_id = {s["id"]: s for s in sources}
    if not sources and report.get("web_context_available") is not False:
        errors.append("web_context_available must be false when no source is available")
    ctx = report.get("context", {})
    _check_items(ctx.get("points", []) if isinstance(ctx, dict) else [], by_id, "context.points", errors)
    out = report.get("outlook", {})
    if isinstance(out, dict):
        _check_items(out.get("risks", []), by_id, "outlook.risks", errors)
        _check_items(out.get("opportunities", []), by_id, "outlook.opportunities", errors)
    return not errors, errors
