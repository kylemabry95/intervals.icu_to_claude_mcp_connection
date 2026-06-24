# Quickstart: DMG Code Signing & Notarization Validation

**Feature**: 003-dmg-code-signing  
**Purpose**: Validate the signing and notarization workflow end-to-end before release

This guide documents runnable validation scenarios proving the feature works. It references [contracts/dmg-signing.md](contracts/dmg-signing.md) and [data-model.md](data-model.md) for full technical detail.

---

## Prerequisites

```bash
# 1. Xcode Command Line Tools installed
xcode-select --install
xcrun --version           # Expected: xcrun version 2371+

# 2. create-dmg installed
brew install create-dmg   # or: brew upgrade create-dmg
create-dmg --version      # Expected: 1.3.3+

# 3. On feature branch
git branch                # Expected: * 003-dmg-code-signing

# 4. App builds successfully
./packaging/macos/build.sh --version 1.0.0 --no-sign
# Expected: dist/macos/IntervalsICU-1.0.0.dmg created
```

---

## Scenario 1: Development Build — Ad-hoc Fallback

**Goal**: Verify unsigned builds succeed with prominent warning and setup instructions.

```bash
# Run without --sign flag
./packaging/macos/build.sh --version 1.0.0
```

**Expected output** (key lines):

```
⚠️  WARNING: No Developer ID certificate provided.
    Using ad-hoc signature for development/testing only.
    This DMG will show a Gatekeeper warning on other Macs.

    To eliminate Gatekeeper warnings for distribution:
    1. Enrol at https://developer.apple.com/developer-id/
    2. Create a "Developer ID Application" certificate
    3. Import to Keychain (double-click the .cer file)
    4. Re-run: ./packaging/macos/build.sh --version 1.0.0 \
         --sign "Developer ID Application: Your Name (TEAMID)"

✅ DMG created: dist/macos/IntervalsICU-1.0.0.dmg
```

**Verification**:

```bash
# Ad-hoc signature present (not Developer ID)
codesign -dv dist/macos/IntervalsICU-1.0.0.dmg 2>&1 | grep "Authority"
# Expected: no "Developer ID" authority line (ad-hoc has none)

# Ad-hoc signature valid locally
codesign -v dist/macos/IntervalsICU-1.0.0.dmg && echo "PASS: signature valid"

# App bundle also ad-hoc signed
codesign -dv dist/macos/IntervalsICU.app 2>&1 | grep "Signature"
# Expected: Signature=adhoc
```

---

## Scenario 2: Production Build — Developer ID Signing

**Goal**: Verify app bundle and DMG are both signed with Developer ID certificate.

### Prerequisites

- Developer ID Application certificate installed in Keychain
- Certificate identity string known (from `security find-identity`)

```bash
# Check available certificates
security find-identity -v -p codesigning | grep "Developer ID"
# Expected: 1) SHA1HASH "Developer ID Application: Your Name (TEAMID)"

# Set identity (or let build.sh auto-detect)
export DEVELOPER_ID_APP="Developer ID Application: Your Name (TEAMID)"

# Build with signing
./packaging/macos/build.sh --version 1.0.0 --sign "$DEVELOPER_ID_APP"
```

**Expected output** (key lines):

```
🔐 Detected certificate: Developer ID Application: Your Name (TEAMID)
🔐 Signing app bundle with Developer ID...
✅ App bundle signed: dist/macos/IntervalsICU.app
🔐 Signing DMG container with Developer ID...
✅ DMG signed: dist/macos/IntervalsICU-1.0.0.dmg
✅ Build complete: dist/macos/IntervalsICU-1.0.0.dmg
```

**Verification**:

```bash
# App bundle: Developer ID chain present
codesign -vvv dist/macos/IntervalsICU.app 2>&1 | grep "Authority"
# Expected lines:
#   Authority=Developer ID Application: Your Name (TEAMID)
#   Authority=Developer ID Certification Authority
#   Authority=Apple Root CA

# App bundle: signature valid
codesign -v dist/macos/IntervalsICU.app && echo "PASS: app bundle valid"

# DMG: Developer ID chain present
codesign -dv dist/macos/IntervalsICU-1.0.0.dmg 2>&1 | grep "Authority"
# Expected: Authority=Developer ID Application: Your Name (TEAMID)

# DMG: signature valid
codesign -v dist/macos/IntervalsICU-1.0.0.dmg && echo "PASS: DMG valid"

# Gatekeeper assessment (requires internet; checks revocation)
spctl --assess --type open --context context:primary-signature \
  dist/macos/IntervalsICU-1.0.0.dmg && echo "PASS: Gatekeeper accepts DMG"
```

---

## Scenario 3: Full Production Build — Signed + Notarized + Stapled

**Goal**: Verify the complete chain: Developer ID signed → Apple notarized → stapled.

### Prerequisites

- Developer ID Application certificate in Keychain
- Active Apple Developer account with app-specific password
- Environment variables set

```bash
export DEVELOPER_ID_APP="Developer ID Application: Your Name (TEAMID)"
export APPLE_ID="your@apple.id.com"
export APPLE_TEAM_ID="YOUR_TEAM_ID"
export APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"  # app-specific password

# Full build: sign + notarize
./packaging/macos/build.sh --version 1.0.0 \
  --sign "$DEVELOPER_ID_APP" \
  --notarize
# ⏳ Takes 5–15 minutes (Apple notarization service latency)
```

