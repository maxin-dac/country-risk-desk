"""Genere docs/API.md par introspection des modules (signatures + docstrings)."""
import importlib
import inspect
import pathlib

MODULES = [
    "src.csv_loader", "src.alerts", "src.risk_scoring", "src.projections",
    "src.dashboard", "src.watchlist", "src.plot_theme", "src.compare",
    "src.web_search", "src.i18n", "src.ui_render",
]

out = ["# API interne - Country Risk Desk", "",
       "Reference generee automatiquement : `python scripts/build_docs.py`.", ""]

for mod_name in MODULES:
    try:
        mod = importlib.import_module(mod_name)
    except Exception as e:
        out.append(f"## `{mod_name}`\n\n_Import impossible: {e}_\n")
        continue
    out.append(f"## `{mod_name}`")
    doc = inspect.getdoc(mod)
    if doc:
        out.append(f"\n{doc}\n")
    for name, fn in inspect.getmembers(mod, inspect.isfunction):
        if name.startswith("_"):
            continue
        if getattr(fn, "__module__", "") != mod_name:
            continue
        try:
            sig = str(inspect.signature(fn))
        except Exception:
            sig = "(...)"
        d = inspect.getdoc(fn) or "_Pas de docstring._"
        out.append(f"### `{name}{sig}`\n\n{d}\n")
    out.append("")

pathlib.Path("docs").mkdir(exist_ok=True)
pathlib.Path("docs/API.md").write_text("\n".join(out), encoding="utf-8")
print("OK: docs/API.md genere")
