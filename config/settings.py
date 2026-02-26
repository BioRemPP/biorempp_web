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
- BIOREMPP_URL_BASE_PATH: Base URL path prefix (default: /)
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
- BIOREMPP_CACHE_DIR: Base cache directory (default: <project_root>/cache)
- BIOREMPP_BACKGROUND_CALLBACKS_ENABLED: Enable Dash background callbacks
- BIOREMPP_OBSERVABILITY_ENABLED: Enable Prometheus instrumentation (True/False)
- BIOREMPP_OBSERVABILITY_METRICS_PATH: Metrics endpoint path (default: /metrics)
- BIOREMPP_RESUME_BACKEND: Resume backend (diskcache|redis)
- BIOREMPP_RESUME_SECURITY_MODE: Resume error mode (normal|strict)
- BIOREMPP_RESUME_TTL_SECONDS: Resume payload TTL in seconds (default: 14400)
- BIOREMPP_RESUME_CACHE_SIZE_MB: Resume cache max size in MB (default: 512)
- BIOREMPP_RESUME_MAX_PAYLOAD_MB: Max payload size per resume job in MB
- BIOREMPP_RESUME_RATE_LIMIT_ATTEMPTS: Max resume attempts per window
- BIOREMPP_RESUME_RATE_LIMIT_WINDOW_SECONDS: Rate-limit window in seconds
- BIOREMPP_RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS: Base backoff in seconds
- BIOREMPP_RESUME_RATE_LIMIT_BACKOFF_MAX_SECONDS: Max backoff in seconds
- BIOREMPP_RESUME_RATE_LIMIT_CACHE_SIZE_MB: Cache size for limiter state
- BIOREMPP_RESUME_ALERT_WINDOW_SECONDS: Security alert window in seconds
- BIOREMPP_RESUME_ALERT_NOT_FOUND_THRESHOLD: Alert threshold for not_found
- BIOREMPP_RESUME_ALERT_TOKEN_MISMATCH_THRESHOLD: Alert threshold for token_mismatch
- BIOREMPP_RESUME_ALERT_SAVE_FAILED_THRESHOLD: Alert threshold for save_failed
- BIOREMPP_RESUME_REDIS_HOST: Resume Redis host
- BIOREMPP_RESUME_REDIS_PORT: Resume Redis port
- BIOREMPP_RESUME_REDIS_DB: Resume Redis database index
- BIOREMPP_RESUME_REDIS_PASSWORD: Resume Redis password
- BIOREMPP_RESUME_REDIS_KEY_PREFIX: Resume Redis key prefix
- BIOREMPP_RESUME_REDIS_COMPRESSION_LEVEL: Resume Redis compression level (1-9)
- BIOREMPP_RESUME_REDIS_SOCKET_TIMEOUT_SECONDS: Resume Redis socket timeout
- BIOREMPP_TRUST_PROXY_HEADERS: Trust X-Forwarded-For only from trusted proxies
- BIOREMPP_TRUSTED_PROXY_CIDRS: CSV of trusted reverse-proxy CIDRs
- BIOREMPP_PUBLIC_DATA_ALLOWED_FILES: CSV allowlist for /data/<filename>
- BIOREMPP_LOG_REF_SALT: Optional dedicated salt for log identifier redaction
- BIOREMPP_LOG_REF_LENGTH: Length of redacted log references (default: 12)
- BIOREMPP_LIMIT_REQUEST_LINE: Gunicorn max request line length
- BIOREMPP_LIMIT_REQUEST_FIELD_SIZE: Gunicorn max header field size
- BIOREMPP_LIMIT_REQUEST_FIELDS: Gunicorn max header field count
- BIOREMPP_MAX_REQUEST_BODY_BYTES: Observability threshold for request body size
- SECRET_KEY: Secret key for cryptographic/session operations (required in production)
"""

import ipaddress
import logging
import os
import secrets
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


def get_app_version() -> str:
    """
    Read application version from pyproject.toml.

    Returns
    -------
    str
        Application version string (e.g., "1.0.3-beta")

    Notes
    -----
    Falls back to "1.0.0" if pyproject.toml cannot be read.
    """
    try:
        import tomllib
    except ImportError:
        # Python < 3.11 fallback
        try:
            import tomli as tomllib
        except ImportError:
            return "1.0.0"

    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        return pyproject_data.get("project", {}).get("version", "1.0.0")
    except (FileNotFoundError, KeyError, Exception):
        return "1.0.0"


def get_app_name() -> str:
    """
    Read application name from pyproject.toml and convert to display format.

    Returns
    -------
    str
        Application display name (e.g., "BioRemPP")

    Notes
    -----
    Converts package name "biorempp-web" to display name "BioRemPP".
    Falls back to "BioRemPP" if pyproject.toml cannot be read.
    """
    try:
        import tomllib
    except ImportError:
        # Python < 3.11 fallback
        try:
            import tomli as tomllib
        except ImportError:
            return "BioRemPP"

    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomllib.load(f)
        package_name = pyproject_data.get("project", {}).get("name", "biorempp-web")
        
        # Convert package name to display name
        # "biorempp-web" -> "BioRemPP"
        if package_name.startswith("biorempp"):
            return "BioRemPP"
        return package_name.replace("-", " ").title()
    except (FileNotFoundError, KeyError, Exception):
        return "BioRemPP"


# =============================================================================
# APPLICATION METADATA (read from pyproject.toml)
# =============================================================================
APP_NAME: str = get_app_name()
APP_VERSION: str = get_app_version()

_INSECURE_SECRET_PLACEHOLDERS = frozenset(
    {
        "DEV-SECRET-KEY-NOT-SECURE",
        "DEV-SECRET-KEY-NOT-SECURE-FOR-DEVELOPMENT-ONLY",
        "CHANGE-ME-IN-PRODUCTION-USE-SECRETS-TOKEN-HEX",
        "REPLACE_WITH_REAL_SECRET_FROM_DOCKER_SECRETS",
        "REPLACE_WITH_SECURE_KEY_MINIMUM_32_CHARS_HEX",
        "CHANGE-THIS-REDIS-PASSWORD",
        "CHANGE-THIS-GRAFANA-PASSWORD",
        "__SET_IN_PROD__",
    }
)

_DEFAULT_TRUSTED_PROXY_CIDRS = ("127.0.0.1/32", "::1/128")
_DEFAULT_PUBLIC_DATA_ALLOWED_FILES = ("exemple_dataset.txt",)
_DEFAULT_LOG_REF_LENGTH = 12
_MIN_LOG_REF_LENGTH = 8
_MAX_LOG_REF_LENGTH = 24


def _is_insecure_secret(value: Optional[str], min_length: int = 1) -> bool:
    """Return True when secret value is empty, too short, or placeholder-like."""
    normalized = (value or "").strip()
    if len(normalized) < min_length:
        return True
    normalized_upper = normalized.upper()
    if normalized_upper in _INSECURE_SECRET_PLACEHOLDERS:
        return True
    if normalized_upper.startswith("CHANGE-THIS-"):
        return True
    return False


# =============================================================================
# DATABASE VERSIONS
# =============================================================================
DATABASE_VERSIONS: dict = {
    "biorempp": {
        "version": "v1.0.0",
        "name": "BioRemPP Database",
        "color": "success",
    },
    "kegg": {
        "version": "Release 116.0+/12-19",
        "name": "KEGG Degradation",
        "color": "info",
    },
    "hadeg": {
        "version": "Commit 8f1ff8f",
        "name": "HADEG",
        "color": "primary",
    },
    "toxcsm": {
        "version": "v1.0",
        "name": "ToxCSM",
        "color": "danger",
    },
}


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
    CACHE_DIR : Path
        Base cache directory (shared by long callbacks and resume payloads)
    BACKGROUND_CALLBACKS_ENABLED : bool
        Enable Dash background callbacks (auto-disabled in incompatible prod setup)
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

    URL_BASE_PATH: str = field(
        default_factory=lambda: os.getenv("BIOREMPP_URL_BASE_PATH", "/")
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

    SECRET_KEY: str = field(
        default_factory=lambda: os.getenv("SECRET_KEY", "").strip()
    )

    LOG_REF_SALT: str = field(
        default_factory=lambda: os.getenv("BIOREMPP_LOG_REF_SALT", "").strip()
    )

    LOG_REF_LENGTH: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_LOG_REF_LENGTH", _DEFAULT_LOG_REF_LENGTH
        )
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

    CACHE_DIR: Path = field(init=False)

    # ========================================================================
    # DASH CALLBACK EXECUTION
    # ========================================================================
    BACKGROUND_CALLBACKS_ENABLED: bool = field(
        default_factory=lambda: _get_bool(
            "BIOREMPP_BACKGROUND_CALLBACKS_ENABLED",
            True,
        )
    )

    # ========================================================================
    # OBSERVABILITY
    # ========================================================================
    OBSERVABILITY_ENABLED: bool = field(
        default_factory=lambda: _get_bool("BIOREMPP_OBSERVABILITY_ENABLED", False)
    )

    OBSERVABILITY_METRICS_PATH: str = field(
        default_factory=lambda: os.getenv(
            "BIOREMPP_OBSERVABILITY_METRICS_PATH",
            "/metrics",
        )
    )

    TRUST_PROXY_HEADERS: bool = field(
        default_factory=lambda: _get_bool("BIOREMPP_TRUST_PROXY_HEADERS", False)
    )

    TRUSTED_PROXY_CIDRS: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            part.strip()
            for part in os.getenv(
                "BIOREMPP_TRUSTED_PROXY_CIDRS",
                ",".join(_DEFAULT_TRUSTED_PROXY_CIDRS),
            ).split(",")
            if part.strip()
        )
    )

    PUBLIC_DATA_ALLOWED_FILES: tuple[str, ...] = field(
        default_factory=lambda: tuple(
            part.strip()
            for part in os.getenv(
                "BIOREMPP_PUBLIC_DATA_ALLOWED_FILES",
                ",".join(_DEFAULT_PUBLIC_DATA_ALLOWED_FILES),
            ).split(",")
            if part.strip()
        )
    )

    _trusted_proxy_networks: tuple[object, ...] = field(
        init=False,
        repr=False,
        default_factory=tuple,
    )
    _trusted_proxy_cidrs_explicit: bool = field(
        init=False,
        repr=False,
        default=False,
    )
    _invalid_trusted_proxy_cidrs: tuple[str, ...] = field(
        init=False,
        repr=False,
        default_factory=tuple,
    )
    _log_ref_salt_source: str = field(
        init=False,
        repr=False,
        default="unset",
    )

    # ========================================================================
    # RESUME / SECURITY CONFIGURATION
    # ========================================================================
    RESUME_BACKEND: Literal["diskcache", "redis"] = field(
        default_factory=lambda: os.getenv("BIOREMPP_RESUME_BACKEND", "diskcache")
        .strip()
        .lower()
    )

    RESUME_SECURITY_MODE: Literal["normal", "strict"] = field(
        default_factory=lambda: os.getenv("BIOREMPP_RESUME_SECURITY_MODE", "normal")
        .strip()
        .lower()
    )

    RESUME_TTL_SECONDS: int = field(
        default_factory=lambda: _get_int("BIOREMPP_RESUME_TTL_SECONDS", 14400)
    )

    RESUME_CACHE_SIZE_MB: int = field(
        default_factory=lambda: _get_int("BIOREMPP_RESUME_CACHE_SIZE_MB", 512)
    )

    RESUME_MAX_PAYLOAD_MB: int = field(
        default_factory=lambda: _get_int("BIOREMPP_RESUME_MAX_PAYLOAD_MB", 64)
    )

    RESUME_RATE_LIMIT_ATTEMPTS: int = field(
        default_factory=lambda: _get_int("BIOREMPP_RESUME_RATE_LIMIT_ATTEMPTS", 10)
    )

    RESUME_RATE_LIMIT_WINDOW_SECONDS: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_RATE_LIMIT_WINDOW_SECONDS", 60
        )
    )

    RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS", 5
        )
    )

    RESUME_RATE_LIMIT_BACKOFF_MAX_SECONDS: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_RATE_LIMIT_BACKOFF_MAX_SECONDS", 300
        )
    )

    RESUME_RATE_LIMIT_CACHE_SIZE_MB: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_RATE_LIMIT_CACHE_SIZE_MB", 64
        )
    )

    RESUME_ALERT_WINDOW_SECONDS: int = field(
        default_factory=lambda: _get_int("BIOREMPP_RESUME_ALERT_WINDOW_SECONDS", 300)
    )

    RESUME_ALERT_NOT_FOUND_THRESHOLD: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_ALERT_NOT_FOUND_THRESHOLD", 30
        )
    )

    RESUME_ALERT_TOKEN_MISMATCH_THRESHOLD: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_ALERT_TOKEN_MISMATCH_THRESHOLD", 10
        )
    )

    RESUME_ALERT_SAVE_FAILED_THRESHOLD: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_ALERT_SAVE_FAILED_THRESHOLD", 5
        )
    )

    RESUME_REDIS_HOST: str = field(
        default_factory=lambda: os.getenv(
            "BIOREMPP_RESUME_REDIS_HOST",
            os.getenv("REDIS_HOST", "redis"),
        )
    )

    RESUME_REDIS_PORT: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_REDIS_PORT",
            _get_int("REDIS_PORT", 6379),
        )
    )

    RESUME_REDIS_DB: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_REDIS_DB",
            _get_int("REDIS_DB", 0),
        )
    )

    RESUME_REDIS_PASSWORD: str = field(
        default_factory=lambda: (
            os.getenv("BIOREMPP_RESUME_REDIS_PASSWORD")
            or os.getenv("REDIS_PASSWORD", "")
        ).strip()
    )

    RESUME_REDIS_KEY_PREFIX: str = field(
        default_factory=lambda: os.getenv(
            "BIOREMPP_RESUME_REDIS_KEY_PREFIX", "biorempp:resume:"
        )
    )

    RESUME_REDIS_COMPRESSION_LEVEL: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_REDIS_COMPRESSION_LEVEL", 6
        )
    )

    RESUME_REDIS_SOCKET_TIMEOUT_SECONDS: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_RESUME_REDIS_SOCKET_TIMEOUT_SECONDS", 3
        )
    )

    GUNICORN_LIMIT_REQUEST_LINE: int = field(
        default_factory=lambda: _get_int("BIOREMPP_LIMIT_REQUEST_LINE", 4096)
    )

    GUNICORN_LIMIT_REQUEST_FIELD_SIZE: int = field(
        default_factory=lambda: _get_int("BIOREMPP_LIMIT_REQUEST_FIELD_SIZE", 8190)
    )

    GUNICORN_LIMIT_REQUEST_FIELDS: int = field(
        default_factory=lambda: _get_int("BIOREMPP_LIMIT_REQUEST_FIELDS", 100)
    )

    GUNICORN_MAX_REQUEST_BODY_BYTES: int = field(
        default_factory=lambda: _get_int(
            "BIOREMPP_MAX_REQUEST_BODY_BYTES",
            5 * 1024 * 1024,
        )
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
        self.URL_BASE_PATH = self._normalize_url_base_path(self.URL_BASE_PATH)

        # Calculate byte size for upload limit
        self.UPLOAD_MAX_SIZE_BYTES = self.UPLOAD_MAX_SIZE_MB * 1024 * 1024

        # Ensure paths exist
        self.LOG_DIR.mkdir(exist_ok=True)
        self.DATA_DIR.mkdir(exist_ok=True)

        cache_dir_raw = os.getenv(
            "BIOREMPP_CACHE_DIR",
            str(self.BASE_DIR / "cache"),
        )
        cache_path = Path(cache_dir_raw)
        if not cache_path.is_absolute():
            cache_path = self.BASE_DIR / cache_path
        self.CACHE_DIR = cache_path
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        self.OBSERVABILITY_METRICS_PATH = (
            self.OBSERVABILITY_METRICS_PATH or "/metrics"
        ).strip()
        if not self.OBSERVABILITY_METRICS_PATH:
            self.OBSERVABILITY_METRICS_PATH = "/metrics"
        if not self.OBSERVABILITY_METRICS_PATH.startswith("/"):
            self.OBSERVABILITY_METRICS_PATH = (
                f"/{self.OBSERVABILITY_METRICS_PATH}"
            )
        if len(self.OBSERVABILITY_METRICS_PATH) > 1:
            self.OBSERVABILITY_METRICS_PATH = (
                self.OBSERVABILITY_METRICS_PATH.rstrip("/")
            )
        if self.OBSERVABILITY_METRICS_PATH in ("/", "/health", "/ready"):
            print(
                "[WARNING] Invalid BIOREMPP_OBSERVABILITY_METRICS_PATH, "
                "using '/metrics'"
            )
            self.OBSERVABILITY_METRICS_PATH = "/metrics"

        raw_proxy_cidrs_env = os.getenv("BIOREMPP_TRUSTED_PROXY_CIDRS")
        self._trusted_proxy_cidrs_explicit = bool(
            raw_proxy_cidrs_env and raw_proxy_cidrs_env.strip()
        )

        normalized_proxy_cidrs: list[str] = []
        trusted_networks: list[object] = []
        invalid_proxy_cidrs: list[str] = []
        for cidr in self.TRUSTED_PROXY_CIDRS:
            cidr_candidate = (cidr or "").strip()
            if not cidr_candidate:
                continue
            try:
                network = ipaddress.ip_network(cidr_candidate, strict=False)
            except ValueError:
                invalid_proxy_cidrs.append(cidr_candidate)
                print(
                    "[WARNING] Ignoring invalid BIOREMPP_TRUSTED_PROXY_CIDRS "
                    f"entry: {cidr_candidate}"
                )
                continue
            normalized_proxy_cidrs.append(str(network))
            trusted_networks.append(network)

        if not trusted_networks:
            normalized_proxy_cidrs = list(_DEFAULT_TRUSTED_PROXY_CIDRS)
            trusted_networks = [
                ipaddress.ip_network(cidr, strict=False)
                for cidr in _DEFAULT_TRUSTED_PROXY_CIDRS
            ]
        self.TRUSTED_PROXY_CIDRS = tuple(normalized_proxy_cidrs)
        self._trusted_proxy_networks = tuple(trusted_networks)
        self._invalid_trusted_proxy_cidrs = tuple(invalid_proxy_cidrs)

        allowed_public_files: list[str] = []
        seen_public_files: set[str] = set()
        for raw_name in self.PUBLIC_DATA_ALLOWED_FILES:
            candidate = (raw_name or "").strip()
            if not candidate:
                continue
            if "/" in candidate or "\\" in candidate or ".." in candidate:
                print(
                    "[WARNING] Ignoring unsafe BIOREMPP_PUBLIC_DATA_ALLOWED_FILES "
                    f"entry: {candidate}"
                )
                continue
            normalized_name = Path(candidate).name
            if normalized_name != candidate:
                print(
                    "[WARNING] Ignoring non-basename PUBLIC_DATA_ALLOWED_FILES "
                    f"entry: {candidate}"
                )
                continue
            if normalized_name in seen_public_files:
                continue
            seen_public_files.add(normalized_name)
            allowed_public_files.append(normalized_name)

        if not allowed_public_files:
            allowed_public_files = list(_DEFAULT_PUBLIC_DATA_ALLOWED_FILES)
        self.PUBLIC_DATA_ALLOWED_FILES = tuple(allowed_public_files)

        if self.RESUME_BACKEND not in ("diskcache", "redis"):
            print(
                "[WARNING] Invalid BIOREMPP_RESUME_BACKEND, using 'diskcache'"
            )
            self.RESUME_BACKEND = "diskcache"

        if self.RESUME_SECURITY_MODE not in ("normal", "strict"):
            print(
                "[WARNING] Invalid BIOREMPP_RESUME_SECURITY_MODE, using 'normal'"
            )
            self.RESUME_SECURITY_MODE = "normal"

        self.RESUME_TTL_SECONDS = max(self.RESUME_TTL_SECONDS, 60)
        self.RESUME_CACHE_SIZE_MB = max(self.RESUME_CACHE_SIZE_MB, 32)
        self.RESUME_MAX_PAYLOAD_MB = max(self.RESUME_MAX_PAYLOAD_MB, 8)

        self.RESUME_RATE_LIMIT_ATTEMPTS = max(self.RESUME_RATE_LIMIT_ATTEMPTS, 1)
        self.RESUME_RATE_LIMIT_WINDOW_SECONDS = max(
            self.RESUME_RATE_LIMIT_WINDOW_SECONDS, 10
        )
        self.RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS = max(
            self.RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS, 1
        )
        self.RESUME_RATE_LIMIT_BACKOFF_MAX_SECONDS = max(
            self.RESUME_RATE_LIMIT_BACKOFF_MAX_SECONDS,
            self.RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS,
        )
        self.RESUME_RATE_LIMIT_CACHE_SIZE_MB = max(
            self.RESUME_RATE_LIMIT_CACHE_SIZE_MB, 16
        )

        self.RESUME_ALERT_WINDOW_SECONDS = max(self.RESUME_ALERT_WINDOW_SECONDS, 60)
        self.RESUME_ALERT_NOT_FOUND_THRESHOLD = max(
            self.RESUME_ALERT_NOT_FOUND_THRESHOLD, 1
        )
        self.RESUME_ALERT_TOKEN_MISMATCH_THRESHOLD = max(
            self.RESUME_ALERT_TOKEN_MISMATCH_THRESHOLD, 1
        )
        self.RESUME_ALERT_SAVE_FAILED_THRESHOLD = max(
            self.RESUME_ALERT_SAVE_FAILED_THRESHOLD, 1
        )

        self.RESUME_REDIS_PORT = max(self.RESUME_REDIS_PORT, 1)
        self.RESUME_REDIS_DB = max(self.RESUME_REDIS_DB, 0)
        self.RESUME_REDIS_COMPRESSION_LEVEL = min(
            max(self.RESUME_REDIS_COMPRESSION_LEVEL, 1), 9
        )
        self.RESUME_REDIS_SOCKET_TIMEOUT_SECONDS = max(
            self.RESUME_REDIS_SOCKET_TIMEOUT_SECONDS, 1
        )
        self.RESUME_REDIS_KEY_PREFIX = (
            self.RESUME_REDIS_KEY_PREFIX.strip() or "biorempp:resume:"
        )

        self.LOG_REF_LENGTH = min(
            max(int(self.LOG_REF_LENGTH), _MIN_LOG_REF_LENGTH),
            _MAX_LOG_REF_LENGTH,
        )

        configured_log_ref_salt = self.LOG_REF_SALT.strip()
        if not _is_insecure_secret(configured_log_ref_salt, min_length=16):
            self.LOG_REF_SALT = configured_log_ref_salt
            self._log_ref_salt_source = "env"
        elif not _is_insecure_secret(self.SECRET_KEY, min_length=16):
            self.LOG_REF_SALT = self.SECRET_KEY.strip()
            self._log_ref_salt_source = "secret_key"
        elif self.is_development:
            self.LOG_REF_SALT = secrets.token_hex(32)
            self._log_ref_salt_source = "ephemeral_dev"
        else:
            # Production validation will fail when SECRET_KEY is insecure.
            self.LOG_REF_SALT = self.SECRET_KEY.strip()
            self._log_ref_salt_source = "secret_key"

        if self.is_production:
            self._validate_production_security()

        self.GUNICORN_LIMIT_REQUEST_LINE = max(self.GUNICORN_LIMIT_REQUEST_LINE, 512)
        self.GUNICORN_LIMIT_REQUEST_FIELD_SIZE = max(
            self.GUNICORN_LIMIT_REQUEST_FIELD_SIZE, 512
        )
        self.GUNICORN_LIMIT_REQUEST_FIELDS = max(
            self.GUNICORN_LIMIT_REQUEST_FIELDS, 10
        )
        self.GUNICORN_MAX_REQUEST_BODY_BYTES = max(
            self.GUNICORN_MAX_REQUEST_BODY_BYTES, self.UPLOAD_MAX_SIZE_BYTES
        )

        worker_class_normalized = (self.WORKER_CLASS or "").strip().lower()
        if self.is_production and self.BACKGROUND_CALLBACKS_ENABLED:
            if self.WORKERS > 1 or worker_class_normalized in ("gevent", "eventlet"):
                print(
                    "[WARNING] Disabling BIOREMPP_BACKGROUND_CALLBACKS_ENABLED in "
                    "production due to incompatible worker model "
                    f"(workers={self.WORKERS}, worker_class={self.WORKER_CLASS})."
                )
                self.BACKGROUND_CALLBACKS_ENABLED = False

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

    def _validate_production_security(self) -> None:
        """Fail fast on insecure secret configuration in production."""
        if _is_insecure_secret(self.SECRET_KEY, min_length=32):
            raise ValueError(
                "Invalid production SECRET_KEY: missing, placeholder, or too short "
                "(minimum 32 chars)."
            )

        if self.RESUME_BACKEND == "redis" and _is_insecure_secret(
            self.RESUME_REDIS_PASSWORD, min_length=12
        ):
            raise ValueError(
                "Invalid production Redis password for resume backend: set "
                "BIOREMPP_RESUME_REDIS_PASSWORD (or REDIS_PASSWORD) with a secure value."
            )

        if self.TRUST_PROXY_HEADERS:
            if not self._trusted_proxy_cidrs_explicit:
                raise ValueError(
                    "Invalid production proxy trust configuration: "
                    "BIOREMPP_TRUSTED_PROXY_CIDRS must be explicitly set when "
                    "BIOREMPP_TRUST_PROXY_HEADERS=true."
                )
            if self._invalid_trusted_proxy_cidrs:
                invalid_entries = ", ".join(self._invalid_trusted_proxy_cidrs)
                raise ValueError(
                    "Invalid production proxy trust configuration: "
                    "BIOREMPP_TRUSTED_PROXY_CIDRS contains invalid CIDR entries "
                    f"({invalid_entries})."
                )
            default_proxy_cidrs = set(_DEFAULT_TRUSTED_PROXY_CIDRS)
            configured_proxy_cidrs = set(self.TRUSTED_PROXY_CIDRS)
            if configured_proxy_cidrs.issubset(default_proxy_cidrs):
                raise ValueError(
                    "Invalid production proxy trust configuration: "
                    "replace loopback-only trusted CIDRs with institutional "
                    "ingress/proxy CIDRs."
                )

    def is_trusted_proxy_ip(self, ip: str) -> bool:
        """Return True when IP address belongs to configured trusted proxy CIDRs."""
        candidate = (ip or "").strip()
        if not candidate:
            return False
        try:
            ip_obj = ipaddress.ip_address(candidate)
        except ValueError:
            return False
        return any(ip_obj in network for network in self._trusted_proxy_networks)

    def is_public_data_file_allowed(self, filename: str) -> bool:
        """Return True when filename is in public allowlist and path-safe."""
        candidate = (filename or "").strip()
        if not candidate:
            return False
        if "/" in candidate or "\\" in candidate or ".." in candidate:
            return False
        normalized_name = Path(candidate).name
        if normalized_name != candidate:
            return False
        return normalized_name in self.PUBLIC_DATA_ALLOWED_FILES

    @staticmethod
    def _normalize_url_base_path(path: str) -> str:
        """Normalize URL base path to '/' or '/prefix/' format."""
        candidate = (path or "/").strip()
        if not candidate:
            return "/"
        if not candidate.startswith("/"):
            candidate = f"/{candidate}"
        if candidate == "/":
            return "/"
        return f"/{candidate.strip('/')}/"

    def build_app_path(self, path: str = "/") -> str:
        """Build an application-internal path honoring URL_BASE_PATH."""
        candidate = (path or "").strip()
        if not candidate:
            return self.URL_BASE_PATH
        if candidate.startswith(("http://", "https://", "mailto:", "tel:", "#")):
            return candidate
        if not candidate.startswith("/"):
            candidate = f"/{candidate}"
        if candidate != "/" and candidate.endswith("/"):
            candidate = candidate.rstrip("/")

        base = self.URL_BASE_PATH
        if base == "/":
            return candidate

        base_without_trailing = base.rstrip("/")
        if candidate == base_without_trailing or candidate.startswith(base):
            return candidate
        if candidate == "/":
            return base
        return f"{base_without_trailing}{candidate}"

    def strip_base_path(self, pathname: Optional[str]) -> str:
        """Strip URL_BASE_PATH prefix from pathname for internal route matching."""
        candidate = (pathname or "").strip()
        if not candidate:
            return "/"
        if not candidate.startswith("/"):
            candidate = f"/{candidate}"
        if candidate != "/" and candidate.endswith("/"):
            candidate = candidate.rstrip("/")

        base = self.URL_BASE_PATH
        if base == "/":
            return candidate or "/"

        base_without_trailing = base.rstrip("/")
        if candidate == base_without_trailing or candidate == base:
            return "/"
        if candidate.startswith(base):
            stripped = candidate[len(base) - 1 :]
            return stripped or "/"
        return candidate

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
        logger.info(f"Cache Directory: {self.CACHE_DIR}")
        logger.info(
            "Observability Configuration",
            extra={
                "observability_enabled": self.OBSERVABILITY_ENABLED,
                "observability_metrics_path": self.OBSERVABILITY_METRICS_PATH,
                "url_base_path": self.URL_BASE_PATH,
                "trust_proxy_headers": self.TRUST_PROXY_HEADERS,
                "trusted_proxy_cidrs": ",".join(self.TRUSTED_PROXY_CIDRS),
                "public_data_allowed_files": ",".join(self.PUBLIC_DATA_ALLOWED_FILES),
                "log_ref_length": self.LOG_REF_LENGTH,
                "log_ref_salt_source": self._log_ref_salt_source,
            },
        )
        logger.info(
            "Resume Configuration",
            extra={
                "resume_backend": self.RESUME_BACKEND,
                "resume_security_mode": self.RESUME_SECURITY_MODE,
                "resume_ttl_seconds": self.RESUME_TTL_SECONDS,
                "resume_rate_limit_attempts": self.RESUME_RATE_LIMIT_ATTEMPTS,
                "resume_rate_limit_window_seconds": self.RESUME_RATE_LIMIT_WINDOW_SECONDS,
                "gunicorn_limit_request_line": self.GUNICORN_LIMIT_REQUEST_LINE,
                "gunicorn_limit_request_field_size": self.GUNICORN_LIMIT_REQUEST_FIELD_SIZE,
                "gunicorn_limit_request_fields": self.GUNICORN_LIMIT_REQUEST_FIELDS,
            },
        )
        logger.info(
            "Dash Callback Execution",
            extra={
                "background_callbacks_enabled": self.BACKGROUND_CALLBACKS_ENABLED,
            },
        )

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
            "Observability:",
            f"  Enabled: {self.OBSERVABILITY_ENABLED}",
            f"  Metrics Path: {self.OBSERVABILITY_METRICS_PATH}",
            f"  URL Base Path: {self.URL_BASE_PATH}",
            f"  Trust Proxy Headers: {self.TRUST_PROXY_HEADERS}",
            f"  Trusted Proxy CIDRs: {', '.join(self.TRUSTED_PROXY_CIDRS)}",
            f"  Public Data Allowlist: {', '.join(self.PUBLIC_DATA_ALLOWED_FILES)}",
            f"  Log Ref Length: {self.LOG_REF_LENGTH}",
            f"  Log Ref Salt Source: {self._log_ref_salt_source}",
            "",
            "Resume Configuration:",
            f"  Backend: {self.RESUME_BACKEND}",
            f"  Security Mode: {self.RESUME_SECURITY_MODE}",
            f"  TTL: {self.RESUME_TTL_SECONDS}s",
            f"  Cache Size: {self.RESUME_CACHE_SIZE_MB} MB",
            f"  Max Payload: {self.RESUME_MAX_PAYLOAD_MB} MB",
            f"  Rate Limit: {self.RESUME_RATE_LIMIT_ATTEMPTS} attempts / "
            f"{self.RESUME_RATE_LIMIT_WINDOW_SECONDS}s",
            f"  Backoff: base {self.RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS}s, "
            f"max {self.RESUME_RATE_LIMIT_BACKOFF_MAX_SECONDS}s",
            f"  Alert Window: {self.RESUME_ALERT_WINDOW_SECONDS}s",
            f"  Gunicorn Line Limit: {self.GUNICORN_LIMIT_REQUEST_LINE}",
            f"  Gunicorn Header Size: {self.GUNICORN_LIMIT_REQUEST_FIELD_SIZE}",
            f"  Gunicorn Header Count: {self.GUNICORN_LIMIT_REQUEST_FIELDS}",
            f"  Max Request Body: {self.GUNICORN_MAX_REQUEST_BODY_BYTES} bytes",
            "",
            "Validation Patterns:",
            f"  KO Pattern: {self.KO_PATTERN}",
            f"  Sample Name Pattern: {self.SAMPLE_NAME_PATTERN}",
            "",
            "Paths:",
            f"  Base: {self.BASE_DIR}",
            f"  Data: {self.DATA_DIR}",
            f"  Logs: {self.LOG_DIR}",
            f"  Cache: {self.CACHE_DIR}",
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
