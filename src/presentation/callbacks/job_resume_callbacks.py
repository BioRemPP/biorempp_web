"""
Job Resume Callbacks - restore processed results by `job_id`.
"""

import hashlib
import ipaddress
import math
import os
import re
import time
from uuid import uuid4

import dash_bootstrap_components as dbc
import diskcache
from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate
from flask import has_request_context, request as flask_request
from threading import Lock

from config.settings import get_settings
from src.presentation.routing import app_path
from src.presentation.services import job_resume_service
from src.presentation.services.results_payload_resolver import (
    build_results_payload_ref,
)
from src.presentation.services.results_context import build_results_context
from src.presentation.services.resume_store_redis import redis as redis_client_module
from src.shared.logging import build_log_ref, get_logger
from src.shared.metrics import (
    RESUME_CALLBACK_ATTEMPTS_TOTAL,
    RESUME_REQUEST_IP_SOURCE_TOTAL,
    RESUME_RATE_LIMIT_BACKEND_INFO,
    RESUME_RATE_LIMIT_ERRORS_TOTAL,
    instrument_callback,
)

logger = get_logger(__name__)
settings = get_settings()
_ACTIVE_RATE_LIMIT_BACKEND = "diskcache"


def _build_status_alert(message: str, color: str = "info") -> dbc.Alert:
    """Create standardized resume status alert."""
    icon_by_color = {
        "success": "fa-check-circle",
        "warning": "fa-exclamation-triangle",
        "danger": "fa-times-circle",
        "info": "fa-info-circle",
    }
    icon = icon_by_color.get(color, "fa-info-circle")
    return dbc.Alert([html.I(className=f"fas {icon} me-2"), message], color=color)


def initialize_resume_browser_token(existing_token: str):
    """
    Ensure browser resume token exists in local storage.

    Returns
    -------
    str | no_update
        Existing token is preserved; missing token gets a new UUID.
    """
    if isinstance(existing_token, str) and existing_token.strip():
        return no_update
    return str(uuid4())


def _strict_resume_errors_enabled() -> bool:
    """Enable generic resume errors to reduce job_id enumeration leaks."""
    mode = os.getenv("BIOREMPP_RESUME_SECURITY_MODE", settings.RESUME_SECURITY_MODE)
    mode = mode.strip().lower()
    return mode == "strict"


def _get_request_ip() -> str:
    """Extract client IP from request context with proxy-aware fallback."""
    if not has_request_context():
        RESUME_REQUEST_IP_SOURCE_TOTAL.labels(source="no_context").inc()
        return "unknown"

    remote_addr = (flask_request.remote_addr or "unknown").strip() or "unknown"
    if not settings.TRUST_PROXY_HEADERS:
        RESUME_REQUEST_IP_SOURCE_TOTAL.labels(source="remote_addr").inc()
        return remote_addr[:64]

    if not settings.is_trusted_proxy_ip(remote_addr):
        RESUME_REQUEST_IP_SOURCE_TOTAL.labels(source="untrusted_proxy_remote_addr").inc()
        return remote_addr[:64]

    forwarded = flask_request.headers.get("X-Forwarded-For", "")
    for candidate in (item.strip() for item in forwarded.split(",")):
        if not candidate:
            continue
        try:
            ipaddress.ip_address(candidate)
        except ValueError:
            continue
        RESUME_REQUEST_IP_SOURCE_TOTAL.labels(source="xff").inc()
        return candidate[:64]
    RESUME_REQUEST_IP_SOURCE_TOTAL.labels(source="trusted_proxy_remote_addr").inc()
    return remote_addr[:64]


def _job_id_ref(job_id: str) -> str:
    """Return deterministic, non-reversible job reference for logs."""
    return build_log_ref(job_id, namespace="job")


def _set_rate_limit_backend_info(selected_backend: str) -> None:
    """Expose selected rate-limit backend as low-cardinality gauge."""
    for backend_name in ("diskcache", "redis"):
        RESUME_RATE_LIMIT_BACKEND_INFO.labels(backend=backend_name).set(
            1.0 if backend_name == selected_backend else 0.0
        )


