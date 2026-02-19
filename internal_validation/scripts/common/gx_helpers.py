"""Great Expectations helpers for context and datasource setup."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

import great_expectations as gx

from .config import ValidationConfig


def get_repo_root() -> Path:
    """Resolve repository root from this file location."""
    return Path(__file__).resolve().parents[3]


def ensure_parent(path: Path) -> None:
    """Ensure parent directory exists."""
    path.parent.mkdir(parents=True, exist_ok=True)


def ensure_gx_context(config: ValidationConfig) -> gx.DataContext:
    """Create/load GX file context based on config."""
    repo_root = get_repo_root()
    context_root = repo_root / config.gx.context_root
    context_root.mkdir(parents=True, exist_ok=True)
    return gx.get_context(context_root_dir=str(context_root), mode="file")


def _delete_asset_if_exists(datasource: object, asset_name: str) -> None:
    try:
        datasource.get_asset(asset_name)
        datasource.delete_asset(asset_name)
    except Exception:
        return


def configure_data_source_from_config(
    context: gx.DataContext, config: ValidationConfig
) -> Dict[str, str]:
    """Create datasource/assets/batch definitions from config."""
    repo_root = get_repo_root()
    base_dir = repo_root / config.gx.datasource_base_directory
    if not base_dir.exists():
        raise FileNotFoundError(f"Datasource base directory not found: {base_dir}")

    datasource = context.data_sources.add_or_update_pandas_filesystem(
        name=config.gx.datasource_name,
        base_directory=str(base_dir),
    )

    created = {}
    for asset_name, asset_cfg in config.gx.assets.items():
        _delete_asset_if_exists(datasource, asset_name)

        asset = datasource.add_csv_asset(name=asset_name, sep=asset_cfg.sep)
        batch_name = f"{asset_name}_full"
        asset.add_batch_definition_path(name=batch_name, path=asset_cfg.file)
        created[asset_name] = batch_name

    return created
