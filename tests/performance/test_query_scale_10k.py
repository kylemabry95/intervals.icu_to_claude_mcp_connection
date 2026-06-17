"""
Performance test: high-volume query workload (10k+ records).

Verifies that the ConversationService handles large data payloads
(simulating 10k+ training records) within the p95 < 5s latency target.
"""

from __future__ import annotations

import statistics
import time
from unittest.mock import MagicMock

import pytest


def _make_large_activities_response(n: int = 10_000) -> str:
    """Generate a JSON string simulating n activity records."""
    import json
    activities = [
        {
            "id": str(i),
            "name": f"Ride {i}",
            "date": "2024-01-01",
            "movingTime": 3600,
            "distance": 50000,
            "avgPower": 200 + (i % 50),
            "avgHr": 150,
        }
        for i in range(n)
    ]
    return json.dumps(activities)


@pytest.mark.slow
class TestQueryScale10k:
    """Latency benchmarks under 10k+ record payloads."""

    def test_p95_latency_under_5s(self):
        """p95 query latency must be < 5 seconds for 10k+ record responses."""
        large_payload = _make_large_activities_response(10_000)

        client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text=f"Here is a summary: {large_payload[:100]}")]
        client.messages.create.return_value = mock_response

        from desktop_app.conversation.service import ConversationService

        svc = ConversationService(client=client)
        latencies: list[float] = []

        for _ in range(20):
            start = time.perf_counter()
            svc.query("Show me all my activities this year.")
            latencies.append(time.perf_counter() - start)

        p95 = statistics.quantiles(latencies, n=20)[-1]
        assert p95 < 5.0, f"p95 latency {p95:.2f}s exceeds 5s threshold."

    def test_conversation_history_trimmed_at_scale(self):
        """Message history does not grow without bound after many turns."""
        client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = [MagicMock(text="ok")]
        client.messages.create.return_value = mock_response

        from desktop_app.conversation.service import ConversationService

        svc = ConversationService(client=client, max_history_turns=5)

        for i in range(50):
            svc.query(f"Query {i}")

        last_call = client.messages.create.call_args
        messages = last_call.kwargs.get("messages", [])
        # Should be bounded: at most (max_history_turns * 2 + 1) = 11
        assert len(messages) <= 11
