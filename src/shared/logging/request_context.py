"""Request-scoped logging context helpers."""

from __future__ import annotations

import re
from contextvars import ContextVar
from uuid import uuid4

_REQUEST_ID_VAR: ContextVar[str | None] = ContextVar(
    "biorempp_request_id",
    default=None,
)
_TRACE_ID_VAR: ContextVar[str | None] = ContextVar(
    "biorempp_trace_id",
    default=None,
)
_REQUEST_ID_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{8,128}$")
_TRACE_ID_SAFE_PATTERN = re.compile(r"^[a-f0-9]{16,32}$")
_TRACEPARENT_PATTERN = re.compile(
    r"^[\da-f]{2}-([\da-f]{32})-([\da-f]{16})-[\da-f]{2}$"
)
_FALLBACK_REQUEST_ID = "-"
_FALLBACK_TRACE_ID = "-"


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


def sanitize_trace_id(raw_value: str) -> str:
    """Validate and normalize incoming trace identifiers."""
    candidate = (raw_value or "").strip().lower()
    if not candidate:
        return ""
    if not _TRACE_ID_SAFE_PATTERN.fullmatch(candidate):
        return ""
    return candidate


def extract_trace_id_from_traceparent(raw_value: str) -> str:
    """Extract W3C trace-id from traceparent header."""
    candidate = (raw_value or "").strip().lower()
    if not candidate:
        return ""
    match = _TRACEPARENT_PATTERN.fullmatch(candidate)
    if not match:
        return ""
    trace_id = match.group(1)
    # Reject all-zero trace-id as required by W3C trace-context.
    if trace_id == "0" * 32:
        return ""
    return trace_id


def generate_trace_id() -> str:
    """Generate opaque trace identifier compatible with trace-id width."""
    return uuid4().hex


def get_request_id(default: str = _FALLBACK_REQUEST_ID) -> str:
    """Get active request id from context."""
    current = _REQUEST_ID_VAR.get()
    if isinstance(current, str) and current.strip():
        return current.strip()
    return default


def get_trace_id(default: str = _FALLBACK_TRACE_ID) -> str:
    """Get active trace id from context."""
    current = _TRACE_ID_VAR.get()
    if isinstance(current, str) and current.strip():
        return current.strip()
    return default


def set_request_id(request_id: str) -> None:
    """Set request id for the current execution context."""
    candidate = (request_id or "").strip()
    _REQUEST_ID_VAR.set(candidate or None)


def set_trace_id(trace_id: str) -> None:
    """Set trace id for the current execution context."""
    candidate = (trace_id or "").strip().lower()
    _TRACE_ID_VAR.set(candidate or None)


def clear_request_id() -> None:
    """Clear request id from current execution context."""
    _REQUEST_ID_VAR.set(None)


def clear_trace_id() -> None:
    """Clear trace id from current execution context."""
    _TRACE_ID_VAR.set(None)
