# Contract: DMG Code Signing Implementation

**Applies to**: `packaging/macos/build.sh` and `packaging/macos/entitlements-dmg.plist`  
**Ownership**: Build Pipeline & Security  
**Status**: Specification → Implementation

---

## Interface Contract

### build.sh Signing Workflow

#### Function: `detect_signing_certificate()`

**Responsibility**: Locate available Developer ID certificates in system Keychain

**Input**:

- None (reads from system Keychain via `security` CLI)

**Process**:

```bash
# List all Developer ID Application certificates
security find-identity -v -p codesigning | grep "Developer ID Application"
```

**Output**:

```bash
# Zero certificates found:
exit 1  # with error message

# One certificate found:
export SIGNING_IDENTITY="Developer ID Application: Kyle Mabry (ABC1234567)"
return 0

# Multiple certificates found:
# Prompt user to select (interactive menu)
# export SIGNING_IDENTITY="<user choice>"
return 0
```

**Error Handling**:

```
1001: Certificate not found (exit 1001)
4001: Multiple certificates found (prompt user, continue)
```

**Contract Guarantees**:

- ✓ If successful, `$SIGNING_IDENTITY` is set to valid certificate
- ✓ If error, exit code signals reason
- ✓ Non-blocking for dev builds (can use ad-hoc fallback)

---

#### Function: `sign_dmg(dmg_path, signing_identity, entitlements_path)`

**Responsibility**: Sign DMG file with provided certificate and entitlements

**Input**:

```bash
dmg_path="dist/macos/IntervalsICU-1.0.0.dmg"
signing_identity="Developer ID Application: Kyle Mabry (ABC1234567)"
entitlements_path="packaging/macos/entitlements-dmg.plist"
```

**Process**:

```bash
codesign -s "$signing_identity" \
  --entitlements "$entitlements_path" \
  --deep \
  --force \
  --options runtime \
  "$dmg_path"
```

**Output**:

```bash
# Success:
return 0

# Failure:
exit 2001  # General signing error
exit 2002  # File not found
exit 2003  # Permission denied
exit 2004  # Insufficient disk space
```

**Verification**:

```bash
codesign -v "$dmg_path"
# Returns: "$dmg_path: valid on disk"
```

**Contract Guarantees**:

- ✓ DMG is signed with specified identity
- ✓ Entitlements are embedded in signature
- ✓ Signature valid after completion (verified)
- ✓ File integrity preserved

---

#### Function: `verify_signature(dmg_path)`

**Responsibility**: Validate code signature on DMG

**Input**:

```bash
dmg_path="dist/macos/IntervalsICU-1.0.0.dmg"
```

**Process**:

```bash
codesign -v "$dmg_path" 2>&1 | grep -q "valid on disk"
```

**Output**:

```bash
# Signature valid:
return 0
output: "✓ Signature valid: $dmg_path"

# Signature invalid or missing:
exit 2005  # Signature validation failed
output: "✗ Signature invalid or missing"
```

**Contract Guarantees**:

