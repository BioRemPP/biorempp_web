#!/usr/bin/env python
"""Runner for results_view validation suite (phase0 baseline + phase1 UC matrix)."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


DEFAULT_ROOT = Path(".archive/prod_optimization/results_view")
DEFAULT_REPORTS_DIR = DEFAULT_ROOT / "reports"
DEFAULT_EVIDENCE_DIR = DEFAULT_ROOT / "evidence"
DEFAULT_STATUS_FILE = DEFAULT_ROOT / "status.json"
DEFAULT_PHASE0_CURRENT_SESSION_FILE = (
    DEFAULT_EVIDENCE_DIR / "phase0" / "current_session.json"
)
DEFAULT_PHASE1_CURRENT_SESSION_FILE = (
    DEFAULT_EVIDENCE_DIR / "phase1" / "current_session.json"
)
DEFAULT_PHASE0_REPORT_NAME = "results_view_phase0_report.json"
DEFAULT_PHASE1_REPORT_NAME = "results_view_phase1_report.json"
DEFAULT_PHASE0_LOG_SUFFIX = "_stdout_phase0.log"
DEFAULT_PHASE1_LOG_SUFFIX = "_stdout_phase1.log"
DEFAULT_CONTAINER = "biorempp"
DEFAULT_BASE_URL = "http://127.0.0.1"
DEFAULT_METRICS_URL = "http://127.0.0.1:8080/metrics"
DEFAULT_ROUTE = "/results"
DEFAULT_PHASE0_OUTPUTS = ("url.pathname", "page-content.children")
DEFAULT_UC_CATALOG_JSON = DEFAULT_REPORTS_DIR / "uc_outputs_catalog.json"
DEFAULT_UC_CHECKLIST_MD = DEFAULT_ROOT / "05_PHASE1_UC_MATRIX_CHECKLIST.md"
GATE0_REQUIRED_ENV = {
    "BIOREMPP_RESULTS_PAYLOAD_MODE": "server",
    "BIOREMPP_RESULTS_HYDRATION_RETRY_ATTEMPTS": "8",
    "BIOREMPP_RESULTS_HYDRATION_RETRY_DELAY_MS": "250",
    "BIOREMPP_RESUME_SAVE_TIMEOUT_SECONDS": "5.0",
}
GATE0_NEW_LOG_MARKER = "Results payload transport decision"
GATE0_LEGACY_LOG_MARKER = "Resume payload unavailable for this run"
PHASE_KEYS = ("gate0", "phase0", "phase1", "final_gate")


def now_utc_iso() -> str:
    """Return ISO-8601 UTC with second precision."""
    return (
        dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def now_utc_compact() -> str:
    """Return compact UTC string for session IDs."""
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_command(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run command and optionally raise on non-zero return code."""
    process = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if check and process.returncode != 0:
        raise RuntimeError("Command failed: " + " ".join(cmd) + "\n" + process.stdout)
    return process


def emit_console_text(text: str) -> None:
    """Print text in a Windows-safe way when console encoding is cp1252."""
    if not text:
        return
    end = "" if text.endswith("\n") else "\n"
    try:
        print(text, end=end)
    except UnicodeEncodeError:
        encoding = sys.stdout.encoding or "utf-8"
        safe_text = text.encode(encoding, errors="replace").decode(
            encoding, errors="replace"
        )
        print(safe_text, end=end)


def is_container_running(container: str) -> bool:
    """Return True when container name appears in docker ps output."""
    process = run_command(
        ["docker", "ps", "--filter", f"name={container}", "--format", "{{.Names}}"],
        check=False,
    )
    if process.returncode != 0:
        return False
    names = [line.strip() for line in process.stdout.splitlines() if line.strip()]
    return container in names


def ensure_directories(root: Path, reports_dir: Path, evidence_dir: Path) -> None:
    """Ensure suite folder structure exists."""
    root.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / "gate0" / "sessions").mkdir(parents=True, exist_ok=True)
    (evidence_dir / "phase0" / "sessions").mkdir(parents=True, exist_ok=True)
    (evidence_dir / "phase1" / "sessions").mkdir(parents=True, exist_ok=True)


def default_status_payload() -> dict[str, Any]:
    """Create default status payload for results_view suite."""
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
        "suite": "results_view",
        "phases": phases,
    }


