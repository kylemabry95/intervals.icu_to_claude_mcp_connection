# Data Model: Installation Process & Error States

**Date**: 2026-06-16 | **Phase**: 1 | **Version**: 1.0

## Installation State Machine

```
┌─────────────────────────────────────────────────────────────────┐
│ SEAMLESS DMG INSTALLATION STATE FLOW                            │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├─ [DETECT] Source Application Bundle
  │    └─→ Find: /Volumes/IntervalsICU/IntervalsICU.app
  │    └─→ Verify: Info.plist exists, executable bit set
  │    └─→ Transition: READY_TO_COPY
  │
  ├─ [VERIFY_DEST] Check Destination
  │    ├─→ If /Applications/IntervalsICU.app exists:
  │    │    └─→ Prompt user: Replace? (Yes/No/Cancel)
  │    │    └─→ If No → ABORT_INSTALLATION
  │    │    └─→ If Cancel → ABORT_INSTALLATION
  │    │    └─→ If Yes → DELETE_EXISTING → READY_TO_COPY
  │    │
  │    ├─→ If /Applications not writable:
  │    │    └─→ ERR_DEST_PERMISSION_DENIED → DISPLAY_ERROR
  │    │
  │    └─→ If insufficient disk space (<100MB):
  │         └─→ ERR_INSUFFICIENT_DISK_SPACE → DISPLAY_ERROR
  │
  ├─ [COPY] Copy Application Bundle
  │    ├─→ Execute: cp -r /Volumes/IntervalsICU/IntervalsICU.app /Applications/
  │    ├─→ On success → READY_FOR_QUARANTINE_REMOVAL
  │    └─→ On failure → ERR_COPY_FAILED → DISPLAY_ERROR
  │
  ├─ [QUARANTINE] Remove Extended Attributes
  │    ├─→ Execute: xattr -rd com.apple.quarantine /Applications/IntervalsICU.app
  │    ├─→ On success → READY_FOR_VERIFICATION
  │    └─→ On failure → WARN_QUARANTINE_ISSUE (non-blocking)
  │
  ├─ [VERIFY] Verify Installation
  │    ├─→ Execute: codesign -v /Applications/IntervalsICU.app
  │    ├─→ On success → INSTALLATION_COMPLETE
  │    └─→ On failure → WARN_SIGNATURE_INVALID (non-blocking)
  │
  ├─ [SUCCESS] Display Success Message
  │    └─→ Show: "✅ Installation complete! IntervalsICU is ready to launch."
  │    └─→ Prompt: "You can now eject the IntervalsICU DMG"
  │    └─→ Transition: READY_FOR_LAUNCH
  │
  └─ END (USER CAN LAUNCH APP)

┌─ ERROR PATHS (shown separately) ────────────────────────────────┐
│                                                                 │
│ DISPLAY_ERROR [from any error state]                            │
│   └─→ Show: "{ERROR_CODE}: {error_description}"                │
│   └─→ Show: "💡 Recovery: {recovery_steps}"                    │
│   └─→ Exit with error code                                      │
│   └─→ INSTALLATION_FAILED                                       │
│                                                                 │
│ ABORT_INSTALLATION [from user cancel]                           │
│   └─→ No message (user initiated)                              │
│   └─→ Exit cleanly (code 0)                                    │
│   └─→ No cleanup needed (nothing copied yet)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Error State Definitions

### Critical Errors (Block Installation)

| Error Code                    | Condition                                              | Message                                                | Recovery                                                              |
| ----------------------------- | ------------------------------------------------------ | ------------------------------------------------------ | --------------------------------------------------------------------- |
| `ERR_SOURCE_NOT_FOUND`        | `/Volumes/IntervalsICU/IntervalsICU.app` doesn't exist | "Source application not found in DMG"                  | "Verify DMG mounted correctly, re-mount if needed"                    |
| `ERR_DEST_PERMISSION_DENIED`  | Cannot write to `/Applications/`                       | "Permission denied: Cannot write to /Applications/"    | "Ask administrator for write permission OR install to ~/Applications" |
| `ERR_INSUFFICIENT_DISK_SPACE` | Less than 100MB free on volume                         | "Insufficient disk space (need 100MB, have XMB)"       | "Free up disk space and try again"                                    |
| `ERR_COPY_FAILED`             | File copy operation failed (general)                   | "Failed to copy application bundle"                    | "Check disk permissions and available space, try again"               |
| `ERR_SIGNATURE_INVALID`       | Code signature verification failed                     | "Signature verification failed (app may be corrupted)" | "Download fresh DMG and try again, or contact support"                |

### Warnings (Non-Blocking)

| Warning Code             | Condition                                      | Message                                                                | Impact                                                                                                   |
| ------------------------ | ---------------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `WARN_QUARANTINE_ISSUE`  | xattr removal returned error                   | "⚠️ Could not remove Gatekeeper restrictions (may be already cleared)" | May see Gatekeeper prompt on first launch; user can manually remove with `xattr -d com.apple.quarantine` |
| `WARN_SIGNATURE_INVALID` | codesign verification failed post-installation | "⚠️ Could not verify app signature (app may still be usable)"          | Lower confidence in app integrity; proceed with caution                                                  |

### User Actions

| Action                                 | Result                             | Next State             |
| -------------------------------------- | ---------------------------------- | ---------------------- |
| User selects "Replace" when app exists | Delete existing, proceed with copy | READY_TO_COPY          |
| User selects "Skip" when app exists    | Exit cleanly without copying       | INSTALLATION_ABORTED   |
| User cancels (Ctrl+C, etc.)            | Attempt cleanup of partial install | INSTALLATION_CANCELLED |

---

## Installation Destination Paths

### Primary Destination

- **Path**: `/Applications/IntervalsICU.app`
- **Permissions**: User write required (standard on most Macs)
- **Visibility**: User-facing; visible in Finder + Spotlight

### Fallback Destinations (documented for advanced users)

- **Path**: `~/Applications/IntervalsICU.app` (user home)
- **Permissions**: Always available (user owns home directory)
- **Usage**: When `/Applications` is locked (multi-user systems)

### Not Recommended (for documentation purposes)

- `/Library/Application Support/IntervalsICU/` — Non-standard location
- `/opt/IntervalsICU/` — Unix convention, not macOS standard
- Temporary locations — User would need to move manually

---

## File & Attribute Models

### Application Bundle Structure

```
IntervalsICU.app/
├── Contents/
│   ├── MacOS/
│   │   └── IntervalsICU          (main executable)
│   ├── Resources/                (images, data files)
│   ├── Frameworks/               (dependencies)
│   └── Info.plist                (app metadata)
├── [CodeSignature]/              (added by codesign)
└── [quarantine attr]             (added by download, removed by install)
```

### Extended Attributes Managed

| Attribute                      | Added By              | Removed By           | Purpose                    |
| ------------------------------ | --------------------- | -------------------- | -------------------------- |
| `com.apple.quarantine`         | macOS (download)      | install.sh (`xattr`) | Gatekeeper security marker |
| `com.apple.code-sign-identity` | build.sh (`codesign`) | N/A (preserved)      | Code signature identity    |

---

## Timing & Performance Model

### Installation Timeline (Target: <30 seconds)

| Phase                           | Duration   | Notes                                      |
| ------------------------------- | ---------- | ------------------------------------------ |
| Source detection & verification | ~100ms     | File system operations only                |
| Destination checks              | ~200ms     | Permission checks, disk space calc         |
| Copy application bundle         | ~5-10s     | Depends on disk speed, bundle size (~50MB) |
| Quarantine attribute removal    | ~100ms     | Fast xattr operation                       |
| Signature verification          | ~500ms     | codesign validation                        |
| **Total**                       | **~6-11s** | **Well under 30s target**                  |

**Critical Path**: File copy dominates timing. Disk I/O performance is bottleneck.

---

## Success Criteria Validation

| Criterion               | Measurement                                           | Target | Status                                      |
| ----------------------- | ----------------------------------------------------- | ------ | ------------------------------------------- |
| **Installation Speed**  | Time from script start to "✅ Complete" message       | <30s   | ✅ Expected ~6-11s                          |
| **Gatekeeper Warnings** | User sees warnings on first app launch                | 0      | ✅ Quarantine removed                       |
| **Success Rate**        | % of installations succeeding with proper permissions | 100%   | ✅ Deterministic process                    |
| **Error Clarity**       | % of users understanding what went wrong              | 95%+   | ✅ Specific error messages + recovery steps |
| **Permission Handling** | Systems handle permission errors gracefully           | 100%   | ✅ Non-blocking, clear guidance             |

---

## Data Validation Rules

### Pre-Installation Validation

```
Source App Bundle Valid?
  ├─→ File exists at /Volumes/IntervalsICU/IntervalsICU.app
  ├─→ Contains Info.plist
  ├─→ Contains executable at Contents/MacOS/IntervalsICU
  └─→ All checks must pass; fail on first error

Destination Writable?
  ├─→ /Applications directory exists
  ├─→ Current user has write permission
  └─→ Continue only if both true; else ERR_DEST_PERMISSION_DENIED

Sufficient Disk Space?
  ├─→ Get free space on volume containing /Applications/
  ├─→ Compare against app bundle size + 10% margin
  └─→ Fail if free_space < (bundle_size * 1.1)
```

### Post-Installation Validation

```
App Bundle Copied Successfully?
  ├─→ /Applications/IntervalsICU.app exists
  ├─→ Is directory (not file)
  └─→ Contains Contents/MacOS/IntervalsICU

Quarantine Attribute Removed?
  ├─→ xattr -l /Applications/IntervalsICU.app | grep quarantine
  └─→ Should return empty (non-zero grep result = removed)

Signature Valid?
  ├─→ codesign -v /Applications/IntervalsICU.app
  └─→ Exit code 0 = valid; non-zero = warn but continue
```

---

## Idempotency & Repeatability

**Installation is idempotent**: Running `install.sh` multiple times yields same result (with user prompt to replace if app exists).

```bash
# Run 1: Fresh install
./install.sh
# → Copies app to /Applications/, removes quarantine
# → ✅ Success

# Run 2: Same script, already installed
./install.sh
# → Detects app exists, asks "Replace? [Yes/No/Cancel]"
# → If Yes: deletes existing, copies again, removes quarantine
# → ✅ Same final state

# This property ensures:
# - Users can retry on failure
# - Automated deployment can re-run safely
# - No accumulation of artifacts or side effects
```

---

## Cleanup & Rollback

**Partial Installation Cleanup**: If process fails after copying but before verification:

- Remaining partial app bundle in `/Applications/` may be left
- Not ideal, but non-critical (user can manually delete)
- Next run will detect and ask to replace

**Recommended Enhancement** (Phase 2):

```bash
trap 'cleanup_partial_install' EXIT
cleanup_partial_install() {
    if [[ -d "$dest_app_path" && "$installation_complete" != "true" ]]; then
        rm -rf "$dest_app_path"
        echo "Removed partial installation"
    fi
}
```
