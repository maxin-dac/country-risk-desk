# -*- coding: utf-8 -*-
"""Version semantique du projet (source de verite unique).

Le numero semver vit ICI (__version__), jamais dans git ni ailleurs.
git ne fournit que le complement d'identification : hash court + date du commit.
"""
import subprocess

__version__ = "1.1.0"


def _git(*args):
    try:
        r = subprocess.run(["git", *args], capture_output=True, text=True, timeout=2)
        return r.stdout.strip()
    except Exception:
        return ""


def version_string():
    out = f"v{__version__}"
    h = _git("rev-parse", "--short=7", "HEAD")
    d = _git("log", "-1", "--format=%ad", "--date=short")
    if h:
        out += f" ({h})"
    if d:
        out += f" \u00b7 {d}"
    return out
