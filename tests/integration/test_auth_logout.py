"""Integration test: logout clears all persisted credentials."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestAuthLogout:
    def test_logout_clears_credentials(self):
        """After logout, no credentials remain in the store."""
        _store = {"intervals_api_key": "key", "intervals_athlete_id": "i1"}
        mock_kr = MagicMock()
        mock_kr.get_password.side_effect = lambda s, k: _store.get(k)
        mock_kr.delete_password.side_effect = lambda s, k: _store.pop(k, None)

        from desktop_app.auth.session import AuthSession
        from desktop_app.security.credentials import CredentialStore

        cred_store = CredentialStore()
        cred_store._keyring = mock_kr

        session = AuthSession(credential_store=cred_store)
        assert session.is_authenticated()

        session.logout()
        assert not session.is_authenticated()
        assert "intervals_api_key" not in _store
        assert "intervals_athlete_id" not in _store
