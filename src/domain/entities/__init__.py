"""
Domain Entities Module.

Contains the main business entities of the system.

Classes
-------
Sample
    Aggregate Root representing a biological sample
Dataset
    Aggregate managing a collection of samples
MergedData
    Entity representing merge results with databases
Analysis
    Entity for analysis metadata and tracking
"""

from .analysis import Analysis
from .dataset import Dataset
from .merged_data import MergedData
from .sample import Sample

__all__ = [
    "Sample",
    "Dataset",
    "MergedData",
    "Analysis",
]
