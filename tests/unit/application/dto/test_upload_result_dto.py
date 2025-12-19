"""
Unit tests for UploadResultDTO.

This module tests the UploadResultDTO immutable data transfer object,
which encapsulates results from file upload operations.

Test Categories:
- Initialization: Test DTO creation with various scenarios
- Validation: Test __post_init__ validation logic
- Error Checking: Test has_errors() method
- Immutability: Test frozen dataclass behavior
- Edge Cases: Test boundary conditions
- Success/Failure Cases: Test typical success and failure scenarios
"""

import pytest

from src.application.dto.upload_result_dto import UploadResultDTO
from src.domain.entities.dataset import Dataset
from src.domain.entities.sample import Sample
from src.domain.value_objects.kegg_orthology import KO
from src.domain.value_objects.sample_id import SampleId


# ============================================================================
# INITIALIZATION TESTS - SUCCESS CASES
# ============================================================================

class TestUploadResultDTOSuccessInitialization:
    """Test UploadResultDTO initialization for successful uploads."""

    def test_initialization_success_with_dataset(self, dataset_with_samples):
        """Test successful initialization with dataset."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="samples.txt",
            sample_count=5,
            ko_count=15,
            message="Upload successful"
        )

        assert dto.success is True
        assert dto.dataset is dataset_with_samples
        assert dto.filename == "samples.txt"
        assert dto.sample_count == 5
        assert dto.ko_count == 15
        assert dto.message == "Upload successful"
        assert dto.errors is None

    def test_initialization_success_with_errors_none(self, dataset_with_samples):
        """Test successful initialization with explicit errors=None."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="data.txt",
            sample_count=3,
            ko_count=9,
            message="Success",
            errors=None
        )

        assert dto.success is True
        assert dto.errors is None

    def test_initialization_success_with_empty_dataset(self, empty_dataset):
        """Test successful initialization with empty dataset."""
        dto = UploadResultDTO(
            success=True,
            dataset=empty_dataset,
            filename="empty.txt",
            sample_count=0,
            ko_count=0,
            message="Empty dataset uploaded"
        )

        assert dto.success is True
        assert dto.dataset is empty_dataset
        assert dto.sample_count == 0
        assert dto.ko_count == 0

    def test_initialization_success_preserves_dataset_reference(
        self, dataset_with_samples
    ):
        """Test that dataset reference is preserved (not copied)."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="test.txt",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        assert dto.dataset is dataset_with_samples


# ============================================================================
# INITIALIZATION TESTS - FAILURE CASES
# ============================================================================

class TestUploadResultDTOFailureInitialization:
    """Test UploadResultDTO initialization for failed uploads."""

    def test_initialization_failure_with_no_dataset(self):
        """Test failed upload initialization with dataset=None."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="invalid.txt",
            sample_count=0,
            ko_count=0,
            message="Upload failed: Invalid format"
        )

        assert dto.success is False
        assert dto.dataset is None
        assert dto.sample_count == 0
        assert dto.ko_count == 0

    def test_initialization_failure_with_error_list(self):
        """Test failed upload with error messages."""
        errors = ["Invalid file format", "Missing required columns"]

        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="bad.csv",
            sample_count=0,
            ko_count=0,
            message="Upload failed",
            errors=errors
        )

        assert dto.success is False
        assert dto.errors == errors
        assert len(dto.errors) == 2

    def test_initialization_failure_with_empty_error_list(self):
        """Test failed upload with empty error list."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=[]
        )

        assert dto.errors == []
        assert len(dto.errors) == 0

    def test_initialization_failure_preserves_error_list_reference(self):
        """Test that errors list reference is preserved."""
        errors = ["Error 1", "Error 2"]

        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=errors
        )

        assert dto.errors is errors


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestUploadResultDTOValidation:
    """Test __post_init__ validation logic."""

    def test_validation_rejects_success_true_without_dataset(self):
        """Test that success=True with dataset=None raises ValueError."""
        with pytest.raises(ValueError, match="Success=True requires a valid dataset"):
            UploadResultDTO(
                success=True,
                dataset=None,  # Invalid for success=True
                filename="file.txt",
                sample_count=5,
                ko_count=10,
                message="Success"
            )

    def test_validation_rejects_negative_sample_count(self, dataset_with_samples):
        """Test that negative sample_count raises ValueError."""
        with pytest.raises(ValueError, match="Counts cannot be negative"):
            UploadResultDTO(
                success=True,
                dataset=dataset_with_samples,
                filename="file.txt",
                sample_count=-1,  # Invalid
                ko_count=10,
                message="Success"
            )

    def test_validation_rejects_negative_ko_count(self, dataset_with_samples):
        """Test that negative ko_count raises ValueError."""
        with pytest.raises(ValueError, match="Counts cannot be negative"):
            UploadResultDTO(
                success=True,
                dataset=dataset_with_samples,
                filename="file.txt",
                sample_count=5,
                ko_count=-10,  # Invalid
                message="Success"
            )

    def test_validation_rejects_both_counts_negative(self, dataset_with_samples):
        """Test that both negative counts raise ValueError."""
        with pytest.raises(ValueError, match="Counts cannot be negative"):
            UploadResultDTO(
                success=True,
                dataset=dataset_with_samples,
                filename="file.txt",
                sample_count=-5,  # Invalid
                ko_count=-10,  # Invalid
                message="Success"
            )

    def test_validation_accepts_zero_counts(self, empty_dataset):
        """Test that zero counts are valid."""
        dto = UploadResultDTO(
            success=True,
            dataset=empty_dataset,
            filename="empty.txt",
            sample_count=0,  # Valid
            ko_count=0,  # Valid
            message="Empty upload"
        )

        assert dto.sample_count == 0
        assert dto.ko_count == 0

    def test_validation_allows_failure_with_none_dataset(self):
        """Test that success=False with dataset=None is valid."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,  # Valid for success=False
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed"
        )

        assert dto.success is False
        assert dto.dataset is None


