#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# packaging/macos/build.sh
#
# Builds and packages the intervals.icu standalone desktop application for
# macOS as a trusted .app bundle and distributable .dmg file.
#
# By default, automatically code-signs with ad-hoc signature so macOS trusts
# the application immediately (no security prompts on first launch).
#
# Requirements:
#   - Python 3.10+ installed (via Homebrew or python.org)
#   - PyInstaller: pip install pyinstaller
#   - create-dmg: brew install create-dmg
#   - codesign (included with Xcode Command Line Tools)
#
# Usage:
#   ./packaging/macos/build.sh                  # Development (auto ad-hoc signed, trusted locally)
#   ./packaging/macos/build.sh --version 1.0.0 # With custom version
#   ./packaging/macos/build.sh --sign           # Production (requires DEVELOPER_ID_APP env var)
#   ./packaging/macos/build.sh --no-sign        # Skip all code signing
#   ./packaging/macos/build.sh --sign --notarize # Production + notarize (requires credentials)
# ---------------------------------------------------------------------------
set -euo pipefail

# ── Defaults ────────────────────────────────────────────────────────────────
APP_NAME="IntervalsICU"
BUNDLE_ID="com.intervalsicu.desktop"
VERSION="${VERSION:-1.0.0}"
SIGN=false
DEV_SIGN=true
NOTARIZE=false
DIST_DIR="dist/macos"
BUILD_DIR="build/macos"

# ── Argument parsing ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --sign)        SIGN=true; DEV_SIGN=false ;;
        --no-sign)     DEV_SIGN=false            ;;
        --notarize)    NOTARIZE=true             ;;
        --version)     VERSION="$2"; shift      ;;
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
    --add-data "server.py:." \
    --distpath "${DIST_DIR}" \
    --workpath "${BUILD_DIR}" \
    --clean \
    desktop_app/main.py

APP_PATH="${DIST_DIR}/${APP_NAME}.app"

# ── Code-sign for macOS trust ────────────────────────────────────────────────
if [[ "${SIGN}" == "true" ]]; then
    # Production build with Developer ID certificate
    : "${DEVELOPER_ID_APP:?Set DEVELOPER_ID_APP to your Developer ID Application identity}"
    echo "🔐 Code-signing with Developer ID: ${DEVELOPER_ID_APP}"
    codesign \
        --deep \
        --force \
        --verbose \
        --options runtime \
        --sign "${DEVELOPER_ID_APP}" \
        --entitlements "packaging/macos/entitlements.plist" \
        "${APP_PATH}"
    echo "✅ Production code signing complete"
elif [[ "${DEV_SIGN}" == "true" ]]; then
    # Development build with ad-hoc signature (automatically trusted locally)
    echo "🔐 Applying ad-hoc code signature for local macOS trust..."
    codesign \
        --deep \
        --force \
        --verbose \
        --options runtime \
        --sign - \
        --entitlements "packaging/macos/entitlements.plist" \
        "${APP_PATH}"
    echo "✅ App is now trusted by macOS (ad-hoc signed)"
else
    echo "⚠️ Skipping code signing (app may show security warnings on launch)"
fi

# ── Create DMG ────────────────────────────────────────────────────────────────
DMG_PATH="${DIST_DIR}/${APP_NAME}-${VERSION}.dmg"
echo "Creating DMG at ${DMG_PATH} …"
create-dmg \
    --volname "${APP_NAME} ${VERSION}" \
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
