"""Personal watchlist with JSON persistence (session-only fallback)."""
import json
import pathlib

PATH = pathlib.Path("data/watchlist.json")


def load():
    try:
        if PATH.exists():
            data = json.loads(PATH.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return [str(x).upper() for x in data]
    except Exception:
        pass
    return []


def save(items):
    try:
        PATH.write_text(json.dumps(items), encoding="utf-8")
        return True
    except Exception:
        return False
