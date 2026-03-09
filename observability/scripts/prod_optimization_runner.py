#!/usr/bin/env python
"""Concrete runner for prod optimization roadmap and Phase 0 baseline."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

DEFAULT_ROOT = Path(".archive/prod_optimization")
DEFAULT_REPORTS_DIR = DEFAULT_ROOT / "reports"
DEFAULT_EVIDENCE_DIR = DEFAULT_ROOT / "evidence" / "phase0"
DEFAULT_STATUS_FILE = DEFAULT_ROOT / "status.json"
DEFAULT_CURRENT_SESSION_FILE = DEFAULT_EVIDENCE_DIR / "current_session.json"
DEFAULT_PHASE0_REPORT_NAME = "results_phase0_clean20.json"
DEFAULT_PHASE0_LOG_SUFFIX = "_stdout_run20.log"
DEFAULT_CONTAINER = "biorempp-dev"
DEFAULT_BASE_URL = "http://127.0.0.1:8050"
DEFAULT_METRICS_URL = "http://127.0.0.1:8050/metrics"
DEFAULT_ROUTE = "/results"
DEFAULT_OUTPUTS = ("url.pathname", "page-content.children")
PHASE_KEYS = ("phase0", "phase1_1", "phase1_2", "phase1_3", "phase2", "final_gate")


def now_utc_iso() -> str:
    """Return ISO-8601 UTC with Z suffix and second precision."""
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def now_utc_compact() -> str:
    """Return compact UTC timestamp for folder names."""
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run command and optionally raise with context on failure."""
    process = subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if check and process.returncode != 0:
        raise RuntimeError(
            "Command failed: "
            + " ".join(cmd)
            + "\n"
            + process.stdout.strip()
        )
    return process


def ensure_directories(root: Path, reports_dir: Path, evidence_dir: Path) -> None:
    """Ensure required roadmap directories exist."""
    root.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "sessions").mkdir(parents=True, exist_ok=True)


def default_status_payload() -> dict[str, Any]:
    """Create default status structure for roadmap phases."""
    phases = {
        phase: {
            "status": "pending",
            "updated_at_utc": None,
            "summary": None,
        }
        for phase in PHASE_KEYS
    }
    return {
        "updated_at_utc": now_utc_iso(),
        "phases": phases,
    }


def load_or_init_status(status_file: Path) -> dict[str, Any]:
    """Load status file or initialize with defaults."""
    if not status_file.exists():
        payload = default_status_payload()
        status_file.parent.mkdir(parents=True, exist_ok=True)
        status_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload
    try:
        content = json.loads(status_file.read_text(encoding="utf-8"))
        if not isinstance(content, dict) or "phases" not in content:
            raise ValueError("Invalid status file structure")
        return content
    except Exception as exc:  # pragma: no cover - defensive path
        raise RuntimeError(f"Failed to load status file: {status_file}") from exc


def save_status(status_file: Path, payload: dict[str, Any]) -> None:
    """Persist roadmap status payload."""
    payload["updated_at_utc"] = now_utc_iso()
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def update_phase_status(
    payload: dict[str, Any],
    phase: str,
    status: str,
    summary: dict[str, Any] | None = None,
) -> None:
    """Update one phase entry in status payload."""
    phases = payload.setdefault("phases", {})
    phase_entry = phases.setdefault(
        phase,
        {"status": "pending", "updated_at_utc": None, "summary": None},
    )
    phase_entry["status"] = status
    phase_entry["updated_at_utc"] = now_utc_iso()
    phase_entry["summary"] = summary


def http_status_code(url: str, timeout_seconds: float = 3.0) -> int | None:
    """Return HTTP status code or None if not reachable."""
    try:
        with urlopen(url, timeout=timeout_seconds) as response:  # nosec B310
            return int(getattr(response, "status", 200))
    except URLError:
        return None
    except Exception:
        return None


