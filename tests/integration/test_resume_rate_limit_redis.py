"""Integration tests for Redis-backed resume rate limiting."""

from __future__ import annotations

import os
import threading
import time
from uuid import uuid4

import pytest

from src.presentation.callbacks.job_resume_callbacks import RedisResumeRateLimiter

try:
    import redis
except ImportError:  # pragma: no cover - optional dependency in local env
    redis = None


pytestmark = [pytest.mark.integration]


def _build_redis_client():
    if redis is None:
        pytest.skip("redis package not available")

    host = os.getenv("BIOREMPP_RESUME_REDIS_HOST", "127.0.0.1")
    port = int(os.getenv("BIOREMPP_RESUME_REDIS_PORT", "6379"))
    db = int(os.getenv("BIOREMPP_RESUME_REDIS_DB", "0"))
    password = os.getenv("BIOREMPP_RESUME_REDIS_PASSWORD", "") or None
    client = redis.Redis(
        host=host,
        port=port,
        db=db,
        password=password,
        decode_responses=False,
        socket_timeout=2.0,
        socket_connect_timeout=2.0,
    )
    try:
        client.ping()
    except Exception as exc:  # pragma: no cover - runtime environment dependent
        pytest.skip(f"Redis is not reachable for integration test: {exc}")
    return client


def _cleanup_prefix(client, prefix: str) -> None:
    cursor = 0
    pattern = f"{prefix}*"
    while True:
        cursor, keys = client.scan(cursor=cursor, match=pattern, count=200)
        if keys:
            client.delete(*keys)
        if cursor == 0:
            break


def _make_prefix() -> str:
    return f"biorempp:resume:ratelimit:inttest:{uuid4().hex[:10]}:"


def test_redis_rate_limiter_ttl_and_backoff_are_enforced():
    """Redis Lua limiter should block after threshold and release after backoff."""
    client = _build_redis_client()
    prefix = _make_prefix()
    limiter = RedisResumeRateLimiter(
        host="unused",
        port=6379,
        db=0,
        password="",
        key_prefix=prefix,
        attempts=2,
        window_seconds=30,
        backoff_base_seconds=1,
        backoff_max_seconds=2,
        client=client,
    )

    identity_hash = "identity-rate-limit-ttl"
    try:
        allowed_1, retry_1 = limiter.evaluate(identity_hash)
        allowed_2, retry_2 = limiter.evaluate(identity_hash)
        allowed_3, retry_3 = limiter.evaluate(identity_hash)

        assert allowed_1 is True and retry_1 == 0
        assert allowed_2 is True and retry_2 == 0
        assert allowed_3 is False and retry_3 >= 1

        time.sleep(1.1)
        allowed_after_backoff, retry_after_backoff = limiter.evaluate(identity_hash)
        assert allowed_after_backoff is True
        assert retry_after_backoff == 0
    finally:
        limiter.close()
        _cleanup_prefix(client, prefix)
        close_fn = getattr(client, "close", None)
        if callable(close_fn):
            close_fn()


def test_redis_rate_limiter_handles_concurrent_attempts_across_instances():
    """Concurrent attempts across limiter instances should trigger blocking."""
    client_a = _build_redis_client()
    client_b = _build_redis_client()
    prefix = _make_prefix()
    limiter_a = RedisResumeRateLimiter(
        host="unused",
        port=6379,
        db=0,
        password="",
        key_prefix=prefix,
        attempts=3,
        window_seconds=30,
        backoff_base_seconds=1,
        backoff_max_seconds=5,
        client=client_a,
    )
    limiter_b = RedisResumeRateLimiter(
        host="unused",
        port=6379,
        db=0,
        password="",
        key_prefix=prefix,
        attempts=3,
        window_seconds=30,
        backoff_base_seconds=1,
        backoff_max_seconds=5,
        client=client_b,
    )

    identity_hash = "identity-rate-limit-concurrency"
    barrier = threading.Barrier(6)
    results: list[tuple[bool, int]] = []
    lock = threading.Lock()

    def _attempt(limiter: RedisResumeRateLimiter) -> None:
        barrier.wait(timeout=5)
        outcome = limiter.evaluate(identity_hash)
        with lock:
            results.append(outcome)

    threads = [
        threading.Thread(target=_attempt, args=(limiter_a,)),
        threading.Thread(target=_attempt, args=(limiter_b,)),
        threading.Thread(target=_attempt, args=(limiter_a,)),
        threading.Thread(target=_attempt, args=(limiter_b,)),
        threading.Thread(target=_attempt, args=(limiter_a,)),
        threading.Thread(target=_attempt, args=(limiter_b,)),
    ]

    try:
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=5)

        assert len(results) == 6
        blocked = [item for item in results if item[0] is False]
        assert len(blocked) >= 1
    finally:
        limiter_a.close()
        limiter_b.close()
        _cleanup_prefix(client_a, prefix)
        close_a = getattr(client_a, "close", None)
        close_b = getattr(client_b, "close", None)
        if callable(close_a):
            close_a()
        if callable(close_b):
            close_b()

