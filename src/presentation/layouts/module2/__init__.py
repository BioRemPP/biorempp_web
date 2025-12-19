"""
Module 2 Layouts - Sample Richness Analysis.

This package contains layout components for Module 2 use cases focused on
ranking samples by functional and compound richness.

Notes
-----
- See official documentation for detailed use case descriptions
- All layouts follow NumPy-style docstring standards
"""

from .uc_2_1_layout import create_uc_2_1_layout
from .uc_2_2_layout import create_uc_2_2_layout
from .uc_2_3_layout import create_uc_2_3_layout
from .uc_2_4_layout import create_uc_2_4_layout
from .uc_2_5_layout import create_uc_2_5_layout

__all__ = [
    "create_uc_2_1_layout",
    "create_uc_2_2_layout",
    "create_uc_2_3_layout",
    "create_uc_2_4_layout",
    "create_uc_2_5_layout",
]
