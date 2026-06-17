"""
Claude API bridge client.

Wraps the Anthropic Python SDK to provide a simplified interface for
sending conversational queries with MCP tool support. Polls connection
state and exposes it via ``is_connected``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from desktop_app.errors import ClaudeBridgeError

if TYPE_CHECKING:
    pass

_DEFAULT_MAX_TOKENS = 4096


class ClaudeBridge:
    """Bridge between the desktop app and the Anthropic Claude API.

    Args:
        api_key:   Anthropic API key.
        model:     Claude model identifier (e.g. ``"claude-3-5-sonnet-20241022"``).
        mcp_tools: List of MCP tool schemas to pass in the ``tools`` field.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        mcp_tools: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._mcp_tools: list[dict[str, Any]] = mcp_tools or []
        self._client = self._build_client()
        self._connected: Optional[bool] = None

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_connected(self) -> bool:
        """Return True if the last connectivity probe succeeded."""
        return self._connected is True

    # ── Public API ────────────────────────────────────────────────────────────

    def probe_connection(self) -> bool:
        """Send a minimal request to verify API reachability.

        Updates ``is_connected`` and returns the result.
        """
        try:
            self._client.messages.create(
                model=self._model,
                max_tokens=1,
                messages=[{"role": "user", "content": "ping"}],
            )
            self._connected = True
        except Exception:
            self._connected = False
        return self._connected

    def send(
        self,
        messages: list[dict[str, Any]],
        system: Optional[str] = None,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
    ) -> str:
        """Send a conversation turn to Claude and return the text response.

        Args:
            messages:   List of ``{"role": ..., "content": ...}`` dicts.
            system:     Optional system prompt.
            max_tokens: Maximum tokens in the response.

        Returns:
            The assistant's text reply.

        Raises:
            ClaudeBridgeError: On any API or network failure.
        """
        kwargs: dict[str, Any] = dict(
            model=self._model,
            max_tokens=max_tokens,
            messages=messages,
        )
        if system:
            kwargs["system"] = system
        if self._mcp_tools:
            kwargs["tools"] = self._mcp_tools

        try:
            response = self._client.messages.create(**kwargs)
        except Exception as exc:
            self._connected = False
            raise ClaudeBridgeError(
                f"Claude API call failed: {exc}",
                user_message="Could not reach Claude. Check your API key and internet connection.",
            ) from exc

        self._connected = True
        # Extract the first text block from the response
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""

    # ── Internal ──────────────────────────────────────────────────────────────

    def _build_client(self):
        try:
            from anthropic import Anthropic  # noqa: PLC0415
        except ImportError as exc:
            raise ClaudeBridgeError(
                "The 'anthropic' package is not installed.",
                user_message="Claude integration is unavailable. Run: pip install anthropic",
            ) from exc
        return Anthropic(api_key=self._api_key)
