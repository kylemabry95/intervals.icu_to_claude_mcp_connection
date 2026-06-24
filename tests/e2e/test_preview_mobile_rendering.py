from pathlib import Path


def test_mobile_breakpoint_defined():
    css = Path("preview/styles.css").read_text(encoding="utf-8")
    assert "@media (max-width: 760px)" in css


def test_mobile_fallback_message_present():
    html = Path("preview/index.html").read_text(encoding="utf-8")
    assert "fallback-banner" in html
