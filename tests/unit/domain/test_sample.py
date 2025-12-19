"""
Unit Tests for Sample Entity
"""

from datetime import datetime

import pytest

from biorempp_web.src.domain.entities.sample import Sample
from biorempp_web.src.domain.value_objects.kegg_orthology import KO
from biorempp_web.src.domain.value_objects.sample_id import SampleId


class TestSample:
    """Tests for the Sample entity."""

    def test_create_sample(self, sample_id_instance):
        """Tests sample creation using fixture."""
        sample = Sample(id=sample_id_instance)

        assert sample.id == sample_id_instance
        assert sample.ko_count == 0
        assert isinstance(sample.created_at, datetime)

    def test_add_ko(self, sample_id_instance, sample_ko):
        """Tests adding a KO to the sample."""
        sample = Sample(id=sample_id_instance)

        sample.add_ko(sample_ko)

        assert sample.ko_count == 1
        assert sample.has_ko(sample_ko)

    def test_add_duplicate_ko(self, sample_id_instance, sample_ko):
        """Tests that duplicate KOs are ignored."""
        sample = Sample(id=sample_id_instance)

        sample.add_ko(sample_ko)
        sample.add_ko(sample_ko)  # Duplicate

        assert sample.ko_count == 1

    def test_add_multiple_kos(self, sample_id_instance, sample_ko_list):
        """Tests adding multiple KOs using fixture."""
        sample = Sample(id=sample_id_instance)

        for ko in sample_ko_list:
            sample.add_ko(ko)

        assert sample.ko_count == len(sample_ko_list)  # Should be 5

    def test_remove_ko(self, sample_id_instance, sample_ko):
        """Tests KO removal."""
        sample = Sample(id=sample_id_instance)

        sample.add_ko(sample_ko)
        assert sample.ko_count == 1

        sample.remove_ko(sample_ko)
        assert sample.ko_count == 0
        assert not sample.has_ko(sample_ko)

    def test_remove_nonexistent_ko(self, sample_id_instance, sample_ko):
        """Tests removing a non-existent KO."""
        sample = Sample(id=sample_id_instance)

        # Should not raise exception
        sample.remove_ko(sample_ko)
        assert sample.ko_count == 0

    def test_has_ko(self, sample_id_instance, sample_ko_list):
        """Tests checking for KO presence."""
        sample = Sample(id=sample_id_instance)
        
        # Add first KO from list
        sample.add_ko(sample_ko_list[0])

        assert sample.has_ko(sample_ko_list[0])
        assert not sample.has_ko(sample_ko_list[1])  # Not added

    def test_get_unique_kos(self, sample_id_instance, sample_ko_list):
        """Tests getting unique KOs using fixture."""
        sample = Sample(id=sample_id_instance)

        for ko in sample_ko_list:
            sample.add_ko(ko)

        unique_kos = sample.get_unique_kos()
        assert len(unique_kos) == len(sample_ko_list)
        assert set(unique_kos) == set(sample_ko_list)

    def test_validate_valid_sample(self, sample_with_kos):
        """Tests validation of a valid sample using fixture."""
        # sample_with_kos already has KOs
        # Should not raise exception
        sample_with_kos.validate()
        assert sample_with_kos.ko_count > 0

    def test_validate_empty_sample(self, empty_sample):
        """Tests validation of a sample with no KOs using fixture."""
        with pytest.raises(ValueError, match="at least one KO"):
            empty_sample.validate()

    def test_sample_metadata(self, sample_id_instance):
        """Tests the use of metadata."""
        sample = Sample(id=sample_id_instance, metadata={"organism": "E. coli"})

        assert sample.metadata["organism"] == "E. coli"

        sample.metadata["temperature"] = 37
        assert sample.metadata["temperature"] == 37

    def test_sample_str_representation(self, sample_with_single_ko, valid_sample_id):
        """Tests string representation using fixture."""
        # sample_with_single_ko has exactly 1 KO
        sample_str = str(sample_with_single_ko)
        
        assert valid_sample_id in sample_str
        assert "1 KOs" in sample_str

    def test_sample_equality(self, valid_sample_id, edge_case_sample_ids):
        """Tests equality between samples using fixtures."""
        id1 = SampleId(valid_sample_id)
        id2 = SampleId(edge_case_sample_ids[0])

        sample1 = Sample(id=id1)
        sample2 = Sample(id=id1)
        sample3 = Sample(id=id2)

        assert sample1 == sample2  # Same ID
        assert sample1 != sample3  # Different IDs

    def test_sample_hashable(self, valid_sample_id, edge_case_sample_ids):
        """Tests use in set/dict using fixtures."""
        sample1 = Sample(id=SampleId(valid_sample_id))
        sample2 = Sample(id=SampleId(valid_sample_id))
        sample3 = Sample(id=SampleId(edge_case_sample_ids[0]))

        sample_set = {sample1, sample2, sample3}
        assert len(sample_set) == 2


class TestSampleBusinessRules:
    """Tests for Sample business rules."""

    def test_sample_with_many_kos(self, sample_id_instance, valid_ko_ids):
        """Tests a sample with many KOs using real data."""
        sample = Sample(id=sample_id_instance)

        # Use all 5 real KOs from fixtures
        for ko_id in valid_ko_ids:
            sample.add_ko(KO(ko_id))

        assert sample.ko_count == len(valid_ko_ids)  # Should be 5

    def test_sample_created_timestamp(self, sample_id_instance):
        """Tests the creation timestamp."""
        before = datetime.now()
        sample = Sample(id=sample_id_instance)
        after = datetime.now()

        assert before <= sample.created_at <= after

