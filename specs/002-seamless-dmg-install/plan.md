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

### Primary Gates

✅ **AI Cost & Token Optimization** — PASS

- Scope is limited to shell scripting and build tooling (deterministic, low LLM overhead)
- No complex AI reasoning loops; straightforward macOS API integration
- Rationale: This is packaging automation, not business logic

✅ **Testing as Non-Negotiable** — PASS with Manual Testing Plan

- Installation behavior is inherently manual-test-heavy (macOS DMG mounting/system integration)
- Automated testing constrained by system-level file operations and user interaction flows
- Justification: Include comprehensive manual DMG test scenarios in Phase 0 research

✅ **Security, Access Control, Data Protection** — PASS

- No credentials or sensitive data involved; purely file system operations
- Existing code signing infrastructure already addresses app trust requirements
- No new API access or data handling introduced

✅ **Reproducibility & Automation** — PASS

- All automation steps documented in shell scripts
- Build process fully reproducible across macOS versions (11+)
- No manual configuration required beyond standard system permissions

✅ **Version Control & Reviewability** — PASS

- All changes tracked in working branch `002-seamless-dmg-install`
- Code review focused on shell script safety and error handling
- DMG build process remains deterministic and auditable

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

```text
packaging/macos/
├── build.sh                    # Main DMG build script (EXISTING - will extend)
├── install.sh                  # NEW: Automated installation script (mounted from DMG)
├── entitlements.plist          # Code signing entitlements (EXISTING)
└── fix-gatekeeper.sh           # Quarantine removal helper (EXISTING)

dist/macos/
└── IntervalsICU-{version}.dmg  # Distributable DMG with install.sh included
```

**Structure Decision**: Build tooling only; no new application code required. This feature extends the existing DMG build pipeline (`packaging/macos/build.sh`) with an embedded installation automation script that users invoke by double-clicking the DMG or running from mounted volume. No changes to application source code structure needed.

---

## Phase 0: Research & Unknowns Resolution

**Status**: ✅ COMPLETE

### Research Questions & Findings

1. **DMG Mounting & Auto-Launch Mechanisms** (RESOLVED)
   - **Finding**: DMG files can include an `autoopen.app` or `install.app` that launches on mount
   - **Decision**: Create `install.sh` script within DMG that users invoke manually or via double-click handler
   - **Rationale**: More reliable than AppleScript automation; respects user control and security sandbox

2. **Gatekeeper Quarantine Attribute Removal** (RESOLVED)
   - **Finding**: `xattr -d com.apple.quarantine` is the standard, supported method for removing quarantine
   - **Decision**: Build into installation script after copying app to `/Applications/`
   - **Rationale**: Already documented in README; proven to work across macOS 11+

3. **Installation Destination Permissions** (RESOLVED)
   - **Finding**: Standard `/Applications/` is writable by users on most macOS installs; `/Library/Application Support/` fallback available
   - **Decision**: Try `/Applications/` first; provide clear error if permission denied, suggest alternatives
   - **Rationale**: Most users expect apps in `/Applications/`; graceful fallback improves UX

4. **DMG Unmounting Strategy** (RESOLVED)
   - **Finding**: Users may leave DMG mounted; automatic unmount can be disruptive; manual prompt + success confirmation better
   - **Decision**: Display installation completion message; guide user to manually eject DMG from Finder
   - **Rationale**: Non-destructive; users retain control; reduces automation errors

### Test Scenarios Documented

- ✅ Successful installation to `/Applications/` with Gatekeeper cleared
- ✅ Permission denied on `/Applications/` with helpful error message
- ✅ Insufficient disk space with specific error and recovery steps
- ✅ Already-installed app (detect and offer to replace/skip)
- ✅ Cancellation midway through process (cleanup partial installation)

**Artifacts Generated**: _(Embedded in Phase 1 design documents)_

---

## Phase 1: Design Artifacts

### 1. Data Model (Installer State)

**Installation State Machine** (`install.sh` logic flow):

