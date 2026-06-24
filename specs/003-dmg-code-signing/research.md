# Research: DMG Code Signing & Notarization

## Background

### macOS Gatekeeper System

Gatekeeper is macOS's security technology that prevents execution of unsigned or untrusted code. It has evolved across macOS versions:

- **macOS 10.5 (Leopard)**: Original Gatekeeper introduced
- **macOS 10.15 (Catalina)**: Notarization requirement introduced
- **macOS 12 (Monterey)**: Stricter enforcement on unsigned code
- **macOS 13+ (Ventura/Sonoma)**: Developer ID requirement for distribution

### DMG vs App Signing

**App Bundle Signing**:

- Protects the `.app` directory structure
- Validates file integrity within bundle
- Gatekeeper checks when launching app
- Issue we fixed in feature 002 (quarantine removal)

**DMG File Signing**:

- Protects the disk image container itself
- Validates integrity of distribution package
- Gatekeeper checks when mounting/opening DMG
- Current issue: DMG is unsigned

### Code Signing Infrastructure

#### Certificates

```
Apple Developer ID Application Certificate:
- Used for: Signing applications outside Mac App Store
- Validity: 1 year (annual renewal)
- Cost: $99/year Apple Developer membership
- Identity format: "Developer ID Application: Company Name (ABC1234567)"
```

#### Tools

- **codesign**: Signs binaries/bundles/DMG (Xcode CLI)
- **security**: Manages keychains and certificates
- **xcrun notarytool**: Submits to Apple's notarization service
- **xcrun stapler**: Attaches notarization approval to DMG

#### Entitlements

XML plist file specifying app capabilities and permissions. For DMG, typically minimal:

```xml
<dict>
  <key>com.apple.security.cs.allow-dyld-environment-variables</key>
  <true/>
  <!-- Allow for development/testing scenarios -->
</dict>
```

---

## Current Implementation Gap

### Build Process Flow (Current)

```
1. PyInstaller bundles Python app → IntervalsICU.app
2. create-dmg creates DMG volume
3. Copies files to DMG
4. Finalizes DMG (no signing)
   ❌ Result: Unsigned DMG causes Gatekeeper warning
```

### What's Needed

```
1. PyInstaller bundles Python app → IntervalsICU.app
2. create-dmg creates DMG volume
3. Copies files to DMG
4. Sign app bundle (if cert available)
5. Finalize DMG
6. ✅ Sign DMG with certificate
7. (Optional) Submit to notarization service
8. (Optional) Staple notarization approval
```

---

## Signing Implementation Approaches

### Approach 1: Development Builds (Ad-hoc)

```bash
codesign -s - dist/macos/IntervalsICU-1.0.0.dmg
# Creates self-signed ad-hoc signature
# ⚠️ Still shows Gatekeeper warning (expected for dev)
# ✅ Useful for local testing
```

**Pros**: No certificate needed
**Cons**: Still triggers Gatekeeper warning

### Approach 2: Production with Developer ID

```bash
codesign -s "Developer ID Application: Kyle Mabry (ABC1234567)" \
  --entitlements entitlements-dmg.plist \
  dist/macos/IntervalsICU-1.0.0.dmg

# Verify signature
codesign -v dist/macos/IntervalsICU-1.0.0.dmg
```

**Pros**: Passes Gatekeeper check (no warning)
**Cons**: Requires Developer ID certificate

### Approach 3: Production with Notarization (Recommended)

```bash
# 1. Sign
codesign -s "Developer ID Application: ..." dist/macos/IntervalsICU-1.0.0.dmg

# 2. Submit to Apple
xcrun notarytool submit dist/macos/IntervalsICU-1.0.0.dmg \
  --apple-id "user@example.com" \
  --team-id "ABC1234567" \
  --password "app-specific-password"

# 3. Poll for approval
xcrun notarytool log <submission-id> \
  --apple-id "user@example.com" \
  --team-id "ABC1234567" \
  --password "app-specific-password"

# 4. Staple approval
xcrun stapler staple dist/macos/IntervalsICU-1.0.0.dmg

# ✅ Result: DMG verified by Apple, no warning on any Mac
```

**Pros**: Apple-verified, no warnings on any Mac
**Cons**: Takes 5-15 minutes, requires credentials

---

## Certificate Setup for Development

### Option A: Use Apple Developer Account

