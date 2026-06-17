"""Unit tests: tooltip component rendering and accessibility."""

from __future__ import annotations

import pytest


class TestHelpTooltips:
    def test_tooltip_has_text(self):
        """Every registered tooltip has non-empty text."""
        from desktop_app.ui.components.help import TOOLTIP_REGISTRY

        for key, text in TOOLTIP_REGISTRY.items():
            assert text.strip(), f"Tooltip '{key}' has empty text."

    def test_tooltip_exists_for_key_fields(self):
        """Key UI fields have tooltips registered."""
        from desktop_app.ui.components.help import TOOLTIP_REGISTRY

        required_keys = ["api_key", "athlete_id", "log_level", "update_check"]
        for key in required_keys:
            assert key in TOOLTIP_REGISTRY, f"No tooltip registered for '{key}'."

    def test_tooltip_text_is_helpful(self):
        """Tooltip texts are at least 10 characters (not placeholder stubs)."""
        from desktop_app.ui.components.help import TOOLTIP_REGISTRY

        for key, text in TOOLTIP_REGISTRY.items():
            assert len(text.strip()) >= 10, (
                f"Tooltip '{key}' is suspiciously short: '{text}'"
            )
