# Data Model: DMG Code Signing & Notarization

## Core Entities

### 1. Certificate Identity

```json
{
  "type": "DeveloperIDCertificate",
  "identity": "Developer ID Application: Kyle Mabry (ABC1234567)",
  "certificateCommonName": "Developer ID Application: Kyle Mabry (ABC1234567)",
  "issuerCommonName": "Developer ID Certification Authority",
  "teamId": "ABC1234567",
  "ownerName": "Kyle Mabry",
  "fingerprint": "A1B2C3D4E5F6...",
  "validityStart": "2025-06-17T00:00:00Z",
  "validityEnd": "2026-06-17T00:00:00Z",
  "keyType": "RSA",
  "keySize": 2048,
  "purpose": "CodeSigning",
  "keychain": "/Users/[username]/Library/Keychains/login.keychain",
  "status": "Valid"
}
```

### 2. Code Signature

```json
{
  "type": "CodeSignature",
  "targetFile": "dist/macos/IntervalsICU-1.0.0.dmg",
  "signedAt": "2026-06-17T14:32:00Z",
  "certificate": "Developer ID Application: Kyle Mabry (ABC1234567)",
  "algorithm": "SHA-256",
  "requirements": {
    "designated": "anchor apple generic and certificate leaf[field.1.2.840.113635.100.6.1.13]",
    "library": "anchor apple generic and certificate leaf[field.1.2.840.113635.100.6.1.8]",
    "plugin": "anchor apple generic and certificate leaf[field.1.2.840.113635.100.6.1.13]"
  },
  "entitlements": {
    "com.apple.security.cs.allow-dyld-environment-variables": true
  },
  "signatureValid": true,
  "signingIdentityValid": true
}
```

### 3. Entitlements

### 3a. App Bundle Entitlements (`entitlements-app.plist`)

Required for PyInstaller-bundled Python app with hardened runtime and network access to intervals.icu API:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <!-- Required: PyInstaller apps load Python via dyld env vars -->
  <key>com.apple.security.cs.allow-dyld-environment-variables</key>
  <true/>
  <!-- Required: Python interpreter uses unsigned executable memory -->
  <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
  <true/>
  <!-- Required: outbound HTTPS calls to intervals.icu API -->
  <key>com.apple.security.network.client</key>
  <true/>
  <!-- Explicitly denied: all privacy-sensitive capabilities -->
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
  <key>com.apple.security.personal-information.location</key>
  <false/>
</dict>
</plist>
```

### 3b. DMG Container Entitlements (`entitlements-dmg.plist`)

Minimal — DMG is a container image, not an executable:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <!-- Minimal: allow dyld vars for any scripts inside the DMG -->
  <key>com.apple.security.cs.allow-dyld-environment-variables</key>
  <true/>
</dict>
</plist>
```

### 4. Notarization Request

```json
{
  "type": "NotarizationRequest",
  "submissionId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "dmgFile": "dist/macos/IntervalsICU-1.0.0.dmg",
  "dmgName": "IntervalsICU-1.0.0.dmg",
  "dmgSize": 34102655,
  "dmgHash": "sha256:...",
  "submittedAt": "2026-06-17T14:35:00Z",
  "submittedBy": "dev@company.com",
  "teamId": "ABC1234567",
  "status": "In Progress",
  "statusCode": 0,
  "statusMessage": "Notarization in progress",
  "progressPercent": 42
}
```

### 5. Notarization Response

```json
{
  "type": "NotarizationResponse",
  "submissionId": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "status": "Accepted",
  "statusCode": 0,
  "approvedAt": "2026-06-17T14:42:00Z",
  "statusMessages": ["Package Approved"],
  "logs": {
    "archiveFilename": "IntervalsICU-1.0.0.dmg",
    "ticketContents": {
      "productsArchiveChecksum": "...",
      "macNotarization": [
        {
          "timestamp": "2026-06-17T14:40:00Z",
          "status": "Accepted"
        }
      ]
    },
    "issues": null,
    "certificateChain": [
      {
        "sha256": "cert1-hash",
        "status": "Trusted"
      }
    ]
  }
}
```

### 6. Signing Operation Context

```json
{
  "type": "SigningContext",
  "buildVersion": "1.0.0",
  "buildType": "production",
  "signingEnabled": true,
  "signingCertificate": "Developer ID Application: Kyle Mabry (ABC1234567)",
  "signingCertificateSource": "auto-detected",
  "entitlementsFile": "packaging/macos/entitlements-dmg.plist",
  "notarizationEnabled": true,
  "notarizationTeamId": "ABC1234567",
  "notarizationAppleId": "dev@company.com",
  "notarizationPasswordSource": "environment",
  "outputDmg": "dist/macos/IntervalsICU-1.0.0.dmg",
  "verificationEnabled": true
}
```

