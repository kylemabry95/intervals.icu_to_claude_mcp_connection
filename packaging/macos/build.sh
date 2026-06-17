#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# packaging/macos/build.sh
#
# Builds and packages the intervals.icu standalone desktop application for
# macOS as a notarized .app bundle and distributable .dmg file.
#
# Requirements:
#   - Python 3.10+ installed (via Homebrew or python.org)
#   - PyInstaller: pip install pyinstaller
#   - create-dmg: brew install create-dmg
#   - Apple Developer ID certificate (for notarisation)
#
# Usage:
#   ./packaging/macos/build.sh [--sign] [--notarize] [--version VERSION]
# ---------------------------------------------------------------------------
set -euo pipefail

# ── Defaults ────────────────────────────────────────────────────────────────
APP_NAME="IntervalsICU"
BUNDLE_ID="com.intervalsicu.desktop"
VERSION="${VERSION:-1.0.0}"
SIGN=false
NOTARIZE=false
DIST_DIR="dist/macos"
BUILD_DIR="build/macos"

# ── Argument parsing ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --sign)     SIGN=true       ;;
        --notarize) NOTARIZE=true   ;;
        --version)  VERSION="$2"; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
    shift
done

echo "Building ${APP_NAME} v${VERSION} for macOS …"

# ── Clean previous artefacts ─────────────────────────────────────────────────
rm -rf "${DIST_DIR}" "${BUILD_DIR}"
mkdir -p "${DIST_DIR}" "${BUILD_DIR}"

# ── Build .app with PyInstaller ───────────────────────────────────────────────
pyinstaller \
    --name "${APP_NAME}" \
    --windowed \
    --icon "packaging/macos/icon.icns" \
    --add-data "server.py:." \
    --distpath "${DIST_DIR}" \
    --workpath "${BUILD_DIR}" \
    --clean \
    desktop_app/main.py

APP_PATH="${DIST_DIR}/${APP_NAME}.app"

# ── Code-sign (optional) ──────────────────────────────────────────────────────
if [[ "${SIGN}" == "true" ]]; then
    : "${DEVELOPER_ID_APP:?Set DEVELOPER_ID_APP to your Developer ID Application identity}"
    echo "Signing ${APP_PATH} …"
    codesign \
        --deep \
        --force \
        --options runtime \
        --sign "${DEVELOPER_ID_APP}" \
        --entitlements "packaging/macos/entitlements.plist" \
        "${APP_PATH}"
fi

# ── Create DMG ────────────────────────────────────────────────────────────────
DMG_PATH="${DIST_DIR}/${APP_NAME}-${VERSION}.dmg"
echo "Creating DMG at ${DMG_PATH} …"
create-dmg \
    --volname "${APP_NAME} ${VERSION}" \
    --volicon "packaging/macos/icon.icns" \
    --window-pos 200 120 \
    --window-size 600 400 \
    --icon-size 100 \
    --icon "${APP_NAME}.app" 175 190 \
    --hide-extension "${APP_NAME}.app" \
    --app-drop-link 425 190 \
    "${DMG_PATH}" \
    "${DIST_DIR}/"

# ── Notarise (optional) ───────────────────────────────────────────────────────
if [[ "${NOTARIZE}" == "true" ]]; then
    : "${APPLE_ID:?Set APPLE_ID}"
    : "${APPLE_TEAM_ID:?Set APPLE_TEAM_ID}"
    : "${APPLE_APP_PASSWORD:?Set APPLE_APP_PASSWORD}"
    echo "Submitting DMG for notarisation …"
    xcrun notarytool submit "${DMG_PATH}" \
        --apple-id "${APPLE_ID}" \
        --team-id "${APPLE_TEAM_ID}" \
        --password "${APPLE_APP_PASSWORD}" \
        --wait
    xcrun stapler staple "${DMG_PATH}"
fi

echo "Build complete: ${DMG_PATH}"
