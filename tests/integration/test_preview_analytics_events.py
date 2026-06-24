from pathlib import Path


def test_required_analytics_events_emitted_in_preview_js():
    js = Path("preview/preview.js").read_text(encoding="utf-8")
    for name in ["preview_loaded", "query_submitted", "response_rendered", "cta_clicked"]:
        assert name in js
