from pathlib import Path


def test_session_model_exists_and_has_device_validation():
    content = Path("preview/session.js").read_text(encoding="utf-8")
    assert "device_type" in content
    assert "Invalid device_type" in content


def test_demo_dataset_contains_no_sensitive_keys_literal():
    content = Path("preview/demo_data.js").read_text(encoding="utf-8").lower()
    assert "api_key" not in content
    assert "password" not in content


def test_event_schema_blocks_sensitive_fields():
    content = Path("preview/events.js").read_text(encoding="utf-8").lower()
    assert "api_key" in content
    assert "sanitizeeventmetadata" in content
