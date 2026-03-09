"""Parity comparison helpers between legacy and GX-first outputs."""

from __future__ import annotations

from typing import Any, Dict

from internal_validation.scripts.common import ParityComparisonResult


def compare_run_with_baseline(
    baseline: Dict[str, Any], current: Dict[str, Any]
) -> ParityComparisonResult:
    """Compare current run summary against baseline snapshot."""
    result = ParityComparisonResult(passed=True)

    baseline_schema = baseline.get("legacy", {}).get("schema_integrity", {})
    current_rows = {
        item["validation_definition_name"]: item["statistics"].get("evaluated_expectations", 0)
        for item in current.get("checkpoint_results", [])
    }

    if baseline_schema:
        expected = baseline_schema.get("database_expectation_counts", {})
        mapped = {
            "biorempp_db_schema_integrity_suite": "BioRemPP",
            "kegg_degradation_db_schema_integrity_suite": "KEGG",
            "hadeg_db_schema_integrity_suite": "HADEG",
            "toxcsm_db_schema_integrity_suite": "toxCSM",
        }
        for suite_name, db_name in mapped.items():
            if suite_name not in current_rows:
                result.critical_failures.append(f"missing_validation_definition:{suite_name}")
                continue
            expected_count = expected.get(db_name)
            actual_count = current_rows[suite_name]
            if expected_count is not None and actual_count < max(1, expected_count // 2):
                result.critical_failures.append(
                    f"too_few_expectations:{suite_name}:expected~{expected_count}:actual={actual_count}"
                )

    if not baseline_schema:
        result.warnings.append("baseline_schema_integrity_missing")

    result.passed = len(result.critical_failures) == 0
    result.comparisons["checkpoint_validation_count"] = len(current.get("checkpoint_results", []))
    return result
