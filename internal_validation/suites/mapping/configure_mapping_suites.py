"""Configure mapping consistency suites."""

from __future__ import annotations

from typing import Dict

import great_expectations as gx
from great_expectations.expectations import (
    ExpectCompoundColumnsToBeUnique,
    ExpectColumnValuesToMatchRegex,
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


def configure_mapping_suites(
    context: gx.DataContext, config: ValidationConfig
) -> Dict[str, gx.ExpectationSuite]:
    """Configure mapping-oriented suites for BioRemPP and toxCSM."""
    suites: Dict[str, gx.ExpectationSuite] = {}
    row_counts = config.validation_parameters.expected_row_counts

    biorempp_suite = _reset_suite(context, "biorempp_mapping_consistency_suite")
    if "biorempp_db" not in row_counts:
        raise KeyError("Missing fixed expected row count for asset 'biorempp_db'")
    biorempp_suite.add_expectation(
        ExpectTableRowCountToEqual(value=int(row_counts["biorempp_db"]))
    )
    biorempp_suite.add_expectation(
        ExpectColumnValuesToMatchRegex(
            column="ko", regex=config.validation_parameters.allowed_ko_regex
        )
    )
    biorempp_suite.add_expectation(ExpectColumnValuesToNotBeNull(column="cpd"))
    context.suites.add_or_update(biorempp_suite)
    suites["biorempp_db"] = biorempp_suite

    toxcsm_suite = _reset_suite(context, "toxcsm_mapping_linkage_suite")
    if "toxcsm_db" not in row_counts:
        raise KeyError("Missing fixed expected row count for asset 'toxcsm_db'")
    toxcsm_suite.add_expectation(
        ExpectTableRowCountToEqual(value=int(row_counts["toxcsm_db"]))
    )
    toxcsm_suite.add_expectation(ExpectColumnValuesToNotBeNull(column="cpd"))
    toxcsm_suite.add_expectation(
        ExpectCompoundColumnsToBeUnique(column_list=["cpd", "SMILES", "ChEBI"])
    )
    context.suites.add_or_update(toxcsm_suite)
    suites["toxcsm_db"] = toxcsm_suite

    return suites
