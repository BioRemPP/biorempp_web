"""Unit tests for resume persistence timeout guard in processing callbacks."""

import time

from src.presentation.callbacks import real_processing_callbacks


class _FastResumeService:
    @staticmethod
    def save_job_payload(job_id, payload, owner_token, ttl_seconds):
        return True


class _SlowResumeService:
    @staticmethod
    def save_job_payload(job_id, payload, owner_token, ttl_seconds):
        time.sleep(0.2)
        return True


class _ErrorResumeService:
    @staticmethod
    def save_job_payload(job_id, payload, owner_token, ttl_seconds):
        raise RuntimeError("backend unavailable")


def test_persist_resume_payload_with_timeout_success(monkeypatch):
    """Fast persistence should return success."""
    monkeypatch.setattr(
        real_processing_callbacks,
        "job_resume_service",
        _FastResumeService(),
    )

    saved = real_processing_callbacks._persist_resume_payload_with_timeout(
        job_id="BRP-20260225-123456-ABCDEF",
        payload={"metadata": {}},
        owner_token="token-a",
        ttl_seconds=60,
        timeout_seconds=0.1,
    )

    assert saved is True


def test_persist_resume_payload_with_timeout_returns_false_on_timeout(monkeypatch):
    """Slow persistence should not block callback completion."""
    monkeypatch.setattr(
        real_processing_callbacks,
        "job_resume_service",
        _SlowResumeService(),
    )

    start = time.perf_counter()
    saved = real_processing_callbacks._persist_resume_payload_with_timeout(
        job_id="BRP-20260225-123457-ABCDEF",
        payload={"metadata": {}},
        owner_token="token-b",
        ttl_seconds=60,
        timeout_seconds=0.05,
    )
    elapsed = time.perf_counter() - start

    assert saved is False
    assert elapsed < 0.15


def test_persist_resume_payload_with_timeout_returns_false_on_error(monkeypatch):
    """Persistence exceptions should be converted to non-blocking failures."""
    monkeypatch.setattr(
        real_processing_callbacks,
        "job_resume_service",
        _ErrorResumeService(),
    )

    saved = real_processing_callbacks._persist_resume_payload_with_timeout(
        job_id="BRP-20260225-123458-ABCDEF",
        payload={"metadata": {}},
        owner_token="token-c",
        ttl_seconds=60,
        timeout_seconds=0.1,
    )

    assert saved is False
