# intervals.icu Public API Reference

> **Complete list of available public API endpoints for intervals.icu**

Based on the official API documentation at https://intervals.icu/api-docs.html and forum discussions.

## Authentication

All API calls require authentication using one of two methods:

### 1. Personal API Key (Basic Auth)
For personal use or single-athlete applications:
- **Username**: `API_KEY`
- **Password**: Your generated API key from Settings → Developer Settings

```bash
curl -u API_KEY:your_api_key_here https://intervals.icu/api/v1/athlete/0/activities
```

### 2. OAuth 2.0 (Bearer Token)
For multi-user applications:
- See: https://forum.intervals.icu/t/intervals-icu-oauth-support/2759
- Required scopes: `ACTIVITY:READ`, `ACTIVITY:WRITE`, `WELLNESS:READ`, `WELLNESS:WRITE`

```bash
curl -H 'Authorization: Bearer your_access_token' https://intervals.icu/api/v1/athlete/0/activities
```

**Note**: Use athlete ID `0` to reference the authenticated athlete.

---

## API Endpoints

### 👤 Athlete Profile

#### Get Athlete Profile
```
GET /api/v1/athlete/{id}
```
Returns athlete information including FTP, weight, zones, and settings.

**Response includes:**
- Athlete name, ID, Strava ID
- Current FTP (cycling), threshold pace (running)
- Weight, height
- Power zones, heart rate zones
- Privacy settings

---

### 🏃 Activities

#### List Activities
```
GET /api/v1/athlete/{id}/activities
```
Get summary data for activities in a date range.

**Query Parameters:**
- `oldest` (required): Start date in YYYY-MM-DD format
- `newest` (required): End date in YYYY-MM-DD format

**Returns:** Array of activity summaries with:
- Activity ID, name, type
- Start date/time
- Duration (moving_time, elapsed_time)
- Distance, elevation gain
- Average/max power, heart rate, cadence
- Training stress score (icu_training_load)
- Intensity factor (icu_intensity)
- Normalized power (weighted_average_watts)

#### Get Activity Details
```
GET /api/v1/activity/{id}
```
Get detailed information for a specific activity.

**Query Parameters:**
- `intervals` (optional, boolean): Include interval data

**Returns:** Complete activity data including:
- All summary fields
- Streams data (power, HR, cadence, altitude, etc.)
- Detected intervals (`icu_intervals`)
- Laps
- Segment efforts
- Power curve data

#### Download Activity File
```
GET /api/v1/activity/{id}/file
```
Download the original activity file (FIT, GPX, or TCX) as gzip compressed.

#### Download intervals.icu Generated FIT File
```
GET /api/v1/activity/{id}/fit-file
```
Download FIT file with intervals.icu edits and interval laps.

#### Upload Activity
```
POST /api/v1/athlete/{id}/activities
```
Upload a new activity file (multipart/form-data).

**Form Parameters:**
- `file`: Activity file (FIT, GPX, TCX, or ZIP/GZ of same)
- `name` (optional): Activity name
- `description` (optional): Activity description
- `external_id` (optional): Your application's activity ID

**Example:**
```bash
curl -F file=@activity.fit \
  'https://intervals.icu/api/v1/athlete/0/activities?name=Morning+Ride' \
  -u API_KEY:your_key
```

#### Update Activity
```
PUT /api/v1/activity/{id}
```
Update activity metadata (name, description, type, etc.).

**Payload:** JSON object with fields to update

#### Delete Activity
```
DELETE /api/v1/activity/{id}
```
Delete an activity.

#### Get Activities as CSV
```
GET /api/v1/athlete/{id}/activities.csv
```
Export all activities to CSV format.

---

### 💪 Wellness Data

#### List Wellness Data
```
GET /api/v1/athlete/{id}/wellness
```
Get wellness metrics for a date range.

**Query Parameters:**
- `oldest` (required): Start date in YYYY-MM-DD format
- `newest` (required): End date in YYYY-MM-DD format

