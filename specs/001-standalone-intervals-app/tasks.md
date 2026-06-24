# Tasks: Standalone intervals.icu + Claude Desktop Application

**Input**: Design documents from `/specs/001-standalone-intervals-app/`

**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included and required by project constitution and feature requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Every task includes an exact file path

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize desktop-app workspace and build tooling for packaging and validation.

- [x] T001 Create desktop app module scaffold in `desktop_app/__init__.py`, `desktop_app/main.py`, `desktop_app/ui/__init__.py`
- [x] T002 Create desktop packaging config stubs in `packaging/macos/build.sh`, `packaging/windows/build.ps1`
- [x] T003 [P] Add desktop runtime and testing dependencies to `requirements.txt`
- [x] T004 [P] Add test package scaffolding in `tests/unit/test_desktop_config.py`, `tests/integration/test_desktop_startup.py`, `tests/e2e/test_local_conversation_flow.py`
- [x] T005 [P] Add environment template for standalone app in `.env.example`
- [x] T006 Document local run and build entrypoints in `README.md`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core components required before implementing user stories.

**CRITICAL**: No user story work starts until this phase is complete.
- [ ] T006b [P] **GATE: Validate AI Token Budget** — Review conversation model (T032 design), MCP tool definitions in `server.py`, and prompt templates for compliance with constitution principle I (AI Cost Optimization). Document token budget assumptions in `specs/001-standalone-intervals-app/contracts/token-budget.md` before Phase 3 stories begin. This ensures query latency and cost targets are achievable.
- [x] T007 Implement desktop app configuration loader and validation in `desktop_app/config.py`
- [x] T008 [P] Implement secure credential abstraction (Keychain/Credential Manager adapters) in `desktop_app/security/credentials.py`
- [x] T009 [P] Implement MCP server process manager (start/stop/health/state) in `desktop_app/runtime/mcp_process.py`
- [x] T010 Implement Claude Desktop bridge client and connection-state polling in `desktop_app/runtime/claude_bridge.py`
- [x] T011 [P] Implement shared structured logging and log file rotation in `desktop_app/observability/logging.py`
- [x] T012 Implement shared error model and user-safe error mapping in `desktop_app/errors.py`
- [x] T013 Create foundational integration tests for config, process lifecycle, and secure storage in `tests/integration/test_foundation_runtime.py`

**Checkpoint**: Foundation complete - user stories can proceed.

---

## Phase 3: User Story 1 - Install and Launch Application (Priority: P1) MVP

**Goal**: Users can install and launch the standalone app on macOS and Windows.

**Independent Test**: Install from generated package and verify app launches to initial screen and exits cleanly.

### Tests for User Story 1

- [x] T014 [P] [US1] Add installer smoke test for macOS package in `tests/e2e/test_install_macos.py`
- [x] T015 [P] [US1] Add installer smoke test for Windows package in `tests/e2e/test_install_windows.py`
- [x] T016 [US1] Add launch and graceful shutdown integration test in `tests/integration/test_launch_shutdown.py`

### Implementation for User Story 1

- [x] T017 [P] [US1] Implement app bootstrap and single-instance guard in `desktop_app/main.py`
- [x] T018 [P] [US1] Implement startup window shell and initial route in `desktop_app/ui/shell.py`
- [x] T019 [US1] Implement startup orchestration for runtime checks in `desktop_app/runtime/startup.py`
- [x] T020 [US1] Implement macOS packaging script for app bundle and DMG in `packaging/macos/build.sh`
- [x] T021 [US1] Implement Windows packaging script for signed installer flow in `packaging/windows/build.ps1`

**Checkpoint**: US1 independently installable and launchable.

---

## Phase 4: User Story 2 - Authenticate with intervals.icu API (Priority: P1)

**Goal**: Users can authenticate with API key, persist credentials securely, and log out safely.

**Independent Test**: Authenticate with valid key, reject invalid key, restart app to verify persisted login, and verify logout clears secure store.

### Tests for User Story 2

- [x] T022 [P] [US2] Add API-key validation unit tests in `tests/unit/test_auth_validation.py`
- [x] T023 [P] [US2] Add credential persistence integration test in `tests/integration/test_auth_persistence.py`
- [x] T024 [US2] Add logout-clears-credentials integration test in `tests/integration/test_auth_logout.py`

### Implementation for User Story 2

- [x] T025 [P] [US2] Implement authentication service and key verification flow in `desktop_app/auth/service.py`
- [x] T026 [P] [US2] Implement login/logout controller and auth session state in `desktop_app/auth/session.py`
- [x] T027 [US2] Implement auth screen and user guidance text in `desktop_app/ui/auth_view.py`
- [x] T028 [US2] Implement auth error messaging and remediation hints in `desktop_app/ui/components/auth_errors.py`

