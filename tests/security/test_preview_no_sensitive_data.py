from pathlib import Path


def test_preview_files_do_not_embed_real_secrets():
    combined = "\n".join(
        Path(path).read_text(encoding="utf-8")
        for path in [
            "preview/preview.js",
            "preview/demo_data.js",
            "preview/messages.js",
            "preview/events.js",
        ]
    ).lower()
    assert "sk-ant-" not in combined
    assert "intervalsecret" not in combined


def test_event_sanitization_blocks_sensitive_keys():
    content = Path("preview/events.js").read_text(encoding="utf-8").lower()
    assert "api_key" in content
    assert "password" in content
