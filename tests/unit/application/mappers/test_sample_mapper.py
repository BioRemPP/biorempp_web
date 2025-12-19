"""
Unit tests for SampleMapper.

Tests cover:
- Dataset to DataFrame conversion
- DataFrame to Dataset conversion
- Dataset to dictionary conversion
- Dictionary to Dataset conversion
- Empty data handling
- Invalid data handling
"""

import pytest
import pandas as pd

from biorempp_web.src.application.mappers.sample_mapper import SampleMapper
from biorempp_web.src.domain.entities.sample import Sample
from biorempp_web.src.domain.entities.dataset import Dataset
from biorempp_web.src.domain.value_objects.sample_id import SampleId
from biorempp_web.src.domain.value_objects.kegg_orthology import KO


class TestSampleMapperToDataFrame:
    """Test Dataset to DataFrame conversion."""
    
    def test_to_dataframe_single_sample_single_ko(self):
        """Test converting dataset with one sample and one KO."""
        sample = Sample(id=SampleId("S1"), ko_list=[KO("K00001")])
        dataset = Dataset([sample])

        df = SampleMapper.to_dataframe(dataset)

        assert len(df) == 1
        assert list(df.columns) == ["Sample", "KO"]
        assert df.iloc[0]["Sample"] == "S1"
        assert df.iloc[0]["KO"] == "K00001"

    def test_to_dataframe_single_sample_multiple_kos(self):
        """Test converting dataset with one sample and multiple KOs."""
        sample = Sample(
            id=SampleId("S1"),
            ko_list=[KO("K00001"), KO("K00002"), KO("K00003")]
        )
        dataset = Dataset([sample])

        df = SampleMapper.to_dataframe(dataset)

        assert len(df) == 3
        assert all(df["Sample"] == "S1")
        assert list(df["KO"]) == ["K00001", "K00002", "K00003"]

    def test_to_dataframe_multiple_samples(self):
        """Test converting dataset with multiple samples."""
        samples = [
            Sample(id=SampleId("S1"), ko_list=[KO("K00001")]),
            Sample(id=SampleId("S2"), ko_list=[KO("K00002"), KO("K00003")]),
            Sample(id=SampleId("S3"), ko_list=[KO("K00004")])
        ]
        dataset = Dataset(samples)
        
        df = SampleMapper.to_dataframe(dataset)
        
        assert len(df) == 4
        assert set(df["Sample"]) == {"S1", "S2", "S3"}
        assert len(df[df["Sample"] == "S2"]) == 2
    
    def test_to_dataframe_empty_dataset(self):
        """Test converting empty dataset."""
        dataset = Dataset([])
        
        df = SampleMapper.to_dataframe(dataset)
        
        assert df.empty
        assert list(df.columns) == ["Sample", "KO"]


class TestSampleMapperFromDataFrame:
    """Test DataFrame to Dataset conversion."""
    
    def test_from_dataframe_single_row(self):
        """Test converting DataFrame with single row."""
        df = pd.DataFrame({
            "Sample": ["S1"],
            "KO": ["K00001"]
        })
        
        dataset = SampleMapper.from_dataframe(df)
        
        assert len(dataset.samples) == 1
        assert dataset.samples[0].id.value == "S1"
        assert len(dataset.samples[0].ko_list) == 1
        assert dataset.samples[0].ko_list[0].id == "K00001"
    
    def test_from_dataframe_multiple_kos_same_sample(self):
        """Test converting DataFrame with multiple KOs for one sample."""
        df = pd.DataFrame({
            "Sample": ["S1", "S1", "S1"],
            "KO": ["K00001", "K00002", "K00003"]
        })
        
        dataset = SampleMapper.from_dataframe(df)
        
        assert len(dataset.samples) == 1
        assert dataset.samples[0].id.value == "S1"
        assert len(dataset.samples[0].ko_list) == 3
        ko_ids = [ko.id for ko in dataset.samples[0].ko_list]
        assert ko_ids == ["K00001", "K00002", "K00003"]
    
    def test_from_dataframe_multiple_samples(self):
        """Test converting DataFrame with multiple samples."""
        df = pd.DataFrame({
            "Sample": ["S1", "S1", "S2", "S3"],
            "KO": ["K00001", "K00002", "K00003", "K00004"]
        })
        
        dataset = SampleMapper.from_dataframe(df)
        
        assert len(dataset.samples) == 3
        sample_ids = [s.id.value for s in dataset.samples]
        assert "S1" in sample_ids
        assert "S2" in sample_ids
        assert "S3" in sample_ids
    
    def test_from_dataframe_empty(self):
        """Test converting empty DataFrame."""
        df = pd.DataFrame(columns=["Sample", "KO"])
        
        dataset = SampleMapper.from_dataframe(df)
        
        assert len(dataset.samples) == 0
    
    def test_from_dataframe_missing_sample_column_raises_error(self):
        """Test that missing Sample column raises error."""
        df = pd.DataFrame({"KO": ["K00001"]})
        
        with pytest.raises(ValueError, match="must have 'Sample' and 'KO'"):
            SampleMapper.from_dataframe(df)
    
    def test_from_dataframe_missing_ko_column_raises_error(self):
        """Test that missing KO column raises error."""
        df = pd.DataFrame({"Sample": ["S1"]})
        
        with pytest.raises(ValueError, match="must have 'Sample' and 'KO'"):
            SampleMapper.from_dataframe(df)
    
    def test_from_dataframe_invalid_ko_raises_error(self):
        """Test that invalid KO format raises error."""
        df = pd.DataFrame({
            "Sample": ["S1"],
            "KO": ["INVALID"]
        })
        
        with pytest.raises(ValueError):
            SampleMapper.from_dataframe(df)


