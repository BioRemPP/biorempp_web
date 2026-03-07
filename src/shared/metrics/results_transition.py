"""Helpers to sanitize and record results transition client telemetry."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from .registry import (
    RESULTS_TRANSITION_CLICK_TO_PAINT_SECONDS,
    RESULTS_TRANSITION_CLICK_TO_REQUEST_SECONDS,
    RESULTS_TRANSITION_REQUEST_BYTES,
    RESULTS_TRANSITION_REQUEST_TO_PAINT_SECONDS,
    RESULTS_TRANSITION_RESPONSE_BYTES,
    RESULTS_TRANSITION_SAMPLES_TOTAL,
)

_DEFAULT_ROUTE = "/results"
_MAX_DURATION_SECONDS = 180.0
_MAX_BYTES = 100 * 1024 * 1024
_MAX_TEXT_LEN = 128
_MAX_USER_AGENT_LEN = 256


def _coerce_seconds(value: Any) -> float | None:
    """Coerce duration values to a finite, non-negative seconds float."""
    if value is None:
        return None
    try:
        coerced = float(value)
    except (TypeError, ValueError):
        return None
    if coerced < 0.0 or coerced > _MAX_DURATION_SECONDS:
        return None
    return coerced


def _coerce_bytes(value: Any) -> int | None:
    """Coerce byte-size values to bounded integers."""
    if value is None:
        return None
    try:
        coerced = int(value)
    except (TypeError, ValueError):
        return None
    if coerced < 0 or coerced > _MAX_BYTES:
        return None
    return coerced


def _coerce_text(value: Any, max_len: int = _MAX_TEXT_LEN) -> str | None:
    """Coerce and trim text values used for metadata labels."""
    if not isinstance(value, str):
        return None
    trimmed = value.strip()
    if not trimmed:
        return None
    return trimmed[:max_len]


def sanitize_results_transition_payload(
    payload: Mapping[str, Any] | Any,
    *,
    remote_addr: str | None = None,
) -> dict[str, Any] | None:
    """
    Validate and sanitize incoming client telemetry payload.

    Parameters
    ----------
    payload : Mapping[str, Any] | Any
        Raw payload received from browser beacon.
    remote_addr : str | None
        Optional client address for log diagnostics.
    """
    if not isinstance(payload, Mapping):
        return None

    route = _coerce_text(payload.get("route")) or _DEFAULT_ROUTE
    if not route.startswith("/"):
        route = _DEFAULT_ROUTE

    click_to_request_seconds = _coerce_seconds(payload.get("click_to_request_seconds"))
    request_to_paint_seconds = _coerce_seconds(payload.get("request_to_paint_seconds"))
    click_to_paint_seconds = _coerce_seconds(payload.get("click_to_paint_seconds"))

    if (
        click_to_request_seconds is None
        and request_to_paint_seconds is None
        and click_to_paint_seconds is None
    ):
        return None

    request_bytes = _coerce_bytes(payload.get("request_bytes"))
    response_bytes = _coerce_bytes(payload.get("response_bytes"))
    job_id = _coerce_text(payload.get("job_id"), max_len=64)
    session_id = _coerce_text(payload.get("session_id"), max_len=64)
    dash_output = _coerce_text(payload.get("dash_output"), max_len=96)
    user_agent = _coerce_text(payload.get("user_agent"), max_len=_MAX_USER_AGENT_LEN)

    sanitized: dict[str, Any] = {
        "route": route,
        "click_to_request_seconds": click_to_request_seconds,
        "request_to_paint_seconds": request_to_paint_seconds,
        "click_to_paint_seconds": click_to_paint_seconds,
        "request_bytes": request_bytes,
        "response_bytes": response_bytes,
        "job_id": job_id,
        "session_id": session_id,
        "dash_output": dash_output,
        "event_time_utc": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
        "client_time_utc": _coerce_text(payload.get("client_time_utc"), max_len=64),
    }

    if user_agent is not None:
        sanitized["user_agent"] = user_agent
    if remote_addr:
        sanitized["remote_addr"] = remote_addr

    return sanitized


def mark_results_transition_invalid_sample() -> None:
    """Increment invalid telemetry payload counter."""
    RESULTS_TRANSITION_SAMPLES_TOTAL.labels(outcome="invalid").inc()


def observe_results_transition_sample(sample: Mapping[str, Any]) -> None:
    """Observe sanitized telemetry sample into Prometheus histograms."""
    route = str(sample.get("route") or _DEFAULT_ROUTE)
    RESULTS_TRANSITION_SAMPLES_TOTAL.labels(outcome="accepted").inc()

    click_to_request_seconds = _coerce_seconds(sample.get("click_to_request_seconds"))
    if click_to_request_seconds is not None:
        RESULTS_TRANSITION_CLICK_TO_REQUEST_SECONDS.labels(route=route).observe(
            click_to_request_seconds
        )

    request_to_paint_seconds = _coerce_seconds(sample.get("request_to_paint_seconds"))
    if request_to_paint_seconds is not None:
        RESULTS_TRANSITION_REQUEST_TO_PAINT_SECONDS.labels(route=route).observe(
            request_to_paint_seconds
        )

    click_to_paint_seconds = _coerce_seconds(sample.get("click_to_paint_seconds"))
    if click_to_paint_seconds is not None:
        RESULTS_TRANSITION_CLICK_TO_PAINT_SECONDS.labels(route=route).observe(
            click_to_paint_seconds
        )

    request_bytes = _coerce_bytes(sample.get("request_bytes"))
    if request_bytes is not None:
        RESULTS_TRANSITION_REQUEST_BYTES.labels(route=route).observe(float(request_bytes))

    response_bytes = _coerce_bytes(sample.get("response_bytes"))
    if response_bytes is not None:
        RESULTS_TRANSITION_RESPONSE_BYTES.labels(route=route).observe(
            float(response_bytes)
        )


__all__ = [
    "sanitize_results_transition_payload",
    "mark_results_transition_invalid_sample",
    "observe_results_transition_sample",
]

