"""
Unit tests for SampleParser.

This test suite validates the SampleParser class, which is responsible for
parsing file-formatted input into domain entities (Dataset with Samples).

Test Coverage:
- Initialization
- Basic parsing (single and multiple samples)
- Edge cases (empty content, invalid format, etc.)
- KO handling (valid, invalid, duplicates)
- Format validation
- Error handling
"""

import pytest

from src.application.core.sample_parser import SampleParser, ParsingMetrics
from src.domain.entities.dataset import Dataset
from src.domain.entities.sample import Sample
from src.domain.value_objects.kegg_orthology import KO
from src.domain.value_objects.sample_id import SampleId
from src.shared.exceptions import InvalidFormatError


class TestSampleParserInitialization:
    """Test SampleParser initialization."""

    def test_initialization(self):
        """Test that SampleParser initializes correctly."""
        parser = SampleParser()
        assert parser is not None


class TestSampleParserParse:
    """Test the main parse() method."""

    def test_parse_single_sample_single_ko(self):
        """Test parsing content with one sample and one KO."""
        parser = SampleParser()
        content = ">Sample1\nK00001"

        dataset, metrics = parser.parse(content)

        assert isinstance(dataset, Dataset)
        assert dataset.total_samples == 1
        assert dataset.samples[0].id.value == "Sample1"
        assert dataset.samples[0].ko_count == 1
        assert dataset.samples[0].ko_list[0].id == "K00001"

    def test_parse_single_sample_multiple_kos(self):
        """Test parsing content with one sample and multiple KOs."""
        parser = SampleParser()
        content = ">Sample1\nK00001\nK00002\nK00003"

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 1
        assert dataset.samples[0].ko_count == 3
        ko_ids = [ko.id for ko in dataset.samples[0].ko_list]
        assert ko_ids == ["K00001", "K00002", "K00003"]

    def test_parse_multiple_samples(self):
        """Test parsing content with multiple samples."""
        parser = SampleParser()
        content = ">Sample1\nK00001\nK00002\n>Sample2\nK00003\n>Sample3\nK00004\nK00005"

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 3
        assert dataset.samples[0].id.value == "Sample1"
        assert dataset.samples[1].id.value == "Sample2"
        assert dataset.samples[2].id.value == "Sample3"
        assert dataset.samples[0].ko_count == 2
        assert dataset.samples[1].ko_count == 1
        assert dataset.samples[2].ko_count == 2

    def test_parse_with_empty_lines(self):
        """Test parsing content with empty lines (should be ignored)."""
        parser = SampleParser()
        content = ">Sample1\n\nK00001\n\n\nK00002\n\n>Sample2\n\nK00003"

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 2
        assert dataset.samples[0].ko_count == 2
        assert dataset.samples[1].ko_count == 1

    def test_parse_with_whitespace(self):
        """Test parsing content with leading/trailing whitespace."""
        parser = SampleParser()
        content = "  >Sample1  \n  K00001  \n  K00002  "

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 1
        assert dataset.samples[0].id.value == "Sample1"
        assert dataset.samples[0].ko_count == 2

    def test_parse_empty_content_raises_error(self):
        """Test that parsing empty content raises ValueError."""
        parser = SampleParser()

        with pytest.raises(ValueError, match="Content cannot be empty"):
            parser.parse("")

    def test_parse_whitespace_only_raises_error(self):
        """Test that parsing whitespace-only content raises ValueError."""
        parser = SampleParser()

        with pytest.raises(ValueError, match="Content cannot be empty"):
            parser.parse("   \n  \n  ")

    def test_parse_no_sample_header_raises_error(self):
        """Test that parsing content without sample header raises InvalidFormatError."""
        parser = SampleParser()
        content = "K00001\nK00002"

        with pytest.raises(InvalidFormatError, match="No sample headers found"):
            parser.parse(content)

    def test_parse_no_ko_after_header_raises_error(self):
        """Test that parsing content with only headers raises InvalidFormatError."""
        parser = SampleParser()
        content = ">Sample1\n>Sample2\n>Sample3"

        with pytest.raises(InvalidFormatError, match="No KO entries found"):
            parser.parse(content)

    def test_parse_duplicate_kos_in_same_sample(self):
        """Test that duplicate KOs in same sample are handled (deduplicated by Sample.add_ko)."""
        parser = SampleParser()
        content = ">Sample1\nK00001\nK00002\nK00001\nK00003\nK00001"

        dataset, metrics = parser.parse(content)

        # Sample.add_ko() automatically deduplicates
        assert dataset.samples[0].ko_count == 3
        ko_ids = [ko.id for ko in dataset.samples[0].ko_list]
        assert ko_ids == ["K00001", "K00002", "K00003"]

    def test_parse_invalid_ko_format_skipped(self):
        """Test that invalid KO formats are silently skipped."""
        parser = SampleParser()
        content = ">Sample1\nK00001\nINVALID_KO\nK00002\nK123\nK00003"

        dataset, metrics = parser.parse(content)

        # Only valid KOs should be parsed
        assert dataset.samples[0].ko_count == 3
        ko_ids = [ko.id for ko in dataset.samples[0].ko_list]
        assert ko_ids == ["K00001", "K00002", "K00003"]

    def test_parse_sample_id_with_spaces(self):
        """Test that sample IDs with spaces are rejected by sanitization."""
        parser = SampleParser()
        content = ">Sample One\nK00001\n>Sample Two\nK00002"

        dataset, metrics = parser.parse(content)

        # Spaces are not allowed in sample names - both should be rejected
        assert dataset.total_samples == 0
        assert metrics.warnings  # Should have warnings about invalid names

    def test_parse_sample_id_with_special_characters(self):
        """Test that sample IDs with special characters (@) are rejected."""
        parser = SampleParser()
        content = ">Sample_1-A@2023\nK00001"

        dataset, metrics = parser.parse(content)

        # @ is not allowed - should be rejected
        assert dataset.total_samples == 0
        assert metrics.warnings  # Should have warning about invalid name