---

## Entity Relationships

```
Certificate ←→ CodeSignature
  ├─ Issued by: Apple Dev Authority
  ├─ Validity: 1 year
  └─ Used to sign: DMG, App Bundle

CodeSignature → Entitlements
  ├─ Applies permissions
  ├─ Validated by Gatekeeper
  └─ Persists in signature metadata

CodeSignature → NotarizationRequest
  ├─ DMG must be signed first
  ├─ Signature verified by Apple
  └─ Creates audit trail

NotarizationRequest → NotarizationResponse
  ├─ Status: In Progress → Accepted/Rejected
  ├─ Timeline: 5-15 minutes
  └─ Result: Approval or rejection reasons

SigningContext coordinates all operations
  ├─ Detects certificates
  ├─ Loads entitlements
  ├─ Orchestrates signing
  ├─ Manages notarization
  └─ Verifies results
```

---

## State Machines

### Certificate Lifecycle

```
Not Found
    ↓
Auto-detected [multiple: prompt user]
    ↓
Selected
    ↓
Validated (expiry, revocation, trust)
    ↓
┌─→ Valid ─→ Ready to use
│
└─→ Invalid ─→ Error [not yet expired, not revoked]
    │
    └─→ Expired ─→ Error [needs renewal]
    └─→ Revoked ─→ Error [needs new cert]
```

### Signing Operation Flow

```
DMG Created
    ↓
[Cert detected?]
    ├─ Yes: Load Certificate
    └─ No: Use Ad-hoc
    ↓
Load Entitlements
    ↓
Sign DMG (codesign)
    ├─ Success ↓
    └─ Failure → Error [disk space? permissions?]
    ↓
Verify Signature
    ├─ Valid ↓
    └─ Invalid → Error [re-sign or rebuild]
    ↓
[Notarization requested?]
    ├─ Yes: Submit to Apple
    └─ No: Done
    ↓
Poll Notarization Status
    ├─ Approved ↓
    ├─ Rejected → Error [review Apple logs]
    └─ Timeout → Error [retry or manual check]
    ↓
Staple Notarization
    ├─ Success → Complete ✓
    └─ Failure → Error [retry]
```

### Notarization Status Machine

```
Submitted
    ├─ In Progress (poll every 10s)
    │   └─ [timeout 30 min]
    │
    ├─ Accepted
    │   ├─ Logs available
    │   └─ Ready to staple
    │
    └─ Rejected
        ├─ Logs contain rejection reasons
        └─ Errors to resolve
```

---

## Build Configuration Data Structure

```toml
[build]
version = "1.0.0"
platform = "macos"

[signing]
enabled = true
certificate = "auto-detect"  # or "Developer ID Application: ..."
entitlements = "packaging/macos/entitlements-dmg.plist"
timestamp = true

[notarization]
enabled = true                    # for production only
apple_id = "${APPLE_ID}"          # env variable
team_id = "${APPLE_TEAM_ID}"      # env variable
password = "${APPLE_NOTARY_PWD}"  # env variable (app-specific)
poll_interval = 10                # seconds
max_wait_time = 1800              # 30 minutes

[verification]
verify_signature = true
verify_notarization = true
validate_requirements = true
```

---

## Error Codes

```
0    Success
1001 Certificate not found
1002 Certificate expired
1003 Certificate revoked
1004 Invalid certificate format
1005 Invalid entitlements

2001 Signing failed (general)
2002 File not found
2003 Permission denied
2004 Insufficient disk space
2005 Signature validation failed

3001 Notarization submission failed
3002 Invalid credentials
3003 Team ID mismatch
3004 Notarization rejected (malware)
3005 Notarization timeout
3006 Stapling failed

4001 Certificate auto-detection returned multiple certs (user action required)
4002 Missing entitlements file
4003 Invalid entitlements XML
```

---

## Performance Metrics

```json
{
  "operation": "sign-and-notarize",
  "startTime": "2026-06-17T14:32:00Z",
  "endTime": "2026-06-17T14:42:00Z",
  "totalDuration": 600,
  "steps": {
    "detectCertificate": 0.5,
    "loadEntitlements": 0.2,
    "signDmg": 1.2,
    "verifySigning": 0.8,
    "submitNotarization": 2.1,
    "pollNotarization": 594.2,
    "stapleNotarization": 1.0
  },
  "dmgSize": 34102655,
  "dmgCompression": 0.647,
  "signatureSize": 4096,
  "entitlementsSize": 892
}
```
