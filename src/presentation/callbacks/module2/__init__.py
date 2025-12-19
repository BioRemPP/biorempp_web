"""
Module 2 Callbacks - Rankings and Compound Analysis.

This module exports callback registration functions for all Use Cases
in Module 2.

Use Cases
---------
UC-2.1 : Ranking of Samples by KO Richness
UC-2.2 : Ranking of Samples by Compound Richness
UC-2.3 : Ranking of Compounds by Sample Diversity per Chemical Class
UC-2.4 : Ranking of Compounds by Genetic Interaction within Chemical Classes
UC-2.5 : Distribution of KO Across Samples

Functions
---------
register_uc_2_1_callbacks
    Register UC-2.1 callbacks (database toggle, render, slider).
register_uc_2_2_callbacks
    Register UC-2.2 callbacks (database toggle, render, slider).
register_uc_2_3_callbacks
    Register UC-2.3 callbacks (dropdown init, render).
register_uc_2_4_callbacks
    Register UC-2.4 callbacks (dropdown init, render, collapse).
register_uc_2_5_callbacks
    Register UC-2.5 callbacks (collapse only - processing pending).

Notes
-----
All callbacks use inline data processing (no separate processing modules).

Author: BioRemPP Development Team
Date: 2025-11-16
"""

from .uc_2_1_callbacks import register_uc_2_1_callbacks
from .uc_2_2_callbacks import register_uc_2_2_callbacks
from .uc_2_3_callbacks import register_uc_2_3_callbacks
from .uc_2_4_callbacks import register_uc_2_4_callbacks
from .uc_2_5_callbacks import register_uc_2_5_callbacks

__all__ = [
    "register_uc_2_1_callbacks",
    "register_uc_2_2_callbacks",
    "register_uc_2_3_callbacks",
    "register_uc_2_4_callbacks",
    "register_uc_2_5_callbacks",
]
