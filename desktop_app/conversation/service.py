"""
Conversation orchestration service.

Sends user queries to Claude (via the Anthropic client) with a system
prompt that describes the available intervals.icu MCP tools, manages
conversation history, and handles error/fallback scenarios.
"""

from __future__ import annotations

from typing import Any, Optional

from desktop_app.conversation.model import ConversationHistory, Role
from desktop_app.conversation.fallbacks import handle_fallback
from desktop_app.errors import ConversationError
from desktop_app.observability.metrics import record_query_latency

import time

_SYSTEM_PROMPT = """\
You are an AI assistant integrated with intervals.icu, an athlete training platform.
You have access to the athlete's training data via MCP tools.

When the user asks about their training, wellness, or performance data, use the
available tools to retrieve accurate, up-to-date information before responding.
Always ground your answers in the data returned by the tools — do not fabricate
metrics or statistics.

If data is unavailable or a query is outside your capabilities, say so clearly
and suggest how the user might find the information themselves.
"""

_DEFAULT_MAX_TOKENS = 2048


class ConversationService:
    """Orchestrates Claude queries with MCP tool context and conversation history.

    Args:
        client:            Anthropic client (or compatible mock).
        model:             Claude model identifier.
        max_history_turns: Maximum conversation pairs to retain in history.
    """

    def __init__(
        self,
        client: Any,
        model: str = "claude-3-5-sonnet-20241022",
        max_history_turns: int = 5,
    ) -> None:
        self._client = client
        self._model = model
        self._history = ConversationHistory(max_turns=max_history_turns)

    # ── Public API ─────────────────────────────────────────────────────────────

    def query(self, user_message: str, max_tokens: int = _DEFAULT_MAX_TOKENS) -> str:
        """Send *user_message* to Claude and return the assistant's text reply.

        Updates the conversation history for context continuity.

        Args:
            user_message: The user's natural-language question.
            max_tokens:   Maximum tokens in the response.

        Returns:
            Claude's text reply.

        Raises:
            ConversationError: On any API or communication failure.
        """
        self._history.add(Role.USER, user_message)
        messages = self._history.to_api_messages()

        t0 = time.perf_counter()
        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=max_tokens,
                system=_SYSTEM_PROMPT,
                messages=messages,
            )
        except Exception as exc:
            self._history._messages.pop()  # Remove un-answered user turn
            raise ConversationError(
                f"Claude API call failed: {exc}",
                user_message="Could not complete your query. Check your internet connection and API key.",
            ) from exc
        finally:
            elapsed = time.perf_counter() - t0
            record_query_latency(elapsed)

        # Extract text from the first content block
        reply = ""
        for block in response.content:
            if hasattr(block, "text"):
                reply = block.text
                break

        if not reply:
            reply = handle_fallback(user_message)

        self._history.add(Role.ASSISTANT, reply)
        return reply

    def clear_history(self) -> None:
        """Reset the conversation history."""
        self._history.clear()

    @property
    def history(self) -> ConversationHistory:
        return self._history
