"""
Custom Log Handlers

Provides specialized handlers for different logging scenarios.
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional


class ContextFilter(logging.Filter):
    """
    Filter to add context information to log records.

    Adds custom attributes like user_id, request_id, etc. to log records.

    Examples
    --------
    >>> handler = logging.StreamHandler()
    >>> filter = ContextFilter(user_id="12345")
    >>> handler.addFilter(filter)
    """

    def __init__(
        self,
        user_id: Optional[str] = None,
        request_id: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize context filter.

        Parameters
        ----------
        user_id : Optional[str]
            User identifier to add to logs
        request_id : Optional[str]
            Request identifier to add to logs
        **kwargs
            Additional context fields
        """
        super().__init__()
        self.user_id = user_id
        self.request_id = request_id
        self.context = kwargs

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Add context to log record.

        Parameters
        ----------
        record : logging.LogRecord
            Log record to modify

        Returns
        -------
        bool
            Always True (does not filter out records)
        """
        if self.user_id:
            record.user_id = self.user_id
        if self.request_id:
            record.request_id = self.request_id

        # Add any additional context
        for key, value in self.context.items():
            setattr(record, key, value)

        return True


class SafeRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """
    Thread-safe rotating file handler with error recovery.

    Extends RotatingFileHandler with better error handling.

    Examples
    --------
    >>> handler = SafeRotatingFileHandler(
    ...     'app.log',
    ...     maxBytes=10*1024*1024,  # 10MB
    ...     backupCount=5
    ... )
    """

    def __init__(
        self,
        filename: str,
        mode: str = "a",
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: Optional[str] = "utf-8",
        delay: bool = False,
    ):
        """
        Initialize safe rotating file handler.

        Parameters
        ----------
        filename : str
            Log file path
        mode : str
            File mode (default: 'a' for append)
        maxBytes : int
            Maximum file size before rotation (default: 0 = no limit)
        backupCount : int
            Number of backup files to keep (default: 0 = no backups)
        encoding : Optional[str]
            File encoding (default: 'utf-8')
        delay : bool
            Delay file opening until first log (default: False)
        """
        # Ensure parent directory exists
        log_path = Path(filename)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        super().__init__(
            filename=filename,
            mode=mode,
            maxBytes=maxBytes,
            backupCount=backupCount,
            encoding=encoding,
            delay=delay,
        )

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a record with error handling.

        Parameters
        ----------
        record : logging.LogRecord
            Log record to emit
        """
        try:
            super().emit(record)
        except Exception:
            # Fallback to stderr if file writing fails
            self.handleError(record)


def create_rotating_handler(
    log_file: str,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    level: int = logging.INFO,
    formatter: Optional[logging.Formatter] = None,
) -> SafeRotatingFileHandler:
    """
    Create a configured rotating file handler.

    Parameters
    ----------
    log_file : str
        Log file path
    max_bytes : int
        Maximum file size before rotation (default: 10MB)
    backup_count : int
        Number of backup files to keep (default: 5)
    level : int
        Log level (default: INFO)
    formatter : Optional[logging.Formatter]
        Custom formatter (default: None)

    Returns
    -------
    SafeRotatingFileHandler
        Configured handler

    Examples
    --------
    >>> handler = create_rotating_handler(
    ...     'logs/app.log',
    ...     max_bytes=50*1024*1024,  # 50MB
    ...     backup_count=10
    ... )
    >>> logger.addHandler(handler)
    """
    handler = SafeRotatingFileHandler(
        filename=log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
    )
    handler.setLevel(level)

    if formatter:
        handler.setFormatter(formatter)
    else:
        default_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(default_formatter)

    return handler


def create_console_handler(
    level: int = logging.INFO,
    formatter: Optional[logging.Formatter] = None,
    colored: bool = False,
) -> logging.StreamHandler:
    """
    Create a configured console handler.

    Parameters
    ----------
    level : int
        Log level (default: INFO)
    formatter : Optional[logging.Formatter]
        Custom formatter (default: None)
    colored : bool
        Use colored output for development (default: False)

    Returns
    -------
    logging.StreamHandler
        Configured handler

    Examples
    --------
    >>> handler = create_console_handler(
    ...     level=logging.DEBUG,
    ...     colored=True
    ... )
    >>> logger.addHandler(handler)
    """
    handler = logging.StreamHandler()
    handler.setLevel(level)

    if formatter:
        handler.setFormatter(formatter)
    elif colored:
        from .formatters import ColoredFormatter

        handler.setFormatter(
            ColoredFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
    else:
        default_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(default_formatter)

    return handler
