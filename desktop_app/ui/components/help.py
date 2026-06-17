"""
Reusable tooltip and help-popover components.

Provides:
  - ``TOOLTIP_REGISTRY``    — dict mapping field names to tooltip texts
  - ``ToolTip``             — tkinter hover tooltip widget
  - ``attach_tooltip()``    — convenience function to bind a tooltip to a widget
"""

from __future__ import annotations

import tkinter as tk
from typing import Optional

# ── Tooltip registry ──────────────────────────────────────────────────────────
# Keys match field identifiers used in auth, settings, and chat views.

TOOLTIP_REGISTRY: dict[str, str] = {
    "api_key": (
        "Your intervals.icu API key. "
        "Found in Settings → API on intervals.icu. Keep it private."
    ),
    "athlete_id": (
        "Your athlete ID starts with 'i' followed by digits (e.g. i12345). "
        "Visible in your intervals.icu profile URL."
    ),
    "log_level": (
        "Controls the verbosity of application logs. "
        "Use DEBUG for troubleshooting, INFO for normal operation."
    ),
    "update_check": (
        "When enabled, the application checks for a new version once per day "
        "and prompts you to download it."
    ),
    "anthropic_api_key": (
        "Your Anthropic Claude API key. Required for the chat feature. "
        "Get one at https://console.anthropic.com."
    ),
    "chat_input": (
        "Type a question about your intervals.icu training data and press Enter or Send."
    ),
}


class ToolTip:
    """Hover tooltip that appears near the widget after a short delay.

    Args:
        widget:  Target tkinter widget.
        text:    Tooltip text to display.
        delay_ms: Milliseconds before the tooltip appears (default 600ms).
    """

    def __init__(self, widget: tk.Widget, text: str, delay_ms: int = 600) -> None:
        self._widget = widget
        self._text = text
        self._delay_ms = delay_ms
        self._tip_window: Optional[tk.Toplevel] = None
        self._after_id: Optional[str] = None

        widget.bind("<Enter>", self._schedule_show)
        widget.bind("<Leave>", self._hide)

    def _schedule_show(self, _event=None) -> None:
        self._cancel()
        self._after_id = self._widget.after(self._delay_ms, self._show)

    def _show(self) -> None:
        if self._tip_window or not self._text:
            return
        x = self._widget.winfo_rootx() + 20
        y = self._widget.winfo_rooty() + self._widget.winfo_height() + 4
        self._tip_window = tw = tk.Toplevel(self._widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self._text,
            justify=tk.LEFT,
            background="#ffffe0",
            relief=tk.SOLID,
            borderwidth=1,
            font=("", 9),
            wraplength=280,
        )
        label.pack(ipadx=4, ipady=2)

    def _hide(self, _event=None) -> None:
        self._cancel()
        if self._tip_window:
            self._tip_window.destroy()
            self._tip_window = None

    def _cancel(self) -> None:
        if self._after_id:
            self._widget.after_cancel(self._after_id)
            self._after_id = None


def attach_tooltip(widget: tk.Widget, key: str) -> Optional[ToolTip]:
    """Attach a tooltip from the registry to *widget* by *key*.

    Returns the ``ToolTip`` instance, or ``None`` if *key* is not registered.
    """
    text = TOOLTIP_REGISTRY.get(key)
    if text:
        return ToolTip(widget, text)
    return None
