"""Hybrid provenance snapshot task."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

from internal_validation.scripts.common import compute_file_sha256, load_csv
from internal_validation.scripts.common.config import ValidationConfig


def run_provenance_snapshot(repo_root: Path, config: ValidationConfig) -> Dict[str, object]:
    """Compute checksums, schema and missingness metadata for all databases."""
    data: Dict[str, object] = {
        "analysis_type": "provenance_snapshot",
        "analysis_date_utc": datetime.now(timezone.utc).isoformat(),
        "databases": {},
    }

    for db_name, rel_path in config.database_paths.as_dict().items():
        full_path = repo_root / rel_path
        df = load_csv(full_path)
        rows = len(df)
        missingness = {}
        for col in df.columns:
            null_count = int(df[col].isna().sum())
            null_pct = round((null_count / rows) * 100, 2) if rows else 0.0
            missingness[col] = {
                "null_count": null_count,
                "null_percentage": null_pct,
            }

        data["databases"][db_name] = {
            "path": str(full_path),
            "sha256": compute_file_sha256(full_path),
            "size_bytes": full_path.stat().st_size,
            "rows": rows,
            "columns": list(df.columns),
            "missingness": missingness,
        }

    return data