1. Log in to developer.apple.com
2. Certificates, Identifiers & Profiles → Certificates
3. Create "Developer ID Application" certificate
4. Download to local machine
5. Double-click to import to Keychain

### Option B: Auto-detection (Our Approach)

```bash
# List available Developer ID certs
security find-identity -v -p codesigning

# Output example:
#  1) A1B2C3D4E5F6... "Developer ID Application: Kyle Mabry (ABC1234567)"
#  2) F6E5D4C3B2A1... "Developer ID Application: Company (XYZ9876543)"

# Use specific cert
codesign -s "Developer ID Application: Kyle Mabry (ABC1234567)" ...
```

---

## Notarization Credentials

### Apple ID + Team ID + App-Specific Password

**Why App-Specific Password?**

- More secure than account password
- Can be revoked individually
- Doesn't grant full account access
- Generated in Apple ID settings

**Setup Steps:**

1. Go to appleid.apple.com → Security
2. App passwords section → "Generate password"
3. Select "macOS" and "Other (specify): notarization-tool"
4. Copy generated password
5. Store in CI/CD secrets or local `.env`

```bash
# Usage
xcrun notarytool submit file.dmg \
  --apple-id "dev@company.com" \
  --team-id "ABC1234567" \
  --password "xxxx-xxxx-xxxx-xxxx"
```

---

## Error Handling

### Common Signing Errors

| Error                                            | Cause                          | Fix                                 |
| ------------------------------------------------ | ------------------------------ | ----------------------------------- |
| `The identity [...] cannot be found`             | Cert not in Keychain           | Import certificate via Keychain     |
| `Code object is not signed at all`               | Signing failed silently        | Check disk space, file permissions  |
| `Unsealed contents present in the bundle`        | Bundle structure issue         | Rebuild app bundle with PyInstaller |
| `The signature does not match the received data` | DMG was modified after signing | Re-sign or rebuild                  |

### Common Notarization Errors

| Error                      | Cause                             | Fix                                      |
| -------------------------- | --------------------------------- | ---------------------------------------- |
| `Invalid credentials`      | Wrong Apple ID or password        | Verify credentials in settings           |
| `Notarization rejected`    | Malware detected (false positive) | Contact Apple Support with submission ID |
| `Team ID mismatch`         | Cert doesn't match team           | Use correct certificate identity         |
| `Invalid hardened runtime` | App needs entitlements            | Update entitlements plist                |

---

## Performance Considerations

### Build Time Impact

- Signing DMG: ~1-2 seconds (negligible)
- Notarization: ~5-15 minutes (significant, but async)
- Total dev build: +2 seconds (if skipping notarization)
- Total production build: +10 minutes (with notarization)

### Recommendations

1. Always sign (adds negligible overhead)
2. Notarization only for release builds (use CI/CD)
3. Development builds: Ad-hoc signature or skip entirely

---

## Tools & Versions

| Tool                     | Version                | Status                      |
| ------------------------ | ---------------------- | --------------------------- |
| Xcode Command Line Tools | 14.0+                  | Required                    |
| codesign                 | bundled with Xcode     | Required                    |
| xcrun                    | bundled with Xcode     | Required (for notarization) |
| stapler                  | bundled with Xcode 13+ | Required (for notarization) |
| create-dmg               | 1.3.3                  | Already in use              |

**Installation Check:**

```bash
xcrun --version
# Expected: xcrun version 2371 or higher

security find-identity
# Lists available certificates
```

---

## Security Implications

### What Signing Provides

✅ **Integrity Verification** — DMG not tampered with
✅ **Publisher Identification** — Users know who created it
✅ **Gatekeeper Bypass** — No quarantine warnings
✅ **Revocation Capability** — Invalid cert can be revoked

### What Signing Does NOT Provide

❌ **Content Inspection** — No malware scanning
❌ **Notarization Requirement** — For that, use Apple Notary Service
❌ **User Verification** — Users still need to trust publisher

### Notarization Security

- Apple scans for known malware patterns
- Additional layer of protection vs just signing
- Stapled approval valid offline
- Can be revoked if malware discovered

---

## References

- [Apple Developer: Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/)
- [notarytool Documentation](https://developer.apple.com/documentation/notaryapi)
- [Gatekeeper and runtime protection](https://support.apple.com/en-us/HT202491)
- [Creating Developer ID Certificates](https://developer.apple.com/developer-id/)
