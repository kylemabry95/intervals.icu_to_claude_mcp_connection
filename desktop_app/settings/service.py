"""
Settings service: coordinates preference updates and API key changes.

Applies business logic on top of the SettingsRepository, such as
validating a new API key before persisting it and triggering
re-authentication.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from desktop_app.errors import AuthError

if TYPE_CHECKING:
    from desktop_app.auth.session import AuthSession
    from desktop_app.settings.repository import SettingsRepository

_MIN_KEY_LENGTH = 8


class SettingsService:
    """Business logic for settings management.

    Args:
        auth_session:        Current authentication session.
        settings_repository: Optional persistent settings store.
    """

    def __init__(
        self,
        auth_session: "AuthSession",
        settings_repository: Optional["SettingsRepository"] = None,
    ) -> None:
        self._session = auth_session
        self._repo = settings_repository

    # ── Public API ─────────────────────────────────────────────────────────────

    def update_api_key(self, new_key: str, athlete_id: str) -> None:
        """Validate and persist a new API key, then update the auth session.

        Args:
            new_key:    New intervals.icu API key.
            athlete_id: Associated athlete ID.

        Raises:
            AuthError: If the key format is invalid.
        """
        if not new_key or len(new_key.strip()) < _MIN_KEY_LENGTH:
            raise AuthError(
                f"API key is too short (minimum {_MIN_KEY_LENGTH} characters).",
                user_message=f"The API key must be at least {_MIN_KEY_LENGTH} characters long.",
            )
        self._session.login(api_key=new_key.strip(), athlete_id=athlete_id.strip())

    def get_preference(self, key: str, default=None):
        """Return a preference value from the settings repository."""
        if self._repo:
            return self._repo.get(key, default)
        return default

    def set_preference(self, key: str, value) -> None:
        """Persist a preference value."""
        if self._repo:
            self._repo.set(key, value)

    def update_update_policy(self, enabled: bool) -> None:
        """Enable or disable scheduled update checks."""
        if self._repo:
            self._repo.set("update_check_enabled", enabled)

    def update_log_level(self, level: str) -> None:
        """Update the active log level preference."""
        valid = {"DEBUG", "INFO", "WARNING", "ERROR"}
        if level.upper() not in valid:
            raise ValueError(f"Log level must be one of: {valid}")
        if self._repo:
            self._repo.set("log_level", level.upper())
