"""Build GX Data Docs for local inspection or CI artifacts."""

from __future__ import annotations

import argparse
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
    parser = argparse.ArgumentParser(description="Build Great Expectations Data Docs")
    parser.add_argument("--no-open", action="store_true", help="Do not open browser")
    args = parser.parse_args()

    repo_root = get_repo_root()
    config = load_validation_config(
        repo_root / "internal_validation" / "config" / "validation_config.yaml"
    )
    context = ensure_gx_context(config)
    context.build_data_docs()
    if not args.no_open:
        context.open_data_docs()

    docs_path = (
        repo_root
        / config.gx.context_root
        / "uncommitted"
        / "data_docs"
        / config.gx.data_docs_site_name
        / "index.html"
    )
    print(f"[OK] Data Docs built: {docs_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

