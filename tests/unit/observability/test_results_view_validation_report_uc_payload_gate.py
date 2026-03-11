"""Unit tests for UC payload request size gate in results_view report."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_report_module():
    repo_root = Path(__file__).resolve().parents[3]
    module_path = repo_root / "observability" / "scripts" / "results_view_validation_report.py"
    module_name = "results_view_validation_report_test_module"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


report = _load_report_module()


def test_phase1_gate_fails_when_uc_request_bytes_exceed_threshold():
    """Phase1 gate must fail when UC request payload exceeds configured threshold."""
    uc_matrix_summary = {
        "expected_count": 56,
        "coverage_complete": True,
        "coverage_ratio": 1.0,
        "duration_p95_max": 1.0,
        "duration_p95_median": 0.5,
    }
    payload_transport_summary = {
        "page_content_request_bytes_p95": 4096.0,
        "uc_request_bytes_p95_max": 1048576.0,
        "uc_request_bytes_violations": ["uc-1-1-chart.children"],
    }

    gate = report._evaluate_phase1_gate(
        uc_matrix_summary=uc_matrix_summary,
        payload_transport_summary=payload_transport_summary,
        metrics_available=True,
        duration_p95_max_threshold=5.0,
        duration_p95_median_threshold=2.5,
        page_content_request_bytes_threshold=65536.0,
        uc_request_bytes_threshold=65536.0,
    )

    assert gate["status"] == "FAIL"
    assert gate["checks"]["uc_request_bytes_ok"] is False
    assert any("UC outputs request_bytes.p95 exceeds threshold" in item for item in gate["failures"])


def test_phase1_gate_passes_when_uc_request_bytes_are_within_threshold():
    """Phase1 gate should pass when UC request payload stays within threshold."""
    uc_matrix_summary = {
        "expected_count": 56,
        "coverage_complete": True,
        "coverage_ratio": 1.0,
        "duration_p95_max": 1.5,
        "duration_p95_median": 0.75,
    }
    payload_transport_summary = {
        "page_content_request_bytes_p95": 2048.0,
        "uc_request_bytes_p95_max": 8192.0,
        "uc_request_bytes_violations": [],
    }

    gate = report._evaluate_phase1_gate(
        uc_matrix_summary=uc_matrix_summary,
        payload_transport_summary=payload_transport_summary,
        metrics_available=True,
        duration_p95_max_threshold=5.0,
        duration_p95_median_threshold=2.5,
        page_content_request_bytes_threshold=65536.0,
        uc_request_bytes_threshold=65536.0,
    )

    assert gate["status"] == "PASS"
    assert gate["checks"]["uc_request_bytes_ok"] is True
