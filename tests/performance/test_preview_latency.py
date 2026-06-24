from pathlib import Path


def test_template_latency_budget_under_one_second():
    js = Path("preview/template_engine.js").read_text(encoding="utf-8")
    assert "latency_budget_ms: 700" in js or "latency_budget_ms: 650" in js
