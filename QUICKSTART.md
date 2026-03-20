# intervals.icu MCP Server - Quick Start Guide

## Setup Steps

### 1. Get Your intervals.icu Credentials
1. Go to https://intervals.icu and log in
2. Navigate to Settings → API
3. Generate an API key
4. Note your athlete ID from the URL: `intervals.icu/athlete/{YOUR_ID}`

### 2. Install Dependencies
```bash
cd intervals-icu-mcp
pip install -r requirements.txt
```

### 3. Configure Claude Desktop

Find your config file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

Add this configuration (update the paths and credentials):

```json
{
  "mcpServers": {
    "intervals-icu": {
      "command": "python",
      "args": ["/FULL/PATH/TO/intervals-icu-mcp/server.py"],
      "env": {
        "INTERVALS_API_KEY": "YOUR_API_KEY",
        "INTERVALS_ATHLETE_ID": "YOUR_ATHLETE_ID"
      }
    }
  }
}
```

### 4. Test Locally (Optional)
```bash
export INTERVALS_API_KEY="your_key"
export INTERVALS_ATHLETE_ID="your_id"
python test_server.py
```

### 5. Restart Claude Desktop
Close and reopen Claude Desktop to load the MCP server.

## Available Tools

1. **get_athlete_profile** - Your profile, FTP, zones
2. **get_wellness_data** - HRV, sleep, resting HR, weight
3. **get_activities** - Training workouts and metrics
4. **get_activity_details** - Detailed activity data
5. **get_fitness_trends** - CTL, ATL, TSB analysis
6. **get_events** - Upcoming races and events
7. **get_planned_workouts** - Scheduled training sessions
8. **get_power_curve** - Best power efforts

## Example Questions to Ask Claude

- "What's my fitness trend over the last month?"
- "Show me my HRV and sleep quality this week"
- "What were my hardest workouts in the past 2 weeks?"
- "Am I building fitness too quickly based on my CTL ramp rate?"
- "What races do I have coming up?"
- "Analyze my training load and recovery balance"
- "What's my current form (TSB)?"

## Troubleshooting

**Server not showing up:**
- Verify config file path is correct
- Check JSON syntax is valid
- Ensure full absolute path to server.py
- Restart Claude Desktop

**Authentication errors:**
- Double-check API key and athlete ID
- Verify intervals.icu subscription is active

**No data returned:**
- Check date format is YYYY-MM-DD
- Verify you have data in intervals.icu for that period

## Security Note

Your API credentials are stored locally in the Claude Desktop config file. No data is sent to third parties - all requests go directly from your machine to intervals.icu.
