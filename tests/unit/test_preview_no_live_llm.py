from pathlib import Path


FORBIDDEN_HINTS = [
    "anthropic",
    "openai",
    "claude api",
    "intervals.icu/api",
]


def test_preview_js_has_no_live_llm_or_api_calls():
    js = Path("preview/preview.js").read_text(encoding="utf-8").lower()
    for hint in FORBIDDEN_HINTS:
        assert hint not in js


def test_template_engine_is_static():
    js = Path("preview/template_engine.js").read_text(encoding="utf-8").lower()
    assert "fetch(" not in js
    assert "xmlhttprequest" not in js
