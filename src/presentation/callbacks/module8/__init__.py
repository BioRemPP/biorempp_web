"""
Module 8 Callbacks Package.

This package contains callback modules for Module 8 use cases,
focusing on metabolic pathway analysis and consortium design.

Modules
-------
uc_8_2_callbacks
    Chemical Class Completeness Scorecard
uc_8_3_callbacks
    Compound-Specific KO Completeness Scorecard
uc_8_4_callbacks
    Pathway Completeness Scorecard for HADEG Pathways
uc_8_5_callbacks
    KEGG Pathway Completeness Scorecard
uc_8_6_callbacks
    Pathway-Centric Consortium Design by KO Coverage
uc_8_7_callbacks
    Intersection of Genes Across Samples

Usage
-----
>>> from src.presentation.callbacks.module8 import register_uc_8_6_callbacks
>>> register_uc_8_6_callbacks(app)
>>> from src.presentation.callbacks.module8 import register_uc_8_7_callbacks
>>> register_uc_8_7_callbacks(app)

Notes
-----
All callback modules follow the pattern:
- register_uc_X_Y_callbacks(app) - Main registration function
- toggle_uc_X_Y_info_panel() - Collapse toggle
- Additional callbacks specific to use case

Author: BioRemPP Development Team
Date: 2025-11-20
"""

from .uc_8_1_callbacks import register_uc_8_1_callbacks
from .uc_8_2_callbacks import register_uc_8_2_callbacks
from .uc_8_3_callbacks import register_uc_8_3_callbacks
from .uc_8_4_callbacks import register_uc_8_4_callbacks
from .uc_8_5_callbacks import register_uc_8_5_callbacks
from .uc_8_6_callbacks import register_uc_8_6_callbacks
from .uc_8_7_callbacks import register_uc_8_7_callbacks

__all__ = [
    "register_uc_8_1_callbacks",
    "register_uc_8_2_callbacks",
    "register_uc_8_3_callbacks",
    "register_uc_8_4_callbacks",
    "register_uc_8_5_callbacks",
    "register_uc_8_6_callbacks",
    "register_uc_8_7_callbacks",
]
