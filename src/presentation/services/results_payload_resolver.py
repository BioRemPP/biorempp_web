"""
Results payload resolver for `/results` callbacks.

This module supports two payload transport modes:
- client mode: full payload is kept in `merged-result-store`
- server mode: only a lightweight payload reference is stored client-side

In server mode, callbacks resolve the reference back to the full payload
through `job_resume_service`, using `job_id` + `owner_token`.
"""

from __future__ import annotations

import hashlib
import threading
import time
from collections import OrderedDict
from typing import Any

from config.settings import get_settings
from src.presentation.services import job_resume_service
from src.shared.logging import build_log_ref, get_logger

logger = get_logger(__name__)
settings = get_settings()

_PAYLOAD_REF_KEY = "_payload_ref"
_PAYLOAD_REF_VERSION = 1
_FULL_PAYLOAD_KEYS = (
    "biorempp_df",
    "hadeg_df",
    "toxcsm_df",
    "kegg_df",
)


class _HydrationCache:
    """Small in-memory cache for hydrated payloads inside one worker process."""

    def __init__(self, max_entries: int, ttl_seconds: int) -> None:
        self._max_entries = max(int(max_entries), 1)
        self._ttl_seconds = max(int(ttl_seconds), 1)
        self._store: OrderedDict[str, tuple[float, dict[str, Any]]] = OrderedDict()
        self._lock = threading.Lock()

    def _now(self) -> float:
        return time.time()

    def _prune_expired(self, now: float) -> None:
        expired_keys = [
            key for key, (expires_at, _) in self._store.items() if expires_at <= now
        ]
        for key in expired_keys:
            self._store.pop(key, None)

    def get(self, key: str) -> dict[str, Any] | None:
        with self._lock:
            now = self._now()
            self._prune_expired(now)
            value = self._store.get(key)
            if value is None:
                return None
            expires_at, payload = value
            if expires_at <= now:
                self._store.pop(key, None)
                return None
            self._store.move_to_end(key)
            return payload

    def set(self, key: str, payload: dict[str, Any]) -> None:
        with self._lock:
            now = self._now()
            self._prune_expired(now)
            self._store[key] = (now + self._ttl_seconds, payload)
            self._store.move_to_end(key)
            while len(self._store) > self._max_entries:
                self._store.popitem(last=False)


_hydration_cache = _HydrationCache(
    max_entries=settings.RESULTS_HYDRATION_CACHE_SIZE,
    ttl_seconds=settings.RESULTS_HYDRATION_CACHE_TTL_SECONDS,
)


def _build_cache_key(job_id: str, owner_token: str) -> str:
    digest = hashlib.sha256(f"{job_id}|{owner_token}".encode("utf-8")).hexdigest()
    return digest


