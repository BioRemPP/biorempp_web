"""Unit tests for results payload transport selection in processing callbacks."""

from typing import Any

from dash import no_update

from src.presentation.callbacks import real_processing_callbacks


def _build_full_payload(job_id: str) -> dict:
    return {
        "biorempp_df": [],
        "hadeg_df": [],
        "toxcsm_df": [],
        "kegg_df": [],
        "metadata": {"job_id": job_id},
    }


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


def test_server_mode_uses_reference_payload_even_without_resume_confirmation(
    monkeypatch,
):
    """Server mode should prefer lightweight payload reference transport."""
    job_id = "BRP-20260310-150001-ABC111"
    token = "token-a"
    full_payload = _build_full_payload(job_id)
    payload_ref = {
        "_payload_ref": {
            "version": 1,
            "job_id": job_id,
            "owner_token": token,
        },
        "metadata": {"job_id": job_id},
    }

    monkeypatch.setattr(
        real_processing_callbacks.settings, "RESULTS_PAYLOAD_MODE", "server"
    )
    monkeypatch.setattr(
        real_processing_callbacks,
        "build_results_payload_ref",
        lambda *_args, **_kwargs: payload_ref,
    )

    merged_store_payload, mode = real_processing_callbacks._select_results_payload_transport(
        full_payload,
        token,
    )

    assert mode == "server_ref"
    assert merged_store_payload == payload_ref


def test_client_mode_keeps_full_payload(monkeypatch):
    """Client mode should keep legacy full payload transport."""
    job_id = "BRP-20260310-150002-ABC112"
    token = "token-b"
    full_payload = _build_full_payload(job_id)

    monkeypatch.setattr(
        real_processing_callbacks.settings, "RESULTS_PAYLOAD_MODE", "client"
    )

    merged_store_payload, mode = real_processing_callbacks._select_results_payload_transport(
        full_payload,
        token,
    )

    assert mode == "client_full"
    assert merged_store_payload == full_payload


def test_server_mode_blocks_when_reference_is_invalid(monkeypatch):
    """Invalid reference result should trigger hard transport guard."""
    job_id = "BRP-20260310-150003-ABC113"
    token = "token-c"
    full_payload = _build_full_payload(job_id)

    monkeypatch.setattr(
        real_processing_callbacks.settings, "RESULTS_PAYLOAD_MODE", "server"
    )
    monkeypatch.setattr(
        real_processing_callbacks,
        "build_results_payload_ref",
        lambda *_args, **_kwargs: full_payload,
    )

    merged_store_payload, mode = real_processing_callbacks._select_results_payload_transport(
        full_payload,
        token,
    )

    assert mode == "guard_blocked_invalid_ref"
    assert merged_store_payload is None


def test_transport_guard_response_returns_controlled_error(monkeypatch):
    """Guard response should keep stores unchanged and return explicit UI error."""
    monkeypatch.setattr(real_processing_callbacks.settings, "RESULTS_PAYLOAD_MODE", "server")

    response = real_processing_callbacks._build_transport_guard_response(
        "BRP-20260310-150004-ABC114",
        "guard_blocked_invalid_ref",
    )

    assert len(response) == 6
    assert "Results Transport Guard" in _flatten_text(response[0])
    assert response[1] is no_update
    assert response[2] is no_update
    assert response[3] == {"display": "none"}
    assert response[4] is no_update
    assert response[5] is no_update
