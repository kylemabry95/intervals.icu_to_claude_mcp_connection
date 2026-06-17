# Installation Script Interface Contract

**Date**: 2026-06-16 | **Version**: 1.0

## Overview

The `install.sh` script is the public interface for users to install IntervalsICU from a mounted DMG. This contract defines the expected behavior, inputs, outputs, and error handling.

---

## Invocation Interface

### Command Line

**Primary Invocation**:

```bash
/Volumes/IntervalsICU/install.sh
```

**Alternative (if user opens Terminal)**:

```bash
bash /Volumes/IntervalsICU/install.sh
```

**With Optional Flags** (for future compatibility):

```bash
/Volumes/IntervalsICU/install.sh --help      # Show usage info
/Volumes/IntervalsICU/install.sh --version   # Show version
/Volumes/IntervalsICU/install.sh --dest ~/Applications  # Custom destination
```

### Prerequisites

- DMG must be mounted (automatic when user opens DMG)
- `/Volumes/IntervalsICU/` mount point must be accessible
- IntervalsICU.app must be present in DMG root
- Bash shell (part of macOS standard tools)

---

## Input Contract

### Environment Variables (Optional)

| Variable              | Type          | Default         | Purpose                                          |
| --------------------- | ------------- | --------------- | ------------------------------------------------ |
| `DMG_INSTALL_DEST`    | Path          | `/Applications` | Override installation destination (testing only) |
| `DMG_INSTALL_VERBOSE` | Boolean (0/1) | `0`             | Enable verbose output (debugging)                |

**Example**:

```bash
DMG_INSTALL_VERBOSE=1 /Volumes/IntervalsICU/install.sh
```

### Command Line Arguments

| Argument        | Type   | Purpose                                           | Example                              |
| --------------- | ------ | ------------------------------------------------- | ------------------------------------ |
| `--help`        | Flag   | Show usage information                            | `./install.sh --help`                |
| `--version`     | Flag   | Display script version                            | `./install.sh --version`             |
| `--dest <path>` | Option | Custom installation destination                   | `./install.sh --dest ~/Applications` |
| `--force`       | Flag   | Skip "already installed" prompt, replace silently | `./install.sh --force`               |

---

## Output Contract

### Standard Output (stdout)

#### Success Messaging

**Informational Messages**:

```
Installing IntervalsICU to /Applications/...
✅ Copying application bundle...
✅ Removing security restrictions...
✅ Verifying installation...
✅ Installation complete! IntervalsICU is ready to launch.
💡 You can now eject the IntervalsICU DMG from Finder.
```

**User Prompts** (when applicable):

```
IntervalsICU is already installed at /Applications/IntervalsICU.app

Replace? (Yes/No/Cancel) [N]:
```

### Standard Error (stderr)

#### Error Messages

**Format**: `{ERROR_CODE}: {description}`

**Examples**:

```
ERR_SOURCE_NOT_FOUND: Source application not found in DMG
ERR_DEST_PERMISSION_DENIED: Permission denied: Cannot write to /Applications/
ERR_INSUFFICIENT_DISK_SPACE: Not enough space (need 100MB, have 45MB free)
ERR_COPY_FAILED: Failed to copy application bundle
ERR_SIGNATURE_INVALID: Signature verification failed
```

#### Recovery Instructions

**Format**: `💡 Recovery: {recovery_steps}`

**Examples**:

```
💡 Recovery: Try one of these options:
  • Ask your administrator for write permission to /Applications
  • For testing: install to ~/Applications directory
  • Contact support if this persists
```

#### Warnings

**Format**: `⚠️ Warning: {description}`

**Examples**:

```
⚠️ Warning: Could not remove Gatekeeper restrictions (may be already cleared)
⚠️ Warning: Could not verify app signature (app may still be usable)
```

---

## Exit Code Contract

