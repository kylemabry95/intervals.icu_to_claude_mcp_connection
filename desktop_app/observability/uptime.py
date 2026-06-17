"""
Uptime SLO instrumentation and rolling availability reporting.

Tracks authenticated session availability to validate the 99.5% uptime
SLO defined in spec.md SC-005.

A "session event" records whether the MCP server responded to a health
probe within the expected timeout.  A rolling window of the last N events
is used to compute availability.
"""

from __future__ import annotations

import datetime
import threading
from collections import deque
from dataclasses import dataclass
from typing import Optional

_WINDOW_SIZE = 1000  # Number of probe results to retain
_lock = threading.Lock()


@dataclass
class ProbeResult:
    timestamp: datetime.datetime
    success: bool


_probe_history: deque[ProbeResult] = deque(maxlen=_WINDOW_SIZE)


def record_probe(success: bool) -> None:
    """Record the result of a single MCP server health probe.

    Args:
        success: True if the probe succeeded (server responded), False otherwise.
    """
    with _lock:
        _probe_history.append(
            ProbeResult(timestamp=datetime.datetime.utcnow(), success=success)
        )


def get_availability_report() -> dict:
    """Return a rolling availability report for the last N probes.

    Returns:
        Dict with keys:
          - ``total``:        Total number of probes recorded.
          - ``successful``:   Number of successful probes.
          - ``availability``: Fraction (0.0–1.0) of successful probes.
          - ``slo_met``:      True if availability >= 99.5%.
    """
    with _lock:
        results = list(_probe_history)

    total = len(results)
    if total == 0:
        return {"total": 0, "successful": 0, "availability": 1.0, "slo_met": True}

    successful = sum(1 for r in results if r.success)
    availability = successful / total

    return {
        "total": total,
        "successful": successful,
        "availability": availability,
        "slo_met": availability >= 0.995,
    }


def reset_uptime_metrics() -> None:
    """Clear all recorded probe history (for testing)."""
    with _lock:
        _probe_history.clear()
