"""
Merged Data Data Transfer Object.

Defines the MergedDataDTO, an immutable data transfer object that
encapsulates results from database merge operations. Provides structured
data for presenting merge outcomes across multiple databases.

Classes
-------
MergedDataDTO
    Immutable DTO containing merge operation results
"""

from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class MergedDataDTO:
    """
    Immutable DTO for database merge operation results.

    Encapsulates merged data from BioRemPP, HADEG, and ToxCSM databases along
    with metadata about the merge operation.

    Parameters
    ----------
    biorempp_data : pd.DataFrame
        Data merged with BioRemPP database
    hadeg_data : Optional[pd.DataFrame]
        Data merged with HADEG database (None if not merged)
    toxcsm_data : Optional[pd.DataFrame]
        Data merged with ToxCSM database (None if not merged)
    match_count : int
        Number of successful matches across all databases
    total_records : int
        Total number of input records processed
    cache_key : str
        Cache key for storing/retrieving this merge result
    processing_time_seconds : float, default=0.0
        Time taken for merge operation in seconds

    Attributes
    ----------
    biorempp_data : pd.DataFrame
        BioRemPP merged data
    hadeg_data : Optional[pd.DataFrame]
        HADEG merged data
    toxcsm_data : Optional[pd.DataFrame]
        ToxCSM merged data
    match_count : int
        Match count
    total_records : int
        Total records
    cache_key : str
        Cache key
    processing_time_seconds : float
        Processing time

    Notes
    -----
    - This DTO is immutable (frozen)
    - DataFrames should be copied before modification to maintain immutability
    """

    biorempp_data: pd.DataFrame
    hadeg_data: Optional[pd.DataFrame]
    toxcsm_data: Optional[pd.DataFrame]
    match_count: int
    total_records: int
    cache_key: str
    processing_time_seconds: float = 0.0

    def __post_init__(self) -> None:
        """
        Validate DTO consistency.

        Raises
        ------
        ValueError
            If counts are negative or match_count > total_records
        TypeError
            If biorempp_data is not a DataFrame
        """
        if not isinstance(self.biorempp_data, pd.DataFrame):
            raise TypeError("biorempp_data must be a pandas DataFrame")

        if self.match_count < 0 or self.total_records < 0:
            raise ValueError("Counts cannot be negative")

        if self.match_count > self.total_records:
            raise ValueError("match_count cannot exceed total_records")

        if self.processing_time_seconds < 0:
            raise ValueError("processing_time_seconds cannot be negative")

    def match_rate(self) -> float:
        """
        Calculate match rate percentage.

        Returns
        -------
        float
            Percentage of records matched (0.0 to 100.0)
        """
        if self.total_records == 0:
            return 0.0
        return (self.match_count / self.total_records) * 100.0

    def has_hadeg_data(self) -> bool:
        """
        Check if HADEG data is available.

        Returns
        -------
        bool
            True if HADEG data exists
        """
        return self.hadeg_data is not None and not self.hadeg_data.empty

    def has_toxcsm_data(self) -> bool:
        """
        Check if ToxCSM data is available.

        Returns
        -------
        bool
            True if ToxCSM data exists
        """
        return self.toxcsm_data is not None and not self.toxcsm_data.empty
