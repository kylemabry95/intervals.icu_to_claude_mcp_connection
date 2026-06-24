from pathlib import Path


def test_auth_flow_leads_to_download_cta_capability():
    cta = Path("preview/cta.js").read_text(encoding="utf-8")
    assert "download_macos" in cta
    assert "download_windows" in cta
