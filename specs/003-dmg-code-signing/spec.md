# Specification: DMG Code Signing and Notarization

**Feature**: Fix DMG Code Signing and Notarization  
**Status**: In Development  
**Priority**: P1 (Blocker)  
**Version**: 1.0

---

## Problem Statement

Users receive a Gatekeeper warning when attempting to open/mount the `IntervalsICU-1.0.0.dmg` file:

> "Apple could not verify 'IntervalsICU' is free of malware that may harm your Mac or compromise your privacy."

**Current State**:

- The DMG is created but **not code-signed**
- macOS Gatekeeper flags unsigned DMGs as potentially malicious
- Users must manually bypass security warnings (right-click → Open)
- This undermines the seamless installation experience from feature 002

**Root Cause**:

- `packaging/macos/build.sh` creates DMG but does not code-sign it
- No entitlements or notarization metadata included
- Ad-hoc signatures insufficient for DMG distribution

**Expected Behavior**:

- DMG mounts without Gatekeeper warnings
- Users can open DMG with confidence (no security dialogs)
- Seamless installation experience maintained end-to-end

---

## Goals & Success Criteria

### Primary Goals

1. **Eliminate Gatekeeper warnings** — DMG opens without "can't verify" dialog
2. **Maintain seamless UX** — Users mount DMG with one click, no interruptions
3. **Support both architectures** — arm64 (Apple Silicon) and x86_64 (Intel)
4. **Preserve build automation** — No manual signing steps in normal development workflow

### Success Criteria

1. ✅ **App bundle signed** — `codesign -vvv IntervalsICU.app` returns exit 0 with Developer ID chain
2. ✅ **Code-signed DMG** — `codesign -v dist/macos/IntervalsICU-1.0.0.dmg` returns exit 0
3. ✅ **Gatekeeper acceptance** — User mounts DMG on clean system with zero warnings
4. ✅ **App launch clean** — `codesign -v /Applications/IntervalsICU.app` after install returns exit 0; no Gatekeeper prompt on launch
5. ✅ **Build-time signature** — Both app bundle and DMG signed automatically during `./build.sh --sign <identity>` execution
6. ✅ **Notarized** — Apple Notary Service approves and ticket is stapled to DMG
7. ✅ **Fallback for dev** — Development builds without signing don't fail; use ad-hoc signatures with guidance

---

## User Scenarios

### Scenario 1: Fresh Installation (Ideal Flow)

```
1. User downloads IntervalsICU-1.0.0.dmg
2. Double-click to mount
   ✅ DMG mounts immediately with NO Gatekeeper warning
3. Double-click install.sh OR drag app to Applications
4. App installs successfully
5. User launches app from Applications
   ✅ App opens with NO Gatekeeper warning
6. App is fully functional
```

### Scenario 2: Development Build (No Signing Certificate)

```
1. Developer runs: ./packaging/macos/build.sh --version 1.0.0
2. Build completes with ad-hoc signature
   ⚠️ Warning: "No signing certificate found. Using ad-hoc signature."
   ℹ️ "For production, use: --sign <identity> --notarize"
3. DMG created for local testing
   Note: Test DMG will show Gatekeeper warning (expected for unsigned)
4. Test installation workflow
```

### Scenario 3: Production Build (Signed & Notarized)

```
1. DevOps runs: ./packaging/macos/build.sh --version 1.0.0 --sign "Developer ID" --notarize
2. DMG signed with Developer ID certificate
3. DMG submitted to Apple for notarization
4. Apple approves and staples notarization ticket
5. Final DMG distributed: NO Gatekeeper warnings on any Mac
```

---

## Functional Requirements

### App Bundle Signing Requirements (Phase 1)

1. **App Bundle Code Signing**
   - Sign `IntervalsICU.app` with Developer ID Application certificate before DMG creation
   - Use `--deep` flag to sign all nested binaries and frameworks
   - Apply `packaging/macos/entitlements-app.plist` for hardened runtime
   - Entitlements must allow Python subprocess spawning and network access
   - Verify bundle signature: `codesign -vvv IntervalsICU.app`

2. **App Bundle Entitlements** (`entitlements-app.plist`)
   - `com.apple.security.cs.allow-dyld-environment-variables`: true
   - `com.apple.security.cs.allow-unsigned-executable-memory`: true
   - `com.apple.security.network.client`: true (for intervals.icu API calls)
   - All privacy-sensitive entitlements (camera, mic, contacts): false

### DMG Signing Requirements (Phase 1)

1. **Code Signing**
   - Sign DMG with valid Apple Developer ID certificate
   - Implement `codesign` command integration in build.sh
   - Sign DMG _after_ app bundle is already signed and placed inside
   - Preserve file permissions and structure during signing
   - Verify signature after signing: `codesign -v`