| Code | Meaning                          | Recovery                                      |
| ---- | -------------------------------- | --------------------------------------------- |
| `0`  | Success or user-initiated cancel | Check app in /Applications                    |
| `1`  | Generic error (install failed)   | Review error message above                    |
| `2`  | Argument parsing error           | Use `--help` to see valid options             |
| `3`  | Source not found                 | Verify DMG mounted correctly                  |
| `4`  | Destination permission denied    | Check file system permissions                 |
| `5`  | Insufficient disk space          | Free up disk space                            |
| `10` | User cancelled (via prompt)      | Installation was cancelled (no app installed) |

---

## User Experience Contract

### Timing

| Operation                | Expected Duration | Tolerance            |
| ------------------------ | ----------------- | -------------------- |
| Script launch to prompts | <500ms            | ±100ms               |
| File copy (50MB app)     | 5-10s             | Varies by disk speed |
| Quarantine removal       | 100ms             | ±50ms                |
| Total installation       | 6-12s             | <30s target          |

### Prompts & Interaction

**Prompt 1**: "Already Installed" (when app exists)

```
IntervalsICU is already installed at /Applications/IntervalsICU.app

Replace? (Yes/No/Cancel) [N]:
```

- Default: `No` (non-destructive)
- Options: `Yes`, `No`, `Cancel` (or `Y`, `N`, `C`)
- Timeout: None (wait for user input)

**Prompt 2**: Permission Denied (shown if /Applications not writable)

```
ERR_DEST_PERMISSION_DENIED: Cannot write to /Applications/
💡 Recovery: Ask your administrator for write permission...
```

- Non-interactive (no user input required)
- Exit after message

---

## Behavioral Contract

### File Operations

| Operation         | Source                                   | Destination                      | Behavior                           |
| ----------------- | ---------------------------------------- | -------------------------------- | ---------------------------------- |
| Copy App Bundle   | `/Volumes/IntervalsICU/IntervalsICU.app` | `/Applications/IntervalsICU.app` | Recursive copy; preserve structure |
| Remove Quarantine | `/Applications/IntervalsICU.app`         | (in-place)                       | Recursive xattr removal            |
| Verify Signature  | `/Applications/IntervalsICU.app`         | (verification only)              | Non-destructive check              |

### Idempotency

**Property**: Running script multiple times yields same final state.

```bash
# Run 1: Fresh install → Success
./install.sh
# ✅ App installed to /Applications

# Run 2: Same system, already installed → User prompted
./install.sh
# Asks: "Replace? Yes/No/Cancel"
# If Yes → Same final state as Run 1
# If No → No changes made
```

### Non-Destructive Failure

**Property**: Failed installation leaves system in known, safe state.

- If copy fails: No partial app bundle left
- If permission denied: No attempt to copy
- If user cancels: Rollback to last-known-good state

---

## Integration Points

### DMG Build Integration

Script must be:

1. Located at: `/Volumes/IntervalsICU/install.sh`
2. Executable: `chmod +x install.sh` before adding to DMG
3. Discoverable: Listed in DMG root (alongside .app bundle)

### Supporting Files in DMG

Script expects these files to exist in same DMG:

- `IntervalsICU.app/` (required)
- `fix-gatekeeper.sh` (optional, for manual quarantine removal)
- `Applications/` symlink (optional, visual convenience)

---

## Security Contract

### Permissions

- Script runs with user permissions (no `sudo` required)
- Respects file system permissions (does not attempt privilege escalation)
- Does not modify system configuration

### Data Handling

- No credentials collected or transmitted
- No user data read or written (only app bundle copied)
- No telemetry or external communication

### Error Handling

- All errors reported with clear, non-technical messages
- No stack traces or debug data exposed to users
- Recovery guidance provided for common failure scenarios

---

## Testing Contract

### Minimum Test Coverage

- [x] Success case (fresh install)
- [x] Permission denied case
- [x] Already installed case (user replace)
- [x] Disk space error case
- [x] Invalid source case
- [x] Exit codes verified for all scenarios

### Validation Scenarios

Reference: [quickstart.md](../quickstart.md) for full test procedures

---

## Version History

| Version | Date       | Changes                           |
| ------- | ---------- | --------------------------------- |
| 1.0     | 2026-06-16 | Initial contract (Phase 1 design) |
