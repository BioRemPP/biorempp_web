"""I/O helpers for validation scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .constants import DEFAULT_ENCODING, DEFAULT_SEPARATOR


def load_csv(path: Path, sep: str = DEFAULT_SEPARATOR) -> pd.DataFrame:
    """Load CSV with deterministic defaults."""
    if not path.exists():
        raise FileNotFoundError(f"CSV not found: {path}")
    return pd.read_csv(path, sep=sep, encoding=DEFAULT_ENCODING, low_memory=False)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    """Write JSON with UTF-8 and deterministic indentation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=DEFAULT_ENCODING) as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False, default=str)


def read_json(path: Path) -> Dict[str, Any]:
    """Read JSON payload."""
    with path.open("r", encoding=DEFAULT_ENCODING) as fh:
        return json.load(fh)

