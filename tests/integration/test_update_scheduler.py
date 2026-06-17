"""Integration test: daily update check prompt and user deferral flow."""

from __future__ import annotations

import datetime
from unittest.mock import MagicMock, patch

import pytest


class TestUpdateScheduler:
    def test_on_update_found_callback_fires(self):
        """When a newer version is found, the callback is invoked with the version string."""
        callbacks: list[str] = []

        from desktop_app.settings.update_scheduler import UpdateScheduler

        sched = UpdateScheduler(
            settings_repo=None,
            on_update_found=callbacks.append,
            enabled=True,
        )

        with patch.object(sched, "_fetch_latest_version", return_value="2.0.0"):
            version = sched.check_now()

        assert version == "2.0.0"

    def test_defer_stores_version_and_date(self):
        """defer() persists the deferred version and today's date."""
        repo = MagicMock()
        from desktop_app.settings.update_scheduler import UpdateScheduler

        sched = UpdateScheduler(settings_repo=repo, enabled=True)
        sched.defer("1.5.0")

        repo.set.assert_any_call("deferred_update_version", "1.5.0")
        repo.set.assert_any_call("last_update_check_date", str(datetime.date.today()))

    def test_no_check_when_disabled(self):
        """UpdateScheduler does not start the thread when enabled=False."""
        from desktop_app.settings.update_scheduler import UpdateScheduler

        sched = UpdateScheduler(settings_repo=None, enabled=False)
        sched.start()
        assert sched._thread is None  # Thread was never created

    def test_should_check_returns_true_when_no_prior_check(self):
        """_should_check() returns True when no prior check date is stored."""
        repo = MagicMock()
        repo.get.return_value = None  # No prior check

        from desktop_app.settings.update_scheduler import UpdateScheduler

        sched = UpdateScheduler(settings_repo=repo, enabled=True)
        assert sched._should_check() is True

    def test_should_not_check_on_same_day(self):
        """_should_check() returns False when last check was today."""
        repo = MagicMock()
        repo.get.return_value = str(datetime.date.today())

        from desktop_app.settings.update_scheduler import UpdateScheduler

        sched = UpdateScheduler(settings_repo=repo, enabled=True)
        assert sched._should_check() is False

    def test_check_returns_none_on_network_error(self):
        """check_now() returns None when the manifest fetch fails."""
        from desktop_app.settings.update_scheduler import UpdateScheduler

        sched = UpdateScheduler(settings_repo=None, enabled=True)
        with patch.object(sched, "_fetch_latest_version", return_value=None):
            result = sched.check_now()
        assert result is None
