from pathlib import Path


def test_preview_funnel_has_entry_points():
    html = Path("preview/index.html").read_text(encoding="utf-8")
    assert "Try IntervalsICU Before You Download" in html
    assert "chat-form" in html


def test_preview_js_exposes_event_bus_for_validation():
    js = Path("preview/preview.js").read_text(encoding="utf-8")
    assert "__previewEventBus" in js
