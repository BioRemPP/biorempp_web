"""Create and update GX suites and validation definitions."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Iterable, Tuple

import great_expectations as gx


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal_validation.scripts.common import (
    ensure_gx_context,
    get_repo_root,
    load_validation_config,
)
from internal_validation.suites.invariants import configure_invariants_suites
from internal_validation.suites.mapping import configure_mapping_suites
from internal_validation.suites.schema import configure_schema_suites
from internal_validation.suites.vocabulary import configure_vocabulary_suites


def _upsert_validation_definition(
    context: gx.DataContext,
    name: str,
    asset_name: str,
    suite: gx.ExpectationSuite,
    datasource_name: str,
) -> gx.ValidationDefinition:
    datasource = context.data_sources.get(datasource_name)
    asset = datasource.get_asset(asset_name)
    batch_def = asset.get_batch_definition(f"{asset_name}_full")
    vd = gx.ValidationDefinition(name=name, data=batch_def, suite=suite)
    return context.validation_definitions.add_or_update(vd)


def _pairs_from_suites(
    suite_map: Dict[str, gx.ExpectationSuite],
    name_suffix: str,
) -> Iterable[Tuple[str, str, gx.ExpectationSuite]]:
    for asset_name, suite in suite_map.items():
        yield (f"validate_{asset_name}_{name_suffix}", asset_name, suite)


def create_all_validation_definitions(context: gx.DataContext, config) -> Dict[str, str]:
    """Configure suites and create all validation definitions."""
    schema_suites = configure_schema_suites(context, config)
    mapping_suites = configure_mapping_suites(context, config)
    invariants_suites = configure_invariants_suites(context, config)
    vocabulary_suites = configure_vocabulary_suites(context, config)

    created: Dict[str, str] = {}
    for vd_name, asset_name, suite in _pairs_from_suites(schema_suites, "schema"):
        _upsert_validation_definition(context, vd_name, asset_name, suite, config.gx.datasource_name)
        created[vd_name] = suite.name
    for vd_name, asset_name, suite in _pairs_from_suites(mapping_suites, "mapping"):
        _upsert_validation_definition(context, vd_name, asset_name, suite, config.gx.datasource_name)
        created[vd_name] = suite.name
    for vd_name, asset_name, suite in _pairs_from_suites(invariants_suites, "invariants"):
        _upsert_validation_definition(context, vd_name, asset_name, suite, config.gx.datasource_name)
        created[vd_name] = suite.name
    for vd_name, asset_name, suite in _pairs_from_suites(vocabulary_suites, "vocabulary"):
        _upsert_validation_definition(context, vd_name, asset_name, suite, config.gx.datasource_name)
        created[vd_name] = suite.name

    return created


def main() -> int:
    repo_root = get_repo_root()
    config = load_validation_config(
        repo_root / "internal_validation" / "config" / "validation_config.yaml"
    )
    context = ensure_gx_context(config)
    created = create_all_validation_definitions(context, config)
    print(f"[OK] Validation definitions upserted: {len(created)}")
    for vd_name, suite_name in sorted(created.items()):
        print(f"  - {vd_name} -> {suite_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
