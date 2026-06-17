# DMG Integration Contract

**Date**: 2026-06-16 | **Version**: 1.0

## Overview

This contract defines how the installation automation is integrated into the DMG build process. It describes changes to `packaging/macos/build.sh` and the DMG contents that enable seamless installation.

---

## DMG Contents Contract

### Required Structure

```
IntervalsICU-1.0.0.dmg (mounted to /Volumes/IntervalsICU/)
├── IntervalsICU.app/                  # App bundle (signed, ~50MB)
├── install.sh                         # Installation automation script (NEW)
├── fix-gatekeeper.sh                  # Gatekeeper quarantine helper (EXISTING)
├── Applications -> /Applications      # Convenience symlink (EXISTING)
└── .DS_Store                          # Finder view settings
```

### File Specifications

| File                | Type         | Size   | Owner | Permissions      | Purpose                                    |
| ------------------- | ------------ | ------ | ----- | ---------------- | ------------------------------------------ |
| `IntervalsICU.app/` | Directory    | ~50MB  | root  | 755              | Main application bundle                    |
| `install.sh`        | Shell Script | ~3-5KB | root  | 755 (executable) | Installation automation                    |
| `fix-gatekeeper.sh` | Shell Script | ~1KB   | root  | 755 (executable) | Manual quarantine removal                  |
| `Applications`      | Symlink      | N/A    | root  | 755              | Visual convenience to /Applications folder |
| `.DS_Store`         | Metadata     | ~10KB  | root  | 644              | Finder layout (optional, for UX)           |

---

## Build Script Integration

### Changes to `packaging/macos/build.sh`

**Current Behavior** (before this feature):

```bash
create-dmg \
    --volname "${APP_NAME} ${VERSION}" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "${APP_NAME}.app" 175 190 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 425 190 \
    "${DMG_PATH}" \
    "${DIST_DIR}/"
```

**Required Changes** (new behavior):

1. **Copy `install.sh` into dist directory before DMG creation**

   ```bash
   # Add this section BEFORE create-dmg call:
   echo "📋 Adding installation script to DMG..."
   cp "packaging/macos/install.sh" "${DIST_DIR}/" || {
       echo "❌ Failed to copy install.sh to dist directory"
       exit 1
   }
   chmod +x "${DIST_DIR}/install.sh"
   ```

2. **Update `create-dmg` call to include new files**

   ```bash
   # Ensure create-dmg includes all files in ${DIST_DIR}/
   # The create-dmg script will automatically include:
   # - IntervalsICU.app
   # - install.sh (if in DIST_DIR before create-dmg)
   # - fix-gatekeeper.sh (already there)
   # - Applications symlink (already there)
   ```

3. **Add symlink creation (if not present)**
   ```bash
   # Create Applications convenience symlink
   ln -sf /Applications "${DIST_DIR}/Applications" 2>/dev/null || true
   ```

### Integration Points

**Location in build.sh**: Add new steps ~20 lines before `create-dmg` invocation

**Existing Dependencies**:

- `${DIST_DIR}` — distribution directory where .app bundle already exists
- `create-dmg` — DMG creation tool (already used)
- `chmod` — make scripts executable (standard Unix)

**No Breaking Changes**: This adds new files to DMG; doesn't modify existing build process

---

## Installation Script Specification

### File Location in Repository

```
packaging/macos/
├── build.sh           (MODIFY: add install.sh copy logic)
├── install.sh         (CREATE: new installation automation)
├── fix-gatekeeper.sh  (existing)
└── entitlements.plist (existing)
```

### Script Template Requirements

The `install.sh` script must:

1. **Detect source app bundle**

   ```bash
   SOURCE_APP="/Volumes/IntervalsICU/IntervalsICU.app"
   if [[ ! -d "$SOURCE_APP" ]]; then
       echo "ERR_SOURCE_NOT_FOUND: Cannot find $SOURCE_APP"
       exit 3
   fi
   ```

2. **Check destination permissions**

   ```bash
   DEST_DIR="/Applications"
   if [[ ! -w "$DEST_DIR" ]]; then
       echo "ERR_DEST_PERMISSION_DENIED: Cannot write to $DEST_DIR"
       # Show recovery steps...
       exit 4
   fi
   ```

3. **Copy app bundle**

   ```bash
   cp -r "$SOURCE_APP" "$DEST_DIR/" || {
       echo "ERR_COPY_FAILED: Failed to copy app bundle"
       exit 1
   }
   ```

