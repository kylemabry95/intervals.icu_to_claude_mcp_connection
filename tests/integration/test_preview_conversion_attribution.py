from pathlib import Path


def test_conversion_attribution_task_support_present():
    analytics = Path("preview/analytics.js").read_text(encoding="utf-8")
    preview = Path("preview/preview.js").read_text(encoding="utf-8")
    assert "computeEngagementRate" in analytics
    assert "cta_clicked" in preview
