"""Initialize GX file context for internal validation."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal_validation.scripts.common import ensure_gx_context, get_repo_root, load_validation_config


def main() -> int:
    repo_root = get_repo_root()
    config = load_validation_config(
        repo_root / "internal_validation" / "config" / "validation_config.yaml"
    )
    context = ensure_gx_context(config)
    print(f"[OK] GX context ready: {context.root_directory}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

