#!/usr/bin/env python
"""Unified validation report for /results optimization (phase0 + phase1 UC matrix)."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import re
import sys
from pathlib import Path
from statistics import median
from typing import Any


def _load_phase0_module() -> Any:
    """Load legacy phase0 report helpers from sibling script path."""
    module_path = Path(__file__).with_name("results_phase0_report.py")
    spec = importlib.util.spec_from_file_location("results_phase0_report", module_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load helper module: {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_phase0 = _load_phase0_module()

parse_results_samples_from_text = _phase0.parse_results_samples_from_text
parse_server_callback_samples_from_text = _phase0.parse_server_callback_samples_from_text
summarize = _phase0.summarize
extract_histogram_buckets_for_dash_output = _phase0.extract_histogram_buckets_for_dash_output
histogram_quantile = _phase0.histogram_quantile
fetch_metrics = _phase0.fetch_metrics
detect_running_container = _phase0.detect_running_container
fetch_metrics_from_container = _phase0.fetch_metrics_from_container
DEFAULT_CONTAINER_METRICS_URLS = _phase0.DEFAULT_CONTAINER_METRICS_URLS


DEFAULT_OUTPUTS = ("url.pathname", "page-content.children")
_LABEL_PAIR_RE = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"')


def now_utc_iso() -> str:
    """Return ISO-8601 UTC timestamp with second precision."""
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _summary_to_dict(values: list[float]) -> dict[str, float | int | None]:
    """Convert summarize() payload to plain dictionary."""
    result = summarize(values)
    return {
        "count": int(getattr(result, "count", 0)),
        "p50": getattr(result, "p50", None),
        "p95": getattr(result, "p95", None),
        "avg": getattr(result, "avg", None),
    }


def _load_outputs_file(outputs_file: Path | None) -> list[str]:
    """Load expected dash outputs from JSON file."""
    if outputs_file is None:
        return list(DEFAULT_OUTPUTS)
    payload = json.loads(outputs_file.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        raw = payload.get("outputs", [])
    elif isinstance(payload, list):
        raw = payload
    else:
        raw = []

    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, str):
            continue
        value = item.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _safe_float(value: Any) -> float | None:
    """Return float when possible, None otherwise."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_counter_series(
    metrics_text: str,
    metric_name: str,
) -> list[tuple[dict[str, str], float]]:
    """Parse Prometheus counter/gauge samples with labels for one metric name."""
    prefix = f"{metric_name}{{"
    samples: list[tuple[dict[str, str], float]] = []
    for raw_line in metrics_text.splitlines():
        line = raw_line.strip()
        if not line.startswith(prefix):
            continue
        if "}" not in line:
            continue
        labels_part, value_part = line.split("}", 1)
        label_blob = labels_part[len(prefix) :]
        labels = {
            match.group(1): match.group(2)
            for match in _LABEL_PAIR_RE.finditer(label_blob)
        }
        value_str = value_part.strip()
        if not value_str:
            continue
        try:
            value = float(value_str)
        except (TypeError, ValueError):
            continue
        samples.append((labels, value))
    return samples


