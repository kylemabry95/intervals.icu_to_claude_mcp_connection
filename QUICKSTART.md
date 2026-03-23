# intervals.icu MCP Server - Quick Start Guide

🎉 Version 2.0.1 - Extended Edition with Authentication Fix
This MCP server provides comprehensive access to intervals.icu with 36 API tools covering:

✅ Full CRUD operations (Create, Read, Update, Delete)
✅ Wellness tracking and bulk updates
✅ Calendar and event management
✅ Complete workout library control
✅ Training plan management
✅ Coaching features
✅ Activity management and CSV export
✅ Fitness trend analysis and power curves

⚠️ New in v2.0.1: Critical authentication fix for 403 errors + required INTERVALS_API_BASE_URL environment variable!
New in v2.0: Write capabilities, workout library, training plans, coaching tools, and bulk operations!

⚠️ IMPORTANT: Authentication Requirements (v2.0.1)
Version 2.0.1 includes a critical authentication fix. If you're experiencing 403 Forbidden errors, you MUST:

Use the latest server.py (includes proper Basic Auth with base64 encoding)
Add all THREE required environment variables (the third one is new!)
Use full Python path (e.g., /usr/local/bin/python3 not just python)
Include the i prefix in athlete ID (e.g., i230309 not 230309)

Required Configuration (Updated for v2.0.1)
json{
  "mcpServers": {
    "intervals-icu": {
      "command": "/usr/local/bin/python3",
      "args": ["/FULL/PATH/TO/intervals-icu-mcp/server.py"],
      "env": {
        "INTERVALS_API_KEY": "YOUR_API_KEY",
        "INTERVALS_ATHLETE_ID": "YOUR_ATHLETE_ID",
        "INTERVALS_API_BASE_URL": "https://intervals.icu/api/v1"
      }
    }
  }
}
Critical changes:

✅ INTERVALS_API_BASE_URL is now REQUIRED (new in v2.0.1)
✅ Full Python path required (e.g., /usr/local/bin/python3)
✅ Athlete ID must include i prefix (e.g., i230309)

## 🎉 Version 2.0 - Extended Edition

This MCP server provides **comprehensive access to intervals.icu** with 36 API tools covering:
- ✅ Full CRUD operations (Create, Read, Update, Delete)
- ✅ Wellness tracking and bulk updates
- ✅ Calendar and event management
- ✅ Complete workout library control
- ✅ Training plan management
- ✅ Coaching features
- ✅ Activity management and CSV export
- ✅ Fitness trend analysis and power curves

**New in v2.0:** Write capabilities, workout library, training plans, coaching tools, and bulk operations!

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

**Total: 36 API endpoints covering all major intervals.icu features**

### Core Data
1. **get_athlete_profile** - Profile, FTP, zones
2. **get_wellness_data** - HRV, sleep, resting HR, weight (date range)
3. **get_wellness_single** - Wellness for specific date
4. **update_wellness** - Update wellness for specific date
5. **update_wellness_bulk** - Batch wellness updates
6. **get_activities** - Training workouts and metrics
7. **get_activities_csv** - Export activities to CSV
8. **get_activity_details** - Detailed activity with streams/intervals
9. **update_activity** - Modify activity metadata
10. **delete_activity** - Remove activity
11. **get_fitness_trends** - CTL, ATL, TSB analysis

### Calendar & Planning
12. **get_calendars** - List all calendars
13. **get_events** - Planned events (races, workouts, notes)
14. **get_event** - Specific event details
15. **create_event** - Add new event
16. **update_event** - Modify event
17. **delete_event** - Remove event
18. **get_planned_workouts** - Upcoming training sessions

### Workout Library
19. **get_folders** - List workout folders
20. **create_folder** - Create folder
21. **update_folder** - Modify folder
22. **delete_folder** - Remove folder
23. **get_workouts** - List all library workouts
24. **get_workout** - Specific workout details
25. **create_workout** - Add workout to library
26. **update_workout** - Modify workout
27. **delete_workout** - Remove workout

### Training Plans
28. **get_training_plans** - List plans
29. **create_training_plan** - Create plan
30. **update_training_plan** - Modify plan
31. **delete_training_plan** - Remove plan

### Coaching
32. **get_coached_athletes** - Athletes you coach
33. **get_wellness_summary** - Athlete wellness overview

