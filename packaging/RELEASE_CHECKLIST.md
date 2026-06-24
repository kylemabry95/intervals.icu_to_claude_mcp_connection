# Release Checklist

Use this checklist for every production release of the IntervalsICU desktop application.

## Pre-Build

- [ ] All tests pass: `pytest tests/ -v -m "not e2e"` → 0 failures
- [ ] SC-004 evaluation passes: `pytest tests/evaluation/ -v` → pass rate ≥ 95%
- [ ] All commits included in release are signed: `git log --show-signature --oneline origin/main..HEAD` shows valid signatures
- [ ] No hardcoded secrets in codebase: `git grep -r "API_KEY\|password\|secret" -- "*.py"` returns no real values
- [ ] `.env` is NOT committed: `git status` shows no `.env` file
- [ ] `requirements.txt` up to date and pinned to compatible versions
- [ ] `__version__` in `desktop_app/__init__.py` matches release version
- [ ] `CHANGELOG.md` updated with release notes

## macOS Build

- [ ] `./packaging/macos/build.sh --version X.Y.Z` completes without errors
- [ ] `dist/macos/IntervalsICU-X.Y.Z.dmg` exists and opens correctly
- [ ] App launches on a clean macOS 11+ system (VM or separate device)
- [ ] Sign: `./packaging/macos/build.sh --version X.Y.Z --sign` (requires Developer ID)
- [ ] Notarise: `./packaging/macos/build.sh --version X.Y.Z --sign --notarize`
- [ ] Gatekeeper passes: `spctl --assess --verbose dist/macos/IntervalsICU.app`

## Windows Build

- [ ] `.\packaging\windows\build.ps1 -Version X.Y.Z` completes without errors
- [ ] `dist\windows\IntervalsICU-X.Y.Z-Setup.exe` exists and installs cleanly
- [ ] App launches on a clean Windows 10 21H2+ system (VM or separate device)
- [ ] Sign: `.\packaging\windows\build.ps1 -Version X.Y.Z -Sign` (requires cert)
- [ ] Installer is flagged as safe by Windows SmartScreen

## Functional Verification (on built package)

- [ ] App launches to auth screen
- [ ] Valid API key + athlete ID signs in successfully
- [ ] Invalid API key shows a user-friendly error message
- [ ] Chat tab sends a query and receives a Claude response
- [ ] Settings can be saved and persisted across restart
- [ ] Log viewer in settings shows application logs
- [ ] Help tab shows FAQ and contextual help content
- [ ] Logout clears credentials (app returns to auth screen)

## Security

- [ ] Application logs contain no plaintext API keys (check via Log Viewer)
- [ ] Credentials are stored in system keychain (Keychain Access / Credential Manager)
- [ ] No `.env` or credential files included in installer package
- [ ] HTTPS used for all external requests (intervals.icu API, Anthropic API)

## Post-Release

- [ ] GitHub Release created with tag `vX.Y.Z`
- [ ] macOS DMG and Windows installer attached to GitHub Release
- [ ] SHA-256 checksums published in release notes
- [ ] `CHANGELOG.md` committed and pushed
