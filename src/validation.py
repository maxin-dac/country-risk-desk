import re

def _norm(s):
    return re.sub(r"\s+", " ", s or "").strip().lower()

def _check_items(items, by_id, label, errors):
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return
    for i, it in enumerate(items):
        if not isinstance(it, dict) or not str(it.get("text", "")).strip():
            errors.append(f"{label}[{i}].text empty or invalid")
            continue
        ev = it.get("evidence")
        if not isinstance(ev, list) or not ev:
            errors.append(f"{label}[{i}].evidence must contain at least one proof")
            continue
        for j, e in enumerate(ev):
            sid, q = (e or {}).get("source_id"), (e or {}).get("quote", "")
            if sid not in by_id:
                errors.append(f"{label}[{i}].evidence[{j}].source_id invalid: {sid}")
            elif len(_norm(q)) < 20:
                errors.append(f"{label}[{i}].evidence[{j}].quote too short")
            elif _norm(q) not in _norm(by_id[sid].get("content", "")):
                errors.append(f"{label}[{i}].evidence[{j}].quote is not an exact substring of source {sid}")

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