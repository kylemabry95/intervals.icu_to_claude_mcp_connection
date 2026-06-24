from pathlib import Path


def test_preview_shell_contains_required_sections():
    html = Path("preview/index.html").read_text(encoding="utf-8")
    assert "panel-chat" in html
    assert "panel-auth" in html
    assert "panel-settings" in html
    assert "panel-help" in html


def test_preview_shell_contains_download_ctas():
    html = Path("preview/index.html").read_text(encoding="utf-8")
    assert "download-macos" in html
    assert "download-windows" in html
