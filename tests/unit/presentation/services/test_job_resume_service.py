"""Unit tests for resume payload persistence by `job_id`."""

import time

import pytest

from src.presentation.services.job_resume_service import JobResumeService
from src.shared.metrics import (
    RESUME_LOAD_ATTEMPTS_TOTAL,
    RESUME_OPERATION_DURATION_SECONDS,
    RESUME_SAVE_TOTAL,
)


def _counter_value(counter, **labels) -> float:
    """Read Prometheus counter value for labels."""
    return float(counter.labels(**labels)._value.get())


def _histogram_count(histogram, **labels) -> float:
    """Read Prometheus histogram observation count for labels."""
    target_name = f"{histogram._name}_count"
    for metric_family in histogram.collect():
        for sample in metric_family.samples:
            if sample.name != target_name:
                continue
            if all(sample.labels.get(k) == v for k, v in labels.items()):
                return float(sample.value)
    return 0.0


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

    before_save_ok = _counter_value(RESUME_SAVE_TOTAL, outcome="ok")
    before_load_ok = _counter_value(RESUME_LOAD_ATTEMPTS_TOTAL, outcome="ok")
    before_save_latency = _histogram_count(
        RESUME_OPERATION_DURATION_SECONDS,
        backend=resume_service._store.backend_name,
        operation="save",
        status="ok",
    )
    before_load_latency = _histogram_count(
        RESUME_OPERATION_DURATION_SECONDS,
        backend=resume_service._store.backend_name,
        operation="load",
        status="ok",
    )

    saved = resume_service.save_job_payload(
        job_id, payload, owner_token, ttl_seconds=30
    )
    loaded_payload, status = resume_service.load_job_payload(job_id, owner_token)

    assert saved is True
    assert status == resume_service.STATUS_OK
    assert loaded_payload == payload
    assert _counter_value(RESUME_SAVE_TOTAL, outcome="ok") >= (before_save_ok + 1.0)
    assert _counter_value(RESUME_LOAD_ATTEMPTS_TOTAL, outcome="ok") >= (
        before_load_ok + 1.0
    )
    assert _histogram_count(
        RESUME_OPERATION_DURATION_SECONDS,
        backend=resume_service._store.backend_name,
        operation="save",
        status="ok",
    ) >= (before_save_latency + 1.0)
    assert _histogram_count(
        RESUME_OPERATION_DURATION_SECONDS,
        backend=resume_service._store.backend_name,
        operation="load",
        status="ok",
    ) >= (before_load_latency + 1.0)


def test_save_job_payload_emits_store_callback_and_timing_log(resume_service, caplog):
    """Save should emit store callback and structured timing event."""
    job_id = "BRP-20260225-120000-ABC124"
    owner_token = "browser-token-cb"
    payload = {"metadata": {"job_id": job_id}, "biorempp_df": []}
    callback_data = {}

    def _on_store(saved: bool, store_set_ms: float) -> None:
        callback_data["saved"] = saved
        callback_data["store_set_ms"] = store_set_ms

    with caplog.at_level("INFO"):
        saved = resume_service.save_job_payload(
            job_id,
            payload,
            owner_token,
            ttl_seconds=30,
            on_store_set_complete=_on_store,
        )

    assert saved is True
    assert callback_data["saved"] is True
    assert callback_data["store_set_ms"] >= 0.0
    timing_records = [
        rec for rec in caplog.records if rec.message == "Resume payload persistence timing"
    ]
    assert timing_records
    timing = timing_records[-1]
    assert getattr(timing, "backend", None) == resume_service._store.backend_name
    assert getattr(timing, "job_ref", "").startswith("job_")
    assert getattr(timing, "payload_size_bytes", None) is not None


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
    before_mismatch = _counter_value(
        RESUME_LOAD_ATTEMPTS_TOTAL, outcome="token_mismatch"
    )
    loaded_payload, status = resume_service.load_job_payload(job_id, "owner-b")

    assert loaded_payload is None
    assert status == resume_service.STATUS_TOKEN_MISMATCH
    assert _counter_value(
        RESUME_LOAD_ATTEMPTS_TOTAL, outcome="token_mismatch"
    ) >= (before_mismatch + 1.0)


def test_load_returns_not_found_when_payload_does_not_exist(resume_service):
    """Unknown job_id should return not_found for valid format."""
    before_not_found = _counter_value(RESUME_LOAD_ATTEMPTS_TOTAL, outcome="not_found")
    loaded_payload, status = resume_service.load_job_payload(
        "BRP-20260225-120003-ABC126",
        "owner-c",
    )

    assert loaded_payload is None
    assert status == resume_service.STATUS_NOT_FOUND
    assert _counter_value(RESUME_LOAD_ATTEMPTS_TOTAL, outcome="not_found") >= (
        before_not_found + 1.0
    )


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

        before_save_failed = _counter_value(RESUME_SAVE_TOTAL, outcome="save_failed")
        saved = service.save_job_payload(job_id, payload, owner_token, ttl_seconds=30)
        loaded_payload, status = service.load_job_payload(job_id, owner_token)

        assert saved is False
        assert loaded_payload is None
        assert status == service.STATUS_NOT_FOUND
        assert _counter_value(RESUME_SAVE_TOTAL, outcome="save_failed") >= (
            before_save_failed + 1.0
        )
    finally:
        service.close()


