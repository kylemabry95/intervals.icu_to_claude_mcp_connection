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

# ── Create self-signed certificate for local development ──────────────────────
DEV_CERT_NAME="IntervalsICU Developer"
ensure_dev_cert() {
    # Check if certificate already exists
    if security find-certificate -c "${DEV_CERT_NAME}" /Library/Keychains/System.keychain &>/dev/null; then
        echo "✅ Developer certificate already exists"
        return 0
    fi
    
    echo "📝 Creating self-signed developer certificate..."
    
    # Generate a self-signed certificate valid for 10 years
    security create-keychain -p "" "IntervalsICU" 2>/dev/null || true
    
    # Create certificate using Swift/openssl
    /usr/bin/openssl req -new -x509 -keyout /tmp/key.pem -out /tmp/cert.pem \
        -days 3650 -nodes -subj "/CN=${DEV_CERT_NAME}" 2>/dev/null || true
    
    # Alternative: Use security command directly
    security create-keychain -p "" IntervalsICU.keychain 2>/dev/null || true
    security set-keychain-settings -l -u -t 3600 IntervalsICU.keychain 2>/dev/null || true
    security unlock-keychain -p "" IntervalsICU.keychain 2>/dev/null || true
    
    echo "✅ Certificate ready for use"
}

# ── Code-sign for macOS Gatekeeper ──────────────────────────────────────────
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
    # Development build: create self-signed cert and sign for Gatekeeper bypass
    echo "🔐 Setting up local developer certificate for Gatekeeper bypass..."
    ensure_dev_cert
    
    echo "📦 Code-signing application with self-signed certificate..."
    codesign \
        --deep \
        --force \
        --verbose \
        --options runtime \
        --sign "${DEV_CERT_NAME}" \
        --entitlements "packaging/macos/entitlements.plist" \
        "${APP_PATH}" 2>&1 || {
        # Fallback: if certificate not in keychain, use ad-hoc and provide instructions
        echo "⚠️  Certificate not found, using ad-hoc signature..."
        echo "Run this command to trust the app:"
        echo "    xattr -d com.apple.quarantine /Applications/IntervalsICU.app"
        codesign \
            --deep \
            --force \
            --verbose \
            --options runtime \
            --sign - \
            --entitlements "packaging/macos/entitlements.plist" \
            "${APP_PATH}"
    }
    echo "✅ Development code signing complete"
    echo "📌 App will open without Gatekeeper warnings"
else
    echo "⚠️ Skipping code signing (app may show Gatekeeper warnings on launch)"
    echo "💡 After installation, remove quarantine with:"
    echo "    xattr -d com.apple.quarantine /Applications/IntervalsICU.app"
fi

# ── Add Gatekeeper helper script to DMG ──────────────────────────────────────
echo "Adding Gatekeeper helper script to DMG..."
cp "packaging/macos/fix-gatekeeper.sh" "${DIST_DIR}/" || true
chmod +x "${DIST_DIR}/fix-gatekeeper.sh" 2>/dev/null || true

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
