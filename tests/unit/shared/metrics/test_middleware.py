"""Unit tests for HTTP observability middleware."""

import re

from flask import Flask, jsonify

from src.shared.metrics.middleware import (
    _is_excluded_endpoint,
    _normalize_endpoint,
    register_metrics_middleware,
)
from src.shared.metrics.registry import (
    HTTP_ERRORS_TOTAL,
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
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


def _http_requests_total_sum() -> float:
    total = 0.0
    for metric in HTTP_REQUESTS_TOTAL.collect():
        for sample in metric.samples:
            if sample.name == "biorempp_http_requests_total":
                total += float(sample.value)
    return total


def _build_test_app() -> Flask:
    app = Flask(__name__)
    register_metrics_middleware(app)

    @app.get("/schemas/biorempp")
    def schema_route():
        return jsonify({"ok": True}), 200

    @app.get("/_dash-layout")
    def dash_internal_route():
        return jsonify({"layout": "ok"}), 200

    @app.get("/health")
    def health_route():
        return jsonify({"status": "healthy"}), 200

    @app.get("/error-400")
    def error_400_route():
        return "<h1>bad request</h1>", 400

    @app.get("/error-500")
    def error_500_route():
        return "<h1>internal error</h1>", 500

    return app


def test_normalize_endpoint_collapses_dynamic_routes() -> None:
    assert _normalize_endpoint("/schemas/biorempp") == "/schemas/<db>"
    assert _normalize_endpoint("/data/example.txt") == "/data/<filename>"
    assert _normalize_endpoint("/_dash-update-component") == "/_dash-internal"
    assert _normalize_endpoint("/results") == "/results"


def test_excluded_endpoint_contains_health_ready_and_metrics() -> None:
    assert _is_excluded_endpoint("/health", "/metrics")
    assert _is_excluded_endpoint("/ready", "/metrics")
    assert _is_excluded_endpoint("/metrics", "/metrics")
    assert not _is_excluded_endpoint("/results", "/metrics")


def test_middleware_tracks_normalized_http_metrics() -> None:
    app = _build_test_app()
    client = app.test_client()

    counter_before = _counter_value(
        HTTP_REQUESTS_TOTAL,
        method="GET",
        endpoint="/schemas/<db>",
        status_code="200",
    )
    duration_count_before = _histogram_count(
        HTTP_REQUEST_DURATION_SECONDS,
        method="GET",
        endpoint="/schemas/<db>",
    )

    response = client.get("/schemas/biorempp")
    assert response.status_code == 200

    counter_after = _counter_value(
        HTTP_REQUESTS_TOTAL,
        method="GET",
        endpoint="/schemas/<db>",
        status_code="200",
    )
    duration_count_after = _histogram_count(
        HTTP_REQUEST_DURATION_SECONDS,
        method="GET",
        endpoint="/schemas/<db>",
    )

    assert counter_after == counter_before + 1.0
    assert duration_count_after == duration_count_before + 1.0


def test_middleware_collapses_dash_internal_endpoints() -> None:
    app = _build_test_app()
    client = app.test_client()

    counter_before = _counter_value(
        HTTP_REQUESTS_TOTAL,
        method="GET",
        endpoint="/_dash-internal",
        status_code="200",
    )

    response = client.get("/_dash-layout")
    assert response.status_code == 200

    counter_after = _counter_value(
        HTTP_REQUESTS_TOTAL,
        method="GET",
        endpoint="/_dash-internal",
        status_code="200",
    )
    assert counter_after == counter_before + 1.0


def test_middleware_skips_health_endpoint() -> None:
    app = _build_test_app()
    client = app.test_client()

    total_before = _http_requests_total_sum()
    response = client.get("/health")
    assert response.status_code == 200
    total_after = _http_requests_total_sum()

    assert total_after == total_before


def test_middleware_sets_request_id_response_header() -> None:
    app = _build_test_app()
    client = app.test_client()

    response = client.get("/schemas/biorempp")
    request_id = response.headers.get("X-Request-ID")

    assert response.status_code == 200
    assert isinstance(request_id, str)
    assert bool(re.fullmatch(r"[a-f0-9]{32}", request_id))


def test_middleware_preserves_valid_incoming_request_id() -> None:
    app = _build_test_app()
    client = app.test_client()

    incoming_request_id = "req-abc12345"
    response = client.get(
        "/schemas/biorempp",
        headers={"X-Request-ID": incoming_request_id},
    )

    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == incoming_request_id


def test_middleware_sets_trace_id_when_missing() -> None:
    app = _build_test_app()
    client = app.test_client()

    response = client.get("/schemas/biorempp")
    trace_id = response.headers.get("X-Trace-ID")

    assert response.status_code == 200
    assert isinstance(trace_id, str)
    assert bool(re.fullmatch(r"[a-f0-9]{32}", trace_id))


def test_middleware_counts_html_error_responses() -> None:
    app = _build_test_app()
    client = app.test_client()

    err400_before = _counter_value(
        HTTP_ERRORS_TOTAL,
        method="GET",
        endpoint="/error-400",
        status_code="400",
    )
    err500_before = _counter_value(
        HTTP_ERRORS_TOTAL,
        method="GET",
        endpoint="/error-500",
        status_code="500",
    )

    response_400 = client.get("/error-400", headers={"Accept": "text/html"})
    response_500 = client.get("/error-500", headers={"Accept": "text/html"})

    assert response_400.status_code == 400
    assert response_500.status_code == 500

    err400_after = _counter_value(
        HTTP_ERRORS_TOTAL,
        method="GET",
        endpoint="/error-400",
        status_code="400",
    )
    err500_after = _counter_value(
        HTTP_ERRORS_TOTAL,
        method="GET",
        endpoint="/error-500",
        status_code="500",
    )

    assert err400_after == err400_before + 1.0
    assert err500_after == err500_before + 1.0


def test_middleware_extracts_trace_id_from_traceparent() -> None:
    app = _build_test_app()
    client = app.test_client()

    trace_id = "4bf92f3577b34da6a3ce929d0e0e4736"
    traceparent = f"00-{trace_id}-00f067aa0ba902b7-01"
    response = client.get(
        "/schemas/biorempp",
        headers={"traceparent": traceparent},
    )

    assert response.status_code == 200
    assert response.headers.get("X-Trace-ID") == trace_id
