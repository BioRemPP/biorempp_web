"""
Unit tests for MergedDataDTO.

This module tests the MergedDataDTO immutable data transfer object,
which encapsulates results from database merge operations.

Test Categories:
- Initialization: Test DTO creation and validation
- Validation: Test __post_init__ validation logic
- Match Rate Calculation: Test match_rate() method
- Data Availability: Test has_hadeg_data() and has_toxcsm_data()
- Immutability: Test frozen dataclass behavior
- Edge Cases: Test boundary conditions
"""

import pytest
import pandas as pd

from src.application.dto.merged_data_dto import MergedDataDTO


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestMergedDataDTOInitialization:
    """Test MergedDataDTO initialization."""

    def test_initialization_with_all_data(self):
        """Test successful initialization with all databases."""
        biorempp_df = pd.DataFrame({'KO': ['K00001'], 'Sample': ['S1']})
        hadeg_df = pd.DataFrame({'KO': ['K00001'], 'Pathway': ['P1']})
        toxcsm_df = pd.DataFrame({'KO': ['K00001'], 'Toxicity': ['Low']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=hadeg_df,
            toxcsm_data=toxcsm_df,
            match_count=10,
            total_records=20,
            cache_key="test_key_123"
        )

        assert dto.biorempp_data is biorempp_df
        assert dto.hadeg_data is hadeg_df
        assert dto.toxcsm_data is toxcsm_df
        assert dto.match_count == 10
        assert dto.total_records == 20
        assert dto.cache_key == "test_key_123"
        assert dto.processing_time_seconds == 0.0  # Default

    def test_initialization_with_optional_data_none(self):
        """Test initialization with optional databases as None."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=5,
            total_records=10,
            cache_key="key_456"
        )

        assert dto.biorempp_data is biorempp_df
        assert dto.hadeg_data is None
        assert dto.toxcsm_data is None

    def test_initialization_with_processing_time(self):
        """Test initialization with processing time specified."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key",
            processing_time_seconds=2.5
        )

        assert dto.processing_time_seconds == 2.5

    def test_initialization_with_zero_counts(self):
        """Test initialization with zero counts."""
        biorempp_df = pd.DataFrame()

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=0,
            total_records=0,
            cache_key="empty"
        )

        assert dto.match_count == 0
        assert dto.total_records == 0

    def test_initialization_with_empty_dataframes(self):
        """Test initialization with empty DataFrames."""
        biorempp_df = pd.DataFrame()
        hadeg_df = pd.DataFrame()
        toxcsm_df = pd.DataFrame()

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=hadeg_df,
            toxcsm_data=toxcsm_df,
            match_count=0,
            total_records=0,
            cache_key="all_empty"
        )

        assert dto.biorempp_data.empty
        assert dto.hadeg_data.empty
        assert dto.toxcsm_data.empty


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestMergedDataDTOValidation:
    """Test __post_init__ validation logic."""

    def test_validation_rejects_non_dataframe_biorempp(self):
        """Test that non-DataFrame biorempp_data raises TypeError."""
        with pytest.raises(TypeError, match="biorempp_data must be a pandas DataFrame"):
            MergedDataDTO(
                biorempp_data="not a dataframe",  # Invalid
                hadeg_data=None,
                toxcsm_data=None,
                match_count=1,
                total_records=1,
                cache_key="key"
            )

    def test_validation_rejects_none_biorempp(self):
        """Test that None biorempp_data raises TypeError."""
        with pytest.raises(TypeError, match="biorempp_data must be a pandas DataFrame"):
            MergedDataDTO(
                biorempp_data=None,  # Invalid
                hadeg_data=None,
                toxcsm_data=None,
                match_count=0,
                total_records=0,
                cache_key="key"
            )

    def test_validation_rejects_negative_match_count(self):
        """Test that negative match_count raises ValueError."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        with pytest.raises(ValueError, match="Counts cannot be negative"):
            MergedDataDTO(
                biorempp_data=biorempp_df,
                hadeg_data=None,
                toxcsm_data=None,
                match_count=-1,  # Invalid
                total_records=10,
                cache_key="key"
            )

    def test_validation_rejects_negative_total_records(self):
        """Test that negative total_records raises ValueError."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        with pytest.raises(ValueError, match="Counts cannot be negative"):
            MergedDataDTO(
                biorempp_data=biorempp_df,
                hadeg_data=None,
                toxcsm_data=None,
                match_count=5,
                total_records=-10,  # Invalid
                cache_key="key"
            )

    def test_validation_rejects_match_count_exceeds_total(self):
        """Test that match_count > total_records raises ValueError."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        with pytest.raises(ValueError, match="match_count cannot exceed total_records"):
            MergedDataDTO(
                biorempp_data=biorempp_df,
                hadeg_data=None,
                toxcsm_data=None,
                match_count=15,  # Greater than total
                total_records=10,
                cache_key="key"
            )

    def test_validation_rejects_negative_processing_time(self):
        """Test that negative processing_time_seconds raises ValueError."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        with pytest.raises(ValueError, match="processing_time_seconds cannot be negative"):
            MergedDataDTO(
                biorempp_data=biorempp_df,
                hadeg_data=None,
                toxcsm_data=None,
                match_count=1,
                total_records=1,
                cache_key="key",
                processing_time_seconds=-0.5  # Invalid
            )

    def test_validation_accepts_match_count_equal_total(self):
        """Test that match_count == total_records is valid."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=10,
            total_records=10,  # Equal is valid
            cache_key="key"
        )

        assert dto.match_count == dto.total_records


# ============================================================================
# MATCH RATE CALCULATION TESTS
# ============================================================================

class TestMatchRateCalculation:
    """Test match_rate() method."""

    def test_match_rate_full_match(self):
        """Test match rate with 100% match."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=10,
            total_records=10,
            cache_key="key"
        )

        assert dto.match_rate() == 100.0

    def test_match_rate_half_match(self):
        """Test match rate with 50% match."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=5,
            total_records=10,
            cache_key="key"
        )

        assert dto.match_rate() == 50.0

    def test_match_rate_no_match(self):
        """Test match rate with 0% match."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=0,
            total_records=10,
            cache_key="key"
        )

        assert dto.match_rate() == 0.0

    def test_match_rate_zero_total_records(self):
        """Test match rate with zero total records returns 0.0."""
        biorempp_df = pd.DataFrame()

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=0,
            total_records=0,
            cache_key="key"
        )

        # Division by zero protection
        assert dto.match_rate() == 0.0

    def test_match_rate_fractional_percentage(self):
        """Test match rate with fractional percentage."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=3,
            cache_key="key"
        )

        # 1/3 * 100 = 33.333...
        assert abs(dto.match_rate() - 33.333333333333336) < 1e-10


# ============================================================================
# DATA AVAILABILITY TESTS
# ============================================================================

class TestDataAvailability:
    """Test has_hadeg_data() and has_toxcsm_data() methods."""

    def test_has_hadeg_data_returns_true_with_data(self):
        """Test has_hadeg_data returns True when data exists."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})
        hadeg_df = pd.DataFrame({'KO': ['K00001'], 'Pathway': ['P1']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=hadeg_df,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        assert dto.has_hadeg_data() is True

    def test_has_hadeg_data_returns_false_with_none(self):
        """Test has_hadeg_data returns False when data is None."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        assert dto.has_hadeg_data() is False

    def test_has_hadeg_data_returns_false_with_empty_dataframe(self):
        """Test has_hadeg_data returns False when DataFrame is empty."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})
        hadeg_df = pd.DataFrame()  # Empty

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=hadeg_df,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        assert dto.has_hadeg_data() is False

    def test_has_toxcsm_data_returns_true_with_data(self):
        """Test has_toxcsm_data returns True when data exists."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})
        toxcsm_df = pd.DataFrame({'KO': ['K00001'], 'Toxicity': ['Low']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=toxcsm_df,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        assert dto.has_toxcsm_data() is True

    def test_has_toxcsm_data_returns_false_with_none(self):
        """Test has_toxcsm_data returns False when data is None."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        assert dto.has_toxcsm_data() is False

    def test_has_toxcsm_data_returns_false_with_empty_dataframe(self):
        """Test has_toxcsm_data returns False when DataFrame is empty."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})
        toxcsm_df = pd.DataFrame()  # Empty

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=toxcsm_df,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        assert dto.has_toxcsm_data() is False

    def test_both_optional_data_available(self):
        """Test both has_hadeg_data and has_toxcsm_data return True."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})
        hadeg_df = pd.DataFrame({'KO': ['K00001'], 'Pathway': ['P1']})
        toxcsm_df = pd.DataFrame({'KO': ['K00001'], 'Toxicity': ['Low']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=hadeg_df,
            toxcsm_data=toxcsm_df,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        assert dto.has_hadeg_data() is True
        assert dto.has_toxcsm_data() is True


# ============================================================================
# IMMUTABILITY TESTS
# ============================================================================

class TestImmutability:
    """Test frozen dataclass behavior."""

    def test_cannot_modify_biorempp_data_attribute(self):
        """Test that biorempp_data attribute cannot be reassigned."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        with pytest.raises(AttributeError):
            dto.biorempp_data = pd.DataFrame({'KO': ['K00002']})

    def test_cannot_modify_match_count(self):
        """Test that match_count attribute cannot be modified."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=5,
            total_records=10,
            cache_key="key"
        )

        with pytest.raises(AttributeError):
            dto.match_count = 10

    def test_cannot_modify_cache_key(self):
        """Test that cache_key attribute cannot be modified."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="original"
        )

        with pytest.raises(AttributeError):
            dto.cache_key = "modified"

    def test_cannot_add_new_attribute(self):
        """Test that new attributes cannot be added."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        with pytest.raises(AttributeError):
            dto.new_attribute = "value"

    def test_dataframe_content_can_be_modified(self):
        """Test that DataFrame content can be modified (not DTO itself)."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        # DataFrame itself is mutable (not the reference)
        dto.biorempp_data['NewColumn'] = ['Value']

        assert 'NewColumn' in dto.biorempp_data.columns


# ============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_large_match_counts(self):
        """Test with large match counts."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1_000_000,
            total_records=1_000_000,
            cache_key="large"
        )

        assert dto.match_count == 1_000_000
        assert dto.match_rate() == 100.0

    def test_very_small_processing_time(self):
        """Test with very small processing time."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key",
            processing_time_seconds=0.0001
        )

        assert dto.processing_time_seconds == 0.0001

    def test_cache_key_with_special_characters(self):
        """Test cache key with special characters."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        cache_key = "key:with-special_chars.123@#"
        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key=cache_key
        )

        assert dto.cache_key == cache_key

    def test_dataframe_with_many_columns(self):
        """Test with DataFrame containing many columns."""
        biorempp_df = pd.DataFrame({
            f'col_{i}': [f'value_{i}'] for i in range(100)
        })

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="many_cols"
        )

        assert len(dto.biorempp_data.columns) == 100

    def test_dataframe_with_unicode_content(self):
        """Test with DataFrame containing unicode characters."""
        biorempp_df = pd.DataFrame({
            'KO': ['K00001'],
            'Sample': ['café ☕'],
            'Description': ['日本語テスト']
        })

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="unicode"
        )

        assert dto.biorempp_data['Sample'][0] == 'café ☕'
        assert dto.biorempp_data['Description'][0] == '日本語テスト'

    def test_multiple_instances_are_independent(self):
        """Test that multiple DTO instances are independent."""
        biorempp_df1 = pd.DataFrame({'KO': ['K00001']})
        biorempp_df2 = pd.DataFrame({'KO': ['K00002']})

        dto1 = MergedDataDTO(
            biorempp_data=biorempp_df1,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=5,
            total_records=10,
            cache_key="key1"
        )

        dto2 = MergedDataDTO(
            biorempp_data=biorempp_df2,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=8,
            total_records=10,
            cache_key="key2"
        )

        # Instances are independent
        assert dto1.cache_key != dto2.cache_key
        assert dto1.match_count != dto2.match_count
        assert dto1.biorempp_data is not dto2.biorempp_data


# ============================================================================
# STRING REPRESENTATION TESTS
# ============================================================================

class TestStringRepresentation:
    """Test string representation of DTO."""

    def test_repr_contains_key_attributes(self):
        """Test that repr contains important attributes."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=5,
            total_records=10,
            cache_key="test_key"
        )

        repr_str = repr(dto)

        assert 'MergedDataDTO' in repr_str
        assert 'match_count=5' in repr_str
        assert 'total_records=10' in repr_str
        assert 'cache_key' in repr_str

    def test_repr_is_deterministic(self):
        """Test that repr is deterministic."""
        biorempp_df = pd.DataFrame({'KO': ['K00001']})

        dto = MergedDataDTO(
            biorempp_data=biorempp_df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="key"
        )

        repr1 = repr(dto)
        repr2 = repr(dto)

        assert repr1 == repr2
