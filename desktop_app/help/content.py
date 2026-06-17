"""
Help content provider and FAQ mapping.

Provides context-sensitive help text for the auth, chat, settings,
and help screens, as well as a general FAQ list.
"""

from __future__ import annotations

from typing import Any

_HELP_CONTENT: dict[str, str] = {
    "auth": (
        "To connect, you need your intervals.icu API key and athlete ID.\n\n"
        "1. Go to https://intervals.icu\n"
        "2. Open Settings → API\n"
        "3. Copy your API key\n"
        "4. Your athlete ID is the 'i' + digits in your profile URL "
        "(e.g. i12345).\n\n"
        "Your credentials are stored securely in your system keychain and are "
        "never uploaded anywhere."
    ),
    "chat": (
        "Ask questions about your training in plain English. Examples:\n\n"
        "• 'What was my average FTP last month?'\n"
        "• 'How many hours did I train this week?'\n"
        "• 'Show me my sleep trend for the past 14 days'\n\n"
        "Claude will retrieve your data from intervals.icu and summarise it. "
        "Use the Clear button to start a new conversation."
    ),
    "settings": (
        "Manage your connection settings, log level, and update preferences.\n\n"
        "• API Key / Athlete ID: Your intervals.icu credentials.\n"
        "• Log Level: Controls the verbosity of application logs.\n"
        "• Update checks: When enabled, the app checks for new versions daily."
    ),
    "help": (
        "Browse the FAQ or visit https://intervals.icu/support for more help.\n\n"
        "To report a bug or request a feature, open an issue at\n"
        "https://github.com/kylemabry95/intervals.icu_to_claude_mcp_connection"
    ),
}

_GENERIC_HELP = (
    "For general help, visit https://intervals.icu/support or open the "
    "Help tab in the application."
)

_FAQ: list[dict[str, str]] = [
    {
        "question": "Where do I find my API key?",
        "answer": (
            "Go to intervals.icu → Settings → API. "
            "Your API key is listed there. Keep it private."
        ),
    },
    {
        "question": "What is my athlete ID?",
        "answer": (
            "Your athlete ID starts with 'i' followed by digits "
            "(e.g. i12345). It appears in your profile URL."
        ),
    },
    {
        "question": "Why is Claude not responding?",
        "answer": (
            "Check that your Anthropic API key is set in Settings and that "
            "you have an active internet connection."
        ),
    },
    {
        "question": "How is my data protected?",
        "answer": (
            "Your API keys are stored in your OS system keychain "
            "(macOS Keychain / Windows Credential Manager) and are never "
            "transmitted to third parties."
        ),
    },
    {
        "question": "How do I update the app?",
        "answer": (
            "The app checks for updates daily. When a new version is available, "
            "you will see a prompt to download it. You can also check manually "
            "via Settings → Check for Updates."
        ),
    },
]


class HelpContentProvider:
    """Returns context-specific help text and FAQ entries."""

    def get_help(self, context: str) -> str:
        """Return help text for the given UI *context*.

        Args:
            context: One of ``"auth"``, ``"chat"``, ``"settings"``, ``"help"``.
                     Falls back to generic help for unknown contexts.
        """
        return _HELP_CONTENT.get(context.lower(), _GENERIC_HELP)

    def get_faq(self) -> list[dict[str, str]]:
        """Return the full FAQ list."""
        return list(_FAQ)
