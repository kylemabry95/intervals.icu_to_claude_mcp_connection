"""
Unavailable-data fallback handling.

When Claude returns an empty response or a query cannot be completed,
``handle_fallback()`` returns a user-friendly message explaining
the situation and suggesting next steps.
"""

from __future__ import annotations


_GENERIC_FALLBACK = (
    "I wasn't able to retrieve a response for your query. "
    "Please check your internet connection and API key, then try again.\n\n"
    "If the problem persists, you can view your data directly at "
    "https://intervals.icu."
)

# Keyword-based hints for specific common failure modes
_HINTS: list[tuple[list[str], str]] = [
    (
        ["ftp", "threshold", "power"],
        "To view your FTP, go to intervals.icu → Settings → Zones.",
    ),
    (
        ["wellness", "hrv", "sleep", "weight"],
        "Wellness data must be logged on intervals.icu before it can be retrieved.",
    ),
    (
        ["activity", "ride", "run", "workout"],
        "Activities are synced from your connected devices and apps on intervals.icu.",
    ),
]


def handle_fallback(user_message: str) -> str:
    """Return a user-friendly fallback message for an unanswered query.

    Uses simple keyword matching to provide a context-relevant hint
    alongside the generic fallback text.

    Args:
        user_message: The original user query that went unanswered.

    Returns:
        A fallback string suitable for display in the chat UI.
    """
    lower = user_message.lower()
    for keywords, hint in _HINTS:
        if any(kw in lower for kw in keywords):
            return f"{_GENERIC_FALLBACK}\n\nHint: {hint}"
    return _GENERIC_FALLBACK
