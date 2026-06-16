# Implementation Plan: Standalone intervals.icu + Claude Desktop Application

**Branch**: `feature/001-standalone-intervals-app` | **Date**: 2026-06-16 | **Spec**: specs/001-standalone-intervals-app/spec.md

## Summary

Deliver a user-friendly desktop application that bundles the existing MCP server and provides a Claude-driven conversational interface to intervals.icu training data. The app targets macOS and Windows (v1), with scheduled update checks and secure credential storage.

## Technical Context

**Language/Version**: Python 3.10 (project README indicates Python 3.10+)

**Primary Dependencies**: `httpx`, `mcp`, (testing: `pytest`)

**Storage**: Local app config + system secure storage (Keychain on macOS, Credential Manager on Windows)

**Testing**: `pytest`, existing `test_server.py` used for integration smoke tests

**Target Platform**: Desktop (macOS 11+, Windows 10 21H2+)

**Project Type**: Local service + desktop UI wrapper (Electron/Neutral UI or native packaging)

**Performance Goals**: p95 query latency < 5s; handle 10k+ training records without degradation

**Constraints**: Must follow constitution: cost-optimization, testing, security, reproducibility

**Scale/Scope**: Single-user local application; later multi-account or Linux support can be added

## Constitution Check

GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.

- AI Cost & Token Optimization: PASS — use of MCP and local deterministic tooling; design favors minimizing prompt size and reusing structured tools
- Testing Requirement: PASS — `test_server.py` exists; tests required for new UI wrapper and packaging steps
- Security & Data Protection: PASS (design-level) — secrets stored in OS-secure store; no credentials in repo

If any of these change during design, abort and document gate violations.

## Project Structure

See repository root. Feature docs will live under `specs/001-standalone-intervals-app/`.

## Phase 0: Outline & Research

1. Resolve clarifications (complete): update mechanism (scheduled checks), OS targets (macOS + Windows), minimum OS versions (macOS 11, Windows 10 21H2)
2. Produce `research.md` (this plan references it)

## Phase 1: Design & Contracts

Outputs: `data-model.md`, `contracts/`, `quickstart.md` (created alongside this plan)

Key design tasks:
- Define packaging approach (Electron vs native bundlers) — tradeoffs: app size, native integration, auto-update support
- Define UI architecture (minimal web UI served locally vs native window) — minimal web UI recommended for rapid MVP
- Define IPC between UI and MCP server (use local stdio proxy or WebSocket adapter)
- Define secure credential storage and retrieval path per OS
- Define update-check service and UX (daily scheduled checks, user deferral)

## Phase 2: Implementation Tasks (high-level)

1. Packaging and installer scripts (macOS DMG or notarized app, Windows installer)
2. Desktop UI: minimal chat interface + settings panel
3. Local MCP server integration and lifecycle management
4. Authentication UX and secure storage
5. Tests: unit tests for packaging scripts, UI integration smoke tests, e2e with `test_server.py`
6. CI: build matrix for macOS and Windows packaging (or use GitHub Actions with macOS runner and Windows runner)

## Quick Validation

- Run `python server.py` locally to validate MCP server starts
- Run `python test_server.py` (with env vars) to smoke-test endpoints

## Artifacts Produced

- specs/001-standalone-intervals-app/plan.md (this file)
- specs/001-standalone-intervals-app/research.md
- specs/001-standalone-intervals-app/data-model.md
- specs/001-standalone-intervals-app/quickstart.md
- specs/001-standalone-intervals-app/contracts/
