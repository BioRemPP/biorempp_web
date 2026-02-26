"""
Diskcache adapter for resume payload persistence.
"""

from pathlib import Path
from typing import Optional

import diskcache

from .resume_store import ResumeStore
from src.shared.logging import build_log_ref, get_logger

logger = get_logger(__name__)


class DiskcacheResumeStore(ResumeStore):
    """Diskcache implementation of ResumeStore."""

    def __init__(self, cache_dir: Path, cache_size_mb: int) -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._cache = diskcache.Cache(
            str(self._cache_dir),
            size_limit=max(int(cache_size_mb), 32) * 1024 * 1024,
        )

    @property
    def backend_name(self) -> str:
        return "diskcache"

    def set(self, key: str, value: dict, ttl_seconds: int) -> bool:
        cache_ref = build_log_ref(key, namespace="cache")
        try:
            self._cache.set(key, value, expire=max(int(ttl_seconds), 1))
            return True
        except Exception:
            logger.exception(
                "Diskcache resume set failed",
                extra={"cache_ref": cache_ref},
            )
            return False

    def get(self, key: str) -> Optional[dict]:
        cache_ref = build_log_ref(key, namespace="cache")
        try:
            value = self._cache.get(key, default=None)
        except Exception:
            logger.exception(
                "Diskcache resume get failed",
                extra={"cache_ref": cache_ref},
            )
            return None
        return value if isinstance(value, dict) else None

    def close(self) -> None:
        self._cache.close()
