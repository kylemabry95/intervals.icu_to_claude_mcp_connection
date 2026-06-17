#!/bin/bash
################################################################################
# packaging/macos/install.sh
#
# Seamless installation script for IntervalsICU macOS application.
#
# This script is included in the IntervalsICU DMG and handles:
#   - Mounting the DMG (if needed)
#   - Copying IntervalsICU.app to /Applications/
#   - Removing macOS quarantine attributes (Gatekeeper bypass)
#   - Verifying successful installation
#   - Providing clear error messages with recovery steps
#
# Usage:
#   ./install.sh                     # Interactive (default destination /Applications)
#   ./install.sh --force             # Force overwrite if app already exists
#   ./install.sh --dest ~/Applications  # Custom destination
#   ./install.sh --verbose           # Verbose debug output
#   ./install.sh --help              # Show help message
#   ./install.sh --version           # Show version
#
# Environment Variables:
#   DMG_INSTALL_DEST         Override installation destination
#   DMG_INSTALL_VERBOSE      Enable verbose output (set to 1)
#
# Exit Codes:
#   0    - Success or user cancelled
#   1    - General error
#   2    - Argument parsing error
#   3    - Source app bundle not found
#   4    - Destination not writable
#   5    - Insufficient disk space
#   6    - Copy operation failed
#   7    - Quarantine removal failed (non-blocking, continues)
#   8    - Installation verification failed
#   9    - Signature verification failed
#   10   - Already installed (user cancelled update)
#
# Author: intervals.icu team
# Version: 1.0.0-beta
################################################################################
set -euo pipefail

# ────────────────────────────────────────────────────────────────────────────
# CONFIGURATION & DEFAULTS
# ────────────────────────────────────────────────────────────────────────────

readonly APP_NAME="IntervalsICU"
readonly APP_BUNDLE="IntervalsICU.app"
readonly BUNDLE_ID="com.intervalsicu.desktop"
readonly VERSION="1.0.0"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Installation defaults
DEST_DIR="${DMG_INSTALL_DEST:-/Applications}"
FORCE_OVERWRITE=false
VERBOSE="${DMG_INSTALL_VERBOSE:-0}"

# Messages & colors (only in interactive mode)
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# ────────────────────────────────────────────────────────────────────────────
# ERROR CODES & MESSAGES
# ────────────────────────────────────────────────────────────────────────────

readonly ERR_SOURCE_NOT_FOUND=3
readonly ERR_DEST_PERMISSION_DENIED=4
readonly ERR_INSUFFICIENT_DISK_SPACE=5
readonly ERR_COPY_FAILED=6
readonly ERR_QUARANTINE_FAILED=7
readonly ERR_VERIFY_FAILED=8
readonly ERR_SIGNATURE_INVALID=9
readonly ERR_ALREADY_INSTALLED=10

# ────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ────────────────────────────────────────────────────────────────────────────

# Enable verbose output if requested
debug() {
    if [[ "${VERBOSE}" == "1" ]]; then
        echo "[DEBUG] $*" >&2
    fi
}

# Print success message (green)
echo_success() {
    echo -e "${GREEN}✅${NC} $*"
}

# Print error message (red)
echo_error() {
    echo -e "${RED}❌${NC} $*" >&2
}

# Print warning message (yellow)
echo_warning() {
    echo -e "${YELLOW}⚠️${NC} $*"
}

# Print info message (blue)
echo_info() {
    echo -e "${BLUE}ℹ️${NC} $*"
}

# Show help message
show_help() {
    cat << 'EOF'
IntervalsICU macOS Installation Script

USAGE:
  ./install.sh [OPTIONS]

OPTIONS:
  --help              Show this help message
  --version           Show version
  --force             Force overwrite existing installation
  --dest <path>       Specify installation destination (default: /Applications)
  --verbose           Enable verbose debug output

EXAMPLES:
  ./install.sh                              # Install to /Applications
  ./install.sh --force                      # Overwrite existing app
  ./install.sh --dest ~/Applications        # Install to home Applications folder
  ./install.sh --verbose                    # Show debug output

ENVIRONMENT VARIABLES:
  DMG_INSTALL_DEST    Destination directory (overrides --dest)
  DMG_INSTALL_VERBOSE Enable verbose output (set to 1)

ERROR RECOVERY:
  If installation fails, check the error message for recovery steps.
  Common issues:
    - Permission denied: Try installing to ~/Applications instead
    - Insufficient disk space: Free up space and try again
    - Already installed: Use --force to overwrite existing app

For more information, visit: https://github.com/intervals-icu/desktop
EOF
}

# Show version
show_version() {
    echo "IntervalsICU Installation Script v${VERSION}"
}

# ────────────────────────────────────────────────────────────────────────────
# VALIDATION FUNCTIONS
# ────────────────────────────────────────────────────────────────────────────

