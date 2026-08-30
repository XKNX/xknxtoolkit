"""Small dependency-free settings store: per-app JSON files in the platform config directory.

Used for lightweight, non-project preferences (e.g. the last connection settings) that should
survive restarts. Not for project data — that lives in the ``.xknx`` document."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

_APP = "knx-gui"


def config_dir() -> Path:
    """Platform-appropriate per-user config directory for this app."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif sys.platform == "win32":
        base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
    return base / _APP


def load_settings(name: str) -> dict[str, Any]:
    """Load ``<config_dir>/<name>.json`` as a dict, or an empty dict if missing/unreadable."""
    path = config_dir() / f"{name}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(name: str, data: dict[str, Any]) -> None:
    """Write ``data`` to ``<config_dir>/<name>.json`` (best effort; failures are ignored)."""
    path = config_dir() / f"{name}.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass
