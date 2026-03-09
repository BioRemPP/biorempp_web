"""Utilities for /results hash navigation normalization and module resolution."""

from __future__ import annotations

import re

_UC_HASH_RE = re.compile(r"^#uc-(?P<module>[1-8])-(?P<uc>\d+)-(?:card|info-panel)$")
_MODULE_HASH_RE = re.compile(r"^#module(?P<module>[1-8])-section$")
_DB_HASHES = {
    "#biorempp-section",
    "#hadeg-section",
    "#toxcsm-section",
    "#kegg-section",
}


def normalize_target_hash(raw_hash: str | None) -> str | None:
    """Normalize incoming hash to canonical targets used by /results."""
    if not isinstance(raw_hash, str):
        return None
    value = raw_hash.strip()
    if not value:
        return None
    if not value.startswith("#"):
        value = f"#{value}"

    uc_match = _UC_HASH_RE.fullmatch(value)
    if uc_match:
        return f"#uc-{uc_match.group('module')}-{uc_match.group('uc')}-card"

    module_match = _MODULE_HASH_RE.fullmatch(value)
    if module_match:
        return value

    if value in _DB_HASHES:
        return value

    return None


def resolve_target_module(target_hash: str | None) -> int | None:
    """Resolve module index (1..8) from canonical /results hash target."""
    if not isinstance(target_hash, str):
        return None

    uc_match = _UC_HASH_RE.fullmatch(target_hash)
    if uc_match:
        return int(uc_match.group("module"))

    module_match = _MODULE_HASH_RE.fullmatch(target_hash)
    if module_match:
        return int(module_match.group("module"))

    return None


def resolve_fallback_hash(target_hash: str | None, module: int | None) -> str | None:
    """Resolve fallback hash when specific UC target is unavailable in DOM."""
    if module is not None and 1 <= int(module) <= 8:
        return f"#module{int(module)}-section"

    normalized = normalize_target_hash(target_hash)
    if normalized in _DB_HASHES:
        return normalized

    return "#module1-section"

