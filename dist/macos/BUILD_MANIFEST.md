# macOS Build Manifest - v1.0.0

**Build Date**: 2026-06-16  
**Platform**: macOS  
**Target**: IntervalsICU Desktop Application  
**Status**: ✅ Complete

## Build Artifacts

| File                     | Size  | Type               | Status             |
| ------------------------ | ----- | ------------------ | ------------------ |
| `IntervalsICU-1.0.0.dmg` | 33 MB | Installer          | ✅ Complete        |
| `IntervalsICU.app/`      | —     | Application Bundle | ✅ Included in DMG |

## Build Configuration

- **Build Script**: `packaging/macos/build.sh`
- **PyInstaller**: Used for app bundling
- **Code Signing**: Not applied (--sign flag not used)
- **Notarization**: Not applied (--notarize flag not used)

## Installation Instructions

1. Mount the DMG: `open IntervalsICU-1.0.0.dmg`
2. Drag `IntervalsICU.app` to Applications folder
3. Launch from Applications or Spotlight search

## Requirements for Production Builds

- **Code Signing**: Requires `DEVELOPER_ID_APP` environment variable

  ```bash
  ./packaging/macos/build.sh --version 1.0.0 --sign
  ```

- **Notarization**: Requires Apple credentials:
  ```bash
  export APPLE_ID="your.email@example.com"
  export APPLE_TEAM_ID="XXXXXXXXXX"
  export APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"
  ./packaging/macos/build.sh --version 1.0.0 --sign --notarize
  ```

## Build Dependencies Used

- Python 3.14.5
- PyInstaller 6.11.0+
- create-dmg 1.3.3
- macOS Sonoma or later

## Next Steps

1. Test the DMG on target macOS versions (10.13+)
2. Verify app launch and credential storage
3. Run integration tests within the installed app
4. For production: Re-build with --sign and --notarize flags
