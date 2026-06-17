"""
Auth error messaging and remediation hints for the sign-in UI.

Maps error types to user-facing remediation guidance shown below the
error message in the auth view.
"""

from __future__ import annotations

from desktop_app.errors import AuthError, CredentialError

# Maps error type → short remediation hint shown in the UI
AUTH_ERROR_HINTS: dict[type, str] = {
    AuthError: (
        "Go to intervals.icu → Settings → API to copy your API key. "
        "Make sure your Athlete ID starts with 'i' (e.g. i12345)."
    ),
    CredentialError: (
        "The application could not access the system keychain. "
        "Check that Keychain Access (macOS) or Credential Manager (Windows) is available."
    ),
}


def format_auth_error(exc: Exception) -> str:
    """Return a combined user message and remediation hint for *exc*."""
    hint = AUTH_ERROR_HINTS.get(type(exc), "")
    if hasattr(exc, "user_message"):
        msg = exc.user_message  # type: ignore[attr-defined]
    else:
        msg = str(exc)
    return f"{msg}\n\n{hint}".strip() if hint else msg
