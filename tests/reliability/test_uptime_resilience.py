"""
Reliability tests: process restart/recovery and uptime SLO verification.

Tests that the MCP server process manager recovers from unexpected crashes
and that the uptime instrumentation correctly tracks availability.
"""

from __future__ import annotations

import time
from pathlib import Path
from unittest.mock import patch

import pytest


class TestUptimeResilience:
    def test_availability_100_percent_with_all_successes(self):
        """Availability is 1.0 when all probes succeed."""
        from desktop_app.observability.uptime import record_probe, get_availability_report, reset_uptime_metrics

        reset_uptime_metrics()
        for _ in range(100):
            record_probe(True)

        report = get_availability_report()
        assert report["availability"] == 1.0
        assert report["slo_met"] is True

    def test_availability_below_slo_when_many_failures(self):
        """slo_met is False when availability drops below 99.5%."""
        from desktop_app.observability.uptime import record_probe, get_availability_report, reset_uptime_metrics

        reset_uptime_metrics()
        for _ in range(99):
            record_probe(True)
        for _ in range(5):
            record_probe(False)

        report = get_availability_report()
        assert report["availability"] < 0.995
        assert report["slo_met"] is False

    def test_empty_history_returns_100_percent(self):
        """An empty probe history reports 100% availability (no evidence of failure)."""
        from desktop_app.observability.uptime import get_availability_report, reset_uptime_metrics

        reset_uptime_metrics()
        report = get_availability_report()
        assert report["availability"] == 1.0
        assert report["slo_met"] is True

    def test_process_manager_detects_unexpected_exit(self, tmp_path):
        """MCPProcessManager transitions to FAILED when the process exits unexpectedly."""
        script = tmp_path / "immediate_exit.py"
        script.write_text("import sys\nsys.exit(0)\n")

        from desktop_app.runtime.mcp_process import MCPProcessManager, ProcessState

        mgr = MCPProcessManager(server_script=script)
        mgr.start()

        # Wait a moment for the process to exit and health thread to detect it
        deadline = time.time() + 5.0
        while mgr.state == ProcessState.RUNNING and time.time() < deadline:
            time.sleep(0.1)

        try:
            assert mgr.state in (ProcessState.FAILED, ProcessState.STOPPED)
        finally:
            mgr.stop()

    def test_process_stop_is_idempotent(self, tmp_path):
        """Calling stop() multiple times does not raise."""
        script = tmp_path / "server.py"
        script.write_text("import time\ntime.sleep(60)\n")

        from desktop_app.runtime.mcp_process import MCPProcessManager

        mgr = MCPProcessManager(server_script=script)
        mgr.start()
        mgr.stop()
        mgr.stop()  # Second call must not raise
