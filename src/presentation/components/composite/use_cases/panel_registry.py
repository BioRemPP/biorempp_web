"""
Use Case Panel Registry - Centralized Panel Configuration Mapping.

This module provides the single source of truth for all use case panel
configurations, mapping use case IDs to their YAML configuration paths.

Design Pattern
--------------
Registry Pattern: Centralized lookup table eliminating the need for 55
wrapper files with duplicated code.

Author: BioRemPP Development Team
Date: 2025-12-04
"""

from pathlib import Path
from typing import Dict

# Project root reference
_PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent


def _get_config_path(module_num: int, uc_num: int, sub_num: int) -> Path:
    """
    Build configuration path for a use case.

    Parameters
    ----------
    module_num : int
        Module number (1-8)
    uc_num : int
        Use case number within module
    sub_num : int
        Sub-case number

    Returns
    -------
    Path
        Absolute path to YAML configuration file
    """
    return (
        _PROJECT_ROOT
        / "infrastructure"
        / "plot_configs"
        / f"module{module_num}"
        / f"uc_{uc_num}_{sub_num}_panel.yaml"
    )


# Panel Registry: use_case_id → config_path
PANEL_REGISTRY: Dict[str, Path] = {
    # Module 1: Database Analysis
    "uc-1-1": _get_config_path(1, 1, 1),
    "uc-1-2": _get_config_path(1, 1, 2),
    "uc-1-3": _get_config_path(1, 1, 3),
    "uc-1-4": _get_config_path(1, 1, 4),
    "uc-1-5": _get_config_path(1, 1, 5),
    "uc-1-6": _get_config_path(1, 1, 6),
    # Module 2: Functional Richness
    "uc-2-1": _get_config_path(2, 2, 1),
    "uc-2-2": _get_config_path(2, 2, 2),
    "uc-2-3": _get_config_path(2, 2, 3),
    "uc-2-4": _get_config_path(2, 2, 4),
    "uc-2-5": _get_config_path(2, 2, 5),
    # Module 3: Compound-Centric Analysis
    "uc-3-1": _get_config_path(3, 3, 1),
    "uc-3-2": _get_config_path(3, 3, 2),
    "uc-3-3": _get_config_path(3, 3, 3),
    "uc-3-4": _get_config_path(3, 3, 4),
    "uc-3-5": _get_config_path(3, 3, 5),
    "uc-3-6": _get_config_path(3, 3, 6),
    "uc-3-7": _get_config_path(3, 3, 7),
    # Module 4: KO-Centric Analysis
    "uc-4-1": _get_config_path(4, 4, 1),
    "uc-4-2": _get_config_path(4, 4, 2),
    "uc-4-3": _get_config_path(4, 4, 3),
    "uc-4-4": _get_config_path(4, 4, 4),
    "uc-4-5": _get_config_path(4, 4, 5),
    "uc-4-6": _get_config_path(4, 4, 6),
    "uc-4-7": _get_config_path(4, 4, 7),
    "uc-4-8": _get_config_path(4, 4, 8),
    "uc-4-9": _get_config_path(4, 4, 9),
    "uc-4-10": _get_config_path(4, 4, 10),
    "uc-4-11": _get_config_path(4, 4, 11),
    "uc-4-12": _get_config_path(4, 4, 12),
    "uc-4-13": _get_config_path(4, 4, 13),
    # Module 5: Interaction Networks
    "uc-5-1": _get_config_path(5, 5, 1),
    "uc-5-2": _get_config_path(5, 5, 2),
    "uc-5-3": _get_config_path(5, 5, 3),
    "uc-5-4": _get_config_path(5, 5, 4),
    "uc-5-5": _get_config_path(5, 5, 5),
    "uc-5-6": _get_config_path(5, 5, 6),
    # Module 6: Heatmaps
    "uc-6-1": _get_config_path(6, 6, 1),
    "uc-6-2": _get_config_path(6, 6, 2),
    "uc-6-3": _get_config_path(6, 6, 3),
    "uc-6-4": _get_config_path(6, 6, 4),
    "uc-6-5": _get_config_path(6, 6, 5),
    # Module 7: Intersections and Groups
    "uc-7-1": _get_config_path(7, 7, 1),
    "uc-7-2": _get_config_path(7, 7, 2),
    "uc-7-3": _get_config_path(7, 7, 3),
    "uc-7-4": _get_config_path(7, 7, 4),
    "uc-7-5": _get_config_path(7, 7, 5),
    "uc-7-6": _get_config_path(7, 7, 6),
    "uc-7-7": _get_config_path(7, 7, 7),
    # Module 8: Consortium Design
    "uc-8-1": _get_config_path(8, 8, 1),
    "uc-8-2": _get_config_path(8, 8, 2),
    "uc-8-3": _get_config_path(8, 8, 3),
    "uc-8-4": _get_config_path(8, 8, 4),
    "uc-8-5": _get_config_path(8, 8, 5),
    "uc-8-6": _get_config_path(8, 8, 6),
    "uc-8-7": _get_config_path(8, 8, 7),
}


def get_available_panels() -> list[str]:
    """
    Get list of all available panel IDs.

    Returns
    -------
    list[str]
        Sorted list of use case IDs

    Examples
    --------
    >>> panels = get_available_panels()
    >>> print(panels[:3])
    ['uc-1-1', 'uc-1-2', 'uc-1-3']
    """
    return sorted(PANEL_REGISTRY.keys())


def get_panel_config_path(use_case_id: str) -> Path:
    """
    Get configuration path for a specific panel.

    Parameters
    ----------
    use_case_id : str
        Use case identifier (e.g., 'uc-2-1')

    Returns
    -------
    Path
        Absolute path to YAML configuration file

    Raises
    ------
    KeyError
        If use_case_id is not registered

    Examples
    --------
    >>> path = get_panel_config_path('uc-2-1')
    >>> print(path.name)
    uc_2_1_panel.yaml
    """
    if use_case_id not in PANEL_REGISTRY:
        available = get_available_panels()
        raise KeyError(
            f"Panel '{use_case_id}' not found in registry. "
            f"Available panels: {available}"
        )

    return PANEL_REGISTRY[use_case_id]
