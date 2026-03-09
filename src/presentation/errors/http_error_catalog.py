"""Centralized HTTP error specifications and payload builders."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HttpErrorSpec:
    """Single source of truth for HTTP error content."""

    status_code: int
    title: str
    message: str
    guidance: str
    json_message: str
    slug: str


HTTP_ERROR_SPECS: dict[int, HttpErrorSpec] = {
    400: HttpErrorSpec(
        status_code=400,
        title="Bad Request",
        message=(
            "We could not process this request because the submitted data "
            "or parameters are invalid."
        ),
        guidance=(
            "Please review your input and try again. If the issue persists, "
            "contact support."
        ),
        json_message="Bad Request",
        slug="bad-request",
    ),
    500: HttpErrorSpec(
        status_code=500,
        title="Internal Server Error",
        message="An unexpected error occurred while processing your request.",
        guidance=(
            "Please try again in a few moments. If the problem continues, "
            "contact support and share the request time."
        ),
        json_message="Internal Server Error",
        slug="internal-server-error",
    ),
}

FILE_NOT_FOUND_PAYLOAD: dict[str, str] = {"error": "File not found"}


def get_http_error_spec(status_code: int) -> HttpErrorSpec:
    """Return registered error spec for a given HTTP status code."""
    try:
        return HTTP_ERROR_SPECS[status_code]
    except KeyError as exc:
        raise ValueError(f"Unsupported HTTP error status code: {status_code}") from exc


def build_json_error_payload(status_code: int) -> dict[str, object]:
    """Build stable JSON payload for Dash/internal API clients."""
    spec = get_http_error_spec(status_code)
    return {
        "status": "error",
        "code": spec.status_code,
        "message": spec.json_message,
    }

