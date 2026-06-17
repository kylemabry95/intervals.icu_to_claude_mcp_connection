"""
Foundational integration tests: config, process lifecycle, secure storage.
"""

from __future__ import annotations

import os
import sys
import threading
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


# ── Config ────────────────────────────────────────────────────────────────────

class TestConfig:
    def test_load_config_valid_env(self, tmp_path):
        env = {
            "INTERVALS_API_KEY": "key-abc",
            "INTERVALS_ATHLETE_ID": "i99",
            "INTERVALS_API_BASE_URL": "https://intervals.icu/api/v1",
            "LOG_DIR": str(tmp_path),
        }
        with patch.dict(os.environ, env, clear=False):
            from desktop_app.config import load_config
            cfg = load_config()
        assert cfg.api_key == "key-abc"
        assert cfg.athlete_id == "i99"
        assert cfg.base_url == "https://intervals.icu/api/v1"

    def test_load_config_missing_raises(self):
        stripped = {k: "" for k in ("INTERVALS_API_KEY", "INTERVALS_ATHLETE_ID")}
        with patch.dict(os.environ, stripped, clear=False):
            os.environ.pop("INTERVALS_API_KEY", None)
            os.environ.pop("INTERVALS_ATHLETE_ID", None)
            from desktop_app.config import load_config
            from desktop_app.errors import ConfigError
            with pytest.raises(ConfigError):
                load_config()


# ── Secure storage ────────────────────────────────────────────────────────────

class TestCredentialStore:
    def test_set_get_delete_roundtrip(self):
        """CredentialStore round-trips a value via keyring (mocked)."""
        _store: dict[str, str] = {}

        mock_keyring = MagicMock()
        mock_keyring.set_password.side_effect = lambda svc, key, val: _store.update({key: val})
        mock_keyring.get_password.side_effect = lambda svc, key: _store.get(key)
        mock_keyring.delete_password.side_effect = lambda svc, key: _store.pop(key, None)

        with patch("desktop_app.security.credentials.CredentialStore._load_keyring", return_value=mock_keyring):
            from desktop_app.security.credentials import CredentialStore
            store = CredentialStore()
            store._keyring = mock_keyring

            store.set("test_key", "secret-value")
            assert store.get("test_key") == "secret-value"
            store.delete("test_key")
            assert store.get("test_key") is None

    def test_get_missing_returns_none(self):
        mock_keyring = MagicMock()
        mock_keyring.get_password.return_value = None

        from desktop_app.security.credentials import CredentialStore
        store = CredentialStore()
        store._keyring = mock_keyring

        result = store.get("nonexistent")
        assert result is None


# ── MCP Process lifecycle ─────────────────────────────────────────────────────

class TestMCPProcessManager:
    def test_start_stop_with_mock_script(self, tmp_path):
        """MCPProcessManager starts and stops a mock subprocess."""
        # Create a minimal "server" script that just sleeps
        script = tmp_path / "fake_server.py"
        script.write_text("import time\ntime.sleep(60)\n")

        from desktop_app.runtime.mcp_process import MCPProcessManager, ProcessState
        mgr = MCPProcessManager(server_script=script)
        mgr.start()
        assert mgr.state == ProcessState.RUNNING
        assert mgr.is_running
        assert mgr.pid is not None
        mgr.stop()
        assert mgr.state == ProcessState.STOPPED

    def test_health_check_true_when_running(self, tmp_path):
        script = tmp_path / "fake_server.py"
        script.write_text("import time\ntime.sleep(60)\n")

        from desktop_app.runtime.mcp_process import MCPProcessManager
        mgr = MCPProcessManager(server_script=script)
        mgr.start()
        try:
            assert mgr.health_check() is True
        finally:
            mgr.stop()

    def test_start_missing_script_raises(self, tmp_path):
        from desktop_app.runtime.mcp_process import MCPProcessManager
        from desktop_app.errors import MCPProcessError
        mgr = MCPProcessManager(server_script=tmp_path / "nonexistent.py")
        with pytest.raises(MCPProcessError):
            mgr.start()
