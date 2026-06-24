# Implementation Plan: UI Preview Before Download

**Branch**: `004-preview-ui-before-download` | **Date**: 2026-06-24 | **Spec**: `specs/004-preview-ui-before-download/spec.md`

**Input**: Feature specification from `/specs/004-preview-ui-before-download/spec.md`

## Summary

Deliver a desktop-first web preview that allows users to experience the product UI before downloading installers. The MVP centers on an interactive chat demo with deterministic responses and clear install CTAs, followed by authentication and settings/help walkthroughs. The design prioritizes conversion clarity, performance (<3s preview load), and strict security boundaries (no real credentials or user data in preview).

## Technical Context

**Language/Version**: HTML5, CSS3, JavaScript (ES2022)

**Primary Dependencies**: No mandatory framework dependency for v1 preview; optional lightweight analytics SDK already used by landing page

**Storage**: N/A for user data; optional lightweight event pipeline for anonymous preview analytics

**Testing**: pytest for backend contract assertions (if server support is added) and browser-based validation scenarios for preview behaviors

**Target Platform**: Desktop web browsers (Chrome, Safari, Firefox, Edge) with mobile fallback support only (no mobile parity target)

**Project Type**: Web preview surface integrated with existing project/site content

**Performance Goals**: p95 preview load <3s; p95 simulated query response <1s

**Constraints**: No real intervals.icu credentials; no live user data; HTTPS-only links; deterministic demo responses

**Scale/Scope**: Marketing/onboarding funnel feature with anonymous sessions and bounded scenario catalog

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- AI Cost & Token Optimization: PASS — deterministic templates and static demo data avoid unnecessary LLM/API runtime cost.
- Approved AI Asset Usage: PASS — no new unreviewed AI assets required.
- Testing Requirement: PASS — independent validation scenarios and measurable outcomes defined.
- Security & Data Protection: PASS — explicit prohibition on real API keys and user data in preview.
- Reproducibility & Automation: PASS — quickstart includes reproducible validation paths.
- Maintainability & Reviewability: PASS — scenario-driven contract with additive extension model.

No constitutional violations identified.

## Project Structure

### Documentation (this feature)

```text
specs/004-preview-ui-before-download/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── ui-preview-contract.md
└── tasks.md
```

### Source Code (repository root)

```text
preview/
├── index.html
├── styles.css
├── preview.js
├── scenarios/
│   ├── chat_scenarios.json
│   ├── auth_scenarios.json
│   └── settings_scenarios.json
└── analytics.js

tests/
├── contract/
├── integration/
└── e2e/
```

**Structure Decision**: Implement as a web preview surface under `preview/` with static assets and deterministic scenario data. Keep all validation and spec contracts in this repository as source of truth.

## Phase 0: Outline & Research

1. Resolve unknowns in Technical Context by confirming hosting stack and dependency strategy.
2. Produce `research.md` documenting decisions, rationale, and alternatives.

## Phase 1: Design & Contracts

1. Produce `data-model.md` for preview sessions, scenario templates, CTAs, and events.
2. Define interface in `contracts/ui-preview-contract.md`.
3. Produce runnable validation guide in `quickstart.md`.
4. Update agent context pointer in `.github/copilot-instructions.md`.

## Post-Design Constitution Re-Check

- AI cost minimization preserved (deterministic templates, no live LLM).
- Security posture preserved (no credential intake; anonymous analytics only).
- Testing and measurability preserved through quickstart acceptance scenarios.

PASS.

## Complexity Tracking

No constitutional violations requiring justification.
