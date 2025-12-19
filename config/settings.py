"""
Application Settings - Environment-based Configuration

Centralized configuration system for BioRemPP v1.0.
Integrates with shared.logging for automatic logging setup.

Usage
-----
At application startup:

>>> from config.settings import get_settings
>>> settings = get_settings()
>>> settings.configure_logging()  # Setup logging based on environment
>>> logger = logging.getLogger(__name__)
>>> logger.info(f"Running in {settings.ENV} mode")

With .env file:

Create `.env` in project root:
```
BIOREMPP_ENV=production
BIOREMPP_DEBUG=False
BIOREMPP_PORT=8080
```

Environment Variables
--------------------
All settings can be overridden with environment variables:

- BIOREMPP_ENV: Environment mode (development/production)
- BIOREMPP_DEBUG: Enable debug mode (True/False)
- BIOREMPP_HOT_RELOAD: Enable hot reload (True/False)
- BIOREMPP_HOST: Server host (default: 127.0.0.1)
- BIOREMPP_PORT: Server port (default: 8050)
- BIOREMPP_LOG_LEVEL: Logging level (DEBUG/INFO/WARNING/ERROR)
- BIOREMPP_LOG_FILE: Log file path (optional)
- BIOREMPP_WORKERS: Number of Gunicorn workers (production)
- BIOREMPP_WORKER_CLASS: Gunicorn worker class (sync/gevent)
- BIOREMPP_TIMEOUT: Request timeout in seconds
- BIOREMPP_UPLOAD_MAX_SIZE_MB: Maximum upload file size in MB
- BIOREMPP_UPLOAD_SAMPLE_LIMIT: Maximum number of samples per upload
- BIOREMPP_UPLOAD_KO_LIMIT: Maximum number of KO entries per upload
- BIOREMPP_UPLOAD_ENCODING: Expected file encoding (default: utf-8)
- BIOREMPP_KO_PATTERN: Regex pattern for KO validation
- BIOREMPP_SAMPLE_NAME_PATTERN: Regex pattern for sample name validation
"""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal, Optional

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    # Try to load .env from project root
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"[OK] Loaded environment from: {env_path}")
    else:
        load_dotenv()  # Try default locations
except ImportError:
    print("[WARNING] python-dotenv not installed, using system environment only")


def _get_bool(env_var: str, default: bool) -> bool:
    """Parse boolean from environment variable."""
    value = os.getenv(env_var, str(default))
    return value.lower() in ("true", "1", "yes", "on")


def _get_int(env_var: str, default: int) -> int:
    """Parse integer from environment variable."""
    try:
        return int(os.getenv(env_var, str(default)))
    except ValueError:
        return default