2. **DMG Entitlements** (`entitlements-dmg.plist`)
   - Minimal permissions — DMG is a container, not an executable
   - `com.apple.security.cs.allow-dyld-environment-variables`: true

3. **Development vs Production** (Phase 1)
   - Development builds (no `--sign` flag): Build **succeeds** using ad-hoc signatures on both app bundle and DMG; prints prominent warning block with step-by-step certificate setup instructions
   - Production builds: `--sign <identity>` flag applies Developer ID to both app bundle and DMG; build fails explicitly if specified cert is not found in Keychain
   - Warning output must include: link to developer.apple.com/developer-id, Keychain import steps, and the exact `--sign` flag syntax to use once cert is installed

4. **Signing Order** (critical)
   - Step 1: Sign app bundle with `--deep --options runtime`
   - Step 2: Place signed app bundle into DMG
   - Step 3: Sign DMG container
   - Step 4: Notarize DMG (Phase 2)
   - Step 5: Staple approval to DMG

### Notarization Requirements (Phase 2)

1. **Notary Service Integration**
   - Submit DMG to Apple Notary Service via `xcrun notarytool`
   - Include Team ID and credentials (Developer ID / app-specific password)
   - Wait for notarization approval
   - Staple notarization ticket to DMG: `xcrun stapler staple`

2. **CI/CD Integration**
   - GitHub Actions workflow for automated notarization
   - Environment variables for credentials (GitHub Secrets)
   - Automated retry logic for transient failures
   - Build artifacts published after successful notarization

### Build Script Updates (Phase 1)

1. **New Flags**:
   - `--sign <identity>` — Use specified certificate for signing
   - `--notarize` — Enable notarization workflow
   - `--verbose` — Show detailed signing/notarization output

2. **Certificate Detection**:
   - Check for available Developer ID certificates: `security find-identity`
   - Auto-select if only one available
   - Prompt user if multiple certs available
   - Fallback to ad-hoc if none available

3. **Error Handling**:
   - Catch signing failures with specific error codes
   - Provide recovery steps for each error
   - Log all signing/notarization operations

---

## Key Entities & Data Model

### Certificates & Identities

```
Developer ID Application Certificate:
├── Subject: CN="Developer ID Application: [Name] ([ID])"
├── Issuer: CN="Developer ID Certification Authority"
├── Validity: 1 year
├── Key Usage: Code signing
└── Extended: MacOS Code Signing

Developer ID Installer Certificate (optional):
├── Subject: CN="Developer ID Installer: [Name] ([ID])"
├── Used for: Package signing (not required for DMG)
└── Optional: Not needed for this feature
```

### Entitlements Plist Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC ... >
<plist version="1.0">
<dict>
  <key>com.apple.security.cs.allow-dyld-environment-variables</key>
  <true/>
  <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
  <true/>
  <key>com.apple.security.device.camera.microphone</key>
  <false/>
  <!-- Minimal entitlements for DMG operations -->
