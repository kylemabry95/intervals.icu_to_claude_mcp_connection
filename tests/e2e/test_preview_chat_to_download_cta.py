from pathlib import Path


def test_chat_to_cta_path_present():
    html = Path("preview/index.html").read_text(encoding="utf-8")
    js = Path("preview/preview.js").read_text(encoding="utf-8")
    assert "download-macos" in html
    assert "cta_clicked" in js
