# Changelog

All notable changes to the intervals.icu MCP Server.

## [2.1.0] - 2025-03-24

### Security Hardening

Comprehensive security audit and fixes across the entire server.

### Fixed

- **Broken Basic Auth**: API key is now properly base64-encoded as `API_KEY:{key}` per HTTP Basic Auth spec
- **Credential leakage**: Removed debug logging that printed athlete ID and partial API key to stderr on every startup

### Added

- **`.gitignore`**: Prevents accidental commit of `.env` files, `claude_desktop_config.json`, and other secrets
- **Input validation**: All date parameters validated against `YYYY-MM-DD` format; all IDs validated against safe character pattern to prevent path traversal
- **Rate limiting**: Token-bucket rate limiter (10 req/sec) on all outbound API requests
- **HTTP client hardening**: 30s request timeout, 10s connect timeout, connection pool limits (20 max / 5 keepalive)
- **Typed error handling**: `ValueError`, `HTTPStatusError`, and `TimeoutException` caught separately with sanitized messages; unexpected errors logged internally and return a generic message

### Changed

- Replaced global mutable `http_client` with private `_http_client` accessed via `_get_http_client()` for safer initialization
- Error responses no longer leak internal paths, stack traces, or partial API response data

---

## [2.0.0] - 2025-03-22

### 🎉 Major Release - Comprehensive API Coverage

Extended the MCP server from 8 basic tools to **36 comprehensive API tools** covering all major intervals.icu features.

### Added

#### Wellness Management (NEW)
- `get_wellness_single` - Get wellness for specific date
- `update_wellness` - Update wellness for specific date  
- `update_wellness_bulk` - Batch update wellness entries

#### Activity Management (NEW)
- `get_activities_csv` - Export activities to CSV
- `update_activity` - Modify activity metadata
- `delete_activity` - Remove activities

#### Calendar & Events (6 new tools)
- `get_calendars` - List all calendars
- `get_event` - Get specific event details
- `create_event` - Create calendar events (races, workouts, notes)
- `update_event` - Modify events
- `delete_event` - Remove events

#### Workout Library (9 new tools)
- `get_folders` - List workout folders
- `create_folder` - Create folders
- `update_folder` - Modify folders
- `delete_folder` - Remove folders
- `get_workouts` - List library workouts
- `get_workout` - Get workout details
- `create_workout` - Add workouts
- `update_workout` - Modify workouts
- `delete_workout` - Remove workouts

#### Training Plans (4 new tools)
- `get_training_plans` - List plans
- `create_training_plan` - Create plans
- `update_training_plan` - Modify plans
- `delete_training_plan` - Remove plans

#### Coaching Features (2 new tools)
- `get_coached_athletes` - List coached athletes
- `get_wellness_summary` - Athlete wellness overview

### Enhanced

- `get_activity_details` - Now includes optional `include_intervals` parameter
- `make_request()` - Extended to support GET, POST, PUT, DELETE methods
- `make_request()` - Added support for activity-specific endpoints
- Error handling improved across all tools
- Better handling of CSV and non-JSON responses

### Changed

- Refactored request handling for better flexibility
- Updated documentation with comprehensive API coverage
- Enhanced README with detailed usage examples
- Expanded QUICKSTART guide with all new capabilities

### Technical Improvements

- Support for full CRUD operations (Create, Read, Update, Delete)
- Unified request handling for both athlete and activity endpoints
- Better JSON payload handling for POST/PUT requests
- Improved error messages and validation

## [1.0.0] - 2025-03-19

### Initial Release

Basic intervals.icu MCP server with 8 core tools:
- `get_athlete_profile`
- `get_wellness_data`
- `get_activities`
- `get_activity_details`
- `get_fitness_trends`
- `get_events`
- `get_planned_workouts`
- `get_power_curve`
