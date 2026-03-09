#!/usr/bin/env python
"""Smoke test for Phase 0 /results transition observability pipeline."""

from __future__ import annotations

import argparse
import re
from typing import Any

import requests

ACCEPTED_COUNTER_PATTERN = re.compile(
    r'^biorempp_results_transition_samples_total\{[^}]*outcome="accepted"[^}]*\}\s+'
    r"(?P<value>[0-9eE+\-\.]+)$"
)
INVALID_COUNTER_PATTERN = re.compile(
    r'^biorempp_results_transition_samples_total\{[^}]*outcome="invalid"[^}]*\}\s+'
    r"(?P<value>[0-9eE+\-\.]+)$"
)


def _counter_value(metrics_text: str, pattern: re.Pattern[str]) -> float:
    """Extract counter value from Prometheus exposition text."""
    for line in metrics_text.splitlines():
        match = pattern.match(line.strip())
        if match:
            try:
                return float(match.group("value"))
            except ValueError:
                return 0.0
    return 0.0


def _join_url(base_url: str, path: str) -> str:
    """Join base URL with absolute path."""
    return base_url.rstrip("/") + path


def _print_result(name: str, ok: bool, detail: str) -> None:
    """Consistent smoke test line output."""
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}: {detail}")


def main() -> None:
    """Run smoke checks for local Phase 0 instrumentation."""
    parser = argparse.ArgumentParser(
        description="Smoke test for /results phase 0 telemetry + metrics."
    )
    parser.add_argument(
        "--base-url",
        default="http://127.0.0.1:8050",
        help="Application base URL.",
    )
    parser.add_argument(
        "--health-path",
        default="/health",
        help="Health endpoint path.",
    )
    parser.add_argument(
        "--metrics-path",
        default="/metrics",
        help="Metrics endpoint path.",
    )
    parser.add_argument(
        "--telemetry-path",
        default="/perf/results-transition",
        help="Telemetry endpoint path.",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=float,
        default=5.0,
        help="HTTP timeout in seconds.",
    )
    args = parser.parse_args()

    health_url = _join_url(args.base_url, args.health_path)
    metrics_url = _join_url(args.base_url, args.metrics_path)
    telemetry_url = _join_url(args.base_url, args.telemetry_path)

    print("Phase 0 smoke test")
    print(f"- base_url: {args.base_url}")
    print(f"- health_url: {health_url}")
    print(f"- metrics_url: {metrics_url}")
    print(f"- telemetry_url: {telemetry_url}")
    print("")

    # 1) Health endpoint
    health_response = requests.get(health_url, timeout=args.timeout_seconds)
    health_ok = health_response.status_code == 200
    _print_result("health", health_ok, f"status={health_response.status_code}")
    if not health_ok:
        raise SystemExit(1)

    # 2) Metrics endpoint before telemetry
    metrics_before_response = requests.get(metrics_url, timeout=args.timeout_seconds)
    metrics_before_ok = metrics_before_response.status_code == 200
    _print_result(
        "metrics_available",
        metrics_before_ok,
        f"status={metrics_before_response.status_code}",
    )
    if not metrics_before_ok:
        raise SystemExit(1)

    metrics_before_text = metrics_before_response.text
    accepted_before = _counter_value(metrics_before_text, ACCEPTED_COUNTER_PATTERN)
    invalid_before = _counter_value(metrics_before_text, INVALID_COUNTER_PATTERN)
    _print_result(
        "metrics_counter_read",
        True,
        f"accepted={accepted_before:.0f}, invalid={invalid_before:.0f}",
    )

    # 3) Telemetry ingestion endpoint
    payload: dict[str, Any] = {
        "route": "/results",
        "click_to_request_seconds": 0.1,
        "request_to_paint_seconds": 1.2,
        "click_to_paint_seconds": 1.3,
        "request_bytes": 1024,
        "response_bytes": 2048,
        "dash_output": "page-content.children",
        "session_id": "phase0-smoke",
        "job_id": "phase0-smoke-job",
        "client_time_utc": "2026-03-04T00:00:00.000Z",
    }
    telemetry_response = requests.post(
        telemetry_url,
        json=payload,
        timeout=args.timeout_seconds,
    )
    telemetry_ok = telemetry_response.status_code in (200, 202)
    _print_result(
        "telemetry_ingest",
        telemetry_ok,
        f"status={telemetry_response.status_code}",
    )
    if not telemetry_ok:
        raise SystemExit(1)

    # 4) Metrics endpoint after telemetry
    metrics_after_response = requests.get(metrics_url, timeout=args.timeout_seconds)
    metrics_after_ok = metrics_after_response.status_code == 200
    _print_result(
        "metrics_after_ingest",
        metrics_after_ok,
        f"status={metrics_after_response.status_code}",
    )
    if not metrics_after_ok:
        raise SystemExit(1)

    metrics_after_text = metrics_after_response.text
    accepted_after = _counter_value(metrics_after_text, ACCEPTED_COUNTER_PATTERN)
    accepted_increment_ok = accepted_after >= (accepted_before + 1.0)
    _print_result(
        "accepted_counter_increment",
        accepted_increment_ok,
        f"before={accepted_before:.0f}, after={accepted_after:.0f}",
    )
    if not accepted_increment_ok:
        raise SystemExit(1)

    print("")
    print("Phase 0 smoke test completed successfully.")


if __name__ == "__main__":
    main()