class ResumeRateLimiter:
    """Shared rate limiter for resume-by-job-id attempts."""

    CACHE_KEY_PREFIX = "resume_rl:"

    def __init__(
        self,
        cache_dir=None,
        cache_size_mb: int = 64,
        attempts: int = 10,
        window_seconds: int = 60,
        backoff_base_seconds: int = 5,
        backoff_max_seconds: int = 300,
    ) -> None:
        cache_path = cache_dir or (settings.CACHE_DIR / "resume_rate_limit")
        self._cache = diskcache.Cache(
            str(cache_path),
            size_limit=max(int(cache_size_mb), 16) * 1024 * 1024,
        )
        self._attempts = max(int(attempts), 1)
        self._window_seconds = max(int(window_seconds), 10)
        self._backoff_base_seconds = max(int(backoff_base_seconds), 1)
        self._backoff_max_seconds = max(
            int(backoff_max_seconds), self._backoff_base_seconds
        )
        self._lock = Lock()

    def _key(self, identity_hash: str) -> str:
        return f"{self.CACHE_KEY_PREFIX}{identity_hash}"

    @staticmethod
    def _now() -> float:
        return time.time()

    def evaluate(self, identity_hash: str) -> tuple[bool, int]:
        """
        Record one attempt and evaluate if request should be allowed.

        Returns
        -------
        tuple[bool, int]
            (allowed, retry_after_seconds)
        """
        key = self._key(identity_hash)
        now = self._now()
        ttl_for_state = max(self._window_seconds, self._backoff_max_seconds) * 3

        with self._lock:
            state = self._cache.get(key, default=None) or {}
            timestamps = [
                float(ts)
                for ts in state.get("timestamps", [])
                if now - float(ts) <= self._window_seconds
            ]
            blocked_until = float(state.get("blocked_until", 0.0))
            strike_count = int(state.get("strike_count", 0))

            if blocked_until > now:
                retry_after = int(math.ceil(blocked_until - now))
                self._cache.set(
                    key,
                    {
                        "timestamps": timestamps,
                        "blocked_until": blocked_until,
                        "strike_count": strike_count,
                    },
                    expire=ttl_for_state,
                )
                return False, max(retry_after, 1)

            timestamps.append(now)
            if len(timestamps) > self._attempts:
                strike_count += 1
                backoff_seconds = min(
                    self._backoff_max_seconds,
                    self._backoff_base_seconds * (2 ** (strike_count - 1)),
                )
                blocked_until = now + backoff_seconds
                self._cache.set(
                    key,
                    {
                        "timestamps": [],
                        "blocked_until": blocked_until,
                        "strike_count": strike_count,
                    },
                    expire=ttl_for_state,
                )
                return False, int(math.ceil(backoff_seconds))

            self._cache.set(
                key,
                {
                    "timestamps": timestamps,
                    "blocked_until": 0.0,
                    "strike_count": strike_count,
                },
                expire=ttl_for_state,
            )
            return True, 0

    def register_success(self, identity_hash: str) -> None:
        """Reset limiter state after a successful resume retrieval."""
        key = self._key(identity_hash)
        with self._lock:
            self._cache.delete(key)

    def close(self) -> None:
        self._cache.close()


