#!/usr/bin/env python3
"""
intervals.icu MCP Server - Extended Edition

Provides Claude Desktop with comprehensive access to intervals.icu training data APIs.
Supports athlete wellness, workouts, activities, fitness trends, calendar management,
workout library, training plans, and coaching features.
"""

import asyncio
import base64
import json
import os
from datetime import datetime, timedelta
from typing import Any, Optional, Literal
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
    method: str = "GET",
    params: Optional[dict[str, Any]] = None,
    json_data: Optional[dict[str, Any]] = None,
    use_activity_endpoint: bool = False
) -> Any:
    """Make authenticated request to intervals.icu API.
    
    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, PUT, DELETE)
        params: Query parameters
        json_data: JSON payload for POST/PUT
        use_activity_endpoint: Use /api/v1/activity/{id} instead of /api/v1/athlete/{id}
    """
    api_key, athlete_id = get_credentials()
    
    if use_activity_endpoint:
        # For activity-specific endpoints like /api/v1/activity/{id}
        url = f"https://intervals.icu/api/v1/{endpoint}"
    else:
        # Standard athlete endpoints
        base_url = f"https://intervals.icu/api/v1/athlete/{athlete_id}"
        url = f"{base_url}/{endpoint}" if endpoint else base_url
    
    headers = {
        "Authorization": f"Basic {api_key}",
        "Accept": "application/json"
    }
    
    if json_data:
        headers["Content-Type"] = "application/json"
    
    if http_client is None:
        raise RuntimeError("HTTP client not initialized")
    
    response = await http_client.request(
        method=method,
        url=url,
        headers=headers,
        params=params,
        json=json_data
    )
    response.raise_for_status()
    
    # Return empty dict for successful DELETE operations with no content
    if method == "DELETE" or response.status_code == 204:
        return {"status": "success"}
    
    # Handle different content types
    content_type = response.headers.get("content-type", "")
    if "application/json" in content_type:
        return response.json()
    else:
        # For CSV or other formats, return as text
        return {"content": response.text, "content_type": content_type}


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available intervals.icu API tools."""
    return [
        # ========== ATHLETE PROFILE ==========
        Tool(
            name="get_athlete_profile",
            description="Get athlete profile information including name, weight, FTP, zones, and settings",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        
        # ========== WELLNESS DATA ==========
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
            name="get_wellness_single",
            description="Get wellness data for a specific date",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format"
                    }
                },
                "required": ["date"]
            }
        ),
        Tool(
            name="update_wellness",
            description="Update wellness data for a specific date (weight, HRV, sleep, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "Date in YYYY-MM-DD format"
                    },
                    "data": {
                        "type": "object",
                        "description": "Wellness fields to update (e.g., weight, restingHR, hrv, sleepSecs, locked)"
                    }
                },
                "required": ["date", "data"]
            }
        ),
        Tool(
            name="update_wellness_bulk",
            description="Update wellness data for multiple dates at once",
            inputSchema={
                "type": "object",
                "properties": {
                    "entries": {
                        "type": "array",
                        "description": "Array of wellness entries, each with 'id' (date) and wellness fields",
                        "items": {
                            "type": "object"
                        }
                    }
                },
                "required": ["entries"]
            }
        ),
        
        # ========== ACTIVITIES ==========
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
            name="get_activities_csv",
            description="Export all activities to CSV format",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_activity_details",
            description="Get detailed information for a specific activity including streams and intervals",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_id": {
                        "type": "string",
                        "description": "The activity ID"
                    },
                    "include_intervals": {
                        "type": "boolean",
                        "description": "Include detected interval data (default: true)"
                    }
                },
                "required": ["activity_id"]
            }
        ),
        Tool(
            name="update_activity",
            description="Update activity metadata (name, description, type, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_id": {
                        "type": "string",
                        "description": "The activity ID"
                    },
                    "data": {
                        "type": "object",
                        "description": "Fields to update (e.g., name, description, type)"
                    }
                },
                "required": ["activity_id", "data"]
            }
        ),
        Tool(
            name="delete_activity",
            description="Delete an activity",
            inputSchema={
                "type": "object",
                "properties": {
                    "activity_id": {
                        "type": "string",
                        "description": "The activity ID to delete"
                    }
                },
                "required": ["activity_id"]
            }
        ),
        
        # ========== FITNESS TRENDS ==========
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
        
        # ========== CALENDAR & EVENTS ==========
        Tool(
            name="get_calendars",
            description="Get list of all calendars",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_events",
            description="Get planned events (races, workouts, notes) from the calendar",
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
                    },
                    "calendar_id": {
                        "type": "string",
                        "description": "Optional: Filter by specific calendar ID"
                    }
                },
            }
        ),
        Tool(
            name="get_event",
            description="Get details for a specific calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "The event ID"
                    }
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="create_event",
            description="Create a new calendar event (workout, race, or note)",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_data": {
                        "type": "object",
                        "description": "Event details (start_date_local, category, name, type, etc.)"
                    }
                },
                "required": ["event_data"]
            }
        ),
        Tool(
            name="update_event",
            description="Update an existing calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "The event ID"
                    },
                    "event_data": {
                        "type": "object",
                        "description": "Fields to update"
                    }
                },
                "required": ["event_id", "event_data"]
            }
        ),
        Tool(
            name="delete_event",
            description="Delete a calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "The event ID to delete"
                    }
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="get_planned_workouts",
            description="Get planned workouts from the training calendar (filters for WORKOUT category)",
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
        
        # ========== WORKOUT LIBRARY ==========
        Tool(
            name="get_folders",
            description="Get all workout library folders and their contents",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="create_folder",
            description="Create a new workout library folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Folder name"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="update_folder",
            description="Update folder metadata",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_id": {
                        "type": "string",
                        "description": "The folder ID"
                    },
                    "data": {
                        "type": "object",
                        "description": "Fields to update (e.g., name)"
                    }
                },
                "required": ["folder_id", "data"]
            }
        ),
        Tool(
            name="delete_folder",
            description="Delete a workout library folder",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder_id": {
                        "type": "string",
                        "description": "The folder ID to delete"
                    }
                },
                "required": ["folder_id"]
            }
        ),
        Tool(
            name="get_workouts",
            description="Get all workouts from the library",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_workout",
            description="Get a specific workout from the library",
            inputSchema={
                "type": "object",
                "properties": {
                    "workout_id": {
                        "type": "string",
                        "description": "The workout ID"
                    }
                },
                "required": ["workout_id"]
            }
        ),
        Tool(
            name="create_workout",
            description="Create a new workout in the library",
            inputSchema={
                "type": "object",
                "properties": {
                    "workout_data": {
                        "type": "object",
                        "description": "Workout details (name, description, folder_id, type)"
                    }
                },
                "required": ["workout_data"]
            }
        ),
        Tool(
            name="update_workout",
            description="Update an existing workout in the library",
            inputSchema={
                "type": "object",
                "properties": {
                    "workout_id": {
                        "type": "string",
                        "description": "The workout ID"
                    },
                    "workout_data": {
                        "type": "object",
                        "description": "Fields to update"
                    }
                },
                "required": ["workout_id", "workout_data"]
            }
        ),
        Tool(
            name="delete_workout",
            description="Delete a workout from the library",
            inputSchema={
                "type": "object",
                "properties": {
                    "workout_id": {
                        "type": "string",
                        "description": "The workout ID to delete"
                    }
                },
                "required": ["workout_id"]
            }
        ),
        
        # ========== TRAINING PLANS ==========
        Tool(
            name="get_training_plans",
            description="Get all training plans",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="create_training_plan",
            description="Create a new training plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_data": {
                        "type": "object",
                        "description": "Training plan details"
                    }
                },
                "required": ["plan_data"]
            }
        ),
        Tool(
            name="update_training_plan",
            description="Update an existing training plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "The plan ID"
                    },
                    "plan_data": {
                        "type": "object",
                        "description": "Fields to update"
                    }
                },
                "required": ["plan_id", "plan_data"]
            }
        ),
        Tool(
            name="delete_training_plan",
            description="Delete a training plan",
            inputSchema={
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "The plan ID to delete"
                    }
                },
                "required": ["plan_id"]
            }
        ),
        
        # ========== COACHING ==========
        Tool(
            name="get_coached_athletes",
            description="Get list of athletes you coach with their current fitness metrics",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        Tool(
            name="get_wellness_summary",
            description="Get wellness overview for coached athletes",
            inputSchema={
                "type": "object",
                "properties": {},
            }
        ),
        
        # ========== PERFORMANCE ANALYSIS ==========
        Tool(
            name="get_power_curve",
            description="Get power curve data (best power efforts) for different durations from recent activities",
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
        
        # ========== ATHLETE PROFILE ==========
        if name == "get_athlete_profile":
            data = await make_request("")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        # ========== WELLNESS DATA ==========
        elif name == "get_wellness_data":
            start_date = arguments.get("start_date") or (today - timedelta(days=30)).isoformat()
            end_date = arguments.get("end_date") or today.isoformat()
            
            data = await make_request("wellness", params={
                "oldest": start_date,
                "newest": end_date
            })
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "get_wellness_single":
            date = arguments.get("date")
            if not date:
                raise ValueError("date is required")
            
            data = await make_request(f"wellness/{date}")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "update_wellness":
            date = arguments.get("date")
            wellness_data = arguments.get("data")
            
            if not date or not wellness_data:
                raise ValueError("date and data are required")
            
            data = await make_request(
                f"wellness/{date}",
                method="PUT",
                json_data=wellness_data
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "update_wellness_bulk":
            entries = arguments.get("entries")
            if not entries:
                raise ValueError("entries array is required")
            
            data = await make_request(
                "wellness-bulk",
                method="PUT",
                json_data=entries
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        # ========== ACTIVITIES ==========
        elif name == "get_activities":
            start_date = arguments.get("start_date") or (today - timedelta(days=30)).isoformat()
            end_date = arguments.get("end_date") or today.isoformat()
            
            data = await make_request("activities", params={
                "oldest": start_date,
                "newest": end_date
            })
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "get_activities_csv":
            data = await make_request("activities.csv")
            return [TextContent(type="text", text=data.get("content", str(data)))]
        
        elif name == "get_activity_details":
            activity_id = arguments.get("activity_id")
            include_intervals = arguments.get("include_intervals", True)
            
            if not activity_id:
                raise ValueError("activity_id is required")
            
            params = {"intervals": "true"} if include_intervals else {}
            data = await make_request(
                f"activity/{activity_id}",
                params=params,
                use_activity_endpoint=True
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "update_activity":
            activity_id = arguments.get("activity_id")
            activity_data = arguments.get("data")
            
            if not activity_id or not activity_data:
                raise ValueError("activity_id and data are required")
            
            data = await make_request(
                f"activity/{activity_id}",
                method="PUT",
                json_data=activity_data,
                use_activity_endpoint=True
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "delete_activity":
            activity_id = arguments.get("activity_id")
            if not activity_id:
                raise ValueError("activity_id is required")
            
            data = await make_request(
                f"activity/{activity_id}",
                method="DELETE",
                use_activity_endpoint=True
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        # ========== FITNESS TRENDS ==========
        elif name == "get_fitness_trends":
            start_date = arguments.get("start_date") or (today - timedelta(days=90)).isoformat()
            end_date = arguments.get("end_date") or today.isoformat()
            
            data = await make_request("wellness", params={
                "oldest": start_date,
                "newest": end_date
            })
            
            # Extract fitness metrics (CTL, ATL, TSB)
            fitness_data = []
            for entry in data:
                if any(k in entry for k in ["ctl", "atl", "tsb", "rampRate"]):
                    fitness_data.append({
                        "date": entry.get("id"),
                        "ctl": entry.get("ctl"),
                        "atl": entry.get("atl"),
                        "tsb": entry.get("tsb"),
                        "ramp_rate": entry.get("rampRate"),
                    })
            
            return [TextContent(type="text", text=json.dumps(fitness_data, indent=2))]
        
        # ========== CALENDAR & EVENTS ==========
        elif name == "get_calendars":
            data = await make_request("calendars")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "get_events":
            start_date = arguments.get("start_date") or today.isoformat()
            end_date = arguments.get("end_date") or (today + timedelta(days=90)).isoformat()
            calendar_id = arguments.get("calendar_id")
            
            params = {
                "oldest": start_date,
                "newest": end_date
            }
            if calendar_id:
                params["calendar_id"] = calendar_id
            
            data = await make_request("events", params=params)
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "get_event":
            event_id = arguments.get("event_id")
            if not event_id:
                raise ValueError("event_id is required")
            
            data = await make_request(f"events/{event_id}")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "create_event":
            event_data = arguments.get("event_data")
            if not event_data:
                raise ValueError("event_data is required")
            
            data = await make_request(
                "events",
                method="POST",
                json_data=event_data
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "update_event":
            event_id = arguments.get("event_id")
            event_data = arguments.get("event_data")
            
            if not event_id or not event_data:
                raise ValueError("event_id and event_data are required")
            
            data = await make_request(
                f"events/{event_id}",
                method="PUT",
                json_data=event_data
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "delete_event":
            event_id = arguments.get("event_id")
            if not event_id:
                raise ValueError("event_id is required")
            
            data = await make_request(
                f"events/{event_id}",
                method="DELETE"
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "get_planned_workouts":
            start_date = arguments.get("start_date") or today.isoformat()
            end_date = arguments.get("end_date") or (today + timedelta(days=14)).isoformat()
            
            data = await make_request("events", params={
                "oldest": start_date,
                "newest": end_date
            })
            
            # Filter for planned workouts (not races/events)
            workouts = [event for event in data if event.get("category") == "WORKOUT"]
            return [TextContent(type="text", text=json.dumps(workouts, indent=2))]
        
        # ========== WORKOUT LIBRARY ==========
        elif name == "get_folders":
            data = await make_request("folders")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "create_folder":
            folder_name = arguments.get("name")
            if not folder_name:
                raise ValueError("name is required")
            
            data = await make_request(
                "folders",
                method="POST",
                json_data={"name": folder_name}
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "update_folder":
            folder_id = arguments.get("folder_id")
            folder_data = arguments.get("data")
            
            if not folder_id or not folder_data:
                raise ValueError("folder_id and data are required")
            
            data = await make_request(
                f"folders/{folder_id}",
                method="PUT",
                json_data=folder_data
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "delete_folder":
            folder_id = arguments.get("folder_id")
            if not folder_id:
                raise ValueError("folder_id is required")
            
            data = await make_request(
                f"folders/{folder_id}",
                method="DELETE"
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "get_workouts":
            data = await make_request("workouts")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "get_workout":
            workout_id = arguments.get("workout_id")
            if not workout_id:
                raise ValueError("workout_id is required")
            
            data = await make_request(f"workouts/{workout_id}")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "create_workout":
            workout_data = arguments.get("workout_data")
            if not workout_data:
                raise ValueError("workout_data is required")
            
            data = await make_request(
                "workouts",
                method="POST",
                json_data=workout_data
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "update_workout":
            workout_id = arguments.get("workout_id")
            workout_data = arguments.get("workout_data")
            
            if not workout_id or not workout_data:
                raise ValueError("workout_id and workout_data are required")
            
            data = await make_request(
                f"workouts/{workout_id}",
                method="PUT",
                json_data=workout_data
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "delete_workout":
            workout_id = arguments.get("workout_id")
            if not workout_id:
                raise ValueError("workout_id is required")
            
            data = await make_request(
                f"workouts/{workout_id}",
                method="DELETE"
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        # ========== TRAINING PLANS ==========
        elif name == "get_training_plans":
            data = await make_request("plans")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "create_training_plan":
            plan_data = arguments.get("plan_data")
            if not plan_data:
                raise ValueError("plan_data is required")
            
            data = await make_request(
                "plans",
                method="POST",
                json_data=plan_data
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "update_training_plan":
            plan_id = arguments.get("plan_id")
            plan_data = arguments.get("plan_data")
            
            if not plan_id or not plan_data:
                raise ValueError("plan_id and plan_data are required")
            
            data = await make_request(
                f"plans/{plan_id}",
                method="PUT",
                json_data=plan_data
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "delete_training_plan":
            plan_id = arguments.get("plan_id")
            if not plan_id:
                raise ValueError("plan_id is required")
            
            data = await make_request(
                f"plans/{plan_id}",
                method="DELETE"
            )
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        # ========== COACHING ==========
        elif name == "get_coached_athletes":
            data = await make_request("athlete-summary")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        elif name == "get_wellness_summary":
            data = await make_request("wellness-summary")
            return [TextContent(type="text", text=json.dumps(data, indent=2))]
        
        # ========== PERFORMANCE ANALYSIS ==========
        elif name == "get_power_curve":
            start_date = arguments.get("start_date") or (today - timedelta(days=90)).isoformat()
            end_date = arguments.get("end_date") or today.isoformat()
            
            # Get activities to extract power curve data
            activities = await make_request("activities", params={
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
            
            return [TextContent(type="text", text=json.dumps(power_curves, indent=2))]
        
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
