"""
Unit Tests for Application Layer Core Components.

This module tests the application layer core components including
UploadHandler, SampleParser, and DataProcessor.
"""

import base64
import pytest
from src.application.core.upload_handler import UploadHandler
from src.application.core.sample_parser import SampleParser, ParsingMetrics
from src.domain.value_objects.sample_id import SampleId
from src.domain.value_objects.kegg_orthology import KO
from src.shared.exceptions import InvalidFormatError


class TestSampleParser:
    """Test SampleParser functionality."""

    def test_parse_valid_fasta(self):
        """Test parsing valid FASTA content."""
        parser = SampleParser()
        content = ">Sample1\nK00001\nK00002\n>Sample2\nK00003"

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 2
        assert dataset.total_kos == 3

    def test_parse_single_sample(self):
        """Test parsing single sample."""
        parser = SampleParser()
        content = ">Sample1\nK00001\nK00002"

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 1
        assert dataset.total_kos == 2

    def test_parse_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        parser = SampleParser()

        with pytest.raises(ValueError, match="Content cannot be empty"):
            parser.parse("")

    def test_parse_no_header_raises_error(self):
        """Test that content without headers raises InvalidFormatError."""
        parser = SampleParser()
        content = "K00001\nK00002"

        with pytest.raises(InvalidFormatError, match="No sample headers found"):
            parser.parse(content)

    def test_validate_format_valid(self):
        """Test format validation with valid content."""
        parser = SampleParser()
        content = ">Sample1\nK00001"

        is_valid, msg = parser.validate_format(content)

        assert is_valid is True
        assert msg == ""

    def test_validate_format_no_header(self):
        """Test format validation with no header."""
        parser = SampleParser()
        content = "K00001\nK00002"

        is_valid, msg = parser.validate_format(content)

        assert is_valid is False
        assert "No sample headers found" in msg

    def test_parse_samples_multiple(self):
        """Test parsing multiple samples."""
        parser = SampleParser()
        content = ">S1\nK00001\n>S2\nK00002\nK00003"

        metrics = ParsingMetrics()
        samples = parser.parse_samples(content, metrics)

        assert len(samples) == 2
        assert samples[0].ko_count == 1
        assert samples[1].ko_count == 2


class TestUploadHandler:
    """Test UploadHandler functionality."""

    def test_process_upload_success(self):
        """Test successful upload processing."""
        handler = UploadHandler()

        # Create valid FASTA content
        content = ">Sample1\nK00001\nK00002"
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        upload_content = f"data:text/plain;base64,{encoded}"

        result = handler.process_upload(upload_content, "test.txt")

        assert result.success is True
        assert result.sample_count == 1
        assert result.ko_count == 2
        assert result.filename == "test.txt"
        assert result.dataset is not None

    def test_process_upload_invalid_content(self):
        """Test upload with invalid content."""
        handler = UploadHandler()

        # Invalid content (no headers)
        content = "K00001\nK00002"
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        upload_content = f"data:text/plain;base64,{encoded}"

        result = handler.process_upload(upload_content, "test.txt")

        assert result.success is False
        assert result.sample_count == 0
        assert result.has_errors() is True

    def test_decode_content_valid(self):
        """Test content decoding."""
        handler = UploadHandler()
        content = "Hello World"
        encoded = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        upload_content = f"data:text/plain;base64,{encoded}"

        decoded = handler.decode_content(upload_content)

        assert decoded == "Hello World"

    def test_decode_content_empty_raises_error(self):
        """Test that empty content raises ValueError."""
        handler = UploadHandler()

        with pytest.raises(ValueError, match="Content is empty"):
            handler.decode_content("")

    def test_validate_and_parse_valid(self):
        """Test validation and parsing with valid content."""
        handler = UploadHandler()
        content = ">Sample1\nK00001\nK00002"

        is_valid, dataset, metrics, errors = handler.validate_and_parse(content)

        assert is_valid is True
        assert dataset is not None
        assert dataset.total_samples == 1
        assert len(errors) == 0

    def test_validate_and_parse_invalid(self):
        """Test validation with invalid content."""
        handler = UploadHandler()
        content = "K00001"  # No header

        is_valid, dataset, metrics, errors = handler.validate_and_parse(content)

        assert is_valid is False
        assert dataset is None
        assert len(errors) > 0
