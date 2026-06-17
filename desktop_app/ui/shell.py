"""
Main application shell window (AppShell).

The AppShell is the top-level tkinter window.  It hosts a simple notebook
with four tab frames:

  - Chat  (ConversationView)
  - Auth  (AuthView)
  - Settings (SettingsView)
  - Help  (HelpView)

The shell routes between tabs and passes the shared Config to each view.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from desktop_app.config import Config

_APP_TITLE = "intervals.icu — Claude Assistant"
_MIN_WIDTH = 800
_MIN_HEIGHT = 600


class AppShell:
    """Top-level application window."""

    def __init__(self, config: "Config") -> None:
        self._config = config
        self._root = tk.Tk()
        self._root.title(_APP_TITLE)
        self._root.minsize(_MIN_WIDTH, _MIN_HEIGHT)
        self._root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._build_ui()

    # ── Public API ─────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Enter the tkinter main-event loop (blocks until window is closed)."""
        self._root.mainloop()

    def navigate_to(self, tab_name: str) -> None:
        """Switch to a named tab (``"chat"``, ``"auth"``, ``"settings"``, ``"help"``)."""
        tab_map = {
            "chat": 0,
            "auth": 1,
            "settings": 2,
            "help": 3,
        }
        idx = tab_map.get(tab_name.lower())
        if idx is not None:
            self._notebook.select(idx)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self._notebook = ttk.Notebook(self._root)
        self._notebook.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        # Lazy import views here to avoid circular imports at module load time
        from desktop_app.ui.chat_view import ChatView
        from desktop_app.ui.auth_view import AuthView
        from desktop_app.ui.settings_view import SettingsView
        from desktop_app.ui.help_integration import HelpView

        self._chat_view = ChatView(self._notebook, self._config)
        self._auth_view = AuthView(self._notebook, self._config)
        self._settings_view = SettingsView(self._notebook, self._config)
        self._help_view = HelpView(self._notebook, self._config)

        self._notebook.add(self._chat_view.frame, text="Chat")
        self._notebook.add(self._auth_view.frame, text="Sign In")
        self._notebook.add(self._settings_view.frame, text="Settings")
        self._notebook.add(self._help_view.frame, text="Help")

    def _on_close(self) -> None:
        self._root.quit()
        self._root.destroy()
