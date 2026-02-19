"""Shared constants for internal validation."""

from __future__ import annotations


DEFAULT_SEPARATOR = ";"
DEFAULT_ENCODING = "utf-8"
KO_REGEX_DEFAULT = r"^K\d{5}$"


class DatabaseDisplayName:
    """Canonical database display names used by config and reports."""

    BIOREMPP = "BioRemPP"
    KEGG = "KEGG"
    HADEG = "HADEG"
    TOXCSM = "toxCSM"

    ALL = [BIOREMPP, KEGG, HADEG, TOXCSM]
    WITH_KO = [BIOREMPP, KEGG, HADEG]

