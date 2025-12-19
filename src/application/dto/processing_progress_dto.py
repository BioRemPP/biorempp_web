"""
Processing Progress Data Transfer Object.

Defines the ProcessingProgressDTO, an immutable data transfer object that
encapsulates processing progress information. Provides real-time feedback on
multi-stage processing operations.

Classes
-------
ProcessingProgressDTO
    Immutable DTO containing processing progress information
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ProcessingProgressDTO:
    """
    Deprecated Immutable DTO for processing progress information.
    """

    current_stage: str
    stage_number: int
    total_stages: int
    progress_percentage: float
    message: str = ""
    estimated_time_remaining: Optional[float] = None
    error: Optional[str] = None

    def __post_init__(self) -> None:
        """
        Validate DTO consistency.

        Raises
        ------
        ValueError
            If stage numbers invalid or percentage out of range
        """
        if self.stage_number < 1 or self.stage_number > self.total_stages:
            raise ValueError(f"stage_number must be between 1 and {self.total_stages}")

        if not 0.0 <= self.progress_percentage <= 100.0:
            raise ValueError("progress_percentage must be between 0.0 and 100.0")

        if self.total_stages < 1:
            raise ValueError("total_stages must be at least 1")

        if (
            self.estimated_time_remaining is not None
            and self.estimated_time_remaining < 0
        ):
            raise ValueError("estimated_time_remaining cannot be negative")

    def is_complete(self) -> bool:
        """
        Check if processing is complete.

        Returns
        -------
        bool
            True if progress is 100%
        """
        return self.progress_percentage >= 100.0

    def has_error(self) -> bool:
        """
        Check if processing has error.

        Returns
        -------
        bool
            True if error exists
        """
        return self.error is not None

    def is_final_stage(self) -> bool:
        """
        Check if currently on final stage.

        Returns
        -------
        bool
            True if on last stage
        """
        return self.stage_number == self.total_stages
