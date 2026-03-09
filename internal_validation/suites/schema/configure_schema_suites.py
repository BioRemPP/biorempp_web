"""Configure schema suites for all primary databases."""

from __future__ import annotations

from typing import Dict

import great_expectations as gx
from great_expectations.expectations import (
    ExpectColumnDistinctValuesToBeInSet,
    ExpectColumnToExist,
    ExpectColumnValuesToMatchRegex,
    ExpectColumnValuesToNotBeNull,
    ExpectCompoundColumnsToBeUnique,
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


def _required_cols(config: ValidationConfig, ref: str) -> list[str]:
    return list(config.validation_parameters.required_columns.get(ref, []))


def _expected_row_count(config: ValidationConfig, asset_name: str) -> int:
    row_counts = config.validation_parameters.expected_row_counts
    if asset_name not in row_counts:
        raise KeyError(
            f"Missing fixed expected row count for asset '{asset_name}' in validation_config.yaml"
        )
    return int(row_counts[asset_name])


def configure_schema_suites(
    context: gx.DataContext, config: ValidationConfig
) -> Dict[str, gx.ExpectationSuite]:
    """Configure one schema suite per configured asset."""
    suites: Dict[str, gx.ExpectationSuite] = {}

    for asset_name, asset_cfg in config.gx.assets.items():
        suite_name = f"{asset_name}_schema_integrity_suite"
        suite = _reset_suite(context, suite_name)

        required_cols = _required_cols(config, asset_cfg.required_columns_ref)
        for col in required_cols:
            suite.add_expectation(ExpectColumnToExist(column=col))
            suite.add_expectation(ExpectColumnValuesToNotBeNull(column=col))

        suite.add_expectation(
            ExpectTableRowCountToEqual(value=_expected_row_count(config, asset_name))
        )

        if "ko" in required_cols:
            suite.add_expectation(
                ExpectColumnValuesToMatchRegex(
                    column="ko",
                    regex=config.validation_parameters.allowed_ko_regex,
                )
            )
            suite.add_expectation(ExpectColumnValuesToNotBeNull(column="ko"))

        if len(required_cols) >= 2:
            suite.add_expectation(ExpectCompoundColumnsToBeUnique(column_list=required_cols))

        if asset_cfg.required_columns_ref == "BioRemPP":
            suite.add_expectation(ExpectColumnValuesToNotBeNull(column="cpd"))
            suite.add_expectation(ExpectColumnValuesToNotBeNull(column="compoundclass"))
            suite.add_expectation(
                ExpectColumnDistinctValuesToBeInSet(
                    column="referenceAG",
                    value_set=config.validation_parameters.allowed_reference_agencies,
                )
            )

        context.suites.add_or_update(suite)
        suites[asset_name] = suite

    return suites
