# Data Model: UI Preview Before Download

## Entities

### 1. PreviewSession

Represents a single anonymous visitor interaction window.

Fields:
- session_id (string, UUID, required)
- started_at (datetime, required)
- last_interaction_at (datetime, required)
- device_type (enum: desktop, tablet, mobile, required)
- browser_family (string, required)
- locale (string, optional)
- completed_first_query (boolean, default false)
- clicked_download_cta (boolean, default false)

Validation:
- session_id must be unique per session.
- device_type must be one of allowed enum values.
- timestamps must be non-decreasing.

### 2. DemoScenario

Represents a predefined interactive use-case in the preview.

Fields:
- scenario_id (string, required)
- title (string, required)
- category (enum: chat, auth, settings, help, required)
- prompt_seed (string, optional)
- expected_outcome_summary (string, required)
- enabled (boolean, default true)
- priority (enum: p1, p2, p3, required)

Validation:
- scenario_id must be globally unique.
- category controls which UI modules can reference this scenario.
- disabled scenarios must not be visible in navigation.

### 3. ChatResponseTemplate

Represents deterministic response output for preview prompts.

Fields:
- template_id (string, required)
- trigger_phrases (array<string>, required)
- response_markdown (string, required)
- related_demo_data_keys (array<string>, optional)
- latency_budget_ms (integer, default 1000)

Validation:
- trigger_phrases must contain at least one value.
- response_markdown must not include secrets or real user identifiers.
- latency_budget_ms must be between 50 and 1000.

### 4. DownloadCTA

Represents install call-to-action targets shown from preview.

Fields:
- cta_id (string, required)
- platform (enum: macos, windows, both, required)
- label (string, required)
- url (string, required)
- placement (enum: header, inline, modal, footer, required)
- active (boolean, default true)

Validation:
- url must be HTTPS.
- macos CTA must map to DMG download route.
- inactive CTA must not be rendered.

### 5. PreviewEvent

Represents analytics event emitted during preview interactions.

Fields:
- event_id (string, UUID, required)
- session_id (string, required)
- event_type (enum: preview_loaded, query_submitted, response_rendered, cta_clicked, error_fallback, required)
- event_time (datetime, required)
- metadata (object, optional)

Validation:
- event_type must match allowlist.
- metadata must exclude sensitive fields (api_key, token, user_id).

## Relationships

- PreviewSession 1:N PreviewEvent
- DemoScenario 1:N ChatResponseTemplate (logical mapping)
- PreviewSession N:M DemoScenario (a session can run multiple scenarios)
- DownloadCTA can be referenced by DemoScenario and response UI states

## State Transitions

PreviewSession state:
- initialized -> active when preview loads
- active -> engaged when first query submitted
- engaged -> converted when download CTA clicked
- active/engaged -> expired after inactivity timeout

Error fallback state:
- normal -> degraded when preview module fails to load
- degraded -> recovered when module reload succeeds
- degraded -> fallback_only when retry budget exhausted
