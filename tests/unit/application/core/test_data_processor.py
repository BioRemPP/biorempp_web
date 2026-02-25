"""
Unit tests for DataProcessor.

This test suite validates the DataProcessor class, which orchestrates
the entire data processing pipeline including cache checking, database
merging, progress tracking, and result preparation.

Test Coverage:
- Initialization
- Full processing pipeline
- Cache hit/miss scenarios
- Database merging coordination
- Result preparation
- Progress tracking integration
- Cache key generation
- Dataset to DataFrame conversion
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
import time

import src.application.core.data_processor as data_processor_module
from src.application.core.data_processor import DataProcessor
from src.application.dto.merged_data_dto import MergedDataDTO
from src.application.services.cache_service import CacheService
from src.application.services.progress_tracker import ProgressTracker
from src.domain.entities.dataset import Dataset
from src.domain.entities.sample import Sample
from src.domain.value_objects.kegg_orthology import KO
from src.domain.value_objects.sample_id import SampleId
from src.domain.services.merge_service import MergeService
from src.shared.exceptions import (
    CircuitBreakerOpenError,
    EmptyDataFrameError,
    RetryExhaustedError,
    StageProcessingError,
)


class TestDataProcessorInitialization:
    """Test DataProcessor initialization."""

    def test_initialization_with_all_dependencies(self):
        """Test initialization with all dependencies provided."""
        cache_service = Mock(spec=CacheService)
        progress_tracker = Mock(spec=ProgressTracker)
        merge_service = Mock(spec=MergeService)

        processor = DataProcessor(cache_service, progress_tracker, merge_service)

        assert processor._cache is cache_service
        assert processor._tracker is progress_tracker
        assert processor._merge_service is merge_service

    def test_initialization_without_merge_service(self):
        """Test initialization uses default MergeService if not provided."""
        cache_service = Mock(spec=CacheService)
        progress_tracker = Mock(spec=ProgressTracker)

        processor = DataProcessor(cache_service, progress_tracker)

        assert processor._cache is cache_service
        assert processor._tracker is progress_tracker
        assert processor._merge_service is MergeService

    def test_initialization_configures_timeout_and_circuit_breakers(self):
        """Test that processor initializes timeout and all circuit breakers."""
        cache = Mock()
        tracker = Mock()

        processor = DataProcessor(cache, tracker)

        assert processor._timeout_seconds == data_processor_module.DEFAULT_TIMEOUT_SECONDS
        assert set(processor._circuit_breakers.keys()) == {
            "biorempp",
            "kegg",
            "hadeg",
            "toxcsm",
        }


class TestDataProcessorProcess:
    """Test the main process() method."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for testing."""
        cache = Mock(spec=CacheService)
        tracker = Mock(spec=ProgressTracker)
        merge_service = Mock(spec=MergeService)
        return cache, tracker, merge_service

    @pytest.fixture
    def sample_dataset(self):
        """Create sample dataset for testing."""
        sample1 = Sample(id=SampleId("S1"), ko_list=[KO("K00001"), KO("K00002")])
        sample2 = Sample(id=SampleId("S2"), ko_list=[KO("K00003")])
        dataset = Dataset()
        dataset.add_sample(sample1)
        dataset.add_sample(sample2)
        return dataset

    def test_process_cache_hit(self, mock_dependencies, sample_dataset):
        """Test process returns cached result when available."""
        cache, tracker, merge_service = mock_dependencies

        # Setup cached result
        cached_dto = MergedDataDTO(
            biorempp_data=pd.DataFrame({"KO": ["K00001"]}),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="test_key",
            processing_time_seconds=1.0
        )
        cache.get.return_value = cached_dto

        processor = DataProcessor(cache, tracker, merge_service)
        result = processor.process(sample_dataset, "session_1")

        # Should return cached result
        assert result is cached_dto
        # Should complete tracking
        tracker.complete.assert_called_once()
        # Should not execute processing stages or recache data
        tracker.start_stage.assert_not_called()
        cache.set.assert_not_called()

    def test_process_cache_miss_performs_full_pipeline(self, mock_dependencies, sample_dataset):
        """Test process performs full pipeline when cache misses."""
        cache, tracker, merge_service = mock_dependencies

        # Setup cache miss
        cache.get.return_value = None
        cache.generate_hash_key.return_value = "test_cache_key"

        # Setup merge results
        biorempp_df = pd.DataFrame({"KO": ["K00001", "K00002"]})
        kegg_df = pd.DataFrame({"KO": ["K00001"]})
        hadeg_df = pd.DataFrame({"KO": ["K00001"]})
        toxcsm_df = pd.DataFrame({"KO": ["K00001"]})

        merge_service.merge_with_biorempp = Mock(return_value=biorempp_df)
        merge_service.merge_with_kegg = Mock(return_value=kegg_df)
        merge_service.merge_with_hadeg = Mock(return_value=hadeg_df)
        merge_service.merge_with_toxcsm = Mock(return_value=toxcsm_df)

        processor = DataProcessor(cache, tracker, merge_service)
        result = processor.process(sample_dataset, "session_1")

        # Verify all merges were called
        merge_service.merge_with_biorempp.assert_called_once()
        merge_service.merge_with_kegg.assert_called_once()
        merge_service.merge_with_hadeg.assert_called_once()
        merge_service.merge_with_toxcsm.assert_called_once()

        # Verify result is MergedDataDTO
        assert isinstance(result, MergedDataDTO)
        assert result.biorempp_data is biorempp_df

        # Verify cache was set
        cache.set.assert_called_once()

        # Verify progress tracking
        tracker.complete.assert_called()

    def test_process_updates_progress_through_stages(self, mock_dependencies, sample_dataset):
        """Test that process updates progress tracker through all stages."""
        cache, tracker, merge_service = mock_dependencies

        cache.get.return_value = None
        cache.generate_hash_key.return_value = "key"

        # Setup merge mocks
        merge_service.merge_with_biorempp = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_kegg = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_hadeg = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_toxcsm = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))

        processor = DataProcessor(cache, tracker, merge_service)
        processor.process(sample_dataset, "session_1")

        # Verify exact stage sequence
        stage_numbers = [call.args[0] for call in tracker.start_stage.call_args_list]
        assert stage_numbers == [3, 4, 5, 6, 7, 8]
        # Verify progress updates occurred
        assert tracker.update_progress.call_count >= 6

    def test_process_caches_result_with_ttl(self, mock_dependencies, sample_dataset):
        """Test that process caches result with correct TTL."""
        cache, tracker, merge_service = mock_dependencies

        cache.get.return_value = None
        cache.generate_hash_key.return_value = "test_key"

        merge_service.merge_with_biorempp = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_kegg = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_hadeg = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_toxcsm = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))

        processor = DataProcessor(cache, tracker, merge_service)
        processor.process(sample_dataset, "session_1")

        # Verify cache.set was called with TTL
        cache.set.assert_called_once()
        call_args = cache.set.call_args
        assert call_args[1]['ttl_seconds'] == 3600  # 1 hour

    def test_process_measures_processing_time(self, mock_dependencies, sample_dataset):
        """Test that process measures and includes processing time."""
        cache, tracker, merge_service = mock_dependencies

        cache.get.return_value = None
        cache.generate_hash_key.return_value = "key"

        merge_service.merge_with_biorempp = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_kegg = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_hadeg = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_toxcsm = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))

        start = time.time()
        processor = DataProcessor(cache, tracker, merge_service)
        result = processor.process(sample_dataset, "session_1")
        end = time.time()

        # Verify processing time is non-negative and bounded by wall-clock runtime
        assert result.processing_time_seconds >= 0
        assert result.processing_time_seconds <= (end - start) + 1