4. **Remove quarantine attribute**

   ```bash
   xattr -rd com.apple.quarantine "$DEST_APP" || {
       echo "⚠️ Warning: Could not remove quarantine (may already be cleared)"
   }
   ```

5. **Verify installation**

   ```bash
   codesign -v "$DEST_APP" >/dev/null 2>&1 || {
       echo "⚠️ Warning: Signature verification failed (app may still be usable)"
   }
   ```

6. **Report success**
   ```bash
   echo "✅ Installation complete! IntervalsICU is ready to launch."
   echo "💡 You can now eject the IntervalsICU DMG from Finder."
   exit 0
   ```

---

## User Discovery Contract

### Discoverability

When user opens DMG in Finder:

**Expected UI**:

- Finder window shows 4-5 items:
  - `IntervalsICU.app` (with app icon)
  - `install.sh` (with script icon)
  - `fix-gatekeeper.sh` (with script icon)
  - `Applications` folder icon (symlink to /Applications)

**User's Next Action**:

- **Preferred**: Double-click `install.sh` → installation runs
- **Alternative**: Drag `IntervalsICU.app` to `Applications` folder
- **Advanced**: Open Terminal, run `./install.sh`

### Documentation Integration

DMG should include visual/text cues:

- Finder window background (optional): "Double-click install.sh to install"
- README (optional): Installation instructions

---

## Platform Compatibility

### Minimum macOS Versions

| OS       | Version | Tested | Status       |
| -------- | ------- | ------ | ------------ |
| Big Sur  | 11.x    | Yes    | ✅ Supported |
| Monterey | 12.x    | Yes    | ✅ Supported |
| Ventura  | 13.x    | Yes    | ✅ Supported |
| Sonoma   | 14.x    | Yes    | ✅ Supported |
| Sequoia  | 15.x    | Yes    | ✅ Supported |

### Architecture Support

| Architecture          | Status        | Notes                      |
| --------------------- | ------------- | -------------------------- |
| arm64 (Apple Silicon) | ✅ Supported  | Primary target             |
| Intel x86_64          | ✅ Supported  | Via universal binary build |
| Rosetta 2             | ✅ Compatible | Runs Intel build natively  |

---

## Build Verification

### Pre-Release Checklist

Before creating release DMG:

```bash
□ install.sh exists in packaging/macos/
□ install.sh has proper error handling
□ install.sh is executable (chmod +x applied)
□ build.sh modified to include install.sh in DMG
□ DMG creation tested locally
□ DMG contents verified (ls /Volumes/IntervalsICU/)
□ install.sh permissions preserved in mounted DMG (should be 755)
□ Installation tested end-to-end
```

### Post-Release Verification

After DMG is built:

```bash
# Mount DMG
hdiutil attach dist/macos/IntervalsICU-1.0.0.dmg -mountpoint /tmp/dmg_test

# Verify contents
ls -la /tmp/dmg_test/
# Should show: IntervalsICU.app, install.sh, fix-gatekeeper.sh, Applications

# Verify script is executable
file /tmp/dmg_test/install.sh
# Should show: "Bourne-Again shell script, ASCII text executable"

# Verify permissions
stat -f "%A" /tmp/dmg_test/install.sh
# Should show: "755"

# Unmount
hdiutil detach /tmp/dmg_test
```

---

## Rollback Plan

If installation script causes issues post-release:

1. **Immediate (manual workaround)**:
   - User can drag-drop `IntervalsICU.app` to Applications folder
   - User can run `fix-gatekeeper.sh` manually if needed
   - Feature degrades gracefully to v1.0.0 behavior

2. **Short-term (v1.0.1 hotfix)**:
   - Rebuild DMG with corrected `install.sh`
   - Release new DMG with version bump
   - Announce fix on GitHub releases page

3. **Documentation fallback**:
   - README section "Troubleshooting Installation" with manual steps
   - Link to previous v1.0.0 DMG if critical issues found

---

## Testing Contract

### Integration Testing

Test scenarios from [quickstart.md](../quickstart.md):

1. Fresh install (happy path)
2. Permission denied (error handling)
3. Already installed (replace prompt)
4. Disk space check (error handling)
5. Gatekeeper warning absence (main success criterion)

### Regression Testing

After any changes to build.sh or install.sh:

- [ ] DMG builds successfully
- [ ] All files present in mounted DMG
- [ ] install.sh permissions preserved
- [ ] Installation completes in <30s
- [ ] No Gatekeeper warnings on app launch

---

## Version History

| Version | Date       | Changes                           |
| ------- | ---------- | --------------------------------- |
| 1.0     | 2026-06-16 | Initial contract (Phase 1 design) |
