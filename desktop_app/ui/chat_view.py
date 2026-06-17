"""
Chat view: streaming conversation UI for Claude queries.

Provides a tkinter-based chat interface with:
  - Message history display (scrollable)
  - Text input with Send button
  - Streaming/thinking state indicator
  - Clear history button
"""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from desktop_app.config import Config

_THINKING_MSG = "Claude is thinking…"


class ChatView:
    """Chat conversation panel."""

    def __init__(self, parent: tk.Widget, config: "Config") -> None:
        self._config = config
        self.frame = ttk.Frame(parent)
        self._service = None  # Lazy-init on first query
        self._build()

    # ── Build UI ───────────────────────────────────────────────────────────────

    def _build(self) -> None:
        # ── History area ──────────────────────────────────────────────────────
        history_frame = ttk.Frame(self.frame)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 4))

        self._history_text = tk.Text(
            history_frame,
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg="#f9f9f9",
            font=("", 11),
        )
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self._history_text.yview)
        self._history_text.configure(yscrollcommand=scrollbar.set)
        self._history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure text tags for roles
        self._history_text.tag_configure("user", foreground="#1a1a1a", font=("", 11, "bold"))
        self._history_text.tag_configure("assistant", foreground="#0055a4")
        self._history_text.tag_configure("system", foreground="#888888", font=("", 10, "italic"))

        # ── Status bar ────────────────────────────────────────────────────────
        self._status_var = tk.StringVar(value="")
        ttk.Label(self.frame, textvariable=self._status_var, foreground="#888888").pack(
            anchor="w", padx=8
        )

        # ── Input area ────────────────────────────────────────────────────────
        input_frame = ttk.Frame(self.frame)
        input_frame.pack(fill=tk.X, padx=8, pady=(0, 8))

        self._input_var = tk.StringVar()
        self._input_entry = ttk.Entry(input_frame, textvariable=self._input_var, font=("", 11))
        self._input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self._input_entry.bind("<Return>", lambda _: self._on_send())

        self._send_btn = ttk.Button(input_frame, text="Send", command=self._on_send)
        self._send_btn.pack(side=tk.LEFT)

        ttk.Button(input_frame, text="Clear", command=self._on_clear).pack(side=tk.LEFT, padx=(4, 0))

        self._append_system("Ask Claude anything about your intervals.icu training data.")

    # ── Handlers ──────────────────────────────────────────────────────────────

    def _on_send(self) -> None:
        user_text = self._input_var.get().strip()
        if not user_text:
            return

        self._input_var.set("")
        self._append_message("You", user_text, "user")
        self._set_loading(True)

        def run_query():
            try:
                svc = self._get_service()
                reply = svc.query(user_text)
                self.frame.after(0, lambda: self._append_message("Claude", reply, "assistant"))
            except Exception as exc:
                from desktop_app.errors import AppError
                msg = exc.user_message if isinstance(exc, AppError) else str(exc)  # type: ignore[attr-defined]
                self.frame.after(0, lambda: self._append_system(f"Error: {msg}"))
            finally:
                self.frame.after(0, lambda: self._set_loading(False))

        threading.Thread(target=run_query, daemon=True).start()

    def _on_clear(self) -> None:
        if self._service:
            self._service.clear_history()
        self._history_text.config(state=tk.NORMAL)
        self._history_text.delete("1.0", tk.END)
        self._history_text.config(state=tk.DISABLED)
        self._append_system("Conversation cleared.")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _get_service(self):
        if self._service is None:
            from anthropic import Anthropic
            from desktop_app.conversation.service import ConversationService

            client = Anthropic(api_key=self._config.anthropic_api_key)
            self._service = ConversationService(
                client=client,
                model=self._config.anthropic_model,
            )
        return self._service

    def _set_loading(self, loading: bool) -> None:
        self._send_btn.config(state=tk.DISABLED if loading else tk.NORMAL)
        self._status_var.set(_THINKING_MSG if loading else "")

    def _append_message(self, sender: str, text: str, tag: str) -> None:
        self._history_text.config(state=tk.NORMAL)
        self._history_text.insert(tk.END, f"{sender}: ", tag)
        self._history_text.insert(tk.END, f"{text}\n\n")
        self._history_text.see(tk.END)
        self._history_text.config(state=tk.DISABLED)

    def _append_system(self, text: str) -> None:
        self._history_text.config(state=tk.NORMAL)
        self._history_text.insert(tk.END, f"{text}\n\n", "system")
        self._history_text.see(tk.END)
        self._history_text.config(state=tk.DISABLED)
