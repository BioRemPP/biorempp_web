"""
Data Tables Module - Results Page Components.

Provides modular data table components for displaying analysis results
with enhanced metadata, on-demand rendering, and download functionality.

Functions
---------
create_biorempp_section
    Create BioRemPP integrated results table section
create_hadeg_section
    Create HADEG pathway analysis table section
create_kegg_section
    Create KEGG degradation pathway table section
create_toxcsm_section
    Create ToxCSM toxicity prediction table section
"""

from .biorempp_table import create_biorempp_section
from .hadeg_table import create_hadeg_section
from .kegg_table import create_kegg_section
from .toxcsm_table import create_toxcsm_section

__all__ = [
    "create_biorempp_section",
    "create_hadeg_section",
    "create_toxcsm_section",
    "create_kegg_section",
]
