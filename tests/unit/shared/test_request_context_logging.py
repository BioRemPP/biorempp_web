"""Unit tests for request and trace logging context integration."""

from __future__ import annotations

import logging

from src.shared.logging.handlers import RequestContextFilter
from src.shared.logging.request_context import (
    clear_request_id,
    clear_trace_id,
    set_request_id,
    set_trace_id,
)


def test_request_context_filter_injects_request_and_trace_id() -> None:
    set_request_id("req-abc12345")
    set_trace_id("1234567890abcdef1234567890abcdef")
    record = logging.LogRecord(
        name="test.logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="hello",
        args=(),
        exc_info=None,
    )
    try:
        assert RequestContextFilter().filter(record) is True
        assert getattr(record, "request_id", None) == "req-abc12345"
        assert getattr(record, "trace_id", None) == "1234567890abcdef1234567890abcdef"
    finally:
        clear_request_id()
        clear_trace_id()
