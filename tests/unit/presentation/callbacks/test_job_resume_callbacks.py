"""Unit tests for job resume callback logic."""

import time
from typing import Any

import pytest
from dash import no_update

from src.presentation.callbacks import job_resume_callbacks
from src.presentation.services.job_resume_service import JobResumeService


def _flatten_text(node: Any) -> str:
    """Extract plain text recursively from Dash component trees."""
    fragments: list[str] = []

    def visit(value: Any) -> None:
        if value is None:
            return
        if isinstance(value, (str, int, float)):
            fragments.append(str(value))
            return
        if isinstance(value, (list, tuple)):
            for item in value:
                visit(item)
            return
        children = getattr(value, "children", None)
        if children is not None:
            visit(children)

    visit(node)
    return " ".join(fragments)


@pytest.fixture
def isolated_resume_service(tmp_path, monkeypatch):
    """Patch callback module singleton with isolated diskcache service."""
    service = JobResumeService(
        cache_dir=tmp_path / "callback_resume_cache",
        ttl_seconds=30,
        cache_size_mb=64,
    )
    monkeypatch.setattr(job_resume_callbacks, "job_resume_service", service)
    yield service
    service.close()


def test_resolve_resume_request_rejects_invalid_job_id(isolated_resume_service):
    """Invalid job id should return an error and keep stores unchanged."""
    data_update, pathname_update, status_component = (
        job_resume_callbacks.resolve_resume_request("invalid-job-id", "token-1")
    )

    assert data_update is no_update
    assert pathname_update is no_update
    assert "Invalid Job ID" in _flatten_text(status_component)


def test_resolve_resume_request_returns_not_found_when_job_absent(
    isolated_resume_service,
):
    """Missing job id should surface not found/expired guidance."""
    data_update, pathname_update, status_component = (
        job_resume_callbacks.resolve_resume_request(
            "BRP-20260225-123000-ABC111",
            "token-2",
        )
    )

    assert data_update is no_update
    assert pathname_update is no_update
    assert "not found or expired" in _flatten_text(status_component)


def test_resolve_resume_request_returns_not_found_when_job_expired(
    isolated_resume_service,
):
    """Expired cache entries should behave as not found."""
    job_id = "BRP-20260225-123001-ABC112"
    owner_token = "token-3"
    payload = {"metadata": {"job_id": job_id}, "biorempp_df": []}

    assert isolated_resume_service.save_job_payload(
        job_id,
        payload,
        owner_token,
        ttl_seconds=1,
    )
    time.sleep(1.2)

    data_update, pathname_update, status_component = (
        job_resume_callbacks.resolve_resume_request(job_id, owner_token)
    )

    assert data_update is no_update
    assert pathname_update is no_update
    assert "not found or expired" in _flatten_text(status_component)


def test_resolve_resume_request_rejects_token_mismatch(isolated_resume_service):
    """Owner token mismatch must be blocked."""
    job_id = "BRP-20260225-123002-ABC113"
    payload = {"metadata": {"job_id": job_id}, "biorempp_df": []}

    assert isolated_resume_service.save_job_payload(
        job_id,
        payload,
        "token-owner-a",
        ttl_seconds=30,
    )

    data_update, pathname_update, status_component = (
        job_resume_callbacks.resolve_resume_request(job_id, "token-owner-b")
    )

    assert data_update is no_update
    assert pathname_update is no_update
    assert "belongs to another browser context" in _flatten_text(status_component)


def test_resolve_resume_request_success_returns_payload_and_redirect(
    isolated_resume_service,
):
    """Valid job+token should restore payload and redirect to results."""
    job_id = "BRP-20260225-123003-ABC114"
    owner_token = "token-4"
    payload = {
        "metadata": {"job_id": job_id},
        "biorempp_df": [{"Sample": "S1", "KO": "K00001"}],
    }
    assert isolated_resume_service.save_job_payload(
        job_id,
        payload,
        owner_token,
        ttl_seconds=30,
    )

    data_update, pathname_update, status_component = (
        job_resume_callbacks.resolve_resume_request(job_id, owner_token)
    )

    assert data_update == payload
    assert pathname_update == "/results"
    assert "loaded" in _flatten_text(status_component)


def test_resolve_resume_request_uses_generic_error_in_strict_mode(
    isolated_resume_service, monkeypatch
):
    """Strict security mode should hide token mismatch details."""
    monkeypatch.setenv("BIOREMPP_RESUME_SECURITY_MODE", "strict")

    job_id = "BRP-20260225-123004-ABC115"
    payload = {"metadata": {"job_id": job_id}, "biorempp_df": []}
    assert isolated_resume_service.save_job_payload(
        job_id,
        payload,
        "token-owner-z",
        ttl_seconds=30,
    )

    data_update, pathname_update, status_component = (
        job_resume_callbacks.resolve_resume_request(job_id, "token-owner-y")
    )

    assert data_update is no_update
    assert pathname_update is no_update
    assert "unavailable in this browser context" in _flatten_text(status_component)
