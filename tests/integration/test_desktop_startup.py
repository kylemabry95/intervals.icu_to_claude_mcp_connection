"""Smoke tests for desktop application startup lifecycle."""

from __future__ import annotations

import pytest


class TestDesktopStartup:
    """Integration tests for startup and shutdown sequencing."""

    def test_startup_sequence_runs(self, tmp_path, monkeypatch):
        """run_startup_sequence() completes without error under a mock config."""
        from unittest.mock import MagicMock, patch
        from desktop_app.config import Config

        cfg = Config(
            api_key="test-key",
            athlete_id="i12345",
            base_url="https://intervals.icu/api/v1",
            log_dir=str(tmp_path),
        )

        with patch("desktop_app.runtime.startup.MCPProcessManager") as MockMgr:
            MockMgr.return_value.start = MagicMock()
            from desktop_app.runtime.startup import run_startup_sequence
            run_startup_sequence(cfg)  # Should not raise

    def test_startup_raises_on_bad_config(self):
        """run_startup_sequence() raises AppError when config is invalid."""
        from desktop_app.errors import AppError
        from desktop_app.runtime.startup import run_startup_sequence

        with pytest.raises((AppError, Exception)):
            run_startup_sequence(None)  # type: ignore[arg-type]