def build_session_payload(
    session_id: str,
    container: str,
    base_url: str,
    metrics_url: str | None,
    expected_runs: int,
) -> dict[str, Any]:
    """Construct Phase 0 session payload."""
    started_at_utc = now_utc_iso()
    return {
        "session_id": session_id,
        "phase": "phase0",
        "container": container,
        "base_url": base_url,
        "metrics_url": metrics_url,
        "expected_runs": expected_runs,
        "started_at_utc": started_at_utc,
        "route": DEFAULT_ROUTE,
        "outputs": list(DEFAULT_OUTPUTS),
    }


def write_session_files(
    session_payload: dict[str, Any],
    evidence_dir: Path,
    current_session_file: Path,
) -> tuple[Path, Path]:
    """Write session files and return (session_dir, session_file)."""
    sessions_dir = evidence_dir / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    session_dir = sessions_dir / str(session_payload["session_id"])
    session_dir.mkdir(parents=True, exist_ok=True)
    session_file = session_dir / "session.json"
    session_file.write_text(json.dumps(session_payload, indent=2), encoding="utf-8")
    current_session_file.parent.mkdir(parents=True, exist_ok=True)
    current_session_file.write_text(
        json.dumps(session_payload, indent=2),
        encoding="utf-8",
    )
    return session_dir, session_file


def export_container_logs_since(
    container: str,
    since_utc: str,
    output_file: Path,
) -> None:
    """Export docker logs since timestamp to file."""
    command = ["docker", "logs", "--since", since_utc, container]
    process = run_command(command, check=False)
    if process.returncode != 0:
        raise RuntimeError(
            f"Failed to export logs from container '{container}'.\n{process.stdout.strip()}"
        )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(process.stdout, encoding="utf-8")


def run_phase0_report(
    report_script: Path,
    app_log: Path,
    report_json: Path,
    route: str,
    outputs: list[str],
    metrics_url: str | None,
    skip_metrics: bool,
) -> None:
    """Execute existing Phase 0 report script against exported stdout log."""
    command: list[str] = [
        sys.executable,
        str(report_script),
        "--app-log",
        str(app_log),
        "--route",
        route,
        "--json-out",
        str(report_json),
        "--outputs",
        *outputs,
    ]
    if skip_metrics or not metrics_url:
        command.append("--skip-metrics")
    else:
        command.extend(["--metrics-url", metrics_url])
    process = run_command(command, check=False)
    print(process.stdout)
    if process.returncode != 0:
        raise RuntimeError("results_phase0_report.py failed")


def _summary_not_null(summary: dict[str, Any] | None) -> bool:
    """Check if summary exists and p95 is numeric."""
    if not isinstance(summary, dict):
        return False
    return summary.get("p95") is not None


def _has_any_metrics(server_dash_metrics: dict[str, Any] | None) -> bool:
    """Return True when at least one dash metric contains p95 value."""
    if not isinstance(server_dash_metrics, dict):
        return False
    for output_payload in server_dash_metrics.values():
        if not isinstance(output_payload, dict):
            continue
        for metric_name in ("duration_seconds", "request_bytes", "response_bytes"):
            metric_payload = output_payload.get(metric_name)
            if isinstance(metric_payload, dict) and metric_payload.get("p95") is not None:
                return True
    return False


