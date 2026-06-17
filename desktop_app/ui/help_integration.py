"""
Help tab: contextual help integration and FAQ view.

The HelpView is the "Help" tab in the AppShell. It displays:
  - Context-sensitive help for the currently active tab
  - A scrollable FAQ section
  - A link to the online documentation
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from desktop_app.config import Config


class HelpView:
    """Help tab panel with FAQ and contextual guidance."""

    def __init__(self, parent: tk.Widget, config: "Config") -> None:
        self._config = config
        self.frame = ttk.Frame(parent)
        self._build()

    def _build(self) -> None:
        pad = {"padx": 20, "pady": 8}

        ttk.Label(self.frame, text="Help & Guidance", font=("", 14, "bold")).pack(**pad, anchor="w")
        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", padx=20, pady=4)

        # ── Context selector ──────────────────────────────────────────────────
        ctx_frame = ttk.Frame(self.frame)
        ctx_frame.pack(**pad, anchor="w")
        ttk.Label(ctx_frame, text="Topic:").pack(side="left")
        self._ctx_var = tk.StringVar(value="chat")
        combo = ttk.Combobox(
            ctx_frame,
            textvariable=self._ctx_var,
            values=["auth", "chat", "settings", "help"],
            state="readonly",
            width=14,
        )
        combo.pack(side="left", padx=6)
        combo.bind("<<ComboboxSelected>>", lambda _: self._refresh_help())

        # ── Help text ─────────────────────────────────────────────────────────
        self._help_text = tk.Text(
            self.frame,
            state=tk.DISABLED,
            height=8,
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg="#f9f9f9",
            font=("", 10),
        )
        self._help_text.pack(fill=tk.X, padx=20, pady=(0, 8))

        ttk.Separator(self.frame, orient="horizontal").pack(fill="x", padx=20, pady=4)

        # ── FAQ ───────────────────────────────────────────────────────────────
        ttk.Label(self.frame, text="Frequently Asked Questions", font=("", 12, "bold")).pack(
            **pad, anchor="w"
        )

        faq_frame = ttk.Frame(self.frame)
        faq_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 12))

        faq_scroll = ttk.Scrollbar(faq_frame, orient="vertical")
        self._faq_text = tk.Text(
            faq_frame,
            state=tk.DISABLED,
            wrap=tk.WORD,
            relief=tk.FLAT,
            bg="#f9f9f9",
            font=("", 10),
            yscrollcommand=faq_scroll.set,
        )
        faq_scroll.config(command=self._faq_text.yview)
        self._faq_text.pack(side="left", fill=tk.BOTH, expand=True)
        faq_scroll.pack(side="right", fill="y")

        self._refresh_help()
        self._populate_faq()

    def _refresh_help(self) -> None:
        from desktop_app.help.content import HelpContentProvider
        provider = HelpContentProvider()
        text = provider.get_help(self._ctx_var.get())
        self._help_text.config(state=tk.NORMAL)
        self._help_text.delete("1.0", tk.END)
        self._help_text.insert(tk.END, text)
        self._help_text.config(state=tk.DISABLED)

    def _populate_faq(self) -> None:
        from desktop_app.help.content import HelpContentProvider
        provider = HelpContentProvider()
        self._faq_text.config(state=tk.NORMAL)
        self._faq_text.delete("1.0", tk.END)
        for entry in provider.get_faq():
            self._faq_text.insert(tk.END, f"Q: {entry['question']}\n", "question")
            self._faq_text.insert(tk.END, f"A: {entry['answer']}\n\n")
        self._faq_text.tag_configure("question", font=("", 10, "bold"))
        self._faq_text.config(state=tk.DISABLED)
