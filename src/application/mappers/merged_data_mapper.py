"""
Application Layer - Merged Data Mapper.

Maps between MergedData domain entities and MergedDataDTO for application
layer operations.

Classes
-------
MergedDataMapper
    Bidirectional mapping between MergedData entity and DTO

Notes
-----
- Stateless mapper
- Preserves DataFrame references (no copying)
- Handles optional database results
"""

from typing import Optional

import pandas as pd

from src.application.dto.merged_data_dto import MergedDataDTO
from src.domain.entities.merged_data import MergedData


class MergedDataMapper:
    """
    Map between MergedData entity and MergedDataDTO.

    Converts between the domain MergedData entity and the application layer
    DTO used for data transfer.

    Methods
    -------
    to_dto(entity, cache_key, processing_time)
        Convert MergedData entity to DTO
    from_dto(dto)
        Convert DTO to MergedData entity

    Notes
    -----
    - All methods are static (stateless)
    - Does not copy DataFrames (shares references)
    - Preserves all metadata
    """

    @staticmethod
    def to_dto(
        entity: MergedData, cache_key: str, processing_time_seconds: float = 0.0
    ) -> MergedDataDTO:
        """
        Convert MergedData entity to DTO.

        Parameters
        ----------
        entity : MergedData
            Domain entity with merged data
        cache_key : str
            Cache key for this merge operation
        processing_time_seconds : float, default=0.0
            Time taken for processing

        Returns
        -------
        MergedDataDTO
            Immutable DTO for application layer

        Notes
        -----
        - Shares DataFrame references (no copying)
        - Adds cache_key and processing_time metadata
        - Preserves all optional database results
        """
        # Calculate match_count and total_records from data
        match_count = 0

        if entity.biorempp_data is not None and isinstance(
            entity.biorempp_data, pd.DataFrame
        ):
            match_count = len(entity.biorempp_data)

        # total_records should be at least match_count
        total_records = (
            len(entity.original_dataset.samples) if entity.original_dataset else 0
        )
        if total_records < match_count:
            total_records = match_count

        return MergedDataDTO(
            biorempp_data=entity.biorempp_data,
            hadeg_data=entity.hadeg_data,
            toxcsm_data=entity.toxcsm_data,
            match_count=match_count,
            total_records=total_records,
            cache_key=cache_key,
            processing_time_seconds=processing_time_seconds,
        )

    @staticmethod
    def from_dto(dto: MergedDataDTO) -> MergedData:
        """
        Convert DTO to MergedData entity.

        Parameters
        ----------
        dto : MergedDataDTO
            Application layer DTO

        Returns
        -------
        MergedData
            Reconstructed domain entity

        Notes
        -----
        - Shares DataFrame references (no copying)
        - Loses cache_key and processing_time (domain doesn't need them)
        - Preserves all database results
        """
        from src.domain.entities.dataset import Dataset

        return MergedData(
            original_dataset=Dataset([]),  # Empty dataset as we don't store it in DTO
            biorempp_data=dto.biorempp_data,
            hadeg_data=dto.hadeg_data,
            toxcsm_data=dto.toxcsm_data,
        )

    @staticmethod
    def create_empty_dto(cache_key: str) -> MergedDataDTO:
        """
        Create empty DTO for no matches scenario.

        Parameters
        ----------
        cache_key : str
            Cache key for this operation

        Returns
        -------
        MergedDataDTO
            DTO with empty DataFrames and zero counts

        Notes
        -----
        - Useful when no matches found in database
        - All DataFrames are empty but not None
        - Maintains DTO structure consistency
        """
        empty_df = pd.DataFrame()
        return MergedDataDTO(
            biorempp_data=empty_df,
            hadeg_data=empty_df,
            toxcsm_data=empty_df,
            match_count=0,
            total_records=0,
            cache_key=cache_key,
            processing_time_seconds=0.0,
        )
