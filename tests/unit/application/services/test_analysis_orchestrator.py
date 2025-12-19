"""
Unit tests for AnalysisOrchestrator.

Tests cover:
- Workflow execution (happy path)
- Individual step execution
- Session state management
- Progress tracking integration
- Export coordination
- Error handling
"""

import pytest
import pandas as pd
from unittest.mock import Mock, MagicMock
from datetime import datetime

from src.application.services.analysis_orchestrator import (
    AnalysisOrchestrator,
    AnalysisSessionDTO
)
from src.application.core.upload_handler import UploadHandler
from src.application.core.data_processor import DataProcessor
from src.application.core.result_exporter import (
    ResultExporter,
    ExportFormat,
    ExportResultDTO
)
from src.application.services.cache_service import CacheService
from src.application.services.progress_tracker import ProgressTracker
from src.application.dto.upload_result_dto import UploadResultDTO
from src.application.dto.merged_data_dto import MergedDataDTO
from src.domain.entities.dataset import Dataset
from src.domain.entities.sample import Sample
from src.domain.value_objects.sample_id import SampleId
from src.domain.value_objects.kegg_orthology import KO


class TestAnalysisOrchestrator:
    """Test AnalysisOrchestrator workflow coordination."""
    
    @pytest.fixture
    def mock_upload_handler(self):
        """Create mock UploadHandler."""
        handler = Mock(spec=UploadHandler)
        
        # Mock successful upload
        sample = Sample(SampleId("S1"), [KO("K00001")])
        dataset = Dataset([sample])
        handler.process_upload.return_value = UploadResultDTO(
            success=True,
            dataset=dataset,
            filename="test.fasta",
            sample_count=1,
            ko_count=1,
            message="Upload successful"
        )
        return handler
    
    @pytest.fixture
    def mock_data_processor(self):
        """Create mock DataProcessor."""
        processor = Mock(spec=DataProcessor)
        
        # Mock successful processing
        df = pd.DataFrame({"Sample": ["S1"], "KO": ["K00001"]})
        processor.process.return_value = MergedDataDTO(
            biorempp_data=df,
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="test_key",
            processing_time_seconds=1.0
        )
        return processor
    
    @pytest.fixture
    def mock_result_exporter(self):
        """Create mock ResultExporter."""
        exporter = Mock(spec=ResultExporter)
        
        # Mock successful export
        exporter.export.return_value = ExportResultDTO(
            success=True,
            format=ExportFormat.CSV,
            data=b"Sample,KO\nS1,K00001",
            filename="results.csv",
            size_bytes=20,
            message="Export successful"
        )
        return exporter
    
    @pytest.fixture
    def mock_cache_service(self):
        """Create mock CacheService."""
        cache = Mock(spec=CacheService)
        cache.get.return_value = None  # No cache hit by default
        return cache
    
    @pytest.fixture
    def mock_progress_tracker(self):
        """Create mock ProgressTracker."""
        tracker = Mock(spec=ProgressTracker)
        return tracker
    
    @pytest.fixture
    def orchestrator(
        self,
        mock_upload_handler,
        mock_data_processor,
        mock_result_exporter,
        mock_cache_service,
        mock_progress_tracker
    ):
        """Create AnalysisOrchestrator with mocked dependencies."""
        return AnalysisOrchestrator(
            upload_handler=mock_upload_handler,
            data_processor=mock_data_processor,
            result_exporter=mock_result_exporter,
            cache_service=mock_cache_service,
            progress_tracker=mock_progress_tracker
        )
    
    def test_execute_workflow_success(self, orchestrator, mock_upload_handler):
        """Test successful workflow execution."""
        session = orchestrator.execute_workflow(
            content="base64_data",
            filename="test.fasta",
            session_id="session123",
            export_formats=[ExportFormat.CSV]
        )
        
        assert session.session_id == "session123"
        assert session.is_complete
        assert session.upload_result.success
        assert session.processing_result is not None
        assert len(session.export_results) == 1
        assert session.export_results[0].success
    
    def test_execute_workflow_calls_components(
        self,
        orchestrator,
        mock_upload_handler,
        mock_data_processor,
        mock_result_exporter,
        mock_progress_tracker
    ):
        """Test that workflow calls all components."""
        orchestrator.execute_workflow(
            content="data",
            filename="file.fasta",
            session_id="sess1"
        )
        
        # Verify upload handler called
        mock_upload_handler.process_upload.assert_called_once_with("data", "file.fasta")
        
        # Verify data processor called
        assert mock_data_processor.process.called
        
        # Verify exporter called
        assert mock_result_exporter.export.called
        
        # Verify progress tracker updated
        assert mock_progress_tracker.update_progress.call_count >= 3
    
    def test_execute_workflow_upload_failure(self, orchestrator, mock_upload_handler):
        """Test workflow handles upload failure gracefully."""
        # Mock upload failure
        mock_upload_handler.process_upload.return_value = UploadResultDTO(
            success=False,
            dataset=None,
            filename="test.fasta",
            sample_count=0,
            ko_count=0,
            message="Upload failed",
            errors=["Invalid format"]
        )
        
        session = orchestrator.execute_workflow(
            content="bad_data",
            filename="test.fasta",
            session_id="sess2"
        )
        
        assert not session.is_complete
        assert not session.upload_result.success
        assert session.processing_result is None
        assert len(session.export_results) == 0
    
    def test_execute_workflow_multiple_export_formats(
        self,
        orchestrator,
        mock_result_exporter
    ):
        """Test workflow with multiple export formats."""
        # Configure exporter to return different results
        export_results = [
            ExportResultDTO(
                success=True,
                format=ExportFormat.CSV,
                data=b"csv_data",
                filename="results.csv",
                size_bytes=8,
                message="CSV export"
            ),
            ExportResultDTO(
                success=True,
                format=ExportFormat.JSON,
                data=b"json_data",
                filename="results.json",
                size_bytes=9,
                message="JSON export"
            )
        ]
        mock_result_exporter.export.side_effect = export_results
        
        session = orchestrator.execute_workflow(
            content="data",
            filename="test.fasta",
            session_id="sess3",
            export_formats=[ExportFormat.CSV, ExportFormat.JSON]
        )
        
        assert len(session.export_results) == 2
        assert session.export_results[0].format == ExportFormat.CSV
        assert session.export_results[1].format == ExportFormat.JSON
    
    def test_process_upload_standalone(self, orchestrator, mock_upload_handler):
        """Test standalone upload processing."""
        result = orchestrator.process_upload("data", "file.fasta")
        
        assert result.success
        mock_upload_handler.process_upload.assert_called_once_with("data", "file.fasta")
    
    def test_process_data_standalone(self, orchestrator, mock_data_processor):
        """Test standalone data processing."""
        sample = Sample(SampleId("S1"), [KO("K00001")])
        dataset = Dataset([sample])
        
        result = orchestrator.process_data(dataset, "sess4")
        
        assert result is not None
        mock_data_processor.process.assert_called_once_with(dataset, "sess4")
    
    def test_export_results_standalone(self, orchestrator, mock_result_exporter):
        """Test standalone export."""
        df = pd.DataFrame({"A": [1, 2, 3]})
        
        results = orchestrator.export_results(
            data=df,
            session_id="sess5",
            formats=[ExportFormat.CSV]
        )
        
        assert len(results) == 1
        assert results[0].success
        mock_result_exporter.export.assert_called_once()
    
    def test_export_results_default_format(self, orchestrator, mock_result_exporter):
        """Test export with default CSV format."""
        df = pd.DataFrame({"A": [1]})
        
        results = orchestrator.export_results(df, "sess6")
        
        assert len(results) == 1
        # Verify CSV was used (default)
        call_args = mock_result_exporter.export.call_args
        assert call_args[0][1] == ExportFormat.CSV
    
    def test_get_session_state_exists(self, orchestrator):
        """Test retrieving existing session state."""
        # Execute workflow to create session
        orchestrator.execute_workflow(
            content="data",
            filename="test.fasta",
            session_id="sess7"
        )
        
        session = orchestrator.get_session_state("sess7")
        
        assert session is not None
        assert session.session_id == "sess7"
    
    def test_get_session_state_not_exists(self, orchestrator):
        """Test retrieving non-existent session."""
        session = orchestrator.get_session_state("nonexistent")
        
        assert session is None
    
    def test_get_progress(self, orchestrator, mock_progress_tracker):
        """Test getting progress for session."""
        from src.application.dto.processing_progress_dto import ProcessingProgressDTO

        mock_progress = ProcessingProgressDTO(
            current_stage="processing",
            stage_number=3,
            total_stages=8,
            progress_percentage=37.5,
            message="Processing data..."
        )
        mock_progress_tracker.get_progress.return_value = mock_progress
        
        progress = orchestrator.get_progress("sess8")
        
        assert progress is not None
        assert progress.progress_percentage == 37.5
        mock_progress_tracker.get_progress.assert_called_once_with("sess8")
    
    def test_clear_session(self, orchestrator, mock_cache_service):
        """Test clearing session data."""
        # Create session first
        orchestrator.execute_workflow(
            content="data",
            filename="test.fasta",
            session_id="sess9"
        )
        
        # Verify session exists
        assert orchestrator.get_session_state("sess9") is not None
        
        # Clear session
        orchestrator.clear_session("sess9")
        
        # Verify session removed
        assert orchestrator.get_session_state("sess9") is None
        # Verify cache cleared
        mock_cache_service.clear.assert_called_once()
    
    def test_session_dto_contains_timestamp(self, orchestrator):
        """Test that session DTO includes creation timestamp."""
        session = orchestrator.execute_workflow(
            content="data",
            filename="test.fasta",
            session_id="sess10"
        )
        
        assert session.created_at is not None
        # Verify it's a valid ISO format timestamp
        datetime.fromisoformat(session.created_at)
    
    def test_progress_tracking_at_each_step(
        self,
        orchestrator,
        mock_progress_tracker
    ):
        """Test that progress is tracked at each workflow step."""
        orchestrator.execute_workflow(
            content="data",
            filename="test.fasta",
            session_id="sess11"
        )
        
        # Should track: upload, processing, exporting, complete
        assert mock_progress_tracker.update_progress.call_count >= 4
        
        # Verify stages are tracked
        calls = mock_progress_tracker.update_progress.call_args_list
        stages = [call.kwargs.get('current_stage') for call in calls]
        
        assert 'upload' in stages
        assert 'processing' in stages
        assert 'exporting' in stages
        assert 'complete' in stages
