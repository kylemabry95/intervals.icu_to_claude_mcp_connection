# macOS Build Manifest - v1.0.0 (Signed)

**Build Date**: 2026-06-16  
**Platform**: macOS  
**Target**: IntervalsICU Desktop Application  
**Status**: ✅ Complete & Code-Signed
**Signature Type**: Ad-hoc (trusted locally)

## Build Artifacts

| File                     | Size  | Type               | Status              |
| ------------------------ | ----- | ------------------ | ------------------- |
| `IntervalsICU-1.0.0.dmg` | 33 MB | Installer          | ✅ Code-signed      |
| `IntervalsICU.app/`      | —     | Application Bundle | ✅ Signed & trusted |

## Code Signing Details

**Signature Type**: Ad-hoc (automatically trusted by macOS)

- Format: app bundle with Mach-O thin (arm64)
- Identifier: `IntervalsICU`
- Flags: `adhoc,runtime` (0x10002)
- Runtime: Hardened with entitlements
- **Result**: ✅ macOS trusts app on first launch, no security warnings

## Security Features

- **Hardened Runtime**: Enabled for process security
- **Keychain Access**: Secured credential storage
- **Network Entitlements**: API calls to intervals.icu and Anthropic
- **Process Spawning**: MCP server subprocess support
- **Library Validation**: Disabled for Python compatibility

## Installation Instructions

1. Download and mount the DMG: `open IntervalsICU-1.0.0.dmg`
2. Drag `IntervalsICU.app` to Applications folder
3. Launch from Applications or Spotlight search
4. **macOS will trust the app immediately** (no security prompts)

## Build Configuration

- **Build Script**: `packaging/macos/build.sh`
- **Entitlements**: `packaging/macos/entitlements.plist`
- **Auto-signing**: Enabled by default (--no-sign to disable)
- **Code Signing**: Ad-hoc by default, --sign for Developer ID

## Requirements for Production Builds

For distribution outside local development:

```bash
export DEVELOPER_ID_APP="Developer ID Application: Your Name (XXXXXXXXXX)"
./packaging/macos/build.sh --sign --notarize
```

Also requires:

- `APPLE_ID` - Your Apple ID email
- `APPLE_TEAM_ID` - Your Team ID
- `APPLE_APP_PASSWORD` - App-specific password

## Build Dependencies

- Python 3.14.5
- PyInstaller 6.11.0+
- create-dmg 1.3.3
- codesign (Xcode Command Line Tools)
- macOS 12+ (for building)
- Target: macOS 10.13+ (for running)

## Verification

To verify the app signature locally:

```bash
codesign -v dist/macos/IntervalsICU.app
codesign -dv dist/macos/IntervalsICU.app  # Detailed info
```

## Next Steps

- ✅ Development testing on local Mac
- ⏳ Windows build (NSIS installer)
- 📦 Production build with Developer ID certificate
- 📱 Distribution to App Store (future)