**Returns:** Array of daily wellness entries with:
- `id`: Date (YYYY-MM-DD)
- `restingHR`: Resting heart rate (bpm)
- `hrv`: Heart rate variability (ms)
- `weight`: Body weight (kg)
- `fatigue`, `motivation`, `soreness`, `stress`: Subjective ratings (1-5)
- `sleepQuality`: Sleep quality rating (1-5)
- `sleepSecs`: Sleep duration (seconds)
- `sleepScore`: Sleep score (0-100)
- `avgSleepingHR`: Average sleeping heart rate
- `menstrualPhase`: Menstrual cycle phase
- `menstruationSeverity`: Period severity
- `ctl`: Chronic Training Load (Fitness)
- `atl`: Acute Training Load (Fatigue)
- `tsb`: Training Stress Balance (Form)
- `rampRate`: Fitness ramp rate

#### Get Single Wellness Entry
```
GET /api/v1/athlete/{id}/wellness/{date}
```
Get wellness data for a specific date (YYYY-MM-DD).

#### Update Single Wellness Entry
```
PUT /api/v1/athlete/{id}/wellness/{date}
```
Update wellness data for a specific date.

**Payload:** JSON object with wellness fields

**Example:**
```json
{
  "weight": 70.5,
  "restingHR": 52,
  "hrv": 68,
  "sleepQuality": 4,
  "locked": true
}
```

**Note:** Set `"locked": true` to prevent external syncs (Oura, Garmin, etc.) from overwriting.

#### Bulk Update Wellness Data
```
PUT /api/v1/athlete/{id}/wellness-bulk
```
Update multiple wellness entries at once.

**Payload:** Array of wellness objects

**Example:**
```json
[
  {"id": "2024-03-20", "weight": 70.1, "restingHR": 51},
  {"id": "2024-03-21", "weight": 70.3, "restingHR": 53}
]
```

---

### 📅 Calendar & Events

#### List Calendars
```
GET /api/v1/athlete/{id}/calendars
```
Get all calendars for the athlete.

#### List Events
```
GET /api/v1/athlete/{id}/events
```
Get calendar events (races, workouts, notes) for a date range.

**Query Parameters:**
- `oldest` (required): Start date in YYYY-MM-DD format
- `newest` (required): End date in YYYY-MM-DD format
- `calendar_id` (optional): Filter by specific calendar

**Returns:** Array of events with:
- Event ID, name, description
- Start/end dates
- Category: `RACE`, `WORKOUT`, `NOTE`, etc.
- Type: Activity type (Ride, Run, etc.)
- Planned training load (`icu_training_load`)
- Workout file reference
- Fitness projections (ctl, atl, tsb at that date)

#### Get Event
```
GET /api/v1/athlete/{id}/events/{eventId}
```
Get details for a specific event.

#### Create Event
```
POST /api/v1/athlete/{id}/events
```
Create a new calendar event.

**Payload:**
```json
{
  "start_date_local": "2025-04-01T00:00:00",
  "category": "WORKOUT",
  "name": "Threshold Intervals",
  "description": "4x8min @ FTP",
  "type": "Ride",
  "icu_training_load": 120,
  "moving_time": 7200
}
```

**Or create from workout file:**
```json
{
  "category": "WORKOUT",
  "start_date_local": "2025-04-01T00:00:00",
  "type": "Ride",
  "filename": "workout.zwo",
  "file_contents": "<?xml version=\"1.0\"...>"
}
```

#### Update Event
```
PUT /api/v1/athlete/{id}/events/{eventId}
```
Update an existing event.

#### Delete Event
```
DELETE /api/v1/athlete/{id}/events/{eventId}
```
Delete a calendar event.

#### Download Planned Workout
```
GET /api/v1/athlete/{id}/events/{eventId}/download{.ext}
```
Download planned workout in specific format.

**Extensions:** `.zwo` (Zwift), `.mrc` (TrainerRoad), `.erg` (Computrainer)

---

### 📚 Workout Library

#### List Folders
```
GET /api/v1/athlete/{id}/folders
```
Get all workout folders and their contents.

#### Create Folder
```
POST /api/v1/athlete/{id}/folders
```
Create a new workout folder.

#### Update Folder
```
PUT /api/v1/athlete/{id}/folders/{folderId}
```
Update folder metadata.

#### Delete Folder
```
DELETE /api/v1/athlete/{id}/folders/{folderId}
```
Delete a folder (and optionally its workouts).

#### Get Folder Sharing
```
GET /api/v1/athlete/{id}/folders/{folderId}/shared-with
```
See who has access to this folder.

#### Update Folder Sharing
```
PUT /api/v1/athlete/{id}/folders/{folderId}/shared-with
```
Share folder with other athletes or coaches.

