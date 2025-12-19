"""
Module 5 Callbacks Package - Interaction Networks.

This package contains callback modules for all use cases within Module 5
(Sample-Compound Interaction Networks and Similarity Analysis).

Use Cases
---------
UC-5.1
    Sample - Compound Class Interaction Strength (Chord Diagram)
UC-5.2
    Sample Similarity via Shared Compounds (Chord Diagram)
UC-5.3
    Sample - Regulatory Agency Interactions (Chord Diagram)

Architecture
------------
Each use case callback module provides:
- `register_uc_5_X_callbacks(app)`: Main registration function
- Informative panel toggle callbacks
- Chart rendering callbacks (on-demand)

Import Pattern
--------------
>>> from src.presentation.callbacks.module5 import register_uc_5_1_callbacks
>>> register_uc_5_1_callbacks(app)

Notes
-----
All callbacks follow best practices:
- Proper logging with module prefix
- Type hints for parameters and returns
- Comprehensive docstrings
- PreventUpdate for invalid states
- Empty state handling

Database Compatibility:
- BioRemPP: Primary data source for interaction networks
- Uses ChordStrategy for visualization

Author: BioRemPP Development Team
Date: 2025-11-23
"""

# UC-5.1: Sample - Compound Class Interaction Strength
from .uc_5_1_callbacks import register_uc_5_1_callbacks

# UC-5.2: Sample Similarity Based on Shared Chemical Profiles
from .uc_5_2_callbacks import register_uc_5_2_callbacks

# UC-5.3: Regulatory Relevance of Samples
from .uc_5_3_callbacks import register_uc_5_3_callbacks

# UC-5.4: Gene-Compound Interaction Network
from .uc_5_4_callbacks import register_uc_5_4_callbacks

# UC-5.5: Gene-Gene Functional Interaction Network
from .uc_5_5_callbacks import register_uc_5_5_callbacks

# UC-5.6: Compound-Compound Functional Similarity Network
from .uc_5_6_callbacks import register_uc_5_6_callbacks

__all__ = [
    "register_uc_5_1_callbacks",
    "register_uc_5_2_callbacks",
    "register_uc_5_3_callbacks",
    "register_uc_5_4_callbacks",
    "register_uc_5_5_callbacks",
    "register_uc_5_6_callbacks",
]
