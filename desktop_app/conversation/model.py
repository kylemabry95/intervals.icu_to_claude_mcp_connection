"""
Conversation domain model.

Defines the data structures used by the ConversationService:

  - ``Message``         — a single conversation turn (user or assistant)
  - ``ConversationHistory`` — bounded sliding window of turns with optional
                              context summary for token cost optimisation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """A single conversation turn."""

    role: Role
    content: str

    def to_api_dict(self) -> dict[str, str]:
        """Return the dict format expected by the Anthropic messages API."""
        return {"role": self.role.value, "content": self.content}


@dataclass
class ConversationHistory:
    """Sliding window conversation history with optional context summary.

    Keeps the *most recent* ``max_turns`` user/assistant pairs.  Older turns
    are discarded to control token usage (SC-004 cost optimisation).

    Args:
        max_turns: Maximum number of user/assistant pairs to retain.
        context_summary: Optional running summary of earlier context injected
                         as a system prompt addendum.
    """

    max_turns: int = 5
    context_summary: str = ""
    _messages: list[Message] = field(default_factory=list, repr=False)

    def add(self, role: Role, content: str) -> None:
        """Append a message and trim history to ``max_turns`` pairs."""
        self._messages.append(Message(role=role, content=content))
        # Each pair is 2 messages (user + assistant); keep max_turns pairs
        max_messages = self.max_turns * 2
        if len(self._messages) > max_messages:
            self._messages = self._messages[-max_messages:]

    def to_api_messages(self) -> list[dict[str, str]]:
        """Return the list of messages in Anthropic API format."""
        return [m.to_api_dict() for m in self._messages]

    def clear(self) -> None:
        """Reset the conversation history."""
        self._messages.clear()
        self.context_summary = ""

    @property
    def is_empty(self) -> bool:
        return len(self._messages) == 0