- ✓ Returns definitive true/false on signature status
- ✓ Clear error message if invalid
- ✓ Non-blocking (doesn't prevent deployment)

---

#### Function: `notarize_dmg(dmg_path, apple_id, team_id, password)`

**Responsibility**: Submit DMG to Apple Notary Service and wait for approval

**Input**:

```bash
dmg_path="dist/macos/IntervalsICU-1.0.0.dmg"
apple_id="dev@example.com"
team_id="ABC1234567"
password="xxxx-xxxx-xxxx-xxxx"  # app-specific
```

**Process**:

```bash
# 1. Submit to notarization service
submission_id=$(xcrun notarytool submit "$dmg_path" \
  --apple-id "$apple_id" \
  --team-id "$team_id" \
  --password "$password" \
  --wait \
  2>&1 | grep "id:" | awk '{print $2}')

# 2. Poll until approved (--wait handles this)
# Polling interval: 10 seconds
# Max wait: 30 minutes
# Returns when approved or rejected
```

**Output**:

```bash
# Approved:
return 0
export NOTARIZATION_ID="uuid-from-service"
output: "✓ Notarization approved: $submission_id"

# Rejected:
exit 3004  # Notarization rejected
output: "✗ Notarization rejected. Review logs for details."

# Timeout:
exit 3005  # Notarization timeout
output: "✗ Notarization timed out after 30 minutes."

# Invalid credentials:
exit 3002  # Invalid credentials
output: "✗ Invalid Apple ID or password."
```

**Contract Guarantees**:

- ✓ If approved, `$NOTARIZATION_ID` is set for stapling
- ✓ If rejected, Apple's feedback provided
- ✓ Non-blocking failure (can retry manually)
- ✓ Comprehensive logging for troubleshooting

---

#### Function: `staple_notarization(dmg_path, notarization_id)`

**Responsibility**: Attach Apple's notarization approval to DMG (for offline validation)

**Input**:

```bash
dmg_path="dist/macos/IntervalsICU-1.0.0.dmg"
notarization_id="uuid-from-service"
```

**Process**:

```bash
xcrun stapler staple "$dmg_path"
```

**Output**:

```bash
# Success:
return 0
output: "✓ Notarization stapled to $dmg_path"

# Failure:
exit 3006  # Stapling failed
output: "✗ Failed to staple notarization."
```

**Contract Guarantees**:

- ✓ Notarization approval is attached to DMG
- ✓ DMG can now be verified offline (no internet needed)
- ✓ File remains mountable and intact

---

### build.sh Interface Changes

#### New Flags

```bash
./packaging/macos/build.sh [options]

--sign <identity>
  Code signing identity for production builds
  Example: --sign "Developer ID Application: Kyle Mabry (ABC1234567)"
  Default: Auto-detect; fallback to ad-hoc if unavailable

--notarize
  Enable Apple notarization workflow
  Requires: Environment variables APPLE_ID, APPLE_TEAM_ID, APPLE_NOTARY_PWD
  Duration: +5-15 minutes
  Default: Disabled (for development builds)

--verbose
  Show detailed signing/notarization output
  Default: Disabled (show summary only)

--version <version>
  DMG version (existing flag, used with signing)
```

#### Configuration via Environment Variables

```bash
# For production/CI builds, set before running:
export APPLE_ID="dev@company.com"
export APPLE_TEAM_ID="ABC1234567"
export APPLE_NOTARY_PWD="xxxx-xxxx-xxxx-xxxx"

# Then run:
./packaging/macos/build.sh --version 1.0.0 --sign "Developer ID Application: ..." --notarize
```

#### Output Examples

**Development Build (ad-hoc, no notarization)**:

```
✓ Building IntervalsICU app...
✓ Creating DMG volume...
✓ Copying files to DMG...
✓ Signing DMG with ad-hoc signature...
⚠ Warning: Using ad-hoc signature. For production: --sign <identity>
✓ DMG created: dist/macos/IntervalsICU-1.0.0.dmg (33 MB)
ℹ Development build complete. Note: DMG will show Gatekeeper warning.
```

**Production Build (Developer ID, with notarization)**:

```
✓ Building IntervalsICU app...
✓ Creating DMG volume...
✓ Copying files to DMG...
✓ Detected certificate: Developer ID Application: Kyle Mabry (ABC1234567)
✓ Loading entitlements: packaging/macos/entitlements-dmg.plist
✓ Signing DMG with Developer ID...
✓ Verifying signature...
✓ Submitting to Apple Notary Service...
⏳ Notarization in progress (this may take 5-15 minutes)...
✓ Notarization approved! ID: a1b2c3d4-e5f6...
✓ Stapling notarization to DMG...
✓ DMG created: dist/macos/IntervalsICU-1.0.0.dmg (33 MB)
✓ Production build complete. Users will see zero Gatekeeper warnings.
```

---

## Entitlements Contract

### entitlements-dmg.plist Structure

**Responsibility**: Define minimal permissions required for DMG operations

**Content**:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <!-- Allows dynamic library loading with environment variables -->
  <key>com.apple.security.cs.allow-dyld-environment-variables</key>
  <true/>

  <!-- Allows execution of unsigned in-memory code -->
  <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
  <true/>

  <!-- Deny all privacy-sensitive operations -->
  <key>com.apple.security.device.microphone</key>
  <false/>

  <key>com.apple.security.device.camera</key>
  <false/>

  <key>com.apple.security.personal-information.photos-library</key>
  <false/>

  <key>com.apple.security.personal-information.contacts</key>
  <false/>

  <key>com.apple.security.personal-information.calendars</key>
  <false/>

  <key>com.apple.security.personal-information.reminders</key>
  <false/>

  <key>com.apple.security.personal-information.location</key>
  <false/>
</dict>
</plist>
```

**Contract Guarantees**:

- ✓ Minimal permissions required for distribution
- ✓ Security-focused: All sensors/privacy data denied
- ✓ Compatible with Gatekeeper validation
- ✓ Accepted by Apple notarization

---

## Error Handling Contract

### Exit Code Framework

```
0     Success
1xxx  Certificate errors
2xxx  Signing errors
3xxx  Notarization errors
4xxx  Non-blocking warnings
```

### Recovery Guidance

```bash
# Error 1001: Certificate not found
→ Install Developer ID Certificate
→ Go to developer.apple.com → Certificates
→ Create "Developer ID Application" certificate
→ Download and double-click to import to Keychain
→ Or run with --sign <identity> explicitly

# Error 2001: Signing failed
→ Check disk space: df -h
→ Check file permissions: stat dist/macos/*.dmg
→ Verify certificate is valid: security find-identity
→ Try again or contact support with error logs

# Error 3002: Invalid credentials
→ Verify APPLE_ID, APPLE_TEAM_ID, APPLE_NOTARY_PWD are correct
→ Generate new app-specific password at appleid.apple.com
→ Retry notarization

# Error 3004: Notarization rejected
→ Review Apple's rejection logs
→ Common cause: Malware signature false positive
→ Contact Apple Developer Support with submission ID
```

---

## Integration Points

### Integration with feature 002 (Seamless DMG Installation)

**Current State**:

- install.sh removes quarantine from app bundle ✓
- Eliminates app-level Gatekeeper warnings ✓

**New Enhancement (this feature)**:

- build.sh signs DMG ← PREVENTS DMG-level warning
- Users see zero warnings throughout entire flow ✓

**Combined Flow**:

```
1. User downloads signed DMG                    ← No Gatekeeper warning
2. Mount DMG                                    ← No Gatekeeper warning
3. Run install.sh                               ← Script signed/verified
4. install.sh removes quarantine from app       ← Extra safety measure
5. App launches                                 ← No Gatekeeper warning
✅ Seamless experience maintained
```

### Integration with CI/CD

**GitHub Actions Workflow** (future Phase 3):

```yaml
- name: Sign and Notarize DMG
  env:
    APPLE_ID: ${{ secrets.APPLE_ID }}
    APPLE_TEAM_ID: ${{ secrets.APPLE_TEAM_ID }}
    APPLE_NOTARY_PWD: ${{ secrets.APPLE_NOTARY_PWD }}
  run: |
    ./packaging/macos/build.sh --version 1.0.0 \
      --sign "Developer ID Application: ..." \
      --notarize
```

---

## Testing Contract

### Unit Tests

- Certificate detection returns valid identity or error code
- Signing produces valid signature (codesign -v passes)
- Entitlements XML is valid and readable
- Error codes match documentation

### Integration Tests

- Sign mock DMG and verify signature persists after copy
- Mount signed DMG and verify contents integrity
- Run install.sh from signed DMG
- Verify installed app signature

### End-to-End Tests

- Fresh system: Mount signed DMG, no Gatekeeper warning
- Install app from DMG: No warnings
- Launch app: No warnings
- Verify signature chain: codesign -vvv shows full chain

---

## Versioning & Compatibility

### Supported Platforms

- macOS 11 (Big Sur) and later
- Xcode Command Line Tools 13.0+
- arm64 (Apple Silicon) and x86_64 (Intel)

### Backward Compatibility

- Unsigned DMGs still work (with warning) — no breaking changes
- Existing install.sh compatible with signed DMG
- No changes to app bundle structure

### Certificate Expiration

- Developer ID certs valid for 1 year
- Renewal reminder should be added to CI/CD monitoring
- Build fails gracefully if cert expired

---

## Non-Functional Requirements

### Performance

- Signing: 1-2 seconds (negligible)
- Notarization: 5-15 minutes (async, acceptable)
- Verification: <1 second

### Reliability

- Signing: 99.9% success rate (system dependent)
- Notarization: 99% approval rate (if no malware detected)
- Fallback: Ad-hoc signing available for dev builds

### Security

- Private key never exposed (stays in Keychain)
- Passwords stored in CI/CD secrets, not in code
- Signed code immutable (changes break signature)

### Maintainability

- All operations logged for audit trail
- Clear error messages for troubleshooting
- Documentation links in error output
