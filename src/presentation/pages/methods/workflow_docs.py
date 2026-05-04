"""Helpers for linking workflow modals to official use case documentation."""

from __future__ import annotations

import re
from typing import Optional


USE_CASE_DOCS_BASE_URL = "https://biorempp-web.readthedocs.io/en/stable/use_cases"
_USE_CASE_ID_PATTERN = re.compile(r"^(?:UC|uc)-(\d+)[.-](\d+)$")


def build_use_case_docs_url(use_case_id: str | None) -> Optional[str]:
    """Build official Read the Docs URL for a use case identifier."""
    if not use_case_id:
        return None

    match = _USE_CASE_ID_PATTERN.match(str(use_case_id).strip())
    if match is None:
        return None

    module_num, case_num = match.groups()
    return (
        f"{USE_CASE_DOCS_BASE_URL}/module{module_num}/"
        f"uc_{module_num}.{case_num}/"
    )
