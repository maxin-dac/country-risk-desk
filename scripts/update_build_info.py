# -*- coding: utf-8 -*-
"""Met a jour src/_build_info.json avec les informations du commit courant."""

import datetime
import json
import pathlib
import subprocess


def update_build_info():
    root = pathlib.Path(__file__).resolve().parent.parent
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    except Exception:
        commit = ""

    try:
        date = subprocess.check_output(["git", "log", "-1", "--format=%ad", "--date=short"], cwd=root, text=True).strip()
    except Exception:
        date = datetime.date.today().isoformat()

    if not date:
        date = datetime.date.today().isoformat()

    info = {
        "commit": commit,
        "date": date
    }
    target = root / "src" / "_build_info.json"
    target.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    print(f"[INFO] Build info mis a jour dans {target}: {info}")


if __name__ == "__main__":
    update_build_info()
