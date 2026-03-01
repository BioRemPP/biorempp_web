"""Unit tests for callback-level metrics instrumentation helpers."""

from __future__ import annotations

import pytest

from src.shared.metrics import instrument_callback
from src.shared.metrics.registry import CALLBACK_DURATION_SECONDS, CALLBACK_ERRORS_TOTAL


def _counter_value(counter, **labels) -> float:
    return float(counter.labels(**labels)._value.get())


def _histogram_count(histogram, **labels) -> float:
    expected_labels = {key: str(value) for key, value in labels.items()}
    sample_name = f"{histogram._name}_count"
    for metric in histogram.collect():
        for sample in metric.samples:
            if sample.name == sample_name and sample.labels == expected_labels:
                return float(sample.value)
    return 0.0


def test_instrument_callback_records_duration_on_success() -> None:
    callback_id = "unit.success_callback"
    before_count = _histogram_count(CALLBACK_DURATION_SECONDS, callback_id=callback_id)

    @instrument_callback(callback_id)
    def _callback_ok(value: int) -> int:
        return value + 1

    assert _callback_ok(10) == 11

    after_count = _histogram_count(CALLBACK_DURATION_SECONDS, callback_id=callback_id)
    assert after_count == before_count + 1.0


def test_instrument_callback_records_error_and_duration_on_exception() -> None:
    callback_id = "unit.error_callback"
    before_duration = _histogram_count(
        CALLBACK_DURATION_SECONDS,
        callback_id=callback_id,
    )
    before_errors = _counter_value(
        CALLBACK_ERRORS_TOTAL,
        callback_id=callback_id,
        error_type="RuntimeError",
    )

    @instrument_callback(callback_id)
    def _callback_error() -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        _callback_error()

    after_duration = _histogram_count(
        CALLBACK_DURATION_SECONDS,
        callback_id=callback_id,
    )
    after_errors = _counter_value(
        CALLBACK_ERRORS_TOTAL,
        callback_id=callback_id,
        error_type="RuntimeError",
    )
    assert after_duration == before_duration + 1.0
    assert after_errors == before_errors + 1.0