class TestDataProcessorPrepareResult:
    """Test the prepare_result() method."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies."""
        cache = Mock(spec=CacheService)
        tracker = Mock(spec=ProgressTracker)
        return cache, tracker

    def test_prepare_result_creates_dto(self, mock_dependencies):
        """Test that prepare_result creates MergedDataDTO."""
        cache, tracker = mock_dependencies

        biorempp_df = pd.DataFrame({"KO": ["K00001", "K00002"]})
        hadeg_df = pd.DataFrame({"KO": ["K00001"]})
        toxcsm_df = pd.DataFrame({"KO": ["K00001"]})

        merge_results = {
            "biorempp_df": biorempp_df,
            "kegg_df": None,
            "hadeg_df": hadeg_df,
            "toxcsm_df": toxcsm_df,
        }

        processor = DataProcessor(cache, tracker)
        result = processor.prepare_result(merge_results, "cache_key_123", 5.5)

        assert isinstance(result, MergedDataDTO)
        assert result.biorempp_data is biorempp_df
        assert result.hadeg_data is hadeg_df
        assert result.toxcsm_data is toxcsm_df
        assert result.cache_key == "cache_key_123"
        assert result.processing_time_seconds == 5.5

    def test_prepare_result_calculates_match_count(self, mock_dependencies):
        """Test that prepare_result calculates match count correctly."""
        cache, tracker = mock_dependencies

        biorempp_df = pd.DataFrame({"KO": ["K00001", "K00002", "K00003"]})

        merge_results = {
            "biorempp_df": biorempp_df,
            "kegg_df": None,
            "hadeg_df": None,
            "toxcsm_df": None,
        }

        processor = DataProcessor(cache, tracker)
        result = processor.prepare_result(merge_results, "key", 1.0)

        assert result.match_count == 3
        assert result.total_records == 3

    def test_prepare_result_handles_empty_dataframes(self, mock_dependencies):
        """Test prepare_result with empty DataFrames."""
        cache, tracker = mock_dependencies

        merge_results = {
            "biorempp_df": pd.DataFrame(),
            "kegg_df": None,
            "hadeg_df": None,
            "toxcsm_df": None,
        }

        processor = DataProcessor(cache, tracker)
        result = processor.prepare_result(merge_results, "key", 0.5)

        assert result.match_count == 0
        assert result.total_records == 0


