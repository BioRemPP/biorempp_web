"""Shared helpers for locating the bundled sample dataset."""

from __future__ import annotations

from pathlib import Path


SAMPLE_DATASET_FILENAME = "exemple_dataset.txt"


def resolve_sample_dataset_path() -> Path:
    """Return the canonical path to the bundled sample dataset."""
    repo_root = Path(__file__).resolve().parents[3]
    candidates = [
        repo_root / "src" / "data" / SAMPLE_DATASET_FILENAME,
        repo_root / "data" / SAMPLE_DATASET_FILENAME,
        repo_root / "data" / "sample_data.txt",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    return candidates[0]
