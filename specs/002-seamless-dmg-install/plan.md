# Implementation Plan: Seamless DMG Installation

**Branch**: `002-seamless-dmg-install` | **Date**: 2026-06-16 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/002-seamless-dmg-install/spec.md`

**Note**: This plan guides Phase 0 (research), Phase 1 (design artifacts), and Phase 1.5 (agent context update).

## Summary

Enable users to install the IntervalsICU macOS application by downloading and double-clicking the DMG file—no manual drag-and-drop or terminal commands required. The system must automatically mount the DMG, copy the application to `/Applications/`, remove Gatekeeper quarantine attributes, and unmount cleanly. All within a 30-second user experience with clear success/error messaging.

## Technical Context

**Language/Version**: Bash/Shell (macOS-compatible), AppleScript (optional for UI polish)

**Primary Dependencies**:

- macOS system tools: `hdiutil` (mount/unmount DMG), `cp` (file operations), `xattr` (remove quarantine), `codesign` (verify signatures)
- Existing: `create-dmg` (DMG creation), entitlements.plist (code signing configuration)

**Storage**: N/A (this is packaging/installation, not application state storage)

**Testing**: Manual DMG testing on macOS 11+, shell script validation, error scenario simulation

**Target Platform**: macOS 11 (Big Sur) and later (arm64 + Intel support via universal binary)

**Project Type**: Build tooling / Installer script (extends existing desktop-app build pipeline)

**Performance Goals**: Installation completes in under 30 seconds from user double-click to app ready-to-launch

**Constraints**:

- Must work with standard user permissions (no sudo required for `/Applications` on typical macOS installs)
- Must handle permission-denied gracefully on locked systems
- Must not disable macOS security features; must work within standard security model
- DMG should be distributable via standard file sharing without re-signing

**Scale/Scope**: Single application installer; applies to all future IntervalsICU DMG releases

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation                  | Why Needed         | Simpler Alternative Rejected Because |
| -------------------------- | ------------------ | ------------------------------------ |
| [e.g., 4th project]        | [current need]     | [why 3 projects insufficient]        |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient]  |
