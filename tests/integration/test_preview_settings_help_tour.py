from pathlib import Path


def test_settings_and_help_preview_modules_present():
    settings_js = Path("preview/settings_preview.js").read_text(encoding="utf-8")
    help_js = Path("preview/help_preview.js").read_text(encoding="utf-8")
    assert "Settings Tour" in settings_js
    assert "Help Preview" in help_js