class TestSampleParserParseSamples:
    """Test the parse_samples() method."""

    def test_parse_samples_single_sample(self):
        """Test parse_samples with single sample."""
        parser = SampleParser()
        content = ">Sample1\nK00001\nK00002"
        metrics = ParsingMetrics()

        samples = parser.parse_samples(content, metrics)

        assert len(samples) == 1
        assert isinstance(samples[0], Sample)
        assert samples[0].id.value == "Sample1"
        assert samples[0].ko_count == 2

    def test_parse_samples_multiple_samples(self):
        """Test parse_samples with multiple samples."""
        parser = SampleParser()
        content = ">S1\nK00001\n>S2\nK00002\n>S3\nK00003"
        metrics = ParsingMetrics()

        samples = parser.parse_samples(content, metrics)

        assert len(samples) == 3
        assert all(isinstance(s, Sample) for s in samples)

    def test_parse_samples_empty_content(self):
        """Test parse_samples with empty content returns empty list."""
        parser = SampleParser()
        content = ""
        metrics = ParsingMetrics()

        samples = parser.parse_samples(content, metrics)

        assert samples == []

    def test_parse_samples_only_headers(self):
        """Test parse_samples with only headers (no KOs)."""
        parser = SampleParser()
        content = ">Sample1\n>Sample2"
        metrics = ParsingMetrics()

        samples = parser.parse_samples(content, metrics)

        # Samples are created but have no KOs
        assert len(samples) == 2
        assert samples[0].ko_count == 0
        assert samples[1].ko_count == 0

    def test_parse_samples_no_headers(self):
        """Test parse_samples with no headers (only KO lines)."""
        parser = SampleParser()
        content = "K00001\nK00002\nK00003"
        metrics = ParsingMetrics()

        samples = parser.parse_samples(content, metrics)

        # No sample context, so no samples created
        assert samples == []

    def test_parse_samples_preserves_order(self):
        """Test that parse_samples preserves the order of samples."""
        parser = SampleParser()
        content = ">Alpha\nK00001\n>Beta\nK00002\n>Gamma\nK00003"
        metrics = ParsingMetrics()

        samples = parser.parse_samples(content, metrics)

        assert [s.id.value for s in samples] == ["Alpha", "Beta", "Gamma"]

    def test_parse_samples_ko_before_any_sample(self):
        """Test that KOs before any sample header are ignored."""
        parser = SampleParser()
        content = "K00001\nK00002\n>Sample1\nK00003"
        metrics = ParsingMetrics()

        samples = parser.parse_samples(content, metrics)

        assert len(samples) == 1
        assert samples[0].ko_count == 1
        assert samples[0].ko_list[0].id == "K00003"


class TestSampleParserValidateFormat:
    """Test the validate_format() method."""

    def test_validate_format_valid_single_sample(self):
        """Test validation of valid single sample format."""
        parser = SampleParser()
        content = ">Sample1\nK00001"

        is_valid, error_msg = parser.validate_format(content)

        assert is_valid is True
        assert error_msg == ""

    def test_validate_format_valid_multiple_samples(self):
        """Test validation of valid multiple samples format."""
        parser = SampleParser()
        content = ">S1\nK00001\n>S2\nK00002"

        is_valid, error_msg = parser.validate_format(content)

        assert is_valid is True
        assert error_msg == ""

    def test_validate_format_empty_content(self):
        """Test validation of empty content."""
        parser = SampleParser()
        content = ""

        is_valid, error_msg = parser.validate_format(content)

        assert is_valid is False
        assert "empty" in error_msg.lower()

    def test_validate_format_whitespace_only(self):
        """Test validation of whitespace-only content."""
        parser = SampleParser()
        content = "   \n  \n  "

        is_valid, error_msg = parser.validate_format(content)

        assert is_valid is False
        assert "empty" in error_msg.lower()

    def test_validate_format_no_headers(self):
        """Test validation of content without sample headers."""
        parser = SampleParser()
        content = "K00001\nK00002\nK00003"

        is_valid, error_msg = parser.validate_format(content)

        assert is_valid is False
        assert "no sample headers" in error_msg.lower()

    def test_validate_format_only_headers(self):
        """Test validation of content with only headers (no KOs)."""
        parser = SampleParser()
        content = ">Sample1\n>Sample2\n>Sample3"

        is_valid, error_msg = parser.validate_format(content)

        assert is_valid is False
        assert "no ko entries" in error_msg.lower()

    def test_validate_format_with_empty_lines(self):
        """Test validation handles empty lines correctly."""
        parser = SampleParser()
        content = ">Sample1\n\nK00001\n\n\n>Sample2\n\nK00002"

        is_valid, error_msg = parser.validate_format(content)

        assert is_valid is True
        assert error_msg == ""

    def test_validate_format_single_header_single_ko(self):
        """Test minimal valid format (one header, one KO)."""
        parser = SampleParser()
        content = ">S\nK00001"

        is_valid, error_msg = parser.validate_format(content)

        assert is_valid is True


