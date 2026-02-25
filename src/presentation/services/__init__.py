"""
BioRemPP Web - Presentation Services
====================================

Service layer for presentation logic.
"""

from config.settings import get_settings
from .data_processing_service import DataProcessingService
from .job_resume_service import JobResumeService
from .resume_store_diskcache import DiskcacheResumeStore
from .resume_store_redis import RedisResumeStore
from src.shared.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


def _build_diskcache_store() -> DiskcacheResumeStore:
    return DiskcacheResumeStore(
        cache_dir=settings.CACHE_DIR / "job_resume",
        cache_size_mb=settings.RESUME_CACHE_SIZE_MB,
    )


def _build_redis_store() -> RedisResumeStore:
    return RedisResumeStore(
        host=settings.RESUME_REDIS_HOST,
        port=settings.RESUME_REDIS_PORT,
        db=settings.RESUME_REDIS_DB,
        password=settings.RESUME_REDIS_PASSWORD or None,
        key_prefix=settings.RESUME_REDIS_KEY_PREFIX,
        socket_timeout_seconds=float(settings.RESUME_REDIS_SOCKET_TIMEOUT_SECONDS),
        compression_level=settings.RESUME_REDIS_COMPRESSION_LEVEL,
    )


def _build_resume_store():
    backend = settings.RESUME_BACKEND
    if backend == "redis":
        store = _build_redis_store()
        logger.info("Resume backend selected", extra={"backend": "redis"})
        return store
    if backend != "diskcache":
        logger.warning(
            "Unknown RESUME_BACKEND. Falling back to diskcache.",
            extra={"backend_value": backend},
        )
    store = _build_diskcache_store()
    logger.info("Resume backend selected", extra={"backend": "diskcache"})
    return store


job_resume_service = JobResumeService(
    store=_build_resume_store(),
    ttl_seconds=settings.RESUME_TTL_SECONDS,
    cache_size_mb=settings.RESUME_CACHE_SIZE_MB,
    max_payload_mb=settings.RESUME_MAX_PAYLOAD_MB,
    alert_window_seconds=settings.RESUME_ALERT_WINDOW_SECONDS,
    alert_not_found_threshold=settings.RESUME_ALERT_NOT_FOUND_THRESHOLD,
    alert_token_mismatch_threshold=settings.RESUME_ALERT_TOKEN_MISMATCH_THRESHOLD,
    alert_save_failed_threshold=settings.RESUME_ALERT_SAVE_FAILED_THRESHOLD,
)

__all__ = [
    "DataProcessingService",
    "JobResumeService",
    "DiskcacheResumeStore",
    "RedisResumeStore",
    "job_resume_service",
]
