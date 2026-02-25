"""
Unit tests for ValidationService.

This module tests the ValidationService domain service, which provides
validation logic for raw input content, datasets, and KO lists.

Test Coverage:
- Raw input validation (valid, empty, no sample, no KO, invalid lines)
- Empty sample name handling
- Invalid KO format detection
- Empty line handling
- Dataset validation (valid, empty, invalid samples)
- KO list validation (valid, empty, invalid KOs)
- Duplicate sample detection
"""

import pytest

from src.domain.entities.dataset import Dataset
from src.domain.entities.sample import Sample
from src.domain.services.validation_service import (
    ValidationService,
)
from src.domain.value_objects.kegg_orthology import KO
from src.domain.value_objects.sample_id import SampleId


class TestValidationService:
    """Tests for ValidationService."""

    def test_validate_raw_input_valid(self):
        """Tests validation of valid input."""
        content = ">Sample1\nK00001\nK00002\n>Sample2\nK00003"

        is_valid, error = ValidationService.validate_raw_input(content)

        assert is_valid is True
        assert error == ""

    def test_validate_raw_input_empty(self):
        """Tests validation of empty input."""
        is_valid, error = ValidationService.validate_raw_input("")

        assert is_valid is False
        assert "Empty" in error

    def test_validate_raw_input_no_sample(self):
        """Tests validation with no samples."""
        content = "K00001\nK00002"

        is_valid, error = ValidationService.validate_raw_input(content)

        assert is_valid is False
        assert "must start with sample identifier" in error

    def test_validate_raw_input_no_ko(self):
        """Tests validation with no KOs."""
        content = ">Sample1\n>Sample2"

        is_valid, error = ValidationService.validate_raw_input(content)

        assert is_valid is False
        assert "No KO entries" in error

    def test_validate_raw_input_invalid_line(self):
        """Tests validation with an invalid line."""
        content = ">Sample1\nK00001\nInvalidLine"

        is_valid, error = ValidationService.validate_raw_input(content)

        assert is_valid is False
        assert "Invalid line format" in error

    def test_validate_raw_input_empty_sample_name(self):
        """Tests validation with an empty sample name."""
        content = ">\nK00001"

        is_valid, error = ValidationService.validate_raw_input(content)

        assert is_valid is False
        assert "Sample name cannot be empty" in error

    def test_validate_raw_input_invalid_ko_format(self):
        """Tests validation with an invalid KO format."""
        content = ">Sample1\nK001"  # KO too short

        is_valid, error = ValidationService.validate_raw_input(content)

        assert is_valid is False
        assert "6 characters" in error

    def test_validate_raw_input_with_empty_lines(self):
        """Tests validation ignoring empty lines."""
        content = ">Sample1\n\nK00001\n\n>Sample2\nK00002\n"

        is_valid, error = ValidationService.validate_raw_input(content)

        assert is_valid is True

    def test_validate_dataset_valid(self):
        """Tests validation of a valid dataset."""
        dataset = Dataset()
        sample = Sample(id=SampleId("Sample1"))
        sample.add_ko(KO("K00001"))
        dataset.add_sample(sample)

        is_valid, error = ValidationService.validate_dataset(dataset)

        assert is_valid is True
        assert error == ""

    def test_validate_dataset_empty(self):
        """Tests validation of an empty dataset."""
        dataset = Dataset()

        is_valid, error = ValidationService.validate_dataset(dataset)

        assert is_valid is False
        assert "no samples" in error

    def test_validate_dataset_with_invalid_sample(self):
        """Tests validation with an invalid sample."""
        dataset = Dataset()
        sample = Sample(id=SampleId("Sample1"))
        # Add without validating (forcing an invalid sample)
        dataset.samples.append(sample)

        is_valid, error = ValidationService.validate_dataset(dataset)

        assert is_valid is False
        assert "at least one KO" in error

    def test_validate_ko_list_valid(self):
        """Tests validation of a valid KO list."""
        ko_strings = ["K00001", "K00002", "K00003"]

        is_valid, error, kos = ValidationService.validate_ko_list(ko_strings)

        assert is_valid is True
        assert error == ""
        assert len(kos) == 3
        assert all(isinstance(ko, KO) for ko in kos)

    def test_validate_ko_list_empty(self):
        """Tests validation of an empty list."""
        is_valid, error, kos = ValidationService.validate_ko_list([])

        assert is_valid is False
        assert "cannot be empty" in error
        assert kos == []

    def test_validate_ko_list_with_invalid_ko(self):
        """Tests validation with an invalid KO in the list."""
        ko_strings = ["K00001", "InvalidKO", "K00003"]

        is_valid, error, kos = ValidationService.validate_ko_list(ko_strings)

        assert is_valid is False
        assert kos == []

    def test_check_duplicate_samples_no_duplicates(self):
        """Tests checking for no duplicates."""
        dataset = Dataset()

        for i in range(3):
            sample = Sample(id=SampleId(f"Sample{i}"))
            sample.add_ko(KO("K00001"))
            dataset.add_sample(sample)

        has_dups, dup_ids = ValidationService.check_duplicate_samples(dataset)

        assert has_dups is False
        assert dup_ids == []

    def test_check_duplicate_samples_with_duplicates(self):
        """Tests checking with duplicates."""
        dataset = Dataset()

        # Add samples with duplicate IDs
        sample1 = Sample(id=SampleId("Sample1"))
        sample1.add_ko(KO("K00001"))
        dataset.samples.append(sample1)

        sample2 = Sample(id=SampleId("Sample1"))  # Duplicate
        sample2.add_ko(KO("K00002"))
        dataset.samples.append(sample2)

        sample3 = Sample(id=SampleId("Sample2"))
        sample3.add_ko(KO("K00003"))
        dataset.samples.append(sample3)

        has_dups, dup_ids = ValidationService.check_duplicate_samples(dataset)

        assert has_dups is True
        assert "Sample1" in dup_ids
        assert len(dup_ids) == 1

    def test_validate_file_size_within_limit(self):
        """Tests file size validation when size is within limit."""
        is_valid, error = ValidationService.validate_file_size(
            size_bytes=512 * 1024, max_bytes=1024 * 1024
        )

        assert is_valid
        assert error == ""

    def test_validate_file_size_exceeds_limit(self):
        """Tests file size validation when size exceeds limit."""
        is_valid, error = ValidationService.validate_file_size(
            size_bytes=2 * 1024 * 1024, max_bytes=1024 * 1024
        )

        assert not is_valid
        assert "exceeds maximum allowed size" in error

    def test_validate_sample_count_within_limit(self):
        """Tests sample count validation when count is within limit."""
        is_valid, error = ValidationService.validate_sample_count(10, 20)

        assert is_valid
        assert error == ""

    def test_validate_sample_count_exceeds_limit(self):
        """Tests sample count validation when count exceeds limit."""
        is_valid, error = ValidationService.validate_sample_count(25, 20)

        assert not is_valid
        assert "exceeds maximum allowed" in error

    def test_validate_ko_count_within_limit(self):
        """Tests KO count validation when count is within limit."""
        is_valid, error = ValidationService.validate_ko_count(1000, 5000)

        assert is_valid
        assert error == ""

    def test_validate_ko_count_exceeds_limit(self):
        """Tests KO count validation when count exceeds limit."""
        is_valid, error = ValidationService.validate_ko_count(6000, 5000)

        assert not is_valid
        assert "exceeds maximum allowed" in error

    def test_validate_encoding_utf8_success(self):
        """Tests encoding validation with valid UTF-8 bytes."""
        content = "Amostra válida com UTF-8".encode("utf-8")

        is_valid, decoded, error = ValidationService.validate_encoding(content)

        assert is_valid
        assert decoded == "Amostra válida com UTF-8"
        assert error == ""

    def test_validate_encoding_latin1_fallback(self):
        """Tests encoding validation fallback to latin-1."""
        content = "café".encode("latin-1")

        is_valid, decoded, error = ValidationService.validate_encoding(content)

        assert is_valid
        assert decoded == "café"
        assert error == ""
