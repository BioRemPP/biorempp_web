"""
Unit Tests for Dataset Entity
"""

import pytest

from biorempp_web.src.domain.entities.dataset import Dataset
from biorempp_web.src.domain.entities.sample import Sample
from biorempp_web.src.domain.value_objects.kegg_orthology import KO
from biorempp_web.src.domain.value_objects.sample_id import SampleId


class TestDataset:
    """Tests for the Dataset entity."""

    def test_create_empty_dataset(self, empty_dataset):
        """Tests creating an empty dataset using fixture."""
        assert empty_dataset.total_samples == 0
        assert empty_dataset.is_empty()

    def test_add_sample(self, sample_with_kos):
        """Tests adding a sample to the dataset using fixture."""
        dataset = Dataset()
        
        dataset.add_sample(sample_with_kos)

        assert dataset.total_samples == 1
        assert not dataset.is_empty()

    def test_add_invalid_sample_raises_error(self, empty_sample):
        """Tests that an invalid sample cannot be added using fixture."""
        dataset = Dataset()

        with pytest.raises(ValueError, match="at least one KO"):
            dataset.add_sample(empty_sample)

    def test_add_multiple_samples(self, dataset_with_samples):
        """Tests adding multiple samples using fixture."""
        # dataset_with_samples already has 5 samples
        assert dataset_with_samples.total_samples == 5

    def test_remove_sample(self, sample_with_kos):
        """Tests removing a sample."""
        dataset = Dataset()
        dataset.add_sample(sample_with_kos)

        result = dataset.remove_sample(sample_with_kos.id)

        assert result is True
        assert dataset.total_samples == 0

    def test_remove_nonexistent_sample(self, valid_sample_id):
        """Tests removing a non-existent sample."""
        dataset = Dataset()

        result = dataset.remove_sample(SampleId(valid_sample_id))

        assert result is False

    def test_get_sample_by_id(self, sample_with_kos):
        """Tests getting a sample by ID using fixture."""
        dataset = Dataset()
        dataset.add_sample(sample_with_kos)

        found = dataset.get_sample_by_id(sample_with_kos.id)

        assert found is not None
        assert found.id == sample_with_kos.id

    def test_get_nonexistent_sample(self, valid_sample_id):
        """Tests getting a non-existent sample."""
        dataset = Dataset()

        found = dataset.get_sample_by_id(SampleId(valid_sample_id))

        assert found is None

    def test_total_kos_unique(self, valid_ko_ids, edge_case_sample_ids):
        """Tests counting unique KOs using real data."""
        dataset = Dataset()

        # Sample 1 with first 2 KOs
        sample1 = Sample(id=SampleId(edge_case_sample_ids[0]))
        sample1.add_ko(KO(valid_ko_ids[0]))
        sample1.add_ko(KO(valid_ko_ids[1]))
        dataset.add_sample(sample1)

        # Sample 2 with KO[0] (duplicate) and KO[2]
        sample2 = Sample(id=SampleId(edge_case_sample_ids[1]))
        sample2.add_ko(KO(valid_ko_ids[0]))  # Duplicate
        sample2.add_ko(KO(valid_ko_ids[2]))
        dataset.add_sample(sample2)

        # Unique total: KO[0], KO[1], KO[2]
        assert dataset.total_kos == 3

    def test_get_all_kos(self, valid_ko_ids, edge_case_sample_ids):
        """Tests getting all unique KOs using fixtures."""
        dataset = Dataset()

        sample1 = Sample(id=SampleId(edge_case_sample_ids[0]))
        sample1.add_ko(KO(valid_ko_ids[0]))
        sample1.add_ko(KO(valid_ko_ids[1]))
        dataset.add_sample(sample1)

        sample2 = Sample(id=SampleId(edge_case_sample_ids[1]))
        sample2.add_ko(KO(valid_ko_ids[0]))
        sample2.add_ko(KO(valid_ko_ids[2]))
        dataset.add_sample(sample2)

        all_kos = dataset.get_all_kos()

        assert len(all_kos) == 3
        assert KO(valid_ko_ids[0]) in all_kos
        assert KO(valid_ko_ids[1]) in all_kos
        assert KO(valid_ko_ids[2]) in all_kos

    def test_get_ko_distribution(self, valid_ko_ids, edge_case_sample_ids):
        """Tests KO distribution using real data."""
        dataset = Dataset()

        # Sample 1: KO[0], KO[1]
        sample1 = Sample(id=SampleId(edge_case_sample_ids[0]))
        sample1.add_ko(KO(valid_ko_ids[0]))
        sample1.add_ko(KO(valid_ko_ids[1]))
        dataset.add_sample(sample1)

        # Sample 2: KO[0], KO[2]
        sample2 = Sample(id=SampleId(edge_case_sample_ids[1]))
        sample2.add_ko(KO(valid_ko_ids[0]))
        sample2.add_ko(KO(valid_ko_ids[2]))
        dataset.add_sample(sample2)

        distribution = dataset.get_ko_distribution()

        assert distribution[KO(valid_ko_ids[0])] == 2  # In 2 samples
        assert distribution[KO(valid_ko_ids[1])] == 1  # In 1 sample
        assert distribution[KO(valid_ko_ids[2])] == 1  # In 1 sample

    def test_get_samples_with_ko(self, valid_ko_ids, edge_case_sample_ids):
        """Tests getting samples containing a specific KO."""
        dataset = Dataset()

        sample1 = Sample(id=SampleId(edge_case_sample_ids[0]))
        sample1.add_ko(KO(valid_ko_ids[0]))
        dataset.add_sample(sample1)

        sample2 = Sample(id=SampleId(edge_case_sample_ids[1]))
        sample2.add_ko(KO(valid_ko_ids[1]))
        dataset.add_sample(sample2)

        sample3 = Sample(id=SampleId(edge_case_sample_ids[2]))
        sample3.add_ko(KO(valid_ko_ids[0]))
        dataset.add_sample(sample3)

        samples_with_k0 = dataset.get_samples_with_ko(KO(valid_ko_ids[0]))

        assert len(samples_with_k0) == 2
        assert sample1 in samples_with_k0
        assert sample3 in samples_with_k0

    def test_to_dict(self, valid_ko_ids, edge_case_sample_ids):
        """Tests conversion to dictionary using real data."""
        dataset = Dataset()

        sample = Sample(id=SampleId(edge_case_sample_ids[0]))
        sample.add_ko(KO(valid_ko_ids[0]))
        sample.add_ko(KO(valid_ko_ids[1]))
        dataset.add_sample(sample)

        data_dict = dataset.to_dict()

        assert "sample" in data_dict
        assert "ko" in data_dict
        assert len(data_dict["sample"]) == 2
        assert edge_case_sample_ids[0] in data_dict["sample"]
        assert valid_ko_ids[0] in data_dict["ko"]

    def test_validate_valid_dataset(self, dataset_with_samples):
        """Tests validation of a valid dataset using fixture."""
        # Should not raise exception
        dataset_with_samples.validate()
        assert not dataset_with_samples.is_empty()

    def test_validate_empty_dataset(self, empty_dataset):
        """Tests validation of an empty dataset using fixture."""
        with pytest.raises(ValueError, match="cannot be empty"):
            empty_dataset.validate()

    def test_dataset_str_representation(self, sample_with_kos):
        """Tests string representation using fixture."""
        dataset = Dataset()
        dataset.add_sample(sample_with_kos)

        str_repr = str(dataset)

        assert "1 samples" in str_repr
        # sample_with_kos has 5 KOs (from sample_ko_list)
        assert "5 unique KOs" in str_repr