class RedisResumeRateLimiter:
    """Shared Redis-backed rate limiter for multi-worker/multi-host setups."""

    PREFIX_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9:_-]{1,64}:$")
    _EVALUATE_SCRIPT = """
local now = tonumber(ARGV[1])
local attempts_limit = tonumber(ARGV[2])
local window_seconds = tonumber(ARGV[3])
local backoff_base = tonumber(ARGV[4])
local backoff_max = tonumber(ARGV[5])
local ttl_for_state = tonumber(ARGV[6])

local blocked_until = tonumber(redis.call('HGET', KEYS[2], 'blocked_until') or '0')
local strike_count = tonumber(redis.call('HGET', KEYS[2], 'strike_count') or '0')

if blocked_until > now then
    local retry_after = math.ceil(blocked_until - now)
    return {0, retry_after, strike_count}
end

local attempt_count = tonumber(redis.call('INCR', KEYS[1]))
if attempt_count == 1 then
    redis.call('EXPIRE', KEYS[1], window_seconds)
end

if attempt_count > attempts_limit then
    strike_count = strike_count + 1
    local backoff = backoff_base * (2 ^ (strike_count - 1))
    if backoff > backoff_max then
        backoff = backoff_max
    end
    if backoff < 1 then
        backoff = 1
    end
    blocked_until = now + backoff

    redis.call('HSET', KEYS[2], 'blocked_until', blocked_until, 'strike_count', strike_count)
    redis.call('EXPIRE', KEYS[2], ttl_for_state)
    redis.call('DEL', KEYS[1])
    return {0, math.ceil(backoff), strike_count}
end

redis.call('HSET', KEYS[2], 'blocked_until', 0, 'strike_count', strike_count)
redis.call('EXPIRE', KEYS[2], ttl_for_state)
return {1, 0, strike_count}
"""

    def __init__(
        self,
        host: str,
        port: int,
        db: int,
        password: str,
        key_prefix: str,
        attempts: int = 10,
        window_seconds: int = 60,
        backoff_base_seconds: int = 5,
        backoff_max_seconds: int = 300,
        socket_timeout_seconds: float = 3.0,
        client=None,
    ) -> None:
        if client is None:
            if redis_client_module is None:
                raise RuntimeError(
                    "Redis client is unavailable for rate limiter backend."
                )
            client = redis_client_module.Redis(
                host=host,
                port=int(port),
                db=int(db),
                password=(password or None),
                decode_responses=False,
                socket_timeout=float(socket_timeout_seconds),
                socket_connect_timeout=float(socket_timeout_seconds),
                health_check_interval=30,
            )

        normalized_prefix = (key_prefix or "biorempp:resume:ratelimit:").strip()
        if normalized_prefix and not normalized_prefix.endswith(":"):
            normalized_prefix = f"{normalized_prefix}:"
        if not self.PREFIX_SAFE_PATTERN.fullmatch(normalized_prefix):
            raise ValueError("Invalid redis rate-limit key prefix")

        self._client = client
        self._key_prefix = normalized_prefix
        self._attempts = max(int(attempts), 1)
        self._window_seconds = max(int(window_seconds), 10)
        self._backoff_base_seconds = max(int(backoff_base_seconds), 1)
        self._backoff_max_seconds = max(
            int(backoff_max_seconds), self._backoff_base_seconds
        )

    @staticmethod
    def _now() -> float:
        return time.time()

    def _attempts_key(self, identity_hash: str) -> str:
        return f"{self._key_prefix}attempts:{identity_hash}"

    def _block_key(self, identity_hash: str) -> str:
        return f"{self._key_prefix}block:{identity_hash}"

    def evaluate(self, identity_hash: str) -> tuple[bool, int]:
        """Record one attempt atomically in Redis and return allow/retry."""
        now = self._now()
        ttl_for_state = max(self._window_seconds, self._backoff_max_seconds) * 3
        identity_ref = identity_hash[:12]
        try:
            raw = self._client.eval(
                self._EVALUATE_SCRIPT,
                2,
                self._attempts_key(identity_hash),
                self._block_key(identity_hash),
                now,
                self._attempts,
                self._window_seconds,
                self._backoff_base_seconds,
                self._backoff_max_seconds,
                ttl_for_state,
            )
            allowed = bool(int(raw[0]))
            retry_after_seconds = max(int(raw[1]), 0)
            return allowed, retry_after_seconds
        except Exception:
            RESUME_RATE_LIMIT_ERRORS_TOTAL.labels(
                backend="redis",
                operation="evaluate",
            ).inc()
            logger.exception(
                "Redis resume rate limiter evaluate failed; allowing request",
                extra={"identity_ref": identity_ref},
            )
            # Fail-open keeps resume flow available if Redis limiter is temporarily down.
            return True, 0

    def register_success(self, identity_hash: str) -> None:
        """Reset limiter state after successful resume retrieval."""
        identity_ref = identity_hash[:12]
        try:
            self._client.delete(
                self._attempts_key(identity_hash),
                self._block_key(identity_hash),
            )
        except Exception:
            RESUME_RATE_LIMIT_ERRORS_TOTAL.labels(
                backend="redis",
                operation="reset",
            ).inc()
            logger.exception(
                "Redis resume rate limiter reset failed",
                extra={"identity_ref": identity_ref},
            )

    def close(self) -> None:
        close_fn = getattr(self._client, "close", None)
        if callable(close_fn):
            close_fn()


def _resolve_resume_rate_limit_backend() -> str:
    """Resolve resume rate-limit backend (auto follows resume backend)."""
    backend = (settings.RESUME_RATE_LIMIT_BACKEND or "auto").strip().lower()
    if backend not in {"auto", "diskcache", "redis"}:
        backend = "auto"
    if backend == "auto":
        return "redis" if settings.RESUME_BACKEND == "redis" else "diskcache"
    return backend