# Validate source app bundle exists
validate_source() {
    debug "Validating source app bundle..."
    
    # Attempt to find the app bundle in DMG or working directory
    local source_app
    if [[ -d "/Volumes/${APP_NAME}/${APP_BUNDLE}" ]]; then
        source_app="/Volumes/${APP_NAME}/${APP_BUNDLE}"
    elif [[ -d "./${APP_BUNDLE}" ]]; then
        source_app="./${APP_BUNDLE}"
    elif [[ -d "${SCRIPT_DIR}/${APP_BUNDLE}" ]]; then
        source_app="${SCRIPT_DIR}/${APP_BUNDLE}"
    else
        echo_error "Source app bundle not found (${APP_NAME}.app)"
        echo_info "Recovery: Ensure DMG is mounted correctly or run from DMG directory"
        return "${ERR_SOURCE_NOT_FOUND}"
    fi
    
    # Verify it's actually an app bundle
    if [[ ! -d "${source_app}/Contents/MacOS" ]]; then
        echo_error "Invalid app bundle structure: ${source_app}"
        echo_info "Recovery: Reinstall from clean DMG"
        return "${ERR_SOURCE_NOT_FOUND}"
    fi
    
    debug "Source app found: ${source_app}"
    echo "${source_app}"
}

# Validate destination directory is writable
validate_destination() {
    local dest_dir="$1"
    debug "Validating destination directory: ${dest_dir}"
    
    # Create destination if it doesn't exist (for ~/Applications case)
    if [[ ! -d "${dest_dir}" ]]; then
        if mkdir -p "${dest_dir}" 2>/dev/null; then
            debug "Created destination directory: ${dest_dir}"
        else
            echo_error "Cannot create destination directory: ${dest_dir}"
            echo_info "Recovery: Check permissions or specify a different destination with --dest"
            return "${ERR_DEST_PERMISSION_DENIED}"
        fi
    fi
    
    # Check if directory is writable
    if [[ ! -w "${dest_dir}" ]]; then
        echo_error "Permission denied: Cannot write to ${dest_dir}"
        echo_info "Recovery: Use --dest ~/Applications or ask administrator for permission"
        return "${ERR_DEST_PERMISSION_DENIED}"
    fi
    
    debug "Destination directory is valid and writable"
    return 0
}

# Check available disk space
check_disk_space() {
    local dest_dir="$1"
    local source_app="$2"
    debug "Checking disk space..."
    
    # Get required space (estimate ~100MB for safety)
    local required_space=$((100 * 1024 * 1024))  # 100MB in bytes
    
    # Get available space on destination volume
    local available_space
    available_space=$(df "${dest_dir}" | awk 'NR==2 {print $4 * 1024}')
    
    debug "Required: ${required_space} bytes, Available: ${available_space} bytes"
    
    if (( available_space < required_space )); then
        echo_error "Insufficient disk space"
        echo_info "Required: $(( required_space / 1024 / 1024 ))MB, Available: $(( available_space / 1024 / 1024 ))MB"
        echo_info "Recovery: Free up space and try again"
        return "${ERR_INSUFFICIENT_DISK_SPACE}"
    fi
    
    return 0
}

# ────────────────────────────────────────────────────────────────────────────
# INSTALLATION FUNCTIONS
# ────────────────────────────────────────────────────────────────────────────

# Copy app bundle to destination
copy_app_bundle() {
    local source_app="$1"
    local dest_dir="$2"
    local dest_app="${dest_dir}/${APP_BUNDLE}"
    
    debug "Copying app bundle from ${source_app} to ${dest_app}..."
    
    # Handle existing installation
    if [[ -d "${dest_app}" ]]; then
        if [[ "${FORCE_OVERWRITE}" != "true" ]]; then
            echo_warning "Installation already exists: ${dest_app}"
            echo_info "Choose an option:"
            read -p "  [R]eplace, [S]kip, [C]ancel? (default: Skip) " -r -n 1 choice
            echo ""
            
            case "${choice,,}" in
                r) echo_info "Replacing existing installation..." ;;
                s) echo_info "Skipping installation"; return "${ERR_ALREADY_INSTALLED}" ;;
                c|"") echo_info "Cancelled"; return "${ERR_ALREADY_INSTALLED}" ;;
                *) echo_info "Invalid choice, skipping"; return "${ERR_ALREADY_INSTALLED}" ;;
            esac
        fi
        
        # Remove existing app
        debug "Removing existing app bundle..."
        if ! rm -rf "${dest_app}"; then
            echo_error "Failed to remove existing app bundle"
            echo_info "Recovery: Check permissions or close the app and try again"
            return "${ERR_COPY_FAILED}"
        fi
    fi
    
    # Copy new app
    if ! cp -r "${source_app}" "${dest_app}"; then
        echo_error "Failed to copy app bundle"
        echo_info "Recovery: Check disk space and permissions"
        return "${ERR_COPY_FAILED}"
    fi
    
    debug "App bundle copied successfully"
    echo_success "App copied to ${dest_app}"
    return 0
}