@dataclass
class Settings:
    """
    Application settings loaded from environment variables.

    Attributes
    ----------
    ENV : str
        Environment mode: 'development' or 'production'
    DEBUG : bool
        Enable debug mode (detailed errors, hot reload)
    HOT_RELOAD : bool
        Enable hot reload (development only)
    HOST : str
        Server bind address
    PORT : int
        Server port
    WORKERS : int
        Number of Gunicorn workers (production)
    WORKER_CLASS : str
        Gunicorn worker class (sync/gevent/eventlet)
    WORKER_CONNECTIONS : int
        Max connections per worker
    TIMEOUT : int
        Request timeout in seconds
    KEEPALIVE : int
        Keepalive timeout in seconds
    LOG_LEVEL : str
        Logging level (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    LOG_FILE : Optional[str]
        Optional log file path (overrides YAML config)
    BASE_DIR : Path
        Project base directory
    DATA_DIR : Path
        Data files directory
    LOG_DIR : Path
        Logs directory
    CONFIG_DIR : Path
        Configuration files directory
    ASSETS_DIR : Path
        Static assets directory
    UPLOAD_MAX_SIZE_MB : int
        Maximum upload file size in MB
    UPLOAD_MAX_SIZE_BYTES : int
        Maximum upload file size in bytes (calculated)
    UPLOAD_SAMPLE_LIMIT : int
        Maximum number of samples per upload
    UPLOAD_KO_LIMIT : int
        Maximum number of KO entries per upload
    UPLOAD_ALLOWED_EXTENSIONS : list
        List of allowed file extensions for upload
    UPLOAD_ENCODING : str
        Expected file encoding for uploads
    KO_PATTERN : str
        Regex pattern for KO identifier validation
    SAMPLE_NAME_PATTERN : str
        Regex pattern for sample name validation

    Examples
    --------
    >>> settings = Settings()
    >>> print(f"Running on {settings.HOST}:{settings.PORT}")
    >>> if settings.is_production:
    ...     print("Production mode active")
    """

    # ========================================================================
    # ENVIRONMENT
    # ========================================================================
    ENV: str = field(
        default_factory=lambda: os.getenv("BIOREMPP_ENV", "development")
    )

    # ========================================================================
    # SERVER CONFIGURATION
    # ========================================================================
    DEBUG: bool = field(
        default_factory=lambda: _get_bool("BIOREMPP_DEBUG", True)
    )

    HOT_RELOAD: bool = field(
        default_factory=lambda: _get_bool("BIOREMPP_HOT_RELOAD", True)
    )

    HOST: str = field(
        default_factory=lambda: os.getenv("BIOREMPP_HOST", "127.0.0.1")
    )

    PORT: int = field(
        default_factory=lambda: _get_int("BIOREMPP_PORT", 8050)
    )

    # ========================================================================
    # GUNICORN (PRODUCTION)
    # ========================================================================
    WORKERS: int = field(
        default_factory=lambda: _get_int("BIOREMPP_WORKERS", 4)
    )

    WORKER_CLASS: str = field(
        default_factory=lambda: os.getenv("BIOREMPP_WORKER_CLASS", "sync")
    )

    WORKER_CONNECTIONS: int = field(
        default_factory=lambda: _get_int("BIOREMPP_WORKER_CONNECTIONS", 1000)
    )

    TIMEOUT: int = field(
        default_factory=lambda: _get_int("BIOREMPP_TIMEOUT", 60)
    )

    KEEPALIVE: int = field(
        default_factory=lambda: _get_int("BIOREMPP_KEEPALIVE", 5)
    )

    # ========================================================================
    # LOGGING
    # ========================================================================
    LOG_LEVEL: str = field(
        default_factory=lambda: os.getenv("BIOREMPP_LOG_LEVEL", "DEBUG")
    )

    LOG_FILE: Optional[str] = field(
        default_factory=lambda: os.getenv("BIOREMPP_LOG_FILE")
    )

    # ========================================================================
    # PATHS
    # ========================================================================
    BASE_DIR: Path = field(
        default_factory=lambda: Path(__file__).parent.parent
    )

    DATA_DIR: Path = field(
        default_factory=lambda: Path(__file__).parent.parent / "data"
    )

    LOG_DIR: Path = field(
        default_factory=lambda: Path(__file__).parent.parent / "logs"
    )

    CONFIG_DIR: Path = field(
        default_factory=lambda: Path(__file__).parent
    )

    ASSETS_DIR: Path = field(
        default_factory=lambda: Path(__file__).parent.parent / "assets"
    )

    # ========================================================================
    # UPLOAD CONFIGURATION
    # ========================================================================
    UPLOAD_MAX_SIZE_MB: int = field(
        default_factory=lambda: _get_int("BIOREMPP_UPLOAD_MAX_SIZE_MB", 5)
    )

    UPLOAD_MAX_SIZE_BYTES: int = field(init=False)

    UPLOAD_SAMPLE_LIMIT: int = field(
        default_factory=lambda: _get_int("BIOREMPP_UPLOAD_SAMPLE_LIMIT", 100)
    )

    UPLOAD_KO_LIMIT: int = field(
        default_factory=lambda: _get_int("BIOREMPP_UPLOAD_KO_LIMIT", 500_000)
    )

    UPLOAD_ALLOWED_EXTENSIONS: list = field(
        default_factory=lambda: ['.txt']
    )

    UPLOAD_ENCODING: str = field(
        default_factory=lambda: os.getenv("BIOREMPP_UPLOAD_ENCODING", "utf-8")
    )

    # ========================================================================
    # VALIDATION PATTERNS
    # ========================================================================
    KO_PATTERN: str = field(
        default_factory=lambda: os.getenv(
            "BIOREMPP_KO_PATTERN",
            r'^K\d{5}$'  # K + 5 digits
        )
    )

    SAMPLE_NAME_PATTERN: str = field(
        default_factory=lambda: os.getenv(
            "BIOREMPP_SAMPLE_NAME_PATTERN",
            r'^[a-zA-Z0-9_\-\.]+$'  # Alphanumeric + _ - .
        )
    )

    # ========================================================================
    # PARSING LIMITS (lightweight application - max 5MB)
    # ========================================================================
    PARSING_MAX_SAMPLES: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_PARSING_MAX_SAMPLES", 1000
        )
    )

    PARSING_MAX_KOS_PER_SAMPLE: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_PARSING_MAX_KOS_PER_SAMPLE", 10000
        )
    )

    PARSING_MAX_TOTAL_KOS: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_PARSING_MAX_TOTAL_KOS", 100000
        )
    )

    # ========================================================================
    # PROCESSING CONFIGURATION
    # ========================================================================
    PROCESSING_TIMEOUT_SECONDS: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_PROCESSING_TIMEOUT", 60
        )
    )

    PROCESSING_MAX_RETRIES: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_PROCESSING_MAX_RETRIES", 2
        )
    )

    PROCESSING_RETRY_DELAY_SECONDS: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_PROCESSING_RETRY_DELAY", 1
        )
    )

    PROCESSING_CIRCUIT_BREAKER_THRESHOLD: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_PROCESSING_CIRCUIT_BREAKER_THRESHOLD", 3
        )
    )

    PROCESSING_CIRCUIT_BREAKER_TIMEOUT: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_PROCESSING_CIRCUIT_BREAKER_TIMEOUT", 30
        )
    )

    def __post_init__(self):
        """Post-initialization validation and setup."""
        # Normalize environment
        self.ENV = self.ENV.lower()

        # Calculate byte size for upload limit
        self.UPLOAD_MAX_SIZE_BYTES = self.UPLOAD_MAX_SIZE_MB * 1024 * 1024

        # Ensure paths exist
        self.LOG_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)

        # Auto-adjust settings based on environment
        if self.is_production:
            # Force production-safe settings
            if self.DEBUG:
                print("[WARNING] DEBUG disabled in production mode")
                self.DEBUG = False

            if self.HOT_RELOAD:
                print("[WARNING] HOT_RELOAD disabled in production mode")
                self.HOT_RELOAD = False

            if self.HOST == "127.0.0.1":
                print("[WARNING] HOST changed to 0.0.0.0 for production")
                self.HOST = "0.0.0.0"

            if self.LOG_LEVEL == "DEBUG":
                print("[WARNING] LOG_LEVEL changed to WARNING for production")
                self.LOG_LEVEL = "WARNING"

    # ========================================================================
    # PROPERTIES
    # ========================================================================

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENV in ("production", "prod")

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENV in ("development", "dev")

    @property
    def log_config_file(self) -> str:
        """Get appropriate logging YAML config file."""
        if self.is_production:
            return "logging_prod.yaml"
        return "logging_dev.yaml"

    # ========================================================================
    # METHODS
    # ========================================================================

    def configure_logging(self) -> None:
        """
        Configure logging system based on environment.

        Uses YAML configuration files for structured logging setup.
        Falls back to basic configuration if YAML not available.

        Notes
        -----
        This should be called once at application startup.

        Examples
        --------
        >>> settings = get_settings()
        >>> settings.configure_logging()
        >>> logger = logging.getLogger(__name__)
        >>> logger.info("Logging configured!")
        """
        from src.shared.logging.config import LogConfig

        # Create and configure logging
        log_config = LogConfig(environment=self.ENV)
        log_config.setup()

        # Log configuration summary
        logger = logging.getLogger(__name__)
        logger.info("=" * 80)
        logger.info("BioRemPP v1.0 - Configuration Loaded")
        logger.info("=" * 80)
        logger.info(f"Environment: {self.ENV.upper()}")
        logger.info(f"Debug Mode: {self.DEBUG}")
        logger.info(f"Host: {self.HOST}")
        logger.info(f"Port: {self.PORT}")
        logger.info(f"Log Level: {self.LOG_LEVEL}")
        logger.info(f"Log Directory: {self.LOG_DIR}")

        if self.is_production:
            logger.info(f"Workers: {self.WORKERS} ({self.WORKER_CLASS})")
            logger.info(f"Timeout: {self.TIMEOUT}s")

        logger.info("=" * 80)

    def summary(self) -> str:
        """
        Get configuration summary as formatted string.

        Returns
        -------
        str
            Multi-line configuration summary

        Examples
        --------
        >>> settings = get_settings()
        >>> print(settings.summary())
        BioRemPP v1.0 Configuration
        Environment: DEVELOPMENT
        Server: 127.0.0.1:8050
        ...
        """
        lines = [
            "=" * 60,
            "BioRemPP v1.0 Configuration",
            "=" * 60,
            f"Environment: {self.ENV.upper()}",
            f"Debug: {self.DEBUG}",
            f"Hot Reload: {self.HOT_RELOAD}",
            "",
            "Server:",
            f"  Host: {self.HOST}",
            f"  Port: {self.PORT}",
            "",
            "Logging:",
            f"  Level: {self.LOG_LEVEL}",
            f"  Directory: {self.LOG_DIR}",
            f"  Config: {self.log_config_file}",
        ]

        if self.is_production:
            lines.extend([
                "",
                "Gunicorn:",
                f"  Workers: {self.WORKERS}",
                f"  Worker Class: {self.WORKER_CLASS}",
                f"  Worker Connections: {self.WORKER_CONNECTIONS}",
                f"  Timeout: {self.TIMEOUT}s",
                f"  Keepalive: {self.KEEPALIVE}s",
            ])

        lines.extend([
            "",
            "Upload Limits:",
            f"  Max File Size: {self.UPLOAD_MAX_SIZE_MB} MB "
            f"({self.UPLOAD_MAX_SIZE_BYTES:,} bytes)",
            f"  Max Samples: {self.UPLOAD_SAMPLE_LIMIT}",
            f"  Max KOs: {self.UPLOAD_KO_LIMIT:,}",
            f"  Extensions: {', '.join(self.UPLOAD_ALLOWED_EXTENSIONS)}",
            f"  Encoding: {self.UPLOAD_ENCODING}",
            "",
            "Parsing Limits:",
            f"  Max Samples: {self.PARSING_MAX_SAMPLES}",
            f"  Max KOs/Sample: {self.PARSING_MAX_KOS_PER_SAMPLE:,}",
            f"  Max Total KOs: {self.PARSING_MAX_TOTAL_KOS:,}",
            "",
            "Processing Configuration:",
            f"  Timeout: {self.PROCESSING_TIMEOUT_SECONDS}s",
            f"  Max Retries: {self.PROCESSING_MAX_RETRIES}",
            f"  Retry Delay: {self.PROCESSING_RETRY_DELAY_SECONDS}s",
            f"  Circuit Breaker Threshold: "
            f"{self.PROCESSING_CIRCUIT_BREAKER_THRESHOLD}",
            f"  Circuit Breaker Timeout: "
            f"{self.PROCESSING_CIRCUIT_BREAKER_TIMEOUT}s",
            "",
            "Validation Patterns:",
            f"  KO Pattern: {self.KO_PATTERN}",
            f"  Sample Name Pattern: {self.SAMPLE_NAME_PATTERN}",
            "",
            "Paths:",
            f"  Base: {self.BASE_DIR}",
            f"  Data: {self.DATA_DIR}",
            f"  Logs: {self.LOG_DIR}",
            f"  Config: {self.CONFIG_DIR}",
            f"  Assets: {self.ASSETS_DIR}",
            "=" * 60,
        ])

        return "\n".join(lines)


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton).

    Returns the same Settings instance on subsequent calls.

    Returns
    -------
    Settings
        Application settings instance

    Examples
    --------
    >>> settings = get_settings()
    >>> print(f"Running on port {settings.PORT}")

    >>> # Later in the code
    >>> settings2 = get_settings()
    >>> assert settings is settings2  # Same instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings() -> None:
    """
    Reset settings singleton (useful for testing).

    Examples
    --------
    >>> # In tests
    >>> reset_settings()
    >>> settings = get_settings()  # Fresh instance
    """
    global _settings
    _settings = None