def test_build_cache_key_uses_isolated_prefix_and_rejects_unsafe_value(resume_service):
    """Cache keys should be isolated by prefix and reject unsafe values."""
    cache_key = resume_service._build_cache_key("BRP-20260225-120006-ABC129")

    assert cache_key.startswith(resume_service.CACHE_KEY_PREFIX)

    with pytest.raises(ValueError):
        resume_service._build_cache_key("BRP-20260225-120006-ABC12/")


def test_load_rejects_payload_without_schema_marker(resume_service):
    """Payloads missing schema marker are incompatible in strict current version."""
    job_id = "BRP-20260225-120007-ABC130"
    owner_token = "owner-no-schema"
    payload = {"metadata": {"job_id": job_id}}

    resume_service._cache.set(
        resume_service._build_cache_key(job_id),
        {
            "job_id": job_id,
            "owner_token": owner_token,
            "created_at": "2026-02-25T12:00:07+00:00",
            "payload_version": resume_service.CURRENT_PAYLOAD_VERSION,
            "merged_result_payload": payload,
        },
        expire=30,
    )

    loaded_payload, status = resume_service.load_job_payload(job_id, owner_token)

    assert status == resume_service.STATUS_INCOMPATIBLE_VERSION
    assert loaded_payload is None


def test_alert_is_emitted_when_not_found_threshold_is_exceeded(tmp_path, caplog):
    """Service should emit operational alert for not_found spikes."""
    service = JobResumeService(
        cache_dir=tmp_path / "alert_not_found_cache",
        ttl_seconds=30,
        cache_size_mb=64,
        alert_window_seconds=60,
        alert_not_found_threshold=1,
        alert_token_mismatch_threshold=999,
        alert_save_failed_threshold=999,
    )
    try:
        with caplog.at_level("WARNING"):
            _, status = service.load_job_payload(
                "BRP-20260225-120008-ABC131",
                "owner-alert",
            )
        assert status == service.STATUS_NOT_FOUND
        assert any(
            rec.message == "Resume security alert threshold exceeded"
            and getattr(rec, "event", None) == service.STATUS_NOT_FOUND
            for rec in caplog.records
        )
    finally:
        service.close()


def test_alert_is_emitted_when_token_mismatch_threshold_is_exceeded(tmp_path, caplog):
    """Service should emit operational alert for token_mismatch spikes."""
    service = JobResumeService(
        cache_dir=tmp_path / "alert_token_cache",
        ttl_seconds=30,
        cache_size_mb=64,
        alert_window_seconds=60,
        alert_not_found_threshold=999,
        alert_token_mismatch_threshold=1,
        alert_save_failed_threshold=999,
    )
    try:
        job_id = "BRP-20260225-120009-ABC132"
        assert service.save_job_payload(
            job_id,
            {"metadata": {"job_id": job_id}},
            "owner-correct",
            ttl_seconds=30,
        )
        with caplog.at_level("WARNING"):
            _, status = service.load_job_payload(job_id, "owner-wrong")
        assert status == service.STATUS_TOKEN_MISMATCH
        assert any(
            rec.message == "Resume security alert threshold exceeded"
            and getattr(rec, "event", None) == service.STATUS_TOKEN_MISMATCH
            for rec in caplog.records
        )
    finally:
        service.close()


def test_alert_is_emitted_when_save_failed_threshold_is_exceeded(tmp_path, caplog):
    """Service should emit operational alert for save_failed spikes."""
    service = JobResumeService(
        cache_dir=tmp_path / "alert_save_failed_cache",
        ttl_seconds=30,
        cache_size_mb=64,
        max_payload_mb=1,
        alert_window_seconds=60,
        alert_not_found_threshold=999,
        alert_token_mismatch_threshold=999,
        alert_save_failed_threshold=1,
    )
    try:
        oversized_payload = {
            "metadata": {"job_id": "BRP-20260225-120010-ABC133"},
            "blob": "x" * (2 * 1024 * 1024),
        }
        with caplog.at_level("WARNING"):
            saved = service.save_job_payload(
                "BRP-20260225-120010-ABC133",
                oversized_payload,
                "owner-save-failed",
                ttl_seconds=30,
            )
        assert saved is False
        assert any(
            rec.message == "Resume security alert threshold exceeded"
            and getattr(rec, "event", None) == "save_failed"
            for rec in caplog.records
        )
    finally:
        service.close()


def test_resume_service_logs_redacted_job_ref_only(tmp_path, caplog):
    """Save/load logs should expose job_ref, never raw job_id fields."""
    service = JobResumeService(
        cache_dir=tmp_path / "job_ref_logs_cache",
        ttl_seconds=30,
        cache_size_mb=64,
    )
    job_id = "BRP-20260225-120011-ABC134"
    owner_token = "owner-job-ref"
    payload = {"metadata": {"job_id": job_id}}

    try:
        with caplog.at_level("INFO"):
            assert service.save_job_payload(job_id, payload, owner_token, ttl_seconds=30)
            loaded_payload, status = service.load_job_payload(job_id, owner_token)
            assert status == service.STATUS_OK
            assert loaded_payload == payload

        relevant_records = [
            rec
            for rec in caplog.records
            if rec.message in {"Resume payload saved", "Resume payload loaded"}
        ]
        assert relevant_records
        assert all(getattr(rec, "job_ref", "").startswith("job_") for rec in relevant_records)
        assert all(not hasattr(rec, "job_id") for rec in relevant_records)
        assert all(job_id not in str(rec.__dict__) for rec in relevant_records)
    finally:
        service.close()