def evaluate_phase0_gate(
    report_payload: dict[str, Any],
    expected_runs: int,
) -> dict[str, Any]:
    """Evaluate Phase 0 gate according to modeled criteria."""
    samples_route = int(report_payload.get("samples_route", 0))
    client_timings = report_payload.get("client_timings", {})
    server_timings = report_payload.get("server_callback_timings", {})
    server_dash_metrics = report_payload.get("server_dash_metrics", {})

    click_to_paint_ok = _summary_not_null(client_timings.get("click_to_paint_seconds"))
    request_to_paint_ok = _summary_not_null(
        client_timings.get("request_to_paint_seconds")
    )
    routing_display_page_ok = _summary_not_null(server_timings.get("routing.display_page"))
    min_samples_ok = samples_route >= expected_runs
    metrics_available = _has_any_metrics(server_dash_metrics)

    failures: list[str] = []
    if not min_samples_ok:
        failures.append(
            f"samples_route={samples_route} below expected_runs={expected_runs}"
        )
    if not click_to_paint_ok:
        failures.append("click_to_paint.p95 is null")
    if not request_to_paint_ok:
        failures.append("request_to_paint.p95 is null")
    if not routing_display_page_ok:
        failures.append("routing.display_page.p95 is null")

    if failures:
        status = "FAIL"
    elif metrics_available:
        status = "PASS"
    else:
        status = "PASS_PARTIAL"

    return {
        "status": status,
        "expected_runs": expected_runs,
        "samples_route": samples_route,
        "checks": {
            "min_samples_ok": min_samples_ok,
            "click_to_paint_ok": click_to_paint_ok,
            "request_to_paint_ok": request_to_paint_ok,
            "routing_display_page_ok": routing_display_page_ok,
            "metrics_available": metrics_available,
        },
        "failures": failures,
        "summary": {
            "click_to_paint_p95": client_timings.get("click_to_paint_seconds", {}).get("p95"),
            "request_to_paint_p95": client_timings.get("request_to_paint_seconds", {}).get(
                "p95"
            ),
            "routing_display_page_p95": server_timings.get("routing.display_page", {}).get(
                "p95"
            ),
            "processing_navigate_p95": server_timings.get(
                "processing.navigate_to_results", {}
            ).get("p95"),
        },
    }


def write_gate_markdown(gate_payload: dict[str, Any], target_file: Path) -> None:
    """Write human-readable gate summary markdown."""
    lines: list[str] = []
    lines.append("# Phase 0 Gate Decision")
    lines.append("")
    lines.append(f"- Status: `{gate_payload.get('status')}`")
    lines.append(f"- Evaluated At (UTC): `{now_utc_iso()}`")
    lines.append("")
    lines.append("## Summary")
    summary = gate_payload.get("summary", {})
    lines.append(f"- samples_route: `{gate_payload.get('samples_route')}`")
    lines.append(f"- click_to_paint.p95: `{summary.get('click_to_paint_p95')}`")
    lines.append(f"- request_to_paint.p95: `{summary.get('request_to_paint_p95')}`")
    lines.append(
        f"- routing.display_page.p95: `{summary.get('routing_display_page_p95')}`"
    )
    lines.append(
        f"- processing.navigate_to_results.p95: `{summary.get('processing_navigate_p95')}`"
    )
    lines.append("")
    lines.append("## Checks")
    checks = gate_payload.get("checks", {})
    for key in sorted(checks.keys()):
        lines.append(f"- {key}: `{checks.get(key)}`")
    failures = gate_payload.get("failures", [])
    if failures:
        lines.append("")
        lines.append("## Failures")
        for item in failures:
            lines.append(f"- {item}")
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def command_init(args: argparse.Namespace) -> None:
    """Initialize roadmap status and required folders."""
    root = Path(args.root)
    reports_dir = Path(args.reports_dir)
    evidence_dir = Path(args.evidence_dir)
    status_file = Path(args.status_file)

    ensure_directories(root, reports_dir, evidence_dir)
    payload = load_or_init_status(status_file)
    save_status(status_file, payload)
    print(f"[OK] Initialized roadmap directories under: {root}")
    print(f"[OK] Status file: {status_file}")


def command_show_status(args: argparse.Namespace) -> None:
    """Print status file."""
    status_file = Path(args.status_file)
    payload = load_or_init_status(status_file)
    print(json.dumps(payload, indent=2))