def _collect_resume_persist_timeout_summary(metrics_text: str | None) -> dict[str, Any]:
    """Build timeout-rate and stage distribution summary for resume persistence."""
    if not metrics_text:
        return {
            "metrics_available": False,
            "has_stage_metric": False,
            "processing_total": 0.0,
            "timeout_total": 0.0,
            "timeout_rate_per_100_processings": None,
            "stage_counts": {},
            "timeout_stage_counts": {},
            "timeout_stage_distribution_pct": {},
        }

    stage_samples = _parse_counter_series(
        metrics_text,
        "biorempp_resume_persist_stage_total",
    )
    processing_samples = _parse_counter_series(
        metrics_text,
        "biorempp_processing_duration_seconds_count",
    )

    stage_counts: dict[str, float] = {}
    for labels, value in stage_samples:
        stage = labels.get("stage", "unknown")
        stage_counts[stage] = stage_counts.get(stage, 0.0) + float(value)

    timeout_stage_counts = {
        stage: count
        for stage, count in stage_counts.items()
        if stage.startswith("timed_out")
    }
    timeout_total = float(sum(timeout_stage_counts.values()))
    processing_total = float(sum(value for _, value in processing_samples))

    timeout_rate_per_100 = None
    if processing_total > 0.0:
        timeout_rate_per_100 = (timeout_total / processing_total) * 100.0

    timeout_stage_distribution_pct: dict[str, float] = {}
    if timeout_total > 0.0:
        timeout_stage_distribution_pct = {
            stage: (count / timeout_total) * 100.0
            for stage, count in timeout_stage_counts.items()
        }

    return {
        "metrics_available": True,
        "has_stage_metric": bool(stage_samples),
        "processing_total": processing_total,
        "timeout_total": timeout_total,
        "timeout_rate_per_100_processings": timeout_rate_per_100,
        "stage_counts": stage_counts,
        "timeout_stage_counts": timeout_stage_counts,
        "timeout_stage_distribution_pct": timeout_stage_distribution_pct,
    }


def _collect_transition_summary(route: str, log_text: str) -> dict[str, Any]:
    """Build transition summary from structured logs."""
    transition_samples = parse_results_samples_from_text(log_text)
    route_samples = [s for s in transition_samples if s.get("route") == route]
    server_samples = parse_server_callback_samples_from_text(log_text)

    click_to_request = [
        _safe_float(sample.get("click_to_request_seconds"))
        for sample in route_samples
    ]
    request_to_paint = [
        _safe_float(sample.get("request_to_paint_seconds"))
        for sample in route_samples
    ]
    click_to_paint = [
        _safe_float(sample.get("click_to_paint_seconds"))
        for sample in route_samples
    ]

    client_timings = {
        "click_to_request_seconds": _summary_to_dict(
            [value for value in click_to_request if value is not None]
        ),
        "request_to_paint_seconds": _summary_to_dict(
            [value for value in request_to_paint if value is not None]
        ),
        "click_to_paint_seconds": _summary_to_dict(
            [value for value in click_to_paint if value is not None]
        ),
    }

    routing_display_page = [
        _safe_float(sample.get("duration_seconds"))
        for sample in server_samples
        if sample.get("callback") == "routing.display_page"
        and sample.get("route") == route
    ]
    processing_navigate = [
        _safe_float(sample.get("duration_seconds"))
        for sample in server_samples
        if sample.get("callback") == "processing.navigate_to_results"
    ]

    server_callback_timings = {
        "routing.display_page": _summary_to_dict(
            [value for value in routing_display_page if value is not None]
        ),
        "processing.navigate_to_results": _summary_to_dict(
            [value for value in processing_navigate if value is not None]
        ),
    }

    return {
        "samples_total": len(transition_samples),
        "samples_route": len(route_samples),
        "server_callback_samples_total": len(server_samples),
        "client_timings": client_timings,
        "server_callback_timings": server_callback_timings,
    }


def _metric_summary_for_output(metrics_text: str, dash_output: str) -> dict[str, Any]:
    """Collect p50/p95 and invocation count for one dash_output label."""
    duration_buckets = extract_histogram_buckets_for_dash_output(
        metrics_text,
        metric_name="biorempp_dash_callback_server_duration_seconds",
        dash_output=dash_output,
    )
    request_buckets = extract_histogram_buckets_for_dash_output(
        metrics_text,
        metric_name="biorempp_dash_callback_request_size_bytes",
        dash_output=dash_output,
    )
    response_buckets = extract_histogram_buckets_for_dash_output(
        metrics_text,
        metric_name="biorempp_dash_callback_response_size_bytes",
        dash_output=dash_output,
    )

    invocations = None
    if duration_buckets:
        invocations = int(duration_buckets[-1][1])

    duration_p50 = histogram_quantile(0.50, duration_buckets)
    duration_p95 = histogram_quantile(0.95, duration_buckets)
    request_p50 = histogram_quantile(0.50, request_buckets)
    request_p95 = histogram_quantile(0.95, request_buckets)
    response_p50 = histogram_quantile(0.50, response_buckets)
    response_p95 = histogram_quantile(0.95, response_buckets)

    return {
        "dash_output": dash_output,
        "invocations": invocations,
        "duration_seconds": {"p50": duration_p50, "p95": duration_p95},
        "request_bytes": {"p50": request_p50, "p95": request_p95},
        "response_bytes": {"p50": response_p50, "p95": response_p95},
    }


