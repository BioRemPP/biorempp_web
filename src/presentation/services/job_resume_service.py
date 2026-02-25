"""
Job Resume Service - temporary file-backed persistence for processed results.

Stores serialized `merged-result-store` payloads keyed by `job_id` so users
can resume results in the same browser context after closing the tab/session.
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import diskcache

from src.shared.logging import get_logger

logger = get_logger(__name__)


class JobResumeService:
    """Service for saving and loading processed payloads by `job_id`."""

    CACHE_KEY_PREFIX = "job_resume:"
    DEFAULT_TTL_SECONDS = 14400  # 4 hours
    DEFAULT_CACHE_SIZE_MB = 512
    CURRENT_PAYLOAD_VERSION = 1
    SUPPORTED_PAYLOAD_VERSIONS = {1}
    JOB_ID_PATTERN = re.compile(r"^BRP-\d{8}-\d{6}-[A-F0-9]{6}$")

    STATUS_OK = "ok"
    STATUS_INVALID_JOB_ID = "invalid_job_id"
    STATUS_NOT_FOUND = "not_found"
    STATUS_TOKEN_MISMATCH = "token_mismatch"
    STATUS_TOKEN_MISSING = "token_missing"
    STATUS_INCOMPATIBLE_VERSION = "incompatible_version"

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl_seconds: Optional[int] = None,
        cache_size_mb: Optional[int] = None,
    ) -> None:
        """
        Initialize resume cache backend.

        Parameters
        ----------
        cache_dir : Optional[Path]
            Cache directory path. Defaults to project `/.cache/job_resume`.
        ttl_seconds : Optional[int]
            Default TTL in seconds.
        cache_size_mb : Optional[int]
            Maximum cache size in MB.
        """
        project_root = Path(__file__).resolve().parents[3]
        self._cache_dir = (
            Path(cache_dir)
            if cache_dir is not None
            else project_root / ".cache" / "job_resume"
        )
        self._cache_dir.mkdir(parents=True, exist_ok=True)

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

        self._cache = diskcache.Cache(
            str(self._cache_dir),
            size_limit=self._cache_size_mb * 1024 * 1024,
        )

        logger.info(
            "JobResumeService initialized",
            extra={
                "cache_dir": str(self._cache_dir),
                "ttl_seconds": self._ttl_seconds,
                "cache_size_mb": self._cache_size_mb,
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

    def get_resume_ttl_seconds(self) -> int:
        """Return configured default TTL used for resume payloads."""
        return self._ttl_seconds

    @classmethod
    def validate_job_id(cls, job_id: str) -> bool:
        """
        Validate `job_id` format.

        Expected format: BRP-YYYYMMDD-HHMMSS-XXXXXX (hex suffix).
        """
        if not isinstance(job_id, str):
            return False
        return bool(cls.JOB_ID_PATTERN.match(job_id.strip().upper()))

    def _build_cache_key(self, job_id: str) -> str:
        """Build cache key from job identifier."""
        return f"{self.CACHE_KEY_PREFIX}{job_id}"

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
        """
        normalized_job_id = (job_id or "").strip().upper()
        if not self.validate_job_id(normalized_job_id):
            logger.warning("Refusing to save resume payload: invalid job_id format")
            return False
        if not isinstance(payload, dict):
            logger.warning(
                "Refusing to save resume payload: payload must be dict",
                extra={"job_id": normalized_job_id},
            )
            return False
        if not isinstance(owner_token, str) or not owner_token.strip():
            logger.warning(
                "Refusing to save resume payload: missing owner_token",
                extra={"job_id": normalized_job_id},
            )
            return False

        if ttl_seconds is None:
            ttl = self._ttl_seconds
        else:
            try:
                ttl = max(int(ttl_seconds), 1)
            except (TypeError, ValueError):
                ttl = self._ttl_seconds

        cache_key = self._build_cache_key(normalized_job_id)
        cache_value = {
            "job_id": normalized_job_id,
            "owner_token": owner_token.strip(),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "payload_version": self.CURRENT_PAYLOAD_VERSION,
            "merged_result_payload": payload,
        }

        try:
            self._cache.set(cache_key, cache_value, expire=ttl)
            logger.info(
                "Resume payload saved",
                extra={
                    "job_id": normalized_job_id,
                    "ttl_seconds": ttl,
                    "payload_size_bytes": self._estimate_payload_size(payload),
                },
            )
            return True
        except Exception:
            logger.exception(
                "Failed to persist resume payload", extra={"job_id": normalized_job_id}
            )
            return False

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
        if not self.validate_job_id(normalized_job_id):
            return None, self.STATUS_INVALID_JOB_ID

        if not isinstance(owner_token, str) or not owner_token.strip():
            return None, self.STATUS_TOKEN_MISSING

        cache_key = self._build_cache_key(normalized_job_id)
        cached = self._cache.get(cache_key, default=None)
        if not isinstance(cached, dict):
            return None, self.STATUS_NOT_FOUND

        cached_owner_token = cached.get("owner_token")
        if cached_owner_token != owner_token.strip():
            return None, self.STATUS_TOKEN_MISMATCH

        raw_payload_version = cached.get("payload_version", self.CURRENT_PAYLOAD_VERSION)
        try:
            payload_version = int(raw_payload_version)
        except (TypeError, ValueError):
            return None, self.STATUS_INCOMPATIBLE_VERSION
        if payload_version not in self.SUPPORTED_PAYLOAD_VERSIONS:
            return None, self.STATUS_INCOMPATIBLE_VERSION

        payload = cached.get("merged_result_payload")
        if not isinstance(payload, dict):
            return None, self.STATUS_NOT_FOUND

        return payload, self.STATUS_OK

    def close(self) -> None:
        """Close underlying diskcache backend."""
        self._cache.close()


job_resume_service = JobResumeService()
