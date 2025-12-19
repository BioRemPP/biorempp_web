"""
Core Operations Module.

This module contains the core application operations and handlers that
orchestrate business workflows. Core operations handle upload processing,
data parsing, merge operations, and result export functionalities.

Classes
-------
UploadHandler
    Handles file upload validation and processing
SampleParser
    Parses input data into domain entities
DataProcessor
    Orchestrates data processing and merge operations
ResultExporter
    Exports analysis results in various formats

Notes
-----
All core operations follow the Single Responsibility Principle and use
dependency injection for testability and maintainability.
"""

from src.application.core.data_processor import DataProcessor
from src.application.core.result_exporter import ResultExporter
from src.application.core.sample_parser import SampleParser
from src.application.core.upload_handler import UploadHandler

__all__ = [
    "UploadHandler",
    "SampleParser",
    "DataProcessor",
    "ResultExporter",
]
