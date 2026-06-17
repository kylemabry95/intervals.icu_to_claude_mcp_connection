"""
Shared error model for the desktop application.

Defines the error hierarchy and user-safe message mapping.
All AppError subclasses carry a ``user_message`` suitable for display
in the UI (no internal details, stack traces, or credentials).
"""

from __future__ import annotations


class AppError(Exception):
    """Base class for all desktop-app errors."""

    def __init__(self, message: str, user_message: str | None = None) -> None:
        super().__init__(message)
        self.user_message: str = user_message or message

    def __str__(self) -> str:  # pragma: no cover
        return self.args[0]


class ConfigError(AppError):
    """Raised when the application configuration is invalid or incomplete."""


class CredentialError(AppError):
    """Raised when credentials cannot be read from or written to secure storage."""


class MCPProcessError(AppError):
    """Raised when the MCP server process fails to start, stop, or respond."""


class ClaudeBridgeError(AppError):
    """Raised when the Claude API bridge encounters a communication error."""


class AuthError(AppError):
    """Raised when intervals.icu API authentication fails."""


class ConversationError(AppError):
    """Raised when a conversation query cannot be completed."""


class UpdateCheckError(AppError):
    """Raised when the update-check service encounters an error."""


# ── User-facing message registry ─────────────────────────────────────────────
# Maps error types to safe display messages shown in the UI.
USER_MESSAGES: dict[type[AppError], str] = {
    ConfigError: "The application is not configured correctly. Check your settings.",
    CredentialError: "Could not access secure credential storage. Check system permissions.",
    MCPProcessError: "The background service could not start. Try restarting the application.",
    ClaudeBridgeError: "Could not connect to Claude. Check your API key and internet connection.",
    AuthError: "Authentication with intervals.icu failed. Check your API key.",
    ConversationError: "Could not complete your query. Please try again.",
    UpdateCheckError: "Update check failed. Check your internet connection.",
}


def user_message_for(error: AppError) -> str:
    """Return a safe, user-friendly message for the given error."""
    return USER_MESSAGES.get(type(error), error.user_message)