```
START
  ├─→ Detect source: /Volumes/IntervalsICU/IntervalsICU.app
  ├─→ Verify app bundle integrity (Info.plist exists, executable bit set)
  ├─→ Check destination: /Applications/IntervalsICU.app
  │    ├─→ Exists? Ask user (replace/skip/cancel)
  │    └─→ Check disk space (need ~100MB)
  ├─→ Copy app bundle to /Applications/
  ├─→ Remove quarantine attribute: xattr -d com.apple.quarantine
  ├─→ Verify installation: codesign -v /Applications/IntervalsICU.app
  ├─→ Display success message
  └─→ Prompt user to eject DMG
END
```

**Error States**:

- `ERR_SOURCE_NOT_FOUND`: Source app bundle not detected
- `ERR_DEST_PERMISSION_DENIED`: No write permission to `/Applications/`
- `ERR_INSUFFICIENT_DISK_SPACE`: Less than 100MB available
- `ERR_COPY_FAILED`: File copy operation failed
- `ERR_SIGNATURE_INVALID`: Post-installation signature verification failed

### 2. Public Contracts

**User Interface Contract** (install.sh output):

```
Installation prompts:
- [Informational] "Installing IntervalsICU to /Applications/..."
- [Progress] "Copying application bundle..."
- [Progress] "Removing security restrictions..."
- [Progress] "Verifying installation..."
- [Success] "✅ Installation complete! IntervalsICU is ready to launch."
- [Success] "💡 You can now eject the IntervalsICU DMG from Finder."
- [Error] "{error_type}: {details}\n💡 Recovery: {recovery_steps}"
```

**DMG Integration Contract** (`packaging/macos/build.sh`):

```bash
# Add to build script:
- Copy install.sh into DMG root (alongside .app bundle)
- Make install.sh executable (chmod +x)
- Document in DMG: "Run './install.sh' to install IntervalsICU"
- Verify install.sh has error handling and clear messaging
```

### 3. Quickstart Validation Guide

**One-Click Installation Test Flow**:

1. **Setup**: Download `IntervalsICU-1.0.0.dmg` to Desktop
2. **User Action**: Double-click DMG to mount
3. **Verification**:
   - DMG mounts to `/Volumes/IntervalsICU/`
   - Visible files: `IntervalsICU.app`, `install.sh`, `Applications` symlink
4. **User Action**: Double-click `install.sh` OR run `./install.sh` in Terminal
5. **Expected Output**:
   ```
   Installing IntervalsICU to /Applications/...
   Copying application bundle...
   Removing security restrictions...
   Verifying installation...
   ✅ Installation complete! IntervalsICU is ready to launch.
   💡 You can now eject the IntervalsICU DMG from Finder.
   ```
6. **Verification**:
   - `/Applications/IntervalsICU.app` exists and is executable
   - `xattr -l /Applications/IntervalsICU.app | grep quarantine` returns empty (attribute removed)
   - User can launch app from Spotlight/Applications without Gatekeeper warnings
   - User can eject DMG from Finder (Cmd+E or drag to Trash)

**Error Scenario Test** (Permission Denied):

1. **Setup**: On a system where `/Applications` is locked (multi-user admin setup)
2. **User Action**: Run `./install.sh`
3. **Expected Output**:
   ```
   ERR_DEST_PERMISSION_DENIED: Cannot write to /Applications/
   💡 Recovery: Try one of these options:
     - Ask your administrator for write permission to /Applications
     - Request the app be installed to ~/Applications instead
     - Contact support@intervals.icu for multi-user installation guide
   ```

---

## Artifacts Checklist

- [x] plan.md (this file) — complete technical plan
- [ ] research.md — phase 0 research findings
- [ ] data-model.md — installation state machine diagram
- [ ] quickstart.md — validation scenarios and test procedures
- [ ] contracts/ — DMG integration contract and installer I/O interface
- [ ] tasks.md — generated by `/speckit.tasks` (Phase 2)

---

## Next Steps

**Phase 2 (Task Generation)**:

- Run `/speckit.tasks` to generate `tasks.md` with implementation steps
- Task breakdown will include:
  - Update `packaging/macos/build.sh` to embed `install.sh` in DMG
  - Create `packaging/macos/install.sh` with full error handling
  - Test scenarios and validation procedures
  - README/documentation updates

**Phase 1.5 (Agent Context Update)**:

- After planning completes, execute post-hook: `/speckit.agent-context.update`
- This updates `.github/copilot-instructions.md` to reference this plan
