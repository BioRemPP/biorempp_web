"""
Prometheus metrics registry for BioRemPP.

Metric objects are defined at module level and created idempotently so
module reloads in development do not raise duplicated timeseries errors.
"""

from __future__ import annotations

from typing import Any, Callable

from prometheus_client import Counter, Gauge, Histogram, REGISTRY

MetricFactory = Callable[..., Any]


def _existing_collector(metric_name: str) -> Any | None:
    """Return existing collector when metric already exists in global registry."""
    names_to_collectors = getattr(REGISTRY, "_names_to_collectors", {})
    return names_to_collectors.get(metric_name)


def _metric(
    factory: MetricFactory,
    metric_name: str,
    documentation: str,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Create metric once per process and reuse collector on module reload."""
    existing = _existing_collector(metric_name)
    if existing is not None:
        return existing
    return factory(metric_name, documentation, *args, **kwargs)


HTTP_DURATION_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)

SIZE_BUCKETS = (
    128.0,
    512.0,
    1024.0,
    4096.0,
    16384.0,
    65536.0,
    262144.0,
    1048576.0,
    5242880.0,
    20971520.0,
)

CALLBACK_DURATION_BUCKETS = (
    0.01,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    15.0,
    30.0,
    60.0,
)

DASH_CALLBACK_DURATION_BUCKETS = (
    0.005,
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)

PROCESSING_DURATION_BUCKETS = (
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    30.0,
    60.0,
    120.0,
    300.0,
)

RESULTS_TRANSITION_DURATION_BUCKETS = (
    0.01,
    0.025,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.0,
    3.0,
    5.0,
    8.0,
    13.0,
    21.0,
)

# HTTP metrics
HTTP_REQUESTS_TOTAL = _metric(
    Counter,
    "biorempp_http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status_code"],
)

HTTP_ERRORS_TOTAL = _metric(
    Counter,
    "biorempp_http_errors_total",
    "Total number of HTTP error responses (status >= 400)",
    ["method", "endpoint", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = _metric(
    Histogram,
    "biorempp_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=HTTP_DURATION_BUCKETS,
)

HTTP_REQUEST_SIZE_BYTES = _metric(
    Histogram,
    "biorempp_http_request_size_bytes",
    "HTTP request body size in bytes",
    ["method", "endpoint"],
    buckets=SIZE_BUCKETS,
)

HTTP_RESPONSE_SIZE_BYTES = _metric(
    Histogram,
    "biorempp_http_response_size_bytes",
    "HTTP response body size in bytes",
    ["method", "endpoint"],
    buckets=SIZE_BUCKETS,
)

# Callback metrics
CALLBACK_DURATION_SECONDS = _metric(
    Histogram,
    "biorempp_callback_duration_seconds",
    "Dash callback execution duration in seconds",
    ["callback_id"],
    buckets=CALLBACK_DURATION_BUCKETS,
)

CALLBACK_ERRORS_TOTAL = _metric(
    Counter,
    "biorempp_callback_errors_total",
    "Total callback execution errors",
    ["callback_id", "error_type"],
)

# Dash callback request-level metrics
DASH_CALLBACK_SERVER_DURATION_SECONDS = _metric(
    Histogram,
    "biorempp_dash_callback_server_duration_seconds",
    "Dash callback request duration in seconds by callback output",
    ["dash_output"],
    buckets=DASH_CALLBACK_DURATION_BUCKETS,
)

DASH_CALLBACK_REQUEST_SIZE_BYTES = _metric(
    Histogram,
    "biorempp_dash_callback_request_size_bytes",
    "Dash callback request payload size in bytes by callback output",
    ["dash_output"],
    buckets=SIZE_BUCKETS,
)

DASH_CALLBACK_RESPONSE_SIZE_BYTES = _metric(
    Histogram,
    "biorempp_dash_callback_response_size_bytes",
    "Dash callback response size in bytes by callback output",
    ["dash_output"],
    buckets=SIZE_BUCKETS,
)

# Cache metrics
CACHE_OPERATIONS_TOTAL = _metric(
    Counter,
    "biorempp_cache_operations_total",
    "Total cache operations by type and outcome",
    ["cache_type", "operation", "outcome"],
)

CACHE_SIZE_ITEMS = _metric(
    Gauge,
    "biorempp_cache_size_items",
    "Current number of items in cache",
    ["cache_type"],
)

CACHE_HIT_RATIO = _metric(
    Gauge,
    "biorempp_cache_hit_ratio",
    "Current cache hit ratio snapshot (0.0 to 1.0)",
    ["cache_type"],
)

CACHE_ENTRY_SIZE_BYTES = _metric(
    Histogram,
    "biorempp_cache_entry_size_bytes",
    "Approximate cache entry size in bytes",
    ["cache_type"],
    buckets=SIZE_BUCKETS,
)

# Resume metrics
RESUME_LOAD_ATTEMPTS_TOTAL = _metric(
    Counter,
    "biorempp_resume_load_attempts_total",
    "Total job resume load attempts by outcome",
    ["outcome"],
)

RESUME_SAVE_TOTAL = _metric(
    Counter,
    "biorempp_resume_save_total",
    "Total job resume save operations by outcome",
    ["outcome"],
)

RESUME_PAYLOAD_SIZE_BYTES = _metric(
    Histogram,
    "biorempp_resume_payload_size_bytes",
    "Serialized resume payload size in bytes",
    ["backend"],
    buckets=(
        1024.0,
        16384.0,
        131072.0,
        524288.0,
        1048576.0,
        4194304.0,
        16777216.0,
        67108864.0,
    ),
)

RESUME_OPERATION_DURATION_SECONDS = _metric(
    Histogram,
    "biorempp_resume_operation_duration_seconds",
    "Resume save/load operation duration in seconds",
    ["backend", "operation", "status"],
    buckets=(
        0.001,
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
    ),
)

RESUME_CALLBACK_ATTEMPTS_TOTAL = _metric(
    Counter,
    "biorempp_resume_callback_attempts_total",
    "Total resume callback attempts by non-sensitive outcome",
    ["outcome"],
)

RESUME_RATE_LIMIT_BACKEND_INFO = _metric(
    Gauge,
    "biorempp_resume_rate_limit_backend_info",
    "Selected resume rate-limit backend (1 active, 0 inactive)",
    ["backend"],
    multiprocess_mode="livemax",
)

RESUME_RATE_LIMIT_ERRORS_TOTAL = _metric(
    Counter,
    "biorempp_resume_rate_limit_errors_total",
    "Total resume rate-limit backend errors by backend and operation",
    ["backend", "operation"],
)

RESUME_REQUEST_IP_SOURCE_TOTAL = _metric(
    Counter,
    "biorempp_resume_request_ip_source_total",
    "Total resume requests by resolved client IP source",
    ["source"],
)

UPLOAD_OPERATIONS_TOTAL = _metric(
    Counter,
    "biorempp_upload_operations_total",
    "Total upload/example operations by source and status",
    ["source", "status"],
)

UPLOAD_SIZE_BYTES = _metric(
    Histogram,
    "biorempp_upload_size_bytes",
    "Upload payload size in bytes by source and status",
    ["source", "status"],
    buckets=SIZE_BUCKETS,
)

PROCESSING_DURATION_SECONDS = _metric(
    Histogram,
    "biorempp_processing_duration_seconds",
    "End-to-end processing callback duration in seconds",
    ["outcome"],
    buckets=PROCESSING_DURATION_BUCKETS,
)

RESUME_PERSIST_DURATION_SECONDS = _metric(
    Histogram,
    "biorempp_resume_persist_duration_seconds",
    "Resume payload persistence duration in seconds",
    ["outcome"],
    buckets=(
        0.001,
        0.005,
        0.01,
        0.025,
        0.05,
        0.1,
        0.25,
        0.5,
        1.0,
        2.5,
        5.0,
    ),
)

RESUME_PERSIST_STAGE_TOTAL = _metric(
    Counter,
    "biorempp_resume_persist_stage_total",
    "Resume persistence wrapper outcomes by execution stage",
    ["stage"],
)

RESULTS_TRANSITION_SAMPLES_TOTAL = _metric(
    Counter,
    "biorempp_results_transition_samples_total",
    "Total results transition client telemetry samples by outcome",
    ["outcome"],
)

RESULTS_TRANSITION_CLICK_TO_REQUEST_SECONDS = _metric(
    Histogram,
    "biorempp_results_transition_click_to_request_seconds",
    "Client-side time from clicking view results to first Dash request start",
    ["route"],
    buckets=RESULTS_TRANSITION_DURATION_BUCKETS,
)

RESULTS_TRANSITION_REQUEST_TO_PAINT_SECONDS = _metric(
    Histogram,
    "biorempp_results_transition_request_to_paint_seconds",
    "Client-side time from first Dash request start to final paint",
    ["route"],
    buckets=RESULTS_TRANSITION_DURATION_BUCKETS,
)

RESULTS_TRANSITION_CLICK_TO_PAINT_SECONDS = _metric(
    Histogram,
    "biorempp_results_transition_click_to_paint_seconds",
    "Client-side time from click to final paint",
    ["route"],
    buckets=RESULTS_TRANSITION_DURATION_BUCKETS,
)

RESULTS_TRANSITION_REQUEST_BYTES = _metric(
    Histogram,
    "biorempp_results_transition_request_bytes",
    "Client-observed request payload size in bytes for results transition",
    ["route"],
    buckets=SIZE_BUCKETS,
)

RESULTS_TRANSITION_RESPONSE_BYTES = _metric(
    Histogram,
    "biorempp_results_transition_response_bytes",
    "Client-observed response size in bytes for results transition",
    ["route"],
    buckets=SIZE_BUCKETS,
)

# Worker metrics
WORKERS_ACTIVE = _metric(
    Gauge,
    "biorempp_workers_active",
    "Number of active Gunicorn worker processes",
    multiprocess_mode="livesum",
)

WORKER_REQUESTS_TOTAL = _metric(
    Counter,
    "biorempp_worker_requests_total",
    "Total requests handled by worker processes",
)

WORKER_MEMORY_BYTES = _metric(
    Gauge,
    "biorempp_worker_memory_bytes",
    "Resident memory size in bytes for live worker processes",
    multiprocess_mode="liveall",
)

WORKER_RESTARTS_TOTAL = _metric(
    Counter,
    "biorempp_worker_restarts_total",
    "Total worker restarts by reason",
    ["reason"],
)


__all__ = [
    "HTTP_REQUESTS_TOTAL",
    "HTTP_ERRORS_TOTAL",
    "HTTP_REQUEST_DURATION_SECONDS",
    "HTTP_REQUEST_SIZE_BYTES",
    "HTTP_RESPONSE_SIZE_BYTES",
    "CALLBACK_DURATION_SECONDS",
    "CALLBACK_ERRORS_TOTAL",
    "DASH_CALLBACK_SERVER_DURATION_SECONDS",
    "DASH_CALLBACK_REQUEST_SIZE_BYTES",
    "DASH_CALLBACK_RESPONSE_SIZE_BYTES",
    "CACHE_OPERATIONS_TOTAL",
    "CACHE_SIZE_ITEMS",
    "CACHE_HIT_RATIO",
    "CACHE_ENTRY_SIZE_BYTES",
    "RESUME_LOAD_ATTEMPTS_TOTAL",
    "RESUME_SAVE_TOTAL",
    "RESUME_PAYLOAD_SIZE_BYTES",
    "RESUME_OPERATION_DURATION_SECONDS",
    "RESUME_CALLBACK_ATTEMPTS_TOTAL",
    "RESUME_RATE_LIMIT_BACKEND_INFO",
    "RESUME_RATE_LIMIT_ERRORS_TOTAL",
    "RESUME_REQUEST_IP_SOURCE_TOTAL",
    "UPLOAD_OPERATIONS_TOTAL",
    "UPLOAD_SIZE_BYTES",
    "PROCESSING_DURATION_SECONDS",
    "RESUME_PERSIST_DURATION_SECONDS",
    "RESUME_PERSIST_STAGE_TOTAL",
    "RESULTS_TRANSITION_SAMPLES_TOTAL",
    "RESULTS_TRANSITION_CLICK_TO_REQUEST_SECONDS",
    "RESULTS_TRANSITION_REQUEST_TO_PAINT_SECONDS",
    "RESULTS_TRANSITION_CLICK_TO_PAINT_SECONDS",
    "RESULTS_TRANSITION_REQUEST_BYTES",
    "RESULTS_TRANSITION_RESPONSE_BYTES",
    "WORKERS_ACTIVE",
    "WORKER_REQUESTS_TOTAL",
    "WORKER_MEMORY_BYTES",
    "WORKER_RESTARTS_TOTAL",
]
