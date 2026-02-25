"""Unit tests for Redis-based resume persistence backend."""

import json
import time
from threading import Lock
from typing import Optional

from src.presentation.services.job_resume_service import JobResumeService
from src.presentation.services.resume_store_redis import RedisResumeStore


class _FakeRedisBackend:
    """Shared in-memory backend to emulate Redis across clients/workers."""

    def __init__(self) -> None:
        self._lock = Lock()
        self._data: dict[str, tuple[bytes, Optional[float]]] = {}

    def set(self, key: str, value: bytes, ex: Optional[int] = None) -> bool:
        expire_at = None if ex is None else (time.time() + max(int(ex), 1))
        with self._lock:
            self._data[key] = (value, expire_at)
        return True

    def get(self, key: str) -> Optional[bytes]:
        with self._lock:
            raw = self._data.get(key)
            if raw is None:
                return None
            value, expire_at = raw
            if expire_at is not None and time.time() >= expire_at:
                del self._data[key]
                return None
            return value

    def raw_value(self, key: str) -> Optional[bytes]:
        with self._lock:
            raw = self._data.get(key)
            return None if raw is None else raw[0]


class _FakeRedisClient:
    """Minimal Redis client contract used by RedisResumeStore."""

    def __init__(self, backend: _FakeRedisBackend) -> None:
        self._backend = backend

    def set(self, name: str, value: bytes, ex: Optional[int] = None) -> bool:
        return self._backend.set(name, value, ex=ex)

    def get(self, name: str) -> Optional[bytes]:
        return self._backend.get(name)

    @staticmethod
    def ping() -> bool:
        return True

    @staticmethod
    def close() -> None:
        return None


def _build_service(backend: _FakeRedisBackend, key_prefix: str) -> JobResumeService:
    store = RedisResumeStore(
        client=_FakeRedisClient(backend),
        key_prefix=key_prefix,
        compression_level=6,
    )
    return JobResumeService(
        store=store,
        ttl_seconds=30,
        max_payload_mb=8,
    )


def test_redis_resume_persists_across_service_instances():
    """
    Payload saved by one service instance must be loadable by another.

    This emulates cross-worker/process retrieval against shared Redis state.
    """
    backend = _FakeRedisBackend()
    producer_service = _build_service(backend, key_prefix="test:resume:")
    consumer_service = _build_service(backend, key_prefix="test:resume:")

    job_id = "BRP-20260225-140000-ABC201"
    owner_token = "worker-owner"
    payload = {"metadata": {"job_id": job_id}, "biorempp_df": [{"KO": "K00001"}]}

    assert producer_service.save_job_payload(job_id, payload, owner_token, ttl_seconds=30)

    loaded_payload, status = consumer_service.load_job_payload(job_id, owner_token)

    assert status == consumer_service.STATUS_OK
    assert loaded_payload == payload

    producer_service.close()
    consumer_service.close()


def test_redis_resume_ttl_expiration_is_enforced():
    """Redis adapter must respect key TTL expiration."""
    backend = _FakeRedisBackend()
    service = _build_service(backend, key_prefix="test:resume:")

    job_id = "BRP-20260225-140001-ABC202"
    owner_token = "owner-ttl"
    payload = {"metadata": {"job_id": job_id}}

    assert service.save_job_payload(job_id, payload, owner_token, ttl_seconds=1)
    time.sleep(1.2)

    loaded_payload, status = service.load_job_payload(job_id, owner_token)

    assert loaded_payload is None
    assert status == service.STATUS_NOT_FOUND

    service.close()


def test_redis_store_uses_prefix_and_compact_compressed_serialization():
    """Redis adapter should namespace keys and compress serialized values."""
    backend = _FakeRedisBackend()
    store = RedisResumeStore(
        client=_FakeRedisClient(backend),
        key_prefix="biorempp:resume:test:",
        compression_level=6,
    )

    logical_key = "job_resume:BRP-20260225-140002-ABC203"
    value = {"payload": "A" * 12000, "metadata": {"k": "v"}}

    assert store.set(logical_key, value, ttl_seconds=30)
    loaded = store.get(logical_key)

    full_key = f"biorempp:resume:test:{logical_key}"
    stored_blob = backend.raw_value(full_key)
    raw_json_size = len(
        json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    )

    assert loaded == value
    assert stored_blob is not None
    assert len(stored_blob) < raw_json_size

    store.close()

