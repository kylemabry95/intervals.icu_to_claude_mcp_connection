"""
MCP server process manager.

Manages the lifecycle of the ``server.py`` MCP server subprocess:
  - start / stop
  - health polling
  - automatic restart on unexpected exit

The manager runs the server as a child process over stdio, which is the
transport used by the ``mcp`` package.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import threading
import time
from enum import Enum, auto
from pathlib import Path
from typing import Optional

from desktop_app.errors import MCPProcessError

# Path to the bundled MCP server script
_SERVER_SCRIPT = Path(__file__).parent.parent.parent / "server.py"

# How long (seconds) to wait for the process to exit on stop()
_STOP_TIMEOUT = 5.0

# Health-poll interval (seconds)
_HEALTH_POLL_INTERVAL = 2.0


class ProcessState(Enum):
    STOPPED = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    FAILED = auto()


class MCPProcessManager:
    """Manages the MCP server subprocess lifecycle."""

    def __init__(
        self,
        server_script: Path = _SERVER_SCRIPT,
        env: Optional[dict[str, str]] = None,
    ) -> None:
        self._server_script = server_script
        self._extra_env = env or {}
        self._process: Optional[subprocess.Popen] = None
        self._state = ProcessState.STOPPED
        self._lock = threading.Lock()
        self._health_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def state(self) -> ProcessState:
        return self._state

    @property
    def is_running(self) -> bool:
        return self._state == ProcessState.RUNNING

    @property
    def pid(self) -> Optional[int]:
        return self._process.pid if self._process else None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the MCP server subprocess.

        Raises:
            MCPProcessError: If the server is already running or fails to start.
        """
        with self._lock:
            if self._state in (ProcessState.RUNNING, ProcessState.STARTING):
                return  # Idempotent

            if not self._server_script.exists():
                raise MCPProcessError(
                    f"MCP server script not found: {self._server_script}",
                    user_message="The background service could not be located. Reinstall the application.",
                )

            env = {**os.environ, **self._extra_env}
            try:
                self._state = ProcessState.STARTING
                self._process = subprocess.Popen(
                    [sys.executable, str(self._server_script)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=False,
                )
                self._state = ProcessState.RUNNING
            except OSError as exc:
                self._state = ProcessState.FAILED
                raise MCPProcessError(
                    f"Failed to start MCP server: {exc}",
                    user_message="The background service failed to start.",
                ) from exc

        self._stop_event.clear()
        self._health_thread = threading.Thread(
            target=self._health_loop, daemon=True, name="mcp-health"
        )
        self._health_thread.start()

    def stop(self) -> None:
        """Stop the MCP server subprocess gracefully."""
        with self._lock:
            if self._state not in (ProcessState.RUNNING, ProcessState.STARTING):
                return
            self._state = ProcessState.STOPPING

        self._stop_event.set()

        if self._process:
            try:
                self._process.terminate()
                self._process.wait(timeout=_STOP_TIMEOUT)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()
            except OSError:
                pass
            finally:
                self._process = None

        self._state = ProcessState.STOPPED

    def health_check(self) -> bool:
        """Return True if the subprocess is still alive."""
        if self._process is None:
            return False
        return self._process.poll() is None

    # ── Internal ──────────────────────────────────────────────────────────────

    def _health_loop(self) -> None:
        """Background thread that monitors the subprocess and updates state."""
        while not self._stop_event.wait(timeout=_HEALTH_POLL_INTERVAL):
            if not self.health_check():
                with self._lock:
                    if self._state == ProcessState.RUNNING:
                        self._state = ProcessState.FAILED
                break
