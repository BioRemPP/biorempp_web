"""
Module 7 Callbacks Package - Toxicological Analysis.

This package contains callback modules for all use cases within Module 7
(Toxicological Risk Assessment and Profiling).

Use Cases
---------
UC-7.1
    Comprehensive Toxicological Landscape (Risk Fingerprints)
UC-7.4
    Toxicity Score Distribution by Endpoint Category
UC-7.6
    Sample Risk Mitigation Breadth by Compound Variety
UC-7.7
    Sample Risk Mitigation Depth Profile by Genetic Investment

Architecture
------------
Each use case callback module provides:
- `register_uc_7_X_callbacks(app)`: Main registration function
- Dropdown initialization callbacks
- Chart rendering callbacks
- Panel toggle callbacks

Import Pattern
--------------
>>> from src.presentation.callbacks.module7 import register_uc_7_4_callbacks
>>> register_uc_7_4_callbacks(app)

Notes
-----
All callbacks follow best practices:
- Proper logging with emojis for visibility
- Type hints for parameters and returns
- Comprehensive docstrings
- PreventUpdate for invalid states
- Empty state handling

Database Compatibility:
- ToxCSM: Primary data source for toxicity predictions
- BioRemPP: Required for UC-7.6, UC-7.7 (sample-compound associations)
- KEGG: Not used in Module 7

Author: BioRemPP Development Team
Date: 2025-11-17
"""

# UC-7.1: Faceted Heatmap of Predicted Compound Toxicity Profiles
from .uc_7_1_callbacks import register_uc_7_1_callbacks

# UC-7.2: Concordance Between Predicted Risk and Regulatory Focus
from .uc_7_2_callbacks import register_uc_7_2_callbacks

# UC-7.3: Elite Specialist Identification
from .uc_7_3_callbacks import register_uc_7_3_callbacks

# UC-7.4: Toxicity Score Distribution by Endpoint Category
from .uc_7_4_callbacks import register_uc_7_4_callbacks

# UC-7.5: Interactive Distribution of Toxicity Scores by Endpoint Category
from .uc_7_5_callbacks import register_uc_7_5_callbacks

# UC-7.6: Sample Risk Mitigation Breadth by Compound Variety
from .uc_7_6_callbacks import register_uc_7_6_callbacks

# UC-7.7: Sample Risk Mitigation Depth Profile by Genetic Investment
from .uc_7_7_callbacks import register_uc_7_7_callbacks

__all__ = [
    "register_uc_7_1_callbacks",
    "register_uc_7_2_callbacks",
    "register_uc_7_3_callbacks",
    "register_uc_7_4_callbacks",
    "register_uc_7_5_callbacks",
    "register_uc_7_6_callbacks",
    "register_uc_7_7_callbacks",
]
