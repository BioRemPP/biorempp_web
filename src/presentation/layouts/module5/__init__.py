"""
Module 5 Layouts - Interaction Networks.

Provides layout modules for Module 5 use cases (Sample-Compound Interaction
Networks and Similarity Analysis).

Notes
-----
- See official documentation for detailed use case descriptions
"""

# UC-5.1: Sample - Compound Class Interaction Strength
from .uc_5_1_layout import create_uc_5_1_layout

# UC-5.2: Sample Similarity Based on Shared Chemical Profiles
from .uc_5_2_layout import create_uc_5_2_layout

# UC-5.3: Regulatory Relevance of Samples
from .uc_5_3_layout import create_uc_5_3_layout

# UC-5.4: Gene-Compound Interaction Network
from .uc_5_4_layout import create_uc_5_4_layout

# UC-5.5: Gene-Gene Functional Interaction Network
from .uc_5_5_layout import create_uc_5_5_layout

# UC-5.6: Compound-Compound Functional Similarity Network
from .uc_5_6_layout import create_uc_5_6_layout

__all__ = [
    "create_uc_5_1_layout",
    "create_uc_5_2_layout",
    "create_uc_5_3_layout",
    "create_uc_5_4_layout",
    "create_uc_5_5_layout",
    "create_uc_5_6_layout",
]
