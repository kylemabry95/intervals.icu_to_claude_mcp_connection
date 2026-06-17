"""
Structured logging with log-file rotation for the desktop application.

Provides a single ``get_logger()`` factory that returns loggers writing to
both stderr and a rotating log file under the configured log directory.

Security: A ``RedactingFormatter`` strips sensitive patterns (API keys,
passwords, tokens) from log messages before they are written to disk or
stderr, preventing accidental credential leakage in logs.

Usage::

    from desktop_app.observability.logging import configure_logging, get_logger

    configure_logging(log_dir="/tmp/IntervalsICU", level="INFO")
    log = get_logger(__name__)
    log.info("Application started")
"""

from __future__ import annotations

import logging
import logging.handlers
import re
from pathlib import Path

_LOG_FILE = "intervals_icu_desktop.log"
_MAX_BYTES = 5 * 1024 * 1024  # 5 MB per file
_BACKUP_COUNT = 3
_FORMAT = "%(asctime)s %(levelname)-8s %(name)s - %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

# Patterns to redact from log output (case-insensitive)
_REDACT_PATTERNS = [
    re.compile(r"(api[_\-]?key\s*[=:]\s*)\S+", re.IGNORECASE),
    re.compile(r"(authorization\s*:\s*basic\s+)\S+", re.IGNORECASE),
    re.compile(r"(password\s*[=:]\s*)\S+", re.IGNORECASE),
    re.compile(r"(token\s*[=:]\s*)\S+", re.IGNORECASE),
    re.compile(r"(secret\s*[=:]\s*)\S+", re.IGNORECASE),
    # Base64-looking strings following Basic Auth prefix
    re.compile(r"(Basic\s+)[A-Za-z0-9+/=]{20,}", re.IGNORECASE),
]

_configured = False


class RedactingFormatter(logging.Formatter):
    """Log formatter that redacts sensitive patterns before output."""

    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        for pattern in _REDACT_PATTERNS:
            msg = pattern.sub(r"\1[REDACTED]", msg)
        return msg


def configure_logging(log_dir: str, level: str = "INFO") -> None:
    """Set up root logger with a rotating file handler and a stderr handler.

    Idempotent — safe to call multiple times; only the first call takes effect.

    Args:
        log_dir: Directory where the log file is written.
        level:   Log level string (DEBUG, INFO, WARNING, ERROR).
    """
    global _configured
    if _configured:
        return

    log_path = Path(log_dir) / _LOG_FILE
    log_path.parent.mkdir(parents=True, exist_ok=True)

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    formatter = RedactingFormatter(fmt=_FORMAT, datefmt=_DATE_FORMAT)

    file_handler = logging.handlers.RotatingFileHandler(
        filename=str(log_path),
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(numeric_level)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setFormatter(formatter)
    stderr_handler.setLevel(numeric_level)

    root = logging.getLogger()
    root.setLevel(numeric_level)
    root.addHandler(file_handler)
    root.addHandler(stderr_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Return a named logger.

    Args:
        name: Typically ``__name__`` of the calling module.
    """
    return logging.getLogger(name)
