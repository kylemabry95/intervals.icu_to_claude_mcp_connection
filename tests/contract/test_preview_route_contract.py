from pathlib import Path


def test_preview_route_contract_exists():
    html = Path("preview/index.html").read_text(encoding="utf-8")
    assert "Demo mode" in html
    assert "Download for macOS (.dmg)" in html
