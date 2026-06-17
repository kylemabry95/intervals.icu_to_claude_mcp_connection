"""
Authentication session state.

Manages the login/logout lifecycle and persists credentials to the OS
keychain via ``CredentialStore``.
"""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from desktop_app.security.credentials import CredentialStore

_KEY_API_KEY = "intervals_api_key"
_KEY_ATHLETE_ID = "intervals_athlete_id"


class AuthSession:
    """Tracks authentication state and persists credentials securely.

    Args:
        credential_store: OS-native credential store instance.
    """

    def __init__(self, credential_store: "CredentialStore") -> None:
        self._store = credential_store

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def api_key(self) -> Optional[str]:
        return self._store.get(_KEY_API_KEY)

    @property
    def athlete_id(self) -> Optional[str]:
        return self._store.get(_KEY_ATHLETE_ID)

    # ── Public API ─────────────────────────────────────────────────────────────

    def is_authenticated(self) -> bool:
        """Return True if stored credentials are present."""
        return bool(self.api_key and self.athlete_id)

    def login(self, api_key: str, athlete_id: str) -> None:
        """Persist credentials and mark the session as authenticated.

        Args:
            api_key:    intervals.icu API key.
            athlete_id: Athlete ID (e.g. ``"i12345"``).
        """
        self._store.set(_KEY_API_KEY, api_key)
        self._store.set(_KEY_ATHLETE_ID, athlete_id)

    def logout(self) -> None:
        """Clear persisted credentials and mark the session as unauthenticated."""
        self._store.delete(_KEY_API_KEY)
        self._store.delete(_KEY_ATHLETE_ID)
