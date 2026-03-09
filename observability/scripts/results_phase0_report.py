#!/usr/bin/env python
"""Phase 0 report generator for /results transition bottleneck diagnostics."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any, Iterable

import requests

LOG_PATTERN = re.compile(r"RESULTS_TRANSITION_SAMPLE\s+(\{.*\})")
SERVER_CALLBACK_PATTERN = re.compile(r"RESULTS_SERVER_CALLBACK_SAMPLE\s+(\{.*\})")
HISTOGRAM_BUCKET_PATTERN = re.compile(
    r'^(?P<name>[a-zA-Z_:][a-zA-Z0-9_:]*)_bucket\{(?P<labels>[^}]*)\}\s+'
    r"(?P<value>[0-9eE+\-\.]+)$"
)
LABEL_PATTERN = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="((?:\\.|[^"])*)"')

DEFAULT_DASH_OUTPUTS = ("url.pathname", "page-content.children")
DEFAULT_CONTAINER_CANDIDATES = ("biorempp-dev", "biorempp")
DEFAULT_CONTAINER_LOG_PATH = "/app/logs/app.log"
DEFAULT_CONTAINER_METRICS_URLS = (
    "http://127.0.0.1:8050/metrics",
    "http://127.0.0.1:8080/metrics",
)


@dataclass
class PercentileSummary:
    """Simple percentile summary container."""

    count: int
    p50: float | None
    p95: float | None
    avg: float | None


@dataclass
class RankedFinding:
    """Ranked diagnostic finding for impact hierarchy output."""

    title: str
    metric: str
    p95: float | None
    share_pct: float | None


def percentile(values: list[float], quantile: float) -> float | None:
    """Compute quantile using linear interpolation between ordered values."""
    if not values:
        return None
    if quantile <= 0:
        return min(values)
    if quantile >= 1:
        return max(values)

    ordered = sorted(values)
    last_index = len(ordered) - 1
    position = quantile * last_index
    lower_index = int(math.floor(position))
    upper_index = int(math.ceil(position))

    if lower_index == upper_index:
        return ordered[lower_index]

    lower_value = ordered[lower_index]
    upper_value = ordered[upper_index]
    fraction = position - lower_index
    return lower_value + (upper_value - lower_value) * fraction


def summarize(values: list[float]) -> PercentileSummary:
    """Return p50/p95/avg summary for numeric series."""
    if not values:
        return PercentileSummary(count=0, p50=None, p95=None, avg=None)
    return PercentileSummary(
        count=len(values),
        p50=percentile(values, 0.50),
        p95=percentile(values, 0.95),
        avg=mean(values),
    )


def _parse_samples_from_text(
    log_text: str,
    pattern: re.Pattern[str],
) -> list[dict[str, Any]]:
    """Parse structured JSON sample lines from log text using regex pattern."""
    samples: list[dict[str, Any]] = []
    for line in log_text.splitlines():
        match = pattern.search(line)
        if not match:
            continue
        try:
            payload = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            samples.append(payload)
    return samples


def parse_results_samples_from_text(log_text: str) -> list[dict[str, Any]]:
    """Parse structured transition samples from already loaded log text."""
    return _parse_samples_from_text(log_text, LOG_PATTERN)


def parse_server_callback_samples_from_text(log_text: str) -> list[dict[str, Any]]:
    """Parse structured server callback samples from already loaded log text."""
    return _parse_samples_from_text(log_text, SERVER_CALLBACK_PATTERN)


def _safe_share(part: float | None, whole: float | None) -> float | None:
    """Return part/whole percentage when both values are valid."""
    if part is None or whole is None or whole <= 0:
        return None
    return (part / whole) * 100.0


def parse_labels(raw_labels: str) -> dict[str, str]:
    """Parse Prometheus metric labels from exposition format."""
    labels: dict[str, str] = {}
    for match in LABEL_PATTERN.finditer(raw_labels):
        key = match.group(1)
        value = bytes(match.group(2), "utf-8").decode("unicode_escape")
        labels[key] = value
    return labels


def extract_histogram_buckets(
    metrics_text: str,
    metric_name: str,
    required_labels: dict[str, str],
) -> list[tuple[float, float]]:
    """
    Extract histogram buckets for one metric/label set.

    Returns cumulative bucket counts as list of (le, count).
    """
    buckets: list[tuple[float, float]] = []
    for line in metrics_text.splitlines():
        match = HISTOGRAM_BUCKET_PATTERN.match(line.strip())
        if not match:
            continue
        if match.group("name") != metric_name:
            continue

        labels = parse_labels(match.group("labels"))
        label_match = all(labels.get(key) == value for key, value in required_labels.items())
        if not label_match:
            continue

        le_raw = labels.get("le")
        if le_raw is None:
            continue
        if le_raw == "+Inf":
            bucket_le = math.inf
        else:
            try:
                bucket_le = float(le_raw)
            except ValueError:
                continue

        try:
            bucket_count = float(match.group("value"))
        except ValueError:
            continue
        buckets.append((bucket_le, bucket_count))

    buckets.sort(key=lambda item: item[0])
    return buckets


def _collect_dash_output_label_values(
    metrics_text: str,
    metric_name: str,
) -> set[str]:
    """Collect distinct dash_output label values for one histogram metric."""
    values: set[str] = set()
    for line in metrics_text.splitlines():
        match = HISTOGRAM_BUCKET_PATTERN.match(line.strip())
        if not match:
            continue
        if match.group("name") != metric_name:
            continue
        labels = parse_labels(match.group("labels"))
        dash_output = labels.get("dash_output")
        if dash_output:
            values.add(dash_output)
    return values


def extract_histogram_buckets_for_dash_output(
    metrics_text: str,
    metric_name: str,
    dash_output: str,
) -> list[tuple[float, float]]:
    """
    Extract histogram buckets for a dash output label.

    Supports Dash duplicate-output hashing where labels can appear as
    `url.pathname_<hash>` instead of `url.pathname`.
    """
    exact = extract_histogram_buckets(
        metrics_text,
        metric_name=metric_name,
        required_labels={"dash_output": dash_output},
    )
    if exact:
        return exact

    prefix = f"{dash_output}_"
    label_values = _collect_dash_output_label_values(metrics_text, metric_name)
    matched_values = sorted(value for value in label_values if value.startswith(prefix))
    if not matched_values:
        return []

    aggregated_counts: dict[float, float] = {}
    for matched_value in matched_values:
        buckets = extract_histogram_buckets(
            metrics_text,
            metric_name=metric_name,
            required_labels={"dash_output": matched_value},
        )
        for upper_bound, cumulative_count in buckets:
            aggregated_counts[upper_bound] = (
                aggregated_counts.get(upper_bound, 0.0) + cumulative_count
            )

    return sorted(aggregated_counts.items(), key=lambda item: item[0])


def histogram_quantile(quantile: float, buckets: list[tuple[float, float]]) -> float | None:
    """Compute quantile from cumulative Prometheus histogram buckets."""
    if not buckets:
        return None

    total = buckets[-1][1]
    if total <= 0:
        return None

    if quantile <= 0:
        return 0.0
    if quantile >= 1:
        for upper_bound, _count in reversed(buckets):
            if math.isfinite(upper_bound):
                return upper_bound
        return None

    target_rank = quantile * total
    previous_upper = 0.0
    previous_count = 0.0

    for upper_bound, cumulative_count in buckets:
        if cumulative_count >= target_rank:
            if not math.isfinite(upper_bound):
                return previous_upper

            bucket_count = cumulative_count - previous_count
            if bucket_count <= 0:
                return upper_bound

            rank_inside_bucket = target_rank - previous_count
            fraction = rank_inside_bucket / bucket_count
            return previous_upper + (upper_bound - previous_upper) * fraction

        previous_upper = 0.0 if not math.isfinite(upper_bound) else upper_bound
        previous_count = cumulative_count

    return None


def fetch_metrics(metrics_url: str, timeout_seconds: float = 5.0) -> str:
    """Fetch Prometheus metrics exposition text from host URL."""
    response = requests.get(metrics_url, timeout=timeout_seconds)
    response.raise_for_status()
    return response.text


def _run_subprocess(command: list[str]) -> subprocess.CompletedProcess[str]:
    """Run subprocess command and return completed process (no exception on rc)."""
    return subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
    )


def detect_running_container(
    candidates: Iterable[str] = DEFAULT_CONTAINER_CANDIDATES,
) -> str | None:
    """Detect first running docker container among known BioRemPP candidates."""
    try:
        for candidate in candidates:
            completed = _run_subprocess(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={candidate}",
                    "--format",
                    "{{.Names}}",
                ]
            )
            if completed.returncode != 0:
                continue
            names = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
            if candidate in names:
                return candidate
    except FileNotFoundError:
        return None

    return None


def list_running_container_names() -> list[str]:
    """Return running docker container names."""
    try:
        completed = _run_subprocess(["docker", "ps", "--format", "{{.Names}}"])
    except FileNotFoundError:
        return []
    if completed.returncode != 0:
        return []
    return [line.strip() for line in completed.stdout.splitlines() if line.strip()]


def fetch_log_text_from_container(container: str, container_log_path: str) -> str:
    """Fetch app log text from running container file path via docker exec."""
    completed = _run_subprocess(
        ["docker", "exec", container, "cat", container_log_path]
    )
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "unknown docker exec error"
        raise RuntimeError(
            f"Failed to read log from container '{container}' ({container_log_path}): {stderr}"
        )
    return completed.stdout


def fetch_metrics_from_container(
    container: str,
    metric_urls: Iterable[str],
) -> str:
    """Fetch metrics text by running python requests inside target container."""
    script = (
        "import sys\n"
        "import requests\n"
        "urls = sys.argv[1:]\n"
        "for url in urls:\n"
        "    try:\n"
        "        response = requests.get(url, timeout=5.0)\n"
        "        if response.status_code == 200 and response.text:\n"
        "            sys.stdout.write(response.text)\n"
        "            sys.exit(0)\n"
        "    except Exception:\n"
        "        pass\n"
        "sys.exit(1)\n"
    )
    command = [
        "docker",
        "exec",
        container,
        "python",
        "-c",
        script,
        *list(metric_urls),
    ]
    completed = _run_subprocess(command)
    if completed.returncode != 0:
        stderr = completed.stderr.strip() or "no response from candidate URLs"
        raise RuntimeError(
            f"Failed to fetch metrics from container '{container}': {stderr}"
        )
    return completed.stdout


def format_seconds_ms(value: float | None) -> str:
    """Format seconds value in milliseconds for readability."""
    if value is None:
        return "--"
    return f"{value * 1000.0:.2f} ms"


def format_bytes(value: float | None) -> str:
    """Format bytes value in kb/mb form."""
    if value is None:
        return "--"
    if value < 1024:
        return f"{value:.0f} B"
    if value < (1024 * 1024):
        return f"{value / 1024.0:.2f} KB"
    return f"{value / (1024.0 * 1024.0):.3f} MB"


def format_share_pct(value: float | None) -> str:
    """Format share percentage with fallback placeholder."""
    if value is None:
        return "--"
    return f"{value:.1f}%"


def _summary_to_ranked_finding(
    title: str,
    metric: str,
    summary: PercentileSummary,
    total_for_share: float | None,
) -> RankedFinding:
    """Convert summary into ranked finding."""
    return RankedFinding(
        title=title,
        metric=metric,
        p95=summary.p95,
        share_pct=_safe_share(summary.p95, total_for_share),
    )


def _metric_p95(
    metrics_summary: dict[str, dict[str, dict[str, float | None]]],
    output: str,
    metric: str,
) -> float | None:
    """Safely read p95 metric value from nested metrics summary payload."""
    return (
        metrics_summary.get(output, {})
        .get(metric, {})
        .get("p95")
    )


def build_hypotheses(
    *,
    click_to_paint_summary: PercentileSummary,
    click_to_request_summary: PercentileSummary,
    request_to_paint_summary: PercentileSummary,
    display_page_summary: PercentileSummary,
    navigate_summary: PercentileSummary,
    metrics_summary: dict[str, dict[str, dict[str, float | None]]],
) -> list[dict[str, Any]]:
    """Build heuristic bottleneck hierarchy from measured p95 values."""
    hypotheses: list[dict[str, Any]] = []
    total_p95 = click_to_paint_summary.p95
    request_to_paint_p95 = request_to_paint_summary.p95
    click_to_request_p95 = click_to_request_summary.p95
    display_page_p95 = display_page_summary.p95
    navigate_p95 = navigate_summary.p95

    if request_to_paint_p95 is not None and total_p95 is not None:
        share = _safe_share(request_to_paint_p95, total_p95)
        hypotheses.append(
            {
                "priority": "P1",
                "title": "Fase request->paint domina a transicao",
                "evidence": {
                    "request_to_paint_p95_seconds": request_to_paint_p95,
                    "click_to_paint_p95_seconds": total_p95,
                    "share_pct": share,
                },
            }
        )

    if display_page_p95 is not None:
        hypotheses.append(
            {
                "priority": "P1",
                "title": "Renderizacao de /results no servidor e custosa",
                "evidence": {
                    "routing.display_page_p95_seconds": display_page_p95,
                },
            }
        )

    if click_to_request_p95 is not None:
        hypotheses.append(
            {
                "priority": "P2",
                "title": "Atraso pre-request (browser/event loop/rede inicial)",
                "evidence": {
                    "click_to_request_p95_seconds": click_to_request_p95,
                    "share_pct_of_total": _safe_share(click_to_request_p95, total_p95),
                },
            }
        )

    page_duration_p95 = _metric_p95(
        metrics_summary, "page-content.children", "duration_seconds"
    )
    if page_duration_p95 is not None:
        hypotheses.append(
            {
                "priority": "P1",
                "title": "Callback Dash de page-content.children esta lento",
                "evidence": {
                    "dash_page_content_duration_p95_seconds": page_duration_p95,
                },
            }
        )

    page_response_bytes_p95 = _metric_p95(
        metrics_summary, "page-content.children", "response_bytes"
    )
    if page_response_bytes_p95 is not None and page_response_bytes_p95 >= 256 * 1024:
        hypotheses.append(
            {
                "priority": "P1",
                "title": "Payload de resposta de /results esta volumoso",
                "evidence": {
                    "page_content_response_bytes_p95": page_response_bytes_p95,
                    "page_content_response_mb_p95": round(
                        page_response_bytes_p95 / (1024.0 * 1024.0), 4
                    ),
                },
            }
        )

    page_request_bytes_p95 = _metric_p95(
        metrics_summary, "page-content.children", "request_bytes"
    )
    if page_request_bytes_p95 is not None and page_request_bytes_p95 >= 256 * 1024:
        hypotheses.append(
            {
                "priority": "P1",
                "title": "Request de /results envia estado grande (store no cliente)",
                "evidence": {
                    "page_content_request_bytes_p95": page_request_bytes_p95,
                    "page_content_request_mb_p95": round(
                        page_request_bytes_p95 / (1024.0 * 1024.0), 4
                    ),
                },
            }
        )

    if navigate_p95 is not None:
        hypotheses.append(
            {
                "priority": "P3",
                "title": "Callback de navegacao do botao tem baixo impacto relativo",
                "evidence": {
                    "processing.navigate_to_results_p95_seconds": navigate_p95,
                    "share_pct_of_total": _safe_share(navigate_p95, total_p95),
                },
            }
        )

    def _rank_score(item: dict[str, Any]) -> float:
        evidence = item.get("evidence", {})
        max_seconds = 0.0
        for key, value in evidence.items():
            if key.endswith("_seconds") and value is not None:
                max_seconds = max(max_seconds, float(value))

        response_mb = float(evidence.get("page_content_response_mb_p95") or 0.0)
        request_mb = float(evidence.get("page_content_request_mb_p95") or 0.0)
        payload_score = max(response_mb, request_mb) * 0.25

        return max(max_seconds, payload_score)

    return sorted(hypotheses, key=_rank_score, reverse=True)


def main() -> None:
    """Run phase 0 diagnostics summary."""
    parser = argparse.ArgumentParser(
        description=(
            "Generate p50/p95 summary for /results transition diagnostics "
            "(supports local files and docker container log collection)."
        )
    )
    parser.add_argument(
        "--app-log",
        type=Path,
        default=Path("logs/app.log"),
        help="Path to local application log file.",
    )
    parser.add_argument(
        "--docker-container",
        default=None,
        help="Optional running container name (ex.: biorempp-dev or biorempp).",
    )
    parser.add_argument(
        "--container-log-path",
        default=DEFAULT_CONTAINER_LOG_PATH,
        help="Log file path inside container.",
    )
    parser.add_argument(
        "--export-log",
        type=Path,
        default=None,
        help="Optional local file path to save container log snapshot used by report.",
    )
    parser.add_argument(
        "--metrics-url",
        default="http://127.0.0.1:8050/metrics",
        help="Host-accessible Prometheus metrics endpoint URL.",
    )
    parser.add_argument(
        "--container-metrics-urls",
        nargs="+",
        default=list(DEFAULT_CONTAINER_METRICS_URLS),
        help=(
            "Candidate metrics URLs to try from inside container if host URL fails "
            "(evaluated in order)."
        ),
    )
    parser.add_argument(
        "--skip-metrics",
        action="store_true",
        help="Skip Prometheus endpoint queries and report only client/server log timings.",
    )
    parser.add_argument(
        "--route",
        default="/results",
        help="Route label to filter client telemetry samples.",
    )
    parser.add_argument(
        "--outputs",
        nargs="+",
        default=list(DEFAULT_DASH_OUTPUTS),
        help="Dash output labels for request/response/duration histogram analysis.",
    )
    parser.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Optional JSON output file path.",
    )
    args = parser.parse_args()

    explicit_container_requested = args.docker_container is not None
    resolved_container = args.docker_container
    if resolved_container is None:
        resolved_container = detect_running_container()

    log_source = str(args.app_log)
    if explicit_container_requested:
        if resolved_container is None:
            raise RuntimeError(
                "Container explicitly requested but not found. "
                "Check --docker-container value and docker compose status."
            )
        log_text = fetch_log_text_from_container(
            container=resolved_container,
            container_log_path=args.container_log_path,
        )
        log_source = f"{resolved_container}:{args.container_log_path}"
        if args.export_log is not None:
            args.export_log.parent.mkdir(parents=True, exist_ok=True)
            args.export_log.write_text(log_text, encoding="utf-8")
    elif args.app_log.exists():
        log_text = args.app_log.read_text(encoding="utf-8", errors="replace")
    elif resolved_container is not None:
        log_text = fetch_log_text_from_container(
            container=resolved_container,
            container_log_path=args.container_log_path,
        )
        log_source = f"{resolved_container}:{args.container_log_path}"
        if args.export_log is not None:
            args.export_log.parent.mkdir(parents=True, exist_ok=True)
            args.export_log.write_text(log_text, encoding="utf-8")
    else:
        raise FileNotFoundError(
            f"Log file not found: {args.app_log}. "
            "Provide --docker-container or start compose service (biorempp-dev/biorempp)."
        )

    samples = parse_results_samples_from_text(log_text)
    server_callback_samples = parse_server_callback_samples_from_text(log_text)
    filtered_samples = [sample for sample in samples if sample.get("route") == args.route]

    click_to_request_values = [
        float(sample["click_to_request_seconds"])
        for sample in filtered_samples
        if sample.get("click_to_request_seconds") is not None
    ]
    request_to_paint_values = [
        float(sample["request_to_paint_seconds"])
        for sample in filtered_samples
        if sample.get("request_to_paint_seconds") is not None
    ]
    click_to_paint_values = [
        float(sample["click_to_paint_seconds"])
        for sample in filtered_samples
        if sample.get("click_to_paint_seconds") is not None
    ]

    click_to_request_summary = summarize(click_to_request_values)
    request_to_paint_summary = summarize(request_to_paint_values)
    click_to_paint_summary = summarize(click_to_paint_values)
    running_containers = list_running_container_names()

    print("=" * 88)
    print("BioRemPP /results Transition - Phase 0 Objective Measurements")
    print("=" * 88)
    print(f"Log source: {log_source}")
    print(f"Samples in log: {len(samples)}")
    print(f"Samples for route {args.route!r}: {len(filtered_samples)}")
    print("")
    print("Client-side transition timings")
    print(
        f"- click -> request start: p50={format_seconds_ms(click_to_request_summary.p50)} | "
        f"p95={format_seconds_ms(click_to_request_summary.p95)} | n={click_to_request_summary.count}"
    )
    print(
        f"- request start -> final paint: p50={format_seconds_ms(request_to_paint_summary.p50)} | "
        f"p95={format_seconds_ms(request_to_paint_summary.p95)} | n={request_to_paint_summary.count}"
    )
    print(
        f"- click -> final paint: p50={format_seconds_ms(click_to_paint_summary.p50)} | "
        f"p95={format_seconds_ms(click_to_paint_summary.p95)} | n={click_to_paint_summary.count}"
    )
    print("")

    display_page_durations = [
        float(sample["duration_seconds"])
        for sample in server_callback_samples
        if sample.get("callback") == "routing.display_page"
        and sample.get("route") == "/results"
        and sample.get("duration_seconds") is not None
    ]
    navigate_durations = [
        float(sample["duration_seconds"])
        for sample in server_callback_samples
        if sample.get("callback") == "processing.navigate_to_results"
        and sample.get("route") == "/results"
        and sample.get("duration_seconds") is not None
    ]

    display_page_summary = summarize(display_page_durations)
    navigate_summary = summarize(navigate_durations)
    print("Server callback timings from app.log")
    print(
        f"- routing.display_page (/results): p50={format_seconds_ms(display_page_summary.p50)} | "
        f"p95={format_seconds_ms(display_page_summary.p95)} | n={display_page_summary.count}"
    )
    print(
        f"- processing.navigate_to_results: p50={format_seconds_ms(navigate_summary.p50)} | "
        f"p95={format_seconds_ms(navigate_summary.p95)} | n={navigate_summary.count}"
    )
    print("")

    metrics_summary: dict[str, dict[str, dict[str, float | None]]] = {}
    metrics_source: str | None = None

    if args.skip_metrics:
        print("Server-side dash callback metrics skipped (--skip-metrics enabled)")
    else:
        metrics_text = ""
        try:
            metrics_text = fetch_metrics(args.metrics_url)
            metrics_source = args.metrics_url
        except Exception as host_exc:
            if resolved_container is not None:
                try:
                    metrics_text = fetch_metrics_from_container(
                        resolved_container,
                        args.container_metrics_urls,
                    )
                    metrics_source = f"{resolved_container}:container_url_fallback"
                except Exception as container_exc:
                    print(
                        "Server-side dash callback metrics unavailable: "
                        f"host_error={type(host_exc).__name__}: {host_exc} | "
                        f"container_error={type(container_exc).__name__}: {container_exc}"
                    )
            else:
                print(
                    "Server-side dash callback metrics unavailable: "
                    f"{type(host_exc).__name__}: {host_exc}"
                )

        if metrics_text:
            print(
                "Server-side dash callback metrics by output"
                + (f" (source: {metrics_source})" if metrics_source else "")
            )
            for dash_output in args.outputs:
                output_summary: dict[str, dict[str, float | None]] = {}
                duration_buckets = extract_histogram_buckets_for_dash_output(
                    metrics_text,
                    metric_name="biorempp_dash_callback_server_duration_seconds",
                    dash_output=dash_output,
                )
                request_size_buckets = extract_histogram_buckets_for_dash_output(
                    metrics_text,
                    metric_name="biorempp_dash_callback_request_size_bytes",
                    dash_output=dash_output,
                )
                response_size_buckets = extract_histogram_buckets_for_dash_output(
                    metrics_text,
                    metric_name="biorempp_dash_callback_response_size_bytes",
                    dash_output=dash_output,
                )

                duration_p50 = histogram_quantile(0.50, duration_buckets)
                duration_p95 = histogram_quantile(0.95, duration_buckets)
                request_p50 = histogram_quantile(0.50, request_size_buckets)
                request_p95 = histogram_quantile(0.95, request_size_buckets)
                response_p50 = histogram_quantile(0.50, response_size_buckets)
                response_p95 = histogram_quantile(0.95, response_size_buckets)

                output_summary["duration_seconds"] = {
                    "p50": duration_p50,
                    "p95": duration_p95,
                }
                output_summary["request_bytes"] = {"p50": request_p50, "p95": request_p95}
                output_summary["response_bytes"] = {
                    "p50": response_p50,
                    "p95": response_p95,
                }
                metrics_summary[dash_output] = output_summary

                print(f"- {dash_output}")
                print(
                    f"  duration: p50={format_seconds_ms(duration_p50)} | "
                    f"p95={format_seconds_ms(duration_p95)}"
                )
                print(
                    f"  request size: p50={format_bytes(request_p50)} | "
                    f"p95={format_bytes(request_p95)}"
                )
                print(
                    f"  response size: p50={format_bytes(response_p50)} | "
                    f"p95={format_bytes(response_p95)}"
                )

    total_p95 = click_to_paint_summary.p95
    stage_findings = [
        _summary_to_ranked_finding(
            title="request start -> final paint (client)",
            metric="request_to_paint_seconds",
            summary=request_to_paint_summary,
            total_for_share=total_p95,
        ),
        _summary_to_ranked_finding(
            title="click -> request start (client)",
            metric="click_to_request_seconds",
            summary=click_to_request_summary,
            total_for_share=total_p95,
        ),
    ]
    stage_findings = [item for item in stage_findings if item.p95 is not None]
    stage_findings.sort(key=lambda item: float(item.p95 or 0.0), reverse=True)

    server_findings = [
        _summary_to_ranked_finding(
            title="routing.display_page (/results)",
            metric="routing.display_page.duration_seconds",
            summary=display_page_summary,
            total_for_share=total_p95,
        ),
        _summary_to_ranked_finding(
            title="processing.navigate_to_results",
            metric="processing.navigate_to_results.duration_seconds",
            summary=navigate_summary,
            total_for_share=total_p95,
        ),
    ]
    page_content_duration_p95 = _metric_p95(
        metrics_summary, "page-content.children", "duration_seconds"
    )
    if page_content_duration_p95 is not None:
        server_findings.append(
            RankedFinding(
                title="dash output page-content.children",
                metric="dash.page-content.children.duration_seconds",
                p95=page_content_duration_p95,
                share_pct=_safe_share(page_content_duration_p95, total_p95),
            )
        )
    server_findings = [item for item in server_findings if item.p95 is not None]
    server_findings.sort(key=lambda item: float(item.p95 or 0.0), reverse=True)

    payload_findings: list[dict[str, Any]] = []
    for dash_output in args.outputs:
        request_bytes_p95 = _metric_p95(metrics_summary, dash_output, "request_bytes")
        response_bytes_p95 = _metric_p95(metrics_summary, dash_output, "response_bytes")
        if request_bytes_p95 is not None:
            payload_findings.append(
                {
                    "title": f"{dash_output} request bytes",
                    "metric": f"dash.{dash_output}.request_bytes",
                    "p95_bytes": request_bytes_p95,
                }
            )
        if response_bytes_p95 is not None:
            payload_findings.append(
                {
                    "title": f"{dash_output} response bytes",
                    "metric": f"dash.{dash_output}.response_bytes",
                    "p95_bytes": response_bytes_p95,
                }
            )
    payload_findings.sort(
        key=lambda item: float(item.get("p95_bytes") or 0.0),
        reverse=True,
    )

    hypotheses = build_hypotheses(
        click_to_paint_summary=click_to_paint_summary,
        click_to_request_summary=click_to_request_summary,
        request_to_paint_summary=request_to_paint_summary,
        display_page_summary=display_page_summary,
        navigate_summary=navigate_summary,
        metrics_summary=metrics_summary,
    )

    print("")
    print("Impact hierarchy (time decomposition, ranked by p95)")
    if stage_findings:
        for index, finding in enumerate(stage_findings, start=1):
            print(
                f"{index}. {finding.title}: p95={format_seconds_ms(finding.p95)} "
                f"(share_of_click_to_paint={format_share_pct(finding.share_pct)})"
            )
    else:
        print("- no stage timings available yet")

    print("")
    print("Impact hierarchy (server callbacks, ranked by p95)")
    if server_findings:
        for index, finding in enumerate(server_findings, start=1):
            print(
                f"{index}. {finding.title}: p95={format_seconds_ms(finding.p95)} "
                f"(share_of_click_to_paint={format_share_pct(finding.share_pct)})"
            )
    else:
        print("- no server callback timings available yet")

    print("")
    print("Impact hierarchy (payload pressure, ranked by p95 bytes)")
    if payload_findings:
        for index, finding in enumerate(payload_findings, start=1):
            print(
                f"{index}. {finding['title']}: p95={format_bytes(finding['p95_bytes'])}"
            )
    else:
        print("- no payload metrics available yet (enable observability and collect more samples)")

    print("")
    print("Probable bottleneck hierarchy (heuristic)")
    if hypotheses:
        for index, hypothesis in enumerate(hypotheses, start=1):
            print(f"{index}. [{hypothesis['priority']}] {hypothesis['title']}")
            print(f"   evidence: {json.dumps(hypothesis.get('evidence', {}), sort_keys=True)}")
    else:
        print("- insufficient data for heuristic hierarchy")

    if len(filtered_samples) == 0:
        print("")
        print("Troubleshooting hints (no samples found)")
        print("- Ensure browser tests are executed on the same target used by this report.")
        if resolved_container == "biorempp-dev":
            print("- Open the app at http://127.0.0.1:8050 (dev) for Phase 0 collection.")
        if "biorempp-dev" in running_containers and "biorempp-nginx" in running_containers:
            print(
                "- Both dev (8050) and nginx/prod (80) are running; "
                "testing on :80 may bypass dev telemetry collection."
            )
        print(
            "- After test runs, confirm log lines exist: "
            "RESULTS_TRANSITION_SAMPLE and RESULTS_SERVER_CALLBACK_SAMPLE."
        )

    if args.json_out is not None:
        report_payload = {
            "route": args.route,
            "log_source": log_source,
            "metrics_source": metrics_source,
            "samples_total": len(samples),
            "samples_route": len(filtered_samples),
            "server_callback_samples_total": len(server_callback_samples),
            "client_timings": {
                "click_to_request_seconds": click_to_request_summary.__dict__,
                "request_to_paint_seconds": request_to_paint_summary.__dict__,
                "click_to_paint_seconds": click_to_paint_summary.__dict__,
            },
            "server_callback_timings": {
                "routing.display_page": display_page_summary.__dict__,
                "processing.navigate_to_results": navigate_summary.__dict__,
            },
            "server_dash_metrics": metrics_summary,
            "impact_hierarchy": {
                "stage_time": [finding.__dict__ for finding in stage_findings],
                "server_time": [finding.__dict__ for finding in server_findings],
                "payload": payload_findings,
                "probable_bottlenecks": hypotheses,
            },
        }
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(
            json.dumps(report_payload, indent=2),
            encoding="utf-8",
        )
        print("")
        print(f"JSON report written to: {args.json_out}")

    print("=" * 88)


if __name__ == "__main__":
    main()
