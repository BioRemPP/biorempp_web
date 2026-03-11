"""Helpers for compact /results navigation context."""

from __future__ import annotations

from typing import Any

_ALLOWED_METADATA_KEYS = (
    "job_id",
    "sample_count",
    "ko_count",
    "processing_time",
    "matched_kos",
    "total_kos",
    "database_overview",
    "database_aggregate_overview",
)


def build_results_context(payload: Any) -> dict[str, Any]:
    """
    Build a lightweight context payload for /results routing.

    Routing only needs compact metadata. In server payload mode,
    ``merged-result-store`` may contain just a payload reference.
    """
    if not isinstance(payload, dict):
        return {"ready": False, "job_id": None, "metadata": {}}

    metadata_raw = payload.get("metadata")
    metadata: dict[str, Any] = {}
    if isinstance(metadata_raw, dict):
        metadata = {
            key: metadata_raw.get(key)
            for key in _ALLOWED_METADATA_KEYS
            if key in metadata_raw
        }

    job_id = metadata.get("job_id")
    if not isinstance(job_id, str) or not job_id.strip():
        job_id = None

    return {
        "ready": True,
        "job_id": job_id,
        "metadata": metadata,
    }


def context_has_results(context: Any) -> bool:
    """Return True when context marks an available processed result."""
    return bool(isinstance(context, dict) and context.get("ready"))

