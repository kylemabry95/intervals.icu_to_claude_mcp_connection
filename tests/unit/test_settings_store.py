"""Unit tests for settings persistence and preference schema."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


class TestSettingsStore:
    def test_save_and_load_roundtrip(self, tmp_path):
        """Settings saved to disk are restored correctly."""
        from desktop_app.settings.repository import SettingsRepository

        repo = SettingsRepository(settings_dir=str(tmp_path))
        repo.set("log_level", "DEBUG")
        repo.set("update_check_enabled", True)

        repo2 = SettingsRepository(settings_dir=str(tmp_path))
        assert repo2.get("log_level") == "DEBUG"
        assert repo2.get("update_check_enabled") is True

    def test_default_returned_when_key_missing(self, tmp_path):
        """get() returns the default value when a key has not been set."""
        from desktop_app.settings.repository import SettingsRepository

        repo = SettingsRepository(settings_dir=str(tmp_path))
        assert repo.get("nonexistent_key", default="fallback") == "fallback"

    def test_settings_file_is_json(self, tmp_path):
        """The settings file is valid JSON."""
        from desktop_app.settings.repository import SettingsRepository

        repo = SettingsRepository(settings_dir=str(tmp_path))
        repo.set("key", "value")
        settings_file = tmp_path / "settings.json"
        assert settings_file.exists()
        data = json.loads(settings_file.read_text())
        assert data["key"] == "value"

    def test_set_multiple_keys(self, tmp_path):
        from desktop_app.settings.repository import SettingsRepository

        repo = SettingsRepository(settings_dir=str(tmp_path))
        repo.set("a", 1)
        repo.set("b", "two")
        repo.set("c", False)
        assert repo.get("a") == 1
        assert repo.get("b") == "two"
        assert repo.get("c") is False
