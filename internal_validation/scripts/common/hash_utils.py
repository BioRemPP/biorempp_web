"""Hash helpers for files and dataframes."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


def compute_file_sha256(path: Path) -> str:
    """Compute SHA256 for a file."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_dataframe_hash(df: pd.DataFrame, normalize: bool = True) -> str:
    """Compute deterministic hash for dataframe content."""
    local = df.copy()
    if normalize and not local.empty:
        local = local.reindex(sorted(local.columns), axis=1)
        local = local.sort_values(by=list(local.columns)).reset_index(drop=True)
    raw = local.to_csv(index=False, sep=";", encoding="utf-8").encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

