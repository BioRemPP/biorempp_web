"""Verify GX setup by loading batches from configured assets."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal_validation.scripts.common import (
    ensure_gx_context,
    get_repo_root,
    load_validation_config,
)


def main() -> int:
    repo_root = get_repo_root()
    config = load_validation_config(
        repo_root / "internal_validation" / "config" / "validation_config.yaml"
    )
    context = ensure_gx_context(config)

    print("=" * 72)
    print("GX Setup Verification")
    print("=" * 72)
    datasources = context.list_datasources()
    print(f"Data sources: {len(datasources)}")
    for ds in datasources:
        if isinstance(ds, dict):
            print(f"  - {ds.get('name', 'unknown')}")
        else:
            print(f"  - {getattr(ds, 'name', str(ds))}")

    datasource = context.data_sources.get(config.gx.datasource_name)
    for asset_name in config.gx.assets:
        asset = datasource.get_asset(asset_name)
        batch_def = asset.get_batch_definition(f"{asset_name}_full")
        batch = batch_def.get_batch()
        df = batch.data.dataframe
        print(f"[OK] {asset_name}: rows={len(df):,} cols={len(df.columns):,}")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
