from pathlib import Path


def test_auth_preview_contains_guidance_link():
    js = Path("preview/auth_preview.js").read_text(encoding="utf-8")
    assert "intervals.icu/settings" in js
    assert "Authentication Preview" in js
