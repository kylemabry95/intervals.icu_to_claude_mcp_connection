"""
Desktop application entry point.

Bootstraps the desktop_app:
  1. Applies a single-instance guard (prevents duplicate processes).
  2. Loads and validates configuration from the environment / .env file.
  3. Starts the MCP server process.
  4. Opens the main UI window.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path


# ── Single-instance guard ─────────────────────────────────────────────────────
# Uses a lock file in the system temp directory to prevent running two copies.

_LOCK_FILE: Path = Path(tempfile.gettempdir()) / "intervals_icu_desktop.lock"
_lock_handle = None


def _acquire_single_instance_lock() -> bool:
    """Try to acquire the single-instance lock.

    Returns:
        True if this is the only running instance, False if another is alive.
    """
    global _lock_handle
    import platform

    if platform.system() == "Windows":
        import msvcrt

        try:
            _lock_handle = open(_LOCK_FILE, "w")  # noqa: WPS515
            msvcrt.locking(_lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False
    else:
        import fcntl

        try:
            _lock_handle = open(_LOCK_FILE, "w")  # noqa: WPS515
            fcntl.flock(_lock_handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False


def _release_single_instance_lock() -> None:
    global _lock_handle
    if _lock_handle:
        try:
            _lock_handle.close()
        except OSError:
            pass
        try:
            _LOCK_FILE.unlink(missing_ok=True)
        except OSError:
            pass


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    """Entry point for the standalone desktop application."""
    if not _acquire_single_instance_lock():
        print(
            "IntervalsICU is already running. Check your system tray.",
            file=sys.stderr,
        )
        sys.exit(0)

    try:
        from desktop_app.config import load_config
        from desktop_app.errors import AppError
        from desktop_app.runtime.startup import run_startup_sequence, shutdown
        from desktop_app.ui.shell import AppShell

        try:
            config = load_config()
            run_startup_sequence(config)
            shell = AppShell(config)
            shell.run()
        except AppError as exc:
            print(f"Fatal startup error: {exc}", file=sys.stderr)
            sys.exit(1)
        finally:
            shutdown()
    finally:
        _release_single_instance_lock()


if __name__ == "__main__":
    main()

