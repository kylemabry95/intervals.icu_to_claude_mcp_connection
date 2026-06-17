# Implementation Plan: DMG Code Signing & Notarization

**Branch**: `003-dmg-code-signing` | **Date**: 2026-06-17 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `specs/003-dmg-code-signing/spec.md`

## Summary

Users receive a Gatekeeper malware warning when opening the distributed `IntervalsICU-1.0.0.dmg`. Root cause: the DMG container and app bundle are not signed with a Developer ID Application certificate. The fix requires (1) signing the app bundle with `--deep --options runtime` and a Developer ID cert before DMG creation, (2) signing the DMG container after creation, and (3) submitting to Apple's Notary Service and stapling the approval ticket. The existing `build.sh` already has structural scaffolding for `--sign` and `--notarize` flags but has gaps: the DMG itself is never signed, there are no separate `entitlements-app.plist` / `entitlements-dmg.plist` files, the `--sign` flag accepts no identity argument (reads only from `DEVELOPER_ID_APP` env var), and the dev fallback warning is insufficient. This feature closes all those gaps.

## Technical Context

**Language/Version**: Bash 4.0+ (build scripts); macOS system tools (`codesign`, `xcrun`, `security`)

**Primary Dependencies**:

- `codesign` — Apple code signing CLI (bundled with Xcode Command Line Tools)
- `xcrun notarytool` — Apple Notary Service submission (Xcode 13+)
- `xcrun stapler` — Staple notarization approval to DMG (Xcode 13+)
- `security` — macOS Keychain CLI for certificate detection
- `create-dmg` 1.3.3 — DMG creation (already in use)
- `packaging/macos/entitlements.plist` — Existing entitlements (to be split into two)

**Storage**: N/A (no persistent data; operates on filesystem artifacts)

**Testing**: Manual validation via `codesign -v`, `xcrun stapler validate`, `hdiutil attach`; `packaging/macos/install.sh.test` extended for signed flow

**Target Platform**: macOS 11 (Big Sur) and later, arm64 + x86_64

**Project Type**: Build tooling / shell script (modifying `packaging/macos/build.sh`)

**Performance Goals**: Signing adds <2s; notarization 5–15 min (Apple service; async-acceptable for release builds)

**Constraints**:

- No Developer ID cert currently installed — build must degrade gracefully to ad-hoc
- Notarization requires active Apple Developer account credentials via env vars
- `codesign --deep` must be applied to app bundle _before_ DMG is created; DMG signed _after_
- Entitlements must permit Python's `dyld` environment variables and unsigned memory (required for PyInstaller apps)

## Constitution Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

| Principle                                     | Status  | Notes                                                                       |
| --------------------------------------------- | ------- | --------------------------------------------------------------------------- |
| I. AI Cost & Token Optimization               | ✅ PASS | Shell scripts; no LLM at runtime                                            |
| II. Approved AI Asset Usage                   | ✅ PASS | No new AI assets introduced                                                 |
| III. Testing Non-Negotiable                   | ✅ PASS | Manual validation scenarios defined; install.sh.test extended               |
| IV. Security, Access Control, Data Protection | ✅ PASS | Credentials via env vars only; never in code; private key stays in Keychain |
| V. Reproducibility & Automation               | ✅ PASS | All signing automated via `--sign` flag; documented for reproducibility     |
| VI. Maintainability & Reviewability           | ✅ PASS | Build script is single file; changes are small and reviewable               |
| VII. Troubleshooting & Debugging              | ✅ PASS | Error codes, recovery steps, `--verbose` flag                               |
| VIII. Version Control                         | ✅ PASS | Feature branch; conventional commits                                        |

**No gate violations. Proceed.**

## Project Structure

### Documentation (this feature)

```text
specs/003-dmg-code-signing/
├── plan.md              ✅ This file
├── research.md          ✅ Existing (complete)
├── data-model.md        ✅ Existing (complete)
├── quickstart.md        ✅ Created (commit 352f0b7)
├── contracts/
│   └── dmg-signing.md  ✅ Existing (complete)
└── tasks.md             🔲 Created by /speckit.tasks (not this command)
```

### Source Code (this feature modifies)

```text
packaging/macos/
├── build.sh                    # Modified: sign flag refactor + DMG signing + verbose flag
├── entitlements-app.plist      # New: hardened runtime entitlements for Python app bundle
├── entitlements-dmg.plist      # New: minimal container entitlements for DMG
└── entitlements.plist          # Existing: kept for backward compatibility reference

specs/003-dmg-code-signing/
├── quickstart.md               # New: validation guide for signing workflow
```

**Structure Decision**: Single-project shell tooling. No src/ hierarchy — all changes are confined to `packaging/macos/` build scripts and `specs/003-dmg-code-signing/` documentation.

## Complexity Tracking

No constitution violations. No complexity justification required.
