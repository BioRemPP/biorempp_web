"""
Value Objects Module.

Contains immutable domain value objects.

Classes
-------
KO
    KEGG Orthology identifier
SampleId
    Unique sample identifier
Pathway
    KEGG metabolic pathway
Compound
    Chemical compound
"""

from .compound import Compound
from .kegg_orthology import KO
from .pathway import Pathway
from .sample_id import SampleId

__all__ = [
    "KO",
    "SampleId",
    "Pathway",
    "Compound",
]
