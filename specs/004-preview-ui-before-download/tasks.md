# Tasks: UI Preview Before Download

**Input**: Design documents from `/specs/004-preview-ui-before-download/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included and required by project constitution and feature requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

- [X] T001 Create preview scaffold in `preview/index.html`, `preview/preview.js`
- [X] T002 Create preview styles and layout scaffold in `preview/styles.css`
- [X] T003 [P] Create preview analytics adapter in `preview/analytics.js`
- [X] T004 [P] Create demo scenario seed files in `preview/scenarios/chat_scenarios.json`, `preview/scenarios/auth_scenarios.json`, `preview/scenarios/settings_scenarios.json`
- [X] T005 [P] Add preview test scaffolding in `tests/unit/test_preview_templates.py`, `tests/integration/test_preview_shell.py`, `tests/e2e/test_preview_funnel.py`
- [X] T006 Document local preview run flow in `README.md`
- [ ] T006 Document local preview run flow in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required before any user story implementation.
- [X] T007 Implement preview session model and validation in `preview/session.js`
- [X] T008 [P] Implement deterministic template resolver in `preview/template_engine.js`
- [X] T009 [P] Implement secure demo dataset provider (no live API) in `preview/demo_data.js`
- [X] T010 Implement preview route/entrypoint wiring in `preview/index.html` and `preview/preview.js`
- [X] T011 [P] Implement preview event schema and sanitization rules in `preview/events.js`
- [X] T012 Implement fallback and degraded-mode behavior in `preview/fallbacks.js`
- [X] T013 Add foundational tests for session, template engine, and data boundaries in `tests/integration/test_preview_foundation.py`
- [X] T014 [P] Add token/cost guardrail check for deterministic preview behavior in `tests/unit/test_preview_no_live_llm.py`
- [ ] T013 Add foundational tests for session, template engine, and data boundaries in `tests/integration/test_preview_foundation.py`
- [ ] T014 [P] Add token/cost guardrail check for deterministic preview behavior in `tests/unit/test_preview_no_live_llm.py`

**Checkpoint**: Foundation complete - user stories can proceed.

---

## Phase 3: User Story 1 - Explore Chat Interface Preview (Priority: P1) MVP


### Tests for User Story 1

- [X] T015 [P] [US1] Add contract test for preview route rendering in `tests/contract/test_preview_route_contract.py`
- [X] T016 [P] [US1] Add integration test for chat query-response flow in `tests/integration/test_preview_chat_flow.py`
- [X] T017 [US1] Add e2e test for CTA visibility from chat interactions in `tests/e2e/test_preview_chat_to_download_cta.py`
- [X] T018 [P] [US1] Implement preview shell layout and chat panel in `preview/index.html`
- [X] T019 [P] [US1] Implement chat input and response rendering controller in `preview/preview.js`
- [X] T020 [US1] Wire deterministic chat templates to sample queries in `preview/template_engine.js`
- [X] T021 [US1] Implement in-preview disclaimer for installed-app-only features in `preview/messages.js`
- [X] T022 [US1] Implement download CTA components (macOS/Windows) in `preview/cta.js`
- [X] T023 [US1] Add primary preview styles and responsive desktop layout in `preview/styles.css`
- [X] T024 [US1] Add preview interaction logic for chat demo in `preview/preview.js`
- [ ] T020 [US1] Wire deterministic chat templates to sample queries in `preview/template_engine.js`
- [ ] T021 [US1] Implement in-preview disclaimer for installed-app-only features in `preview/messages.js`
- [ ] T022 [US1] Implement download CTA components (macOS/Windows) in `preview/cta.js`
- [ ] T023 [US1] Add primary preview styles and responsive desktop layout in `preview/styles.css`
- [ ] T024 [US1] Add preview interaction logic for chat demo in `preview/preview.js`

**Checkpoint**: US1 independently usable and demonstrable.

---

**Goal**: Users can preview onboarding/auth steps and understand API key setup before download.

- [X] T025 [P] [US2] Add integration test for auth-preview walkthrough in `tests/integration/test_preview_auth_walkthrough.py`
- [X] T026 [US2] Add e2e test for API-key guidance links and final CTA in `tests/e2e/test_preview_auth_guidance_cta.py`
- [X] T027 [P] [US2] Implement auth preview panel and stepper in `preview/auth_preview.js`
- [X] T028 [US2] Add API key help text and intervals.icu guidance links in `preview/messages.js`
- [X] T029 [US2] Implement non-functional demo auth form state (no real credential handling) in `preview/auth_preview.js`
- [X] T030 [US2] Add transition from auth preview completion to download CTA state in `preview/cta.js`
- [ ] T026 [US2] Add e2e test for API-key guidance links and final CTA in `tests/e2e/test_preview_auth_guidance_cta.py`

### Implementation for User Story 2

- [ ] T027 [P] [US2] Implement auth preview panel and stepper in `preview/auth_preview.js`
- [ ] T028 [US2] Add API key help text and intervals.icu guidance links in `preview/messages.js`
- [ ] T029 [US2] Implement non-functional demo auth form state (no real credential handling) in `preview/auth_preview.js`
- [ ] T030 [US2] Add transition from auth preview completion to download CTA state in `preview/cta.js`

---

## Phase 5: User Story 3 - Browse Settings and Help Features (Priority: P3)
- [X] T031 [P] [US3] Add integration test for settings/help preview tour in `tests/integration/test_preview_settings_help_tour.py`
- [X] T032 [US3] Add accessibility-focused test for keyboard navigation in preview tour in `tests/unit/test_preview_accessibility.py`
- [X] T033 [P] [US3] Implement settings feature tour cards in `preview/settings_preview.js`
- [X] T034 [P] [US3] Implement help and tooltip preview module in `preview/help_preview.js`
- [X] T035 [US3] Add update/logging/preferences content mapping for preview in `preview/scenario_mapper.js`
- [X] T036 [US3] Integrate settings/help tour into preview navigation tabs in `preview/index.html`
### Tests for User Story 3

- [ ] T031 [P] [US3] Add integration test for settings/help preview tour in `tests/integration/test_preview_settings_help_tour.py`
- [ ] T032 [US3] Add accessibility-focused test for keyboard navigation in preview tour in `tests/unit/test_preview_accessibility.py`

- [X] T037 [P] Add performance benchmark test for preview load and response timing in `tests/performance/test_preview_latency.py`
- [X] T038 [P] Add security test ensuring no real credential fields/events in payloads in `tests/security/test_preview_no_sensitive_data.py`
- [X] T039 Implement graceful fallback UI for script/load failures in `preview/fallbacks.js`
- [X] T040 [P] Implement analytics event emission for funnel milestones in `preview/analytics.js`
- [X] T041 [P] Add integration test for required analytics events (`preview_loaded`, `query_submitted`, `response_rendered`, `cta_clicked`) in `tests/integration/test_preview_analytics_events.py`
- [X] T042 Validate all quickstart scenarios end-to-end in `specs/004-preview-ui-before-download/quickstart.md`
- [X] T043 Update operator/developer documentation for preview maintenance in `SETUP_NOTES.md`
- [X] T044 Define SC-002 conversion experiment design (control vs preview variant), baseline window, and uplift calculation in `specs/004-preview-ui-before-download/quickstart.md`
- [X] T045 [P] Add analytics validation test for SC-002 conversion cohort tagging and attribution in `tests/integration/test_preview_conversion_attribution.py`
- [X] T046 Add explicit mobile rendering validation for SC-007 across breakpoints/devices in `tests/e2e/test_preview_mobile_rendering.py`
- [X] T047 Add VCS compliance gate verifying signed commits before merge/release in `packaging/RELEASE_CHECKLIST.md`
- [X] T048 Define SC-001 engagement-rate formula, reporting cadence, and acceptance evaluation in `specs/004-preview-ui-before-download/quickstart.md`
- [X] T049 Define SC-006 preview-vs-real-app expectation alignment survey plan and validation threshold in `specs/004-preview-ui-before-download/quickstart.md`
**Purpose**: Final hardening, performance, analytics validation, and release readiness.

- [ ] T037 [P] Add performance benchmark test for preview load and response timing in `tests/performance/test_preview_latency.py`
- [ ] T038 [P] Add security test ensuring no real credential fields/events in payloads in `tests/security/test_preview_no_sensitive_data.py`
- [ ] T039 Implement graceful fallback UI for script/load failures in `preview/fallbacks.js`
- [ ] T040 [P] Implement analytics event emission for funnel milestones in `preview/analytics.js`
- [ ] T041 [P] Add integration test for required analytics events (`preview_loaded`, `query_submitted`, `response_rendered`, `cta_clicked`) in `tests/integration/test_preview_analytics_events.py`
- [ ] T042 Validate all quickstart scenarios end-to-end in `specs/004-preview-ui-before-download/quickstart.md`
- [ ] T043 Update operator/developer documentation for preview maintenance in `SETUP_NOTES.md`
- [ ] T044 Define SC-002 conversion experiment design (control vs preview variant), baseline window, and uplift calculation in `specs/004-preview-ui-before-download/quickstart.md`
- [ ] T045 [P] Add analytics validation test for SC-002 conversion cohort tagging and attribution in `tests/integration/test_preview_conversion_attribution.py`
- [ ] T046 Add explicit mobile rendering validation for SC-007 across breakpoints/devices in `tests/e2e/test_preview_mobile_rendering.py`
- [ ] T047 Add VCS compliance gate verifying signed commits before merge/release in `packaging/RELEASE_CHECKLIST.md`
- [ ] T048 Define SC-001 engagement-rate formula, reporting cadence, and acceptance evaluation in `specs/004-preview-ui-before-download/quickstart.md`
- [ ] T049 Define SC-006 preview-vs-real-app expectation alignment survey plan and validation threshold in `specs/004-preview-ui-before-download/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: no dependencies
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all user stories
- **Phases 3-5 (User Stories)**: depend on Phase 2 completion
- **Phase 6 (Polish)**: depends on completion of desired user stories

