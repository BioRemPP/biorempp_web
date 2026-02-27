"""Helpers for Dash callback-level observability metrics."""

from __future__ import annotations

import re
import time
from functools import wraps

from .registry import CALLBACK_DURATION_SECONDS, CALLBACK_ERRORS_TOTAL

_CALLBACK_ID_SAFE_PATTERN = re.compile(r"[^a-zA-Z0-9_:.:-]+")


def _normalize_callback_id(callback_id: str) -> str:
    """Normalize callback id to a low-cardinality metric label."""
    raw_value = (callback_id or "").strip()
    if not raw_value:
        return "unknown_callback"
    normalized = _CALLBACK_ID_SAFE_PATTERN.sub("_", raw_value)
    return normalized[:96] or "unknown_callback"


def instrument_callback(callback_id: str):
    """
    Decorate callback function with duration/error metrics.

    Parameters
    ----------
    callback_id : str
        Stable callback identifier used as metric label.
    """

    normalized_id = _normalize_callback_id(callback_id)

    def _decorator(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            started_at = time.perf_counter()
            try:
                result = func(*args, **kwargs)
                CALLBACK_DURATION_SECONDS.labels(callback_id=normalized_id).observe(
                    max(time.perf_counter() - started_at, 0.0)
                )
                return result
            except Exception as exc:
                CALLBACK_ERRORS_TOTAL.labels(
                    callback_id=normalized_id,
                    error_type=type(exc).__name__,
                ).inc()
                CALLBACK_DURATION_SECONDS.labels(callback_id=normalized_id).observe(
                    max(time.perf_counter() - started_at, 0.0)
                )
                raise

        return _wrapped

    return _decorator

