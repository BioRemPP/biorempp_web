"""HTTP error catalog and Flask handler registration for presentation layer."""

from .http_error_catalog import (
    FILE_NOT_FOUND_PAYLOAD,
    HTTP_ERROR_SPECS,
    HttpErrorSpec,
    build_json_error_payload,
    get_http_error_spec,
)
from .http_error_handlers import register_http_error_handlers

__all__ = [
    "HttpErrorSpec",
    "HTTP_ERROR_SPECS",
    "FILE_NOT_FOUND_PAYLOAD",
    "get_http_error_spec",
    "build_json_error_payload",
    "register_http_error_handlers",
]

