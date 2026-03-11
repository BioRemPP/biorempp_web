"""
Job Resume Service - orchestration layer for resumable processed results.

The service validates job metadata and delegates persistence to a ResumeStore
backend (diskcache or redis).
"""

import json
import os
import re
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Callable, Optional

from .resume_store import ResumeStore
from .resume_store_diskcache import DiskcacheResumeStore
from src.shared.logging import build_log_ref, get_logger
from src.shared.metrics import (
    RESUME_LOAD_ATTEMPTS_TOTAL,
    RESUME_OPERATION_DURATION_SECONDS,
    RESUME_PAYLOAD_SIZE_BYTES,
    RESUME_SAVE_TOTAL,
)

logger = get_logger(__name__)


class JobResumeService:
    """Service for saving and loading processed payloads by `job_id`."""

    CACHE_KEY_PREFIX = "resume:v1:job:"
    CACHE_KEY_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9:_-]{1,128}$")
    DEFAULT_TTL_SECONDS = 14400  # 4 hours
    DEFAULT_CACHE_SIZE_MB = 512
    DEFAULT_MAX_PAYLOAD_MB = 64
    DEFAULT_ALERT_WINDOW_SECONDS = 300
    DEFAULT_ALERT_NOT_FOUND_THRESHOLD = 30
    DEFAULT_ALERT_TOKEN_MISMATCH_THRESHOLD = 10
    DEFAULT_ALERT_SAVE_FAILED_THRESHOLD = 5
    CURRENT_PAYLOAD_VERSION = 1
    SUPPORTED_PAYLOAD_VERSIONS = {1}
    PAYLOAD_SCHEMA_PREFIX = "resume-payload-v"
    JOB_ID_PATTERN = re.compile(r"^BRP-\d{8}-\d{6}-[A-F0-9]{6}$")

    STATUS_OK = "ok"
    STATUS_INVALID_JOB_ID = "invalid_job_id"
    STATUS_NOT_FOUND = "not_found"
    STATUS_TOKEN_MISMATCH = "token_mismatch"
    STATUS_TOKEN_MISSING = "token_missing"
    STATUS_INCOMPATIBLE_VERSION = "incompatible_version"
    STATUS_SAVE_FAILED = "save_failed"

    def __init__(
        self,
        store: Optional[ResumeStore] = None,
        cache_dir: Optional[Path] = None,
        ttl_seconds: Optional[int] = None,
        cache_size_mb: Optional[int] = None,
        max_payload_mb: Optional[int] = None,
        alert_window_seconds: Optional[int] = None,
        alert_not_found_threshold: Optional[int] = None,
        alert_token_mismatch_threshold: Optional[int] = None,
        alert_save_failed_threshold: Optional[int] = None,
    ) -> None:
        """
        Initialize service orchestration and persistence backend.

        Parameters
        ----------
        store : Optional[ResumeStore]
            Persistence adapter. Defaults to DiskcacheResumeStore.
        cache_dir : Optional[Path]
            Diskcache directory path when store is not provided.
        ttl_seconds : Optional[int]
            Default TTL in seconds.
        cache_size_mb : Optional[int]
            Maximum cache size in MB (diskcache backend only).
        max_payload_mb : Optional[int]
            Maximum size of a single resume payload in MB.
        alert_window_seconds : Optional[int]
            Rolling window (seconds) for anomaly alerts.
        alert_not_found_threshold : Optional[int]
            Alert threshold for not_found events inside alert window.
        alert_token_mismatch_threshold : Optional[int]
            Alert threshold for token_mismatch events inside alert window.
        alert_save_failed_threshold : Optional[int]
            Alert threshold for save_failed events inside alert window.
        """
        project_root = Path(__file__).resolve().parents[3]
        base_cache_dir = self._resolve_base_cache_dir(project_root)
        self._cache_dir = (
            Path(cache_dir) if cache_dir is not None else base_cache_dir / "job_resume"
        )

        self._ttl_seconds = (
            int(ttl_seconds)
            if ttl_seconds is not None
            else self._read_env_int(
                "BIOREMPP_RESUME_TTL_SECONDS",
                self.DEFAULT_TTL_SECONDS,
                minimum=60,
            )
        )
        self._cache_size_mb = (
            int(cache_size_mb)
            if cache_size_mb is not None
            else self._read_env_int(
                "BIOREMPP_RESUME_CACHE_SIZE_MB",
                self.DEFAULT_CACHE_SIZE_MB,
                minimum=32,
            )
        )
        self._max_payload_mb = (
            int(max_payload_mb)
            if max_payload_mb is not None
            else self._read_env_int(
                "BIOREMPP_RESUME_MAX_PAYLOAD_MB",
                self.DEFAULT_MAX_PAYLOAD_MB,
                minimum=8,
            )
        )
        self._max_payload_bytes = self._max_payload_mb * 1024 * 1024
        self._alert_window_seconds = (
            int(alert_window_seconds)
            if alert_window_seconds is not None
            else self._read_env_int(
                "BIOREMPP_RESUME_ALERT_WINDOW_SECONDS",
                self.DEFAULT_ALERT_WINDOW_SECONDS,
                minimum=60,
            )
        )
        self._alert_thresholds = {
            self.STATUS_NOT_FOUND: (
                int(alert_not_found_threshold)
                if alert_not_found_threshold is not None
                else self._read_env_int(
                    "BIOREMPP_RESUME_ALERT_NOT_FOUND_THRESHOLD",
                    self.DEFAULT_ALERT_NOT_FOUND_THRESHOLD,
                    minimum=1,
                )
            ),
            self.STATUS_TOKEN_MISMATCH: (
                int(alert_token_mismatch_threshold)
                if alert_token_mismatch_threshold is not None
                else self._read_env_int(
                    "BIOREMPP_RESUME_ALERT_TOKEN_MISMATCH_THRESHOLD",
                    self.DEFAULT_ALERT_TOKEN_MISMATCH_THRESHOLD,
                    minimum=1,
                )
            ),
            "save_failed": (
                int(alert_save_failed_threshold)
                if alert_save_failed_threshold is not None
                else self._read_env_int(
                    "BIOREMPP_RESUME_ALERT_SAVE_FAILED_THRESHOLD",
                    self.DEFAULT_ALERT_SAVE_FAILED_THRESHOLD,
                    minimum=1,
                )
            ),
        }
        self._event_history: dict[str, deque[float]] = {
            event: deque() for event in self._alert_thresholds
        }
        self._last_alert_ts: dict[str, float] = {event: 0.0 for event in self._alert_thresholds}
        self._event_lock = Lock()

        self._store = (
            store
            if store is not None
            else DiskcacheResumeStore(
                cache_dir=self._cache_dir,
                cache_size_mb=self._cache_size_mb,
            )
        )

        # Exposed for tests using diskcache adapter internals.
        self._cache = getattr(self._store, "_cache", None)

        logger.info(
            "JobResumeService initialized",
            extra={
                "backend": self._store.backend_name,
                "cache_dir": str(self._cache_dir),
                "ttl_seconds": self._ttl_seconds,
                "cache_size_mb": self._cache_size_mb,
                "max_payload_mb": self._max_payload_mb,
                "alert_window_seconds": self._alert_window_seconds,
            },
        )

    @staticmethod
    def _read_env_int(name: str, default: int, minimum: int = 1) -> int:
        """Read int environment variable with fallback and floor."""
        raw_value = os.getenv(name)
        if raw_value is None:
            return max(default, minimum)
        try:
            return max(int(raw_value), minimum)
        except ValueError:
            return max(default, minimum)

    @staticmethod
    def _resolve_base_cache_dir(project_root: Path) -> Path:
        """Resolve standardized cache root from BIOREMPP_CACHE_DIR."""
        raw_value = os.getenv("BIOREMPP_CACHE_DIR")
        if not raw_value:
            return project_root / "cache"
        candidate = Path(raw_value)
        if not candidate.is_absolute():
            candidate = project_root / candidate
        return candidate

    def get_resume_ttl_seconds(self) -> int:
        """Return configured default TTL used for resume payloads."""
        return self._ttl_seconds

    def get_resume_max_payload_mb(self) -> int:
        """Return configured max payload size per job (MB)."""
        return self._max_payload_mb

    @classmethod
    def estimate_payload_size_bytes(cls, payload: dict) -> int:
        """Estimate serialized payload size in bytes."""
        return cls._estimate_payload_size(payload)

    @classmethod
    def validate_job_id(cls, job_id: str) -> bool:
        """
        Validate `job_id` format.

        Expected format: BRP-YYYYMMDD-HHMMSS-XXXXXX (hex suffix).
        """
        if not isinstance(job_id, str):
            return False
        return bool(cls.JOB_ID_PATTERN.match(job_id.strip().upper()))

    @staticmethod
    def _mask_job_id(job_id: str) -> str:
        """Return deterministic, redacted job reference for logs."""
        return build_log_ref(job_id, namespace="job")

    @classmethod
    def _expected_payload_schema(cls, payload_version: int) -> str:
        return f"{cls.PAYLOAD_SCHEMA_PREFIX}{payload_version}"

    @classmethod
    def _sanitize_cache_key(cls, key: str, required_prefix: str) -> str:
        """
        Validate store key shape and prefix isolation.

        Raises
        ------
        ValueError
            If key format is unsafe or outside expected namespace.
        """
        if not isinstance(key, str):
            raise ValueError("Cache key must be string")
        if not key.startswith(required_prefix):
            raise ValueError("Cache key prefix mismatch")
        if ".." in key or "\\" in key or "//" in key:
            raise ValueError("Cache key contains traversal sequence")
        if not cls.CACHE_KEY_SAFE_PATTERN.fullmatch(key):
            raise ValueError("Cache key contains unsafe characters")
        return key

    def _build_cache_key(self, job_id: str) -> str:
        """Build isolated cache key from validated job identifier."""
        normalized_job_id = (job_id or "").strip().upper()
        if not self.validate_job_id(normalized_job_id):
            raise ValueError("Invalid job id for cache key")
        return self._sanitize_cache_key(
            f"{self.CACHE_KEY_PREFIX}{normalized_job_id}",
            required_prefix=self.CACHE_KEY_PREFIX,
        )

    def _record_security_event(self, event_name: str) -> None:
        """Track events and emit operational alerts when threshold is exceeded."""
        threshold = self._alert_thresholds.get(event_name)
        if threshold is None:
            return

        now = time.time()
        with self._event_lock:
            events = self._event_history[event_name]
            events.append(now)
            cutoff = now - self._alert_window_seconds
            while events and events[0] < cutoff:
                events.popleft()

            current_count = len(events)
            if current_count < threshold:
                return

            # Avoid repeated identical alerts at high traffic.
            cooldown = max(self._alert_window_seconds // 2, 30)
            last_alert = self._last_alert_ts.get(event_name, 0.0)
            if now - last_alert < cooldown:
                return
            self._last_alert_ts[event_name] = now

        logger.warning(
            "Resume security alert threshold exceeded",
            extra={
                "event": event_name,
                "count": current_count,
                "window_seconds": self._alert_window_seconds,
                "threshold": threshold,
                "backend": self._store.backend_name,
            },
        )

    @staticmethod
    def _normalize_resume_metric_status(status: str) -> str:
        """Collapse internal statuses into stable metric buckets."""
        if status in ("ok", "not_found", "token_mismatch", "save_failed"):
            return status
        if status in ("invalid_job_id", "token_missing", "incompatible_version"):
            return "not_found"
        return "save_failed"

    def _emit_save_metrics(
        self,
        status: str,
        elapsed_seconds: float,
        payload_size_bytes: Optional[int] = None,
    ) -> None:
        metric_status = self._normalize_resume_metric_status(status)
        RESUME_SAVE_TOTAL.labels(outcome=metric_status).inc()
        RESUME_OPERATION_DURATION_SECONDS.labels(
            backend=self._store.backend_name,
            operation="save",
            status=metric_status,
        ).observe(max(float(elapsed_seconds), 0.0))
        if payload_size_bytes is not None and payload_size_bytes >= 0:
            RESUME_PAYLOAD_SIZE_BYTES.labels(
                backend=self._store.backend_name
            ).observe(float(payload_size_bytes))

    def _emit_load_metrics(
        self,
        status: str,
        elapsed_seconds: float,
        payload_size_bytes: Optional[int] = None,
    ) -> None:
        metric_status = self._normalize_resume_metric_status(status)
        RESUME_LOAD_ATTEMPTS_TOTAL.labels(outcome=metric_status).inc()
        RESUME_OPERATION_DURATION_SECONDS.labels(
            backend=self._store.backend_name,
            operation="load",
            status=metric_status,
        ).observe(max(float(elapsed_seconds), 0.0))
        if payload_size_bytes is not None and payload_size_bytes >= 0:
            RESUME_PAYLOAD_SIZE_BYTES.labels(
                backend=self._store.backend_name
            ).observe(float(payload_size_bytes))

    @staticmethod
    def _estimate_payload_size(payload: dict) -> int:
        """Estimate payload size in bytes for logging."""
        try:
            return len(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        except Exception:
            return len(str(payload).encode("utf-8", errors="ignore"))

    def save_job_payload(
        self,
        job_id: str,
        payload: dict,
        owner_token: str,
        ttl_seconds: Optional[int] = None,
        on_store_set_complete: Optional[Callable[[bool, float], None]] = None,
    ) -> bool:
        """
        Save serialized result payload by `job_id`.

        Parameters
        ----------
        job_id : str
            Processing job identifier.
        payload : dict
            Serialized `merged-result-store` payload.
        owner_token : str
            Browser ownership token for same-browser enforcement.
        ttl_seconds : Optional[int]
            Custom TTL override.
        on_store_set_complete : Optional[Callable[[bool, float], None]]
            Optional callback invoked right after backend `set()` completes with
            `(saved, store_set_ms)`.
        """
        normalized_job_id = (job_id or "").strip().upper()
        operation_started = time.perf_counter()
        serialize_check_ms = 0.0
        store_set_ms = 0.0
        metrics_emit_ms = 0.0
        payload_size_bytes: Optional[int] = None
        masked_job_id = self._mask_job_id(normalized_job_id)

        def _emit_timing_log(status: str) -> None:
            total_ms = (time.perf_counter() - operation_started) * 1000
            logger.info(
                "Resume payload persistence timing",
                extra={
                    "job_ref": masked_job_id,
                    "backend": self._store.backend_name,
                    "status": status,
                    "payload_size_bytes": payload_size_bytes,
                    "serialize_check_ms": round(float(serialize_check_ms), 2),
                    "store_set_ms": round(float(store_set_ms), 2),
                    "metrics_emit_ms": round(float(metrics_emit_ms), 2),
                    "total_ms": round(float(total_ms), 2),
                },
            )

        if not self.validate_job_id(normalized_job_id):
            logger.warning("Refusing to save resume payload: invalid job_id format")
            metrics_started = time.perf_counter()
            self._emit_save_metrics(
                self.STATUS_SAVE_FAILED,
                time.perf_counter() - operation_started,
            )
            metrics_emit_ms = (time.perf_counter() - metrics_started) * 1000
            _emit_timing_log(self.STATUS_SAVE_FAILED)
            return False
        if not isinstance(payload, dict):
            logger.warning(
                "Refusing to save resume payload: payload must be dict",
                extra={"job_ref": masked_job_id},
            )
            metrics_started = time.perf_counter()
            self._emit_save_metrics(
                self.STATUS_SAVE_FAILED,
                time.perf_counter() - operation_started,
            )
            metrics_emit_ms = (time.perf_counter() - metrics_started) * 1000
            _emit_timing_log(self.STATUS_SAVE_FAILED)
            return False
        if not isinstance(owner_token, str) or not owner_token.strip():
            logger.warning(
                "Refusing to save resume payload: missing owner_token",
                extra={"job_ref": masked_job_id},
            )
            metrics_started = time.perf_counter()
            self._emit_save_metrics(
                self.STATUS_SAVE_FAILED,
                time.perf_counter() - operation_started,
            )
            metrics_emit_ms = (time.perf_counter() - metrics_started) * 1000
            _emit_timing_log(self.STATUS_SAVE_FAILED)
            return False

        if ttl_seconds is None:
            ttl = self._ttl_seconds
        else:
            try:
                ttl = max(int(ttl_seconds), 1)
            except (TypeError, ValueError):
                ttl = self._ttl_seconds

        payload_size_bytes = self.estimate_payload_size_bytes(payload)
        if payload_size_bytes > self._max_payload_bytes:
            self._record_security_event("save_failed")
            logger.warning(
                "Refusing to save resume payload: payload too large",
                extra={
                    "job_ref": masked_job_id,
                    "payload_size_bytes": payload_size_bytes,
                    "max_payload_bytes": self._max_payload_bytes,
                },
            )
            metrics_started = time.perf_counter()
            self._emit_save_metrics(
                self.STATUS_SAVE_FAILED,
                time.perf_counter() - operation_started,
                payload_size_bytes=payload_size_bytes,
            )
            metrics_emit_ms = (time.perf_counter() - metrics_started) * 1000
            _emit_timing_log(self.STATUS_SAVE_FAILED)
            return False

        try:
            cache_key = self._build_cache_key(normalized_job_id)
        except ValueError:
            self._record_security_event("save_failed")
            logger.warning("Refusing to save resume payload: unsafe cache key")
            metrics_started = time.perf_counter()
            self._emit_save_metrics(
                self.STATUS_SAVE_FAILED,
                time.perf_counter() - operation_started,
                payload_size_bytes=payload_size_bytes,
            )
            metrics_emit_ms = (time.perf_counter() - metrics_started) * 1000
            _emit_timing_log(self.STATUS_SAVE_FAILED)
            return False

        cache_value = {
            "job_id": normalized_job_id,
            "owner_token": owner_token.strip(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "payload_version": self.CURRENT_PAYLOAD_VERSION,
            "payload_schema": self._expected_payload_schema(
                self.CURRENT_PAYLOAD_VERSION
            ),
            "merged_result_payload": payload,
        }

        serialize_check_ms = (time.perf_counter() - operation_started) * 1000
        start_time = time.perf_counter()
        saved = self._store.set(cache_key, cache_value, ttl)
        store_set_ms = (time.perf_counter() - start_time) * 1000
        if on_store_set_complete is not None:
            try:
                on_store_set_complete(bool(saved), float(store_set_ms))
            except Exception:  # pragma: no cover - defensive callback guard
                logger.debug(
                    "on_store_set_complete callback failed",
                    exc_info=True,
                )

        total_elapsed_s = time.perf_counter() - operation_started
        if saved:
            logger.info(
                "Resume payload saved",
                extra={
                    "job_ref": masked_job_id,
                    "backend": self._store.backend_name,
                    "ttl_seconds": ttl,
                    "payload_size_bytes": payload_size_bytes,
                    "save_ms": round(store_set_ms, 2),
                },
            )
            metrics_started = time.perf_counter()
            self._emit_save_metrics(
                self.STATUS_OK,
                total_elapsed_s,
                payload_size_bytes=payload_size_bytes,
            )
            metrics_emit_ms = (time.perf_counter() - metrics_started) * 1000
            _emit_timing_log(self.STATUS_OK)
        else:
            self._record_security_event("save_failed")
            logger.warning(
                "Failed to persist resume payload",
                extra={
                    "job_ref": masked_job_id,
                    "backend": self._store.backend_name,
                    "payload_size_bytes": payload_size_bytes,
                    "save_ms": round(store_set_ms, 2),
                },
            )
            metrics_started = time.perf_counter()
            self._emit_save_metrics(
                self.STATUS_SAVE_FAILED,
                total_elapsed_s,
                payload_size_bytes=payload_size_bytes,
            )
            metrics_emit_ms = (time.perf_counter() - metrics_started) * 1000
            _emit_timing_log(self.STATUS_SAVE_FAILED)
        return saved

    def load_job_payload(
        self,
        job_id: str,
        owner_token: str,
    ) -> tuple[Optional[dict], str]:
        """
        Load serialized payload by `job_id`.

        Returns
        -------
        tuple[Optional[dict], str]
            (payload, status) where status is one of:
            ok, invalid_job_id, not_found, token_missing, token_mismatch,
            incompatible_version.
        """
        normalized_job_id = (job_id or "").strip().upper()
        operation_started = time.perf_counter()
        if not self.validate_job_id(normalized_job_id):
            self._emit_load_metrics(
                self.STATUS_INVALID_JOB_ID,
                time.perf_counter() - operation_started,
            )
            return None, self.STATUS_INVALID_JOB_ID

        if not isinstance(owner_token, str) or not owner_token.strip():
            self._emit_load_metrics(
                self.STATUS_TOKEN_MISSING,
                time.perf_counter() - operation_started,
            )
            return None, self.STATUS_TOKEN_MISSING

        masked_job_id = self._mask_job_id(normalized_job_id)
        try:
            cache_key = self._build_cache_key(normalized_job_id)
        except ValueError:
            self._emit_load_metrics(
                self.STATUS_INVALID_JOB_ID,
                time.perf_counter() - operation_started,
            )
            return None, self.STATUS_INVALID_JOB_ID

        start_time = time.perf_counter()
        cached = self._store.get(cache_key)
        if not isinstance(cached, dict):
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._record_security_event(self.STATUS_NOT_FOUND)
            logger.info(
                "Resume payload lookup miss",
                extra={
                    "job_ref": masked_job_id,
                    "backend": self._store.backend_name,
                    "load_ms": round(elapsed_ms, 2),
                },
            )
            self._emit_load_metrics(
                self.STATUS_NOT_FOUND,
                time.perf_counter() - operation_started,
            )
            return None, self.STATUS_NOT_FOUND

        cached_owner_token = cached.get("owner_token")
        if cached_owner_token != owner_token.strip():
            self._record_security_event(self.STATUS_TOKEN_MISMATCH)
            self._emit_load_metrics(
                self.STATUS_TOKEN_MISMATCH,
                time.perf_counter() - operation_started,
            )
            return None, self.STATUS_TOKEN_MISMATCH

        raw_payload_version = cached.get("payload_version")
        if not isinstance(raw_payload_version, int):
            self._emit_load_metrics(
                self.STATUS_INCOMPATIBLE_VERSION,
                time.perf_counter() - operation_started,
            )
            return None, self.STATUS_INCOMPATIBLE_VERSION
        payload_version = raw_payload_version
        if payload_version not in self.SUPPORTED_PAYLOAD_VERSIONS:
            self._emit_load_metrics(
                self.STATUS_INCOMPATIBLE_VERSION,
                time.perf_counter() - operation_started,
            )
            return None, self.STATUS_INCOMPATIBLE_VERSION
        payload_schema = cached.get("payload_schema")
        expected_schema = self._expected_payload_schema(payload_version)
        if payload_schema != expected_schema:
            self._emit_load_metrics(
                self.STATUS_INCOMPATIBLE_VERSION,
                time.perf_counter() - operation_started,
            )
            return None, self.STATUS_INCOMPATIBLE_VERSION

        payload = cached.get("merged_result_payload")
        if not isinstance(payload, dict):
            self._record_security_event(self.STATUS_NOT_FOUND)
            self._emit_load_metrics(
                self.STATUS_NOT_FOUND,
                time.perf_counter() - operation_started,
            )
            return None, self.STATUS_NOT_FOUND

        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "Resume payload loaded",
            extra={
                "job_ref": masked_job_id,
                "backend": self._store.backend_name,
                "payload_size_bytes": self.estimate_payload_size_bytes(payload),
                "load_ms": round(elapsed_ms, 2),
            },
        )
        self._emit_load_metrics(
            self.STATUS_OK,
            time.perf_counter() - operation_started,
            payload_size_bytes=self.estimate_payload_size_bytes(payload),
        )

        return payload, self.STATUS_OK

    def close(self) -> None:
        """Close underlying resume backend."""
        self._store.close()
