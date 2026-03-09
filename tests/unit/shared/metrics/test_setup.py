"""Unit tests for observability setup and metrics endpoint."""

import importlib

import dash
from dash import html

from src.shared.metrics import setup_observability
from src.shared.metrics import registry as metrics_registry


def _route_count(flask_app, route_path: str) -> int:
    return sum(1 for rule in flask_app.url_map.iter_rules() if rule.rule == route_path)


def test_setup_observability_exposes_metrics_endpoint(monkeypatch) -> None:
    monkeypatch.delenv("PROMETHEUS_MULTIPROC_DIR", raising=False)

    app = dash.Dash(__name__)
    app.layout = html.Div("metrics-test")
    setup_observability(app)

    client = app.server.test_client()
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "biorempp_http_requests_total" in response.get_data(as_text=True)


def test_setup_observability_is_idempotent(monkeypatch) -> None:
    monkeypatch.delenv("PROMETHEUS_MULTIPROC_DIR", raising=False)

    app = dash.Dash(__name__)
    app.layout = html.Div("idempotent-test")
    flask_app = app.server

    before_before_hooks = len(flask_app.before_request_funcs.get(None, []))
    before_after_hooks = len(flask_app.after_request_funcs.get(None, []))

    setup_observability(app)
    hooks_after_first_setup = (
        len(flask_app.before_request_funcs.get(None, [])),
        len(flask_app.after_request_funcs.get(None, [])),
    )

    setup_observability(app)
    hooks_after_second_setup = (
        len(flask_app.before_request_funcs.get(None, [])),
        len(flask_app.after_request_funcs.get(None, [])),
    )

    assert hooks_after_first_setup[0] == before_before_hooks + 1
    assert hooks_after_first_setup[1] == before_after_hooks + 1
    assert hooks_after_second_setup == hooks_after_first_setup
    assert _route_count(flask_app, "/metrics") == 1

    response = flask_app.test_client().get("/metrics")
    assert response.status_code == 200


def test_registry_reload_does_not_raise_duplicated_timeseries() -> None:
    importlib.reload(metrics_registry)
