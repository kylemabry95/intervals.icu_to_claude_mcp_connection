"""
Scheduled daily update-check service.

Runs a background thread that wakes once per day to check for a newer
version of the application.  When a new version is found, it emits a
callback with the version string so the UI can prompt the user.
The user can defer the update; the deferred state persists in the
SettingsRepository so the reminder is not repeated in the same day.
"""

from __future__ import annotations

import datetime
import threading
from typing import Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from desktop_app.settings.repository import SettingsRepository

# Update manifest URL (placeholder — replace with real endpoint on release)
_UPDATE_MANIFEST_URL = "https://api.github.com/repos/kylemabry95/intervals.icu_to_claude_mcp_connection/releases/latest"
_CHECK_INTERVAL_SECONDS = 60 * 60 * 24  # 24 hours
_PREF_KEY_LAST_CHECK = "last_update_check_date"
_PREF_KEY_DEFERRED_VERSION = "deferred_update_version"


class UpdateScheduler:
    """Daily background update checker.

    Args:
        settings_repo:    Persistent settings repository for storing check
                          date and deferred version.
        on_update_found:  Callback ``(version: str) -> None`` called when a
                          newer version is detected.
        enabled:          Whether update checking is active.
    """

    def __init__(
        self,
        settings_repo: Optional["SettingsRepository"],
        on_update_found: Optional[Callable[[str], None]] = None,
        enabled: bool = True,
    ) -> None:
        self._repo = settings_repo
        self._on_update_found = on_update_found
        self._enabled = enabled
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    # ── Public API ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the background update-check loop."""
        if not self._enabled:
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._loop, daemon=True, name="update-checker"
        )
        self._thread.start()

    def stop(self) -> None:
        """Stop the background loop."""
        self._stop_event.set()

    def defer(self, version: str) -> None:
        """Record that the user deferred the update for *version* today."""
        if self._repo:
            self._repo.set(_PREF_KEY_DEFERRED_VERSION, version)
            self._repo.set(_PREF_KEY_LAST_CHECK, str(datetime.date.today()))

    def check_now(self) -> Optional[str]:
        """Perform an immediate synchronous update check.

        Returns:
            The latest version string if a newer version exists, else None.
        """
        return self._fetch_latest_version()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _loop(self) -> None:
        while not self._stop_event.wait(timeout=_CHECK_INTERVAL_SECONDS):
            if self._should_check():
                version = self._fetch_latest_version()
                if version and self._on_update_found:
                    self._on_update_found(version)

    def _should_check(self) -> bool:
        """Return True if enough time has elapsed since the last check."""
        if not self._repo:
            return True
        last = self._repo.get(_PREF_KEY_LAST_CHECK)
        if not last:
            return True
        try:
            last_date = datetime.date.fromisoformat(last)
            return datetime.date.today() > last_date
        except ValueError:
            return True

    def _fetch_latest_version(self) -> Optional[str]:
        """Fetch the latest release version from GitHub releases API.

        Returns:
            Version string (e.g. ``"1.1.0"``) or None on failure.
        """
        try:
            import httpx  # noqa: PLC0415

            response = httpx.get(_UPDATE_MANIFEST_URL, timeout=10.0, follow_redirects=True)
            if response.status_code == 200:
                data = response.json()
                tag = data.get("tag_name", "")
                return tag.lstrip("v") if tag else None
        except Exception:
            pass
        return None
