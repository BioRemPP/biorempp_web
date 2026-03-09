"""Unit tests for request/trace context helper functions."""

from src.shared.logging.request_context import (
    extract_trace_id_from_traceparent,
    sanitize_trace_id,
)


def test_extract_trace_id_from_valid_traceparent() -> None:
    trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
    traceparent = f"00-{trace_id}-00f067aa0ba902b7-01"
    assert extract_trace_id_from_traceparent(traceparent) == trace_id


def test_extract_trace_id_from_invalid_traceparent() -> None:
    assert extract_trace_id_from_traceparent("invalid-traceparent") == ""
    assert (
        extract_trace_id_from_traceparent(
            "00-00000000000000000000000000000000-00f067aa0ba902b7-01"
        )
        == ""
    )


def test_sanitize_trace_id_accepts_16_or_32_hex() -> None:
    assert sanitize_trace_id("0123456789abcdef") == "0123456789abcdef"
    assert sanitize_trace_id("4bf92f3577b34da6a3ce929d0e0e4736") == (
        "4bf92f3577b34da6a3ce929d0e0e4736"
    )
    assert sanitize_trace_id("BADTRACE") == ""
