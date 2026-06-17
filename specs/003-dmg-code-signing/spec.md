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

1. ✅ **Code-signed DMG** — `codesign -v dist/macos/IntervalsICU-1.0.0.dmg` returns exit 0
2. ✅ **Gatekeeper acceptance** — User mounts DMG on clean system with zero warnings
3. ✅ **App signature valid** — `codesign -v /Applications/IntervalsICU.app` after install returns exit 0
4. ✅ **Build-time signature** — DMG signed automatically during `./build.sh` execution (production builds)
5. ✅ **Fallback for dev** — Development builds without signing don't fail; use ad-hoc signature with guidance

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

### DMG Signing Requirements

1. **Code Signing** (Phase 1)
   - Sign DMG with valid Apple Developer ID certificate
   - Implement `codesign` command integration in build.sh
   - Support both hardened runtime and standard runtime
   - Preserve file permissions and structure during signing
   - Verify signature after signing: `codesign -v`

2. **Entitlements** (Phase 1)
   - Create `packaging/macos/entitlements-dmg.plist` for DMG
   - Grant minimal required permissions (file read, basic app execution)
   - Apply entitlements during signing: `codesign -s <identity> --entitlements <plist>`

3. **Development vs Production** (Phase 1)
   - Development builds: Ad-hoc signatures (no cert required)
   - Production builds: Require `--sign <identity>` flag with valid cert
   - Fallback messaging for missing certificates

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
2. Production builds will have Developer ID certificate in Keychain
3. Notarization credentials available via environment variables (CI/CD)
4. Users accept minor delays for production builds (~5-10 min with notarization)
5. Ad-hoc signatures acceptable for development/testing

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

### Phase 2: Notarization (Future Enhancement)

1. Create notarization wrapper using `xcrun notarytool`
2. Implement credential management (environment variables)
3. Add notarization polling (wait for approval)
4. Add `--notarize` flag to build.sh
5. CI/CD workflow for automated notarization

**Effort**: ~4 hours

### Phase 3: CI/CD Integration (Future)

1. GitHub Actions workflow for automated builds
2. Environment variable setup for secrets
3. Automated notarization on release branches
4. Build artifact publication

**Effort**: ~2 hours

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

## Open Questions / Clarifications

- [NEEDS CLARIFICATION: Notarization Timeline] Should Phase 2 (notarization) be done immediately or deferred to future release?
- [NEEDS CLARIFICATION: CI/CD Environment] Should GitHub Actions be configured now or defer to Phase 3?

---

## Acceptance Criteria

- ✅ DMG signed with developer certificate (or ad-hoc for dev)
- ✅ User downloads fresh DMG and mounts with zero Gatekeeper warnings
- ✅ Installation via install.sh succeeds post-mount
- ✅ App launches with zero Gatekeeper warnings
- ✅ `codesign -v` validation passes for both DMG and app bundle
- ✅ Build script supports `--sign` and `--verbose` flags
- ✅ Fallback messaging for missing certificates
- ✅ Documentation updated with signing process

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
