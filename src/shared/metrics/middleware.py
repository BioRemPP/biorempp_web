"""
Flask middleware for HTTP request metrics.
"""

from __future__ import annotations

import json
import re
import time

from flask import Flask, Response, g, request

from src.shared.logging import (
    clear_request_id,
    clear_trace_id,
    extract_trace_id_from_traceparent,
    generate_request_id,
    generate_trace_id,
    sanitize_trace_id,
    sanitize_incoming_request_id,
    set_request_id,
    set_trace_id,
)

from .registry import (
    DASH_CALLBACK_REQUEST_SIZE_BYTES,
    DASH_CALLBACK_RESPONSE_SIZE_BYTES,
    DASH_CALLBACK_SERVER_DURATION_SECONDS,
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUEST_SIZE_BYTES,
    HTTP_REQUESTS_TOTAL,
    HTTP_RESPONSE_SIZE_BYTES,
)

_STATE_KEY = "biorempp_observability"
_MIDDLEWARE_FLAG = "middleware_registered"
_DEFAULT_EXCLUDED_PATHS = frozenset(("/health", "/ready", "/favicon.ico"))
_DASH_OUTPUT_SAFE_PATTERN = re.compile(r"[^a-zA-Z0-9_.:\-]+")
_MAX_DASH_OUTPUT_LEN = 96


def _canonical_path(path: str) -> str:
    """Normalize path representation for comparisons."""
    if not path:
        return "/"
    trimmed = path.strip()
    if not trimmed:
        return "/"
    if not trimmed.startswith("/"):
        trimmed = f"/{trimmed}"
    if len(trimmed) > 1:
        trimmed = trimmed.rstrip("/")
    return trimmed or "/"


def _normalize_endpoint(path: str) -> str:
    """Normalize dynamic and high-cardinality paths for metric labels."""
    normalized = _canonical_path(path)

    if normalized.startswith("/_dash-"):
        return "/_dash-internal"
    if normalized.startswith("/data/"):
        return "/data/<filename>"
    if normalized.startswith("/schemas/"):
        return "/schemas/<db>"
    return normalized


def _is_excluded_endpoint(path: str, metrics_path: str = "/metrics") -> bool:
    """Check whether endpoint should be excluded from HTTP instrumentation."""
    canonical_path = _canonical_path(path)
    canonical_metrics_path = _canonical_path(metrics_path)
    return (
        canonical_path in _DEFAULT_EXCLUDED_PATHS
        or canonical_path == canonical_metrics_path
    )


def _normalize_dash_output_label(value: str) -> str:
    """Normalize dash callback output label to low cardinality safe text."""
    raw_value = (value or "").strip()
    if not raw_value:
        return "unknown_output"
    normalized = _DASH_OUTPUT_SAFE_PATTERN.sub("_", raw_value)
    return normalized[:_MAX_DASH_OUTPUT_LEN] or "unknown_output"


def _dash_output_from_descriptor(descriptor: object) -> str | None:
    """Extract callback output descriptor from Dash request payload fields."""
    if isinstance(descriptor, str):
        return descriptor
    if not isinstance(descriptor, dict):
        return None

    prop = descriptor.get("property")
    if not isinstance(prop, str) or not prop.strip():
        return None

    component_id = descriptor.get("id")
    if isinstance(component_id, dict):
        component_repr = json.dumps(component_id, sort_keys=True, separators=(",", ":"))
    else:
        component_repr = str(component_id).strip() if component_id is not None else ""
    if not component_repr:
        return None

    return f"{component_repr}.{prop.strip()}"


def _extract_dash_output_label(payload: object) -> str:
    """Extract callback output label from Dash update request payload."""
    if not isinstance(payload, dict):
        return "unknown_output"

    output_label = _dash_output_from_descriptor(payload.get("output"))
    if output_label:
        return _normalize_dash_output_label(output_label)

    outputs = payload.get("outputs")
    if isinstance(outputs, list) and outputs:
        output_label = _dash_output_from_descriptor(outputs[0])
    elif isinstance(outputs, dict):
        output_label = _dash_output_from_descriptor(outputs)
    else:
        output_label = None

    return _normalize_dash_output_label(output_label or "unknown_output")


def _get_state(flask_app: Flask) -> dict:
    """Return mutable observability state for this Flask app."""
    return flask_app.extensions.setdefault(_STATE_KEY, {})


