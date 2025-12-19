"""
Module 3 Callbacks Package.

This package contains callback modules for Module 3 use cases
(Functional Similarity Analysis):
- UC-3.1: PCA - Sample Relationships by KO Profile
- UC-3.4: Sample Similarity Based on KO Profiles
- UC-3.5: Sample Similarity Based on Compound Profiles (future)
- UC-3.6: Gene Symbol Co-occurrence Correlogram (future)
- UC-3.7: Compound Co-occurrence Correlogram (future)

Database Compatibility:
- BioRemPP: Primary data source for Sample/KO/Compound correlations

Author: BioRemPP Development Team
Date: 2025-11-24
"""

# UC-3.1: PCA - Sample Relationships by KO Profile
from .uc_3_1_callbacks import register_uc_3_1_callbacks

# UC-3.2: PCA - Sample Relationships by Chemical Profile
from .uc_3_2_callbacks import register_uc_3_2_callbacks

# UC-3.3: Interactive Hierarchical Clustering of Samples
from .uc_3_3_callbacks import register_uc_3_3_callbacks

# UC-3.4: Sample Similarity Based on KO Profiles
from .uc_3_4_callbacks import register_uc_3_4_callbacks

# UC-3.5: Sample Similarity Based on Compound Profiles
from .uc_3_5_callbacks import register_uc_3_5_callbacks

# UC-3.6: Gene Co-occurrence Patterns Across Samples
from .uc_3_6_callbacks import register_uc_3_6_callbacks

# UC-3.7: Compound Co-occurrence Patterns Across Samples
from .uc_3_7_callbacks import register_uc_3_7_callbacks

__all__ = [
    "register_uc_3_1_callbacks",
    "register_uc_3_2_callbacks",
    "register_uc_3_3_callbacks",
    "register_uc_3_4_callbacks",
    "register_uc_3_5_callbacks",
    "register_uc_3_6_callbacks",
    "register_uc_3_7_callbacks",
]
