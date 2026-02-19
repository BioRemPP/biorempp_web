"""Create migration baseline snapshot from legacy `.internal_validation` outputs."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from internal_validation.scripts.common import read_json, write_json


def _safe_read(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


def build_snapshot(repo_root: Path) -> Dict[str, Any]:
    legacy_root = repo_root / ".internal_validation" / "outputs_latest"
    index = _safe_read(legacy_root / "index.json")
    schema = _safe_read(legacy_root / "02_schema_integrity" / "summary.json")
    mapping = _safe_read(legacy_root / "04_mapping_consistency" / "summary.json")
    invariants = _safe_read(legacy_root / "06_uc_invariants" / "summary.json")
    vocab = _safe_read(legacy_root / "07_controlled_vocabulary_audit" / "summary.json")

    schema_expectation_counts = {}
    for db_name, payload in schema.items():
        if isinstance(payload, dict):
            keys = [k for k, v in payload.items() if isinstance(v, dict) and "rule" in v]
            schema_expectation_counts[db_name] = len(keys)

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": ".internal_validation/outputs_latest",
        "legacy": {
            "index": {
                "total_scripts": index.get("total_scripts"),
                "successful_scripts": index.get("successful_scripts"),
                "failed_scripts": index.get("failed_scripts"),
            },
            "schema_integrity": {
                "database_expectation_counts": schema_expectation_counts,
                "databases": list(schema.keys()) if isinstance(schema, dict) else [],
            },
            "mapping_consistency": {
                "matched_compounds": mapping.get("toxcsm_linkage", {}).get("matched_compounds"),
                "coverage_percentage": mapping.get("toxcsm_linkage", {}).get("coverage_percentage"),
            },
            "uc_invariants": {
                "datasets_validated": invariants.get("datasets_validated"),
            },
            "vocabulary_audit": {
                "audited_columns": list(vocab.keys()) if isinstance(vocab, dict) else [],
            },
        },
    }


def main() -> int:
    repo_root = REPO_ROOT
    snapshot = build_snapshot(repo_root)
    out = repo_root / "internal_validation" / "docs" / "migration" / "baseline_snapshot.json"
    write_json(out, snapshot)
    print(f"[OK] Baseline snapshot created: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

