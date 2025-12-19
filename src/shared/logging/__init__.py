"""
Centralized Logging System

Provides comprehensive logging infrastructure for BioRemPP Web.

Usage
-----
Basic setup at application startup:

>>> from src.shared.logging import LogConfig, get_logger
>>> config = LogConfig(environment='development')
>>> config.setup()
>>> logger = get_logger(__name__)
>>> logger.info("Application started")

With decorators:

>>> from src.shared.logging.decorators import log_execution
>>> @log_execution(level=logging.INFO)
... def process_data():
...     pass
"""

from .config import LogConfig, configure_logger, get_logger
from .decorators import log_exceptions, log_execution, log_method_calls, log_performance
from .formatters import ColoredFormatter, DetailedFormatter, JSONFormatter
from .handlers import (
    ContextFilter,
    SafeRotatingFileHandler,
    create_console_handler,
    create_rotating_handler,
)

__all__ = [
    # Configuration
    "LogConfig",
    "get_logger",
    "configure_logger",
    # Decorators
    "log_execution",
    "log_performance",
    "log_exceptions",
    "log_method_calls",
    # Formatters
    "JSONFormatter",
    "ColoredFormatter",
    "DetailedFormatter",
    # Handlers
    "SafeRotatingFileHandler",
    "ContextFilter",
    "create_rotating_handler",
    "create_console_handler",
]