class TestDataProcessorInternalErrorHandling:
    """Test DataProcessor private helpers for error handling."""

    @pytest.fixture
    def processor(self):
        """Create processor with mocked dependencies."""
        cache = Mock(spec=CacheService)
        tracker = Mock(spec=ProgressTracker)
        merge_service = Mock(spec=MergeService)
        return DataProcessor(cache, tracker, merge_service)

    def test_validate_dataframe_rejects_none(self, processor):
        """_validate_dataframe should reject None results."""
        with pytest.raises(EmptyDataFrameError, match="DataFrame is None"):
            processor._validate_dataframe(None, "StageX")

    def test_validate_dataframe_rejects_non_dataframe(self, processor):
        """_validate_dataframe should reject non-DataFrame values."""
        with pytest.raises(EmptyDataFrameError, match="not a DataFrame"):
            processor._validate_dataframe(["not", "a", "df"], "StageY")

    def test_validate_dataframe_rejects_empty_dataframe(self, processor):
        """_validate_dataframe should reject empty DataFrames."""
        with pytest.raises(EmptyDataFrameError, match="No data in result"):
            processor._validate_dataframe(pd.DataFrame(), "StageZ")

    def test_merge_with_retry_raises_after_exhausting_attempts(self, processor):
        """_merge_with_retry should raise RetryExhaustedError after all retries."""
        failing_merge = Mock(side_effect=ValueError("temporary failure"))

        with patch("src.application.core.data_processor.time.sleep", return_value=None):
            with pytest.raises(RetryExhaustedError, match="Failed after"):
                processor._merge_with_retry(failing_merge, dataset=Mock())

        assert failing_merge.call_count == data_processor_module.MAX_RETRIES + 1

    def test_process_stage_wraps_errors_as_stage_processing_error(self, processor):
        """_process_stage should wrap internal errors in StageProcessingError."""
        failing_merge = Mock(side_effect=ValueError("database unavailable"))

        with pytest.raises(StageProcessingError, match="BioRemPP"):
            processor._process_stage(
                stage_num=3,
                stage_name="BioRemPP Database Merge",
                stage_desc="Merging with main database",
                merge_func=failing_merge,
                breaker_key="biorempp",
                dataset=Mock(),
            )

        assert processor._circuit_breakers["biorempp"].failures == 1

    def test_process_stage_blocks_when_circuit_is_open(self, processor):
        """_process_stage should fail fast when circuit breaker is open."""
        breaker = processor._circuit_breakers["kegg"]
        breaker._is_open = True
        breaker.last_failure_time = time.time()
        merge_func = Mock()

        with pytest.raises(CircuitBreakerOpenError):
            processor._process_stage(
                stage_num=4,
                stage_name="KEGG Database Merge",
                stage_desc="Merging with KEGG pathways",
                merge_func=merge_func,
                breaker_key="kegg",
                biorempp_df=pd.DataFrame({"KO": ["K00001"]}),
            )

        merge_func.assert_not_called()


