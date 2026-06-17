# packaging/macos

Build and packaging tools for IntervalsICU macOS application distribution.

## Directory Structure

```
packaging/macos/
├── build.sh              # Main DMG build script
├── install.sh            # Installation script (included in DMG)
├── install.sh.test       # Test harness for install.sh
├── fix-gatekeeper.sh     # User helper for Gatekeeper workaround
├── entitlements.plist    # macOS code signing entitlements
└── README.md             # This file
```

## Build Tools

### build.sh

Master script for building and packaging the IntervalsICU desktop application as a distributable DMG file.

**Features:**

- Creates .app bundle using PyInstaller
- Code-signs for macOS Gatekeeper
- Packages as DMG with create-dmg
- Optional notarization support (macOS 10.15+)
- Development and production modes

**Dependencies:**

- Python 3.10+
- PyInstaller: `pip install pyinstaller`
- create-dmg: `brew install create-dmg`
- Xcode Command Line Tools (includes codesign)

**Usage:**

```bash
# Development build (auto ad-hoc signed)
./build.sh

# Development build with custom version
./build.sh --version 1.0.0

# Production build (Developer ID signing)
./build.sh --sign

# Production build with notarization
./build.sh --sign --notarize

# Skip code signing entirely
./build.sh --no-sign
```

**Output:**

- `dist/macos/IntervalsICU.app` - Application bundle
- `dist/macos/IntervalsICU-X.Y.Z.dmg` - Distributable DMG file
- `dist/macos/BUILD_MANIFEST.md` - Build information and signing details

**Signing Options:**

| Flag        | Behavior                                       | Use Case            |
| ----------- | ---------------------------------------------- | ------------------- |
| (default)   | Ad-hoc signature + quarantine removal guidance | Local development   |
| `--sign`    | Developer ID certificate (production)          | Public distribution |
| `--no-sign` | No signing, users must handle Gatekeeper       | CI/testing          |

**Development Workflow:**

1. Make code changes
2. Run `./build.sh --version 1.0.0` to create DMG
3. Test via mounted DMG: `hdiutil attach dist/macos/IntervalsICU-1.0.0.dmg`
4. Run `./install.sh` from mounted volume
5. Verify app launches without Gatekeeper warnings

### install.sh

Installation script that provides seamless one-click installation experience for users.

**Features:**

- Automatic app bundle copying to /Applications
- Gatekeeper quarantine attribute removal
- Error handling with helpful recovery steps
- Permission checking and disk space validation
- User prompts for existing installations

**Dependencies:**

- macOS built-in tools: `xattr`, `codesign`, `hdiutil`
- Bash 4.0+
- No external dependencies

**Usage:**

```bash
# Interactive installation (mounts DMG, runs installer)
./install.sh

# Force overwrite existing app
./install.sh --force

# Install to alternate location
./install.sh --dest ~/Applications

# Verbose debug output
./install.sh --verbose

# Show help
./install.sh --help
```

**Environment Variables:**

| Variable              | Purpose                                |
| --------------------- | -------------------------------------- |
| `DMG_INSTALL_DEST`    | Override installation destination      |
| `DMG_INSTALL_VERBOSE` | Enable verbose debug output (set to 1) |

**Exit Codes:**

| Code | Meaning                                  | Recovery                                    |
| ---- | ---------------------------------------- | ------------------------------------------- |
| 0    | Success or user cancelled                | Installation complete or user cancelled     |
| 1    | General error                            | See error message                           |
| 3    | Source app not found                     | Ensure DMG is properly mounted              |
| 4    | Permission denied                        | Use `--dest ~/Applications` or run as admin |
| 5    | Insufficient disk space                  | Free up space and retry                     |
| 6    | Copy failed                              | Check permissions and disk space            |
| 7    | Quarantine removal failed (non-blocking) | Run fix-gatekeeper.sh manually              |
| 8    | Verification failed                      | Reinstall from fresh DMG                    |
| 9    | Signature verification failed (warning)  | May see Gatekeeper warning on launch        |
| 10   | Already installed                        | Use `--force` to overwrite                  |

**Development Testing:**

```bash
# Test in development (from within DMG mount)
cd /Volumes/IntervalsICU
./install.sh

# Test with verbose output
./install.sh --verbose

# Test with custom destination
./install.sh --dest ~/.test-apps

# Test force overwrite
./install.sh --force

# Test permission error scenario
./install.sh --dest /root  # Should fail with permission error
```

### install.sh.test

Local test harness for validating install.sh functionality without a mounted DMG.

**Features:**

- Syntax validation
- Mock app bundle creation
- Argument parsing tests
- Help and version output tests
- Shell linting (via shellcheck if available)

**Dependencies:**

- Bash 4.0+
- Optional: `shellcheck` for code linting (`brew install shellcheck`)

**Usage:**

```bash
# Run all tests
./install.sh.test

# Create test environment
./install.sh.test --setup

# Clean up test artifacts
./install.sh.test --clean

# Show help
./install.sh.test --help
```

**Test Coverage:**

- ✓ Shell script syntax validation
- ✓ Help output (`--help` flag)
- ✓ Version output (`--version` flag)
- ✓ Invalid argument handling
- ✓ Mock app bundle structure
- ✓ Fresh installation scenario
- ✓ Quarantine attribute detection
- ✓ Shellcheck linting (if available)

