# Tasks: DMG Code Signing & Notarization

**Input**: Design documents from `specs/003-dmg-code-signing/`

**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/dmg-signing.md ✅ | quickstart.md ✅

**Tests**: No automated tests — this is build tooling. Validation is via `codesign -v`, `plutil -lint`, `xcrun stapler validate`, and manual Gatekeeper checks per quickstart.md.

**Organization**: Tasks grouped by user story. US1 (signing) must complete before US2 (notarization) can begin. US3 (developer UX) is parallel to US1/US2.

---

## Format Reference

- **[P]**: Can run in parallel (different files, no blocking dependencies)
- **[US#]**: User story this task belongs to
- All file paths relative to repository root

---

## Phase 1: Setup

**Purpose**: Create the two entitlements plist files that both signing phases depend on; verify toolchain availability.

- [ ] T001 Verify Xcode CLT toolchain: run `xcode-select -p && xcrun --version && codesign --version` and confirm all present in `packaging/macos/README.md`
- [ ] T002 [P] Create `packaging/macos/entitlements-app.plist` with hardened runtime entitlements for PyInstaller Python app (dyld-env-vars, unsigned-memory, network.client; all privacy caps denied)
- [ ] T003 [P] Create `packaging/macos/entitlements-dmg.plist` with minimal container entitlements (dyld-env-vars only)
- [ ] T004 Validate both plist files: `plutil -lint packaging/macos/entitlements-app.plist && plutil -lint packaging/macos/entitlements-dmg.plist`

**Checkpoint**: Two valid entitlements files exist; toolchain confirmed present.

---

## Phase 2: Foundational — build.sh Refactor

**Purpose**: Refactor the `--sign` flag in `packaging/macos/build.sh` to accept an identity argument, add certificate auto-detection, and wire up the new entitlements files. All user stories build on this.

**⚠️ CRITICAL**: Must complete before US1 and US2 work begins.

- [ ] T005 Refactor `--sign` argument parsing in `packaging/macos/build.sh` to accept an optional identity string: `--sign [identity]` (currently reads only from `DEVELOPER_ID_APP` env var; update to accept inline value and fall back to env var, then auto-detect)
- [ ] T006 Implement `detect_signing_certificate()` function in `packaging/macos/build.sh`: runs `security find-identity -v -p codesigning | grep "Developer ID Application"`, returns single cert or prompts on multiple, exits with error code 1001 if none found when identity required
- [ ] T007 Add `--verbose` flag to `packaging/macos/build.sh` argument parsing; gate all `codesign --verbose` output behind it; default: summary only
- [ ] T008 Replace existing `--entitlements packaging/macos/entitlements.plist` references in `packaging/macos/build.sh` with `entitlements-app.plist` for app bundle signing and `entitlements-dmg.plist` for DMG signing

**Checkpoint**: `build.sh` accepts `--sign [identity]`, auto-detects certs, `--verbose` flag wired, new entitlements files referenced.

---

## Phase 3: User Story 1 — Developer ID App Bundle + DMG Signing (Priority: P1) 🎯 MVP

**Goal**: Running `./packaging/macos/build.sh --version 1.0.0 --sign "Developer ID Application: ..."` signs both the app bundle and DMG with a Developer ID certificate. Gatekeeper accepts the DMG on any Mac.

**Independent Test**: `codesign -vvv dist/macos/IntervalsICU.app` shows Developer ID chain; `codesign -v dist/macos/IntervalsICU-1.0.0.dmg` exits 0; `spctl --assess dist/macos/IntervalsICU-1.0.0.dmg` returns `accepted` (quickstart.md Scenario 2).

### Implementation for User Story 1

- [ ] T009 [US1] Implement app bundle signing block in `packaging/macos/build.sh`: after PyInstaller builds `${APP_PATH}`, call `codesign --deep --force --options runtime --sign "${SIGNING_IDENTITY}" --entitlements packaging/macos/entitlements-app.plist "${APP_PATH}"`
- [ ] T010 [P] [US1] Add post-sign app bundle verification in `packaging/macos/build.sh`: `codesign -v "${APP_PATH}"` — fail build with error code 2005 if invalid
- [ ] T011 [US1] Implement DMG signing block in `packaging/macos/build.sh`: after `create-dmg` produces `${DMG_PATH}`, call `codesign --force --sign "${SIGNING_IDENTITY}" --entitlements packaging/macos/entitlements-dmg.plist "${DMG_PATH}"`
- [ ] T012 [P] [US1] Add post-sign DMG verification in `packaging/macos/build.sh`: `codesign -v "${DMG_PATH}"` — fail build with error code 2005 if invalid
- [ ] T013 [US1] Implement error handler for signing failures in `packaging/macos/build.sh`: catch non-zero exit from `codesign`, print error code + recovery steps (check cert name, check disk space, check file permissions), exit with code 2001

**Checkpoint**: `./packaging/macos/build.sh --sign "Developer ID Application: ..."` produces a signed app bundle and signed DMG. Both pass `codesign -v`.

---

## Phase 4: User Story 2 — Apple Notarization + Stapling (Priority: P1)

**Goal**: Running `./packaging/macos/build.sh --sign "..." --notarize` submits the signed DMG to Apple's Notary Service, waits for approval, and staples the ticket. The final DMG passes `xcrun stapler validate` and `spctl --assess` returns `Notarized Developer ID`.

**Independent Test**: `xcrun stapler validate dist/macos/IntervalsICU-1.0.0.dmg` returns "already stapled"; `spctl --assess --verbose dist/macos/IntervalsICU-1.0.0.dmg` returns `accepted  source=Notarized Developer ID` (quickstart.md Scenario 3).

### Implementation for User Story 2

- [ ] T014 [US2] Add `--notarize` flag guard in `packaging/macos/build.sh`: when `--notarize` set, validate that `APPLE_ID`, `APPLE_TEAM_ID`, and `APPLE_APP_PASSWORD` env vars are present; fail with error code 3002 and setup instructions if missing
- [ ] T015 [US2] Implement notarization submission in `packaging/macos/build.sh`: call `xcrun notarytool submit "${DMG_PATH}" --apple-id "${APPLE_ID}" --team-id "${APPLE_TEAM_ID}" --password "${APPLE_APP_PASSWORD}" --wait` after DMG signing completes; capture and display submission ID
- [ ] T016 [US2] Implement notarization result handling in `packaging/macos/build.sh`: parse `notarytool` exit code — exit 0 → proceed to staple; non-zero → print error code 3004 (rejected) or 3005 (timeout) with Apple submission ID and recovery steps
- [ ] T017 [US2] Implement stapling in `packaging/macos/build.sh`: on notarization approval, call `xcrun stapler staple "${DMG_PATH}"`; verify with `xcrun stapler validate "${DMG_PATH}"`; fail with error code 3006 if staple fails
- [ ] T018 [P] [US2] Add verbose notarization output in `packaging/macos/build.sh`: when `--verbose` set, print submission ID, polling status, approval timestamp, and staple confirmation

**Checkpoint**: `./packaging/macos/build.sh --sign "..." --notarize` produces a notarized, stapled DMG. `xcrun stapler validate` passes.

---

## Phase 5: User Story 3 — Developer UX: Ad-hoc Fallback + Warning (Priority: P2)

**Goal**: Running `./packaging/macos/build.sh --version 1.0.0` (no `--sign`) succeeds with ad-hoc signatures on both app bundle and DMG, and prints a prominent warning block with step-by-step certificate setup instructions.

**Independent Test**: `./packaging/macos/build.sh --version 1.0.0` exits 0; output contains warning block with `developer.apple.com/developer-id` URL; `codesign -dv dist/macos/IntervalsICU.app` shows `Signature=adhoc`; `codesign -dv dist/macos/IntervalsICU-1.0.0.dmg` shows `Signature=adhoc` (quickstart.md Scenario 1).

### Implementation for User Story 3

- [ ] T019 [US3] Implement ad-hoc fallback signing path in `packaging/macos/build.sh`: when no `--sign` and no cert auto-detected, sign app bundle with `codesign --deep --force --options runtime --sign - --entitlements packaging/macos/entitlements-app.plist "${APP_PATH}"` and DMG with `codesign --force --sign - "${DMG_PATH}"`
- [ ] T020 [US3] Implement prominent warning block output in `packaging/macos/build.sh` for ad-hoc builds: print bordered warning (using `echo` with `⚠️` and `═` characters) containing: reason why warnings will appear, `developer.apple.com/developer-id` URL, 3-step certificate setup instructions, exact `--sign` flag syntax to use once cert installed
- [ ] T021 [P] [US3] Remove legacy `ensure_dev_cert()` self-signed certificate function from `packaging/macos/build.sh` (replaced by ad-hoc fallback in T019 and Developer ID path in Phase 3)
- [ ] T022 [P] [US3] Update build.sh header comment block to document new `--sign [identity]`, `--notarize`, `--verbose`, and `--no-sign` flags with usage examples

**Checkpoint**: Unsigned builds succeed with ad-hoc + warning block. `codesign -dv` confirms ad-hoc signature. Warning includes cert setup URL and `--sign` syntax.

---

## Final Phase: Polish & Validation

**Purpose**: Verify end-to-end behaviour, clean up, update documentation.

- [ ] T023 Run quickstart.md Scenario 1 (dev build, ad-hoc): `./packaging/macos/build.sh --version 1.0.0` — confirm warning block present, ad-hoc signatures valid, DMG mounts
- [ ] T024 Run quickstart.md Scenario 4 (entitlements validation): `plutil -lint` both plist files; `codesign -d --entitlements -` on signed app bundle confirms correct keys embedded
- [ ] T025 [P] Run quickstart.md Scenario 6 (error handling): `./packaging/macos/build.sh --sign "Developer ID Application: Nobody (FAKE)"` — confirm non-zero exit and error 1001 message
- [ ] T026 [P] Update `packaging/macos/README.md` with new `--sign [identity]`, `--notarize`, `--verbose` flag documentation and certificate setup prerequisites
- [ ] T027 [P] Update `README.md` "Build & Deploy" section: document that production builds require `--sign "Developer ID Application: ..."` flag and link to certificate setup guide
- [ ] T028 Run `bash -n packaging/macos/build.sh` to confirm no syntax errors; run `shellcheck packaging/macos/build.sh` if available
- [ ] T029 Commit final implementation; push branch `003-dmg-code-signing`

**Checkpoint**: ✅ All acceptance criteria from spec.md met. Feature ready for merge.

---

## Dependencies & Execution Order

```
T001-T004 (Setup: entitlements files)
    ↓
T005-T008 (Foundational: build.sh refactor)
    ├→ T009-T013 (US1: Developer ID signing — app + DMG)
    │       ↓
    │   T014-T018 (US2: Notarization + stapling; depends on signed DMG from US1)
    │
    └→ T019-T022 (US3: Ad-hoc fallback + warning; parallel to US1/US2)
    ↓
T023-T029 (Polish & validation)
```

### Parallel Execution Per Story

**US1** (once T005-T008 done): T009 → T010+T012 in parallel → T011 → T013  
**US2** (once T009-T013 done): T014 → T015 → T016 → T017 → T018  
**US3** (once T005-T008 done): T019 → T020 → T021+T022 in parallel  
**Final**: T023 → T024+T025+T028 in parallel → T026+T027 in parallel → T029

---

## Implementation Strategy

**MVP Scope** (User Story 1 only — T001-T013): Delivers Developer ID signing for both app bundle and DMG. This is the minimum to eliminate the Gatekeeper warning for production distribution once a certificate is obtained.

**Full Scope** (all phases — T001-T029): Adds notarization (Apple-verified, stapled), improved developer UX with ad-hoc fallback warnings, and full documentation. Recommended since cert setup is in progress.

**Current Blocker**: No Developer ID certificate available yet. T001-T022 can all be implemented and validated with ad-hoc signing (Scenario 1 and 6). T009-T013 and T014-T018 require a valid cert for final Gatekeeper acceptance testing (Scenarios 2-5).
