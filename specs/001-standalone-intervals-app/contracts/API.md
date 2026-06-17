# Contracts: MCP Tools ↔ intervals.icu API

This document maps MCP tool names to the underlying intervals.icu endpoints and expected input schema.

- `get_athlete_profile` → `GET /athlete/{athlete_id}`
- `get_wellness_data` → `GET /athlete/{athlete_id}/wellness?oldest={start}&newest={end}`
- `get_activities` → `GET /athlete/{athlete_id}/activities?oldest={start}&newest={end}`
- `get_activity_details` → `GET /activity/{activity_id}`
- `update_wellness` → `PUT /athlete/{athlete_id}/wellness/{date}`
- `get_fitness_trends` → `GET /athlete/{athlete_id}/fitness-trends?oldest={start}&newest={end}`

Inputs: all dates in YYYY-MM-DD; IDs must be alphanumeric with allowed characters `-_:.`

Errors: HTTP 4xx/5xx propagated as structured error messages; tools return JSON text content.
