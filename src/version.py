import datetime
import json
import pathlib
import re
import subprocess

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_PYPROJECT = _ROOT / "pyproject.toml"

_DEFAULT_VERSION = "0.1.0"


def _read_pyproject_version() -> str:
    try:
        text = _PYPROJECT.read_text(encoding="utf-8")
        m = re.search(r'^\s*version\s*=\s*"([^"]+)"', text, re.MULTILINE)
        if m:
            return m.group(1)
        m = re.search(r"^\s*version\s*=\s*'([^']+)'", text, re.MULTILINE)
        if m:
            return m.group(1)
    except Exception:
        pass
    return _DEFAULT_VERSION


def _git_sha() -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(_ROOT), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
        )
        return out.decode("utf-8").strip()
    except Exception:
        return ""


def _git_tag() -> str:
    try:
        out = subprocess.check_output(
            ["git", "-C", str(_ROOT), "describe", "--tags", "--exact-match"],
            stderr=subprocess.DEVNULL,
        )
        tag = out.decode("utf-8").strip()
        return tag.lstrip("v")
    except Exception:
        return ""


VERSION: str = _git_tag() or _read_pyproject_version()
BUILD_DATE: str = datetime.date.today().isoformat()
GIT_SHA: str = _git_sha()


def version_string(verbose: bool = True) -> str:
    base = f"v{VERSION}"
    if verbose and GIT_SHA:
        base += f" ({GIT_SHA})"
    if verbose:
        base += f" · {BUILD_DATE}"
    return base


def version_info() -> dict:
    return {
        "version": VERSION,
        "build_date": BUILD_DATE,
        "git_sha": GIT_SHA,
        "display": version_string(),
    }


def version_info_json() -> str:
    return json.dumps(version_info(), ensure_ascii=False)


if __name__ == "__main__":
    print(version_string())
