"""
Settings repository: persistent JSON-backed preference store.

Stores application preferences (log level, update policy, etc.) in a
JSON file under the platform application data directory.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any, Optional

_SETTINGS_FILE = "settings.json"


class SettingsRepository:
    """JSON-backed key/value preference store.

    Args:
        settings_dir: Directory where ``settings.json`` is written.
                      Defaults to the platform application data directory.
    """

    def __init__(self, settings_dir: Optional[str] = None) -> None:
        if settings_dir is None:
            settings_dir = str(self._default_dir())
        self._path = Path(settings_dir) / _SETTINGS_FILE
        self._lock = threading.Lock()
        self._data: dict[str, Any] = self._load()

    # ── Public API ─────────────────────────────────────────────────────────────

    def get(self, key: str, default: Any = None) -> Any:
        """Return the value stored under *key*, or *default* if absent."""
        with self._lock:
            return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Store *value* under *key* and persist to disk."""
        with self._lock:
            self._data[key] = value
            self._save()

    def delete(self, key: str) -> None:
        """Remove *key* from preferences if present."""
        with self._lock:
            self._data.pop(key, None)
            self._save()

    def all(self) -> dict[str, Any]:
        """Return a snapshot of all current preferences."""
        with self._lock:
            return dict(self._data)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load(self) -> dict[str, Any]:
        if not self._path.exists():
            return {}
        try:
            with self._path.open(encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            return {}

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("w", encoding="utf-8") as fh:
            json.dump(self._data, fh, indent=2)

    @staticmethod
    def _default_dir() -> Path:
        import platform
        import os

        system = platform.system()
        if system == "Darwin":
            return Path.home() / "Library" / "Application Support" / "IntervalsICU"
        if system == "Windows":
            appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
            return Path(appdata) / "IntervalsICU"
        return Path.home() / ".config" / "IntervalsICU"