class TestSampleMapperToDict:
    """Test Dataset to dictionary conversion."""
    
    def test_samples_to_dict_single_sample(self):
        """Test converting dataset to dict with single sample."""
        sample = Sample(SampleId("S1"), [KO("K00001"), KO("K00002")])
        dataset = Dataset([sample])
        
        result = SampleMapper.samples_to_dict(dataset)
        
        assert result == {"S1": ["K00001", "K00002"]}
    
    def test_samples_to_dict_multiple_samples(self):
        """Test converting dataset to dict with multiple samples."""
        samples = [
            Sample(SampleId("S1"), [KO("K00001")]),
            Sample(SampleId("S2"), [KO("K00002"), KO("K00003")]),
            Sample(SampleId("S3"), [KO("K00004")])
        ]
        dataset = Dataset(samples)
        
        result = SampleMapper.samples_to_dict(dataset)
        
        assert result == {
            "S1": ["K00001"],
            "S2": ["K00002", "K00003"],
            "S3": ["K00004"]
        }
    
    def test_samples_to_dict_empty_dataset(self):
        """Test converting empty dataset to dict."""
        dataset = Dataset([])
        
        result = SampleMapper.samples_to_dict(dataset)
        
        assert result == {}


class TestSampleMapperFromDict:
    """Test dictionary to Dataset conversion."""
    
    def test_dict_to_dataset_single_sample(self):
        """Test converting dict to dataset with single sample."""
        data = {"S1": ["K00001", "K00002"]}
        
        dataset = SampleMapper.dict_to_dataset(data)
        
        assert len(dataset.samples) == 1
        assert dataset.samples[0].id.value == "S1"
        assert len(dataset.samples[0].ko_list) == 2
    
    def test_dict_to_dataset_multiple_samples(self):
        """Test converting dict to dataset with multiple samples."""
        data = {
            "S1": ["K00001"],
            "S2": ["K00002", "K00003"],
            "S3": ["K00004"]
        }
        
        dataset = SampleMapper.dict_to_dataset(data)
        
        assert len(dataset.samples) == 3
        sample_ids = [s.id.value for s in dataset.samples]
        assert set(sample_ids) == {"S1", "S2", "S3"}
    
    def test_dict_to_dataset_empty_dict(self):
        """Test converting empty dict to dataset."""
        data = {}
        
        dataset = SampleMapper.dict_to_dataset(data)
        
        assert len(dataset.samples) == 0
    
    def test_dict_to_dataset_invalid_ko_raises_error(self):
        """Test that invalid KO in dict raises error."""
        data = {"S1": ["INVALID"]}
        
        with pytest.raises(ValueError):
            SampleMapper.dict_to_dataset(data)


class TestSampleMapperRoundTrip:
    """Test round-trip conversions (no data loss)."""
    
    def test_dataset_to_dataframe_to_dataset(self):
        """Test Dataset → DataFrame → Dataset preserves data."""
        original_samples = [
            Sample(SampleId("S1"), [KO("K00001"), KO("K00002")]),
            Sample(SampleId("S2"), [KO("K00003")])
        ]
        original_dataset = Dataset(original_samples)
        
        # Convert to DataFrame and back
        df = SampleMapper.to_dataframe(original_dataset)
        reconstructed_dataset = SampleMapper.from_dataframe(df)
        
        # Verify same number of samples
        assert len(reconstructed_dataset.samples) == len(original_dataset.samples)
        
        # Verify same sample IDs
        original_ids = {s.id.value for s in original_dataset.samples}
        reconstructed_ids = {s.id.value for s in reconstructed_dataset.samples}
        assert original_ids == reconstructed_ids
    
    def test_dataset_to_dict_to_dataset(self):
        """Test Dataset → dict → Dataset preserves data."""
        original_samples = [
            Sample(SampleId("S1"), [KO("K00001")]),
            Sample(SampleId("S2"), [KO("K00002"), KO("K00003")])
        ]
        original_dataset = Dataset(original_samples)
        
        # Convert to dict and back
        data_dict = SampleMapper.samples_to_dict(original_dataset)
        reconstructed_dataset = SampleMapper.dict_to_dataset(data_dict)
        
        # Verify same structure
        assert len(reconstructed_dataset.samples) == len(original_dataset.samples)
        
        # Verify same KO counts
        original_ko_counts = {
            s.id.value: len(s.ko_list) for s in original_dataset.samples
        }
        reconstructed_ko_counts = {
            s.id.value: len(s.ko_list) for s in reconstructed_dataset.samples
        }
        assert original_ko_counts == reconstructed_ko_counts
