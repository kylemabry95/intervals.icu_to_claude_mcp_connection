# IntervalsICU macOS Build Manifest

**Build Version**: 1.0.0  
**Build Date**: 2024  
**Platform**: macOS (arm64)  
**DMG Size**: 33 MB

## Code Signing

**Signature Type**: Ad-hoc (development)  
**Signing Status**: ✅ Applied  
**Runtime Hardening**: Enabled

### Verification

To verify the app signature:

```bash
codesign -dv /Applications/IntervalsICU.app
```

Expected output includes: `Signature=adhoc` and `flags=0x10002(adhoc,runtime)`

## Security Features

- **Hardened Runtime**: Enabled for enhanced security
- **Entitlements**: Configured for Python subprocess spawning, network access, and Keychain integration
- **Quarantine Handling**: Documented method for users to remove quarantine attribute if needed

## Gatekeeper Workaround

If macOS blocks the app with "can't be scanned for malware" error:

### Quick Fix (Recommended)

```bash
xattr -d com.apple.quarantine /Applications/IntervalsICU.app
```

### Using Helper Script

From the mounted DMG:

```bash
./fix-gatekeeper.sh /Applications/IntervalsICU.app
```

### Manual Trust

1. Right-click IntervalsICU.app → Open
2. Click "Open" in the security dialog
3. App will be added to trusted apps

## Build Dependencies

- **PyInstaller** 6.11.0+ (Python application bundler)
- **create-dmg** 1.3.3 (DMG creator)
- **macOS codesign** (Apple code signing tool)
- **Python** 3.14+ with tkinter support

## Production Builds

For production distribution with Developer ID certificates:

- Requires Apple Developer account
- Notarization required for distribution outside Mac App Store
- Use `./build.sh --sign YOUR_DEVELOPER_ID --notarize`

## Contents

- **IntervalsICU.app**: Application bundle
- **IntervalsICU/**: Folder for Finder drag-and-drop installation
- **fix-gatekeeper.sh**: Helper script for Gatekeeper quarantine removal
- **BUILD_MANIFEST.md**: This file
