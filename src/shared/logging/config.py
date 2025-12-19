"""
Centralized Logging Configuration

Provides logging setup for development and production environments.
"""

import logging
import logging.config
from pathlib import Path
from typing import Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class LogConfig:
    """
    Centralized logging configuration manager.

    Handles logging setup for different environments (development/production).

    Examples
    --------
    >>> # At application startup
    >>> config = LogConfig(environment='development')
    >>> config.setup()
    """

    def __init__(self, environment: str = "development"):
        """
        Initialize logging configuration.

        Parameters
        ----------
        environment : str
            Environment type: 'development' or 'production'
            Default is 'development'
        """
        self.environment = environment
        # Path resolution: /app/src/shared/logging/config.py -> /app/
        base_dir = Path(__file__).parent.parent.parent.parent
        self.log_dir = base_dir / "logs"
        self.config_dir = base_dir / "config"

        # Ensure log directory exists
        self.log_dir.mkdir(exist_ok=True)

    def setup(self) -> None:
        """
        Configure logging based on environment.

        Tries to load YAML configuration file if available,
        otherwise falls back to basic configuration.
        """
        if YAML_AVAILABLE:
            self._setup_from_yaml()
        else:
            self._setup_basic()

    def _setup_from_yaml(self) -> None:
        """Load logging configuration from YAML file."""
        # Determine config file based on environment
        if self.environment.lower() in ["production", "prod"]:
            config_file = "logging_prod.yaml"
        else:
            config_file = "logging_dev.yaml"

        config_path = self.config_dir / config_file

        if config_path.exists():
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
                    logging.config.dictConfig(config)
                    logging.info(
                        f"Logging configured from {config_file} "
                        f"in {self.environment} mode"
                    )
            except Exception as e:
                print(f"Error loading logging config from {config_path}: {e}")
                self._setup_basic()
        else:
            msg = f"Config file {config_path} not found, using basic configuration"
            print(msg)
            self._setup_basic()

    def _setup_basic(self) -> None:
        """Setup basic logging configuration as fallback."""
        # Determine log level based on environment
        if self.environment.lower() in ["production", "prod"]:
            level = logging.INFO
            format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        else:
            level = logging.DEBUG
            format_str = (
                "%(asctime)s - %(name)s - %(levelname)s - "
                "[%(filename)s:%(lineno)d] - %(message)s"
            )

        # Create handlers
        handlers = [logging.StreamHandler()]

        # Add file handler
        log_file = self.log_dir / "app.log"
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            handlers.append(file_handler)
        except Exception as e:
            print(f"Warning: Could not create file handler: {e}")

        # Configure logging
        logging.basicConfig(
            level=level,
            format=format_str,
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=handlers,
        )

        logging.info(f"Basic logging configured in {self.environment} mode")


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger instance.

    Parameters
    ----------
    name : str
        Logger name (usually __name__ of the module)

    Returns
    -------
    logging.Logger
        Configured logger instance

    Examples
    --------
    >>> from src.shared.logging import get_logger
    >>> logger = get_logger(__name__)
    >>> logger.info("Operation completed")
    """
    return logging.getLogger(name)


def configure_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> logging.Logger:
    """
    Configure a specific logger with custom settings.

    Parameters
    ----------
    name : str
        Logger name
    level : int
        Logging level (default: INFO)
    log_file : Optional[str]
        Optional log file path

    Returns
    -------
    logging.Logger
        Configured logger

    Examples
    --------
    >>> logger = configure_logger('my_module', level=logging.DEBUG)
    >>> logger.debug("Debug message")
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(console_formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"Could not create file handler: {e}")

    return logger