def command_phase0_start(args: argparse.Namespace) -> None:
    """Start Phase 0 session and mark phase in_progress."""
    root = Path(args.root)
    reports_dir = Path(args.reports_dir)
    evidence_dir = Path(args.evidence_dir)
    status_file = Path(args.status_file)
    current_session_file = Path(args.current_session_file)
    ensure_directories(root, reports_dir, evidence_dir)

    status_payload = load_or_init_status(status_file)
    session_id = args.session_id or f"phase0_{now_utc_compact()}"

    session_payload = build_session_payload(
        session_id=session_id,
        container=args.container,
        base_url=args.base_url,
        metrics_url=args.metrics_url,
        expected_runs=args.expected_runs,
    )
    session_dir, session_file = write_session_files(
        session_payload=session_payload,
        evidence_dir=evidence_dir,
        current_session_file=current_session_file,
    )

    health_url = args.base_url.rstrip("/") + "/health"
    health_status = http_status_code(health_url, timeout_seconds=3.0)
    metrics_status = (
        http_status_code(args.metrics_url, timeout_seconds=3.0)
        if args.metrics_url
        else None
    )

    update_phase_status(
        payload=status_payload,
        phase="phase0",
        status="in_progress",
        summary={
            "session_id": session_id,
            "session_file": str(session_file),
            "started_at_utc": session_payload["started_at_utc"],
            "container": args.container,
            "health_status": health_status,
            "metrics_status": metrics_status,
            "expected_runs": args.expected_runs,
        },
    )
    save_status(status_file, status_payload)

    print("[OK] Phase 0 session started")
    print(f"- session_id: {session_id}")
    print(f"- session_file: {session_file}")
    print(f"- current_session: {current_session_file}")
    print(f"- started_at_utc: {session_payload['started_at_utc']}")
    print(f"- health_status: {health_status}")
    print(f"- metrics_status: {metrics_status}")
    print("")
    print("Next:")
    print("1) Execute manual browser flow expected_runs times.")
    print("2) Finalize with:")
    print(
        f"   python {Path(__file__).as_posix()} phase0-finalize "
        f"--session-file {session_file.as_posix()}"
    )
    print(f"   or use --current-session-file {current_session_file.as_posix()}")


