"""
Secure credential storage abstraction.

Wraps the ``keyring`` library to provide a consistent interface for storing
and retrieving sensitive values (API keys) via the OS-native backend:
  - macOS: Keychain
  - Windows: Windows Credential Manager
  - Linux: Secret Service / libsecret (fallback)

Usage::

    from desktop_app.security.credentials import CredentialStore

    store = CredentialStore()
    store.set("intervals_api_key", "my-secret-key")
    key = store.get("intervals_api_key")   # -> "my-secret-key"
    store.delete("intervals_api_key")
"""

from __future__ import annotations

from typing import Optional

from desktop_app.errors import CredentialError

_SERVICE_NAME = "IntervalsICU"


class CredentialStore:
    """OS-native secure credential store backed by ``keyring``."""

    def __init__(self, service: str = _SERVICE_NAME) -> None:
        self._service = service
        self._keyring = self._load_keyring()

    @staticmethod
    def _load_keyring():
        try:
            import keyring  # noqa: PLC0415
            return keyring
        except ImportError as exc:
            raise CredentialError(
                "The 'keyring' package is not installed.",
                user_message="Secure storage is unavailable. Run: pip install keyring",
            ) from exc

    # ── Public API ────────────────────────────────────────────────────────────

    def set(self, key: str, value: str) -> None:
        """Store *value* under *key* in the OS keychain.

        Args:
            key:   Credential name (e.g. ``"intervals_api_key"``).
            value: Secret value to store.

        Raises:
            CredentialError: On write failure.
        """
        try:
            self._keyring.set_password(self._service, key, value)
        except Exception as exc:
            raise CredentialError(
                f"Failed to store credential '{key}': {exc}",
                user_message="Could not save your credentials. Check system permissions.",
            ) from exc

    def get(self, key: str) -> Optional[str]:
        """Retrieve the value stored under *key*, or ``None`` if absent.

        Raises:
            CredentialError: On read failure.
        """
        try:
            return self._keyring.get_password(self._service, key)
        except Exception as exc:
            raise CredentialError(
                f"Failed to retrieve credential '{key}': {exc}",
                user_message="Could not read your credentials. Check system permissions.",
            ) from exc

    def delete(self, key: str) -> None:
        """Delete the credential stored under *key* (no-op if absent).

        Raises:
            CredentialError: On deletion failure.
        """
        try:
            self._keyring.delete_password(self._service, key)
        except Exception:
            # keyring raises PasswordDeleteError if the credential does not
            # exist; treat as a no-op so callers can call delete() safely.
            pass