class TestDataProcessorDatasetToDataFrame:
    """Test the _dataset_to_dataframe() private method."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies."""
        cache = Mock(spec=CacheService)
        tracker = Mock(spec=ProgressTracker)
        return cache, tracker

    def test_dataset_to_dataframe_single_sample(self, mock_dependencies):
        """Test conversion of dataset with single sample."""
        cache, tracker = mock_dependencies

        sample = Sample(id=SampleId("S1"), ko_list=[KO("K00001"), KO("K00002")])
        dataset = Dataset()
        dataset.add_sample(sample)

        processor = DataProcessor(cache, tracker)
        df = processor._dataset_to_dataframe(dataset)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["sample", "ko"]
        assert all(df["sample"] == "S1")
        assert list(df["ko"]) == ["K00001", "K00002"]

    def test_dataset_to_dataframe_multiple_samples(self, mock_dependencies):
        """Test conversion of dataset with multiple samples."""
        cache, tracker = mock_dependencies

        sample1 = Sample(id=SampleId("S1"), ko_list=[KO("K00001")])
        sample2 = Sample(id=SampleId("S2"), ko_list=[KO("K00002"), KO("K00003")])
        dataset = Dataset()
        dataset.add_sample(sample1)
        dataset.add_sample(sample2)

        processor = DataProcessor(cache, tracker)
        df = processor._dataset_to_dataframe(dataset)

        assert len(df) == 3
        assert set(df["sample"]) == {"S1", "S2"}
        assert set(df["ko"]) == {"K00001", "K00002", "K00003"}

    def test_dataset_to_dataframe_empty_dataset(self, mock_dependencies):
        """Test conversion of empty dataset."""
        cache, tracker = mock_dependencies

        dataset = Dataset()

        processor = DataProcessor(cache, tracker)
        df = processor._dataset_to_dataframe(dataset)

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
        assert list(df.columns) == ["sample", "ko"]