**Example Test Run:**

```bash
$ ./install.sh.test
═══════════════════════════════════════════════════════════════
IntervalsICU install.sh Test Suite
═══════════════════════════════════════════════════════════════

[TEST] Setting up test environment...
[PASS] Test environment ready
[TEST] Testing shell script syntax...
[PASS] Shell syntax valid
[TEST] Testing --help flag...
[PASS] Help output valid
...
═══════════════════════════════════════════════════════════════
Test Results: 8 run, 8 passed, 0 failed
═══════════════════════════════════════════════════════════════
```

### fix-gatekeeper.sh

User helper script for manually removing macOS Gatekeeper quarantine attribute from installed app.

**Purpose:**

- Provides fallback mechanism if automated quarantine removal fails
- Included in DMG for user self-service
- Used as reference in error messages

**Usage:**

```bash
# Run from any location
./fix-gatekeeper.sh /Applications/IntervalsICU.app

# Or manually
xattr -rd com.apple.quarantine /Applications/IntervalsICU.app
```

**Technical Details:**

- Uses `xattr -rd com.apple.quarantine` to recursively remove quarantine attribute
- Idempotent (safe to run multiple times)
- Returns success even if attribute wasn't present
- Non-blocking failure (doesn't prevent app launch)

### entitlements.plist

macOS code signing entitlements configuration for the IntervalsICU application.

**Contents:**

- Hardened runtime (security.allow-dyld-environment-variables)
- Python subprocess spawning (security.allow-unsigned-executable-memory)
- Network access (outbound-connections)
- Keychain access (keychain-access-groups)

**Usage:**

- Referenced by `codesign` during code signing in build.sh
- Applied to app bundle during DMG creation
- Enables runtime features needed by IntervalsICU

## Build Workflow

### Local Development Build

```bash
# 1. Ensure dependencies installed
pip install pyinstaller
brew install create-dmg

# 2. Create DMG
./build.sh --version 1.0.0

# 3. Test installation
hdiutil attach dist/macos/IntervalsICU-1.0.0.dmg
/Volumes/IntervalsICU/install.sh
open /Applications/IntervalsICU.app
hdiutil detach /Volumes/IntervalsICU
```

### Production Build (Developer ID Signing)

```bash
# 1. Export Developer ID signing certificate
# (See Xcode documentation for setup)

# 2. Build with production signing
DEVELOPER_ID_APP="Developer ID Application: Your Name" \
  ./build.sh --version 1.0.0 --sign

# 3. Optional: Notarize (requires Apple Developer account)
APPLE_ID="your-email@example.com" \
APPLE_TEAM_ID="XXXXXXXXXX" \
APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx" \
  ./build.sh --version 1.0.0 --sign --notarize
```

### Continuous Integration

For CI/CD environments where code signing isn't available:

```bash
# Build without signing (users handle Gatekeeper)
./build.sh --version 1.0.0 --no-sign

# Or build with ad-hoc signing
./build.sh --version 1.0.0
```

## Troubleshooting

### Gatekeeper Warnings

If users see "can't be scanned for malware" error:

1. **First attempt:** Automatic (handled by install.sh)
   - install.sh removes quarantine attribute
   - App launches without warnings

2. **Fallback:** Manual removal
   - Provide `fix-gatekeeper.sh` script
   - Users run: `./fix-gatekeeper.sh /Applications/IntervalsICU.app`

3. **Last resort:** Right-click trust
   - Users can right-click app in Finder
   - Select "Open" (forces trust dialog)
   - System adds app to trust list

### Code Signing Issues

**Issue:** `codesign: error: Can't find certificate`

**Solution:**

- Ensure developer certificate is installed
- Check with: `security find-certificate -c "IntervalsICU Developer"`
- If missing, run: `./build.sh --no-sign` and user manual method

**Issue:** Notarization fails

**Solution:**

- Verify Apple Developer account credentials
- Check Apple ID is in AppleDeveloper program
- Ensure app binary is properly signed before notarization

### Build Issues

**Issue:** `create-dmg: command not found`

**Solution:** `brew install create-dmg`

**Issue:** `PyInstaller: command not found`

**Solution:** `pip install pyinstaller`

## Version Control

These scripts are **version-controlled** in `.gitignore` with explicit includes:

```gitignore
!packaging/macos/
!packaging/macos/*.sh
!packaging/macos/*.plist
```

This ensures:

- All build scripts are tracked
- No accidental commits of dist/ artifacts
- install.sh and fix-gatekeeper.sh included in DMG

## Testing

Run the test suite to validate install.sh before releasing:

```bash
./install.sh.test
```

Run complete E2E testing:

```bash
# See specs/002-seamless-dmg-install/quickstart.md for full test scenarios
```

## Documentation

- **[BUILD_MANIFEST.md](../dist/macos/BUILD_MANIFEST.md)** - Details of built DMG
- **[specs/002-seamless-dmg-install/quickstart.md](../../specs/002-seamless-dmg-install/quickstart.md)** - Installation validation scenarios
- **[README.md](../../README.md)** - Main project documentation

## Related

- [intervals.icu Desktop Application](../../README.md)
- [Installation Guide](../../QUICKSTART.md)
- [Build & Release Notes](../../SETUP_NOTES.md)