#### List Workouts
```
GET /api/v1/athlete/{id}/workouts
```
Get all workouts in the library (excluding shared by others).

#### Get Workout
```
GET /api/v1/athlete/{id}/workouts/{workoutId}
```
Get a specific workout.

#### Create Workout
```
POST /api/v1/athlete/{id}/workouts
```
Create a new workout in the library.

**Payload:**
```json
{
  "folder_id": 123,
  "name": "VO2max Intervals",
  "description": "5x5min @ 120% FTP\n\n- 20m warmup\n- 5x5m 120% / 5m 50%\n- 10m cooldown",
  "type": "Ride"
}
```

#### Update Workout
```
PUT /api/v1/athlete/{id}/workouts/{workoutId}
```
Update an existing workout.

#### Delete Workout
```
DELETE /api/v1/athlete/{id}/workouts/{workoutId}
```
Delete a workout from the library.

#### Download Workout
```
POST /api/v1/download-workout{.ext}
```
Download a workout in specific format.

**Extensions:** `.zwo`, `.mrc`, `.erg`

---

### 📊 Training Plans

#### List Training Plans
```
GET /api/v1/athlete/{id}/plans
```
Get all training plans.

#### Create Training Plan
```
POST /api/v1/athlete/{id}/plans
```
Create a new training plan.

#### Update Training Plan
```
PUT /api/v1/athlete/{id}/plans/{planId}
```
Update a training plan.

#### Delete Training Plan
```
DELETE /api/v1/athlete/{id}/plans/{planId}
```
Delete a training plan.

---

### 👥 Coaching & Athletes

#### List Coached Athletes
```
GET /api/v1/athlete/{id}/athlete-summary
```
Get list of athletes you coach.

**Returns:** Array of athlete summaries with current fitness metrics.

#### Get Athlete Wellness Summary
```
GET /api/v1/athlete/{id}/wellness-summary
```
Get wellness overview for coached athletes.

---

### 📈 Power & Performance Curves

Power curve data is included in activity details when available:
- `power_curve`: Best power efforts at different durations
- `icu_power_curve`: intervals.icu calculated power curve

Access via:
```
GET /api/v1/activity/{id}
```

Look for `power_curve` or `icu_power_curve` fields in the response.

---

### 🔗 Webhooks

Configure webhooks in your OAuth app settings to receive real-time notifications.

**Available Webhook Events:**
- `ACTIVITY_UPLOADED`: New activity added
- `ACTIVITY_UPDATED`: Activity modified
- `ACTIVITY_ANALYZED`: Activity analysis complete (60s delay)
- `ACTIVITY_DELETED`: Activity removed
- `CALENDAR_UPDATED`: Calendar events changed
- `CALENDAR_EVENT_DELETED`: Event removed (legacy)
- `WELLNESS_UPDATED`: Wellness data changed
- `SPORT_SETTINGS_UPDATED`: FTP, zones, or settings changed

**Webhook Payload:**
```json
{
  "secret": "your_webhook_secret",
  "events": [
    {
      "athlete_id": "i12345",
      "type": "ACTIVITY_UPLOADED",
      "timestamp": "2025-03-22T10:00:00.000+00:00",
      "activity": { /* activity data */ }
    }
  ]
}
```

**Important:** Respond with HTTP 2xx status to acknowledge receipt.

---

## Common Query Patterns

### Get Last 30 Days of Activities
```bash
curl -u API_KEY:your_key \
  'https://intervals.icu/api/v1/athlete/0/activities?oldest=2025-02-20&newest=2025-03-22'
```

### Get Current Fitness Metrics (CTL/ATL/TSB)
```bash
curl -u API_KEY:your_key \
  'https://intervals.icu/api/v1/athlete/0/wellness?oldest=2025-03-22&newest=2025-03-22'
```

### Upload Wellness Data
```bash
curl -X PUT -u API_KEY:your_key \
  -H 'Content-Type: application/json' \
  -d '[{"id":"2025-03-22","weight":70.5,"hrv":65}]' \
  'https://intervals.icu/api/v1/athlete/0/wellness-bulk'
```

