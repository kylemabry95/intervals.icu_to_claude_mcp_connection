"""Integration test: credential persistence across sessions."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestAuthPersistence:
    def test_login_persists_credentials(self):
        """After login, credentials are stored and retrievable."""
        _store: dict[str, str] = {}
        mock_kr = MagicMock()
        mock_kr.set_password.side_effect = lambda s, k, v: _store.update({k: v})
        mock_kr.get_password.side_effect = lambda s, k: _store.get(k)

        from desktop_app.auth.session import AuthSession
        from desktop_app.security.credentials import CredentialStore

        cred_store = CredentialStore()
        cred_store._keyring = mock_kr

        session = AuthSession(credential_store=cred_store)
        session.login(api_key="test-key", athlete_id="i99")

        assert cred_store.get("intervals_api_key") == "test-key"
        assert cred_store.get("intervals_athlete_id") == "i99"

    def test_session_restored_after_restart(self):
        """is_authenticated() returns True when persisted credentials exist."""
        _store = {"intervals_api_key": "stored-key", "intervals_athlete_id": "i1"}
        mock_kr = MagicMock()
        mock_kr.get_password.side_effect = lambda s, k: _store.get(k)

        from desktop_app.auth.session import AuthSession
        from desktop_app.security.credentials import CredentialStore

        cred_store = CredentialStore()
        cred_store._keyring = mock_kr

        session = AuthSession(credential_store=cred_store)
        assert session.is_authenticated()
