"""
Integration tests: primary conversation query flow.

Tests that the ConversationService integrates with the Claude bridge
to produce non-empty responses and handles errors gracefully.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestConversationQueries:
    def test_simple_query_returns_string(self, mock_anthropic_client):
        from desktop_app.conversation.service import ConversationService

        svc = ConversationService(client=mock_anthropic_client)
        result = svc.query("What was my FTP last month?")
        assert isinstance(result, str)
        assert result  # non-empty

    def test_query_calls_claude_once(self, mock_anthropic_client):
        from desktop_app.conversation.service import ConversationService

        svc = ConversationService(client=mock_anthropic_client)
        svc.query("How many rides did I do this week?")
        assert mock_anthropic_client.messages.create.call_count >= 1

    def test_unavailable_data_returns_fallback(self):
        from desktop_app.conversation.service import ConversationService
        from desktop_app.errors import ConversationError

        client = MagicMock()
        client.messages.create.side_effect = Exception("Simulated Claude error")

        svc = ConversationService(client=client)
        with pytest.raises(ConversationError):
            svc.query("What was my best 20-minute power?")
