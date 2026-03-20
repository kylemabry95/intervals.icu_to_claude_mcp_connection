#!/usr/bin/env python3
"""
intervals.icu MCP Server

Provides Claude Desktop with access to intervals.icu training data APIs.
Supports athlete wellness, workouts, activities, and fitness trend analysis.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional
from urllib.parse import quote

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# Initialize MCP server
app = Server("intervals-icu")

# Global HTTP client
http_client: Optional[httpx.AsyncClient] = None


def get_credentials() -> tuple[str, str]:
    """Get intervals.icu credentials from environment variables."""
    api_key = os.getenv("INTERVALS_API_KEY")
    athlete_id = os.getenv("INTERVALS_ATHLETE_ID")
    
    if not api_key or not athlete_id:
        raise ValueError(
            "Missing credentials. Set INTERVALS_API_KEY and INTERVALS_ATHLETE_ID "
            "environment variables."
        )
    
    return api_key, athlete_id


async def make_request(
    endpoint: str,
    params: Optional[dict[str, Any]] = None
) -> dict[str, Any]:
    """Make authenticated request to intervals.icu API."""
    api_key, athlete_id = get_credentials()
    
    base_url = f"https://intervals.icu/api/v1/athlete/{athlete_id}"
    url = f"{base_url}/{endpoint}"
    
    headers = {
        "Authorization": f"Basic {api_key}",
        "Accept": "application/json"
    }
    
    if http_client is None:
        raise RuntimeError("HTTP client not initialized")
    
    response = await http_client.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available intervals.icu API tools."""
    return [
        Tool(
            name="get_athlete_profile",
            description="Get athlete profile information including name, weight, FTP, and other settings",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_wellness_data",
            description="Get wellness data (sleep, HRV, resting HR, weight, etc.) for a date range",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (defaults to 30 days ago)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (defaults to today)"
                    }
                },
            }
        ),
        Tool(
            name="get_activities",
            description="Get training activities/workouts for a date range with detailed metrics",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (defaults to 30 days ago)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (defaults to today)"
                    }
                },
            }
        ),
        Tool(
            name="get_activity_details",
            description="Get detailed information for a specific activity including streams (power, HR, cadence, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_id": {
                        "type": "string",
                        "description": "The activity ID"
                    }
                },
                "required": ["activity_id"]
            }
        ),
        Tool(
            name="get_fitness_trends",
            description="Get fitness trend data (CTL, ATL, TSB) for analyzing training load and fatigue",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (defaults to 90 days ago)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (defaults to today)"
                    }
                },
            }
        ),
        Tool(
            name="get_events",
            description="Get planned events (races, key workouts) from the calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (defaults to today)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (defaults to 90 days from today)"
                    }
                },
            }
        ),
        Tool(
            name="get_planned_workouts",
            description="Get planned workouts from the training calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (defaults to today)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (defaults to 14 days from today)"
                    }
                },
            }
        ),
        Tool(
            name="get_power_curve",
            description="Get power curve data (best power efforts) for different durations",
            inputSchema={
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format (defaults to 90 days ago)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format (defaults to today)"
                    }
                },
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls for intervals.icu API."""
    
    try:
        # Default date ranges
        today = datetime.now().date()
        
        if name == "get_athlete_profile":
            data = await make_request("")
            return [TextContent(
                type="text",
                text=json.dumps(data, indent=2)
            )]
        
        elif name == "get_wellness_data":
            start_date = arguments.get("start_date") or (today - timedelta(days=30)).isoformat()
            end_date = arguments.get("end_date") or today.isoformat()
            
            data = await make_request("wellness", {
                "oldest": start_date,
                "newest": end_date
            })
            
            return [TextContent(
                type="text",
                text=json.dumps(data, indent=2)
            )]
        
        elif name == "get_activities":
            start_date = arguments.get("start_date") or (today - timedelta(days=30)).isoformat()
            end_date = arguments.get("end_date") or today.isoformat()
            
            data = await make_request("activities", {
                "oldest": start_date,
                "newest": end_date
            })
            
            return [TextContent(
                type="text",
                text=json.dumps(data, indent=2)
            )]
        
        elif name == "get_activity_details":
            activity_id = arguments.get("activity_id")
            if not activity_id:
                raise ValueError("activity_id is required")
            
            data = await make_request(f"activities/{activity_id}")
            
            return [TextContent(
                type="text",
                text=json.dumps(data, indent=2)
            )]
        
        elif name == "get_fitness_trends":
            start_date = arguments.get("start_date") or (today - timedelta(days=90)).isoformat()
            end_date = arguments.get("end_date") or today.isoformat()
            
            data = await make_request("wellness", {
                "oldest": start_date,
                "newest": end_date
            })
            
            # Extract fitness metrics (CTL, ATL, TSB)
            fitness_data = []
            for entry in data:
                if any(k in entry for k in ["ctl", "atl", "tsb", "rampRate"]):
                    fitness_data.append({
                        "date": entry.get("id"),
                        "ctl": entry.get("ctl"),  # Chronic Training Load (Fitness)
                        "atl": entry.get("atl"),  # Acute Training Load (Fatigue)
                        "tsb": entry.get("tsb"),  # Training Stress Balance (Form)
                        "ramp_rate": entry.get("rampRate"),
                    })
            
            return [TextContent(
                type="text",
                text=json.dumps(fitness_data, indent=2)
            )]
        
        elif name == "get_events":
            start_date = arguments.get("start_date") or today.isoformat()
            end_date = arguments.get("end_date") or (today + timedelta(days=90)).isoformat()
            
            data = await make_request("events", {
                "oldest": start_date,
                "newest": end_date
            })
            
            return [TextContent(
                type="text",
                text=json.dumps(data, indent=2)
            )]
        
        elif name == "get_planned_workouts":
            start_date = arguments.get("start_date") or today.isoformat()
            end_date = arguments.get("end_date") or (today + timedelta(days=14)).isoformat()
            
            data = await make_request("events", {
                "oldest": start_date,
                "newest": end_date
            })
            
            # Filter for planned workouts (not races/events)
            workouts = [event for event in data if event.get("category") == "WORKOUT"]
            
            return [TextContent(
                type="text",
                text=json.dumps(workouts, indent=2)
            )]
        
        elif name == "get_power_curve":
            start_date = arguments.get("start_date") or (today - timedelta(days=90)).isoformat()
            end_date = arguments.get("end_date") or today.isoformat()
            
            # Get activities to calculate power curve
            activities = await make_request("activities", {
                "oldest": start_date,
                "newest": end_date
            })
            
            # Extract power curve data if available
            power_curves = []
            for activity in activities:
                if "power_curve" in activity or "icu_power_curve" in activity:
                    power_curves.append({
                        "date": activity.get("start_date_local"),
                        "name": activity.get("name"),
                        "type": activity.get("type"),
                        "power_curve": activity.get("power_curve") or activity.get("icu_power_curve")
                    })
            
            return [TextContent(
                type="text",
                text=json.dumps(power_curves, indent=2)
            )]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    global http_client
    
    async with httpx.AsyncClient() as client:
        http_client = client
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )


if __name__ == "__main__":
    asyncio.run(main())