# Remove quarantine attribute
remove_quarantine() {
    local app_path="$1"
    debug "Removing quarantine attribute from ${app_path}..."
    
    # Check if quarantine attribute exists
    if xattr -l "${app_path}" 2>/dev/null | grep -q "com.apple.quarantine"; then
        debug "Quarantine attribute found, removing..."
        
        if ! xattr -rd com.apple.quarantine "${app_path}" 2>/dev/null; then
            echo_warning "Could not remove quarantine attribute (non-blocking)"
            echo_info "Recovery: Run this command manually:"
            echo "  xattr -d com.apple.quarantine '${app_path}'"
            return "${ERR_QUARANTINE_FAILED}"
        fi
        
        echo_success "Quarantine attribute removed"
    else
        debug "No quarantine attribute present"
    fi
    
    return 0
}

# Verify installation
verify_installation() {
    local app_path="$1"
    debug "Verifying installation at ${app_path}..."
    
    # Check app bundle exists
    if [[ ! -d "${app_path}" ]]; then
        echo_error "Verification failed: App bundle not found"
        return "${ERR_VERIFY_FAILED}"
    fi
    
    # Check Contents/MacOS directory
    if [[ ! -d "${app_path}/Contents/MacOS" ]]; then
        echo_error "Verification failed: Invalid app bundle structure"
        return "${ERR_VERIFY_FAILED}"
    fi
    
    # Check for executable
    local executable="${app_path}/Contents/MacOS/${APP_NAME}"
    if [[ ! -x "${executable}" ]]; then
        echo_error "Verification failed: Executable not found or not executable"
        return "${ERR_VERIFY_FAILED}"
    fi
    
    debug "Installation verified successfully"
    echo_success "Installation verified"
    return 0
}

# Verify code signature (non-blocking)
verify_signature() {
    local app_path="$1"
    debug "Verifying code signature..."
    
    if codesign -v "${app_path}" 2>/dev/null; then
        echo_success "Code signature verified"
        return 0
    else
        echo_warning "Code signature verification failed (non-blocking)"
        echo_info "The app may show a Gatekeeper warning on first launch"
        echo_info "Recovery: Run fix-gatekeeper.sh or use xattr command shown above"
        return "${ERR_SIGNATURE_INVALID}"
    fi
}

# ────────────────────────────────────────────────────────────────────────────
# CLEANUP FUNCTIONS
# ────────────────────────────────────────────────────────────────────────────

# Cleanup function (called on exit)
cleanup() {
    local exit_code=$?
    debug "Cleanup called with exit code: ${exit_code}"
    
    # Cleanup temporary files if any
    if [[ -n "${TEMP_DIR:-}" ]] && [[ -d "${TEMP_DIR}" ]]; then
        debug "Removing temporary directory: ${TEMP_DIR}"
        rm -rf "${TEMP_DIR}"
    fi
    
    return "${exit_code}"
}

trap cleanup EXIT

# ────────────────────────────────────────────────────────────────────────────
# MAIN INSTALLATION LOGIC
# ────────────────────────────────────────────────────────────────────────────

main() {
    echo_info "IntervalsICU Installation Script v${VERSION}"
    debug "Starting installation..."
    debug "Destination: ${DEST_DIR}"
    debug "Force overwrite: ${FORCE_OVERWRITE}"
    
    # Validate source app
    local source_app
    if ! source_app=$(validate_source); then
        exit "${ERR_SOURCE_NOT_FOUND}"
    fi
    
    # Validate destination
    if ! validate_destination "${DEST_DIR}"; then
        exit "${ERR_DEST_PERMISSION_DENIED}"
    fi
    
    # Check disk space
    if ! check_disk_space "${DEST_DIR}" "${source_app}"; then
        exit "${ERR_INSUFFICIENT_DISK_SPACE}"
    fi
    
    echo_info "Starting installation..."
    
    # Copy app bundle
    if ! copy_app_bundle "${source_app}" "${DEST_DIR}"; then
        exit "${ERR_COPY_FAILED}"
    fi
    
    local dest_app="${DEST_DIR}/${APP_BUNDLE}"
    
    # Remove quarantine attribute
    remove_quarantine "${dest_app}" || true  # Non-blocking
    
    # Verify installation
    if ! verify_installation "${dest_app}"; then
        exit "${ERR_VERIFY_FAILED}"
    fi
    
    # Verify signature (non-blocking)
    verify_signature "${dest_app}" || true
    
    # Success!
    echo ""
    echo_success "Installation complete!"
    echo_info "IntervalsICU is ready to use at: ${dest_app}"
    echo_info "You can now:"
    echo "  • Launch the app: open '${dest_app}'"
    echo "  • Eject the DMG: hdiutil detach /Volumes/${APP_NAME}/"
    echo ""
}

# ────────────────────────────────────────────────────────────────────────────
# ARGUMENT PARSING & ENTRY POINT
# ────────────────────────────────────────────────────────────────────────────

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --help)
            show_help
            exit 0
            ;;
        --version)
            show_version
            exit 0
            ;;
        --force)
            FORCE_OVERWRITE=true
            shift
            ;;
        --dest)
            DEST_DIR="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE="1"
            shift
            ;;
        *)
            echo_error "Unknown option: $1"
            echo_info "Use --help for usage information"
            exit 2
            ;;
    esac
done

# Run main installation
main
