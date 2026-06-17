"""Unit tests for desktop application configuration loading."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest


class TestDesktopConfig:
    """Tests for desktop_app.config module."""

    def test_load_config_returns_object(self, tmp_path):
        """load_config() returns a Config dataclass with expected fields."""
        from desktop_app.config import load_config, Config

        env = {
            "INTERVALS_API_KEY": "test-key",
            "INTERVALS_ATHLETE_ID": "i12345",
            "INTERVALS_API_BASE_URL": "https://intervals.icu/api/v1",
        }
        with patch.dict(os.environ, env, clear=False):
            cfg = load_config()
        assert isinstance(cfg, Config)

    def test_missing_required_env_raises(self):
        """load_config() raises ConfigError when required env vars are absent."""
        from desktop_app.config import load_config
        from desktop_app.errors import ConfigError

        env_clean = {
            k: "" for k in ("INTERVALS_API_KEY", "INTERVALS_ATHLETE_ID")
        }
        with patch.dict(os.environ, env_clean):
            with pytest.raises(ConfigError):
                load_config()

    def test_default_base_url(self):
        """load_config() applies default base URL when env var is absent."""
        from desktop_app.config import load_config, DEFAULT_BASE_URL

        env = {
            "INTERVALS_API_KEY": "test-key",
            "INTERVALS_ATHLETE_ID": "i12345",
        }
        with patch.dict(os.environ, env, clear=False):
            # Remove INTERVALS_API_BASE_URL if set
            os.environ.pop("INTERVALS_API_BASE_URL", None)
            cfg = load_config()
        assert cfg.base_url == DEFAULT_BASE_URL