### User Story Dependencies

- **US1 (Chat Preview)**: starts after foundational completion
- **US2 (Auth Preview)**: starts after foundational completion; can proceed in parallel with US1
- **US3 (Settings/Help Tour)**: starts after foundational completion; can proceed in parallel with US1/US2

### Execution Preference

- Priority-first path: US1 -> US2 -> US3
- Parallel path (team): US1 + US2 + US3 after Phase 2

---

## Parallel Opportunities

- Setup: T003, T004, T005 can run in parallel
- Foundational: T008, T009, T011, T014 can run in parallel
- US1: T015, T016, T018, T019 can run in parallel
- US2: T025, T027 can run in parallel
- US3: T031, T033, T034 can run in parallel
- Polish: T037, T038, T040, T041, T045, T048 can run in parallel

---

## Implementation Strategy

### MVP First (Recommended)

1. Complete Phase 1 and Phase 2
2. Complete US1 (Phase 3)
3. Validate independent tests for US1
4. Demo pre-download preview MVP

### Incremental Delivery

1. Setup + Foundational
2. Deliver US1 (interactive chat preview)
3. Deliver US2 (authentication walkthrough)
4. Deliver US3 (settings/help tour)
5. Polish and release

### Parallel Team Strategy

1. Team completes Setup + Foundational
2. Split by story ownership:
   - Dev A: US1
   - Dev B: US2
   - Dev C: US3
3. Integrate at phase checkpoints and run full matrix in Phase 6

---

## Notes

- All tasks follow strict checklist format and include file paths.
- Tests are explicitly included for each story to satisfy constitutional requirements.
- Run `/specify.analyze` after task generation and before implementation.
