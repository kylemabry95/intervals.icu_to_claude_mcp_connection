"""Integration test: log viewer renders application log entries."""

from __future__ import annotations

import logging
from pathlib import Path


class TestSettingsLogs:
    def test_log_viewer_reads_log_file(self, tmp_path):
        """LogViewer loads and returns lines from the application log file."""
        log_file = tmp_path / "intervals_icu_desktop.log"
        log_file.write_text("2026-06-16T10:00:00 INFO test - Application started\n"
                            "2026-06-16T10:00:01 WARNING test - Retrying connection\n")

        from desktop_app.ui.components.log_viewer import LogViewerModel

        model = LogViewerModel(log_dir=str(tmp_path))
        lines = model.load_lines()
        assert len(lines) == 2
        assert "Application started" in lines[0]

    def test_log_viewer_filters_by_level(self, tmp_path):
        """LogViewer can filter by log level."""
        log_file = tmp_path / "intervals_icu_desktop.log"
        log_file.write_text(
            "2026-06-16T10:00:00 INFO test - ok\n"
            "2026-06-16T10:00:01 WARNING test - warn\n"
            "2026-06-16T10:00:02 ERROR test - err\n"
        )

        from desktop_app.ui.components.log_viewer import LogViewerModel

        model = LogViewerModel(log_dir=str(tmp_path))
        warnings_and_above = model.load_lines(min_level="WARNING")
        for line in warnings_and_above:
            assert "INFO" not in line or "WARNING" in line or "ERROR" in line

    def test_log_viewer_empty_when_no_file(self, tmp_path):
        """LogViewer returns an empty list when no log file exists."""
        from desktop_app.ui.components.log_viewer import LogViewerModel

        model = LogViewerModel(log_dir=str(tmp_path))
        assert model.load_lines() == []
