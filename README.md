# intervals.icu MCP Server

A Model Context Protocol (MCP) server that provides Claude Desktop with access to [intervals.icu](https://intervals.icu) training data APIs. This enables Claude to analyze your athletic training data, wellness metrics, fitness trends, and planned workouts.

## Features

The server provides access to the following intervals.icu APIs:

### 🏃 Athlete Profile
- **get_athlete_profile**: Get athlete information including FTP, weight, training zones, and settings

### 💪 Wellness & Recovery
- **get_wellness_data**: Access daily wellness metrics:
  - Sleep quality and duration
  - HRV (Heart Rate Variability)
  - Resting heart rate
  - Weight and body composition
  - Subjective wellness scores
  - Readiness and recovery metrics

### 🚴 Training Activities
- **get_activities**: Retrieve workouts/activities with detailed metrics:
  - Power, heart rate, pace data
  - Training stress scores (TSS)
  - Intensity factors
  - Duration and distance
  - Activity type (cycling, running, swimming, etc.)

- **get_activity_details**: Get granular data for specific activities including power/HR streams

### 📊 Fitness Analytics
- **get_fitness_trends**: Analyze training load and form:
  - CTL (Chronic Training Load / Fitness)
  - ATL (Acute Training Load / Fatigue)  
  - TSB (Training Stress Balance / Form)
  - Ramp rate

- **get_power_curve**: Access best power efforts across different durations

### 📅 Planning
- **get_events**: Retrieve planned races and key events
- **get_planned_workouts**: Access upcoming scheduled training sessions

## Installation

### 1. Get intervals.icu API Credentials

1. Log in to [intervals.icu](https://intervals.icu)
2. Go to your athlete settings
3. Generate an API key
4. Note your athlete ID (visible in the URL: `intervals.icu/athlete/{ATHLETE_ID}`)

### 2. Install Python Dependencies

```bash
cd intervals-icu-mcp
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

### 3. Configure Claude Desktop

Add the MCP server to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "intervals-icu": {
      "command": "python",
      "args": ["/absolute/path/to/intervals-icu-mcp/server.py"],
      "env": {
        "INTERVALS_API_KEY": "your_api_key_here",
        "INTERVALS_ATHLETE_ID": "your_athlete_id_here"
      }
    }
  }
}
```

**Important**: Replace:
- `/absolute/path/to/intervals-icu-mcp/server.py` with the actual path to server.py
- `your_api_key_here` with your intervals.icu API key
- `your_athlete_id_here` with your athlete ID

### 4. Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP server.

## Usage Examples

Once configured, you can ask Claude questions like:

### Wellness & Recovery
- "What's my HRV trend over the past 2 weeks?"
- "How has my sleep quality been this month?"
- "Show me my resting heart rate trend"
- "Am I getting enough recovery based on my wellness data?"

### Training Analysis
- "Summarize my training volume for the past 30 days"
- "What were my hardest workouts this week?"
- "Compare my cycling vs running volume this month"
- "Show me my longest activities this year"

### Fitness Trends
- "What's my current fitness (CTL) and form (TSB)?"
- "Am I building fitness too quickly? Check my ramp rate"
- "When was I at peak fitness in the last 90 days?"
- "Analyze my training load balance"

### Performance
- "What's my best 20-minute power in the last 90 days?"
- "Show me my power curve improvements over time"
- "What were my best efforts at different durations?"

### Planning
- "What races do I have coming up?"
- "Show me my planned workouts for next week"
- "What's my training schedule looking like?"

### Combined Analysis
- "How has my fitness progressed leading up to my next race?"
- "Is my wellness data suggesting I need more recovery?"
- "Analyze whether my training load matches my upcoming events"

## API Reference

### Tool: get_athlete_profile
Returns athlete profile information.

**Parameters**: None

**Returns**: Athlete profile with FTP, weight, zones, and settings

---

### Tool: get_wellness_data
Get wellness metrics for a date range.

**Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format (default: 30 days ago)
- `end_date` (optional): End date in YYYY-MM-DD format (default: today)

**Returns**: Array of daily wellness entries with HRV, sleep, weight, etc.

---

### Tool: get_activities
Get training activities for a date range.

**Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format (default: 30 days ago)
- `end_date` (optional): End date in YYYY-MM-DD format (default: today)

**Returns**: Array of activities with metrics

---

### Tool: get_activity_details
Get detailed data for a specific activity.

**Parameters**:
- `activity_id` (required): The activity ID

**Returns**: Detailed activity data including streams

---

### Tool: get_fitness_trends
Get CTL/ATL/TSB trend data.

**Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format (default: 90 days ago)
- `end_date` (optional): End date in YYYY-MM-DD format (default: today)

**Returns**: Array of fitness metrics by date

---

### Tool: get_events
Get planned events (races, key workouts).

**Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format (default: today)
- `end_date` (optional): End date in YYYY-MM-DD format (default: 90 days from today)

**Returns**: Array of calendar events

---

### Tool: get_planned_workouts
Get planned workouts from the calendar.

**Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format (default: today)
- `end_date` (optional): End date in YYYY-MM-DD format (default: 14 days from today)

**Returns**: Array of planned workout events

---

### Tool: get_power_curve
Get power curve data (best efforts).

**Parameters**:
- `start_date` (optional): Start date in YYYY-MM-DD format (default: 90 days ago)
- `end_date` (optional): End date in YYYY-MM-DD format (default: today)

**Returns**: Power curve data for different durations

## Troubleshooting

### Server Not Appearing in Claude Desktop

1. Check the config file path is correct for your OS
2. Ensure the JSON is valid (use a JSON validator)
3. Verify the absolute path to `server.py` is correct
4. Check that environment variables are set correctly
5. Look at Claude Desktop logs for error messages

### Authentication Errors

- Verify your API key is correct
- Ensure your athlete ID matches your account
- Check that your intervals.icu subscription is active

### No Data Returned

- Verify date ranges are valid (YYYY-MM-DD format)
- Check that you have data in intervals.icu for the requested period
- Ensure your athlete ID is correct

## Privacy & Security

- API credentials are stored in the Claude Desktop config file on your local machine
- All API requests go directly from your machine to intervals.icu
- No data is sent to third parties
- Claude processes responses locally

## intervals.icu API Documentation

For more details on the intervals.icu API, see:
- [intervals.icu API Documentation](https://intervals.icu/api/)
- [Forum Discussion on API](https://forum.intervals.icu/)

## Contributing

Contributions are welcome! This MCP server can be extended with additional intervals.icu API endpoints such as:
- Training plans
- Workout libraries
- Athlete comparisons
- Custom charts and analytics
- Stream data analysis
- Zone distribution analysis

## License

MIT License - feel free to use and modify for your own training analysis needs!

## Credits

Built for the [Model Context Protocol](https://modelcontextprotocol.io/) to integrate intervals.icu with Claude Desktop.