</dict>
</plist>
```

### Notarization Response

```json
{
  "data": {
    "id": "uuid-from-notary-service",
    "type": "notarization-upload",
    "attributes": {
      "createdDate": "2026-06-17T...",
      "name": "IntervalsICU-1.0.0.dmg",
      "status": "Accepted"
    }
  }
}
```

---

## Dependencies & Assumptions

### Dependencies

- **macOS 11+** — Required for notarization infrastructure
- **Xcode Command Line Tools** — `codesign`, `xcrun`, `security`
- **Developer ID Certificate** — Required for production signing (not development)
- **Apple Developer Account** — Required for notarization (optional for dev builds)

### Assumptions

1. Developers have Xcode Command Line Tools installed
2. **No Developer ID certificate currently available** — must be obtained before production signing (requires $99/year Apple Developer Program membership at developer.apple.com)
3. Phase 1 implementation should include setup guidance for obtaining and installing the certificate
4. Notarization credentials available via environment variables (CI/CD)
5. Users accept minor delays for production builds (~5-10 min with notarization)
6. Ad-hoc signatures acceptable for development/testing and as interim distribution fallback

### Constraints

- Notarization takes 5-15 minutes (Apple service latency)
- Notarization only available on macOS 10.15+
- Previous macOS versions (10.14 and earlier) don't validate notarization

---

## Implementation Approach

### Phase 1: Code Signing (MVP)

1. Create entitlements plist (`packaging/macos/entitlements-dmg.plist`)
2. Add signing logic to `packaging/macos/build.sh`
3. Implement certificate detection via `security find-identity`
4. Add `--sign` and `--verbose` flags
5. Comprehensive error handling and messaging

**Effort**: ~3 hours

### Phase 2: Notarization (In Scope — Same Feature)

1. Create notarization wrapper using `xcrun notarytool`
2. Implement credential management (environment variables)
3. Add notarization polling (wait for approval)
4. Add `--notarize` flag to build.sh
5. CI/CD workflow for automated notarization

**Effort**: ~4 hours

### Phase 3: CI/CD Integration (Out of Scope — Future Feature)

> **Deferred**: GitHub Actions automation is explicitly out of scope for this feature. Implement signing and notarization locally first; automate in a separate feature.

- GitHub Actions workflow for automated builds
- Environment variable setup for secrets
- Automated notarization on release branches
- Build artifact publication

**Effort**: ~2 hours (future)

---

## Risks & Mitigations

| Risk                             | Severity | Mitigation                                         |
| -------------------------------- | -------- | -------------------------------------------------- |
| Missing Developer ID cert        | HIGH     | Fallback to ad-hoc; clear messaging; doc for setup |
| Notarization fails/rejected      | MEDIUM   | Retry logic; detailed Apple feedback; human review |
| Signing breaks app functionality | MEDIUM   | Test harness validates functionality post-signing  |
| Notarization timeout (API slow)  | LOW      | Polling with exponential backoff; timeout safety   |
| Cert expiration not checked      | MEDIUM   | Validation before signing; renewal reminders       |

---

## Testing Strategy

### Unit Tests

- Certificate detection and selection logic
- Entitlements plist parsing and validation
- Error code generation and messaging

### Integration Tests

- Sign DMG and verify signature: `codesign -v`
- Mount signed DMG and check file integrity
- Run install.sh from signed DMG
- Verify installed app signature

### End-to-End Tests

- Fresh system: Mount DMG with zero Gatekeeper warnings
- Gatekeeper bypass logic works on Sonoma/Sequoia
- Notarization approval and stapling (production only)

### Manual Tests

- User mounting signed DMG on macOS 11-15
- Installation workflow verification
- App launch verification (zero security warnings)

---

## Clarifications

### Session 2026-06-17

- Q: Do you have an Apple Developer ID Application certificate currently installed in your Mac Keychain? → A: No cert yet, willing to obtain one (requires $99/year Apple Developer account)
- Q: Should notarization be included in this feature, or deferred to a future release? → A: Certificate + Notarization in same feature (Phases 1 & 2 together)
- Q: Should a GitHub Actions CI/CD workflow be included in this feature? → A: No — defer CI/CD automation to a future feature; implement signing + notarization locally first
- Q: Should the app bundle also be signed, or only the DMG container? → A: Sign both — Developer ID signs the app bundle AND the DMG for a fully verified chain
- Q: When `build.sh` is run without `--sign`, what should happen? → A: Succeed with ad-hoc signatures + prominent warning + certificate setup instructions printed

## Open Questions / Clarifications

- [RESOLVED] Notarization is in scope for this feature (Phases 1 & 2 together)
- [RESOLVED] CI/CD GitHub Actions is explicitly out of scope — deferred to a future feature

---

## Acceptance Criteria

- ✅ App bundle signed with Developer ID before DMG creation
- ✅ DMG signed with Developer ID after app bundle placed inside
- ✅ User downloads fresh DMG and mounts with zero Gatekeeper warnings
- ✅ Installation via install.sh succeeds post-mount
- ✅ App launches with zero Gatekeeper warnings (no prompt on first open)
- ✅ `codesign -vvv` validation passes for app bundle with full certificate chain
- ✅ `codesign -v` validation passes for DMG container
- ✅ Apple notarization approved and stapled to DMG
- ✅ Build script supports `--sign`, `--notarize`, and `--verbose` flags
- ✅ Two entitlements files created: `entitlements-app.plist` and `entitlements-dmg.plist`
- ✅ Fallback messaging for missing certificates
- ✅ Documentation updated with certificate setup guide and signing process

---

## Related Documents

- [DMG-Integration Contract](contracts/dmg-integration.md) — Technical implementation details
- [Build System Research](research.md) — Signing tools and approaches
- [../002-seamless-dmg-install/spec.md](../002-seamless-dmg-install/spec.md) — App installation (predecessor feature)

---

## Glossary

- **Code Signing**: Cryptographic signature proving authenticity and integrity of code
- **Gatekeeper**: macOS security feature validating signed/notarized applications
- **Notarization**: Apple's service reviewing apps for malware before allowing execution
- **Developer ID**: Certificate identity for signing apps outside Mac App Store
- **Stapling**: Attaching Apple's notarization approval to DMG (offline validation)
- **Ad-hoc Signature**: Temporary self-signed certificate (development only)
