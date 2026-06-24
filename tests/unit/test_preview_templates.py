from pathlib import Path


def test_preview_template_engine_file_exists():
    path = Path("preview/template_engine.js")
    assert path.exists()


def test_preview_template_engine_has_deterministic_helper():
    content = Path("preview/template_engine.js").read_text(encoding="utf-8")
    assert "isDeterministic" in content
