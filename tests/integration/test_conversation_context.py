"""Integration test: follow-up conversation context continuity."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest


class TestConversationContext:
    def test_follow_up_includes_prior_messages(self):
        """The second query includes prior conversation history in the messages sent to Claude."""
        sent_messages: list = []

        client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="FTP is 280W.")]

        def capture_and_respond(**kwargs):
            sent_messages.append(kwargs.get("messages", []))
            return mock_response

        client.messages.create.side_effect = capture_and_respond

        from desktop_app.conversation.service import ConversationService

        svc = ConversationService(client=client)
        svc.query("What is my FTP?")
        svc.query("How does that compare to six months ago?")

        # Second call should carry at least 3 messages (user1, assistant1, user2)
        assert len(sent_messages) == 2
        assert len(sent_messages[1]) >= 3

    def test_context_summary_kept_under_limit(self):
        """History is summarised/trimmed so the message list does not grow unbounded."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="Answer.")]
        client.messages.create.return_value = mock_response

        from desktop_app.conversation.service import ConversationService

        svc = ConversationService(client=client, max_history_turns=3)

        for i in range(10):
            svc.query(f"Question {i}")

        # The history sent to Claude should not exceed max_history_turns * 2 + 1 messages
        last_call_kwargs = client.messages.create.call_args
        sent = last_call_kwargs.kwargs.get("messages", last_call_kwargs.args[0] if last_call_kwargs.args else [])
        assert len(sent) <= 3 * 2 + 1