def load_or_init_status(status_file: Path) -> dict[str, Any]:
    """Load status file or initialize default structure."""
    if not status_file.exists():
        payload = default_status_payload()
        status_file.parent.mkdir(parents=True, exist_ok=True)
        status_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return payload

    payload = json.loads(status_file.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or "phases" not in payload:
        raise RuntimeError(f"Invalid status payload: {status_file}")
    phases = payload.setdefault("phases", {})
    for phase in PHASE_KEYS:
        phases.setdefault(
            phase,
            {"status": "pending", "updated_at_utc": None, "summary": None},
        )
    return payload


def save_status(status_file: Path, payload: dict[str, Any]) -> None:
    """Persist status payload to disk."""
    payload["updated_at_utc"] = now_utc_iso()
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def update_phase_status(
    payload: dict[str, Any],
    phase: str,
    status: str,
    summary: dict[str, Any] | None = None,
) -> None:
    """Update one phase record in status payload."""
    phase_entry = payload.setdefault("phases", {}).setdefault(
        phase,
        {"status": "pending", "updated_at_utc": None, "summary": None},
    )
    phase_entry["status"] = status
    phase_entry["updated_at_utc"] = now_utc_iso()
    phase_entry["summary"] = summary


def http_status_code(url: str, timeout_seconds: float = 3.0) -> int | None:
    """Return HTTP status code or None when URL is unavailable."""
    try:
        with urlopen(url, timeout=timeout_seconds) as response:  # nosec B310
            return int(getattr(response, "status", 200))
    except URLError:
        return None
    except Exception:
        return None


def export_container_logs_since(container: str, since_utc: str, output_file: Path) -> None:
    """Export docker logs since timestamp to output file."""
    process = run_command(
        ["docker", "logs", "--since", since_utc, container], check=False
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"Failed to export logs from container '{container}'.\n{process.stdout.strip()}"
        )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(process.stdout, encoding="utf-8")


def export_container_logs_tail(
    container: str,
    output_file: Path,
    tail_lines: int = 4000,
) -> str:
    """Export docker logs tail to output file and return exported text."""
    process = run_command(
        ["docker", "logs", "--tail", str(int(tail_lines)), container],
        check=False,
    )
    if process.returncode != 0:
        raise RuntimeError(
            f"Failed to export logs from container '{container}'.\n{process.stdout.strip()}"
        )
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(process.stdout, encoding="utf-8")
    return process.stdout


def read_container_environment(container: str) -> tuple[dict[str, str] | None, str | None]:
    """Read container environment variables using docker exec printenv."""
    process = run_command(
        ["docker", "exec", container, "/bin/sh", "-lc", "printenv"],
        check=False,
    )
    if process.returncode != 0:
        return None, process.stdout.strip()

    env_map: dict[str, str] = {}
    for line in process.stdout.splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        env_map[key] = value.strip()
    return env_map, None


def require_gate0_pass(
    status_payload: dict[str, Any],
    command_name: str,
    allow_without_gate0: bool = False,
) -> None:
    """Require gate0 PASS before executing phase commands."""
    if allow_without_gate0:
        return
    gate0_status = str(
        status_payload.get("phases", {}).get("gate0", {}).get("status", "pending")
    ).lower()
    if gate0_status != "pass":
        raise RuntimeError(
            f"{command_name} requires gate0=pass. "
            "Run gate0 first: python observability/scripts/results_view_validation_runner.py gate0"
        )


def _repo_root() -> Path:
    """Resolve repository root from this script location."""
    return Path(__file__).resolve().parents[2]


def resolve_report_script_path(report_script_value: str) -> Path:
    """Resolve report script path relative to repository root when needed."""
    report_script_path = Path(report_script_value)
    if report_script_path.is_absolute():
        return report_script_path
    return _repo_root() / report_script_path


def discover_uc_outputs() -> list[str]:
    """Discover UC chart outputs from callback source files."""
    callbacks_root = _repo_root() / "src" / "presentation" / "callbacks"
    files = sorted(callbacks_root.glob("module*/uc_*_callbacks.py"))
    pattern = re.compile(r'Output\(\s*"(?P<component_id>uc-[^"]+)"\s*,\s*"children"')

    outputs: list[str] = []
    seen: set[str] = set()
    for file_path in files:
        text = file_path.read_text(encoding="utf-8", errors="replace")
        for match in pattern.finditer(text):
            component_id = match.group("component_id").strip()
            if not (
                component_id.endswith("-chart")
                or component_id.endswith("-chart-container")
            ):
                continue
            dash_output = f"{component_id}.children"
            if dash_output in seen:
                continue
            seen.add(dash_output)
            outputs.append(dash_output)

    outputs.sort()
    return outputs


def uc_label_from_dash_output(dash_output: str) -> str:
    """Convert `uc-X-Y-chart.children` into display label `UC X.Y`."""
    prefix = dash_output.split(".", 1)[0]
    parts = prefix.split("-")
    if len(parts) >= 3 and parts[0] == "uc":
        return f"UC {parts[1]}.{parts[2]}"
    return prefix


def write_uc_checklist_markdown(outputs: list[str], target_file: Path) -> None:
    """Write markdown checklist for full manual UC matrix execution."""
    lines: list[str] = []
    lines.append("# Phase1 UC Matrix Checklist")
    lines.append("")
    lines.append(f"- Generated at: `{now_utc_iso()}`")
    lines.append(f"- Total expected outputs: `{len(outputs)}`")
    lines.append("")
    lines.append("## Manual execution checklist")
    for output in outputs:
        lines.append(f"- [ ] {uc_label_from_dash_output(output)} -> `{output}`")
    target_file.parent.mkdir(parents=True, exist_ok=True)
    target_file.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs_file(outputs: list[str], file_path: Path) -> None:
    """Write outputs list JSON payload."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps({"outputs": outputs}, indent=2), encoding="utf-8")


def write_session_files(
    session_payload: dict[str, Any],
    session_file: Path,
    current_session_file: Path,
) -> None:
    """Persist session payload for direct and current references."""
    session_file.parent.mkdir(parents=True, exist_ok=True)
    current_session_file.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(session_payload, indent=2)
    session_file.write_text(text, encoding="utf-8")
    current_session_file.write_text(text, encoding="utf-8")


def write_gate_markdown(gate_payload: dict[str, Any], target_file: Path, title: str) -> None:
    """Write gate summary markdown."""
    lines: list[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"- Status: `{gate_payload.get('status')}`")
    lines.append(f"- Evaluated At (UTC): `{now_utc_iso()}`")
    lines.append("")
    lines.append("## Summary")
    summary = gate_payload.get("summary", {})
    for key in sorted(summary.keys()):
        lines.append(f"- {key}: `{summary.get(key)}`")
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


def run_validation_report(
    report_script: Path,
    app_log: Path,
    route: str,
    outputs_file: Path,
    report_json: Path,
    metrics_url: str,
    expected_runs: int,
    skip_metrics: bool,
) -> None:
    """Execute unified validation report script."""
    command = [
        sys.executable,
        str(report_script),
        "--app-log",
        str(app_log),
        "--route",
        route,
        "--outputs-file",
        str(outputs_file),
        "--metrics-url",
        metrics_url,
        "--expected-runs",
        str(expected_runs),
        "--json-out",
        str(report_json),
    ]
    if skip_metrics:
        command.append("--skip-metrics")

    process = run_command(command, check=False)
    emit_console_text(process.stdout)
    if process.returncode != 0:
        raise RuntimeError("results_view_validation_report.py failed")


def command_init(args: argparse.Namespace) -> None:
    """Initialize suite root, folders, and status file."""
    root = Path(args.root)
    reports_dir = Path(args.reports_dir)
    evidence_dir = Path(args.evidence_dir)
    status_file = Path(args.status_file)

    ensure_directories(root, reports_dir, evidence_dir)
    payload = load_or_init_status(status_file)
    save_status(status_file, payload)

    print(f"[OK] Initialized results_view suite at: {root}")
    print(f"[OK] Status file: {status_file}")


def command_show_status(args: argparse.Namespace) -> None:
    """Print current status payload."""
    status_file = Path(args.status_file)
    payload = load_or_init_status(status_file)
    print(json.dumps(payload, indent=2))


def command_preflight(args: argparse.Namespace) -> None:
    """Run non-mutating environment checks before manual suite execution."""
    checks: list[tuple[str, bool, str, bool]] = []
    report_script = resolve_report_script_path(str(args.report_script))

    container_ok = is_container_running(args.container)
    checks.append(("container_running", container_ok, args.container, True))

    health_url = args.base_url.rstrip("/") + "/health"
    health_status = http_status_code(health_url)
    checks.append(
        (
            "health_endpoint",
            health_status == 200,
            f"{health_url} status={health_status}",
            True,
        )
    )

    metrics_status = http_status_code(args.metrics_url)
    metrics_ok = metrics_status == 200
    checks.append(
        (
            "metrics_endpoint",
            metrics_ok,
            (
                f"{args.metrics_url} status={metrics_status} "
                "(non-blocking: report has container fallback)"
            ),
            False,
        )
    )

    report_exists = report_script.exists()
    checks.append(("report_script_exists", report_exists, str(report_script), True))

    runner_exists = Path(__file__).exists()
    checks.append(("runner_script_exists", runner_exists, str(Path(__file__)), True))

    outputs = discover_uc_outputs()
    outputs_ok = len(outputs) > 0
    checks.append(("uc_outputs_discovered", outputs_ok, f"count={len(outputs)}", True))

    print("results_view preflight")
    for name, ok, detail, critical in checks:
        if ok:
            status = "PASS"
        elif critical:
            status = "FAIL"
        else:
            status = "WARN"
        print(f"[{status}] {name}: {detail}")

    failed_critical = [name for name, ok, _, critical in checks if (not ok and critical)]
    if failed_critical:
        raise SystemExit(1)


def command_gate0(args: argparse.Namespace) -> None:
    """Run mandatory deploy consistency gate before phase0/phase1."""
    root = Path(args.root)
    reports_dir = Path(args.reports_dir)
    evidence_dir = Path(args.evidence_dir)
    status_file = Path(args.status_file)

    ensure_directories(root, reports_dir, evidence_dir)
    status_payload = load_or_init_status(status_file)

    session_id = args.session_id or f"gate0_{now_utc_compact()}"
    started_at_utc = now_utc_iso()
    session_dir = evidence_dir / "gate0" / "sessions" / session_id
    report_json = session_dir / "gate0_report.json"
    decision_json = session_dir / "gate0_decision.json"
    decision_md = session_dir / "gate0_decision.md"
    log_file = session_dir / f"{args.container}_stdout_gate0.log"

    container_ok = is_container_running(args.container)
    health_url = args.base_url.rstrip("/") + "/health"
    health_status = http_status_code(health_url)

    env_map: dict[str, str] | None = None
    env_error: str | None = None
    if container_ok:
        env_map, env_error = read_container_environment(args.container)
    else:
        env_error = "container not running"

    env_checks: dict[str, dict[str, Any]] = {}
    for env_name, expected in GATE0_REQUIRED_ENV.items():
        actual = env_map.get(env_name) if isinstance(env_map, dict) else None
        env_checks[env_name] = {
            "expected": expected,
            "actual": actual,
            "ok": actual == expected,
        }

    log_error: str | None = None
    log_text = ""
    if container_ok:
        try:
            log_text = export_container_logs_tail(
                container=args.container,
                output_file=log_file,
                tail_lines=args.log_tail_lines,
            )
        except RuntimeError as exc:
            log_error = str(exc)
    else:
        log_error = "container not running"

    new_marker_present = GATE0_NEW_LOG_MARKER in log_text
    legacy_marker_present = GATE0_LEGACY_LOG_MARKER in log_text

    checks = {
        "container_running": container_ok,
        "health_endpoint_ok": health_status == 200,
        "required_env_values_ok": all(
            item.get("ok") is True for item in env_checks.values()
        ),
        "new_transport_log_marker_present": new_marker_present,
        "legacy_fallback_log_marker_absent": not legacy_marker_present,
    }

    failures: list[str] = []
    if not checks["container_running"]:
        failures.append("container is not running")
    if not checks["health_endpoint_ok"]:
        failures.append(f"{health_url} status is {health_status}")
    if not checks["required_env_values_ok"]:
        failures.append("required environment values do not match expected defaults")
    if not checks["new_transport_log_marker_present"]:
        failures.append(
            "runtime log does not contain new transport marker "
            f"'{GATE0_NEW_LOG_MARKER}'"
        )
    if not checks["legacy_fallback_log_marker_absent"]:
        failures.append(
            "runtime log still contains legacy marker "
            f"'{GATE0_LEGACY_LOG_MARKER}'"
        )
    if env_error:
        failures.append(f"failed to read container env: {env_error}")
    if log_error:
        failures.append(f"failed to export container logs: {log_error}")

    status = "PASS" if not failures else "FAIL"
    finalized_at_utc = now_utc_iso()

    report_payload = {
        "generated_at_utc": finalized_at_utc,
        "phase": "gate0",
        "session_id": session_id,
        "container": args.container,
        "health_url": health_url,
        "health_status": health_status,
        "required_env": GATE0_REQUIRED_ENV,
        "env_values": env_checks,
        "env_error": env_error,
        "log_markers": {
            "new_marker": GATE0_NEW_LOG_MARKER,
            "new_marker_present": new_marker_present,
            "legacy_marker": GATE0_LEGACY_LOG_MARKER,
            "legacy_marker_present": legacy_marker_present,
        },
        "log_error": log_error,
        "log_file": str(log_file),
        "checks": checks,
        "failures": failures,
        "status": status,
    }
    report_json.parent.mkdir(parents=True, exist_ok=True)
    report_json.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")

    decision_payload = {
        "status": status,
        "phase": "gate0",
        "session_id": session_id,
        "started_at_utc": started_at_utc,
        "finalized_at_utc": finalized_at_utc,
        "checks": checks,
        "failures": failures,
        "summary": {
            "container": args.container,
            "health_status": health_status,
            "required_env_ok": checks["required_env_values_ok"],
            "new_marker_present": new_marker_present,
            "legacy_marker_present": legacy_marker_present,
        },
        "report_json": str(report_json),
        "log_file": str(log_file),
    }
    decision_json.write_text(json.dumps(decision_payload, indent=2), encoding="utf-8")
    write_gate_markdown(decision_payload, decision_md, title="Gate0 Deploy Decision")

    latest_report_json = evidence_dir / "gate0" / "latest_report.json"
    latest_decision_json = evidence_dir / "gate0" / "latest_gate.json"
    latest_decision_md = evidence_dir / "gate0" / "latest_gate.md"
    latest_report_json.write_text(json.dumps(report_payload, indent=2), encoding="utf-8")
    latest_decision_json.write_text(
        json.dumps(decision_payload, indent=2),
        encoding="utf-8",
    )
    write_gate_markdown(decision_payload, latest_decision_md, title="Gate0 Deploy Decision")

    update_phase_status(
        payload=status_payload,
        phase="gate0",
        status=status.lower(),
        summary={
            "session_id": session_id,
            "status": status,
            "health_status": health_status,
            "required_env_ok": checks["required_env_values_ok"],
            "new_marker_present": new_marker_present,
            "legacy_marker_present": legacy_marker_present,
            "report_json": str(report_json),
            "gate_json": str(decision_json),
        },
    )
    save_status(status_file, status_payload)

    print("[OK] Gate0 completed")
    print(f"- status: {status}")
    print(f"- report_json: {report_json}")
    print(f"- gate_json: {decision_json}")


def command_build_uc_catalog(args: argparse.Namespace) -> None:
    """Generate UC outputs catalog JSON and markdown checklist."""
    outputs = discover_uc_outputs()
    payload = {
        "generated_at_utc": now_utc_iso(),
        "count": len(outputs),
        "outputs": outputs,
    }

    catalog_json = Path(args.catalog_json)
    checklist_md = Path(args.checklist_md)
    catalog_json.parent.mkdir(parents=True, exist_ok=True)
    catalog_json.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_uc_checklist_markdown(outputs, checklist_md)

    print("[OK] UC catalog generated")
    print(f"- outputs_count: {len(outputs)}")
    print(f"- catalog_json: {catalog_json}")
    print(f"- checklist_md: {checklist_md}")


def command_phase0_start(args: argparse.Namespace) -> None:
    """Start phase0 baseline session."""
    root = Path(args.root)
    reports_dir = Path(args.reports_dir)
    evidence_dir = Path(args.evidence_dir)
    status_file = Path(args.status_file)
    current_session_file = Path(args.current_session_file)

    ensure_directories(root, reports_dir, evidence_dir)
    status_payload = load_or_init_status(status_file)
    require_gate0_pass(status_payload, "phase0-start")

    session_id = args.session_id or f"phase0_{now_utc_compact()}"
    started_at_utc = now_utc_iso()

    session_dir = evidence_dir / "phase0" / "sessions" / session_id
    session_file = session_dir / "session.json"
    outputs_file = session_dir / "outputs_phase0.json"
    write_outputs_file(list(DEFAULT_PHASE0_OUTPUTS), outputs_file)

    session_payload = {
        "session_id": session_id,
        "phase": "phase0",
        "container": args.container,
        "base_url": args.base_url,
        "metrics_url": args.metrics_url,
        "started_at_utc": started_at_utc,
        "expected_runs": args.expected_runs,
        "route": args.route,
        "outputs_file": str(outputs_file),
    }
    write_session_files(session_payload, session_file, current_session_file)

    health_status = http_status_code(args.base_url.rstrip("/") + "/health")
    metrics_status = http_status_code(args.metrics_url)

    update_phase_status(
        payload=status_payload,
        phase="phase0",
        status="in_progress",
        summary={
            "session_id": session_id,
            "started_at_utc": started_at_utc,
            "container": args.container,
            "health_status": health_status,
            "metrics_status": metrics_status,
            "expected_runs": args.expected_runs,
            "route": args.route,
            "outputs_file": str(outputs_file),
        },
    )
    save_status(status_file, status_payload)

    print("[OK] Phase0 session started")
    print(f"- session_file: {session_file}")
    print(f"- current_session: {current_session_file}")
    print(f"- outputs_file: {outputs_file}")
    print("Next: execute manual flow expected_runs times and run phase0-finalize.")


def command_phase0_finalize(args: argparse.Namespace) -> None:
    """Finalize phase0 baseline and evaluate phase0 gate."""
    root = Path(args.root)
    reports_dir = Path(args.reports_dir)
    evidence_dir = Path(args.evidence_dir)
    status_file = Path(args.status_file)
    current_session_file = Path(args.current_session_file)
    report_script = resolve_report_script_path(str(args.report_script))

    ensure_directories(root, reports_dir, evidence_dir)
    status_payload = load_or_init_status(status_file)
    require_gate0_pass(status_payload, "phase0-finalize")

    session_file = Path(args.session_file) if args.session_file else current_session_file
    if not session_file.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")
    session_payload = json.loads(session_file.read_text(encoding="utf-8"))

    session_id = str(session_payload["session_id"])
    session_dir = evidence_dir / "phase0" / "sessions" / session_id
    container = str(session_payload.get("container", args.container))
    started_at_utc = str(session_payload["started_at_utc"])
    expected_runs = int(session_payload.get("expected_runs", args.expected_runs))
    route = str(session_payload.get("route", args.route))
    metrics_url = str(session_payload.get("metrics_url", args.metrics_url))
    outputs_file = Path(str(session_payload["outputs_file"]))

    log_file = session_dir / f"{container}{DEFAULT_PHASE0_LOG_SUFFIX}"
    report_json = session_dir / DEFAULT_PHASE0_REPORT_NAME

    export_container_logs_since(
        container=container,
        since_utc=started_at_utc,
        output_file=log_file,
    )
    run_validation_report(
        report_script=report_script,
        app_log=log_file,
        route=route,
        outputs_file=outputs_file,
        report_json=report_json,
        metrics_url=metrics_url,
        expected_runs=expected_runs,
        skip_metrics=bool(args.skip_metrics),
    )

    report_payload = json.loads(report_json.read_text(encoding="utf-8"))
    phase0_gate = report_payload.get("gates", {}).get("phase0", {"status": "FAIL"})

    gate_payload = {
        **phase0_gate,
        "phase": "phase0",
        "session_id": session_id,
        "started_at_utc": started_at_utc,
        "finalized_at_utc": now_utc_iso(),
        "log_file": str(log_file),
        "report_json": str(report_json),
    }

    gate_json = session_dir / "gate_phase0.json"
    gate_md = session_dir / "gate_phase0.md"
    gate_json.write_text(json.dumps(gate_payload, indent=2), encoding="utf-8")
    write_gate_markdown(gate_payload, gate_md, title="Phase0 Gate Decision")

    latest_report_json = reports_dir / DEFAULT_PHASE0_REPORT_NAME
    shutil.copyfile(report_json, latest_report_json)
    latest_gate_json = evidence_dir / "phase0" / "latest_gate.json"
    latest_gate_md = evidence_dir / "phase0" / "latest_gate.md"
    latest_gate_json.write_text(json.dumps(gate_payload, indent=2), encoding="utf-8")
    write_gate_markdown(gate_payload, latest_gate_md, title="Phase0 Gate Decision")

    phase0_status = str(gate_payload.get("status", "FAIL")).lower()
    update_phase_status(
        payload=status_payload,
        phase="phase0",
        status=phase0_status,
        summary={
            "session_id": session_id,
            "status": gate_payload.get("status"),
            "samples_route": gate_payload.get("summary", {}).get("samples_route"),
            "click_to_paint_p95": gate_payload.get("summary", {}).get("click_to_paint_p95"),
            "routing_display_page_p95": gate_payload.get("summary", {}).get(
                "routing_display_page_p95"
            ),
            "report_json": str(report_json),
            "gate_json": str(gate_json),
        },
    )
    save_status(status_file, status_payload)

    print("[OK] Phase0 finalized")
    print(f"- status: {gate_payload.get('status')}")
    print(f"- report_json: {report_json}")
    print(f"- gate_json: {gate_json}")


def command_phase1_start(args: argparse.Namespace) -> None:
    """Start phase1 UC matrix session and discover expected outputs."""
    root = Path(args.root)
    reports_dir = Path(args.reports_dir)
    evidence_dir = Path(args.evidence_dir)
    status_file = Path(args.status_file)
    current_session_file = Path(args.current_session_file)

    ensure_directories(root, reports_dir, evidence_dir)
    status_payload = load_or_init_status(status_file)
    require_gate0_pass(
        status_payload,
        "phase1-start",
        allow_without_gate0=bool(args.allow_without_gate0),
    )

    session_id = args.session_id or f"phase1_{now_utc_compact()}"
    started_at_utc = now_utc_iso()
    outputs = discover_uc_outputs()

    session_dir = evidence_dir / "phase1" / "sessions" / session_id
    session_file = session_dir / "session.json"
    outputs_file = session_dir / "outputs_phase1_uc_matrix.json"
    write_outputs_file(outputs, outputs_file)

    session_payload = {
        "session_id": session_id,
        "phase": "phase1",
        "container": args.container,
        "base_url": args.base_url,
        "metrics_url": args.metrics_url,
        "started_at_utc": started_at_utc,
        "route": args.route,
        "outputs_file": str(outputs_file),
        "expected_outputs": len(outputs),
    }
    write_session_files(session_payload, session_file, current_session_file)

    health_status = http_status_code(args.base_url.rstrip("/") + "/health")
    metrics_status = http_status_code(args.metrics_url)

    update_phase_status(
        payload=status_payload,
        phase="phase1",
        status="in_progress",
        summary={
            "session_id": session_id,
            "started_at_utc": started_at_utc,
            "container": args.container,
            "health_status": health_status,
            "metrics_status": metrics_status,
            "expected_outputs": len(outputs),
            "outputs_file": str(outputs_file),
            "allow_without_gate0": bool(args.allow_without_gate0),
        },
    )
    save_status(status_file, status_payload)

    print("[OK] Phase1 session started")
    print(f"- session_file: {session_file}")
    print(f"- current_session: {current_session_file}")
    print(f"- expected_outputs: {len(outputs)}")
    print(f"- outputs_file: {outputs_file}")
    print("Next: execute full UC matrix manually and run phase1-finalize.")


def command_phase1_finalize(args: argparse.Namespace) -> None:
    """Finalize phase1 UC matrix and evaluate phase1/final gates."""
    root = Path(args.root)
    reports_dir = Path(args.reports_dir)
    evidence_dir = Path(args.evidence_dir)
    status_file = Path(args.status_file)
    current_session_file = Path(args.current_session_file)
    report_script = resolve_report_script_path(str(args.report_script))

    ensure_directories(root, reports_dir, evidence_dir)
    status_payload = load_or_init_status(status_file)
    require_gate0_pass(
        status_payload,
        "phase1-finalize",
        allow_without_gate0=bool(args.allow_without_gate0),
    )

    session_file = Path(args.session_file) if args.session_file else current_session_file
    if not session_file.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")
    session_payload = json.loads(session_file.read_text(encoding="utf-8"))

    session_id = str(session_payload["session_id"])
    session_dir = evidence_dir / "phase1" / "sessions" / session_id
    container = str(session_payload.get("container", args.container))
    started_at_utc = str(session_payload["started_at_utc"])
    route = str(session_payload.get("route", args.route))
    metrics_url = str(session_payload.get("metrics_url", args.metrics_url))
    outputs_file = Path(str(session_payload["outputs_file"]))

    log_file = session_dir / f"{container}{DEFAULT_PHASE1_LOG_SUFFIX}"
    report_json = session_dir / DEFAULT_PHASE1_REPORT_NAME

    export_container_logs_since(
        container=container,
        since_utc=started_at_utc,
        output_file=log_file,
    )
    run_validation_report(
        report_script=report_script,
        app_log=log_file,
        route=route,
        outputs_file=outputs_file,
        report_json=report_json,
        metrics_url=metrics_url,
        expected_runs=1,
        skip_metrics=bool(args.skip_metrics),
    )

    report_payload = json.loads(report_json.read_text(encoding="utf-8"))
    phase1_gate = report_payload.get("gates", {}).get("phase1", {"status": "FAIL"})

    gate_payload = {
        **phase1_gate,
        "phase": "phase1",
        "session_id": session_id,
        "started_at_utc": started_at_utc,
        "finalized_at_utc": now_utc_iso(),
        "log_file": str(log_file),
        "report_json": str(report_json),
    }

    gate_json = session_dir / "gate_phase1.json"
    gate_md = session_dir / "gate_phase1.md"
    gate_json.write_text(json.dumps(gate_payload, indent=2), encoding="utf-8")
    write_gate_markdown(gate_payload, gate_md, title="Phase1 Gate Decision")

    latest_report_json = reports_dir / DEFAULT_PHASE1_REPORT_NAME
    shutil.copyfile(report_json, latest_report_json)
    latest_gate_json = evidence_dir / "phase1" / "latest_gate.json"
    latest_gate_md = evidence_dir / "phase1" / "latest_gate.md"
    latest_gate_json.write_text(json.dumps(gate_payload, indent=2), encoding="utf-8")
    write_gate_markdown(gate_payload, latest_gate_md, title="Phase1 Gate Decision")

    phase1_status = str(gate_payload.get("status", "FAIL")).lower()
    update_phase_status(
        payload=status_payload,
        phase="phase1",
        status=phase1_status,
        summary={
            "session_id": session_id,
            "status": gate_payload.get("status"),
            "coverage_ratio": gate_payload.get("summary", {}).get("coverage_ratio"),
            "duration_p95_max": gate_payload.get("summary", {}).get("duration_p95_max"),
            "duration_p95_median": gate_payload.get("summary", {}).get(
                "duration_p95_median"
            ),
            "report_json": str(report_json),
            "gate_json": str(gate_json),
        },
    )

    gate0_status = str(
        status_payload.get("phases", {}).get("gate0", {}).get("status", "fail")
    ).lower()
    phase0_status = str(
        status_payload.get("phases", {}).get("phase0", {}).get("status", "fail")
    ).lower()
    phase1_only_mode = bool(args.allow_without_gate0)
    if phase1_only_mode:
        if phase1_status == "pass":
            overall_status = "PASS"
        elif phase1_status == "pass_partial":
            overall_status = "PASS_PARTIAL"
        else:
            overall_status = "FAIL"
    else:
        if "fail" in {gate0_status, phase0_status, phase1_status}:
            overall_status = "FAIL"
        elif "pass_partial" in {gate0_status, phase0_status, phase1_status}:
            overall_status = "PASS_PARTIAL"
        elif gate0_status == "pass" and phase0_status == "pass" and phase1_status == "pass":
            overall_status = "PASS"
        else:
            overall_status = "FAIL"
    update_phase_status(
        payload=status_payload,
        phase="final_gate",
        status=overall_status.lower(),
        summary={
            "status": overall_status,
            "gate0_status": gate0_status,
            "phase0_status": status_payload.get("phases", {}).get("phase0", {}).get(
                "status"
            ),
            "phase1_status": phase1_status,
            "phase1_only_mode": phase1_only_mode,
            "report_json": str(report_json),
        },
    )

    save_status(status_file, status_payload)

    print("[OK] Phase1 finalized")
    print(f"- status: {gate_payload.get('status')}")
    print(f"- overall_status: {overall_status}")
    print(f"- report_json: {report_json}")
    print(f"- gate_json: {gate_json}")


def build_parser() -> argparse.ArgumentParser:
    """Build runner CLI parser."""
    parser = argparse.ArgumentParser(
        description="Runner for results_view validation suite."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    preflight_cmd = sub.add_parser("preflight", help="Run environment preflight checks.")
    preflight_cmd.add_argument("--container", default=DEFAULT_CONTAINER)
    preflight_cmd.add_argument("--base-url", default=DEFAULT_BASE_URL)
    preflight_cmd.add_argument("--metrics-url", default=DEFAULT_METRICS_URL)
    preflight_cmd.add_argument(
        "--report-script",
        default=str(Path("observability/scripts/results_view_validation_report.py")),
    )
    preflight_cmd.set_defaults(func=command_preflight)

    gate0_cmd = sub.add_parser("gate0", help="Run gate0 deploy consistency checks.")
    gate0_cmd.add_argument("--root", default=str(DEFAULT_ROOT))
    gate0_cmd.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    gate0_cmd.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    gate0_cmd.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    gate0_cmd.add_argument("--session-id", default=None)
    gate0_cmd.add_argument("--container", default=DEFAULT_CONTAINER)
    gate0_cmd.add_argument("--base-url", default=DEFAULT_BASE_URL)
    gate0_cmd.add_argument("--log-tail-lines", type=int, default=4000)
    gate0_cmd.set_defaults(func=command_gate0)

    catalog_cmd = sub.add_parser(
        "build-uc-catalog",
        help="Generate UC outputs catalog JSON and checklist markdown.",
    )
    catalog_cmd.add_argument("--catalog-json", default=str(DEFAULT_UC_CATALOG_JSON))
    catalog_cmd.add_argument("--checklist-md", default=str(DEFAULT_UC_CHECKLIST_MD))
    catalog_cmd.set_defaults(func=command_build_uc_catalog)

    init_cmd = sub.add_parser("init", help="Initialize results_view suite folders/status.")
    init_cmd.add_argument("--root", default=str(DEFAULT_ROOT))
    init_cmd.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    init_cmd.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    init_cmd.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    init_cmd.set_defaults(func=command_init)

    show_cmd = sub.add_parser("show-status", help="Show suite status JSON.")
    show_cmd.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    show_cmd.set_defaults(func=command_show_status)

    phase0_start = sub.add_parser("phase0-start", help="Start phase0 baseline session.")
    phase0_start.add_argument("--root", default=str(DEFAULT_ROOT))
    phase0_start.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    phase0_start.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    phase0_start.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    phase0_start.add_argument(
        "--current-session-file",
        default=str(DEFAULT_PHASE0_CURRENT_SESSION_FILE),
    )
    phase0_start.add_argument("--session-id", default=None)
    phase0_start.add_argument("--container", default=DEFAULT_CONTAINER)
    phase0_start.add_argument("--base-url", default=DEFAULT_BASE_URL)
    phase0_start.add_argument("--metrics-url", default=DEFAULT_METRICS_URL)
    phase0_start.add_argument("--expected-runs", type=int, default=20)
    phase0_start.add_argument("--route", default=DEFAULT_ROUTE)
    phase0_start.set_defaults(func=command_phase0_start)

    phase0_finalize = sub.add_parser("phase0-finalize", help="Finalize phase0 baseline.")
    phase0_finalize.add_argument("--root", default=str(DEFAULT_ROOT))
    phase0_finalize.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    phase0_finalize.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    phase0_finalize.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    phase0_finalize.add_argument(
        "--current-session-file",
        default=str(DEFAULT_PHASE0_CURRENT_SESSION_FILE),
    )
    phase0_finalize.add_argument("--session-file", default=None)
    phase0_finalize.add_argument("--container", default=DEFAULT_CONTAINER)
    phase0_finalize.add_argument("--metrics-url", default=DEFAULT_METRICS_URL)
    phase0_finalize.add_argument("--expected-runs", type=int, default=20)
    phase0_finalize.add_argument("--route", default=DEFAULT_ROUTE)
    phase0_finalize.add_argument("--skip-metrics", action="store_true")
    phase0_finalize.add_argument(
        "--report-script",
        default=str(Path("observability/scripts/results_view_validation_report.py")),
    )
    phase0_finalize.set_defaults(func=command_phase0_finalize)

    phase1_start = sub.add_parser("phase1-start", help="Start phase1 UC matrix session.")
    phase1_start.add_argument("--root", default=str(DEFAULT_ROOT))
    phase1_start.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    phase1_start.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    phase1_start.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    phase1_start.add_argument(
        "--current-session-file",
        default=str(DEFAULT_PHASE1_CURRENT_SESSION_FILE),
    )
    phase1_start.add_argument("--session-id", default=None)
    phase1_start.add_argument("--container", default=DEFAULT_CONTAINER)
    phase1_start.add_argument("--base-url", default=DEFAULT_BASE_URL)
    phase1_start.add_argument("--metrics-url", default=DEFAULT_METRICS_URL)
    phase1_start.add_argument("--route", default=DEFAULT_ROUTE)
    phase1_start.add_argument("--allow-without-gate0", action="store_true")
    phase1_start.set_defaults(func=command_phase1_start)

    phase1_finalize = sub.add_parser("phase1-finalize", help="Finalize phase1 UC matrix.")
    phase1_finalize.add_argument("--root", default=str(DEFAULT_ROOT))
    phase1_finalize.add_argument("--reports-dir", default=str(DEFAULT_REPORTS_DIR))
    phase1_finalize.add_argument("--evidence-dir", default=str(DEFAULT_EVIDENCE_DIR))
    phase1_finalize.add_argument("--status-file", default=str(DEFAULT_STATUS_FILE))
    phase1_finalize.add_argument(
        "--current-session-file",
        default=str(DEFAULT_PHASE1_CURRENT_SESSION_FILE),
    )
    phase1_finalize.add_argument("--session-file", default=None)
    phase1_finalize.add_argument("--container", default=DEFAULT_CONTAINER)
    phase1_finalize.add_argument("--metrics-url", default=DEFAULT_METRICS_URL)
    phase1_finalize.add_argument("--expected-runs", type=int, default=20)
    phase1_finalize.add_argument("--route", default=DEFAULT_ROUTE)
    phase1_finalize.add_argument("--skip-metrics", action="store_true")
    phase1_finalize.add_argument("--allow-without-gate0", action="store_true")
    phase1_finalize.add_argument(
        "--report-script",
        default=str(Path("observability/scripts/results_view_validation_report.py")),
    )
    phase1_finalize.set_defaults(func=command_phase1_finalize)

    return parser


def main() -> None:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
