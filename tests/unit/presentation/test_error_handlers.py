"""Tests for Flask error handlers integrated in biorempp_app."""

from __future__ import annotations

from flask import abort

import biorempp_app


def _build_test_client(monkeypatch):
    """Create a test client with explicit test routes for 400/500 paths."""
    monkeypatch.setattr(biorempp_app.settings, "URL_BASE_PATH", "/")

    app = biorempp_app.create_app(force_initialize=True)
    server = app.server
    server.config["TESTING"] = False
    server.config["PROPAGATE_EXCEPTIONS"] = False

    if "__test_error_400" not in server.view_functions:
        @server.route("/__test_error_400")
        def __test_error_400():  # pragma: no cover - exercised by requests
            abort(400)

    if "__test_error_500" not in server.view_functions:
        @server.route("/__test_error_500")
        def __test_error_500():  # pragma: no cover - exercised by requests
            raise RuntimeError("forced test failure")

    if "__test_dash_error_500" not in server.view_functions:
        @server.route("/_dash-test-error")
        def __test_dash_error_500():  # pragma: no cover - exercised by requests
            raise RuntimeError("forced dash-like failure")

    return server.test_client()


def test_bad_request_html_returns_400_page(monkeypatch):
    """Browser requests should receive HTML body with real 400 status."""
    client = _build_test_client(monkeypatch)

    response = client.get("/__test_error_400", headers={"Accept": "text/html"})

    body = response.get_data(as_text=True)
    assert response.status_code == 400
    assert "text/html" in (response.content_type or "")
    assert "Bad Request" in body
    assert "Back to Home" in body


def test_internal_error_html_returns_500_page(monkeypatch):
    """Browser requests should receive HTML body with real 500 status."""
    client = _build_test_client(monkeypatch)

    response = client.get("/__test_error_500", headers={"Accept": "text/html"})

    body = response.get_data(as_text=True)
    assert response.status_code == 500
    assert "text/html" in (response.content_type or "")
    assert "Internal Server Error" in body
    assert "Contact Support" in body


def test_bad_request_json_returns_minimal_payload(monkeypatch):
    """JSON clients should receive protocol-safe compact JSON errors."""
    client = _build_test_client(monkeypatch)

    response = client.get(
        "/__test_error_400",
        headers={"Accept": "application/json"},
    )

    assert response.status_code == 400
    assert response.get_json() == {
        "status": "error",
        "code": 400,
        "message": "Bad Request",
    }


def test_dash_like_path_keeps_json_error_response(monkeypatch):
    """Dash-prefixed paths should keep JSON responses even with HTML accept."""
    client = _build_test_client(monkeypatch)

    response = client.get("/_dash-test-error", headers={"Accept": "text/html"})

    assert response.status_code == 500
    assert response.get_json() == {
        "status": "error",
        "code": 500,
        "message": "Internal Server Error",
    }
