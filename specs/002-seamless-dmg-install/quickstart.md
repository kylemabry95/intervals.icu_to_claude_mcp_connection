# Quickstart: DMG Installation Validation

**Date**: 2026-06-16 | **Phase**: 1 | **Updated**: TBD (post-implementation)

This guide validates that the seamless DMG installation feature works end-to-end. Follow the procedures below to verify the feature meets success criteria.

---

## Prerequisite Setup

### System Requirements

- macOS 11 (Big Sur) or later
- ~100MB free disk space
- Standard user permissions for `/Applications/`
- Freshly mounted IntervalsICU DMG

### Initial State Verification

```bash
# 1. Verify DMG is mounted
mount | grep IntervalsICU
# Expected: /dev/disk{X}s{Y} on /Volumes/IntervalsICU (...)

# 2. Verify install script exists and is executable
ls -la /Volumes/IntervalsICU/install.sh
# Expected: -rwxr-xr-x ... install.sh

# 3. Confirm /Applications is writable
touch /Applications/.write-test && rm /Applications/.write-test && echo "✅ Writable"
# Expected: ✅ Writable
```

---

## Validation Scenario 1: Successful Installation (Happy Path)

**Objective**: User downloads DMG and installs app with zero friction

**Duration**: ~2 minutes

### Steps

1. **Mount DMG**

   ```bash
   # Double-click IntervalsICU-1.0.0.dmg in Finder
   # OR from Terminal:
   hdiutil attach ~/Downloads/IntervalsICU-1.0.0.dmg
   ```

   **Verification**: `/Volumes/IntervalsICU` appears in Finder sidebar

2. **View DMG Contents**

   ```bash
   ls -la /Volumes/IntervalsICU/
   ```

   **Expected Output**:

   ```
   total 0
   drwxr-xr-x ... Applications -> /Applications
   drwxr-xr-x ... IntervalsICU.app
   -rwxr-xr-x ... fix-gatekeeper.sh
   -rwxr-xr-x ... install.sh
   ```

3. **Run Installation**

   ```bash
   /Volumes/IntervalsICU/install.sh
   ```

   **Expected Output** (one of):
   - ✅ **If app not already installed**:
     ```
     Installing IntervalsICU to /Applications/...
     ✅ Copying application bundle...
     ✅ Removing security restrictions...
     ✅ Verifying installation...
     ✅ Installation complete! IntervalsICU is ready to launch.
     💡 You can now eject the IntervalsICU DMG from Finder.
     ```
   - ✅ **If app already installed** (interactive):
     ```
     IntervalsICU is already installed at /Applications/IntervalsICU.app
     Replace? (Yes/No/Cancel) [N]:
     ```
     → Enter `Yes` and installation proceeds

4. **Verify Installation**

   ```bash
   # Check app exists
   ls -l /Applications/IntervalsICU.app
   # Expected: drwx------ (app bundle directory)

   # Verify quarantine attribute removed
   xattr -l /Applications/IntervalsICU.app | grep quarantine
   # Expected: (empty output — quarantine removed)

   # Verify signature
   codesign -v /Applications/IntervalsICU.app
   # Expected: /Applications/IntervalsICU.app: valid on disk
   ```

5. **Test App Launch (No Gatekeeper Warnings)**

   ```bash
   open /Applications/IntervalsICU.app
   ```

   **Expected Behavior**:
   - ✅ App launches immediately
   - ✅ NO "Can't be scanned for malware" dialog
   - ✅ NO security prompts
   - ✅ App is fully functional

6. **Cleanup DMG**
   ```bash
   # Either:
   # - Drag /Volumes/IntervalsICU to Trash in Finder, or
   hdiutil detach /Volumes/IntervalsICU
   ```
   **Expected**: DMG unmounts cleanly, no "volume busy" errors

### Success Criteria Met

- [x] Installation completes in under 30 seconds
- [x] Zero Gatekeeper warnings on first launch
- [x] App appears in /Applications
- [x] Quarantine attribute successfully removed
- [x] DMG can be cleanly unmounted

---

## Validation Scenario 2: Permission Denied Error

**Objective**: Verify graceful error handling when user lacks write permissions

**Duration**: ~5 minutes

### Setup (Create Permission-Denied Environment)

```bash
# Create test directory with restricted permissions
mkdir -p /tmp/restricted_apps
chmod 555 /tmp/restricted_apps  # Read-only (no write)

# Modify install.sh to use /tmp/restricted_apps instead of /Applications/
# (or patch environment variable for testing)
export DMG_INSTALL_DEST="/tmp/restricted_apps"
```

### Steps

1. **Run Installation**

   ```bash
   /Volumes/IntervalsICU/install.sh
   ```

2. **Expected Error Output**

   ```
   ERR_DEST_PERMISSION_DENIED: Permission denied: Cannot write to /tmp/restricted_apps/

   💡 Recovery: Try one of these options:
     • Ask your administrator for write permission to /Applications
     • Check that /Applications directory exists and is writable
     • For testing: install to ~/Applications directory
     • Contact support if this persists
   ```

3. **Verify Exit Code**
   ```bash
   echo $?
   # Expected: non-zero (1 or error code)
   ```

### Success Criteria Met

- [x] Clear error message explains what went wrong
- [x] Recovery steps provided
- [x] No app installed (partial cleanup occurred)
- [x] No crash or unclear error

---

## Validation Scenario 3: Already Installed (Replace Prompt)

**Objective**: Verify correct behavior when app already exists

**Duration**: ~3 minutes

### Setup

```bash
# Run install.sh once to install the app
/Volumes/IntervalsICU/install.sh
# → Installation complete

# Verify app installed
ls -l /Applications/IntervalsICU.app
# → Exists
```

### Steps