def register_metrics_middleware(flask_app: Flask, metrics_path: str = "/metrics") -> None:
    """Register request/response metrics hooks on Flask app (idempotent)."""
    state = _get_state(flask_app)
    if state.get(_MIDDLEWARE_FLAG):
        return

    canonical_metrics_path = _canonical_path(metrics_path)
    state["metrics_path"] = canonical_metrics_path

    @flask_app.before_request
    def _before_request_metrics() -> None:
        incoming_request_id = sanitize_incoming_request_id(
            request.headers.get("X-Request-ID", "")
        )
        request_id = incoming_request_id or generate_request_id()
        g._biorempp_request_id = request_id
        set_request_id(request_id)

        trace_id = (
            extract_trace_id_from_traceparent(request.headers.get("traceparent", ""))
            or sanitize_trace_id(request.headers.get("X-B3-TraceId", ""))
            or sanitize_trace_id(request.headers.get("X-Trace-ID", ""))
            or generate_trace_id()
        )
        g._biorempp_trace_id = trace_id
        set_trace_id(trace_id)

        request_path = _canonical_path(request.path)
        if _is_excluded_endpoint(request_path, canonical_metrics_path):
            g._biorempp_track_metrics = False
            return

        g._biorempp_track_metrics = True
        g._biorempp_metrics_start = time.perf_counter()
        g._biorempp_metrics_endpoint = _normalize_endpoint(request_path)
        g._biorempp_dash_output = "unknown_output"

        if g._biorempp_metrics_endpoint == "/_dash-internal":
            payload = request.get_json(silent=True)
            g._biorempp_dash_output = _extract_dash_output_label(payload)

        content_length = request.content_length or 0
        if content_length > 0:
            HTTP_REQUEST_SIZE_BYTES.labels(
                method=request.method,
                endpoint=g._biorempp_metrics_endpoint,
            ).observe(float(content_length))

            if g._biorempp_metrics_endpoint == "/_dash-internal":
                DASH_CALLBACK_REQUEST_SIZE_BYTES.labels(
                    dash_output=g._biorempp_dash_output,
                ).observe(float(content_length))

    @flask_app.after_request
    def _after_request_metrics(response: Response) -> Response:
        request_id = getattr(g, "_biorempp_request_id", None)
        if request_id:
            response.headers["X-Request-ID"] = request_id
        trace_id = getattr(g, "_biorempp_trace_id", None)
        if trace_id:
            response.headers["X-Trace-ID"] = trace_id

        if not getattr(g, "_biorempp_track_metrics", False):
            clear_request_id()
            clear_trace_id()
            return response

        start = getattr(g, "_biorempp_metrics_start", None)
        endpoint = getattr(g, "_biorempp_metrics_endpoint", _normalize_endpoint(request.path))
        if start is None:
            clear_request_id()
            clear_trace_id()
            return response

        method = request.method
        status_code = str(response.status_code)
        elapsed = time.perf_counter() - start

        HTTP_REQUESTS_TOTAL.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
        ).inc()

        HTTP_REQUEST_DURATION_SECONDS.labels(
            method=method,
            endpoint=endpoint,
        ).observe(elapsed)

        if endpoint == "/_dash-internal":
            dash_output = getattr(g, "_biorempp_dash_output", "unknown_output")
            DASH_CALLBACK_SERVER_DURATION_SECONDS.labels(
                dash_output=dash_output,
            ).observe(elapsed)

        if response.status_code >= 400:
            HTTP_ERRORS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
            ).inc()

        response_size = response.content_length
        if response_size is None:
            response_size = response.calculate_content_length()
        if response_size:
            HTTP_RESPONSE_SIZE_BYTES.labels(
                method=method,
                endpoint=endpoint,
            ).observe(float(response_size))

            if endpoint == "/_dash-internal":
                dash_output = getattr(g, "_biorempp_dash_output", "unknown_output")
                DASH_CALLBACK_RESPONSE_SIZE_BYTES.labels(
                    dash_output=dash_output,
                ).observe(float(response_size))

        clear_request_id()
        clear_trace_id()
        return response

    @flask_app.teardown_request
    def _teardown_request_metrics(_exc) -> None:
        clear_request_id()
        clear_trace_id()

    state[_MIDDLEWARE_FLAG] = True


__all__ = [
    "register_metrics_middleware",
    "_normalize_endpoint",
    "_is_excluded_endpoint",
    "_extract_dash_output_label",
]
