"""
BioRemPP Web - Presentation Services
====================================

Service layer for presentation logic.
"""

import os
from pathlib import Path

from .data_processing_service import DataProcessingService
from .job_resume_service import JobResumeService
from .resume_store_diskcache import DiskcacheResumeStore
from .resume_store_redis import RedisResumeStore
from src.shared.logging import get_logger

logger = get_logger(__name__)


def _read_env_int(name: str, default: int, minimum: int = 1) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return max(default, minimum)
    try:
        return max(int(raw_value), minimum)
    except ValueError:
        return max(default, minimum)


def _resolve_base_cache_dir() -> Path:
    project_root = Path(__file__).resolve().parents[3]
    raw_value = os.getenv("BIOREMPP_CACHE_DIR")
    if not raw_value:
        return project_root / "cache"
    candidate = Path(raw_value)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    return candidate


def _build_diskcache_store() -> DiskcacheResumeStore:
    cache_size_mb = _read_env_int(
        "BIOREMPP_RESUME_CACHE_SIZE_MB",
        JobResumeService.DEFAULT_CACHE_SIZE_MB,
        minimum=32,
    )
    cache_dir = _resolve_base_cache_dir() / "job_resume"
    return DiskcacheResumeStore(cache_dir=cache_dir, cache_size_mb=cache_size_mb)


def _build_resume_store():
    backend = os.getenv("BIOREMPP_RESUME_BACKEND", "diskcache").strip().lower()
    if backend == "redis":
        store = RedisResumeStore.from_env()
        logger.info("Resume backend selected", extra={"backend": "redis"})
        return store
    if backend and backend != "diskcache":
        logger.warning(
            "Unknown BIOREMPP_RESUME_BACKEND. Falling back to diskcache.",
            extra={"backend_value": backend},
        )
    store = _build_diskcache_store()
    logger.info("Resume backend selected", extra={"backend": "diskcache"})
    return store


job_resume_service = JobResumeService(store=_build_resume_store())

__all__ = [
    "DataProcessingService",
    "JobResumeService",
    "DiskcacheResumeStore",
    "RedisResumeStore",
    "job_resume_service",
]
