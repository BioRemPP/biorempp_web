"""Tests for centralized HTTP error catalog consistency."""

from __future__ import annotations

from flask import abort

import biorempp_app
from src.presentation.errors.http_error_catalog import (
    HTTP_ERROR_SPECS,
    build_json_error_payload,
    get_http_error_spec,
)
from src.presentation.pages.error_pages import create_error_400_page, create_error_500_page


def _collect_text(node) -> list[str]:
    """Recursively collect text children from Dash component trees."""
    if node is None:
        return []
    if isinstance(node, str):
        return [node]
    if isinstance(node, (list, tuple)):
        text: list[str] = []
        for child in node:
            text.extend(_collect_text(child))
        return text
    return _collect_text(getattr(node, "children", None))


def _build_test_client(monkeypatch):
    """Create test client exposing controlled 400/500 failure routes."""
    monkeypatch.setattr(biorempp_app.settings, "URL_BASE_PATH", "/")
    app = biorempp_app.create_app(force_initialize=True)
    server = app.server
    server.config["TESTING"] = False
    server.config["PROPAGATE_EXCEPTIONS"] = False

    if "__catalog_error_400" not in server.view_functions:
        @server.route("/__catalog_error_400")
        def __catalog_error_400():  # pragma: no cover - exercised by requests
            abort(400)

    if "__catalog_dash_error_500" not in server.view_functions:
        @server.route("/_dash-catalog-error-500")
        def __catalog_dash_error_500():  # pragma: no cover - exercised by requests
            raise RuntimeError("forced dash-like failure")

    return server.test_client()


def test_http_error_specs_contain_required_fields():
    """Catalog must provide complete 400/500 specs."""
    assert set(HTTP_ERROR_SPECS.keys()) == {400, 500}

    for status_code in (400, 500):
        spec = get_http_error_spec(status_code)
        assert spec.status_code == status_code
        assert spec.title
        assert spec.message
        assert spec.guidance
        assert spec.json_message
        assert spec.slug


def test_build_json_error_payload_keeps_contract():
    """JSON payload shape and values should remain backward compatible."""
    assert build_json_error_payload(400) == {
        "status": "error",
        "code": 400,
        "message": "Bad Request",
    }
    assert build_json_error_payload(500) == {
        "status": "error",
        "code": 500,
        "message": "Internal Server Error",
    }


def test_error_pages_text_matches_catalog_specs():
    """Rendered error page copy should match centralized catalog values."""
    for status_code, page_factory in (
        (400, create_error_400_page),
        (500, create_error_500_page),
    ):
        spec = get_http_error_spec(status_code)
        page = page_factory()
        text_blob = " ".join(_collect_text(page))
        assert str(spec.status_code) in text_blob
        assert spec.title in text_blob
        assert spec.message in text_blob
        assert spec.guidance in text_blob


def test_error_handlers_use_catalog_for_html_and_json(monkeypatch):
    """Flask handlers should stay aligned with catalog for both response types."""
    client = _build_test_client(monkeypatch)

    bad_request_spec = get_http_error_spec(400)
    html_response = client.get("/__catalog_error_400", headers={"Accept": "text/html"})
    html_body = html_response.get_data(as_text=True)

    assert html_response.status_code == 400
    assert bad_request_spec.title in html_body
    assert bad_request_spec.message in html_body
    assert bad_request_spec.guidance in html_body

    json_response = client.get(
        "/_dash-catalog-error-500",
        headers={"Accept": "text/html"},
    )
    assert json_response.status_code == 500
    assert json_response.get_json() == build_json_error_payload(500)

