"""Unit tests for /results payload resolver hydration behavior."""

from src.presentation.services import results_payload_resolver as resolver


def _build_full_payload(job_id: str) -> dict:
    return {
        "biorempp_df": [],
        "hadeg_df": [],
        "toxcsm_df": [],
        "kegg_df": [],
        "metadata": {"job_id": job_id},
    }


def _build_store_ref(job_id: str, owner_token: str) -> dict:
    return {
        "_payload_ref": {
            "version": 1,
            "job_id": job_id,
            "owner_token": owner_token,
        },
        "metadata": {"job_id": job_id},
    }


def test_prime_cache_allows_resolve_without_backend_call(monkeypatch):
    """Primed cache should satisfy resolver without hitting resume backend."""
    job_id = "BRP-20260310-150010-ABC120"
    owner_token = "token-primed"
    payload = _build_full_payload(job_id)
    store_ref = _build_store_ref(job_id, owner_token)

    assert resolver.prime_results_payload_cache(payload, owner_token) is True

    def _unexpected_backend_call(*_args, **_kwargs):
        raise AssertionError("resume backend should not be called for primed payload")

    monkeypatch.setattr(
        resolver.job_resume_service,
        "load_job_payload",
        _unexpected_backend_call,
    )

    resolved = resolver.resolve_results_payload(store_ref)
    assert resolved == payload


def test_resolver_retries_not_found_before_success(monkeypatch):
    """Hydration should retry transient not_found and eventually resolve payload."""
    job_id = "BRP-20260310-150011-ABC121"
    owner_token = "token-retry"
    payload = _build_full_payload(job_id)
    store_ref = _build_store_ref(job_id, owner_token)
    status_not_found = resolver.job_resume_service.STATUS_NOT_FOUND
    status_ok = resolver.job_resume_service.STATUS_OK

    monkeypatch.setattr(resolver.settings, "RESULTS_HYDRATION_RETRY_ATTEMPTS", 3)
    monkeypatch.setattr(resolver.settings, "RESULTS_HYDRATION_RETRY_DELAY_MS", 1)

    sleep_calls: list[float] = []
    monkeypatch.setattr(resolver.time, "sleep", lambda value: sleep_calls.append(value))

    attempts = {"count": 0}

    def _fake_load(*_args, **_kwargs):
        attempts["count"] += 1
        if attempts["count"] < 3:
            return None, status_not_found
        return payload, status_ok

    monkeypatch.setattr(resolver.job_resume_service, "load_job_payload", _fake_load)

    resolved = resolver.resolve_results_payload(store_ref)
    assert resolved == payload
    assert attempts["count"] == 3
    assert len(sleep_calls) == 2


def test_resolver_does_not_retry_on_token_mismatch(monkeypatch):
    """Token mismatch must fail fast without retry loop."""
    job_id = "BRP-20260310-150012-ABC122"
    owner_token = "token-fast-fail"
    store_ref = _build_store_ref(job_id, owner_token)
    status_token_mismatch = resolver.job_resume_service.STATUS_TOKEN_MISMATCH

    monkeypatch.setattr(resolver.settings, "RESULTS_HYDRATION_RETRY_ATTEMPTS", 8)
    monkeypatch.setattr(resolver.settings, "RESULTS_HYDRATION_RETRY_DELAY_MS", 250)

    sleep_calls: list[float] = []
    monkeypatch.setattr(resolver.time, "sleep", lambda value: sleep_calls.append(value))

    attempts = {"count": 0}

    def _fake_load(*_args, **_kwargs):
        attempts["count"] += 1
        return None, status_token_mismatch

    monkeypatch.setattr(resolver.job_resume_service, "load_job_payload", _fake_load)

    resolved = resolver.resolve_results_payload(store_ref)
    assert resolved == {}
    assert attempts["count"] == 1
    assert sleep_calls == []
