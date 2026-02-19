"""Create GX checkpoints for schema-only and full validation."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import great_expectations as gx
from great_expectations.checkpoint import UpdateDataDocsAction


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal_validation.scripts.common import (
    ensure_gx_context,
    get_repo_root,
    load_validation_config,
)


def _find_validation_defs(context: gx.DataContext) -> List[gx.ValidationDefinition]:
    return list(context.validation_definitions.all())


def create_checkpoints(context: gx.DataContext, config) -> None:
    """Create schema and full checkpoints from registered validation defs."""
    all_defs = _find_validation_defs(context)
    schema_defs = [vd for vd in all_defs if vd.name.endswith("_schema")]

    full_checkpoint = gx.Checkpoint(
        name=config.gx.checkpoint_names.full,
        validation_definitions=all_defs,
        actions=[UpdateDataDocsAction(name="update_data_docs")],
        result_format={
            "result_format": "COMPLETE",
            "include_unexpected_rows": True,
            "partial_unexpected_count": 20,
        },
    )
    context.checkpoints.add_or_update(full_checkpoint)

    schema_checkpoint = gx.Checkpoint(
        name=config.gx.checkpoint_names.schema,
        validation_definitions=schema_defs,
        actions=[UpdateDataDocsAction(name="update_data_docs")],
        result_format={
            "result_format": "COMPLETE",
            "include_unexpected_rows": True,
            "partial_unexpected_count": 20,
        },
    )
    context.checkpoints.add_or_update(schema_checkpoint)


def main() -> int:
    repo_root = get_repo_root()
    config = load_validation_config(
        repo_root / "internal_validation" / "config" / "validation_config.yaml"
    )
    context = ensure_gx_context(config)
    create_checkpoints(context, config)
    print(f"[OK] Checkpoint created/updated: {config.gx.checkpoint_names.full}")
    print(f"[OK] Checkpoint created/updated: {config.gx.checkpoint_names.schema}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

