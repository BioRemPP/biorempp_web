"""
Unit tests for MergedDataMapper.

Tests cover:
- Entity to DTO conversion
- DTO to entity conversion
- Empty DTO creation
- Metadata preservation
- DataFrame reference sharing
"""

import pytest
import pandas as pd

from biorempp_web.src.application.mappers.merged_data_mapper import (
    MergedDataMapper
)
from biorempp_web.src.domain.entities.merged_data import MergedData
from biorempp_web.src.domain.entities.dataset import Dataset
from biorempp_web.src.application.dto.merged_data_dto import MergedDataDTO


class TestMergedDataMapperToDTO:
    """Test MergedData entity to DTO conversion."""

    def test_to_dto_with_all_databases(self):
        """Test converting entity with all database results."""
        biorempp_df = pd.DataFrame({"KO": ["K00001"], "Compound": ["C1"]})
        hadeg_df = pd.DataFrame({"KO": ["K00001"], "HADEG": ["H1"]})
        toxcsm_df = pd.DataFrame({"KO": ["K00001"], "Toxicity": ["Low"]})

        entity = MergedData(
            original_dataset=Dataset([]),
            biorempp_data=biorempp_df,
            hadeg_data=hadeg_df,
            toxcsm_data=toxcsm_df
        )

        dto = MergedDataMapper.to_dto(entity, "cache_key_123", 2.5)

        assert dto.cache_key == "cache_key_123"
        assert dto.processing_time_seconds == 2.5
        assert dto.has_hadeg_data()
        assert dto.has_toxcsm_data()
        assert dto.match_count == 1  # Based on biorempp_df length

    def test_to_dto_biorempp_only(self):
        """Test converting entity with BioRemPP data only."""
        biorempp_df = pd.DataFrame({"KO": ["K00001"]})

        entity = MergedData(
            original_dataset=Dataset([]),
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None
        )

        dto = MergedDataMapper.to_dto(entity, "cache_key", 1.0)

        assert dto.biorempp_data is biorempp_df
        assert not dto.has_hadeg_data()
        assert not dto.has_toxcsm_data()

    def test_to_dto_default_processing_time(self):
        """Test that default processing time is 0.0."""
        entity = MergedData(
            original_dataset=Dataset([]),
            biorempp_data=pd.DataFrame({"KO": ["K00001"]})
        )

        dto = MergedDataMapper.to_dto(entity, "key")

        assert dto.processing_time_seconds == 0.0

    def test_to_dto_shares_dataframe_reference(self):
        """Test that DataFrame references are shared, not copied."""
        biorempp_df = pd.DataFrame({"KO": ["K00001"]})

        entity = MergedData(
            original_dataset=Dataset([]),
            biorempp_data=biorempp_df
        )

        dto = MergedDataMapper.to_dto(entity, "key", 1.0)

        assert dto.biorempp_data is biorempp_df


class TestMergedDataMapperFromDTO:
    """Test DTO to MergedData entity conversion."""

    def test_from_dto_with_all_databases(self):
        """Test converting DTO with all database results."""
        biorempp_df = pd.DataFrame({"KO": ["K00001"]})
        hadeg_df = pd.DataFrame({"KO": ["K00001"]})
        toxcsm_df = pd.DataFrame({"KO": ["K00001"]})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=hadeg_df,
            toxcsm_data=toxcsm_df,
            match_count=1,
            total_records=1,
            cache_key="key",
            processing_time_seconds=1.0
        )

        entity = MergedDataMapper.from_dto(dto)

        assert entity.biorempp_data is biorempp_df
        assert entity.hadeg_data is hadeg_df
        assert entity.toxcsm_data is toxcsm_df

    def test_from_dto_biorempp_only(self):
        """Test converting DTO with BioRemPP data only."""
        biorempp_df = pd.DataFrame({"KO": ["K00001"]})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key",
            processing_time_seconds=1.0
        )

        entity = MergedDataMapper.from_dto(dto)

        assert entity.biorempp_data is biorempp_df
        assert entity.hadeg_data is None
        assert entity.toxcsm_data is None

    def test_from_dto_shares_dataframe_reference(self):
        """Test that DataFrame references are shared, not copied."""
        biorempp_df = pd.DataFrame({"KO": ["K00001"]})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key",
            processing_time_seconds=1.0
        )

        entity = MergedDataMapper.from_dto(dto)

        assert entity.biorempp_data is biorempp_df


class TestMergedDataMapperCreateEmptyDTO:
    """Test empty DTO creation."""

    def test_create_empty_dto(self):
        """Test creating empty DTO."""
        dto = MergedDataMapper.create_empty_dto("empty_key")

        assert dto.match_count == 0
        assert dto.total_records == 0
        assert dto.cache_key == "empty_key"
        assert dto.processing_time_seconds == 0.0
        assert not dto.has_hadeg_data()
        assert not dto.has_toxcsm_data()


class TestMergedDataMapperRoundTrip:
    """Test round-trip conversions."""

    def test_entity_to_dto_to_entity(self):
        """Test entity -> DTO -> entity preserves data."""
        biorempp_df = pd.DataFrame({"KO": ["K00001", "K00002"]})
        hadeg_df = pd.DataFrame({"KO": ["K00001"]})

        original_entity = MergedData(
            original_dataset=Dataset([]),
            biorempp_data=biorempp_df,
            hadeg_data=hadeg_df,
            toxcsm_data=None
        )

        dto = MergedDataMapper.to_dto(original_entity, "key", 1.0)
        reconstructed_entity = MergedDataMapper.from_dto(dto)

        # Verify data preserved
        assert reconstructed_entity.biorempp_data is biorempp_df
        assert reconstructed_entity.hadeg_data is hadeg_df
        assert reconstructed_entity.toxcsm_data is None

    def test_dto_to_entity_to_dto(self):
        """Test DTO -> entity -> DTO preserves data."""
        biorempp_df = pd.DataFrame({"KO": ["K00001"]})

        original_dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="original_key",
            processing_time_seconds=2.0
        )

        entity = MergedDataMapper.from_dto(original_dto)
        new_dto = MergedDataMapper.to_dto(entity, "new_key", 3.0)

        # Verify core data preserved (note: cache_key and processing_time change)
        assert new_dto.biorempp_data is original_dto.biorempp_data
        assert new_dto.cache_key == "new_key"
        assert new_dto.processing_time_seconds == 3.0
