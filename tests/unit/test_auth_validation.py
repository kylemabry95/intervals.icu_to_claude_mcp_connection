"""Unit tests for API key validation logic."""

from __future__ import annotations

import pytest


class TestAPIKeyValidation:
    def test_valid_key_passes(self):
        from desktop_app.auth.service import AuthService

        svc = AuthService.__new__(AuthService)
        assert svc._validate_key_format("API_KEY_1234567890abcdef") is True

    def test_empty_key_fails(self):
        from desktop_app.auth.service import AuthService

        svc = AuthService.__new__(AuthService)
        assert svc._validate_key_format("") is False

    def test_whitespace_only_fails(self):
        from desktop_app.auth.service import AuthService

        svc = AuthService.__new__(AuthService)
        assert svc._validate_key_format("   ") is False

    def test_key_too_short_fails(self):
        from desktop_app.auth.service import AuthService

        svc = AuthService.__new__(AuthService)
        # Keys shorter than 8 characters are considered invalid
        assert svc._validate_key_format("abc") is False

    def test_athlete_id_valid(self):
        from desktop_app.auth.service import AuthService

        svc = AuthService.__new__(AuthService)
        assert svc._validate_athlete_id("i12345") is True

    def test_athlete_id_missing_prefix(self):
        from desktop_app.auth.service import AuthService

        svc = AuthService.__new__(AuthService)
        assert svc._validate_athlete_id("12345") is False

    def test_athlete_id_empty(self):
        from desktop_app.auth.service import AuthService

        svc = AuthService.__new__(AuthService)
        assert svc._validate_athlete_id("") is False
