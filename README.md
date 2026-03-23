# intervals.icu MCP Server

A Model Context Protocol (MCP) server that provides Claude Desktop with access to [intervals.icu](https://intervals.icu) training data APIs. This enables Claude to analyze your athletic training data, wellness metrics, fitness trends, and planned workouts.

## Features

The server provides comprehensive access to intervals.icu APIs:

### 👤 **Athlete Profile**
- **get_athlete_profile**: Get athlete information including FTP, weight, training zones, and settings

### 💪 **Wellness & Recovery**
- **get_wellness_data**: Access daily wellness metrics for date ranges
- **get_wellness_single**: Get wellness data for a specific date
- **update_wellness**: Update wellness data for a specific date
- **update_wellness_bulk**: Batch update wellness entries

**Wellness metrics include:**
  - Sleep quality and duration
  - HRV (Heart Rate Variability)
  - Resting heart rate
  - Weight and body composition
  - Subjective wellness scores (fatigue, soreness, stress, motivation)
  - Readiness and recovery metrics
  - CTL, ATL, TSB (fitness, fatigue, form)

### 🚴 **Training Activities**
- **get_activities**: Retrieve workouts for date ranges with detailed metrics
- **get_activities_csv**: Export all activities to CSV
- **get_activity_details**: Get granular data including power/HR streams and detected intervals
- **update_activity**: Modify activity metadata (name, description, type)
- **delete_activity**: Remove an activity

**Activity data includes:**
  - Power, heart rate, pace, cadence data
  - Training stress scores (TSS)
  - Intensity factors
  - Duration and distance
  - Detected intervals
  - Power curves
  - Time in zones

### 📊 **Fitness Analytics**
- **get_fitness_trends**: Analyze training load and form over time
  - CTL (Chronic Training Load / Fitness)
  - ATL (Acute Training Load / Fatigue)  
  - TSB (Training Stress Balance / Form)
  - Ramp rate

- **get_power_curve**: Access best power efforts across different durations

### 📅 **Calendar & Event Management**
- **get_calendars**: List all calendars
- **get_events**: Retrieve planned races, workouts, and notes
- **get_event**: Get specific event details
- **create_event**: Add new calendar events (races, workouts, notes)
- **update_event**: Modify existing events
- **delete_event**: Remove calendar events
- **get_planned_workouts**: Filter for upcoming scheduled training sessions

### 📚 **Workout Library**
- **get_folders**: List all workout library folders
- **create_folder**: Create new workout folders
- **update_folder**: Modify folder metadata
- **delete_folder**: Remove folders
- **get_workouts**: List all workouts in library
- **get_workout**: Get specific workout details
- **create_workout**: Add new workouts to library
- **update_workout**: Modify existing workouts
- **delete_workout**: Remove workouts

### 📈 **Training Plans**
- **get_training_plans**: List all training plans
- **create_training_plan**: Create new training plans
- **update_training_plan**: Modify existing plans
- **delete_training_plan**: Remove training plans

### 👥 **Coaching Features**
- **get_coached_athletes**: List athletes you coach with current fitness metrics
- **get_wellness_summary**: Get wellness overview for coached athletes

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
- "Update my wellness data for today with weight 70kg and HRV 65ms"

### Training Analysis
- "Summarize my training volume for the past 30 days"
- "What were my hardest workouts this week?"
- "Compare my cycling vs running volume this month"
- "Show me my longest activities this year"
- "Export all my activities to CSV"
- "Rename my activity from yesterday to 'Easy Recovery Ride'"

### Fitness Trends
- "What's my current fitness (CTL) and form (TSB)?"
- "Am I building fitness too quickly? Check my ramp rate"
- "When was I at peak fitness in the last 90 days?"
- "Analyze my training load balance"

### Performance
- "What's my best 20-minute power in the last 90 days?"
- "Show me my power curve improvements over time"
- "What were my best efforts at different durations?"

### Calendar & Planning
- "What races do I have coming up?"
- "Show me my planned workouts for next week"
- "What's my training schedule looking like?"
- "Create a new workout event for tomorrow: 60min Z2 ride"
- "Add a race event for the marathon on April 15th"
- "Delete the workout planned for next Tuesday"

### Workout Library
- "List all my workout folders"
- "Show me all workouts in my library"
- "Create a new folder called 'VO2max Sessions'"
- "Add a new workout: 4x8min @ 110% FTP with 4min rest"
- "Get details for my Sweet Spot workout"

### Training Plans
- "Show me all my training plans"
- "Create a new 12-week marathon plan"

### Coaching (if you coach athletes)
- "List all the athletes I coach"
- "Show wellness summary for my coached athletes"
- "What's the fitness trend for athlete John Doe?"

### Combined Analysis
- "How has my fitness progressed leading up to my next race?"
- "Is my wellness data suggesting I need more recovery?"
- "Analyze whether my training load matches my upcoming events"
- "Compare my planned vs completed workouts this week"

## API Reference

### Athlete Profile

**get_athlete_profile**
- Parameters: None
- Returns: Athlete profile with FTP, weight, zones, and settings

---

### Wellness Data

**get_wellness_data**
- Parameters: `start_date` (optional), `end_date` (optional)
- Returns: Array of daily wellness entries with HRV, sleep, weight, etc.

**get_wellness_single**
- Parameters: `date` (required, YYYY-MM-DD)
- Returns: Wellness data for specific date

**update_wellness**
- Parameters: `date` (required), `data` (required, object with wellness fields)
- Returns: Updated wellness entry

**update_wellness_bulk**
- Parameters: `entries` (required, array of wellness objects with 'id' and fields)
- Returns: Updated wellness entries

---

### Activities

**get_activities**
- Parameters: `start_date` (optional), `end_date` (optional)
- Returns: Array of activities with metrics

**get_activities_csv**
- Parameters: None
- Returns: All activities in CSV format

**get_activity_details**
- Parameters: `activity_id` (required), `include_intervals` (optional, default: true)
- Returns: Detailed activity data including streams and intervals

**update_activity**
- Parameters: `activity_id` (required), `data` (required, object with fields to update)
- Returns: Updated activity

**delete_activity**
- Parameters: `activity_id` (required)
- Returns: Success confirmation

---

### Fitness Trends

**get_fitness_trends**
- Parameters: `start_date` (optional), `end_date` (optional)
- Returns: Array of fitness metrics (CTL, ATL, TSB, ramp rate) by date

---

### Calendar & Events

**get_calendars**
- Parameters: None
- Returns: List of all calendars

**get_events**
- Parameters: `start_date` (optional), `end_date` (optional), `calendar_id` (optional)
- Returns: Array of calendar events

**get_event**
- Parameters: `event_id` (required)
- Returns: Event details

**create_event**
- Parameters: `event_data` (required, object with start_date_local, category, name, etc.)
- Returns: Created event

**update_event**
- Parameters: `event_id` (required), `event_data` (required)
- Returns: Updated event

**delete_event**
- Parameters: `event_id` (required)
- Returns: Success confirmation

**get_planned_workouts**
- Parameters: `start_date` (optional), `end_date` (optional)
- Returns: Array of planned workout events (filters WORKOUT category)

---

### Workout Library

**get_folders**
- Parameters: None
- Returns: All workout folders and their contents

**create_folder**
- Parameters: `name` (required)
- Returns: Created folder

**update_folder**
- Parameters: `folder_id` (required), `data` (required)
- Returns: Updated folder

**delete_folder**
- Parameters: `folder_id` (required)
- Returns: Success confirmation

**get_workouts**
- Parameters: None
- Returns: All workouts in library

**get_workout**
- Parameters: `workout_id` (required)
- Returns: Workout details

**create_workout**
- Parameters: `workout_data` (required, object with name, description, folder_id, type)
- Returns: Created workout

**update_workout**
- Parameters: `workout_id` (required), `workout_data` (required)
- Returns: Updated workout

**delete_workout**
- Parameters: `workout_id` (required)
- Returns: Success confirmation

---

### Training Plans

**get_training_plans**
- Parameters: None
- Returns: All training plans

**create_training_plan**
- Parameters: `plan_data` (required)
- Returns: Created plan

**update_training_plan**
- Parameters: `plan_id` (required), `plan_data` (required)
- Returns: Updated plan

**delete_training_plan**
- Parameters: `plan_id` (required)
- Returns: Success confirmation

---

### Coaching

**get_coached_athletes**
- Parameters: None
- Returns: List of athletes you coach with current fitness metrics

**get_wellness_summary**
- Parameters: None
- Returns: Wellness overview for coached athletes

---

### Performance Analysis

**get_power_curve**
- Parameters: `start_date` (optional), `end_date` (optional)
- Returns: Power curve data for different durations

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