**Checkpoint**: US2 independently usable with secure login lifecycle.

---

## Phase 5: User Story 3 - Query Training Data via Claude Conversation (Priority: P1)

**Goal**: Users can ask natural-language questions and receive Claude answers grounded in intervals.icu data.

**Independent Test**: Submit representative prompts and verify response quality, context carry-over, and graceful handling of missing data.

### Tests for User Story 3

- [x] T029 [P] [US3] Add contract tests for MCP tool-to-endpoint mapping in `tests/contract/test_mcp_contracts.py`
- [x] T030 [P] [US3] Add integration test for primary query flow in `tests/integration/test_conversation_queries.py`
- [x] T031 [US3] Add follow-up context continuity test in `tests/integration/test_conversation_context.py`
- [x] T055 [US3] Add endpoint coverage matrix test for all supported intervals.icu tool endpoints in `tests/contract/test_endpoint_coverage_matrix.py`
- [x] T056 [US3] Add high-volume query performance test for 10k+ record workloads in `tests/performance/test_query_scale_10k.py`
- [x] T061 [US3] Create SC-004 acceptance evaluation dataset and expected answer annotations in `tests/evaluation/sc004_dataset.json`
- [x] T062 [US3] Implement SC-004 rubric scorer and pass/fail CI check (95% threshold) in `tests/evaluation/test_sc004_response_quality.py`

### Implementation for User Story 3

- [x] T032 [P] [US3] Implement conversation domain model and context summarization in `desktop_app/conversation/model.py`
- [x] T033 [P] [US3] Implement conversation orchestration service (Claude + MCP calls) in `desktop_app/conversation/service.py`
- [x] T034 [US3] Implement chat UI, streaming states, and message history in `desktop_app/ui/chat_view.py`
- [x] T035 [US3] Implement unavailable-data fallback handling in `desktop_app/conversation/fallbacks.py`
- [x] T036 [US3] Add performance telemetry for query latency SLIs in `desktop_app/observability/metrics.py`

**Checkpoint**: US3 independently delivers the core conversational value.

---

## Phase 6: User Story 4 - Manage Application Settings (Priority: P2)

**Goal**: Users can manage API key, preferences, logging visibility, and update behavior in a settings panel.

**Independent Test**: Change settings and API key in UI, restart app, and verify persisted behavior and re-authentication.

### Tests for User Story 4

- [x] T037 [P] [US4] Add settings persistence unit tests in `tests/unit/test_settings_store.py`
- [x] T038 [P] [US4] Add integration test for API key update and re-auth in `tests/integration/test_settings_reauth.py`
- [x] T039 [US4] Add integration test for log viewer rendering in `tests/integration/test_settings_logs.py`

### Implementation for User Story 4

- [x] T040 [P] [US4] Implement settings repository and preference schema in `desktop_app/settings/repository.py`
- [x] T041 [P] [US4] Implement settings service for update policy and preferences in `desktop_app/settings/service.py`
- [x] T042 [US4] Implement settings panel UI and forms in `desktop_app/ui/settings_view.py`
- [x] T043 [US4] Implement in-app log viewer and filtering in `desktop_app/ui/components/log_viewer.py`
- [x] T057 [US4] Implement scheduled daily update-check scheduler with prompt and defer actions in `desktop_app/settings/update_scheduler.py`
- [x] T058 [US4] Add integration test for daily update check prompt and user deferral flow in `tests/integration/test_update_scheduler.py`

**Checkpoint**: US4 independently provides complete settings management.

---

## Phase 7: User Story 5 - Receive Contextual Help and Guidance (Priority: P2)

**Goal**: Users can discover help content, understand fields, and recover from errors using contextual guidance.

**Independent Test**: Verify tooltips, help center links, and actionable error guidance across auth/chat/settings views.

### Tests for User Story 5

- [x] T044 [P] [US5] Add tooltip rendering and accessibility tests in `tests/unit/test_help_tooltips.py`
- [x] T045 [P] [US5] Add integration test for contextual help routing in `tests/integration/test_help_navigation.py`

### Implementation for User Story 5

- [x] T046 [P] [US5] Implement help-content provider and FAQ mapping in `desktop_app/help/content.py`
- [x] T047 [P] [US5] Implement reusable tooltip/help components in `desktop_app/ui/components/help.py`
- [x] T048 [US5] Integrate contextual help in auth/chat/settings screens in `desktop_app/ui/help_integration.py`
- [x] T049 [US5] Implement error-to-help link mapping in `desktop_app/help/error_guidance.py`

**Checkpoint**: US5 independently improves user onboarding and recovery.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening and release quality checks across all stories.

