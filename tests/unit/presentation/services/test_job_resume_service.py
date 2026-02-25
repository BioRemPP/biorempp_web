"""Unit tests for resume payload persistence by `job_id`."""

import time

import pytest

from src.presentation.services.job_resume_service import JobResumeService


@pytest.fixture
def resume_service(tmp_path):
    """Create isolated service instance backed by temporary diskcache."""
    service = JobResumeService(
        cache_dir=tmp_path / "job_resume_cache",
        ttl_seconds=30,
        cache_size_mb=64,
    )
    yield service
    service.close()


def test_save_and_load_job_payload_success(resume_service):
    """Service should persist and retrieve payload for same owner token."""
    job_id = "BRP-20260225-120000-ABC123"
    owner_token = "browser-token-1"
    payload = {"metadata": {"job_id": job_id}, "biorempp_df": []}

    saved = resume_service.save_job_payload(job_id, payload, owner_token, ttl_seconds=30)
    loaded_payload, status = resume_service.load_job_payload(job_id, owner_token)

    assert saved is True
    assert status == resume_service.STATUS_OK
    assert loaded_payload == payload


def test_save_rejects_invalid_job_id(resume_service):
    """Invalid job format should be rejected on save and load validation."""
    payload = {"metadata": {"job_id": "invalid"}}
    saved = resume_service.save_job_payload("not-a-job-id", payload, "token", ttl_seconds=30)
    loaded_payload, status = resume_service.load_job_payload("not-a-job-id", "token")

    assert saved is False
    assert loaded_payload is None
    assert status == resume_service.STATUS_INVALID_JOB_ID


def test_load_returns_not_found_after_ttl_expiration(resume_service):
    """Expired payload should not be retrievable."""
    job_id = "BRP-20260225-120001-ABC124"
    owner_token = "browser-token-2"
    payload = {"metadata": {"job_id": job_id}}

    assert resume_service.save_job_payload(job_id, payload, owner_token, ttl_seconds=1)
    time.sleep(1.2)

    loaded_payload, status = resume_service.load_job_payload(job_id, owner_token)
    assert loaded_payload is None
    assert status == resume_service.STATUS_NOT_FOUND


def test_load_returns_token_mismatch_for_wrong_owner(resume_service):
    """Payload must be blocked when owner token does not match."""
    job_id = "BRP-20260225-120002-ABC125"
    payload = {"metadata": {"job_id": job_id}}

    assert resume_service.save_job_payload(job_id, payload, "owner-a", ttl_seconds=30)
    loaded_payload, status = resume_service.load_job_payload(job_id, "owner-b")

    assert loaded_payload is None
    assert status == resume_service.STATUS_TOKEN_MISMATCH


def test_load_returns_not_found_when_payload_does_not_exist(resume_service):
    """Unknown job_id should return not_found for valid format."""
    loaded_payload, status = resume_service.load_job_payload(
        "BRP-20260225-120003-ABC126",
        "owner-c",
    )

    assert loaded_payload is None
    assert status == resume_service.STATUS_NOT_FOUND


def test_load_handles_incompatible_payload_version(resume_service):
    """Incompatible payload_version should fail gracefully."""
    job_id = "BRP-20260225-120004-ABC127"
    owner_token = "owner-d"

    resume_service._cache.set(
        resume_service._build_cache_key(job_id),
        {
            "job_id": job_id,
            "owner_token": owner_token,
            "created_at": "2026-02-25T12:00:04+00:00",
            "payload_version": 999,
            "merged_result_payload": {"metadata": {"job_id": job_id}},
        },
        expire=30,
    )

    loaded_payload, status = resume_service.load_job_payload(job_id, owner_token)

    assert loaded_payload is None
    assert status == resume_service.STATUS_INCOMPATIBLE_VERSION


def test_save_rejects_payload_larger_than_configured_limit(tmp_path):
    """Payloads above configured max size should not be persisted."""
    service = JobResumeService(
        cache_dir=tmp_path / "limited_resume_cache",
        ttl_seconds=30,
        cache_size_mb=64,
        max_payload_mb=1,
    )
    try:
        job_id = "BRP-20260225-120005-ABC128"
        owner_token = "owner-e"
        payload = {"metadata": {"job_id": job_id}, "blob": "x" * (2 * 1024 * 1024)}

        saved = service.save_job_payload(job_id, payload, owner_token, ttl_seconds=30)
        loaded_payload, status = service.load_job_payload(job_id, owner_token)

        assert saved is False
        assert loaded_payload is None
        assert status == service.STATUS_NOT_FOUND
    finally:
        service.close()