def _fetch_metrics_with_fallback(
    metrics_url: str,
    container_metric_urls: list[str],
    skip_metrics: bool,
) -> tuple[str | None, str | None, str | None]:
    """Fetch metrics from URL and fallback to docker exec in running container."""
    if skip_metrics:
        return None, None, "metrics skipped by flag"

    try:
        text = fetch_metrics(metrics_url)
        return text, metrics_url, None
    except Exception as host_exc:  # pragma: no cover - network variability
        running = detect_running_container()
        if not running:
            return None, None, f"host metrics unavailable: {host_exc}"
        try:
            text = fetch_metrics_from_container(running, container_metric_urls)
            return text, f"{running}:container_url_fallback", None
        except Exception as container_exc:  # pragma: no cover - runtime variability
            return None, None, (
                "host metrics unavailable and container fallback failed: "
                f"{host_exc}; {container_exc}"
            )


def _evaluate_phase0_gate(
    transition_summary: dict[str, Any],
    metrics_available: bool,
    expected_runs: int,
) -> dict[str, Any]:
    """Evaluate baseline gate for /results transition."""
    client = transition_summary.get("client_timings", {})
    server = transition_summary.get("server_callback_timings", {})

    samples_route = int(transition_summary.get("samples_route", 0))
    click_to_paint_p95 = _safe_float(
        client.get("click_to_paint_seconds", {}).get("p95")
    )
    routing_p95 = _safe_float(server.get("routing.display_page", {}).get("p95"))

    checks = {
        "min_samples_ok": samples_route >= expected_runs,
        "click_to_paint_ok": click_to_paint_p95 is not None,
        "routing_display_page_ok": routing_p95 is not None,
        "metrics_available": metrics_available,
    }

    failures: list[str] = []
    if not checks["min_samples_ok"]:
        failures.append(
            f"samples_route={samples_route} below expected_runs={expected_runs}"
        )
    if not checks["click_to_paint_ok"]:
        failures.append("click_to_paint_seconds.p95 is null")
    if not checks["routing_display_page_ok"]:
        failures.append("routing.display_page.p95 is null")

    if failures:
        status = "FAIL"
    elif checks["metrics_available"]:
        status = "PASS"
    else:
        status = "PASS_PARTIAL"

    return {
        "status": status,
        "checks": checks,
        "failures": failures,
        "summary": {
            "samples_route": samples_route,
            "click_to_paint_p95": click_to_paint_p95,
            "routing_display_page_p95": routing_p95,
        },
    }


