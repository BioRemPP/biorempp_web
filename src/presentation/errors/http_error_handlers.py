"""Flask error handlers for browser and Dash/internal JSON requests."""

from __future__ import annotations

import html as html_std
import logging

import dash
from flask import jsonify, request

from src.presentation.routing import app_path, strip_base_path
from src.shared.logging import get_request_id, get_trace_id

from .http_error_catalog import build_json_error_payload, get_http_error_spec

logger = logging.getLogger(__name__)


def _normalized_request_path() -> str:
    """Normalize request path for internal checks (base-path aware)."""
    raw_path = request.path or "/"
    try:
        return strip_base_path(raw_path)
    except Exception:
        return raw_path


def _is_dash_or_json_request() -> bool:
    """
    Return True for Dash internal/JSON requests.

    Dash callback protocol expects JSON payloads. Returning HTML here can
    break client behavior, so these requests receive compact JSON errors.
    """
    normalized_path = _normalized_request_path()
    if normalized_path.startswith("/_dash-"):
        return True

    if request.is_json:
        return True

    accept_header = (request.headers.get("Accept") or "").lower()
    content_type = (request.headers.get("Content-Type") or "").lower()
    return (
        "application/json" in accept_header
        or "application/json" in content_type
    )


def _build_error_log_context(status_code: int, path: str) -> dict:
    """Build structured, non-sensitive error context for operational logs."""
    return {
        "status_code": status_code,
        "path": path,
        "method": request.method,
        "request_id": get_request_id(),
        "trace_id": get_trace_id(),
    }


def _build_error_html_response(*, status_code: int, title: str, message: str, guidance: str):
    """
    Build HTML error response for browser requests.

    This keeps real HTTP status codes (400/500) so observability counters
    reflect browser-visible errors.
    """
    home_href = app_path("/")
    contact_href = app_path("/help/contact")
    logo_src = app_path("/assets/HAZARD_LOGO.png")
    status_text = html_std.escape(str(status_code))
    title_text = html_std.escape(title)
    message_text = html_std.escape(message)
    guidance_text = html_std.escape(guidance)

    html_body = f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{status_text} - {title_text}</title>
    <style>
      body {{
        margin: 0;
        font-family: "Segoe UI", Tahoma, sans-serif;
        background: #f8f9fa;
        color: #2d3e50;
      }}
      .container {{
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 24px;
      }}
      .card {{
        width: min(760px, 100%);
        background: #ffffff;
        border: 1px solid #e6e9ee;
        border-top: 5px solid #f0ad4e;
        border-radius: 10px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.06);
        padding: 28px 24px;
        text-align: center;
      }}
      .logo {{
        width: 120px;
        height: auto;
        margin-bottom: 12px;
      }}
      .code {{
        font-size: 2.2rem;
        font-weight: 700;
        color: #f0ad4e;
        margin: 4px 0 8px 0;
      }}
      .title {{
        font-size: 1.6rem;
        margin: 0 0 10px 0;
      }}
      .message {{
        margin: 0 0 8px 0;
      }}
      .guidance {{
        margin: 0 0 18px 0;
        color: #5f6f82;
      }}
      .actions {{
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
      }}
      .btn {{
        display: inline-block;
        padding: 10px 18px;
        border-radius: 8px;
        text-decoration: none;
        font-weight: 600;
      }}
      .btn-home {{
        background: #5ec7a4;
        color: #fff;
      }}
      .btn-contact {{
        background: #6c757d;
        color: #fff;
      }}
    </style>
  </head>
  <body>
    <main class="container">
      <section class="card">
        <img class="logo" src="{logo_src}" alt="Hazard Warning" />
        <div class="code">{status_text}</div>
        <h1 class="title">{title_text}</h1>
        <p class="message">{message_text}</p>
        <p class="guidance">{guidance_text}</p>
        <div class="actions">
          <a class="btn btn-home" href="{home_href}">Back to Home</a>
          <a class="btn btn-contact" href="{contact_href}">Contact Support</a>
        </div>
      </section>
    </main>
  </body>
</html>
"""
    return html_body, status_code, {"Content-Type": "text/html; charset=utf-8"}


def register_http_error_handlers(app: dash.Dash) -> None:
    """Register centralized Flask error handlers on the Dash server."""

    @app.server.errorhandler(400)
    def handle_bad_request(error):
        """
        Handle HTTP 400 with Dash-compatible JSON fallback.

        Browser requests receive an HTML error body with real HTTP status.
        """
        spec = get_http_error_spec(400)
        normalized_path = _normalized_request_path()
        logger.warning(
            f"HTTP {spec.status_code} {spec.title}",
            extra=_build_error_log_context(spec.status_code, normalized_path),
        )

        if _is_dash_or_json_request():
            return jsonify(build_json_error_payload(spec.status_code)), spec.status_code

        return _build_error_html_response(
            status_code=spec.status_code,
            title=spec.title,
            message=spec.message,
            guidance=spec.guidance,
        )

    @app.server.errorhandler(500)
    def handle_internal_server_error(error):
        """
        Handle HTTP 500 with generic response and Dash compatibility.

        No stack trace details are exposed to clients.
        """
        spec = get_http_error_spec(500)
        normalized_path = _normalized_request_path()
        logger.error(
            f"HTTP {spec.status_code} {spec.title}",
            extra=_build_error_log_context(spec.status_code, normalized_path),
            exc_info=True,
        )

        if _is_dash_or_json_request():
            return jsonify(build_json_error_payload(spec.status_code)), spec.status_code

        return _build_error_html_response(
            status_code=spec.status_code,
            title=spec.title,
            message=spec.message,
            guidance=spec.guidance,
        )

