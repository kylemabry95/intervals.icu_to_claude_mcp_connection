"""
Desktop application configuration loader and validator.

Reads configuration from environment variables (.env file or real env).
Falls back to sensible defaults where appropriate.
"""

from __future__ import annotations

import os
import platform
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from desktop_app.errors import ConfigError

DEFAULT_BASE_URL = "https://intervals.icu/api/v1"
DEFAULT_ANTHROPIC_MODEL = "claude-3-5-sonnet-20241022"


def _default_log_dir() -> str:
    system = platform.system()
    if system == "Darwin":
        log_root = Path.home() / "Library" / "Logs" / "IntervalsICU"
    elif system == "Windows":
        appdata = os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming"))
        log_root = Path(appdata) / "IntervalsICU" / "Logs"
    else:
        log_root = Path(tempfile.gettempdir()) / "IntervalsICU" / "logs"
    log_root.mkdir(parents=True, exist_ok=True)
    return str(log_root)


@dataclass
class Config:
    """Validated runtime configuration for the desktop application."""

    api_key: str
    athlete_id: str
    base_url: str = DEFAULT_BASE_URL
    anthropic_api_key: str = ""
    anthropic_model: str = DEFAULT_ANTHROPIC_MODEL
    log_dir: str = field(default_factory=_default_log_dir)
    log_level: str = "INFO"
    update_check_enabled: bool = True


def _load_dotenv() -> None:
    """Load .env from the project root if present (without requiring python-dotenv)."""
    env_path = Path.cwd() / ".env"
    if not env_path.exists():
        return
    with env_path.open() as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and key not in os.environ:
                os.environ[key] = value


def load_config() -> Config:
    """Load and validate desktop app configuration from the environment.

    Raises:
        ConfigError: When required environment variables are missing or invalid.
    """
    _load_dotenv()

    api_key = os.environ.get("INTERVALS_API_KEY", "").strip()
    athlete_id = os.environ.get("INTERVALS_ATHLETE_ID", "").strip()

    missing = [name for name, val in [
        ("INTERVALS_API_KEY", api_key),
        ("INTERVALS_ATHLETE_ID", athlete_id),
    ] if not val]
    if missing:
        raise ConfigError(
            f"Missing required environment variable(s): {', '.join(missing)}. "
            "Copy .env.example to .env and fill in your credentials."
        )

    return Config(
        api_key=api_key,
        athlete_id=athlete_id,
        base_url=os.environ.get("INTERVALS_API_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL,
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY", "").strip(),
        anthropic_model=os.environ.get("ANTHROPIC_MODEL", DEFAULT_ANTHROPIC_MODEL).strip() or DEFAULT_ANTHROPIC_MODEL,
        log_dir=os.environ.get("LOG_DIR", "").strip() or _default_log_dir(),
        log_level=os.environ.get("LOG_LEVEL", "INFO").strip().upper(),
        update_check_enabled=os.environ.get("UPDATE_CHECK_ENABLED", "true").lower() == "true",
    )