def command_phase0_finalize(args: argparse.Namespace) -> None:
    """Finalize Phase 0: export logs, run report, evaluate gate."""
    root = Path(args.root)
    reports_dir = Path(args.reports_dir)
    evidence_dir = Path(args.evidence_dir)
    status_file = Path(args.status_file)
    current_session_file = Path(args.current_session_file)
    report_script = Path(args.report_script)
    ensure_directories(root, reports_dir, evidence_dir)

    status_payload = load_or_init_status(status_file)
    if args.session_file:
        session_file = Path(args.session_file)
    else:
        session_file = current_session_file
    if not session_file.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")
    session_payload = json.loads(session_file.read_text(encoding="utf-8"))

    session_id = str(session_payload["session_id"])
    session_dir = evidence_dir / "sessions" / session_id
    session_dir.mkdir(parents=True, exist_ok=True)

    container = str(session_payload.get("container", args.container))
    started_at_utc = str(session_payload["started_at_utc"])
    expected_runs = int(session_payload.get("expected_runs", args.expected_runs))
    route = str(session_payload.get("route", DEFAULT_ROUTE))
    outputs = list(session_payload.get("outputs", list(DEFAULT_OUTPUTS)))
    metrics_url = session_payload.get("metrics_url", args.metrics_url)

    log_file = session_dir / f"{container}{DEFAULT_PHASE0_LOG_SUFFIX}"
    report_json = session_dir / DEFAULT_PHASE0_REPORT_NAME

    export_container_logs_since(
        container=container,
        since_utc=started_at_utc,
        output_file=log_file,
    )

    run_phase0_report(
        report_script=report_script,
        app_log=log_file,
        report_json=report_json,
        route=route,
        outputs=outputs,
        metrics_url=None if args.skip_metrics else metrics_url,
        skip_metrics=bool(args.skip_metrics),
    )

    report_payload = json.loads(report_json.read_text(encoding="utf-8"))
    gate_payload = evaluate_phase0_gate(
        report_payload=report_payload,
        expected_runs=expected_runs,
    )
    gate_payload["session_id"] = session_id
    gate_payload["started_at_utc"] = started_at_utc
    gate_payload["finalized_at_utc"] = now_utc_iso()
    gate_payload["log_file"] = str(log_file)
    gate_payload["report_json"] = str(report_json)

    gate_json = session_dir / "gate_decision.json"
    gate_md = session_dir / "gate_decision.md"
    gate_json.write_text(json.dumps(gate_payload, indent=2), encoding="utf-8")
    write_gate_markdown(gate_payload, gate_md)

    latest_report_json = reports_dir / DEFAULT_PHASE0_REPORT_NAME
    shutil.copyfile(report_json, latest_report_json)

    latest_gate_json = evidence_dir / "latest_gate.json"
    latest_gate_md = evidence_dir / "latest_gate.md"
    latest_gate_json.write_text(json.dumps(gate_payload, indent=2), encoding="utf-8")
    write_gate_markdown(gate_payload, latest_gate_md)

    phase0_status = gate_payload["status"].lower()
    update_phase_status(
        payload=status_payload,
        phase="phase0",
        status=phase0_status,
        summary={
            "session_id": session_id,
            "status": gate_payload["status"],
            "samples_route": gate_payload.get("samples_route"),
            "click_to_paint_p95": gate_payload.get("summary", {}).get(
                "click_to_paint_p95"
            ),
            "routing_display_page_p95": gate_payload.get("summary", {}).get(
                "routing_display_page_p95"
            ),
            "report_json": str(report_json),
            "gate_json": str(gate_json),
        },
    )
    save_status(status_file, status_payload)

    print("[OK] Phase 0 finalized")
    print(f"- session_id: {session_id}")
    print(f"- status: {gate_payload['status']}")
    print(f"- report_json: {report_json}")
    print(f"- gate_json: {gate_json}")
    print(f"- latest_report_json: {latest_report_json}")
    print(f"- latest_gate_json: {latest_gate_json}")


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser."""
    parser = argparse.ArgumentParser(
        description="Concrete runner for prod optimization roadmap and Phase 0."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    init_cmd = sub.add_parser("init", help="Initialize roadmap folders and status file.")
    init_cmd.add_argument("--root", default=str(DEFAULT_ROOT))
    init_cmd.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    init_cmd.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    init_cmd.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    init_cmd.set_defaults(func=command_init)

    show_cmd = sub.add_parser("show-status", help="Print roadmap status JSON.")
    show_cmd.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    show_cmd.set_defaults(func=command_show_status)

    start_cmd = sub.add_parser("phase0-start", help="Start Phase 0 session.")
    start_cmd.add_argument("--root", default=str(DEFAULT_ROOT))
    start_cmd.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    start_cmd.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    start_cmd.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    start_cmd.add_argument(
        "--current-session-file",
        default=str(DEFAULT_CURRENT_SESSION_FILE),
    )
    start_cmd.add_argument("--session-id", default=None)
    start_cmd.add_argument("--container", default=DEFAULT_CONTAINER)
    start_cmd.add_argument("--base-url", default=DEFAULT_BASE_URL)
    start_cmd.add_argument("--metrics-url", default=DEFAULT_METRICS_URL)
    start_cmd.add_argument("--expected-runs", type=int, default=20)
    start_cmd.set_defaults(func=command_phase0_start)

    finalize_cmd = sub.add_parser("phase0-finalize", help="Finalize Phase 0 session.")
    finalize_cmd.add_argument("--root", default=str(DEFAULT_ROOT))
    finalize_cmd.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    finalize_cmd.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    finalize_cmd.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    finalize_cmd.add_argument(
        "--current-session-file",
        default=str(DEFAULT_CURRENT_SESSION_FILE),
    )
    finalize_cmd.add_argument("--session-file", default=None)
    finalize_cmd.add_argument("--container", default=DEFAULT_CONTAINER)
    finalize_cmd.add_argument("--metrics-url", default=DEFAULT_METRICS_URL)
    finalize_cmd.add_argument("--expected-runs", type=int, default=20)
    finalize_cmd.add_argument("--skip-metrics", action="store_true")
    finalize_cmd.add_argument(
        "--report-script",
        default=str(Path("observability/scripts/results_phase0_report.py")),
    )
    finalize_cmd.set_defaults(func=command_phase0_finalize)

    return parser


def main() -> None:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