def _build_resume_rate_limiter():
    """Build rate limiter backend with safe fallback behavior."""
    global _ACTIVE_RATE_LIMIT_BACKEND
    backend = _resolve_resume_rate_limit_backend()
    if backend == "redis":
        try:
            limiter = RedisResumeRateLimiter(
                host=settings.RESUME_REDIS_HOST,
                port=settings.RESUME_REDIS_PORT,
                db=settings.RESUME_REDIS_DB,
                password=settings.RESUME_REDIS_PASSWORD,
                key_prefix=settings.RESUME_RATE_LIMIT_REDIS_KEY_PREFIX,
                attempts=settings.RESUME_RATE_LIMIT_ATTEMPTS,
                window_seconds=settings.RESUME_RATE_LIMIT_WINDOW_SECONDS,
                backoff_base_seconds=settings.RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS,
                backoff_max_seconds=settings.RESUME_RATE_LIMIT_BACKOFF_MAX_SECONDS,
                socket_timeout_seconds=settings.RESUME_REDIS_SOCKET_TIMEOUT_SECONDS,
            )
            logger.info(
                "Resume rate limiter backend selected",
                extra={"backend": "redis"},
            )
            _set_rate_limit_backend_info("redis")
            _ACTIVE_RATE_LIMIT_BACKEND = "redis"
            return limiter
        except Exception:
            RESUME_RATE_LIMIT_ERRORS_TOTAL.labels(
                backend="redis",
                operation="init",
            ).inc()
            logger.exception(
                "Failed to initialize Redis resume rate limiter; using diskcache fallback"
            )

    limiter = ResumeRateLimiter(
        cache_size_mb=settings.RESUME_RATE_LIMIT_CACHE_SIZE_MB,
        attempts=settings.RESUME_RATE_LIMIT_ATTEMPTS,
        window_seconds=settings.RESUME_RATE_LIMIT_WINDOW_SECONDS,
        backoff_base_seconds=settings.RESUME_RATE_LIMIT_BACKOFF_BASE_SECONDS,
        backoff_max_seconds=settings.RESUME_RATE_LIMIT_BACKOFF_MAX_SECONDS,
    )
    logger.info(
        "Resume rate limiter backend selected",
        extra={"backend": "diskcache"},
    )
    _set_rate_limit_backend_info("diskcache")
    _ACTIVE_RATE_LIMIT_BACKEND = "diskcache"
    return limiter


resume_rate_limiter = _build_resume_rate_limiter()


def _identity_hash(owner_token: str, ip_address: str) -> str:
    token_value = owner_token.strip() if isinstance(owner_token, str) else ""
    digest = hashlib.sha256(f"{ip_address}|{token_value}".encode("utf-8")).hexdigest()
    return digest


def _ip_ref(ip_address: str) -> str:
    """Return non-reversible short reference for client ip logs."""
    return hashlib.sha256((ip_address or "unknown").encode("utf-8")).hexdigest()[:12]