**Expected output** (key lines):

```
🔐 Signing app bundle with Developer ID...
✅ App bundle signed
🔐 Signing DMG container with Developer ID...
✅ DMG signed
📤 Submitting to Apple Notary Service...
⏳ Notarization in progress... (checking every 10s, max 30 min)
✅ Notarization approved! Submission ID: a1b2c3d4-...
📎 Stapling notarization ticket to DMG...
✅ Notarization stapled
✅ Build complete: dist/macos/IntervalsICU-1.0.0.dmg
```

**Verification**:

```bash
# Notarization stapled (no internet required for this check)
xcrun stapler validate dist/macos/IntervalsICU-1.0.0.dmg
# Expected: The file dist/macos/IntervalsICU-1.0.0.dmg is already stapled.

# Full Gatekeeper acceptance (signed + notarized)
spctl --assess --verbose=4 --type open dist/macos/IntervalsICU-1.0.0.dmg
# Expected: accepted  source=Notarized Developer ID

# Mount DMG on clean system — zero warnings
hdiutil attach dist/macos/IntervalsICU-1.0.0.dmg
# Expected: mounts immediately, no Gatekeeper dialog
```

---

## Scenario 4: Entitlements Validation

**Goal**: Verify both entitlements files exist, are valid XML, and have correct keys.

```bash
# Validate entitlements-app.plist is valid XML
plutil -lint packaging/macos/entitlements-app.plist
# Expected: packaging/macos/entitlements-app.plist: OK

# Validate entitlements-dmg.plist is valid XML
plutil -lint packaging/macos/entitlements-dmg.plist
# Expected: packaging/macos/entitlements-dmg.plist: OK

# Verify app entitlements contain required keys
plutil -p packaging/macos/entitlements-app.plist | grep -E "dyld|unsigned-memory|network"
# Expected output includes:
#   "com.apple.security.cs.allow-dyld-environment-variables" => 1
#   "com.apple.security.cs.allow-unsigned-executable-memory" => 1
#   "com.apple.security.network.client" => 1

# Verify app entitlements embedded in signed bundle
codesign -d --entitlements - dist/macos/IntervalsICU.app
# Expected: XML plist showing the three keys above
```

---

## Scenario 5: Post-Install Gatekeeper Check (End-to-End)

**Goal**: Install from notarized DMG; verify app launches with zero Gatekeeper warnings.

```bash
# 1. Mount notarized DMG
hdiutil attach dist/macos/IntervalsICU-1.0.0.dmg

# 2. Run automated installer
/Volumes/IntervalsICU/install.sh
# Expected: "✅ Installation complete"

# 3. Verify installed app signature preserved
codesign -v /Applications/IntervalsICU.app && echo "PASS: installed app valid"

# 4. Verify quarantine NOT present (notarization removes the need)
xattr -l /Applications/IntervalsICU.app | grep quarantine
# Expected: no output (quarantine attribute absent)

# 5. Gatekeeper clears installed app
spctl --assess --verbose /Applications/IntervalsICU.app
# Expected: accepted  source=Notarized Developer ID

# 6. MANUAL: Open app
open /Applications/IntervalsICU.app
# Expected: App opens immediately — NO Gatekeeper dialog, NO security warning

# 7. Eject DMG
hdiutil detach /Volumes/IntervalsICU
```

---

## Scenario 6: Error Handling — Unknown Certificate Identity

**Goal**: Verify build fails with clear error when `--sign` is given a non-existent cert.

```bash
./packaging/macos/build.sh --version 1.0.0 --sign "Developer ID Application: Nobody (FAKEID)"
```

**Expected**:

```
❌ ERROR: Certificate not found in Keychain
   Identity: "Developer ID Application: Nobody (FAKEID)"

   To fix:
   1. List available certs: security find-identity -v -p codesigning
   2. Use the exact identity string shown
   3. Or import your certificate: double-click the .cer file from developer.apple.com
```

**Expected exit code**: non-zero (not 0)

```bash
echo $?  # Expected: non-zero (e.g., 1 or error code 1001)
```

---

## Quick Reference

| Command                                    | Purpose                             |
| ------------------------------------------ | ----------------------------------- |
| `security find-identity -v -p codesigning` | List available signing certificates |
| `codesign -v <file>`                       | Validate signature                  |
| `codesign -dv <file>`                      | Display signature details           |
| `codesign -vvv <file>`                     | Full certificate chain              |
| `codesign -d --entitlements - <app>`       | Show embedded entitlements          |
| `spctl --assess --verbose <file>`          | Gatekeeper assessment               |
| `xcrun stapler validate <dmg>`             | Check notarization stapled          |
| `plutil -lint <plist>`                     | Validate plist XML                  |
| `xattr -l <path>`                          | Show extended attributes            |

---

## Links

- [Apple Developer Program](https://developer.apple.com/developer-id/) — Enrol and create Developer ID certificate
- [Notarizing macOS Software](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution) — Apple documentation
- [contracts/dmg-signing.md](contracts/dmg-signing.md) — Full implementation contract
- [data-model.md](data-model.md) — Entitlements plists and entity models
- [../002-seamless-dmg-install/quickstart.md](../002-seamless-dmg-install/quickstart.md) — Installation workflow (predecessor)
