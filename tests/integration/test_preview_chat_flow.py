from pathlib import Path


def test_chat_flow_template_resolution_wired():
    js = Path("preview/preview.js").read_text(encoding="utf-8")
    assert "resolveTemplate" in js
    assert "query_submitted" in js
    assert "response_rendered" in js
