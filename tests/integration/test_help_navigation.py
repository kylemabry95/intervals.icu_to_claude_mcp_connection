"""Integration test: contextual help content routing."""

from __future__ import annotations

import pytest


class TestHelpNavigation:
    def test_get_help_for_auth_returns_content(self):
        """get_help() returns content for the 'auth' context."""
        from desktop_app.help.content import HelpContentProvider

        provider = HelpContentProvider()
        content = provider.get_help("auth")
        assert content and isinstance(content, str)

    def test_get_help_for_unknown_context_returns_generic(self):
        """get_help() falls back to generic content for unknown contexts."""
        from desktop_app.help.content import HelpContentProvider

        provider = HelpContentProvider()
        content = provider.get_help("completely_unknown_context_xyz")
        assert content  # Should return something, not empty/None

    def test_get_faq_returns_list(self):
        """get_faq() returns a non-empty list of FAQ entries."""
        from desktop_app.help.content import HelpContentProvider

        provider = HelpContentProvider()
        faqs = provider.get_faq()
        assert isinstance(faqs, list)
        assert len(faqs) >= 1

    def test_faq_entries_have_question_and_answer(self):
        """Each FAQ entry has a non-empty 'question' and 'answer' key."""
        from desktop_app.help.content import HelpContentProvider

        provider = HelpContentProvider()
        for entry in provider.get_faq():
            assert "question" in entry and entry["question"].strip()
            assert "answer" in entry and entry["answer"].strip()
