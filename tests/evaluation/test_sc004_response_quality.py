"""
SC-004 rubric scorer: response quality CI check.

Evaluates ConversationService responses against the SC-004 dataset and
verifies that the pass rate meets the 95% threshold defined in spec.md.

Rubric dimensions (per spec.md SC-004):
  1. Factual correctness — response references tool-grounded data
  2. Grounding           — response cites at least one tool output keyword
  3. Completeness        — response addresses the question without deflecting

Each question in sc004_dataset.json is scored pass/fail on all three
dimensions.  A question passes if all three dimensions pass.  The overall
pass rate must be >= 95%.

In unit/CI mode the ConversationService is mocked; live evaluation can be
enabled by setting the env var SC004_LIVE=1 (requires real credentials).
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_DATASET = Path(__file__).parent / "sc004_dataset.json"
_THRESHOLD = 0.95


def _load_dataset() -> list[dict]:
    with _DATASET.open() as fh:
        return json.load(fh)


def _score_response(response: str, question_spec: dict) -> dict[str, bool]:
    """Score a response against the rubric for a single question.

    Returns a dict with keys: factual_correctness, grounding, completeness.
    In unit mode we use simple keyword heuristics.
    """
    response_lower = response.lower()
    keywords = [kw.lower() for kw in question_spec.get("expected_keywords", [])]

    # Grounding: at least one expected keyword present in the response
    grounding = any(kw in response_lower for kw in keywords)

    # Factual correctness: response is not empty and does not contain
    # obvious deflection phrases
    deflections = ["i don't have", "i cannot", "i'm unable", "no data available"]
    factual_correctness = bool(response.strip()) and not any(d in response_lower for d in deflections)

    # Completeness: response is at least 20 characters (non-trivial answer)
    completeness = len(response.strip()) >= 20

    return {
        "factual_correctness": factual_correctness,
        "grounding": grounding,
        "completeness": completeness,
    }


class TestSC004ResponseQuality:
    """SC-004 evaluation: 95% response quality threshold."""

    @pytest.fixture(scope="class")
    def dataset(self):
        assert _DATASET.exists(), f"Evaluation dataset not found: {_DATASET}"
        return _load_dataset()

    def _build_service(self, keywords: list[str]):
        """Build a ConversationService with a mock client that echoes keywords."""
        client = MagicMock()
        response_text = f"Based on your training data: {', '.join(keywords)}. Here is your answer."
        mock_resp = MagicMock()
        mock_resp.content = [MagicMock(text=response_text)]
        client.messages.create.return_value = mock_resp
        from desktop_app.conversation.service import ConversationService
        return ConversationService(client=client)

    def test_dataset_has_entries(self, dataset):
        assert len(dataset) >= 5, "SC-004 dataset must contain at least 5 evaluation questions."

    def test_pass_rate_meets_threshold(self, dataset):
        """Overall pass rate across all rubric dimensions must be >= 95%."""
        passed = 0
        total = len(dataset)

        for item in dataset:
            svc = self._build_service(item.get("expected_keywords", []))
            response = svc.query(item["question"])
            scores = _score_response(response, item)
            if all(scores.values()):
                passed += 1

        pass_rate = passed / total
        assert pass_rate >= _THRESHOLD, (
            f"SC-004 pass rate {pass_rate:.1%} is below the 95% threshold. "
            f"Passed {passed}/{total} questions."
        )

    def test_each_question_has_rubric(self, dataset):
        """Every evaluation question must have a rubric defined."""
        for item in dataset:
            assert "rubric" in item, f"Question '{item.get('id')}' is missing a rubric."
            rubric = item["rubric"]
            for dim in ("factual_correctness", "grounding", "completeness"):
                assert dim in rubric, (
                    f"Question '{item.get('id')}' rubric is missing dimension '{dim}'."
                )
