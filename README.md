# intervals.icu MCP Server

[![Version](https://img.shields.io/badge/version-2.0.1-blue.svg)](https://github.com/kylemabry95/intervals.icu_to_claude_mcp_connection)
[![Python](https://img.shields.io/badge/python-3.10+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![API Coverage](https://img.shields.io/badge/API%20coverage-~95%25-brightgreen.svg)](API_REFERENCE.md)

> 🏃 **Transform Claude Desktop into a comprehensive intervals.icu training platform interface**

A Model Context Protocol (MCP) server that gives Claude Desktop **complete access** to [intervals.icu](https://intervals.icu) training data APIs. Manage every aspect of your training through natural conversation — from logging wellness data to organizing workout libraries to coaching athletes.

---

## 📖 Documentation

| File | Purpose |
|------|---------|
| **README.md** *(this file)* | Feature overview, installation, and usage examples |
| [QUICKSTART.md](QUICKSTART.md) | Fast setup guide with troubleshooting tips |
| [API_REFERENCE.md](API_REFERENCE.md) | Complete endpoint specifications and parameters |
| [CHANGELOG.md](CHANGELOG.md) | Version history and release notes |
| [EXTENSION_SUMMARY.md](EXTENSION_SUMMARY.md) | Technical architecture and implementation details |
| [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) | Project metrics, deliverables, and completion status |

---

## 🎉 What's New in v2.0.1

**Critical authentication fix + 4.5× more capabilities than v1.0.**

- ✅ Fixed 403 Forbidden errors (proper Basic Auth with base64 encoding)
- ✅ Added required `INTERVALS_API_BASE_URL` environment variable
- ✅ **36 API tools** (up from 8 in v1.0)
- ✅ Full CRUD operations on all major entities
- ✅ Workout Library management (9 tools)
- ✅ Training Plans support (4 tools)
- ✅ Coaching features (2 tools)
- ✅ Bulk operations and CSV export
- ✅ Complete documentation suite (6 guides)

### Version Comparison

| Feature | v1.0 | v2.0.1 |
|---------|------|--------|
| Total Tools | 8 | 36 |
| Read Operations | ✅ | ✅ |
| Write Operations | ❌ | ✅ |
| Update Operations | ❌ | ✅ |
| Delete Operations | ❌ | ✅ |
| Bulk Operations | ❌ | ✅ |
| CSV Export | ❌ | ✅ |
| Workout Library | ❌ | ✅ (9 tools) |
| Training Plans | ❌ | ✅ (4 tools) |
| Coaching Features | ❌ | ✅ (2 tools) |
| Calendar Management | Read-only | Full CRUD |
| Wellness Management | Read-only | Full CRUD + Bulk |
| Activity Management | Read-only | Full CRUD + CSV |
| API Coverage | ~25% | ~95% |
| Lines of Code | 361 | 1,016 |

---

## ✨ Features

### 👤 Athlete Profile
- **`get_athlete_profile`** — Retrieve FTP, weight, training zones, and account settings

### 💪 Wellness & Recovery
- **`get_wellness_data`** — Daily wellness metrics for a date range
- **`get_wellness_single`** — Wellness data for a specific date
- **`update_wellness`** — Update a single wellness entry
- **`update_wellness_bulk`** — Batch-update multiple wellness entries

Metrics covered: sleep quality and duration, HRV, resting heart rate, weight, body composition, subjective scores (fatigue, soreness, stress, motivation), readiness, CTL/ATL/TSB.

### 🚴 Training Activities
- **`get_activities`** — Workouts for a date range with key metrics
- **`get_activities_csv`** — Export all activities to CSV
- **`get_activity_details`** — Granular data including power/HR streams and detected intervals
- **`update_activity`** — Modify name, description, or type
- **`delete_activity`** — Remove an activity

### 📊 Fitness Analytics
- **`get_fitness_trends`** — CTL (Fitness), ATL (Fatigue), TSB (Form), and ramp rate
- **`get_power_curve`** — Best power efforts across different durations

### 📅 Calendar & Event Management
- **`get_calendars`** — List all calendars
- **`get_events`** — Planned races, workouts, and notes
- **`get_event`** — Details for a specific event
- **`create_event`** — Add races, workouts, or notes
- **`update_event`** — Modify an existing event
- **`delete_event`** — Remove a calendar event
- **`get_planned_workouts`** — Filter for upcoming scheduled training sessions

### 📚 Workout Library
- **`get_folders`** / **`create_folder`** / **`update_folder`** / **`delete_folder`**
- **`get_workouts`** / **`get_workout`** / **`create_workout`** / **`update_workout`** / **`delete_workout`**

### 📈 Training Plans
- **`get_training_plans`** / **`create_training_plan`** / **`update_training_plan`** / **`delete_training_plan`**

### 👥 Coaching
- **`get_coached_athletes`** — Athletes you coach with current fitness metrics
- **`get_wellness_summary`** — Wellness overview for coached athletes

---

## ⚡ Quick Stats

| Metric | Value |
|--------|-------|
| Total API Tools | 36 |
| API Coverage | ~95% of public intervals.icu APIs |
| CRUD Support | Full (Create, Read, Update, Delete) |
| Lines of Code | 1,016 |
| Documentation Files | 6 |
| Supported HTTP Methods | GET, POST, PUT, DELETE |

---

## 🚀 Installation

> 💡 For a faster path, see [QUICKSTART.md](QUICKSTART.md). It includes platform-specific notes and a comprehensive troubleshooting section.

### Prerequisites
- Python 3.10 or higher
- [Claude Desktop](https://claude.ai/download)
- An active [intervals.icu](https://intervals.icu) account with API access

### 1. Get Your API Credentials

1. Log in to [intervals.icu](https://intervals.icu)
2. Navigate to **Settings → Developer Settings** (near the bottom)
3. Click **Generate API Key**
4. Note your athlete ID from the URL: `intervals.icu/athlete/{ATHLETE_ID}`  
   ⚠️ The athlete ID must include the `i` prefix (e.g., `i230309`)

### 2. Install Python Dependencies

```bash
cd intervals-icu-mcp
pip install -r requirements.txt
```

Or install in development mode:

```bash
pip install -e .
```

### 3. Test the Server (Recommended)

```bash
export INTERVALS_API_KEY="your_api_key"
export INTERVALS_ATHLETE_ID="your_athlete_id"   # e.g., i230309
export INTERVALS_API_BASE_URL="https://intervals.icu/api/v1"
python test_server.py
```

### 4. Configure Claude Desktop

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "intervals-icu": {
      "command": "/usr/local/bin/python3",
      "args": ["/absolute/path/to/intervals-icu-mcp/server.py"],
      "env": {
        "INTERVALS_API_KEY": "your_api_key_here",
        "INTERVALS_ATHLETE_ID": "your_athlete_id_here",
        "INTERVALS_API_BASE_URL": "https://intervals.icu/api/v1"
      }
    }
  }
}
```

> **Important:** Use the full path to Python (e.g., `/usr/local/bin/python3`, not just `python`). On macOS, run `which python3` to find the correct path.

### 5. Restart Claude Desktop

Close and reopen Claude Desktop to load the MCP server.

---

## 💬 Usage Examples

### Wellness & Recovery
- "What's my HRV trend over the past 2 weeks?"
- "Update my wellness for today: weight 70 kg, HRV 65 ms, sleep quality 4"
- "Am I getting enough recovery based on my recent wellness data?"

### Training Analysis
- "Summarize my training volume for the past 30 days"
- "What were my hardest workouts this week?"
- "Export all my activities to CSV"

### Fitness Trends
- "What's my current fitness (CTL) and form (TSB)?"
- "Am I building fitness too quickly? Check my ramp rate"
- "When was I at peak fitness in the last 90 days?"

### Calendar & Planning
- "What races do I have coming up?"
- "Create a workout event for tomorrow: 60 min Z2 ride"
- "Delete the workout planned for next Tuesday"

### Workout Library
- "List all my workout folders"
- "Add a new workout: 4×8 min @ 110% FTP with 4 min rest"
- "Create a folder called 'VO2max Sessions'"

### Coaching
- "List all the athletes I coach"
- "What's the fitness trend for athlete John Doe?"

---

## 🔧 Troubleshooting

### Server not appearing in Claude Desktop
1. Verify the config file path is correct for your OS
2. Validate JSON syntax: `python -m json.tool ~/Library/Application\ Support/Claude/claude_desktop_config.json`
3. Confirm the absolute path to `server.py` is correct
4. Check that all three environment variables are present

### 401 / 403 Authentication Errors
- Confirm you're using v2.0.1 of `server.py` (includes the authentication fix)
- Ensure `INTERVALS_API_BASE_URL` is set
- Verify the athlete ID includes the `i` prefix
- Regenerate your API key in intervals.icu settings if needed

### No Data Returned
- Use `YYYY-MM-DD` date format
- Try a broader date range
- Confirm you have data in intervals.icu for the requested period

For a full troubleshooting guide, see [QUICKSTART.md](QUICKSTART.md).

---

## 🔒 Privacy & Security

- API credentials are stored locally in the Claude Desktop config file
- All requests go directly from your machine to intervals.icu — no third parties
- Claude processes responses locally on your machine

**Best practices:**
- Never share your API key or config file
- Protect the config file with restrictive permissions: `chmod 600 claude_desktop_config.json`
- Regenerate your API key if you suspect compromise

---

## 🤝 Contributing

~95% of the public intervals.icu API is already covered. Potential areas for future contribution include FIT/GPX/TCX file uploads, workout file downloads (`.zwo`, `.mrc`, `.erg`), real-time activity streams, advanced analytics, and webhook integration.

When contributing:
- Match existing code style and naming conventions
- Add docstrings to all new tools
- Update relevant documentation (README, QUICKSTART, API_REFERENCE)
- Add test cases to `test_server.py`

---

## 📜 License

MIT License — free to use and modify for your own training analysis needs.

---

## 🙏 Credits

Built for the [Model Context Protocol](https://modelcontextprotocol.io/) to integrate intervals.icu with Claude Desktop.

- [intervals.icu](https://intervals.icu) — comprehensive training analytics platform
- [Anthropic](https://www.anthropic.com) — Claude and the MCP framework
- The intervals.icu community — API feedback and feature requests

---

## 💬 Support

- 📖 **Setup**: [QUICKSTART.md](QUICKSTART.md)
- 📚 **API Reference**: [API_REFERENCE.md](API_REFERENCE.md)
- 📋 **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/kylemabry95/intervals.icu_to_claude_mcp_connection/issues)

---

*Made with ❤️ for athletes training smarter, not just harder*

⭐ Star this repo if it's useful for your training!

**v2.0.1** | [Changelog](CHANGELOG.md) | [Quick Start](QUICKSTART.md) | [API Reference](API_REFERENCE.md)
