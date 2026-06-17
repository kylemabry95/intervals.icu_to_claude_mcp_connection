"""
Contract tests: verify MCP tool schema integrity and required fields.

These tests validate that each tool registered by server.py:
  - Has a non-empty name and description
  - Has a valid JSON Schema for inputSchema
  - Required fields listed in inputSchema actually exist in properties
"""

from __future__ import annotations

import asyncio
from typing import Any

import pytest


EXPECTED_TOOL_NAMES = [
    "get_athlete_profile",
    "get_wellness_data",
    "get_wellness_single",
    "update_wellness",
    "update_wellness_bulk",
    "get_activities",
    "get_activities_csv",
    "get_activity_details",
    "update_activity",
    "delete_activity",
    "get_events",
    "create_event",
    "update_event",
    "delete_event",
    "get_workouts",
    "get_workout",
    "create_workout",
    "update_workout",
    "delete_workout",
    "get_training_plans",
]


class TestMCPContracts:
    """Validate MCP tool schema contracts."""

    @pytest.fixture(scope="class")
    def tools(self):
        from server import list_tools
        return asyncio.run(list_tools())

    def test_expected_tools_are_registered(self, tools):
        tool_names = {t.name for t in tools}
        missing = [n for n in EXPECTED_TOOL_NAMES if n not in tool_names]
        assert not missing, f"Missing expected MCP tools: {missing}"

    def test_all_tools_have_description(self, tools):
        for tool in tools:
            assert tool.description, f"Tool '{tool.name}' is missing a description."

    def test_all_tools_have_input_schema(self, tools):
        for tool in tools:
            assert tool.inputSchema, f"Tool '{tool.name}' is missing inputSchema."
            assert tool.inputSchema.get("type") == "object", (
                f"Tool '{tool.name}' inputSchema must have type='object'."
            )

    def test_required_fields_exist_in_properties(self, tools):
        for tool in tools:
            schema = tool.inputSchema or {}
            required = schema.get("required", [])
            properties = schema.get("properties", {})
            for field in required:
                assert field in properties, (
                    f"Tool '{tool.name}': required field '{field}' "
                    f"not found in properties."
                )

    def test_tool_names_are_snake_case(self, tools):
        import re
        pattern = re.compile(r"^[a-z][a-z0-9_]*$")
        for tool in tools:
            assert pattern.match(tool.name), (
                f"Tool name '{tool.name}' is not snake_case."
            )
