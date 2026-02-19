"""Run summary and parity result models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List

from great_expectations.checkpoint.checkpoint import CheckpointResult


@dataclass
class RunSummary:
    """Unified run summary for GX + hybrid tasks."""

    run_id: str
    checkpoint_name: str
    overall_success: bool
    checkpoint_success: bool
    checkpoint_results: List[Dict[str, Any]] = field(default_factory=list)
    hybrid_tasks: Dict[str, Any] = field(default_factory=dict)
    output_version: str = "v2.0.0-gx-first"
    timestamp_utc: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ParityComparisonResult:
    """Result of parity comparison between legacy and GX-first outputs."""

    passed: bool
    critical_failures: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    comparisons: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def checkpoint_result_to_dict(result: CheckpointResult) -> List[Dict[str, Any]]:
    """Convert checkpoint result object to JSON-serializable list."""
    rows: List[Dict[str, Any]] = []
    for identifier, suite_result in result.run_results.items():
        id_str = str(identifier)
        if "::" in id_str and "/" in id_str:
            suite_name = id_str.split("::", 1)[1].split("/", 1)[0]
        else:
            suite_name = id_str
        rows.append(
            {
                "validation_definition_name": suite_name,
                "success": bool(suite_result.success),
                "statistics": dict(suite_result.statistics),
                "failed_expectations": [
                    {
                        "expectation_type": exp.expectation_config.type,
                        "kwargs": dict(exp.expectation_config.kwargs),
                    }
                    for exp in suite_result.results
                    if not exp.success
                ],
            }
        )
    return rows
