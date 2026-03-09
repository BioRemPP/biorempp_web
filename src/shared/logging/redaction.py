"""
Utilities for safe, deterministic log references.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Tuple

from config.settings import get_settings

_DEFAULT_NAMESPACE = "ref"
_DEFAULT_LENGTH = 12
_MIN_LENGTH = 8
_MAX_LENGTH = 24
_UNKNOWN_SUFFIX = "unknown"


def _sanitize_namespace(namespace: str) -> str:
    """Normalize namespace for stable log-field prefixes."""
    candidate = (namespace or "").strip().lower()
    if not candidate:
        return _DEFAULT_NAMESPACE
    normalized = "".join(ch for ch in candidate if ch.isalnum() or ch == "_")
    return normalized[:24] or _DEFAULT_NAMESPACE


def _resolve_redaction_key_and_length() -> Tuple[str, int]:
    """
    Resolve redaction key and output length without leaking secret material.

    Falls back safely for non-initialized app contexts (e.g., isolated tests).
    """
    try:
        settings = get_settings()
        key = (settings.LOG_REF_SALT or "").strip()
        length = int(getattr(settings, "LOG_REF_LENGTH", _DEFAULT_LENGTH))
    except Exception:
        key = (os.getenv("BIOREMPP_LOG_REF_SALT") or os.getenv("SECRET_KEY") or "").strip()
        try:
            length = int(os.getenv("BIOREMPP_LOG_REF_LENGTH", str(_DEFAULT_LENGTH)))
        except (TypeError, ValueError):
            length = _DEFAULT_LENGTH

    length = min(max(length, _MIN_LENGTH), _MAX_LENGTH)
    if not key:
        key = "biorempp-log-ref-fallback"
    return key, length


def build_log_ref(value: str, namespace: str) -> str:
    """
    Build a short, non-reversible reference for logs.

    Returns `<namespace>_<hexdigest-prefix>` using HMAC-SHA256.
    """
    ns = _sanitize_namespace(namespace)
    raw_value = (value or "").strip()
    if not raw_value:
        return f"{ns}_{_UNKNOWN_SUFFIX}"

    key, length = _resolve_redaction_key_and_length()
    digest = hmac.new(
        key=key.encode("utf-8"),
        msg=raw_value.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return f"{ns}_{digest[:length]}"