def _is_full_payload(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False
    return all(key in payload for key in _FULL_PAYLOAD_KEYS)


def _hydration_retry_attempts() -> int:
    raw_value = getattr(settings, "RESULTS_HYDRATION_RETRY_ATTEMPTS", 1)
    try:
        return max(int(raw_value), 1)
    except (TypeError, ValueError):
        return 1


def _hydration_retry_delay_seconds() -> float:
    raw_value = getattr(settings, "RESULTS_HYDRATION_RETRY_DELAY_MS", 0)
    try:
        delay_ms = max(int(raw_value), 0)
    except (TypeError, ValueError):
        delay_ms = 0
    return float(delay_ms) / 1000.0


def _extract_payload_ref_identity(payload_ref: dict[str, Any]) -> tuple[str, str] | None:
    version = payload_ref.get("version")
    job_id = payload_ref.get("job_id")
    owner_token = payload_ref.get("owner_token")
    if version != _PAYLOAD_REF_VERSION:
        logger.warning(
            "Unsupported results payload ref version",
            extra={"version": version},
        )
        return None
    if not isinstance(job_id, str) or not job_id.strip():
        return None
    if not isinstance(owner_token, str) or not owner_token.strip():
        return None
    return job_id.strip().upper(), owner_token.strip()


def _load_payload_with_retry(
    job_id: str,
    owner_token: str,
) -> tuple[dict[str, Any] | None, str | None, int]:
    max_attempts = _hydration_retry_attempts()
    delay_seconds = _hydration_retry_delay_seconds()
    status_not_found = getattr(job_resume_service, "STATUS_NOT_FOUND", "not_found")

    attempts = 0
    last_status: str | None = None
    for attempt in range(1, max_attempts + 1):
        attempts = attempt
        payload, status = job_resume_service.load_job_payload(job_id, owner_token)
        last_status = status
        if status == job_resume_service.STATUS_OK and isinstance(payload, dict):
            return payload, status, attempts

        if status != status_not_found:
            break

        if attempt < max_attempts and delay_seconds > 0:
            time.sleep(delay_seconds)

    return None, last_status, attempts


def prime_results_payload_cache(payload: Any, owner_token: str) -> bool:
    """
    Prime hydration cache with a just-produced full payload.

    This reduces first-render misses in server payload mode when the
    resume backend write is still converging.
    """
    if not _is_full_payload(payload):
        return False

    metadata_raw = payload.get("metadata") if isinstance(payload, dict) else None
    metadata = metadata_raw if isinstance(metadata_raw, dict) else {}
    job_id = metadata.get("job_id")
    token = (owner_token or "").strip()
    if not isinstance(job_id, str) or not job_id.strip() or not token:
        return False

    normalized_job_id = job_id.strip().upper()
    cache_key = _build_cache_key(normalized_job_id, token)
    _hydration_cache.set(cache_key, payload)
    return True


def build_results_payload_ref(payload: dict[str, Any], owner_token: str) -> dict[str, Any]:
    """
    Build lightweight payload reference for `merged-result-store`.

    Falls back to full payload when reference cannot be safely built.
    """
    if not isinstance(payload, dict):
        return {}

    metadata_raw = payload.get("metadata")
    metadata = metadata_raw if isinstance(metadata_raw, dict) else {}
    job_id = metadata.get("job_id")
    token = (owner_token or "").strip()

    if not isinstance(job_id, str) or not job_id.strip():
        logger.warning(
            "Results payload ref fallback to full payload: missing job_id in metadata"
        )
        return payload
    if not token:
        logger.warning(
            "Results payload ref fallback to full payload: missing owner token",
            extra={"job_ref": build_log_ref(job_id, namespace="job")},
        )
        return payload

    return {
        _PAYLOAD_REF_KEY: {
            "version": _PAYLOAD_REF_VERSION,
            "job_id": job_id.strip().upper(),
            "owner_token": token,
        },
        "metadata": metadata,
    }


def resolve_results_payload(store_data: Any) -> dict[str, Any]:
    """
    Resolve full merged payload from store data.

    Accepted shapes:
    - full payload dict (legacy/client mode)
    - reference payload dict (server mode)
    """
    if _is_full_payload(store_data):
        return store_data

    if not isinstance(store_data, dict):
        return {}

    payload_ref = store_data.get(_PAYLOAD_REF_KEY)
    if not isinstance(payload_ref, dict):
        return store_data

    identity = _extract_payload_ref_identity(payload_ref)
    if identity is None:
        return {}
    normalized_job_id, normalized_owner_token = identity

    cache_key = _build_cache_key(normalized_job_id, normalized_owner_token)
    cached_payload = _hydration_cache.get(cache_key)
    if isinstance(cached_payload, dict):
        return cached_payload

    payload, status, attempts = _load_payload_with_retry(
        normalized_job_id,
        normalized_owner_token,
    )
    if isinstance(payload, dict):
        _hydration_cache.set(cache_key, payload)
        return payload

    logger.warning(
        "Failed to hydrate results payload from resume backend",
        extra={
            "job_ref": build_log_ref(normalized_job_id, namespace="job"),
            "status": status,
            "attempts": attempts,
        },
    )
    return {}
