"""
Data Transfer Objects (DTOs) Module.

This module contains immutable data transfer objects that encapsulate
data crossing layer boundaries. DTOs prevent tight coupling between
layers and provide clear contracts for data exchange.

Classes
-------
UploadResultDTO
    Encapsulates upload operation results with validation status
ValidationResultDTO
    Contains validation results with detailed error messages
MergedDataDTO
    Represents merged data results from database integration
ProcessingProgressDTO
    Encapsulates processing progress information

Notes
-----
All DTOs are immutable frozen dataclasses to ensure data integrity
across layer boundaries. They contain only data, no business logic.
"""

from src.application.dto.merged_data_dto import MergedDataDTO
from src.application.dto.processing_progress_dto import ProcessingProgressDTO
from src.application.dto.upload_result_dto import UploadResultDTO
from src.application.dto.validation_result_dto import ValidationResultDTO

__all__ = [
    "UploadResultDTO",
    "ValidationResultDTO",
    "MergedDataDTO",
    "ProcessingProgressDTO",
]
