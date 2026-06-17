"""
Settings panel UI.

Provides a tkinter form for managing:
  - API key and athlete ID
  - Log level preference
  - Update check enable/disable toggle
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from desktop_app.config import Config


class SettingsView:
    """Application settings panel."""

    def __init__(self, parent: tk.Widget, config: "Config") -> None:
        self._config = config
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self) -> None:
        pad = {"padx": 20, "pady": 8}

        ttk.Label(self.frame, text="Settings", font=("", 14, "bold")).pack(**pad, anchor="w")
        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", padx=20, pady=4)

        # ── API Key ────────────────────────────────────────────────────────────
        ttk.Label(self.frame, text="API Key:").pack(**pad, anchor="w")
        self._api_key_var = tk.StringVar(value=self._config.api_key or "")
        ttk.Entry(self.frame, textvariable=self._api_key_var, width=50, show="*").pack(**pad, anchor="w")

        # ── Athlete ID ─────────────────────────────────────────────────────────
        ttk.Label(self.frame, text="Athlete ID:").pack(**pad, anchor="w")
        self._athlete_id_var = tk.StringVar(value=self._config.athlete_id or "")
        ttk.Entry(self.frame, textvariable=self._athlete_id_var, width=30).pack(**pad, anchor="w")

        # ── Log Level ──────────────────────────────────────────────────────────
        ttk.Label(self.frame, text="Log Level:").pack(**pad, anchor="w")
        self._log_level_var = tk.StringVar(value=self._config.log_level)
        log_combo = ttk.Combobox(
            self.frame,
            textvariable=self._log_level_var,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            state="readonly",
            width=12,
        )
        log_combo.pack(**pad, anchor="w")

        # ── Update checks ──────────────────────────────────────────────────────
        self._update_check_var = tk.BooleanVar(value=self._config.update_check_enabled)
        ttk.Checkbutton(
            self.frame,
            text="Check for updates daily",
            variable=self._update_check_var,
        ).pack(**pad, anchor="w")

        # ── Status ────────────────────────────────────────────────────────────
        self._status_var = tk.StringVar(value="")
        ttk.Label(self.frame, textvariable=self._status_var, foreground="green").pack(**pad, anchor="w")

        # ── Save button ────────────────────────────────────────────────────────
        ttk.Button(self.frame, text="Save Settings", command=self._on_save).pack(**pad, anchor="w")

    def _on_save(self) -> None:
        from desktop_app.security.credentials import CredentialStore
        from desktop_app.auth.session import AuthSession
        from desktop_app.settings.service import SettingsService
        from desktop_app.errors import AuthError

        api_key = self._api_key_var.get().strip()
        athlete_id = self._athlete_id_var.get().strip()

        try:
            cred_store = CredentialStore()
            session = AuthSession(credential_store=cred_store)
            svc = SettingsService(auth_session=session)
            svc.update_api_key(api_key, athlete_id)
            self._status_var.set("Settings saved.")
        except AuthError as exc:
            messagebox.showerror("Save Error", exc.user_message)
