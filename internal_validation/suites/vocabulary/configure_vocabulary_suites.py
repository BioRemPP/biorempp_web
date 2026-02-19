"""Configure vocabulary suites for controlled fields."""

from __future__ import annotations

from typing import Dict

import great_expectations as gx
from great_expectations.expectations import (
    ExpectColumnDistinctValuesToBeInSet,
    ExpectColumnValuesToNotBeNull,
    ExpectTableRowCountToEqual,
)

from internal_validation.scripts.common.config import ValidationConfig


def _reset_suite(context: gx.DataContext, suite_name: str) -> gx.ExpectationSuite:
    try:
        suite = context.suites.get(suite_name)
        suite.expectations = []
    except Exception:
        suite = context.suites.add(gx.ExpectationSuite(name=suite_name))
    return suite


def configure_vocabulary_suites(
    context: gx.DataContext, config: ValidationConfig
) -> Dict[str, gx.ExpectationSuite]:
    """Configure vocabulary audit suite for BioRemPP."""
    suite = _reset_suite(context, "biorempp_vocabulary_suite")
    row_counts = config.validation_parameters.expected_row_counts
    if "biorempp_db" not in row_counts:
        raise KeyError("Missing fixed expected row count for asset 'biorempp_db'")
    suite.add_expectation(
        ExpectTableRowCountToEqual(value=int(row_counts["biorempp_db"]))
    )
    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="compoundclass"))
    suite.add_expectation(ExpectColumnValuesToNotBeNull(column="enzyme_activity"))
    suite.add_expectation(
        ExpectColumnDistinctValuesToBeInSet(
            column="referenceAG",
            value_set=config.validation_parameters.allowed_reference_agencies,
        )
    )
    context.suites.add_or_update(suite)
    return {"biorempp_db": suite}
