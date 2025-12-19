"""
Module 6 Callbacks Package.

This package contains callback modules for Module 6 use cases
(Hierarchical and Flow-based Functional Analysis):
- UC-6.1: Regulatory to Molecular Interaction Flow (Sankey)
- UC-6.2: Biological Interaction Flow (Sankey)
- UC-6.3: Chemical Hierarchy of Bioremediation (Treemap)
- UC-6.4: Enzymatic Activity Overview (Treemap)
- UC-6.5: Chemical-Enzymatic Landscape by Substrate Scope (Treemap)

Database Compatibility:
- BioRemPP: Primary data source for Sankey flows and treemap hierarchies

Author: BioRemPP Development Team
Date: 2025-11-22
"""

# UC-6.1: Regulatory to Molecular Interaction Flow
from .uc_6_1_callbacks import register_uc_6_1_callbacks

# UC-6.2: Biological Interaction Flow
from .uc_6_2_callbacks import register_uc_6_2_callbacks

# UC-6.3: Chemical Hierarchy of Bioremediation
from .uc_6_3_callbacks import register_uc_6_3_callbacks

# UC-6.4: Overview of Enzymatic Activity and Substrate Scope
from .uc_6_4_callbacks import register_uc_6_4_callbacks

# UC-6.5: Chemical-Enzymatic Landscape by Substrate Scope
from .uc_6_5_callbacks import register_uc_6_5_callbacks

__all__ = [
    "register_uc_6_1_callbacks",
    "register_uc_6_2_callbacks",
    "register_uc_6_3_callbacks",
    "register_uc_6_4_callbacks",
    "register_uc_6_5_callbacks",
]
