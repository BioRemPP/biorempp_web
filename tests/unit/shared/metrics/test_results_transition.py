"""Unit tests for results transition telemetry helpers."""

from __future__ import annotations

from src.shared.metrics.registry import (
    RESULTS_TRANSITION_CLICK_TO_PAINT_SECONDS,
    RESULTS_TRANSITION_CLICK_TO_REQUEST_SECONDS,
    RESULTS_TRANSITION_REQUEST_BYTES,
    RESULTS_TRANSITION_REQUEST_TO_PAINT_SECONDS,
    RESULTS_TRANSITION_RESPONSE_BYTES,
    RESULTS_TRANSITION_SAMPLES_TOTAL,
)
from src.shared.metrics.results_transition import (
    mark_results_transition_invalid_sample,
    observe_results_transition_sample,
    sanitize_results_transition_payload,
)


def _counter_value(counter, **labels) -> float:
    return float(counter.labels(**labels)._value.get())


def _histogram_count(histogram, **labels) -> float:
    expected_labels = {key: str(value) for key, value in labels.items()}
    sample_name = f"{histogram._name}_count"
    for metric in histogram.collect():
        for sample in metric.samples:
            if sample.name == sample_name and sample.labels == expected_labels:
                return float(sample.value)
    return 0.0


def test_sanitize_results_transition_payload_rejects_invalid_payload() -> None:
    assert sanitize_results_transition_payload(None) is None
    assert sanitize_results_transition_payload({"route": "/results"}) is None
    assert (
        sanitize_results_transition_payload({"click_to_request_seconds": -1})
        is None
    )


def test_sanitize_results_transition_payload_accepts_expected_fields() -> None:
    sample = sanitize_results_transition_payload(
        {
            "route": "/results",
            "click_to_request_seconds": 0.125,
            "request_to_paint_seconds": 1.55,
            "click_to_paint_seconds": 1.675,
            "request_bytes": 320,
            "response_bytes": 10240,
            "dash_output": "url.pathname",
            "session_id": "abc123",
            "job_id": "BRP-20260304-111730-F07FDD",
        }
    )
    assert sample is not None
    assert sample["route"] == "/results"
    assert sample["click_to_request_seconds"] == 0.125
    assert sample["request_to_paint_seconds"] == 1.55
    assert sample["click_to_paint_seconds"] == 1.675
    assert sample["request_bytes"] == 320
    assert sample["response_bytes"] == 10240
    assert sample["dash_output"] == "url.pathname"
    assert sample["session_id"] == "abc123"
    assert sample["job_id"] == "BRP-20260304-111730-F07FDD"


def test_observe_results_transition_sample_updates_metrics() -> None:
    sample = {
        "route": "/results",
        "click_to_request_seconds": 0.20,
        "request_to_paint_seconds": 1.40,
        "click_to_paint_seconds": 1.60,
        "request_bytes": 512,
        "response_bytes": 2048,
    }

    accepted_before = _counter_value(
        RESULTS_TRANSITION_SAMPLES_TOTAL,
        outcome="accepted",
    )
    ctr_before = _histogram_count(
        RESULTS_TRANSITION_CLICK_TO_REQUEST_SECONDS,
        route="/results",
    )
    rtp_before = _histogram_count(
        RESULTS_TRANSITION_REQUEST_TO_PAINT_SECONDS,
        route="/results",
    )
    ctp_before = _histogram_count(
        RESULTS_TRANSITION_CLICK_TO_PAINT_SECONDS,
        route="/results",
    )
    req_size_before = _histogram_count(
        RESULTS_TRANSITION_REQUEST_BYTES,
        route="/results",
    )
    res_size_before = _histogram_count(
        RESULTS_TRANSITION_RESPONSE_BYTES,
        route="/results",
    )

    observe_results_transition_sample(sample)

    accepted_after = _counter_value(
        RESULTS_TRANSITION_SAMPLES_TOTAL,
        outcome="accepted",
    )
    ctr_after = _histogram_count(
        RESULTS_TRANSITION_CLICK_TO_REQUEST_SECONDS,
        route="/results",
    )
    rtp_after = _histogram_count(
        RESULTS_TRANSITION_REQUEST_TO_PAINT_SECONDS,
        route="/results",
    )
    ctp_after = _histogram_count(
        RESULTS_TRANSITION_CLICK_TO_PAINT_SECONDS,
        route="/results",
    )
    req_size_after = _histogram_count(
        RESULTS_TRANSITION_REQUEST_BYTES,
        route="/results",
    )
    res_size_after = _histogram_count(
        RESULTS_TRANSITION_RESPONSE_BYTES,
        route="/results",
    )

    assert accepted_after == accepted_before + 1.0
    assert ctr_after == ctr_before + 1.0
    assert rtp_after == rtp_before + 1.0
    assert ctp_after == ctp_before + 1.0
    assert req_size_after == req_size_before + 1.0
    assert res_size_after == res_size_before + 1.0


def test_mark_results_transition_invalid_sample_updates_counter() -> None:
    invalid_before = _counter_value(
        RESULTS_TRANSITION_SAMPLES_TOTAL,
        outcome="invalid",
    )
    mark_results_transition_invalid_sample()
    invalid_after = _counter_value(
        RESULTS_TRANSITION_SAMPLES_TOTAL,
        outcome="invalid",
    )
    assert invalid_after == invalid_before + 1.0

