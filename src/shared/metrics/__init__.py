"""
Observability setup utilities and metrics exports.
"""

from __future__ import annotations

import os
from typing import Any

from flask import Flask, Response
from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, generate_latest

from .middleware import register_metrics_middleware
from .registry import *  # noqa: F401,F403
from .registry import __all__ as _registry_exports

_STATE_KEY = "biorempp_observability"
_SETUP_FLAG = "setup_completed"
_ENDPOINT_FLAG = "metrics_endpoint_registered"
_METRICS_ENDPOINT_NAME = "biorempp_prometheus_metrics"


def _canonical_metrics_path(metrics_path: str) -> str:
    """Normalize metrics path to a canonical Flask route."""
    path = (metrics_path or "/metrics").strip()
    if not path:
        path = "/metrics"
    if not path.startswith("/"):
        path = f"/{path}"
    if len(path) > 1:
        path = path.rstrip("/")
    return path


def _resolve_flask_server(app_or_server: Any) -> Flask:
    """Support Dash app instances and raw Flask apps."""
    return app_or_server.server if hasattr(app_or_server, "server") else app_or_server


def _get_state(flask_app: Flask) -> dict:
    """Return mutable observability state for this Flask app."""
    return flask_app.extensions.setdefault(_STATE_KEY, {})


def register_metrics_endpoint(
    app_or_server: Any,
    metrics_path: str = "/metrics",
) -> None:
    """Register Prometheus `/metrics` endpoint (idempotent)."""
    flask_app = _resolve_flask_server(app_or_server)
    state = _get_state(flask_app)
    if state.get(_ENDPOINT_FLAG):
        return

    normalized_path = _canonical_metrics_path(metrics_path)
    if _METRICS_ENDPOINT_NAME in flask_app.view_functions:
        state[_ENDPOINT_FLAG] = True
        state["metrics_path"] = normalized_path
        return

    def _metrics_handler() -> Response:
        multiproc_dir = os.getenv("PROMETHEUS_MULTIPROC_DIR")
        if multiproc_dir:
            from prometheus_client import CollectorRegistry, multiprocess

            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)
            payload = generate_latest(registry)
        else:
            payload = generate_latest(REGISTRY)
        return Response(payload, mimetype=CONTENT_TYPE_LATEST)

    flask_app.add_url_rule(
        normalized_path,
        endpoint=_METRICS_ENDPOINT_NAME,
        view_func=_metrics_handler,
        methods=["GET"],
    )
    state[_ENDPOINT_FLAG] = True
    state["metrics_path"] = normalized_path


def setup_observability(
    app_or_server: Any,
    metrics_path: str = "/metrics",
) -> None:
    """Setup middleware and metrics endpoint once per app instance."""
    flask_app = _resolve_flask_server(app_or_server)
    state = _get_state(flask_app)
    if state.get(_SETUP_FLAG):
        return

    normalized_path = _canonical_metrics_path(metrics_path)
    register_metrics_middleware(flask_app, metrics_path=normalized_path)
    register_metrics_endpoint(flask_app, metrics_path=normalized_path)
    state[_SETUP_FLAG] = True


__all__ = [
    "register_metrics_endpoint",
    "register_metrics_middleware",
    "setup_observability",
] + _registry_exports