class TestSampleParserEdgeCases:
    """Test edge cases and special scenarios."""

    def test_parse_very_long_sample_name(self):
        """Test parsing sample with very long name."""
        parser = SampleParser()
        long_name = "Sample_" + "A" * 1000
        content = f">{long_name}\nK00001"

        dataset, metrics = parser.parse(content)

        assert dataset.samples[0].id.value == long_name

    def test_parse_many_kos_in_single_sample(self):
        """Test parsing sample with many KOs."""
        parser = SampleParser()
        ko_lines = "\n".join([f"K{str(i).zfill(5)}" for i in range(1, 1001)])
        content = f">Sample1\n{ko_lines}"

        dataset, metrics = parser.parse(content)

        assert dataset.samples[0].ko_count == 1000

    def test_parse_many_samples(self):
        """Test parsing many samples."""
        parser = SampleParser()
        sample_blocks = [f">Sample{i}\nK{str(i).zfill(5)}" for i in range(1, 101)]
        content = "\n".join(sample_blocks)

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 100

    def test_parse_unix_line_endings(self):
        """Test parsing with Unix line endings (\\n)."""
        parser = SampleParser()
        content = ">Sample1\nK00001\nK00002"

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 1
        assert dataset.samples[0].ko_count == 2

    def test_parse_windows_line_endings(self):
        """Test parsing with Windows line endings (\\r\\n)."""
        parser = SampleParser()
        content = ">Sample1\r\nK00001\r\nK00002"

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 1
        assert dataset.samples[0].ko_count == 2

    def test_parse_mixed_line_endings(self):
        """Test parsing with mixed line endings."""
        parser = SampleParser()
        content = ">Sample1\r\nK00001\nK00002\r\n>Sample2\nK00003"

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 2

    def test_parse_sample_without_name(self):
        """Test parsing sample header with empty name (just '>')."""
        parser = SampleParser()
        content = ">\nK00001"

        # Empty names are caught by sanitization and ignored, not raised
        dataset, metrics = parser.parse(content)
        assert dataset.total_samples == 0
        assert metrics.warnings  # Should have warning about empty name

    def test_parse_consecutive_headers(self):
        """Test parsing consecutive headers with at least one KO each."""
        parser = SampleParser()
        content = ">Sample1\nK00001\n>Sample2\nK00002"

        dataset, metrics = parser.parse(content)

        # Both samples should have one KO each
        assert dataset.total_samples == 2
        assert dataset.samples[0].ko_count == 1
        assert dataset.samples[1].ko_count == 1


class TestSampleParserIntegration:
    """Integration tests combining multiple features."""

    def test_parse_realistic_example(self):
        """Test parsing realistic example content."""
        parser = SampleParser()
        content = """
>Metagenome_Sample_A1
K00001
K00002
K00003
K00010

>Metagenome_Sample_B1
K00005
K00006
K00001

>Metagenome_Sample_C1
K00002
K00007
K00008
K00009
K00010
"""

        dataset, metrics = parser.parse(content)

        assert dataset.total_samples == 3
        assert dataset.samples[0].id.value == "Metagenome_Sample_A1"
        assert dataset.samples[0].ko_count == 4
        assert dataset.samples[1].id.value == "Metagenome_Sample_B1"
        assert dataset.samples[1].ko_count == 3
        assert dataset.samples[2].id.value == "Metagenome_Sample_C1"
        assert dataset.samples[2].ko_count == 5

    def test_parse_with_invalid_and_valid_kos_mixed(self):
        """Test parsing with mix of valid and invalid KOs."""
        parser = SampleParser()
        content = """
>Sample1
K00001
INVALID
K00002
K999
K00003
not_a_ko
K00004
"""

        dataset, metrics = parser.parse(content)

        # Only valid KOs should be included
        assert dataset.samples[0].ko_count == 4
        ko_ids = [ko.id for ko in dataset.samples[0].ko_list]
        assert "INVALID" not in ko_ids
        assert "not_a_ko" not in ko_ids
