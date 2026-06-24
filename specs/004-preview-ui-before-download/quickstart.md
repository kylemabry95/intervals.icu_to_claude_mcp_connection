# Quickstart: Validate UI Preview Before Download

## Goal

Validate end-to-end behavior of the preview funnel before implementation handoff.

## Prerequisites

- Repository cloned and on main branch or feature branch for 004.
- Access to static host or local web server for preview page delivery.
- Specs available: spec.md, plan.md, data-model.md, contracts/ui-preview-contract.md.

## Scenario 1: Chat Preview Usability (P1)

1. Open preview route in desktop browser.
2. Confirm preview shell renders within 3 seconds.
3. Submit query: "Show my recent workouts".
4. Verify response appears within 1 second and reflects demo dataset.
5. Verify disclaimer indicates live data needs installed app.

Expected outcome:
- User can understand and test primary chat interaction before download.

## Scenario 2: Authentication Flow Preview (P2)

1. Click "See How to Get Started" from preview area.
2. Navigate through API-key onboarding demo screens.
3. Confirm intervals.icu key guidance link is present.
4. Confirm final step presents download CTA.

Expected outcome:
- User understands setup requirements without entering real credentials.

## Scenario 3: Settings & Help Walkthrough (P3)

1. Open feature tour/settings tab from preview.
2. Verify update preferences, logging, and help areas are visible.
3. Confirm each section indicates it is a preview representation.

Expected outcome:
- User sees breadth of product capabilities before install.

## Scenario 4: Fallback Behavior

1. Simulate preview module load failure (disable script bundle or trigger error path).
2. Confirm graceful fallback message is shown.
3. Confirm active download CTA remains available.

Expected outcome:
- Preview failure does not block user from downloading app.

## Scenario 5: Analytics Validation

1. Start preview session.
2. Submit at least one query.
3. Click macOS download CTA.
4. Inspect event stream/logs for required event types.

Expected outcome:
- Events emitted: preview_loaded, query_submitted, response_rendered, cta_clicked.
- Payloads contain no sensitive fields.

## Scenario 6: SC-001 Engagement Evaluation

Define engagement as sessions that submit at least one query.

Formula:

`engagement_rate = engaged_sessions / total_preview_sessions`

Acceptance threshold:

- PASS if engagement_rate >= 0.25 over the evaluation window.

Reporting cadence:

- Daily internal dashboard snapshot.
- Weekly rollup for release-readiness review.

## Scenario 7: SC-002 Conversion Uplift Experiment

Use two cohorts:

- Control: landing page without interactive preview.
- Variant: landing page with interactive preview enabled.

Formula:

`uplift = (variant_download_rate - control_download_rate) / control_download_rate`

Acceptance threshold:

- PASS if uplift >= 0.15 with stable attribution tagging.

Attribution requirements:

- Every CTA click event includes cohort and platform metadata.
- Conversion summary excludes sessions with missing cohort tags.

## Scenario 8: SC-006 Expectation-Alignment Survey

Run a lightweight post-install survey for users who used preview first.

Survey prompt:

- "Did the installed app match what you expected from the preview?"

Response scale:

- 1 (not at all) to 5 (fully matched)

Acceptance threshold:

- PASS if at least 80% of responses are 4 or 5.

Validation notes:

- Collect and summarize top mismatch themes.
- Feed mismatch findings into preview scenario/content updates.

## Acceptance Checklist

- P1 scenario passes independently.
- P2 and P3 scenarios are demonstrable.
- Performance targets met (3s load, 1s simulated response).
- Security/privacy boundary upheld (no real auth/data in preview).
- Download paths are always visible and functional.
