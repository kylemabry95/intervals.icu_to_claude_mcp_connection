"""
Authentication screen UI.

Provides the login form where users enter their intervals.icu API key
and athlete ID.  On successful verification, credentials are persisted
via ``AuthSession`` and the shell is directed to the chat view.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from desktop_app.config import Config


class AuthView:
    """Login / API-key entry form."""

    def __init__(self, parent: tk.Widget, config: "Config") -> None:
        self._config = config
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self) -> None:
        pad = {"padx": 20, "pady": 8}

        ttk.Label(
            self.frame,
            text="Connect to intervals.icu",
            font=("", 14, "bold"),
        ).pack(**pad, anchor="w")

        ttk.Label(
            self.frame,
            text=(
                "Enter your intervals.icu API key and athlete ID to get started.\n"
                "You can find your API key in Settings → API on intervals.icu."
            ),
            wraplength=520,
            justify="left",
        ).pack(**pad, anchor="w")

        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", padx=20, pady=4)

        # ── API Key field ──────────────────────────────────────────────────────
        ttk.Label(self.frame, text="API Key:").pack(**pad, anchor="w")
        self._api_key_var = tk.StringVar(value=self._config.api_key or "")
        key_entry = ttk.Entry(self.frame, textvariable=self._api_key_var, width=50, show="*")
        key_entry.pack(**pad, anchor="w")

        # ── Athlete ID field ───────────────────────────────────────────────────
        ttk.Label(self.frame, text="Athlete ID (e.g. i12345):").pack(**pad, anchor="w")
        self._athlete_id_var = tk.StringVar(value=self._config.athlete_id or "")
        id_entry = ttk.Entry(self.frame, textvariable=self._athlete_id_var, width=30)
        id_entry.pack(**pad, anchor="w")

        # ── Error area ─────────────────────────────────────────────────────────
        self._error_label = ttk.Label(self.frame, text="", foreground="red", wraplength=520)
        self._error_label.pack(**pad, anchor="w")

        # ── Action buttons ─────────────────────────────────────────────────────
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(**pad, anchor="w")

        ttk.Button(btn_frame, text="Sign In", command=self._on_sign_in).pack(side="left", padx=(0, 8))
        ttk.Button(btn_frame, text="Clear", command=self._on_clear).pack(side="left")

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_sign_in(self) -> None:
        from desktop_app.auth.service import AuthService
        from desktop_app.auth.session import AuthSession
        from desktop_app.security.credentials import CredentialStore
        from desktop_app.errors import AuthError
        from desktop_app.ui.components.auth_errors import AUTH_ERROR_HINTS

        api_key = self._api_key_var.get().strip()
        athlete_id = self._athlete_id_var.get().strip()

        svc = AuthService(base_url=self._config.base_url)
        try:
            svc.verify(api_key, athlete_id)
        except AuthError as exc:
            hint = AUTH_ERROR_HINTS.get(type(exc), "")
            self._show_error(f"{exc.user_message}\n{hint}" if hint else exc.user_message)
            return

        store = CredentialStore()
        session = AuthSession(credential_store=store)
        session.login(api_key=api_key, athlete_id=athlete_id)
        self._show_error("")
        messagebox.showinfo("Signed In", "Successfully connected to intervals.icu!")

    def _on_clear(self) -> None:
        self._api_key_var.set("")
        self._athlete_id_var.set("")
        self._show_error("")

    def _show_error(self, message: str) -> None:
        self._error_label.config(text=message)
