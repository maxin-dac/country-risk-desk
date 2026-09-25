# -*- coding: utf-8 -*-
"""Version sémantique du projet (source de vérité unique via pyproject.toml)."""

import json
import os
import pathlib
import re
import subprocess

__version__ = "0.7.1"


def get_project_version() -> str:
    """Extrait la version depuis pyproject.toml s'il existe, sinon utilise __version__."""
    try:
        root_dir = pathlib.Path(__file__).resolve().parent.parent
        pyproject_path = root_dir / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text(encoding="utf-8")
            match = re.search(r'^\s*version\s*=\s*"([^"]+)"', content, re.MULTILINE)
            if match:
                return match.group(1)
    except Exception:
        pass
    return __version__


def _git(*args) -> str:
    """Exécute une commande git et renvoie la sortie (si git et .git sont présents)."""
    try:
        root_dir = pathlib.Path(__file__).resolve().parent.parent
        r = subprocess.run(
            ["git", *args],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=2,
        )
        return r.stdout.strip()
    except Exception:
        return ""


def get_build_info() -> tuple[str, str]:
    """Récupère le commit hash (court) et la date du commit.

    Tente dans l'ordre:
    1. Commande Git directe (local / dev avec .git)
    2. Fichier _build_info.json (généré lors des CI/CD)
    3. Variables d'environnement (GITHUB_SHA / STREAMLIT_GIT_COMMIT)
    """
    # 1. Essai Git
    h = _git("rev-parse", "--short=7", "HEAD")
    d = _git("log", "-1", "--format=%ad", "--date=short")
    if h:
        return h, d

    # 2. Essai _build_info.json
    try:
        build_file = pathlib.Path(__file__).resolve().parent / "_build_info.json"
        if build_file.exists():
            data = json.loads(build_file.read_text(encoding="utf-8"))
            h = data.get("commit", "")[:7]
            d = data.get("date", "")
            if h:
                return h, d
    except Exception:
        pass

    # 3. Variables d'environnement (CI / Streamlit Cloud)
    env_sha = os.getenv("GITHUB_SHA") or os.getenv("STREAMLIT_GIT_COMMIT") or ""
    if env_sha:
        return env_sha[:7], ""

    return "", ""


def version_string() -> str:
    """Retourne la chaîne formatée de la version (ex: v0.7.1 (2cc4ceb) · 2026-09-25)."""
    ver = get_project_version()
    out = f"v{ver}"
    h, d = get_build_info()
    if h:
        out += f" ({h})"
    if d:
        out += f" \u00b7 {d}"
    return out