### Performance
34. **get_power_curve** - Best power efforts

## Example Questions to Ask Claude

### Data Analysis
- "What's my fitness trend over the last month?"
- "Show me my HRV and sleep quality this week"
- "What were my hardest workouts in the past 2 weeks?"
- "Am I building fitness too quickly based on my CTL ramp rate?"
- "What's my current form (TSB)?"
- "Export all my activities to CSV"

### Calendar Management
- "What races do I have coming up?"
- "Show me my planned workouts for next week"
- "Create a workout event for tomorrow: 90min endurance ride"
- "Add my marathon race on April 15th to the calendar"
- "Update today's planned workout to be a rest day"
- "Delete the workout scheduled for next Tuesday"

### Wellness Updates
- "Update my wellness data for today: weight 70kg, HRV 65ms, sleep quality 4"
- "Log my resting heart rate as 52 for today"
- "Bulk update my weight for the past week"

### Workout Library
- "Show me all my workout folders"
- "Create a new folder called 'Race Prep Workouts'"
- "List all workouts in my library"
- "Add a new Sweet Spot workout: 3x20min @ 88-92% FTP"
- "Get details for my VO2max interval workout"

### Activity Management
- "Rename yesterday's activity to 'Easy Recovery Spin'"
- "Update the description of my last run"
- "Delete that accidental duplicate activity"

### Training Plans
- "Show me all my training plans"
- "Create a new 16-week marathon training plan"

### Coaching (if applicable)
- "List all the athletes I coach"
- "Show wellness summary for my coached athletes"
- "What's Sarah's current fitness and form?"

### Performance Analysis
- "Analyze my training load and recovery balance"
- "What's my best 5-minute power from the last 90 days?"
- "Show me power curve improvements over time"

## Common Workflows

### Daily Training Routine
1. **Morning**: "Update my wellness: weight 70kg, HRV 65, sleep quality 4, resting HR 52"
2. **After workout**: "Rename today's activity to 'Tempo Intervals' and add description 'Felt strong'"
3. **Evening**: "What's my current form (TSB)? Am I ready for tomorrow's hard workout?"

### Race Preparation
1. "Create a race event: Half Marathon on April 15th"
2. "What's my fitness trend leading up to April 15th?"
3. "Show planned workouts for the 2 weeks before my race"
4. "Am I tapering properly based on my CTL?"

### Weekly Planning
1. "Show me my planned workouts for next week"
2. "Create a workout event for Tuesday: 5x5min @ VO2max"
3. "What's my training load for this week vs last week?"
4. "Export my activities to CSV for my coach"

### Workout Library Organization
1. "Create folders: 'Base Training', 'Race Prep', 'Recovery'"
2. "Add my threshold workout to the Race Prep folder"
3. "Show all workouts in my Base Training folder"
4. "Copy this workout to my calendar for next Thursday"

### Coaching Workflow (for coaches)
1. "List all athletes I coach"
2. "Show wellness summary for my team"
3. "What's John's current fitness and form?"
4. "Create a training plan for Sarah's upcoming race"

### Data Analysis
1. "Export all my activities to CSV"
2. "Show my power curve for the last 90 days"
3. "What were my top 5 workouts by training load this month?"
4. "Compare my HRV trend with my training load"

## Quick Reference - Tool Categories

### Read-Only (View Data)
- Profile, wellness, activities, events, workouts, plans, coached athletes
- Fitness trends, power curves, wellness summaries
- Perfect for analysis and review

### Write Operations (Modify Data)
- **Update**: Wellness, activities, events, workouts, folders, plans
- **Create**: Events, workouts, folders, plans
- **Delete**: Activities, events, workouts, folders, plans
- Use with care - changes are immediate!

### Bulk Operations
- `update_wellness_bulk` - Update multiple wellness entries at once
- `get_activities_csv` - Export all activities for external analysis

### Date Ranges
Most tools support optional date filtering:
- Default ranges vary by tool (7-90 days)
- Format: YYYY-MM-DD
- Always in local time zone

## Troubleshooting

### Server not showing up in Claude Desktop

**Check config file location:**
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

**Verify JSON syntax:**
```bash
# macOS/Linux - validate JSON
python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Windows
python -m json.tool %APPDATA%/Claude/claude_desktop_config.json
```

