"""
Custom Log Formatters

Provides specialized formatting for different log outputs.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Useful for log aggregation systems (ELK, Splunk, CloudWatch).

    Examples
    --------
    >>> handler = logging.StreamHandler()
    >>> handler.setFormatter(JSONFormatter())
    >>> logger.addHandler(handler)
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.

        Parameters
        ----------
        record : logging.LogRecord
            Log record to format

        Returns
        -------
        str
            JSON-formatted log entry
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.thread,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields from record
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "sample_id"):
            log_data["sample_id"] = record.sample_id
        if hasattr(record, "analysis_id"):
            log_data["analysis_id"] = record.analysis_id
        if hasattr(record, "event"):
            log_data["event"] = record.event

        return json.dumps(log_data, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for development.

    Uses ANSI color codes for better readability in terminal.

    Examples
    --------
    >>> handler = logging.StreamHandler()
    >>> handler.setFormatter(ColoredFormatter())
    >>> logger.addHandler(handler)
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record: logging.LogRecord) -> str:
        """
        Format with colors.

        Parameters
        ----------
        record : logging.LogRecord
            Log record to format

        Returns
        -------
        str
            Colored formatted log entry
        """
        # Store original levelname
        original_levelname = record.levelname

        # Apply color to levelname
        color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{color}{self.BOLD}{record.levelname}{self.RESET}"

        # Format the message
        formatted = super().format(record)

        # Restore original levelname
        record.levelname = original_levelname

        return formatted


class DetailedFormatter(logging.Formatter):
    """
    Detailed formatter with full context information.

    Includes filename, line number, function name, and timestamp.

    Examples
    --------
    >>> handler = logging.FileHandler('detailed.log')
    >>> handler.setFormatter(DetailedFormatter())
    >>> logger.addHandler(handler)
    """

    def __init__(self):
        """Initialize detailed formatter."""
        fmt = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[%(filename)s:%(lineno)d:%(funcName)s] - %(message)s"
        )
        datefmt = "%Y-%m-%d %H:%M:%S"
        super().__init__(fmt=fmt, datefmt=datefmt)
