"""Integration test: app launch and graceful shutdown lifecycle."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest


class TestLaunchShutdown:
    def test_startup_sequence_completes(self, tmp_path):
        """run_startup_sequence() succeeds with a valid config."""
        from desktop_app.config import Config
        from desktop_app.runtime.startup import run_startup_sequence

        cfg = Config(
            api_key="key",
            athlete_id="i1",
            log_dir=str(tmp_path),
        )

        with patch("desktop_app.runtime.startup.MCPProcessManager") as MockMgr:
            MockMgr.return_value.start = MagicMock()
            run_startup_sequence(cfg)  # must not raise

    def test_graceful_shutdown_stops_mcp(self, tmp_path):
        """Shutdown calls MCPProcessManager.stop()."""
        from desktop_app.config import Config
        from desktop_app.runtime.startup import run_startup_sequence, shutdown

        cfg = Config(
            api_key="key",
            athlete_id="i1",
            log_dir=str(tmp_path),
        )

        mock_mgr = MagicMock()
        with patch("desktop_app.runtime.startup.MCPProcessManager", return_value=mock_mgr):
            run_startup_sequence(cfg)
            shutdown()

        mock_mgr.stop.assert_called_once()

    def test_startup_configures_logging(self, tmp_path):
        """run_startup_sequence() configures the logging subsystem."""
        from desktop_app.config import Config
        from desktop_app.runtime.startup import run_startup_sequence

        cfg = Config(
            api_key="key",
            athlete_id="i1",
            log_dir=str(tmp_path),
        )

        with patch("desktop_app.runtime.startup.MCPProcessManager"):
            with patch("desktop_app.runtime.startup.configure_logging") as mock_log:
                run_startup_sequence(cfg)
                mock_log.assert_called_once()
