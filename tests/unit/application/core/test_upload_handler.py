"""
Unit tests for UploadHandler.
"""

import base64
import pytest
from unittest.mock import Mock

from src.application.core.upload_handler import UploadHandler


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

    def test_decode_content_without_data_uri_prefix(self):
        """Test content decoding accepts plain base64 payloads."""
        handler = UploadHandler()
        encoded = base64.b64encode(b"Plain content").decode("utf-8")

        decoded = handler.decode_content(encoded)

        assert decoded == "Plain content"

    def test_decode_content_empty_raises_error(self):
        """Test that empty content raises ValueError."""
        handler = UploadHandler()

        with pytest.raises(ValueError, match="Content is empty"):
            handler.decode_content("")

    def test_decode_content_invalid_base64_raises_error(self):
        """Test invalid base64 payload raises a decode error."""
        handler = UploadHandler()

        with pytest.raises(ValueError, match="Failed to decode content"):
            handler.decode_content("not-base64!")

    def test_process_upload_handles_decode_error(self):
        """Test process_upload returns error DTO when decode fails."""
        handler = UploadHandler()

        result = handler.process_upload("not-base64!", "invalid.txt")

        assert result.success is False
        assert result.has_errors() is True
        assert "Failed to decode content" in result.errors[0]

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

    def test_validate_and_parse_handles_parser_value_error(self):
        """Test parser ValueError is returned as parsing error."""
        parser = Mock()
        parser.parse.side_effect = ValueError("bad payload")
        validation_service = Mock()
        validation_service.validate_raw_input.return_value = (True, "")
        handler = UploadHandler(parser=parser, validation_service=validation_service)

        is_valid, dataset, metrics, errors = handler.validate_and_parse(">Sample1\nK00001")

        assert is_valid is False
        assert dataset is None
        assert metrics is None
        assert errors == ["Parsing error: bad payload"]

    def test_validate_and_parse_handles_dataset_validation_error(self):
        """Test dataset.validate errors are returned as validation errors."""
        parser = Mock()
        dataset = Mock()
        dataset.validate.side_effect = ValueError("invalid dataset state")
        parser.parse.return_value = (dataset, Mock())
        validation_service = Mock()
        validation_service.validate_raw_input.return_value = (True, "")
        handler = UploadHandler(parser=parser, validation_service=validation_service)

        is_valid, parsed_dataset, metrics, errors = handler.validate_and_parse(
            ">Sample1\nK00001"
        )

        assert is_valid is False
        assert parsed_dataset is None
        assert metrics is None
        assert errors == ["Validation error: invalid dataset state"]
