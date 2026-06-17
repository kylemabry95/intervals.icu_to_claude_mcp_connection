"""Integration test: API key update triggers re-authentication."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


class TestSettingsReauth:
    def test_api_key_update_updates_session(self):
        """Saving a new API key through SettingsService updates the auth session."""
        mock_store = MagicMock()
        mock_store.get.side_effect = lambda k, default=None: {
            "intervals_api_key": "old-key",
            "intervals_athlete_id": "i1",
        }.get(k, default)

        saved: dict = {}
        mock_store.set.side_effect = lambda k, v: saved.update({k: v})

        from desktop_app.security.credentials import CredentialStore
        from desktop_app.auth.session import AuthSession
        from desktop_app.settings.service import SettingsService

        cred_store = CredentialStore.__new__(CredentialStore)
        cred_store._service = "IntervalsICU"
        cred_store._keyring = mock_store

        session = AuthSession(credential_store=cred_store)
        svc = SettingsService(auth_session=session)

        svc.update_api_key("new-key-123", "i1")

        assert saved.get("intervals_api_key") == "new-key-123"

    def test_update_with_invalid_format_raises(self):
        """Updating with a too-short key raises an error."""
        from desktop_app.settings.service import SettingsService
        from desktop_app.errors import AuthError

        svc = SettingsService(auth_session=MagicMock())
        with pytest.raises((AuthError, ValueError)):
            svc.update_api_key("bad", "i1")
