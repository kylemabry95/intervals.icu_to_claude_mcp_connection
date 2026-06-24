# Contract: UI Preview Interface

## Purpose

Defines the external interface and behavioral contract for the pre-download UI preview experience.

## Surface 1: Landing Page Preview Embed

Route:
- GET /preview

Contract:
- Must render preview container and initial demo state.
- Must display clear "demo mode" label.
- Must provide download CTAs for macOS and Windows.

Response expectations:
- First meaningful paint target: <= 3s p95.
- Rendering must degrade gracefully when JS modules fail.

## Surface 2: Demo Query Interaction

Input contract:
- User enters text query into preview input.
- Query is matched against template triggers.

Output contract:
- A deterministic preview response is rendered in <= 1s.
- Response includes disclaimer when functionality requires installed app.
- No live intervals.icu or Claude credentials are accepted or forwarded.

Error contract:
- Unknown query returns helpful fallback with suggested examples.
- Module errors show fallback summary and active download CTA.

## Surface 3: Authentication Flow Preview

Contract:
- Must show API-key onboarding screens as non-functional demo flow.
- Must include link guidance to intervals.icu API key docs.
- Must clearly indicate real authentication requires installed app.

## Surface 4: Settings & Help Walkthrough

Contract:
- Must display representative settings categories (updates, logs, preferences).
- Must display help/tooltip examples and troubleshooting entry points.
- May be screenshot-based or lightweight interactive cards in v1.

## Surface 5: Analytics Events

Event contract:
- Emit preview_loaded when preview is shown.
- Emit query_submitted and response_rendered for chat interactions.
- Emit cta_clicked with platform metadata for conversion tracking.
- Emit error_fallback when preview enters degraded state.

Privacy contract:
- No API keys or personal data in event payloads.
- Session IDs are anonymous and short-lived.

## Backward Compatibility

- New scenario categories must not break existing query templates.
- CTA configuration changes must preserve at least one active desktop download path.
- Event schema additions must be additive; existing fields remain stable.
