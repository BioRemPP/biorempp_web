"""
Module 1 Callbacks Package.

This package contains callback modules for Module 1 use cases:
- UC-1.1: Database Overlap and Unique Contributions Analysis
- UC-1.2: Regulatory Agency Compound Overlap Analysis
- UC-1.3: Proportional Contribution of Reference Agencies (FIGURA 1D)
- UC-1.4: Proportional Functional Diversity of Samples (FIGURA 1E)
- UC-1.5: Regulatory Compliance Scorecard (FIGURA)
- UC-1.6: Sample-Agency Functional Potential Heatmap

Author: BioRemPP Development Team
Date: 2025-11-21
"""

from .uc_1_1_callbacks import register_uc_1_1_callbacks
from .uc_1_2_callbacks import register_uc_1_2_callbacks
from .uc_1_3_callbacks import register_uc_1_3_callbacks
from .uc_1_4_callbacks import register_uc_1_4_callbacks
from .uc_1_5_callbacks import register_uc_1_5_callbacks
from .uc_1_6_callbacks import register_uc_1_6_callbacks

__all__ = [
    "register_uc_1_1_callbacks",
    "register_uc_1_2_callbacks",
    "register_uc_1_3_callbacks",
    "register_uc_1_4_callbacks",
    "register_uc_1_5_callbacks",
    "register_uc_1_6_callbacks",
]
