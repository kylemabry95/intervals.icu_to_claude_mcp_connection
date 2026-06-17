"""
Startup orchestration for the desktop application.

Responsibilities:
  - Configure logging
  - Start the MCP server subprocess
  - Perform pre-flight runtime checks
  - Register shutdown handlers

After `run_startup_sequence()` returns, the app is ready to open its UI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from desktop_app.errors import AppError, MCPProcessError

if TYPE_CHECKING:
    from desktop_app.config import Config

_mcp_manager: Optional["MCPProcessManager"] = None  # type: ignore[name-defined]


def run_startup_sequence(config: "Config") -> None:
    """Start all background services required before the UI opens.

    Args:
        config: Validated application configuration.

    Raises:
        AppError: If any required service fails to start.
    """
    if config is None:
        raise AppError("run_startup_sequence() requires a valid Config, got None.")

    from desktop_app.observability.logging import configure_logging
    from desktop_app.runtime.mcp_process import MCPProcessManager

    global _mcp_manager

    # 1. Configure logging first so all subsequent failures are recorded
    configure_logging(log_dir=config.log_dir, level=config.log_level)

    from desktop_app.observability.logging import get_logger
    log = get_logger(__name__)
    log.info("Starting IntervalsICU desktop application…")

    # 2. Start the MCP server subprocess
    _mcp_manager = MCPProcessManager(
        env={
            "INTERVALS_API_KEY": config.api_key,
            "INTERVALS_ATHLETE_ID": config.athlete_id,
            "INTERVALS_API_BASE_URL": config.base_url,
        }
    )
    try:
        _mcp_manager.start()
        log.info("MCP server process started (pid=%s).", _mcp_manager.pid)
    except MCPProcessError as exc:
        log.error("MCP server failed to start: %s", exc)
        raise

    log.info("Startup sequence complete.")


def shutdown() -> None:
    """Stop all background services on application exit."""
    global _mcp_manager
    if _mcp_manager is not None:
        try:
            _mcp_manager.stop()
        except Exception:
            pass
        _mcp_manager = None
