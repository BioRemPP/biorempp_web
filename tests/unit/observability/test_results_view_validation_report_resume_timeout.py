"""Unit tests for resume persistence timeout summary in results_view report."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def _load_report_module():
    repo_root = Path(__file__).resolve().parents[3]
    module_path = repo_root / "observability" / "scripts" / "results_view_validation_report.py"
    module_name = "results_view_validation_report_timeout_test_module"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


report = _load_report_module()


def test_resume_persist_timeout_summary_computes_rate_and_distribution():
    """Timeout summary should expose rate per 100 processings and stage split."""
    metrics_text = "\n".join(
        [
            'biorempp_resume_persist_stage_total{stage="saved"} 10',
            'biorempp_resume_persist_stage_total{stage="timed_out_before_store"} 2',
            'biorempp_resume_persist_stage_total{stage="timed_out_after_store"} 1',
            'biorempp_processing_duration_seconds_count{outcome="success"} 20',
            'biorempp_processing_duration_seconds_count{outcome="validation_error"} 5',
        ]
    )

    summary = report._collect_resume_persist_timeout_summary(metrics_text)

    assert summary["metrics_available"] is True
    assert summary["has_stage_metric"] is True
    assert summary["processing_total"] == 25.0
    assert summary["timeout_total"] == 3.0
    assert summary["timeout_rate_per_100_processings"] == 12.0
    assert summary["timeout_stage_counts"]["timed_out_before_store"] == 2.0
    assert summary["timeout_stage_counts"]["timed_out_after_store"] == 1.0
    assert round(summary["timeout_stage_distribution_pct"]["timed_out_before_store"], 2) == 66.67
    assert round(summary["timeout_stage_distribution_pct"]["timed_out_after_store"], 2) == 33.33


def test_resume_persist_timeout_summary_handles_missing_stage_metric():
    """When stage metric is absent, summary should remain safe and non-failing."""
    metrics_text = 'biorempp_processing_duration_seconds_count{outcome="success"} 7'

    summary = report._collect_resume_persist_timeout_summary(metrics_text)

    assert summary["metrics_available"] is True
    assert summary["has_stage_metric"] is False
    assert summary["processing_total"] == 7.0
    assert summary["timeout_total"] == 0.0
    assert summary["timeout_rate_per_100_processings"] == 0.0
    assert summary["timeout_stage_counts"] == {}
