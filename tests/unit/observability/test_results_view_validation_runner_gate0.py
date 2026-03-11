"""Unit tests for results_view runner gate0 command."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def _load_runner_module():
    repo_root = Path(__file__).resolve().parents[3]
    module_path = repo_root / "observability" / "scripts" / "results_view_validation_runner.py"
    module_name = "results_view_validation_runner_test_module"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


runner = _load_runner_module()


def _build_args(tmp_path: Path, session_id: str) -> argparse.Namespace:
    root = tmp_path / "results_view"
    return argparse.Namespace(
        root=str(root),
        reports_dir=str(root / "reports"),
        evidence_dir=str(root / "evidence"),
        status_file=str(root / "status.json"),
        session_id=session_id,
        container="biorempp",
        base_url="http://127.0.0.1",
        log_tail_lines=100,
    )


def test_command_gate0_pass(monkeypatch, tmp_path):
    """Gate0 should pass when env and log markers are compliant."""
    args = _build_args(tmp_path, "gate0_test_pass")

    monkeypatch.setattr(runner, "is_container_running", lambda _container: True)
    monkeypatch.setattr(runner, "http_status_code", lambda _url: 200)
    monkeypatch.setattr(
        runner,
        "read_container_environment",
        lambda _container: (dict(runner.GATE0_REQUIRED_ENV), None),
    )
    monkeypatch.setattr(
        runner,
        "export_container_logs_tail",
        lambda **_kwargs: (
            "INFO start\nINFO Results payload transport decision\nINFO end\n"
        ),
    )

    runner.command_gate0(args)

    status_payload = json.loads(Path(args.status_file).read_text(encoding="utf-8"))
    gate0_status = status_payload["phases"]["gate0"]["status"]
    assert gate0_status == "pass"

    decision_path = (
        Path(args.evidence_dir)
        / "gate0"
        / "sessions"
        / "gate0_test_pass"
        / "gate0_decision.json"
    )
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    assert decision["status"] == "PASS"
    assert decision["checks"]["new_transport_log_marker_present"] is True
    assert decision["checks"]["legacy_fallback_log_marker_absent"] is True


def test_command_gate0_fail_when_legacy_marker_present(monkeypatch, tmp_path):
    """Gate0 should fail when legacy marker is present in runtime logs."""
    args = _build_args(tmp_path, "gate0_test_fail")

    monkeypatch.setattr(runner, "is_container_running", lambda _container: True)
    monkeypatch.setattr(runner, "http_status_code", lambda _url: 200)
    monkeypatch.setattr(
        runner,
        "read_container_environment",
        lambda _container: (dict(runner.GATE0_REQUIRED_ENV), None),
    )
    monkeypatch.setattr(
        runner,
        "export_container_logs_tail",
        lambda **_kwargs: (
            "INFO Results payload transport decision\n"
            "WARN Resume payload unavailable for this run\n"
        ),
    )

    runner.command_gate0(args)

    status_payload = json.loads(Path(args.status_file).read_text(encoding="utf-8"))
    gate0_status = status_payload["phases"]["gate0"]["status"]
    assert gate0_status == "fail"

    decision_path = (
        Path(args.evidence_dir)
        / "gate0"
        / "sessions"
        / "gate0_test_fail"
        / "gate0_decision.json"
    )
    decision = json.loads(decision_path.read_text(encoding="utf-8"))
    assert decision["status"] == "FAIL"
    assert decision["checks"]["legacy_fallback_log_marker_absent"] is False


def test_require_gate0_pass_blocks_when_not_approved():
    """Phase commands should still be blocked by default when gate0 is not pass."""
    payload = {
        "phases": {
            "gate0": {"status": "pending"},
        }
    }

    try:
        runner.require_gate0_pass(payload, "phase1-start")
    except RuntimeError as exc:
        assert "requires gate0=pass" in str(exc)
    else:
        raise AssertionError("expected RuntimeError when gate0 is pending")


def test_require_gate0_pass_allows_phase1_only_override():
    """Explicit override should allow phase1-only execution without gate0 pass."""
    payload = {
        "phases": {
            "gate0": {"status": "pending"},
        }
    }

    runner.require_gate0_pass(
        payload,
        "phase1-start",
        allow_without_gate0=True,
    )
