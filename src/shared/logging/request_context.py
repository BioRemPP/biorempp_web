"""Request-scoped logging context helpers."""

from __future__ import annotations

import re
from contextvars import ContextVar
from uuid import uuid4

_REQUEST_ID_VAR: ContextVar[str | None] = ContextVar(
    "biorempp_request_id",
    default=None,
)
_REQUEST_ID_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
_FALLBACK_REQUEST_ID = "-"


def sanitize_incoming_request_id(raw_value: str) -> str:
    """Validate and normalize incoming request id header values."""
    candidate = (raw_value or "").strip()
    if not candidate:
        return ""
    if not _REQUEST_ID_SAFE_PATTERN.fullmatch(candidate):
        return ""
    return candidate


def generate_request_id() -> str:
    """Generate non-sensitive opaque request identifier."""
    return uuid4().hex


def get_request_id(default: str = _FALLBACK_REQUEST_ID) -> str:
    """Get active request id from context."""
    current = _REQUEST_ID_VAR.get()
    if isinstance(current, str) and current.strip():
        return current.strip()
    return default


def set_request_id(request_id: str) -> None:
    """Set request id for the current execution context."""
    candidate = (request_id or "").strip()
    _REQUEST_ID_VAR.set(candidate or None)


def clear_request_id() -> None:
    """Clear request id from current execution context."""
    _REQUEST_ID_VAR.set(None)