- [x] T050 [P] Run full automated test matrix and fix regressions in `tests/`
- [x] T051 [P] Add security hardening checks for secrets/log redaction in `desktop_app/security/credentials.py` and `desktop_app/observability/logging.py`
- [x] T052 Validate quickstart instructions end-to-end in `specs/001-standalone-intervals-app/quickstart.md`
- [x] T053 [P] Finalize release checklist and installer verification in `packaging/RELEASE_CHECKLIST.md`
- [x] T054 Update user and operator documentation for deploy/run/troubleshooting in `README.md` and `SETUP_NOTES.md`
- [x] T059 Add uptime SLO instrumentation and rolling availability reports for authenticated sessions in `desktop_app/observability/uptime.py`
- [x] T060 Add resilience and uptime verification tests for process restart/recovery scenarios in `tests/reliability/test_uptime_resilience.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: no dependencies
- **Phase 2 (Foundational)**: depends on Phase 1 and blocks all stories
- **Phases 3-7 (User Stories)**: depend on Phase 2 completion
- **Phase 8 (Polish)**: depends on completion of desired user stories

### User Story Dependencies

- **US1 (Install/Launch)**: starts after foundational completion
- **US2 (Authentication)**: starts after foundational completion; independent of US1 implementation details
- **US3 (Conversation)**: starts after foundational completion; can proceed in parallel, integrates auth state when available
- **US4 (Settings)**: starts after foundational completion; can proceed in parallel, consumes shared settings/auth services
- **US5 (Help)**: starts after foundational completion; can proceed in parallel and integrate incrementally

### Execution Preference

- Priority-first path: US1 -> US2 -> US3 -> US4 -> US5
- Parallel path (team): US1 + US2 + US3 in parallel after Phase 2, then US4 + US5

---

## Parallel Opportunities

- Setup: T003, T004, T005 can run in parallel
- Foundational: T008, T009, T011 can run in parallel
- US1: T014, T015, T017, T018 can run in parallel
- US2: T022, T023, T025, T026 can run in parallel
- US3: T029, T030, T032, T033, T061 can run in parallel
- US4: T037, T038, T040, T041, T057 can run in parallel
- US5: T044, T045, T046, T047 can run in parallel
- Polish: T050, T051, T053, T059 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Run in parallel after Phase 2
Task T014: tests/e2e/test_install_macos.py
Task T015: tests/e2e/test_install_windows.py
Task T017: desktop_app/main.py
Task T018: desktop_app/ui/shell.py
```

## Parallel Example: User Story 2

```bash
# Run in parallel after Phase 2
Task T022: tests/unit/test_auth_validation.py
Task T023: tests/integration/test_auth_persistence.py
Task T025: desktop_app/auth/service.py
Task T026: desktop_app/auth/session.py
```

## Parallel Example: User Story 3

```bash
# Run in parallel after Phase 2
Task T029: tests/contract/test_mcp_contracts.py
Task T030: tests/integration/test_conversation_queries.py
Task T032: desktop_app/conversation/model.py
Task T033: desktop_app/conversation/service.py
Task T055: tests/contract/test_endpoint_coverage_matrix.py
Task T061: tests/evaluation/sc004_dataset.json
```

## Parallel Example: User Story 4

```bash
# Run in parallel after Phase 2
Task T037: tests/unit/test_settings_store.py
Task T038: tests/integration/test_settings_reauth.py
Task T040: desktop_app/settings/repository.py
Task T041: desktop_app/settings/service.py
Task T057: desktop_app/settings/update_scheduler.py
```

## Parallel Example: User Story 5

```bash
# Run in parallel after Phase 2
Task T044: tests/unit/test_help_tooltips.py
Task T045: tests/integration/test_help_navigation.py
Task T046: desktop_app/help/content.py
Task T047: desktop_app/ui/components/help.py
```

---

## Implementation Strategy

### MVP First (Recommended)

1. Complete Phase 1 and Phase 2
2. Complete US1, US2, US3 (Phases 3-5)
3. Validate independent tests for US1-US3
4. Demo/deploy MVP

### Incremental Delivery

1. Setup + Foundational
2. Deliver US1 (install/launch)
3. Deliver US2 (authentication)
4. Deliver US3 (conversation value)
5. Deliver US4 (settings)
6. Deliver US5 (help/guidance)
7. Polish and release

### Parallel Team Strategy

1. Team completes Setup + Foundational together
2. Then split stories by ownership:
   - Dev A: US1
   - Dev B: US2
   - Dev C: US3
   - Dev D: US4/US5
3. Integrate at phase checkpoints and run full matrix in Phase 8

---

## Notes

- All tasks follow strict checklist format and include file paths.
- Tests are explicitly included for each story to satisfy constitutional requirements.
- Use `/specify.analyze` after this file and before `/specify.implement` per constitution.