def _evaluate_phase1_gate(
    uc_matrix_summary: dict[str, Any],
    payload_transport_summary: dict[str, Any],
    metrics_available: bool,
    duration_p95_max_threshold: float,
    duration_p95_median_threshold: float,
    page_content_request_bytes_threshold: float,
    uc_request_bytes_threshold: float,
) -> dict[str, Any]:
    """Evaluate UC matrix gate for chart render performance."""
    expected_count = int(uc_matrix_summary.get("expected_count", 0))
    coverage_complete = bool(uc_matrix_summary.get("coverage_complete", False))
    duration_p95_max = _safe_float(uc_matrix_summary.get("duration_p95_max"))
    duration_p95_median = _safe_float(uc_matrix_summary.get("duration_p95_median"))
    page_content_request_p95 = _safe_float(
        payload_transport_summary.get("page_content_request_bytes_p95")
    )
    uc_request_bytes_p95_max = _safe_float(
        payload_transport_summary.get("uc_request_bytes_p95_max")
    )
    uc_request_bytes_violations = payload_transport_summary.get(
        "uc_request_bytes_violations",
        [],
    )
    if not isinstance(uc_request_bytes_violations, list):
        uc_request_bytes_violations = []

    checks = {
        "expected_outputs_non_zero": expected_count > 0,
        "coverage_complete": coverage_complete,
        "uc_duration_p95_max_ok": (
            duration_p95_max is not None
            and duration_p95_max <= duration_p95_max_threshold
        ),
        "uc_duration_p95_median_ok": (
            duration_p95_median is not None
            and duration_p95_median <= duration_p95_median_threshold
        ),
        "page_content_request_bytes_ok": (
            page_content_request_p95 is not None
            and page_content_request_p95 <= page_content_request_bytes_threshold
        ),
        "uc_request_bytes_ok": (
            (uc_request_bytes_p95_max is None and not uc_request_bytes_violations)
            or (
                uc_request_bytes_p95_max is not None
                and uc_request_bytes_p95_max <= uc_request_bytes_threshold
                and not uc_request_bytes_violations
            )
        ),
        "metrics_available": metrics_available,
    }

    failures: list[str] = []
    if not checks["expected_outputs_non_zero"]:
        failures.append("expected outputs catalog is empty")

    if checks["expected_outputs_non_zero"] and not metrics_available:
        status = "PASS_PARTIAL"
        return {
            "status": status,
            "checks": checks,
            "failures": failures,
            "summary": {
                "expected_count": expected_count,
                "coverage_ratio": uc_matrix_summary.get("coverage_ratio"),
                "duration_p95_max": duration_p95_max,
                "duration_p95_median": duration_p95_median,
                "page_content_request_bytes_p95": page_content_request_p95,
                "uc_request_bytes_p95_max": uc_request_bytes_p95_max,
            },
        }

    if not checks["coverage_complete"]:
        failures.append("UC output coverage is not complete")
    if not checks["uc_duration_p95_max_ok"]:
        failures.append(
            f"uc_duration_p95_max exceeds threshold {duration_p95_max_threshold}s"
        )
    if not checks["uc_duration_p95_median_ok"]:
        failures.append(
            "uc_duration_p95_median exceeds threshold "
            f"{duration_p95_median_threshold}s"
        )
    if not checks["page_content_request_bytes_ok"]:
        failures.append(
            "page-content.children.request_bytes.p95 exceeds threshold "
            f"{page_content_request_bytes_threshold}"
        )
    if not checks["uc_request_bytes_ok"]:
        failures.append(
            "UC outputs request_bytes.p95 exceeds threshold "
            f"{uc_request_bytes_threshold}"
        )

    status = "FAIL" if failures else "PASS"
    return {
        "status": status,
        "checks": checks,
        "failures": failures,
        "summary": {
            "expected_count": expected_count,
            "coverage_ratio": uc_matrix_summary.get("coverage_ratio"),
            "duration_p95_max": duration_p95_max,
            "duration_p95_median": duration_p95_median,
            "page_content_request_bytes_p95": page_content_request_p95,
            "uc_request_bytes_p95_max": uc_request_bytes_p95_max,
            "uc_request_bytes_violations": uc_request_bytes_violations,
        },
    }


def _build_overall_status(gates: dict[str, Any]) -> str:
    """Compute consolidated gate status."""
    statuses = [
        str(gates.get("phase0", {}).get("status", "")),
        str(gates.get("phase1", {}).get("status", "")),
    ]
    if any(status == "FAIL" for status in statuses):
        return "FAIL"
    if any(status == "PASS_PARTIAL" for status in statuses):
        return "PASS_PARTIAL"
    if all(status == "PASS" for status in statuses):
        return "PASS"
    return "FAIL"


