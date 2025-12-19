"""
Shared logging utilities.

Provides logger configuration and utilities with file and console output.

.. deprecated:: 2.0
    This module is deprecated. Use :mod:`shared.logging.config` and
    :mod:`config.settings` instead for environment-aware logging.

    Migration example::

        # Old way
        from src.shared.logger_utils import get_logger
        logger = get_logger(__name__, log_level="DEBUG")

        # New way
        from config.settings import get_settings
        import logging

        settings = get_settings()
        settings.configure_logging()  # Setup logging based on environment
        logger = logging.getLogger(__name__)

    The new system provides:
    - Environment-based configuration (dev/prod)
    - YAML-based logging configuration
    - JSON formatting for production
    - Colored output for development
    - Separate logs for security and performance
    - Integration with application settings
"""

import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Optional

_LOGGER_CONFIGURED = False
_LOG_DIR = None
_SESSION_ID = datetime.now().strftime("%Y%m%d_%H%M%S")


def get_logger(name: str, log_level: str = "INFO") -> logging.Logger:
    """
    Get a configured logger instance with file and console output.

    Logs are saved to:
    - biorempp_web/logs/biorempp_{session_id}.log (main log file)
    - Console output with color-coded levels

    Parameters
    ----------
    name : str
        Logger name (typically __name__).
    log_level : str
        Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        Default is INFO.

    Returns
    -------
    logging.Logger
        Configured logger instance.

    Examples
    --------
    >>> logger = get_logger(__name__)
    >>> logger.info("Application started")
    >>> logger.debug("Debug information")
    >>> logger.error("Error occurred")
    """
    global _LOGGER_CONFIGURED

    logger = logging.getLogger(name)

    # Configure logging system once
    if not _LOGGER_CONFIGURED:
        _setup_logging_system(log_level)
        _LOGGER_CONFIGURED = True

    return logger


def _setup_logging_system(log_level: str = "INFO") -> None:
    """
    Configure the global logging system.

    Sets up:
    - File handler with rotation (10MB max, 5 backups)
    - Console handler with color formatting
    - Unified format for all logs

    Parameters
    ----------
    log_level : str
        Logging level for the system.
    """
    global _LOG_DIR

    # Create logs directory
    log_dir = Path(__file__).parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    _LOG_DIR = log_dir

    # Log file with session timestamp
    log_file = log_dir / f"biorempp_{_SESSION_ID}.log"

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Clear existing handlers
    root_logger.handlers.clear()

    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8",
    )
    file_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)  # File gets all levels

    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Add handlers to root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Log initialization
    logging.info("=" * 80)
    logging.info(f"BioRemPP Logging System Initialized - Session: {_SESSION_ID}")
    logging.info(f"Log file: {log_file}")
    logging.info(f"Log level: {log_level.upper()}")
    logging.info("=" * 80)


def get_log_file() -> Optional[Path]:
    """
    Get the current log file path.

    Returns
    -------
    Optional[Path]
        Path to current log file, or None if not configured.

    Examples
    --------
    >>> log_path = get_log_file()
    >>> print(f"Logs saved to: {log_path}")
    """
    if _LOG_DIR:
        return _LOG_DIR / f"biorempp_{_SESSION_ID}.log"
    return None


def set_debug_mode(enabled: bool = True) -> None:
    """
    Enable or disable debug mode for all loggers.

    Parameters
    ----------
    enabled : bool
        True to enable DEBUG level, False for INFO level.

    Examples
    --------
    >>> set_debug_mode(True)  # Enable debug logs
    >>> set_debug_mode(False)  # Back to info logs
    """
    level = logging.DEBUG if enabled else logging.INFO
    logging.getLogger().setLevel(level)

    # Update console handler level
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler, logging.handlers.RotatingFileHandler
        ):
            handler.setLevel(level)

    logging.info(f"Debug mode {'enabled' if enabled else 'disabled'}")
