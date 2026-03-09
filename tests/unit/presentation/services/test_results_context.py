"""Unit tests for lightweight /results context helpers."""

from src.presentation.services.results_context import (
    build_results_context,
    context_has_results,
)


def test_build_results_context_returns_empty_for_invalid_payload():
    """Non-dict payload should produce a not-ready context."""
    context = build_results_context(None)
    assert context == {"ready": False, "job_id": None, "metadata": {}}


def test_build_results_context_keeps_only_allowed_metadata_keys():
    """Context metadata should stay compact and drop unrelated keys."""
    payload = {
        "metadata": {
            "job_id": "BRP-20260304-235959-ABCDEF",
            "sample_count": 9,
            "ko_count": 23644,
            "processing_time": 0.03,
            "database_overview": {"biorempp": {"matches": 1}},
            "ignored_field": "drop-me",
        }
    }

    context = build_results_context(payload)

    assert context["ready"] is True
    assert context["job_id"] == "BRP-20260304-235959-ABCDEF"
    assert context["metadata"]["sample_count"] == 9
    assert context["metadata"]["ko_count"] == 23644
    assert context["metadata"]["processing_time"] == 0.03
    assert "database_overview" in context["metadata"]
    assert "ignored_field" not in context["metadata"]


def test_context_has_results_true_only_when_ready_flag_present():
    """Ready flag controls whether /results can render processed state."""
    assert context_has_results({"ready": True}) is True
    assert context_has_results({"ready": False}) is False
    assert context_has_results({}) is False
    assert context_has_results(None) is False

