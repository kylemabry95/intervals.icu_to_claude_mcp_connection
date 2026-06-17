# ---------------------------------------------------------------------------
# packaging/windows/build.ps1
#
# Builds and packages the intervals.icu standalone desktop application for
# Windows as a signed NSIS/MSI installer.
#
# Requirements:
#   - Python 3.10+ (python.org installer, added to PATH)
#   - PyInstaller: pip install pyinstaller
#   - NSIS 3.x: https://nsis.sourceforge.io/
#   - signtool.exe from Windows SDK (optional, for code signing)
#
# Usage:
#   .\packaging\windows\build.ps1 [-Sign] [-Version "1.0.0"]
# ---------------------------------------------------------------------------
[CmdletBinding()]
param(
    [switch]$Sign,
    [string]$Version = "1.0.0"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$AppName   = "IntervalsICU"
$BundleId  = "com.intervalsicu.desktop"
$DistDir   = "dist\windows"
$BuildDir  = "build\windows"

Write-Host "Building $AppName v$Version for Windows ..." -ForegroundColor Cyan

# ── Clean previous artefacts ─────────────────────────────────────────────────
if (Test-Path $DistDir)  { Remove-Item $DistDir  -Recurse -Force }
if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
New-Item -ItemType Directory -Path $DistDir  -Force | Out-Null
New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null

# ── Build .exe with PyInstaller ───────────────────────────────────────────────
pyinstaller `
    --name $AppName `
    --windowed `
    --icon "packaging\windows\icon.ico" `
    --add-data "server.py;." `
    --distpath $DistDir `
    --workpath $BuildDir `
    --clean `
    desktop_app\main.py

$ExePath = "$DistDir\$AppName\$AppName.exe"

# ── Code-sign the executable (optional) ──────────────────────────────────────
if ($Sign) {
    $CertThumb = $env:WINDOWS_CERT_THUMBPRINT
    if (-not $CertThumb) { throw "Set WINDOWS_CERT_THUMBPRINT env var." }
    Write-Host "Signing $ExePath ..."
    signtool sign `
        /sha1 $CertThumb `
        /tr http://timestamp.digicert.com `
        /td sha256 `
        /fd sha256 `
        $ExePath
}

# ── Build NSIS installer ──────────────────────────────────────────────────────
$NsisScript = "packaging\windows\installer.nsi"
$InstallerPath = "$DistDir\${AppName}-${Version}-Setup.exe"

Write-Host "Building NSIS installer at $InstallerPath ..."
makensis `
    /DAPP_NAME=$AppName `
    /DAPP_VERSION=$Version `
    /DDIST_DIR="$((Get-Item $DistDir).FullName)" `
    /DOUTPUT_FILE="$((Get-Item $DistDir).FullName)\${AppName}-${Version}-Setup.exe" `
    $NsisScript

# ── Sign installer (optional) ─────────────────────────────────────────────────
if ($Sign) {
    Write-Host "Signing installer ..."
    signtool sign `
        /sha1 $env:WINDOWS_CERT_THUMBPRINT `
        /tr http://timestamp.digicert.com `
        /td sha256 `
        /fd sha256 `
        $InstallerPath
}

Write-Host "Build complete: $InstallerPath" -ForegroundColor Green
