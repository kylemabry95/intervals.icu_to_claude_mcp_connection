"""E2E smoke test: Windows package installation and launch."""

from __future__ import annotations

import platform
from pathlib import Path

import pytest


@pytest.mark.e2e
@pytest.mark.skipif(platform.system() != "Windows", reason="Windows only")
class TestInstallWindows:
    """Verify that the Windows installer and executable are present after build."""

    def test_installer_exists(self):
        """The NSIS installer is present in dist/windows/ after build."""
        installer_files = list(Path("dist/windows").glob("*-Setup.exe"))
        assert installer_files, "No setup .exe found in dist/windows/. Run .\\packaging\\windows\\build.ps1 first."

    def test_app_executable_exists(self):
        """The standalone app .exe is present after build."""
        exe = Path("dist/windows/IntervalsICU/IntervalsICU.exe")
        assert exe.exists(), f"App executable not found at {exe}. Run .\\packaging\\windows\\build.ps1 first."
