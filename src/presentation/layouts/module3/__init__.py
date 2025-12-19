"""
Module 3 Layouts - Functional Similarity Analysis.

This package contains layout components for Module 3 use cases focused on
sample relationships, clustering, and co-occurrence patterns.

Notes
-----
- See official documentation for detailed use case descriptions
- All layouts follow NumPy-style docstring standards
"""

# UC-3.1: PCA - Sample Relationships by KO Profile
from .uc_3_1_layout import create_uc_3_1_layout

# UC-3.2: PCA - Sample Relationships by Chemical Profile
from .uc_3_2_layout import create_uc_3_2_layout

# UC-3.3: Interactive Hierarchical Clustering of Samples
from .uc_3_3_layout import create_uc_3_3_layout

# UC-3.4: Sample Similarity Based on KO Profiles
from .uc_3_4_layout import create_uc_3_4_layout

# UC-3.5: Sample Similarity Based on Chemical Profiles
from .uc_3_5_layout import create_uc_3_5_layout

# UC-3.6: Gene Co-occurrence Patterns Across Samples
from .uc_3_6_layout import create_uc_3_6_layout

# UC-3.7: Compound Co-occurrence Patterns Across Samples
from .uc_3_7_layout import create_uc_3_7_layout

__all__ = [
    "create_uc_3_1_layout",
    "create_uc_3_2_layout",
    "create_uc_3_3_layout",
    "create_uc_3_4_layout",
    "create_uc_3_5_layout",
    "create_uc_3_6_layout",
    "create_uc_3_7_layout",
]
