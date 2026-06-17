"""
In-app log viewer widget with level filtering.

Provides:
  - ``LogViewerModel`` — reads and filters log file lines
  - ``LogViewerWidget`` — tkinter widget for the settings panel
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path
from typing import Optional

_LOG_FILE = "intervals_icu_desktop.log"
_LEVEL_ORDER = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}


class LogViewerModel:
    """Reads and filters lines from the application log file.

    Args:
        log_dir: Directory containing the log file.
    """

    def __init__(self, log_dir: str) -> None:
        self._log_path = Path(log_dir) / _LOG_FILE

    def load_lines(self, min_level: str = "DEBUG", max_lines: int = 500) -> list[str]:
        """Load and optionally filter log lines.

        Args:
            min_level: Minimum log level to include (DEBUG/INFO/WARNING/ERROR).
            max_lines: Maximum number of lines to return (most recent).

        Returns:
            List of matching log lines.
        """
        if not self._log_path.exists():
            return []

        min_order = _LEVEL_ORDER.get(min_level.upper(), 0)
        lines: list[str] = []

        try:
            with self._log_path.open(encoding="utf-8", errors="replace") as fh:
                for raw_line in fh:
                    line = raw_line.rstrip()
                    # Check if the line contains a level token we can compare
                    level_found = False
                    for level, order in _LEVEL_ORDER.items():
                        if f" {level} " in line or f" {level}\t" in line:
                            if order >= min_order:
                                lines.append(line)
                            level_found = True
                            break
                    if not level_found:
                        # Unknown level format — include it
                        lines.append(line)
        except OSError:
            return []

        return lines[-max_lines:]


class LogViewerWidget:
    """Embedded log viewer for the settings panel."""

    def __init__(self, parent: tk.Widget, log_dir: str) -> None:
        self._model = LogViewerModel(log_dir=log_dir)
        self.frame = ttk.LabelFrame(parent, text="Application Logs")
        self._build()

    def _build(self) -> None:
        # ── Filter controls ───────────────────────────────────────────────────
        ctrl_frame = ttk.Frame(self.frame)
        ctrl_frame.pack(fill="x", padx=8, pady=4)

        ttk.Label(ctrl_frame, text="Min level:").pack(side="left")
        self._level_var = tk.StringVar(value="INFO")
        ttk.Combobox(
            ctrl_frame,
            textvariable=self._level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=10,
        ).pack(side="left", padx=4)
        ttk.Button(ctrl_frame, text="Refresh", command=self._refresh).pack(side="left")

        # ── Text area ─────────────────────────────────────────────────────────
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        self._text = tk.Text(text_frame, state=tk.DISABLED, height=12, font=("Courier", 9))
        scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self._text.yview)
        self._text.configure(yscrollcommand=scroll.set)
        self._text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._refresh()

    def _refresh(self) -> None:
        lines = self._model.load_lines(min_level=self._level_var.get())
        self._text.config(state=tk.NORMAL)
        self._text.delete("1.0", tk.END)
        self._text.insert(tk.END, "\n".join(lines) if lines else "(no log entries)")
        self._text.see(tk.END)
        self._text.config(state=tk.DISABLED)