def main() -> None:
    """CLI entrypoint for unified results_view validation report."""
    parser = argparse.ArgumentParser(
        description="Unified report for /results transition and UC matrix validation."
    )
    parser.add_argument("--app-log", required=True, help="Path to exported app log text.")
    parser.add_argument("--metrics-url", default="http://127.0.0.1:8080/metrics")
    parser.add_argument("--route", default="/results")
    parser.add_argument("--outputs-file", default=None)
    parser.add_argument("--json-out", default=None)
    parser.add_argument("--expected-runs", type=int, default=20)
    parser.add_argument("--uc-p95-max-seconds", type=float, default=5.0)
    parser.add_argument("--uc-p95-median-seconds", type=float, default=2.5)
    parser.add_argument("--page-content-request-p95-max-bytes", type=float, default=65536.0)
    parser.add_argument("--uc-request-p95-max-bytes", type=float, default=65536.0)
    parser.add_argument("--skip-metrics", action="store_true")
    parser.add_argument(
        "--container-metrics-urls",
        nargs="*",
        default=list(DEFAULT_CONTAINER_METRICS_URLS),
    )
    args = parser.parse_args()

    app_log = Path(args.app_log)
    outputs_file = Path(args.outputs_file) if args.outputs_file else None

    log_text = app_log.read_text(encoding="utf-8", errors="replace")
    expected_outputs = _load_outputs_file(outputs_file)

    transition_summary = _collect_transition_summary(args.route, log_text)

    metrics_text, metrics_source, metrics_warning = _fetch_metrics_with_fallback(
        metrics_url=args.metrics_url,
        container_metric_urls=list(args.container_metrics_urls),
        skip_metrics=bool(args.skip_metrics),
    )
    metrics_available = metrics_text is not None

    output_summaries: list[dict[str, Any]] = []
    if metrics_text is not None:
        for dash_output in expected_outputs:
            output_summaries.append(
                _metric_summary_for_output(metrics_text, dash_output)
            )

    measured_outputs = [
        item["dash_output"]
        for item in output_summaries
        if int(item.get("invocations") or 0) > 0
    ]
    expected_count = len(expected_outputs)
    coverage_count = len(measured_outputs)
    coverage_ratio = (
        float(coverage_count) / float(expected_count)
        if expected_count > 0
        else 0.0
    )
    coverage_complete = expected_count > 0 and coverage_count == expected_count

    duration_p95_values = [
        _safe_float(item.get("duration_seconds", {}).get("p95"))
        for item in output_summaries
        if int(item.get("invocations") or 0) > 0
    ]
    duration_p95_values = [value for value in duration_p95_values if value is not None]
    duration_p95_max = max(duration_p95_values) if duration_p95_values else None
    duration_p95_median = median(duration_p95_values) if duration_p95_values else None

    page_content_summary = None
    if metrics_text is not None:
        page_content_summary = _metric_summary_for_output(
            metrics_text, "page-content.children"
        )
    page_content_request_p95 = (
        _safe_float(page_content_summary.get("request_bytes", {}).get("p95"))
        if isinstance(page_content_summary, dict)
        else None
    )
    page_content_response_p95 = (
        _safe_float(page_content_summary.get("response_bytes", {}).get("p95"))
        if isinstance(page_content_summary, dict)
        else None
    )
    uc_output_summaries = [
        item
        for item in output_summaries
        if str(item.get("dash_output", "")).startswith("uc-")
        and int(item.get("invocations") or 0) > 0
    ]
    uc_request_p95_records = [
        (
            str(item.get("dash_output")),
            _safe_float(item.get("request_bytes", {}).get("p95")),
        )
        for item in uc_output_summaries
    ]
    uc_request_p95_values = [
        value for _, value in uc_request_p95_records if value is not None
    ]
    uc_request_bytes_p95_max = (
        max(uc_request_p95_values) if uc_request_p95_values else None
    )
    uc_request_bytes_violations = sorted(
        [
            dash_output
            for dash_output, p95 in uc_request_p95_records
            if p95 is not None and p95 > args.uc_request_p95_max_bytes
        ]
    )

    payload_transport_summary = {
        "page_content_request_bytes_p95": page_content_request_p95,
        "page_content_response_bytes_p95": page_content_response_p95,
        "page_content_request_bytes_threshold": args.page_content_request_p95_max_bytes,
        "uc_request_bytes_threshold": args.uc_request_p95_max_bytes,
        "request_bytes_gate_ok": (
            (
                page_content_request_p95
                <= args.page_content_request_p95_max_bytes
            )
            if page_content_request_p95 is not None
            else None
        ),
        "uc_request_bytes_p95_max": uc_request_bytes_p95_max,
        "uc_request_bytes_violations": uc_request_bytes_violations,
        "uc_request_bytes_gate_ok": (
            (
                uc_request_bytes_p95_max <= args.uc_request_p95_max_bytes
                and not uc_request_bytes_violations
            )
            if uc_request_bytes_p95_max is not None
            else None
        ),
    }
    resume_persist_timeout_summary = _collect_resume_persist_timeout_summary(metrics_text)

    uc_matrix_summary = {
        "expected_outputs": expected_outputs,
        "expected_count": expected_count,
        "measured_outputs": measured_outputs,
        "coverage_count": coverage_count,
        "coverage_ratio": coverage_ratio,
        "coverage_complete": coverage_complete,
        "duration_p95_max": duration_p95_max,
        "duration_p95_median": duration_p95_median,
        "outputs": output_summaries,
    }

    phase0_gate = _evaluate_phase0_gate(
        transition_summary=transition_summary,
        metrics_available=metrics_available,
        expected_runs=args.expected_runs,
    )
    phase1_gate = _evaluate_phase1_gate(
        uc_matrix_summary=uc_matrix_summary,
        payload_transport_summary=payload_transport_summary,
        metrics_available=metrics_available,
        duration_p95_max_threshold=args.uc_p95_max_seconds,
        duration_p95_median_threshold=args.uc_p95_median_seconds,
        page_content_request_bytes_threshold=args.page_content_request_p95_max_bytes,
        uc_request_bytes_threshold=args.uc_request_p95_max_bytes,
    )

    gates = {
        "phase0": phase0_gate,
        "phase1": phase1_gate,
    }
    overall_status = _build_overall_status(gates)

    report_payload = {
        "generated_at_utc": now_utc_iso(),
        "route": args.route,
        "log_source": str(app_log),
        "metrics_source": metrics_source,
        "metrics_warning": metrics_warning,
        "transition_summary": transition_summary,
        "payload_transport_summary": payload_transport_summary,
        "resume_persist_timeout_summary": resume_persist_timeout_summary,
        "uc_matrix_summary": uc_matrix_summary,
        "gates": gates,
        "overall_status": overall_status,
    }

    print("Results View Validation Report")
    print(f"- status: {overall_status}")
    print(
        "- phase0: "
        f"{phase0_gate.get('status')} "
        f"(samples_route={phase0_gate.get('summary', {}).get('samples_route')})"
    )
    print(
        "- phase1: "
        f"{phase1_gate.get('status')} "
        f"(coverage={uc_matrix_summary.get('coverage_count')}/{uc_matrix_summary.get('expected_count')})"
    )
    if metrics_warning:
        print(f"- metrics_warning: {metrics_warning}")
    timeout_rate = resume_persist_timeout_summary.get("timeout_rate_per_100_processings")
    if timeout_rate is not None:
        print(f"- resume_timeout_rate_per_100: {timeout_rate:.4f}")
    timeout_stages = resume_persist_timeout_summary.get("timeout_stage_counts", {})
    if isinstance(timeout_stages, dict) and timeout_stages:
        print(f"- resume_timeout_stages: {timeout_stages}")

    if args.json_out:
        json_out = Path(args.json_out)
        json_out.parent.mkdir(parents=True, exist_ok=True)
        json_out.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
        print(f"- json_out: {json_out}")


if __name__ == "__main__":
    main()