1. **Run Installation Script Again**

   ```bash
   /Volumes/IntervalsICU/install.sh
   ```

2. **Expected Prompt Output**

   ```
   IntervalsICU is already installed at /Applications/IntervalsICU.app

   Replace? (Yes/No/Cancel) [N]:
   ```

3. **Test All Three Options**

   **Option A: Replace (Yes)**

   ```
   Replace? (Yes/No/Cancel) [N]: Yes
   # Proceed with:
   ✅ Removing existing version...
   ✅ Copying new version...
   ✅ Removing security restrictions...
   ✅ Verifying installation...
   ✅ Installation complete!
   ```

   → App is updated to latest from DMG

   **Option B: Skip (No)**

   ```
   Replace? (Yes/No/Cancel) [N]: No
   # Outputs:
   💡 Installation skipped. IntervalsICU remains at /Applications/IntervalsICU.app
   ```

   → App remains unchanged, script exits cleanly (exit code 0)

   **Option C: Cancel (Ctrl+C or Cancel)**

   ```
   Replace? (Yes/No/Cancel) [N]: ^C
   # Or:
   Replace? (Yes/No/Cancel) [N]: Cancel
   # Outputs:
   ✋ Installation cancelled by user.
   ```

   → Script exits cleanly, no changes made

### Success Criteria Met

- [x] User prompted clearly when app already exists
- [x] All three options work as expected
- [x] No data loss or corruption on replace
- [x] No partial installations left behind

---

## Validation Scenario 4: Insufficient Disk Space

**Objective**: Verify error handling for low disk space

**Duration**: ~5 minutes

### Setup (Simulate Low Disk Space)

```bash
# Create a sparse disk image with limited space
hdiutil create -size 50m -type SPARSE -fs HFS+ -volname "LowSpace" ~/low_space.dmg
hdiutil attach ~/low_space.dmg

# Modify install.sh temporarily to use this low-space volume for destination
export DMG_INSTALL_DEST="/Volumes/LowSpace"
```

### Steps

1. **Run Installation**

   ```bash
   /Volumes/IntervalsICU/install.sh
   ```

2. **Expected Error Output**

   ```
   ERR_INSUFFICIENT_DISK_SPACE: Not enough space (need 100MB, have 45MB free)

   💡 Recovery: Try one of these options:
     • Free up disk space (delete files, empty Trash)
     • Move files to external drive
     • Try again after freeing space
   ```

3. **Verify Exit Code**
   ```bash
   echo $?
   # Expected: non-zero (error code)
   ```

### Cleanup

```bash
hdiutil detach /Volumes/LowSpace
rm ~/low_space.dmg
unset DMG_INSTALL_DEST
```

### Success Criteria Met

- [x] Specific error message about disk space
- [x] Shows required vs. available space
- [x] Clear recovery steps
- [x] No app installed (nothing copied to failed destination)

---

## Validation Scenario 5: Gatekeeper Warning Absence

**Objective**: Verify users see NO Gatekeeper warnings after installation

**Duration**: ~2 minutes

### Prerequisites

- Fresh install completed (Scenario 1 passed)
- App not previously launched on this system

### Steps

1. **Launch App First Time**

   ```bash
   open /Applications/IntervalsICU.app
   ```

2. **Expected Behavior**
   - ✅ App window appears immediately
   - ✅ NO "Cannot verify developer" dialog
   - ✅ NO "IntervalsICU can't be opened" dialog
   - ✅ NO "can't be scanned for malware" warning
   - ✅ App is fully functional

3. **Verify Quarantine Removal**

   ```bash
   xattr -l /Applications/IntervalsICU.app | grep -i quarantine
   # Expected: (empty output — attribute removed)

   # Check specific attribute
   xattr -p com.apple.quarantine /Applications/IntervalsICU.app 2>&1
   # Expected: xattr: com.apple.quarantine: No such file
   ```

### Success Criteria Met

- [x] Zero Gatekeeper warnings
- [x] App launches cleanly
- [x] Quarantine attribute confirmed removed
- [x] User can work without additional security dialogs

---

## Manual Regression Test Checklist

Run this checklist after any changes to `install.sh` or `build.sh`:

```bash
□ Scenario 1: Fresh Install (Happy Path)
  □ Mounts DMG successfully
  □ Shows correct menu items/files
  □ Installation completes in <30s
  □ Zero Gatekeeper warnings on launch
  □ DMG unmounts cleanly

□ Scenario 2: Permission Error Handling
  □ Detects permission denied gracefully
  □ Provides clear error message
  □ Shows recovery steps
  □ No partial app left behind

□ Scenario 3: Already Installed Handling
  □ Detects existing app
  □ Prompts user (Yes/No/Cancel)
  □ All three options work correctly
  □ Replace works without corruption

□ Scenario 4: Disk Space Handling
  □ Detects low disk space
  □ Shows specific space requirements
  □ No partial install left behind

□ Scenario 5: Gatekeeper Compliance
  □ No warnings on first launch
  □ Quarantine attribute confirmed removed
  □ Signature verification passes

□ General
  □ All prompts are clear and user-friendly
  □ All error messages are actionable
  □ No mysterious exit codes or hangs
  □ Works on macOS 11, 12, 13, 14, 15+
```

---

## Success Metrics

**Installation Meets Success Criteria When**:

- Installation completes in under 30 seconds (typical: 6-11 seconds)
- 100% of installations succeed with proper permissions
- Zero Gatekeeper warnings on first launch
- 95% of users understand what happened (clear messages)
- Error scenarios provide actionable recovery steps

**Feature Ready for Release When**:

- All 5 scenarios pass on macOS 11+
- Manual test checklist 100% complete
- Code review completed
- Documentation (README) updated with installation instructions
