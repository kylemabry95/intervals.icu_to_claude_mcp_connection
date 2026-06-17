"""
Endpoint coverage matrix test.

Asserts that every intervals.icu endpoint documented in contracts/API.md
has a corresponding MCP tool registered in server.py.
"""

from __future__ import annotations

import asyncio
import re
from pathlib import Path

import pytest

# Absolute path to the contracts API doc
_API_MD = Path(__file__).parents[2] / "specs" / "001-standalone-intervals-app" / "contracts" / "API.md"


def _parse_api_doc_tools(path: Path) -> list[str]:
    """Extract MCP tool names from the API.md contracts file."""
    if not path.exists():
        return []
    text = path.read_text()
    # Look for lines like: | `tool_name` | GET /... |
    pattern = re.compile(r"`([a-z][a-z0-9_]+)`")
    # Only pick up names that look like MCP tool names (snake_case, >=3 chars)
    names = []
    for line in text.splitlines():
        if "|" not in line:
            continue
        matches = pattern.findall(line)
        for m in matches:
            if len(m) >= 3 and "_" in m:
                names.append(m)
    return list(dict.fromkeys(names))  # deduplicated, order-preserving


class TestEndpointCoverageMatrix:
    """Every tool documented in API.md must be registered in the MCP server."""

    @pytest.fixture(scope="class")
    def registered_tools(self):
        from server import list_tools
        tools = asyncio.run(list_tools())
        return {t.name for t in tools}

    def test_api_doc_exists(self):
        assert _API_MD.exists(), f"contracts/API.md not found at {_API_MD}"

    def test_all_documented_tools_are_registered(self, registered_tools):
        documented = _parse_api_doc_tools(_API_MD)
        if not documented:
            pytest.skip("No tool names found in API.md — skipping coverage check.")
        missing = [t for t in documented if t not in registered_tools]
        assert not missing, (
            f"The following tools are documented in API.md but not registered "
            f"in server.py: {missing}"
        )
