"""
Analysis Entity

Represents metadata of an analysis executed in the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class AnalysisStatus(Enum):
    """
    Possible statuses of an analysis.

    Attributes
    ----------
    PENDING : str
        Analysis awaiting execution.
    RUNNING : str
        Analysis in progress.
    COMPLETED : str
        Analysis completed successfully.
    FAILED : str
        Analysis failed.
    CACHED : str
        Result loaded from cache.
    """

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"


@dataclass
class Analysis:
    """
    Entity for analysis metadata.

    Stores information about an analysis that has been or will be executed,
    including identification, status, timestamps, and configurations.

    Parameters
    ----------
    id : str
        Unique identifier for the analysis (e.g., 'UC1_1', 'UC2_3')
    name : str
        Descriptive name of the analysis
    category : str
        Category of the analysis (e.g., 'heatmaps', 'rankings')
    status : AnalysisStatus, default=PENDING
        Current status of the analysis
    created_at : datetime, default=datetime.now()
        Creation timestamp
    started_at : Optional[datetime], default=None
        Execution start timestamp
    completed_at : Optional[datetime], default=None
        Completion timestamp
    config : Dict[str, Any], default={}
        Specific configurations for the analysis
    result_metadata : Dict[str, Any], default={}
        Result metadata
    error_message : Optional[str], default=None
        Error message if it failed

    Notes
    -----
    This entity is used for tracking and auditing analyses.
    """

    id: str
    name: str
    category: str
    status: AnalysisStatus = field(default=AnalysisStatus.PENDING)
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    config: Dict[str, Any] = field(default_factory=dict)
    result_metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None

    def start(self) -> None:
        """
        Marks the analysis as started.

        Notes
        -----
        Updates status to RUNNING and records the start timestamp.
        """
        self.status = AnalysisStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Marks the analysis as successfully completed.

        Parameters
        ----------
        metadata : Optional[Dict[str, Any]], optional
            Result metadata, by default None.

        Notes
        -----
        Updates status to COMPLETED and records the completion timestamp.
        """
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = datetime.now()
        if metadata:
            self.result_metadata.update(metadata)

    def fail(self, error_message: str) -> None:
        """
        Marks the analysis as failed.

        Parameters
        ----------
        error_message : str
            Error message describing the failure.

        Notes
        -----
        Updates status to FAILED and records the error message.
        """
        self.status = AnalysisStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message

    def mark_from_cache(self) -> None:
        """
        Marks the analysis as loaded from cache.

        Notes
        -----
        The CACHED status indicates that the result was retrieved from
        the cache without the need for reprocessing.
        """
        self.status = AnalysisStatus.CACHED
        self.completed_at = datetime.now()

    @property
    def duration_seconds(self) -> Optional[float]:
        """
        Calculates the analysis duration in seconds.

        Returns
        -------
        Optional[float]
            Duration in seconds or None if not finished.
        """
        if self.started_at and self.completed_at:
            delta = self.completed_at - self.started_at
            return delta.total_seconds()
        return None

    @property
    def is_completed(self) -> bool:
        """
        Checks if the analysis is completed (success or failure).

        Returns
        -------
        bool
            True if status is COMPLETED, FAILED, or CACHED.
        """
        return self.status in [
            AnalysisStatus.COMPLETED,
            AnalysisStatus.FAILED,
            AnalysisStatus.CACHED,
        ]

    @property
    def is_successful(self) -> bool:
        """
        Checks if the analysis was successful.

        Returns
        -------
        bool
            True if status is COMPLETED or CACHED.
        """
        return self.status in [
            AnalysisStatus.COMPLETED,
            AnalysisStatus.CACHED,
        ]

    def validate(self) -> None:
        """
        Validates the analysis metadata.

        Raises
        ------
        ValueError
            If ID, name, or category are empty.
        """
        if not self.id or not self.id.strip():
            raise ValueError("Analysis ID cannot be empty")

        if not self.name or not self.name.strip():
            raise ValueError("Analysis name cannot be empty")

        if not self.category or not self.category.strip():
            raise ValueError("Analysis category cannot be empty")

    def __str__(self) -> str:
        """
        Returns the string representation of the analysis.

        Returns
        -------
        str
            Descriptive string.
        """
        return f"Analysis({self.id}: {self.name}) - {self.status.value}"

    def __repr__(self) -> str:
        """
        Returns the debug representation of the analysis.

        Returns
        -------
        str
            Detailed representation.
        """
        return (
            f"Analysis(id='{self.id}', "
            f"name='{self.name}', "
            f"status={self.status})"
        )
