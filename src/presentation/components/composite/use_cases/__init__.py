"""
Use Cases Composite Components - Panel Factory Exports.

This module provides the centralized factory for creating use case
informative panels, replacing individual wrapper functions.

Migration Guide
---------------
Old Pattern (deprecated):
>>> from src.presentation.components.composite.use_cases import (
...     create_uc_2_1_panel
... )
>>> panel = create_uc_2_1_panel()

New Pattern (recommended):
>>> from src.presentation.components.composite.use_cases import (
...     create_panel_by_id
... )
>>> panel = create_panel_by_id('uc-2-1')

Batch Creation:
>>> from src.presentation.components.composite.use_cases import (
...     create_panels_batch
... )
>>> panels = create_panels_batch(['uc-2-1', 'uc-2-2', 'uc-2-3'])

Available Panels:
>>> from src.presentation.components.composite.use_cases import (
...     get_available_panels
... )
>>> all_panels = get_available_panels()
>>> # Returns ['uc-1-1', 'uc-1-2', ...]

Notes
-----
All panels are created from YAML configuration files located in:
infrastructure/plot_configs/moduleX/uc_X_Y_panel.yaml

The factory pattern eliminates 55 duplicate wrapper files while
maintaining the same functionality with centralized error handling.

Author: BioRemPP Development Team
Date: 2025-12-04
"""

from src.presentation.components.composite.use_cases.panel_factory import (
    create_panel_by_id,
    create_panels_batch,
)
from src.presentation.components.composite.use_cases.panel_registry import (
    PANEL_REGISTRY,
    get_available_panels,
    get_panel_config_path,
)

__all__ = [
    # Factory functions (recommended)
    "create_panel_by_id",
    "create_panels_batch",
    # Registry utilities
    "get_available_panels",
    "get_panel_config_path",
    "PANEL_REGISTRY",
]