# ============================================================================
# ERROR CHECKING TESTS
# ============================================================================

class TestErrorChecking:
    """Test has_errors() method."""

    def test_has_errors_returns_false_when_errors_none(self, dataset_with_samples):
        """Test has_errors returns False when errors is None."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file.txt",
            sample_count=5,
            ko_count=15,
            message="Success",
            errors=None
        )

        assert dto.has_errors() is False

    def test_has_errors_returns_false_when_errors_empty(self):
        """Test has_errors returns False when errors list is empty."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=[]
        )

        assert dto.has_errors() is False

    def test_has_errors_returns_true_when_errors_exist(self):
        """Test has_errors returns True when errors list has items."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=["Error 1", "Error 2"]
        )

        assert dto.has_errors() is True

    def test_has_errors_returns_true_with_single_error(self):
        """Test has_errors returns True with single error."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=["Single error"]
        )

        assert dto.has_errors() is True

    def test_has_errors_consistent_across_calls(self):
        """Test has_errors returns consistent results."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=["Error"]
        )

        result1 = dto.has_errors()
        result2 = dto.has_errors()

        assert result1 is True
        assert result2 is True
        assert result1 == result2


# ============================================================================
# IMMUTABILITY TESTS
# ============================================================================

class TestImmutability:
    """Test frozen dataclass behavior."""

    def test_cannot_modify_success(self, dataset_with_samples):
        """Test that success attribute cannot be modified."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file.txt",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        with pytest.raises(AttributeError):
            dto.success = False

    def test_cannot_modify_dataset(self, dataset_with_samples):
        """Test that dataset attribute cannot be reassigned."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file.txt",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        with pytest.raises(AttributeError):
            dto.dataset = Dataset()

    def test_cannot_modify_filename(self, dataset_with_samples):
        """Test that filename attribute cannot be modified."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="original.txt",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        with pytest.raises(AttributeError):
            dto.filename = "modified.txt"

    def test_cannot_modify_sample_count(self, dataset_with_samples):
        """Test that sample_count attribute cannot be modified."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file.txt",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        with pytest.raises(AttributeError):
            dto.sample_count = 10

    def test_cannot_modify_ko_count(self, dataset_with_samples):
        """Test that ko_count attribute cannot be modified."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file.txt",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        with pytest.raises(AttributeError):
            dto.ko_count = 20

    def test_cannot_modify_message(self, dataset_with_samples):
        """Test that message attribute cannot be modified."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file.txt",
            sample_count=5,
            ko_count=15,
            message="Original message"
        )

        with pytest.raises(AttributeError):
            dto.message = "Modified message"

    def test_cannot_modify_errors(self):
        """Test that errors attribute cannot be reassigned."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=["Error 1"]
        )

        with pytest.raises(AttributeError):
            dto.errors = ["Error 2"]

    def test_cannot_add_new_attribute(self, dataset_with_samples):
        """Test that new attributes cannot be added."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file.txt",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        with pytest.raises(AttributeError):
            dto.new_field = "value"

    def test_error_list_content_can_be_modified(self):
        """Test that error list content can be modified (not the reference)."""
        errors = ["Error 1"]

        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=errors
        )

        # List itself is mutable (not the reference)
        dto.errors.append("Error 2")

        assert len(dto.errors) == 2
        assert "Error 2" in dto.errors


# ============================================================================
# EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_large_sample_and_ko_counts(self, dataset_with_samples):
        """Test with very large counts."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="large.txt",
            sample_count=1_000_000,
            ko_count=50_000_000,
            message="Large upload"
        )

        assert dto.sample_count == 1_000_000
        assert dto.ko_count == 50_000_000

    def test_filename_with_special_characters(self, dataset_with_samples):
        """Test filename with special characters."""
        special_filename = "file-name_with.special#chars@2024.txt"

        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename=special_filename,
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        assert dto.filename == special_filename

    def test_filename_with_unicode(self, dataset_with_samples):
        """Test filename with Unicode characters."""
        unicode_filename = "données_café_日本語.txt"

        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename=unicode_filename,
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        assert dto.filename == unicode_filename

    def test_message_with_unicode(self, dataset_with_samples):
        """Test message with Unicode characters."""
        unicode_message = "Upload successful: café ☕ データ 🎉"

        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file.txt",
            sample_count=5,
            ko_count=15,
            message=unicode_message
        )

        assert dto.message == unicode_message

    def test_long_error_list(self):
        """Test with many error messages."""
        errors = [f"Error {i}" for i in range(100)]

        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Many errors",
            errors=errors
        )

        assert len(dto.errors) == 100
        assert dto.has_errors() is True

    def test_error_messages_with_special_content(self):
        """Test error messages with special characters and newlines."""
        errors = [
            "Error with 'quotes'",
            "Error with \"double quotes\"",
            "Error with\nnewline",
            "Error with\ttab",
            "Error with special: @#$%"
        ]

        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=errors
        )

        assert all(err in dto.errors for err in errors)

    def test_empty_filename(self, dataset_with_samples):
        """Test with empty string filename."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        assert dto.filename == ""

    def test_empty_message(self, dataset_with_samples):
        """Test with empty message."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file.txt",
            sample_count=5,
            ko_count=15,
            message=""
        )

        assert dto.message == ""

    def test_multiple_instances_are_independent(self, dataset_with_samples):
        """Test that multiple DTO instances are independent."""
        dto1 = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="file1.txt",
            sample_count=5,
            ko_count=15,
            message="Success 1"
        )

        dto2 = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file2.txt",
            sample_count=0,
            ko_count=0,
            message="Failed 2",
            errors=["Error"]
        )

        assert dto1.success is not dto2.success
        assert dto1.filename != dto2.filename
        assert dto1.message != dto2.message
        assert dto1.dataset is not None
        assert dto2.dataset is None