**Common issues:**
- Missing comma between server entries
- Incorrect quote marks (use straight quotes, not curly)
- Wrong path separators (use forward slashes or escaped backslashes)
- Relative path instead of absolute path

**Test the server manually:**
```bash
export INTERVALS_API_KEY="your_key"
export INTERVALS_ATHLETE_ID="your_id"
python /full/path/to/server.py
```

### Authentication errors

**Error: "Missing credentials"**
- Check environment variables are set correctly in config
- Ensure no extra spaces in API key or athlete ID
- Verify key hasn't been revoked in intervals.icu settings

**Error: "401 Unauthorized" or "403 Forbidden"**
- Regenerate API key in intervals.icu settings
- Check athlete ID matches your account
- Verify intervals.icu subscription is active

**Finding your athlete ID:**
1. Log into intervals.icu
2. Look at the URL: `intervals.icu/athlete/i123456`
3. Your athlete ID is the part after `/athlete/` (e.g., `i123456`)

### No data returned

**"Empty array" or "null" responses:**
- Check date format is YYYY-MM-DD (not MM/DD/YYYY)
- Verify you have data in intervals.icu for that date range
- Try a broader date range
- Check filters aren't excluding all results

**CSV export shows "content" field:**
- This is expected - the actual CSV data is in the `content` field
- Ask Claude to "extract the CSV data" or "format the CSV"

### Write operations not working

**Updates not persisting:**
- Check if wellness entries are "locked" (external sync enabled)
- Set `"locked": true` in update to prevent overwrites
- Verify data format matches API requirements

**Can't delete items:**
- Ensure you own the item (not shared by others)
- Check item ID is correct
- Some items can't be deleted if linked to activities

**Events/workouts not appearing:**
- Wait a few seconds and refresh
- Check correct calendar is being viewed
- Verify event category (WORKOUT vs RACE vs NOTE)

### Performance issues

**Slow responses:**
- Reduce date ranges for large queries
- Use specific date filters instead of "all time"
- Consider splitting bulk operations

**Rate limiting:**
- Space out rapid consecutive requests
- Use bulk operations where available
- Cache data locally when possible

### Getting help

**Check logs:**
```bash
# View Claude Desktop logs (macOS)
tail -f ~/Library/Logs/Claude/mcp*.log

# View Claude Desktop logs (Windows)
type %LOCALAPPDATA%\Claude\Logs\mcp*.log
```

**Verify MCP server is running:**
- Look for "intervals-icu" in Claude's available tools
- Check for error messages in Claude Desktop
- Try other MCP servers to rule out general MCP issues

**Still stuck?**
1. Read the full README.md for detailed documentation
2. Check API_REFERENCE.md for endpoint specifications
3. Run test_server.py to validate your setup
4. Review CHANGELOG.md for known issues

## Security Note

Your API credentials are stored locally in the Claude Desktop config file. No data is sent to third parties - all requests go directly from your machine to intervals.icu.

**Best practices:**
- Never share your API key or config file
- Use file permissions to protect config (chmod 600 on Unix)
- Regenerate API key if you suspect compromise
- Review API access regularly in intervals.icu settings

**What Claude can access:**
- Only your personal intervals.icu data
- Athletes you coach (if you're a coach)
- No access to other users' private data
- No access to your intervals.icu password

## Tips & Best Practices

### For Daily Use
- Update wellness data consistently for better trends
- Use descriptive activity names for easier searching
- Tag important workouts/races in calendar
- Review fitness trends weekly

### For Coaches
- Check coached athletes' wellness daily
- Maintain organized workout library
- Use training plans for structured periodization
- Export CSV data for deeper analysis

### For Data Analysis
- Export to CSV regularly for backup
- Use date ranges to focus analysis
- Compare fitness trends with race results
- Track power curve improvements over time

### For Workflow Efficiency
- Use bulk wellness updates for backdating
- Create workout templates in library
- Organize workouts by training phase
- Set up recurring calendar events

## Next Steps

1. ✅ **Start simple**: Get your athlete profile and recent activities
2. 📊 **Explore data**: Review wellness and fitness trends
3. 📅 **Plan ahead**: Add upcoming races and key workouts
4. 📚 **Organize**: Build your workout library
5. 🚀 **Advanced**: Use bulk operations and CSV exports

**Pro tip**: Ask Claude to "help me get started with intervals.icu MCP server" for a personalized walkthrough!
