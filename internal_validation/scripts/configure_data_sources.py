"""Configure GX datasource, assets and batch definitions from config."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal_validation.scripts.common import (
    configure_data_source_from_config,
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
    created = configure_data_source_from_config(context, config)
    print(f"[OK] Datasource configured: {config.gx.datasource_name}")
    for asset_name, batch_name in created.items():
        print(f"  - {asset_name}: {batch_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

