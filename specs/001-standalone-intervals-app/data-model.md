# data-model.md

Entities

- UserAccount
  - id: UUID
  - intervals_api_key: stored in OS secure storage
  - athlete_id: string
  - preferences: JSON

- AthleteProfile
  - athlete_id: string
  - name, weight, ftp, zones
  - metadata: JSON

- TrainingSession
  - session_id: string
  - athlete_id: string
  - date, duration, type, metrics (power, hr, pace)
  - source (device, imported)

- Conversation
  - conversation_id: UUID
  - messages: array of {role, text, timestamp, tool_calls}
  - context_summary: short cached summary for cost optimization

Validation rules and relationships

- `UserAccount` owns `Conversation` and `AthleteProfile` references
- TrainingSession references `athlete_id`, must validate date format YYYY-MM-DD
