"""
Authentication service: API key verification and format validation.

Verifies credentials against the intervals.icu API using the same
Basic Auth scheme used by the MCP server (base64-encoded ``API_KEY:api_key``).
"""

from __future__ import annotations

import base64
import re

from desktop_app.errors import AuthError

# Minimum length for a plausible API key
_MIN_KEY_LENGTH = 8

# intervals.icu athlete IDs start with 'i' followed by digits
_ATHLETE_ID_RE = re.compile(r"^i\d+$")


class AuthService:
    """Validates intervals.icu credentials against the live API."""

    def __init__(self, base_url: str = "https://intervals.icu/api/v1") -> None:
        self._base_url = base_url.rstrip("/")

    # ── Validation helpers (pure, no I/O) ─────────────────────────────────────

    def _validate_key_format(self, api_key: str) -> bool:
        """Return True if *api_key* looks like a plausible API key."""
        return bool(api_key and api_key.strip() and len(api_key.strip()) >= _MIN_KEY_LENGTH)

    def _validate_athlete_id(self, athlete_id: str) -> bool:
        """Return True if *athlete_id* matches the ``i<digits>`` pattern."""
        return bool(athlete_id and _ATHLETE_ID_RE.match(athlete_id.strip()))

    # ── Live verification ─────────────────────────────────────────────────────

    def verify(self, api_key: str, athlete_id: str) -> bool:
        """Verify credentials against the intervals.icu API.

        Makes a lightweight GET request to the athlete profile endpoint.

        Args:
            api_key:    intervals.icu API key.
            athlete_id: Athlete ID (e.g. ``"i12345"``).

        Returns:
            True on success.

        Raises:
            AuthError: If credentials are invalid or the API is unreachable.
        """
        if not self._validate_key_format(api_key):
            raise AuthError(
                f"API key format is invalid (too short or empty).",
                user_message="The API key you entered looks invalid. Check your intervals.icu Settings.",
            )
        if not self._validate_athlete_id(athlete_id):
            raise AuthError(
                f"Athlete ID '{athlete_id}' is invalid. Expected format: i<digits>.",
                user_message="Athlete ID must start with 'i' followed by digits (e.g. i12345).",
            )

        try:
            import httpx  # noqa: PLC0415

            encoded = base64.b64encode(f"API_KEY:{api_key}".encode()).decode()
            headers = {"Authorization": f"Basic {encoded}"}
            url = f"{self._base_url}/athlete/{athlete_id}"
            response = httpx.get(url, headers=headers, timeout=10.0)
        except Exception as exc:
            raise AuthError(
                f"Network error during credential verification: {exc}",
                user_message="Could not reach intervals.icu. Check your internet connection.",
            ) from exc

        if response.status_code == 401:
            raise AuthError(
                "intervals.icu returned 401 Unauthorized.",
                user_message="Invalid API key. Check your intervals.icu Settings → API.",
            )
        if response.status_code == 403:
            raise AuthError(
                "intervals.icu returned 403 Forbidden.",
                user_message="Access denied. Check your API key permissions.",
            )
        if response.status_code >= 400:
            raise AuthError(
                f"intervals.icu returned HTTP {response.status_code}.",
                user_message=f"Authentication failed (HTTP {response.status_code}). Try again.",
            )

        return True
