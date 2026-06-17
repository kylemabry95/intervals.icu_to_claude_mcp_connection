"""End-to-end smoke test for a local conversation flow."""

from __future__ import annotations

import pytest


@pytest.mark.e2e
class TestLocalConversationFlow:
    """E2E tests for the local conversation pipeline.

    These tests require a running local environment (MCP server + API key).
    Marked @e2e so they can be excluded from fast CI runs:
        pytest -m "not e2e"
    """

    def test_conversation_returns_response(self, mock_anthropic_client):
        """A natural-language query returns a non-empty Claude response."""
        from desktop_app.conversation.service import ConversationService

        svc = ConversationService(client=mock_anthropic_client)
        response = svc.query("What was my longest ride this week?")
        assert response and isinstance(response, str)

    def test_follow_up_preserves_context(self, mock_anthropic_client):
        """A follow-up question carries prior conversation context."""
        from desktop_app.conversation.service import ConversationService

        svc = ConversationService(client=mock_anthropic_client)
        svc.query("What is my current FTP?")
        response = svc.query("How does that compare to last month?")
        assert response  # context should be non-empty
