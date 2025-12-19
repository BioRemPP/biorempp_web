"""
Unit Tests for SampleId Value Object
"""

import pytest

from biorempp_web.src.domain.value_objects.sample_id import SampleId


class TestSampleId:
    """Tests for the SampleId Value Object."""

    def test_create_valid_sample_id(self, valid_sample_id):
        """Tests creating a valid SampleId with real data."""
        sample_id = SampleId(valid_sample_id)
        assert sample_id.value == valid_sample_id
        assert isinstance(sample_id.value, str)
        assert len(sample_id.value) > 0

    def test_sample_id_str_representation(self, valid_sample_id):
        """Tests the string representation."""
        sample_id = SampleId(valid_sample_id)
        assert str(sample_id) == valid_sample_id

    def test_sample_id_repr_representation(self, valid_sample_id):
        """Tests the debug representation."""
        sample_id = SampleId(valid_sample_id)
        expected = f"SampleId('{valid_sample_id}')"
        assert repr(sample_id) == expected

    def test_sample_id_is_immutable(self, sample_id_instance):
        """Tests immutability using fixture."""
        with pytest.raises(Exception):
            sample_id_instance.value = "DifferentSample"

    def test_sample_id_equality(self, valid_sample_id, edge_case_sample_ids):
        """Tests equality with real data."""
        sid1 = SampleId(valid_sample_id)
        sid2 = SampleId(valid_sample_id)  # Same value
        sid3 = SampleId(edge_case_sample_ids[0])  # Different value

        assert sid1 == sid2
        assert sid1 != sid3

    def test_sample_id_hashable(self, valid_sample_id, edge_case_sample_ids):
        """Tests use in set/dict with real data."""
        sid1 = SampleId(valid_sample_id)
        sid2 = SampleId(valid_sample_id)  # Duplicate
        sid3 = SampleId(edge_case_sample_ids[0])  # Different

        id_set = {sid1, sid2, sid3}
        assert len(id_set) == 2  # sid1 and sid2 are equal

    def test_invalid_sample_id_empty(self, edge_case_empty_string):
        """Tests an empty SampleId using fixture."""
        with pytest.raises(ValueError, match="cannot be empty"):
            SampleId(edge_case_empty_string)

    def test_invalid_sample_id_whitespace(self, edge_case_whitespace_string):
        """Tests SampleId with only whitespace using fixture."""
        with pytest.raises(ValueError, match="cannot be empty"):
            SampleId(edge_case_whitespace_string)

    def test_sample_id_with_spaces(self, edge_case_sample_ids):
        """Tests SampleId with valid spaces using real examples."""
        # Use edge case that might have spaces
        for sample_id_str in edge_case_sample_ids[:3]:
            if ' ' in sample_id_str or '_' in sample_id_str:
                sample_id = SampleId(sample_id_str)
                assert sample_id.value == sample_id_str

    def test_sample_id_special_characters(self, edge_case_sample_ids):
        """Tests SampleId with special characters from real data."""
        # Test first few edge case sample IDs which may contain special chars
        for id_str in edge_case_sample_ids[:5]:
            sample_id = SampleId(id_str)
            assert sample_id.value == id_str
            assert len(sample_id.value) > 0

