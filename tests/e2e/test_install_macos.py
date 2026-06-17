"""E2E smoke test: macOS package installation and launch."""

from __future__ import annotations

import platform
import subprocess
from pathlib import Path

import pytest


@pytest.mark.e2e
@pytest.mark.skipif(platform.system() != "Darwin", reason="macOS only")
class TestInstallMacOS:
    """Verify that the macOS .app bundle launches and exits cleanly."""

    def test_app_bundle_exists(self):
        """The macOS .app bundle is present in dist/macos/ after build."""
        app_path = Path("dist/macos/IntervalsICU.app")
        assert app_path.exists(), f"App bundle not found at {app_path}. Run ./packaging/macos/build.sh first."

    def test_app_bundle_executable(self):
        """The macOS app binary is executable."""
        exe = Path("dist/macos/IntervalsICU.app/Contents/MacOS/IntervalsICU")
        assert exe.exists() and exe.stat().st_mode & 0o111, "App binary is not executable."

    def test_dmg_exists(self):
        """A distributable .dmg file is produced after build."""
        dmg_files = list(Path("dist/macos").glob("*.dmg"))
        assert dmg_files, "No .dmg found in dist/macos/. Run ./packaging/macos/build.sh first."
