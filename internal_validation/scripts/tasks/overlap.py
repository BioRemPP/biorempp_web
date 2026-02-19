"""Hybrid KO overlap analysis task."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Set

from internal_validation.scripts.common import load_csv
from internal_validation.scripts.common.config import ValidationConfig


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    return round((len(a & b) / len(union)) if union else 0.0, 4)


def run_cross_database_overlap(repo_root: Path, config: ValidationConfig) -> Dict[str, object]:
    """Compute pairwise KO overlap metrics for BioRemPP, KEGG and HADEG."""
    mapping = config.database_paths.as_dict()
    ko_sources = ["BioRemPP", "KEGG", "HADEG"]
    ko_sets: Dict[str, Set[str]] = {}
    for db in ko_sources:
        df = load_csv(repo_root / mapping[db])
        ko_sets[db] = set(df["ko"].dropna().astype(str).unique()) if "ko" in df.columns else set()

    pairwise = {}
    for i, a in enumerate(ko_sources):
        for b in ko_sources[i + 1 :]:
            inter = ko_sets[a] & ko_sets[b]
            pairwise[f"{a}∩{b}"] = {
                "intersection_size": len(inter),
                "jaccard_index": _jaccard(ko_sets[a], ko_sets[b]),
                "pct_of_a": round((len(inter) / len(ko_sets[a]) * 100), 2) if ko_sets[a] else 0.0,
                "pct_of_b": round((len(inter) / len(ko_sets[b]) * 100), 2) if ko_sets[b] else 0.0,
            }

    shared_all = set.intersection(*ko_sets.values()) if ko_sets else set()
    exclusive = {}
    for db in ko_sources:
        others = [ko_sets[k] for k in ko_sources if k != db]
        union_others = set().union(*others) if others else set()
        exclusive[db] = len(ko_sets[db] - union_others)

    return {
        "analysis_type": "cross_database_overlap",
        "analysis_date_utc": datetime.now(timezone.utc).isoformat(),
        "database_sizes": {db: len(ko_sets[db]) for db in ko_sources},
        "pairwise": pairwise,
        "shared_across_all": len(shared_all),
        "exclusive_counts": exclusive,
    }

