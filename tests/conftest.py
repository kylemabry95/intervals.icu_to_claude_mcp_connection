"""Shared pytest fixtures for the desktop application test suite."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_anthropic_client():
    """Return a mock Anthropic client that returns a canned response."""
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Mocked Claude response.")]
    client.messages.create.return_value = mock_response
    return client


@pytest.fixture
def valid_env(monkeypatch, tmp_path):
    """Set up a valid environment for config loading tests."""
    monkeypatch.setenv("INTERVALS_API_KEY", "test-api-key")
    monkeypatch.setenv("INTERVALS_ATHLETE_ID", "i12345")
    monkeypatch.setenv("INTERVALS_API_BASE_URL", "https://intervals.icu/api/v1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("LOG_DIR", str(tmp_path))
    return tmp_path