class TestDataProcessorGenerateCacheKey:
    """Test the _generate_cache_key() private method."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies."""
        cache = Mock(spec=CacheService)
        cache.generate_hash_key = Mock(return_value="hashed_key_123")
        tracker = Mock(spec=ProgressTracker)
        return cache, tracker

    def test_generate_cache_key_creates_deterministic_key(self, mock_dependencies):
        """Test that cache key is deterministic for same dataset."""
        cache, tracker = mock_dependencies

        sample = Sample(id=SampleId("S1"), ko_list=[KO("K00001")])
        dataset = Dataset()
        dataset.add_sample(sample)

        processor = DataProcessor(cache, tracker)
        key1 = processor._generate_cache_key(dataset)
        key2 = processor._generate_cache_key(dataset)

        assert key1 == key2
        assert cache.generate_hash_key.called

    def test_generate_cache_key_sorts_samples(self, mock_dependencies):
        """Test that cache key generation sorts samples for consistency."""
        cache, tracker = mock_dependencies

        # Create datasets with same samples in different order
        sample1 = Sample(id=SampleId("S1"), ko_list=[KO("K00001")])
        sample2 = Sample(id=SampleId("S2"), ko_list=[KO("K00002")])

        dataset1 = Dataset()
        dataset1.add_sample(sample1)
        dataset1.add_sample(sample2)

        dataset2 = Dataset()
        dataset2.add_sample(sample2)
        dataset2.add_sample(sample1)

        processor = DataProcessor(cache, tracker)

        # Both should generate same content for hashing
        processor._generate_cache_key(dataset1)
        call1_content = cache.generate_hash_key.call_args[0][0]

        cache.generate_hash_key.reset_mock()
        processor._generate_cache_key(dataset2)
        call2_content = cache.generate_hash_key.call_args[0][0]

        # Content should be identical (sorted)
        assert call1_content == call2_content

    def test_generate_cache_key_different_datasets_different_keys(self, mock_dependencies):
        """Test that different datasets produce different cache keys."""
        cache, tracker = mock_dependencies
        cache.generate_hash_key = Mock(side_effect=lambda x: f"hash_{hash(x)}")

        sample1 = Sample(id=SampleId("S1"), ko_list=[KO("K00001")])
        sample2 = Sample(id=SampleId("S2"), ko_list=[KO("K00002")])

        dataset1 = Dataset()
        dataset1.add_sample(sample1)

        dataset2 = Dataset()
        dataset2.add_sample(sample2)

        processor = DataProcessor(cache, tracker)
        key1 = processor._generate_cache_key(dataset1)
        key2 = processor._generate_cache_key(dataset2)

        # Keys should be different
        assert key1 != key2


class TestDataProcessorIntegration:
    """Integration tests combining multiple components."""

    def test_full_pipeline_no_cache(self):
        """Test complete processing pipeline without cache."""
        # Setup mocks
        cache = Mock(spec=CacheService)
        cache.get.return_value = None  # Cache miss
        cache.generate_hash_key.return_value = "integration_test_key"

        tracker = Mock(spec=ProgressTracker)

        merge_service = Mock(spec=MergeService)
        merge_service.merge_with_biorempp = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_kegg = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_hadeg = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))
        merge_service.merge_with_toxcsm = Mock(return_value=pd.DataFrame({"KO": ["K00001"]}))

        # Create dataset
        sample = Sample(id=SampleId("IntegrationSample"), ko_list=[KO("K00001")])
        dataset = Dataset()
        dataset.add_sample(sample)

        # Process
        processor = DataProcessor(cache, tracker, merge_service)
        result = processor.process(dataset, "integration_session")

        # Verify
        assert isinstance(result, MergedDataDTO)
        assert result.cache_key == "integration_test_key"
        assert result.match_count == 1
        cache.set.assert_called_once()
        tracker.complete.assert_called_once()

    def test_full_pipeline_with_cache(self):
        """Test complete processing pipeline with cache hit."""
        cached_dto = MergedDataDTO(
            biorempp_data=pd.DataFrame({"KO": ["K00001"]}),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="cached_key",
            processing_time_seconds=0.5
        )

        cache = Mock(spec=CacheService)
        cache.get.return_value = cached_dto

        tracker = Mock(spec=ProgressTracker)
        merge_service = Mock(spec=MergeService)

        sample = Sample(id=SampleId("S1"), ko_list=[KO("K00001")])
        dataset = Dataset()
        dataset.add_sample(sample)

        processor = DataProcessor(cache, tracker, merge_service)
        result = processor.process(dataset, "cached_session")

        # Should return cached result immediately
        assert result is cached_dto
        # Tracker should complete
        tracker.complete.assert_called_once()