### Create Planned Workout from Description
```bash
curl -X POST -u API_KEY:your_key \
  -H 'Content-Type: application/json' \
  -d '{
    "start_date_local":"2025-03-25T00:00:00",
    "category":"WORKOUT",
    "type":"Ride",
    "name":"Sweet Spot",
    "description":"- 15m warmup\n- 3x10m 88-92%\n- 10m cooldown"
  }' \
  'https://intervals.icu/api/v1/athlete/0/events'
```

---

## Wellness Fields Reference

All wellness metrics (units are metric):

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Date (YYYY-MM-DD) |
| `weight` | float | Body weight (kg) |
| `restingHR` | int | Resting heart rate (bpm) |
| `hrv` | int | Heart rate variability (ms) |
| `avgSleepingHR` | int | Average sleeping heart rate (bpm) |
| `sleepSecs` | int | Sleep duration (seconds) |
| `sleepScore` | int | Sleep quality score (0-100) |
| `sleepQuality` | int | Subjective sleep quality (1-5) |
| `soreness` | int | Muscle soreness (1-5) |
| `fatigue` | int | Fatigue level (1-5) |
| `stress` | int | Stress level (1-5) |
| `motivation` | int | Motivation (1-5) |
| `spO2` | float | Blood oxygen saturation (%) |
| `systolic` | int | Blood pressure systolic (mmHg) |
| `diastolic` | int | Blood pressure diastolic (mmHg) |
| `menstrualPhase` | string | Cycle phase |
| `menstruationSeverity` | int | Period severity (1-5) |
| `hydration` | float | Hydration level |
| `ctl` | float | Chronic Training Load (Fitness) |
| `atl` | float | Acute Training Load (Fatigue) |
| `tsb` | float | Training Stress Balance (Form) |
| `rampRate` | float | CTL ramp rate |
| `locked` | boolean | Prevent external sync overwrites |

---

## Activity Fields Reference

Key activity summary fields:

| Field | Description |
|-------|-------------|
| `id` | Activity ID |
| `start_date_local` | Start time (local timezone) |
| `type` | Activity type (Ride, Run, Swim, etc.) |
| `name` | Activity name |
| `description` | Activity description |
| `moving_time` | Moving time (seconds) |
| `elapsed_time` | Total elapsed time (seconds) |
| `distance` | Distance (meters) |
| `total_elevation_gain` | Elevation gain (meters) |
| `average_watts` | Average power (watts) |
| `weighted_average_watts` | Normalized power (watts) |
| `average_heartrate` | Average heart rate (bpm) |
| `average_cadence` | Average cadence (rpm) |
| `average_speed` | Average speed (m/s) |
| `icu_training_load` | Training stress score |
| `icu_intensity` | Intensity factor (%) |
| `icu_power_hr_z1`-`z7` | Time in zones (seconds) |

---

## Rate Limits & Best Practices

- **Rate Limiting**: Be respectful with API calls; no official rate limit published
- **Caching**: Cache data locally when possible
- **Bulk Operations**: Use bulk endpoints (`wellness-bulk`) when updating multiple records
- **Webhooks**: Prefer webhooks over polling for real-time updates
- **Date Ranges**: Keep date ranges reasonable (avoid requesting years of data at once)
- **Athlete ID 0**: Always use `0` to reference the authenticated athlete

---

## Additional Resources

- **Official API Docs (RapiDoc)**: https://intervals.icu/api-docs.html
- **Swagger UI**: https://intervals.icu/api/v1/docs/swagger-ui/index.html
- **API Integration Cookbook**: https://forum.intervals.icu/t/intervals-icu-api-integration-cookbook/80090
- **OAuth Guide**: https://forum.intervals.icu/t/intervals-icu-oauth-support/2759
- **API Terms & Conditions**: https://forum.intervals.icu/t/intervals-icu-api-terms-and-conditions/114087
- **Forum (API Questions)**: https://forum.intervals.icu/c/guide/11

---

## Python Libraries

- **py-intervalsicu**: https://py-intervalsicu.readthedocs.io/
  ```bash
  pip install intervalsicu
  ```

---

## Notes

- All timestamps are ISO-8601 format
- Dates for wellness/events must use local dates (no timezone): `YYYY-MM-DDT00:00:00`
- All distance units are meters
- All duration units are seconds
- All weight units are kilograms
- Power zones and training metrics follow intervals.icu's calculation methodology

---

**Last Updated**: March 2025  
**API Version**: v1
