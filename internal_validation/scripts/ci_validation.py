"""CI entrypoint for GX-first internal validation."""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal_validation.scripts.run_all_gx import run_pipeline


def main() -> int:
    try:
        return run_pipeline(ci_mode=True, open_docs=False)
    except Exception as exc:
        print(f"[ERROR] CI validation execution error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

