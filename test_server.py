#!/usr/bin/env python3
"""
Test script for intervals.icu MCP server.

This script simulates MCP tool calls to verify the server works correctly.
Set INTERVALS_API_KEY and INTERVALS_ATHLETE_ID environment variables before running.
"""

import asyncio
import json
import os
from datetime import datetime, timedelta

# Mock the MCP imports for testing
class MockTextContent:
    def __init__(self, type, text):
        self.type = type
        self.text = text

# Import and patch
import sys
sys.path.insert(0, os.path.dirname(__file__))

# Mock MCP types
import mcp.types as mcp_types
mcp_types.TextContent = MockTextContent

import server


async def test_tools():
    """Test each tool in the MCP server."""
    
    print("Testing intervals.icu MCP Server")
    print("=" * 50)
    
    # Check credentials
    try:
        api_key, athlete_id = server.get_credentials()
        print(f"✓ Credentials found for athlete: {athlete_id}")
    except ValueError as e:
        print(f"✗ Error: {e}")
        print("\nPlease set environment variables:")
        print("  export INTERVALS_API_KEY='your_api_key'")
        print("  export INTERVALS_ATHLETE_ID='your_athlete_id'")
        return
    
    # Initialize HTTP client
    import httpx
    async with httpx.AsyncClient() as client:
        server.http_client = client
        
        print("\n" + "=" * 50)
        print("Testing Tools")
        print("=" * 50)
        
        # Test get_athlete_profile
        print("\n1. Testing get_athlete_profile...")
        try:
            result = await server.call_tool("get_athlete_profile", {})
            data = json.loads(result[0].text)
            print(f"✓ Retrieved profile for: {data.get('name', 'Unknown')}")
            print(f"  FTP: {data.get('ftp', 'N/A')} W")
            print(f"  Weight: {data.get('weight', 'N/A')} kg")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test get_wellness_data
        print("\n2. Testing get_wellness_data (last 7 days)...")
        try:
            today = datetime.now().date()
            week_ago = (today - timedelta(days=7)).isoformat()
            
            result = await server.call_tool("get_wellness_data", {
                "start_date": week_ago,
                "end_date": today.isoformat()
            })
            data = json.loads(result[0].text)
            print(f"✓ Retrieved {len(data)} wellness entries")
            if data:
                latest = data[-1]
                print(f"  Latest entry: {latest.get('id')}")
                if 'restingHR' in latest:
                    print(f"  Resting HR: {latest['restingHR']} bpm")
                if 'hrv' in latest:
                    print(f"  HRV: {latest['hrv']} ms")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test get_activities
        print("\n3. Testing get_activities (last 14 days)...")
        try:
            today = datetime.now().date()
            two_weeks_ago = (today - timedelta(days=14)).isoformat()
            
            result = await server.call_tool("get_activities", {
                "start_date": two_weeks_ago,
                "end_date": today.isoformat()
            })
            data = json.loads(result[0].text)
            print(f"✓ Retrieved {len(data)} activities")
            if data:
                for i, activity in enumerate(data[:3]):  # Show first 3
                    print(f"  {i+1}. {activity.get('name', 'Unnamed')} - {activity.get('type')} - {activity.get('moving_time', 0)//60} min")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test get_fitness_trends
        print("\n4. Testing get_fitness_trends (last 30 days)...")
        try:
            today = datetime.now().date()
            month_ago = (today - timedelta(days=30)).isoformat()
            
            result = await server.call_tool("get_fitness_trends", {
                "start_date": month_ago,
                "end_date": today.isoformat()
            })
            data = json.loads(result[0].text)
            print(f"✓ Retrieved fitness trends for {len(data)} days")
            if data:
                latest = [d for d in data if d.get('ctl') is not None]
                if latest:
                    recent = latest[-1]
                    print(f"  Latest metrics:")
                    print(f"    CTL (Fitness): {recent.get('ctl', 'N/A')}")
                    print(f"    ATL (Fatigue): {recent.get('atl', 'N/A')}")
                    print(f"    TSB (Form): {recent.get('tsb', 'N/A')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test get_events
        print("\n5. Testing get_events (next 60 days)...")
        try:
            today = datetime.now().date()
            future = (today + timedelta(days=60)).isoformat()
            
            result = await server.call_tool("get_events", {
                "start_date": today.isoformat(),
                "end_date": future
            })
            data = json.loads(result[0].text)
            print(f"✓ Retrieved {len(data)} upcoming events")
            if data:
                for i, event in enumerate(data[:3]):
                    print(f"  {i+1}. {event.get('name', 'Unnamed')} - {event.get('start_date_local')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        # Test get_planned_workouts
        print("\n6. Testing get_planned_workouts (next 7 days)...")
        try:
            today = datetime.now().date()
            week_ahead = (today + timedelta(days=7)).isoformat()
            
            result = await server.call_tool("get_planned_workouts", {
                "start_date": today.isoformat(),
                "end_date": week_ahead
            })
            data = json.loads(result[0].text)
            print(f"✓ Retrieved {len(data)} planned workouts")
            if data:
                for i, workout in enumerate(data[:3]):
                    print(f"  {i+1}. {workout.get('name', 'Unnamed')} - {workout.get('start_date_local')}")
        except Exception as e:
            print(f"✗ Error: {e}")
        
        print("\n" + "=" * 50)
        print("Testing Complete!")
        print("=" * 50)
        print("\nIf all tests passed, your MCP server is ready to use with Claude Desktop.")


if __name__ == "__main__":
    asyncio.run(test_tools())
