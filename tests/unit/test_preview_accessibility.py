from pathlib import Path


def test_preview_has_accessible_live_regions_and_labels():
    html = Path("preview/index.html").read_text(encoding="utf-8")
    assert 'aria-live="polite"' in html
    assert 'aria-label="Preview sections"' in html