# ============================================================================
# TYPICAL USE CASE TESTS
# ============================================================================

class TestTypicalUseCases:
    """Test typical success and failure scenarios."""

    def test_successful_upload_typical_case(self):
        """Test typical successful upload scenario."""
        # Create a dataset with samples
        dataset = Dataset()
        sample1 = Sample(id=SampleId("S1"))
        sample1.add_ko(KO("K00001"))
        sample1.add_ko(KO("K00002"))
        dataset.add_sample(sample1)

        sample2 = Sample(id=SampleId("S2"))
        sample2.add_ko(KO("K00003"))
        dataset.add_sample(sample2)

        dto = UploadResultDTO(
            success=True,
            dataset=dataset,
            filename="samples.txt",
            sample_count=2,
            ko_count=3,
            message="Successfully uploaded 2 samples with 3 KOs"
        )

        assert dto.success is True
        assert dto.dataset == dataset
        assert dto.sample_count == 2
        assert dto.ko_count == 3
        assert dto.has_errors() is False

    def test_failed_upload_invalid_format(self):
        """Test typical failed upload with invalid format."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="invalid.csv",
            sample_count=0,
            ko_count=0,
            message="Upload failed: Invalid file format",
            errors=["Expected .txt file, got .csv"]
        )

        assert dto.success is False
        assert dto.dataset is None
        assert dto.has_errors() is True
        assert len(dto.errors) == 1

    def test_failed_upload_validation_errors(self):
        """Test failed upload with multiple validation errors."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="data.txt",
            sample_count=0,
            ko_count=0,
            message="Upload failed: Validation errors",
            errors=[
                "Missing required column 'Sample'",
                "Invalid KO format in line 5",
                "Duplicate sample ID 'S1'"
            ]
        )

        assert dto.success is False
        assert dto.has_errors() is True
        assert len(dto.errors) == 3

    def test_partial_success_with_warnings(self, dataset_with_samples):
        """Test upload that succeeded but has warnings."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="data_with_warnings.txt",
            sample_count=5,
            ko_count=12,  # Some KOs might have been filtered
            message="Upload successful with warnings",
            errors=["Warning: 3 invalid KO IDs were skipped"]
        )

        assert dto.success is True
        assert dto.dataset is not None
        assert dto.has_errors() is True  # Warnings stored as errors


# ============================================================================
# STRING REPRESENTATION TESTS
# ============================================================================

class TestStringRepresentation:
    """Test string representation of DTO."""

    def test_repr_contains_key_attributes(self, dataset_with_samples):
        """Test that repr contains important attributes."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="test.txt",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        repr_str = repr(dto)

        assert 'UploadResultDTO' in repr_str
        assert 'success=True' in repr_str
        assert 'filename=' in repr_str
        assert 'sample_count=5' in repr_str
        assert 'ko_count=15' in repr_str

    def test_repr_is_deterministic(self, dataset_with_samples):
        """Test that repr is deterministic."""
        dto = UploadResultDTO(
            success=True,
            dataset=dataset_with_samples,
            filename="test.txt",
            sample_count=5,
            ko_count=15,
            message="Success"
        )

        repr1 = repr(dto)
        repr2 = repr(dto)

        assert repr1 == repr2

    def test_repr_with_errors(self):
        """Test repr with errors present."""
        dto = UploadResultDTO(
            success=False,
            dataset=None,
            filename="file.txt",
            sample_count=0,
            ko_count=0,
            message="Failed",
            errors=["Error 1", "Error 2"]
        )

        repr_str = repr(dto)

        assert 'UploadResultDTO' in repr_str
        assert 'success=False' in repr_str
        assert 'errors=' in repr_str