def resolve_resume_request(job_id: str, owner_token: str):
    """
    Resolve resume flow outputs from job_id + owner_token.

    Returns
    -------
    tuple
        (
            merged_result_store_update,
            results_context_store_update,
            pathname_update,
            hash_update,
            status_component,
        )
    """
    _set_rate_limit_backend_info(_ACTIVE_RATE_LIMIT_BACKEND)
    normalized_job_id = (job_id or "").strip().upper()
    ip_address = _get_request_ip()
    ip_ref = _ip_ref(ip_address)
    RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="attempt").inc()

    if not normalized_job_id:
        RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="empty_job_id").inc()
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            _build_status_alert("Provide a Job ID to resume an analysis.", "warning"),
        )

    if not isinstance(owner_token, str) or not owner_token.strip():
        RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="token_missing").inc()
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            _build_status_alert(
                "This browser context is not initialized for resume yet.",
                "danger",
            ),
        )

    identity_hash = _identity_hash(owner_token, ip_address)
    allowed, retry_after_seconds = resume_rate_limiter.evaluate(identity_hash)
    if not allowed:
        RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="rate_limited").inc()
        logger.warning(
            "Resume request blocked by rate limiter",
            extra={
                "event": "resume_rate_limit_blocked",
                "client_ref": ip_ref,
                "identity_ref": identity_hash[:12],
                "retry_after_seconds": retry_after_seconds,
            },
        )
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            _build_status_alert(
                f"Too many resume attempts. Please retry in {retry_after_seconds}s.",
                "danger",
            ),
        )

    if len(normalized_job_id) != 26:
        RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="invalid_job_id").inc()
        logger.info(
            "Resume request rejected (invalid length)",
            extra={
                "event": "resume_invalid_job_length",
                "client_ref": ip_ref,
                "identity_ref": identity_hash[:12],
            },
        )
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            _build_status_alert(
                "Invalid Job ID length. Use BRP-YYYYMMDD-HHMMSS-XXXXXX.",
                "danger",
            ),
        )

    if not job_resume_service.validate_job_id(normalized_job_id):
        RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="invalid_job_id").inc()
        logger.info(
            "Resume request rejected (invalid format)",
            extra={
                "event": "resume_invalid_job_format",
                "client_ref": ip_ref,
                "identity_ref": identity_hash[:12],
            },
        )
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            _build_status_alert(
                "Invalid Job ID format. Use BRP-YYYYMMDD-HHMMSS-XXXXXX.",
                "danger",
            ),
        )

    payload, status = job_resume_service.load_job_payload(
        normalized_job_id, owner_token
    )
    job_ref = _job_id_ref(normalized_job_id)

    if status == job_resume_service.STATUS_OK and payload is not None:
        RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="success").inc()
        logger.info(
            "Resume request succeeded",
            extra={
                "event": "resume_load_ok",
                "client_ref": ip_ref,
                "identity_ref": identity_hash[:12],
                "job_ref": job_ref,
            },
        )
        resume_rate_limiter.register_success(identity_hash)
        merged_store_payload = payload
        if settings.RESULTS_PAYLOAD_MODE == "server":
            merged_store_payload = build_results_payload_ref(payload, owner_token)
        return (
            merged_store_payload,
            build_results_context(merged_store_payload),
            app_path("/results"),
            "",
            _build_status_alert(
                f"Job {normalized_job_id} loaded. Redirecting to results...",
                "success",
            ),
        )

    if status == job_resume_service.STATUS_TOKEN_MISMATCH:
        RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="token_mismatch").inc()
        logger.warning(
            "Resume request denied by owner-token mismatch",
            extra={
                "event": "resume_token_mismatch",
                "client_ref": ip_ref,
                "identity_ref": identity_hash[:12],
                "job_ref": job_ref,
            },
        )
        if _strict_resume_errors_enabled():
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                _build_status_alert(
                    "Job ID unavailable in this browser context.", "warning"
                ),
            )
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            _build_status_alert(
                "This Job ID belongs to another browser context.", "danger"
            ),
        )

    if status == job_resume_service.STATUS_INCOMPATIBLE_VERSION:
        RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="incompatible_version").inc()
        logger.warning(
            "Resume request denied by incompatible payload version",
            extra={
                "event": "resume_incompatible_payload_version",
                "client_ref": ip_ref,
                "identity_ref": identity_hash[:12],
                "job_ref": job_ref,
            },
        )
        if _strict_resume_errors_enabled():
            return (
                no_update,
                no_update,
                no_update,
                no_update,
                _build_status_alert(
                    "Job ID unavailable in this browser context.", "warning"
                ),
            )
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            _build_status_alert(
                "Stored job data version is not compatible anymore. "
                "Please process the file again.",
                "danger",
            ),
        )

    RESUME_CALLBACK_ATTEMPTS_TOTAL.labels(outcome="not_found").inc()
    logger.info(
        "Resume request missed (not_found_or_expired)",
        extra={
            "event": "resume_not_found",
            "client_ref": ip_ref,
            "identity_ref": identity_hash[:12],
            "job_ref": job_ref,
        },
    )
    if _strict_resume_errors_enabled():
        return (
            no_update,
            no_update,
            no_update,
            no_update,
            _build_status_alert("Job ID unavailable in this browser context.", "warning"),
        )

    return (
        no_update,
        no_update,
        no_update,
        no_update,
        _build_status_alert(
            "Job ID not found or expired. Run processing again to generate a new job.",
            "warning",
        ),
    )


def register_job_resume_callbacks(app):
    """Register callbacks related to resume-by-job-id flow."""
    logger.info("=" * 60)
    logger.info("Registering JOB RESUME callbacks...")
    logger.info("=" * 60)

    @app.callback(
        Output("resume-browser-token-store", "data"),
        Input("resume-browser-token-store", "modified_timestamp"),
        State("resume-browser-token-store", "data"),
    )
    @instrument_callback("resume.ensure_browser_token")
    def ensure_resume_browser_token(_, existing_token):
        token = initialize_resume_browser_token(existing_token)
        if token is no_update:
            raise PreventUpdate
        logger.info("Resume browser token initialized")
        return token

    @app.callback(
        [
            Output("merged-result-store", "data", allow_duplicate=True),
            Output("results-context-store", "data", allow_duplicate=True),
            Output("url", "pathname"),
            Output("url", "hash"),
            Output("resume-job-status", "children"),
        ],
        Input("resume-job-btn", "n_clicks"),
        [
            State("resume-job-id-input", "value"),
            State("resume-browser-token-store", "data"),
        ],
        prevent_initial_call=True,
    )
    @instrument_callback("resume.resume_job_by_id")
    def resume_job_by_id(n_clicks, job_id, owner_token):
        if n_clicks is None:
            raise PreventUpdate

        return resolve_resume_request(job_id, owner_token)

    logger.info("[OK] Job resume callbacks registered successfully")
