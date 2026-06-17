"""
Error-to-help link mapping.

Maps application error types to contextual help content and remediation
links. Used by UI views to show actionable guidance when errors occur.
"""

from __future__ import annotations

from desktop_app.errors import (
    AppError,
    AuthError,
    ClaudeBridgeError,
    ConfigError,
    ConversationError,
    CredentialError,
    MCPProcessError,
    UpdateCheckError,
)

# Each entry: (help_context, remediation_text, optional_url)
ErrorGuidance = tuple[str, str, str]

ERROR_GUIDANCE: dict[type[AppError], ErrorGuidance] = {
    ConfigError: (
        "settings",
        "Open Settings and verify your API key and athlete ID are correct.",
        "",
    ),
    CredentialError: (
        "settings",
        "The system keychain could not be accessed. "
        "Check Keychain Access (macOS) or Credential Manager (Windows).",
        "",
    ),
    AuthError: (
        "auth",
        "Check your API key and athlete ID. "
        "Your key is in intervals.icu → Settings → API.",
        "https://intervals.icu/settings",
    ),
    ClaudeBridgeError: (
        "settings",
        "Verify your Anthropic API key in Settings and check your internet connection.",
        "https://console.anthropic.com",
    ),
    MCPProcessError: (
        "help",
        "The background service failed. Try restarting the application. "
        "If the problem persists, reinstall the application.",
        "",
    ),
    ConversationError: (
        "chat",
        "The query could not be completed. Check your connection and try again.",
        "",
    ),
    UpdateCheckError: (
        "help",
        "Update check failed. This is non-critical; check your internet connection.",
        "",
    ),
}


def get_guidance(error: AppError) -> ErrorGuidance:
    """Return help context, remediation text, and URL for *error*.

    Falls back to a generic help context if the error type is not mapped.
    """
    return ERROR_GUIDANCE.get(
        type(error),
        ("help", error.user_message, ""),
    )
