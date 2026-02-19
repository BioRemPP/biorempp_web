"""Configure invariant suites adjusted to real current schemas."""

from __future__ import annotations

from typing import Dict, List

import great_expectations as gx
from great_expectations.expectations import (
    ExpectColumnDistinctValuesToBeInSet,
    ExpectColumnValuesToBeInSet,
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


def _toxcsm_value_columns(context: gx.DataContext, config: ValidationConfig) -> List[str]:
    datasource = context.data_sources.get(config.gx.datasource_name)
    asset = datasource.get_asset("toxcsm_db")
    batch = asset.get_batch_definition("toxcsm_db_full").get_batch()
    df = batch.data.dataframe
    return [c for c in df.columns if c.startswith("value_")]


def _fixed_probability_value_set() -> List[float]:
    # Fixed numeric domain accepted by the consolidated toxCSM snapshot.
    return [round(i / 100.0, 2) for i in range(0, 101)]


def configure_invariants_suites(
    context: gx.DataContext, config: ValidationConfig
) -> Dict[str, gx.ExpectationSuite]:
    """Configure invariant suites for BioRemPP and toxCSM."""
    suites: Dict[str, gx.ExpectationSuite] = {}
    row_counts = config.validation_parameters.expected_row_counts

    biorempp_suite = _reset_suite(context, "biorempp_invariants_suite")
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
    biorempp_suite.add_expectation(
        ExpectColumnDistinctValuesToBeInSet(
            column="referenceAG",
            value_set=config.validation_parameters.allowed_reference_agencies,
        )
    )
    context.suites.add_or_update(biorempp_suite)
    suites["biorempp_db"] = biorempp_suite

    toxcsm_suite = _reset_suite(context, "toxcsm_invariants_suite")
    if "toxcsm_db" not in row_counts:
        raise KeyError("Missing fixed expected row count for asset 'toxcsm_db'")
    toxcsm_suite.add_expectation(
        ExpectTableRowCountToEqual(value=int(row_counts["toxcsm_db"]))
    )
    toxcsm_suite.add_expectation(ExpectColumnValuesToNotBeNull(column="cpd"))
    probability_values = _fixed_probability_value_set()
    for col in _toxcsm_value_columns(context, config):
        toxcsm_suite.add_expectation(
            ExpectColumnValuesToBeInSet(column=col, value_set=probability_values)
        )
    context.suites.add_or_update(toxcsm_suite)
    suites["toxcsm_db"] = toxcsm_suite

    return suites
