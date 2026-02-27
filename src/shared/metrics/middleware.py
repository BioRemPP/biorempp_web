"""
Flask middleware for HTTP request metrics.
"""

from __future__ import annotations

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
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUEST_SIZE_BYTES,
    HTTP_REQUESTS_TOTAL,
    HTTP_RESPONSE_SIZE_BYTES,
)

_STATE_KEY = "biorempp_observability"
_MIDDLEWARE_FLAG = "middleware_registered"
_DEFAULT_EXCLUDED_PATHS = frozenset(("/health", "/ready", "/favicon.ico"))


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

        content_length = request.content_length or 0
        if content_length > 0:
            HTTP_REQUEST_SIZE_BYTES.labels(
                method=request.method,
                endpoint=g._biorempp_metrics_endpoint,
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
]
