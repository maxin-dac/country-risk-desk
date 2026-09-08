import datetime
import pathlib
import subprocess

_ROOT = pathlib.Path(__file__).resolve().parent.parent
_VERSION_FILE = _ROOT / "VERSION"

_DEFAULT_VERSION = "0.1.0"


def _read_version_file() -> str:
    try:
        return _VERSION_FILE.read_text(encoding="utf-8").strip()
    except Exception:
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


VERSION: str = _git_tag() or _read_version_file()
BUILD_DATE: str = datetime.date.today().isoformat()
GIT_SHA: str = _git_sha()


def version_string(verbose: bool = True) -> str:
    base = f"v{VERSION}"
    if verbose and GIT_SHA:
        base += f" ({GIT_SHA})"
    if verbose:
        base += f" · {BUILD_DATE}"
    return base
