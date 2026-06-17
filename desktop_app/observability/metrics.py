"""
Performance telemetry: query latency SLIs.

Collects and exposes p50/p95/p99 query latency metrics for the
conversation service.  Metrics are stored in-process (no external
dependency) and can be exported to log files or health endpoints.
"""

from __future__ import annotations

import statistics
import threading
from collections import deque
from typing import Optional

_MAX_SAMPLES = 500  # Rolling window of recent latency samples
_lock = threading.Lock()
_latency_samples: deque[float] = deque(maxlen=_MAX_SAMPLES)


def record_query_latency(seconds: float) -> None:
    """Record a single query latency measurement (in seconds)."""
    with _lock:
        _latency_samples.append(seconds)


def get_latency_stats() -> dict[str, Optional[float]]:
    """Return a snapshot of rolling latency statistics.

    Returns:
        Dict with keys ``p50``, ``p95``, ``p99``, ``count``, ``mean``.
        All latency values are in seconds.  Returns ``None`` values when
        there are fewer than 2 samples.
    """
    with _lock:
        samples = list(_latency_samples)

    if len(samples) < 2:
        return {"p50": None, "p95": None, "p99": None, "count": len(samples), "mean": None}

    sorted_samples = sorted(samples)
    n = len(sorted_samples)

    def percentile(p: float) -> float:
        k = (p / 100) * (n - 1)
        lo = int(k)
        hi = min(lo + 1, n - 1)
        return sorted_samples[lo] + (k - lo) * (sorted_samples[hi] - sorted_samples[lo])

    return {
        "p50": percentile(50),
        "p95": percentile(95),
        "p99": percentile(99),
        "count": n,
        "mean": statistics.mean(samples),
    }


def reset_metrics() -> None:
    """Clear all recorded latency samples (useful for testing)."""
    with _lock:
        _latency_samples.clear()
