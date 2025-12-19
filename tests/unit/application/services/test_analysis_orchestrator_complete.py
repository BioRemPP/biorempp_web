"""
Unit tests for AnalysisOrchestrator.

This test suite validates the AnalysisOrchestrator class, which is the high-level
coordinator for the complete analysis workflow from upload through processing to export.

Test Coverage:
- Initialization and dependency injection
- Complete workflow execution (execute_workflow)
- Upload processing
- Data processing
- Result exporting (single and multiple formats)
- Session state management
- Progress tracking integration
- Error handling at each stage
- Cache integration
- Edge cases and error scenarios
"""

import pytest
import pandas as pd
from unittest.mock import Mock
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
from src.application.dto.processing_progress_dto import ProcessingProgressDTO
from src.domain.entities.dataset import Dataset
from src.domain.entities.sample import Sample
from src.domain.value_objects.kegg_orthology import KO
from src.domain.value_objects.sample_id import SampleId


class TestAnalysisOrchestratorInitialization:
    """Test AnalysisOrchestrator initialization."""

    def test_initialization_with_all_dependencies(self):
        """Test initialization with all required dependencies."""
        upload_handler = Mock(spec=UploadHandler)
        data_processor = Mock(spec=DataProcessor)
        result_exporter = Mock(spec=ResultExporter)
        cache_service = Mock(spec=CacheService)
        progress_tracker = Mock(spec=ProgressTracker)

        orchestrator = AnalysisOrchestrator(
            upload_handler=upload_handler,
            data_processor=data_processor,
            result_exporter=result_exporter,
            cache_service=cache_service,
            progress_tracker=progress_tracker
        )

        assert orchestrator._upload_handler is upload_handler
        assert orchestrator._data_processor is data_processor
        assert orchestrator._result_exporter is result_exporter
        assert orchestrator._cache_service is cache_service
        assert orchestrator._progress_tracker is progress_tracker
        assert orchestrator._sessions == {}

    def test_initialization_creates_empty_sessions_dict(self):
        """Test that initialization creates empty sessions dictionary."""
        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=Mock(),
            cache_service=Mock(),
            progress_tracker=Mock()
        )

        assert isinstance(orchestrator._sessions, dict)
        assert len(orchestrator._sessions) == 0


class TestAnalysisOrchestratorExecuteWorkflow:
    """Test the main execute_workflow() method."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for testing."""
        upload_handler = Mock(spec=UploadHandler)
        data_processor = Mock(spec=DataProcessor)
        result_exporter = Mock(spec=ResultExporter)
        cache_service = Mock(spec=CacheService)
        progress_tracker = Mock(spec=ProgressTracker)

        return {
            'upload_handler': upload_handler,
            'data_processor': data_processor,
            'result_exporter': result_exporter,
            'cache_service': cache_service,
            'progress_tracker': progress_tracker
        }

    @pytest.fixture
    def sample_dataset(self):
        """Create sample dataset for testing."""
        sample = Sample(id=SampleId("S1"), ko_list=[KO("K00001"), KO("K00002")])
        dataset = Dataset()
        dataset.add_sample(sample)
        return dataset

    def test_execute_workflow_success_with_default_export(
        self, mock_dependencies, sample_dataset
    ):
        """Test successful workflow execution with default CSV export."""
        deps = mock_dependencies

        # Setup successful upload
        upload_result = UploadResultDTO(
            success=True,
            dataset=sample_dataset,
            filename="test.fasta",
            sample_count=1,
            ko_count=2,
            message="Upload successful",
            errors=None
        )
        deps['upload_handler'].process_upload = Mock(return_value=upload_result)

        # Setup successful processing
        processing_result = MergedDataDTO(
            biorempp_data=pd.DataFrame({"KO": ["K00001"]}),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="test_key",
            processing_time_seconds=1.0
        )
        deps['data_processor'].process = Mock(return_value=processing_result)

        # Setup successful export
        export_result = ExportResultDTO(
            success=True,
            format=ExportFormat.CSV,
            data=b"KO\nK00001",
            filename="biorempp_results_session123.csv",
            size_bytes=11,
            message="Export successful",
            error=""
        )
        deps['result_exporter'].export = Mock(return_value=export_result)

        orchestrator = AnalysisOrchestrator(**deps)

        # Execute workflow
        session = orchestrator.execute_workflow(
            content="base64_content",
            filename="test.fasta",
            session_id="session123"
        )

        # Verify session state
        assert session.session_id == "session123"
        assert session.is_complete is True
        assert session.upload_result is upload_result
        assert session.processing_result is processing_result
        assert len(session.export_results) == 1
        assert session.export_results[0] is export_result
        assert session.created_at is not None

        # Verify calls
        deps['upload_handler'].process_upload.assert_called_once_with(
            "base64_content", "test.fasta"
        )
        deps['data_processor'].process.assert_called_once_with(
            dataset=sample_dataset, session_id="session123"
        )
        deps['result_exporter'].export.assert_called_once()

    def test_execute_workflow_with_multiple_export_formats(
        self, mock_dependencies, sample_dataset
    ):
        """Test workflow execution with multiple export formats."""
        deps = mock_dependencies

        # Setup mocks
        upload_result = UploadResultDTO(
            success=True,
            dataset=sample_dataset,
            filename="test.fasta",
            sample_count=1,
            ko_count=2,
            message="Upload successful",
            errors=None
        )
        deps['upload_handler'].process_upload = Mock(return_value=upload_result)

        processing_result = MergedDataDTO(
            biorempp_data=pd.DataFrame({"KO": ["K00001"]}),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="test_key",
            processing_time_seconds=1.0
        )
        deps['data_processor'].process = Mock(return_value=processing_result)

        # Setup export results for different formats
        csv_export = ExportResultDTO(
            success=True, format=ExportFormat.CSV, data=b"csv",
            filename="test.csv", size_bytes=3, message="OK", error=""
        )
        excel_export = ExportResultDTO(
            success=True, format=ExportFormat.EXCEL, data=b"xlsx",
            filename="test.xlsx", size_bytes=4, message="OK", error=""
        )
        json_export = ExportResultDTO(
            success=True, format=ExportFormat.JSON, data=b"json",
            filename="test.json", size_bytes=4, message="OK", error=""
        )

        deps['result_exporter'].export = Mock(
            side_effect=[csv_export, excel_export, json_export]
        )

        orchestrator = AnalysisOrchestrator(**deps)

        # Execute with multiple formats
        session = orchestrator.execute_workflow(
            content="base64_content",
            filename="test.fasta",
            session_id="session123",
            export_formats=[ExportFormat.CSV, ExportFormat.EXCEL, ExportFormat.JSON]
        )

        # Verify exports
        assert len(session.export_results) == 3
        assert session.export_results[0].format == ExportFormat.CSV
        assert session.export_results[1].format == ExportFormat.EXCEL
        assert session.export_results[2].format == ExportFormat.JSON
        assert deps['result_exporter'].export.call_count == 3

    def test_execute_workflow_upload_failure(self, mock_dependencies):
        """Test workflow execution when upload fails."""
        deps = mock_dependencies

        # Setup failed upload
        upload_result = UploadResultDTO(
            success=False,
            dataset=None,
            filename="test.txt",
            sample_count=0,
            ko_count=0,
            message="Upload failed",
            errors=["Invalid file format"]
        )
        deps['upload_handler'].process_upload = Mock(return_value=upload_result)

        orchestrator = AnalysisOrchestrator(**deps)

        # Execute workflow
        session = orchestrator.execute_workflow(
            content="invalid_content",
            filename="test.txt",
            session_id="session123"
        )

        # Verify session state
        assert session.session_id == "session123"
        assert session.is_complete is False
        assert session.upload_result is upload_result
        assert session.processing_result is None
        assert len(session.export_results) == 0

        # Verify processing and export were NOT called
        deps['data_processor'].process.assert_not_called()
        deps['result_exporter'].export.assert_not_called()

    def test_execute_workflow_updates_progress(
        self, mock_dependencies, sample_dataset
    ):
        """Test that workflow updates progress at each stage."""
        deps = mock_dependencies

        # Setup successful mocks
        upload_result = UploadResultDTO(
            success=True,
            dataset=sample_dataset,
            filename="test.fasta",
            sample_count=1,
            ko_count=2,
            message="OK",
            errors=None
        )
        deps['upload_handler'].process_upload = Mock(return_value=upload_result)

        processing_result = MergedDataDTO(
            biorempp_data=pd.DataFrame({"KO": ["K00001"]}),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="test_key",
            processing_time_seconds=1.0
        )
        deps['data_processor'].process = Mock(return_value=processing_result)

        export_result = ExportResultDTO(
            success=True, format=ExportFormat.CSV, data=b"csv",
            filename="test.csv", size_bytes=3, message="OK", error=""
        )
        deps['result_exporter'].export = Mock(return_value=export_result)

        orchestrator = AnalysisOrchestrator(**deps)

        # Execute workflow
        orchestrator.execute_workflow(
            content="content",
            filename="test.fasta",
            session_id="session123"
        )

        # Verify progress updates
        progress_calls = deps['progress_tracker'].update_progress.call_args_list
        assert len(progress_calls) >= 3  # upload, processing, exporting, complete

        # Verify upload stage
        upload_call = progress_calls[0][1]
        assert upload_call['session_id'] == "session123"
        assert upload_call['current_stage'] == "upload"
        assert upload_call['stage_number'] == 1

        # Verify processing stage
        processing_call = progress_calls[1][1]
        assert processing_call['current_stage'] == "processing"
        assert processing_call['stage_number'] == 2

    def test_execute_workflow_stores_session(
        self, mock_dependencies, sample_dataset
    ):
        """Test that workflow stores session in internal state."""
        deps = mock_dependencies

        upload_result = UploadResultDTO(
            success=True,
            dataset=sample_dataset,
            filename="test.fasta",
            sample_count=1,
            ko_count=2,
            message="OK",
            errors=None
        )
        deps['upload_handler'].process_upload = Mock(return_value=upload_result)

        processing_result = MergedDataDTO(
            biorempp_data=pd.DataFrame({"KO": ["K00001"]}),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="test_key",
            processing_time_seconds=1.0
        )
        deps['data_processor'].process = Mock(return_value=processing_result)

        export_result = ExportResultDTO(
            success=True, format=ExportFormat.CSV, data=b"csv",
            filename="test.csv", size_bytes=3, message="OK", error=""
        )
        deps['result_exporter'].export = Mock(return_value=export_result)

        orchestrator = AnalysisOrchestrator(**deps)

        # Execute workflow
        session = orchestrator.execute_workflow(
            content="content",
            filename="test.fasta",
            session_id="session123"
        )

        # Verify session is stored
        assert "session123" in orchestrator._sessions
        assert orchestrator._sessions["session123"] is session


class TestAnalysisOrchestratorExportByFormat:
    """Test the _export_result_by_format() private method."""

    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies."""
        return {
            'upload_handler': Mock(),
            'data_processor': Mock(),
            'result_exporter': Mock(spec=ResultExporter),
            'cache_service': Mock(),
            'progress_tracker': Mock()
        }

    @pytest.fixture
    def processing_result(self):
        """Create processing result DTO."""
        return MergedDataDTO(
            biorempp_data=pd.DataFrame({"KO": ["K00001"]}),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="test_key",
            processing_time_seconds=1.0
        )

    def test_export_by_format_csv(self, mock_dependencies, processing_result):
        """Test export with CSV format."""
        deps = mock_dependencies
        export_result = ExportResultDTO(
            success=True, format=ExportFormat.CSV, data=b"csv",
            filename="test.csv", size_bytes=3, message="OK", error=""
        )
        deps['result_exporter'].export = Mock(return_value=export_result)

        orchestrator = AnalysisOrchestrator(**deps)

        result = orchestrator._export_result_by_format(
            processing_result=processing_result,
            format=ExportFormat.CSV,
            session_id="session123"
        )

        assert result is export_result
        deps['result_exporter'].export.assert_called_once()
        call_args = deps['result_exporter'].export.call_args
        assert call_args[0][1] == ExportFormat.CSV
        assert "session123" in call_args[0][2]
        assert ".csv" in call_args[0][2]

    def test_export_by_format_excel(self, mock_dependencies, processing_result):
        """Test export with Excel format."""
        deps = mock_dependencies
        export_result = ExportResultDTO(
            success=True, format=ExportFormat.EXCEL, data=b"xlsx",
            filename="test.xlsx", size_bytes=4, message="OK", error=""
        )
        deps['result_exporter'].export = Mock(return_value=export_result)

        orchestrator = AnalysisOrchestrator(**deps)

        result = orchestrator._export_result_by_format(
            processing_result=processing_result,
            format=ExportFormat.EXCEL,
            session_id="session123"
        )

        assert result is export_result
        call_args = deps['result_exporter'].export.call_args
        assert call_args[0][1] == ExportFormat.EXCEL
        assert ".xlsx" in call_args[0][2]

    def test_export_by_format_json(self, mock_dependencies, processing_result):
        """Test export with JSON format."""
        deps = mock_dependencies
        export_result = ExportResultDTO(
            success=True, format=ExportFormat.JSON, data=b"json",
            filename="test.json", size_bytes=4, message="OK", error=""
        )
        deps['result_exporter'].export = Mock(return_value=export_result)

        orchestrator = AnalysisOrchestrator(**deps)

        result = orchestrator._export_result_by_format(
            processing_result=processing_result,
            format=ExportFormat.JSON,
            session_id="session123"
        )

        assert result is export_result
        call_args = deps['result_exporter'].export.call_args
        assert call_args[0][1] == ExportFormat.JSON
        assert ".json" in call_args[0][2]

    def test_export_by_format_unsupported_format(
        self, mock_dependencies, processing_result
    ):
        """Test export with unsupported format returns error DTO."""
        deps = mock_dependencies

        orchestrator = AnalysisOrchestrator(**deps)

        # Create a mock unsupported format
        unsupported_format = "UNSUPPORTED"

        result = orchestrator._export_result_by_format(
            processing_result=processing_result,
            format=unsupported_format,
            session_id="session123"
        )

        # Should return error DTO without calling exporter
        assert result.success is False
        assert "Unsupported format" in result.error
        deps['result_exporter'].export.assert_not_called()


class TestAnalysisOrchestratorProcessUpload:
    """Test the process_upload() method."""

    def test_process_upload_delegates_to_handler(self):
        """Test that process_upload delegates to upload handler."""
        upload_handler = Mock(spec=UploadHandler)
        upload_result = UploadResultDTO(
            success=True,
            dataset=Dataset(),
            filename="test.fasta",
            sample_count=0,
            ko_count=0,
            message="OK",
            errors=None
        )
        upload_handler.process_upload = Mock(return_value=upload_result)

        orchestrator = AnalysisOrchestrator(
            upload_handler=upload_handler,
            data_processor=Mock(),
            result_exporter=Mock(),
            cache_service=Mock(),
            progress_tracker=Mock()
        )

        result = orchestrator.process_upload("content", "test.fasta")

        assert result is upload_result
        upload_handler.process_upload.assert_called_once_with(
            "content", "test.fasta"
        )


class TestAnalysisOrchestratorProcessData:
    """Test the process_data() method."""

    def test_process_data_delegates_to_processor(self):
        """Test that process_data delegates to data processor."""
        data_processor = Mock(spec=DataProcessor)
        processing_result = MergedDataDTO(
            biorempp_data=pd.DataFrame({"KO": ["K00001"]}),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="test_key",
            processing_time_seconds=1.0
        )
        data_processor.process = Mock(return_value=processing_result)

        dataset = Dataset()
        sample = Sample(id=SampleId("S1"), ko_list=[KO("K00001")])
        dataset.add_sample(sample)

        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=data_processor,
            result_exporter=Mock(),
            cache_service=Mock(),
            progress_tracker=Mock()
        )

        result = orchestrator.process_data(dataset, "session123")

        assert result is processing_result
        data_processor.process.assert_called_once_with(dataset, "session123")


class TestAnalysisOrchestratorExportResults:
    """Test the export_results() method."""

    def test_export_results_with_single_format(self):
        """Test exporting with single format."""
        result_exporter = Mock(spec=ResultExporter)
        export_result = ExportResultDTO(
            success=True, format=ExportFormat.CSV, data=b"csv",
            filename="test.csv", size_bytes=3, message="OK", error=""
        )
        result_exporter.export = Mock(return_value=export_result)

        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=result_exporter,
            cache_service=Mock(),
            progress_tracker=Mock()
        )

        df = pd.DataFrame({"KO": ["K00001"]})
        results = orchestrator.export_results(
            data=df,
            session_id="session123",
            formats=[ExportFormat.CSV]
        )

        assert len(results) == 1
        assert results[0] is export_result
        result_exporter.export.assert_called_once()

    def test_export_results_with_multiple_formats(self):
        """Test exporting with multiple formats."""
        result_exporter = Mock(spec=ResultExporter)

        csv_result = ExportResultDTO(
            success=True, format=ExportFormat.CSV, data=b"csv",
            filename="test.csv", size_bytes=3, message="OK", error=""
        )
        json_result = ExportResultDTO(
            success=True, format=ExportFormat.JSON, data=b"json",
            filename="test.json", size_bytes=4, message="OK", error=""
        )

        result_exporter.export = Mock(side_effect=[csv_result, json_result])

        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=result_exporter,
            cache_service=Mock(),
            progress_tracker=Mock()
        )

        df = pd.DataFrame({"KO": ["K00001"]})
        results = orchestrator.export_results(
            data=df,
            session_id="session123",
            formats=[ExportFormat.CSV, ExportFormat.JSON]
        )

        assert len(results) == 2
        assert results[0].format == ExportFormat.CSV
        assert results[1].format == ExportFormat.JSON
        assert result_exporter.export.call_count == 2

    def test_export_results_default_format_is_csv(self):
        """Test that default export format is CSV."""
        result_exporter = Mock(spec=ResultExporter)
        export_result = ExportResultDTO(
            success=True, format=ExportFormat.CSV, data=b"csv",
            filename="test.csv", size_bytes=3, message="OK", error=""
        )
        result_exporter.export = Mock(return_value=export_result)

        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=result_exporter,
            cache_service=Mock(),
            progress_tracker=Mock()
        )

        df = pd.DataFrame({"KO": ["K00001"]})
        results = orchestrator.export_results(
            data=df,
            session_id="session123"
            # formats not specified - should default to CSV
        )

        assert len(results) == 1
        assert results[0].format == ExportFormat.CSV


class TestAnalysisOrchestratorSessionManagement:
    """Test session state management methods."""

    def test_get_session_state_existing_session(self):
        """Test retrieving existing session state."""
        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=Mock(),
            cache_service=Mock(),
            progress_tracker=Mock()
        )

        # Manually add a session
        session = AnalysisSessionDTO(
            session_id="session123",
            upload_result=None,
            processing_result=None,
            export_results=[],
            created_at=datetime.now().isoformat(),
            is_complete=False
        )
        orchestrator._sessions["session123"] = session

        # Retrieve it
        retrieved = orchestrator.get_session_state("session123")

        assert retrieved is session
        assert retrieved.session_id == "session123"

    def test_get_session_state_nonexistent_session(self):
        """Test retrieving non-existent session returns None."""
        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=Mock(),
            cache_service=Mock(),
            progress_tracker=Mock()
        )

        result = orchestrator.get_session_state("nonexistent")

        assert result is None

    def test_get_progress_delegates_to_tracker(self):
        """Test that get_progress delegates to progress tracker."""
        progress_tracker = Mock(spec=ProgressTracker)
        progress_dto = ProcessingProgressDTO(
            current_stage="processing",
            stage_number=2,
            total_stages=8,
            progress_percentage=30.0,
            message="Processing...",
            estimated_time_remaining=None,
            error=None
        )
        progress_tracker.get_progress = Mock(return_value=progress_dto)

        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=Mock(),
            cache_service=Mock(),
            progress_tracker=progress_tracker
        )

        result = orchestrator.get_progress("session123")

        assert result is progress_dto
        progress_tracker.get_progress.assert_called_once_with("session123")

    def test_clear_session_removes_session_from_dict(self):
        """Test that clear_session removes session from internal storage."""
        cache_service = Mock(spec=CacheService)

        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=Mock(),
            cache_service=cache_service,
            progress_tracker=Mock()
        )

        # Add a session
        session = AnalysisSessionDTO(
            session_id="session123",
            upload_result=None,
            processing_result=None,
            export_results=[],
            created_at=datetime.now().isoformat(),
            is_complete=False
        )
        orchestrator._sessions["session123"] = session

        # Clear it
        orchestrator.clear_session("session123")

        # Verify removed
        assert "session123" not in orchestrator._sessions
        cache_service.clear.assert_called_once()

    def test_clear_session_nonexistent_session_does_not_error(self):
        """Test clearing non-existent session doesn't raise error."""
        cache_service = Mock(spec=CacheService)

        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=Mock(),
            cache_service=cache_service,
            progress_tracker=Mock()
        )

        # Should not raise error
        orchestrator.clear_session("nonexistent")

        # Cache should still be cleared
        cache_service.clear.assert_called_once()


class TestAnalysisSessionDTO:
    """Test AnalysisSessionDTO dataclass."""

    def test_analysis_session_dto_creation(self):
        """Test creating AnalysisSessionDTO."""
        session = AnalysisSessionDTO(
            session_id="abc123",
            upload_result=None,
            processing_result=None,
            export_results=[],
            created_at="2025-11-13T10:00:00",
            is_complete=False
        )

        assert session.session_id == "abc123"
        assert session.upload_result is None
        assert session.processing_result is None
        assert session.export_results == []
        assert session.created_at == "2025-11-13T10:00:00"
        assert session.is_complete is False

    def test_analysis_session_dto_is_frozen(self):
        """Test that AnalysisSessionDTO is immutable (frozen)."""
        session = AnalysisSessionDTO(
            session_id="abc123",
            upload_result=None,
            processing_result=None,
            export_results=[],
            created_at="2025-11-13T10:00:00",
            is_complete=False
        )

        # Should not be able to modify frozen dataclass
        with pytest.raises(AttributeError):
            session.session_id = "new_id"

    def test_analysis_session_dto_with_complete_workflow(self):
        """Test AnalysisSessionDTO with all workflow results."""
        upload_result = UploadResultDTO(
            success=True,
            dataset=Dataset(),
            filename="test.fasta",
            sample_count=0,
            ko_count=0,
            message="Upload OK",
            errors=None
        )

        processing_result = MergedDataDTO(
            biorempp_data=pd.DataFrame({"KO": ["K00001"]}),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=1,
            total_records=1,
            cache_key="test_key",
            processing_time_seconds=1.0
        )

        export_result = ExportResultDTO(
            success=True,
            format=ExportFormat.CSV,
            data=b"csv",
            filename="test.csv",
            size_bytes=3,
            message="Export OK",
            error=""
        )

        session = AnalysisSessionDTO(
            session_id="abc123",
            upload_result=upload_result,
            processing_result=processing_result,
            export_results=[export_result],
            created_at="2025-11-13T10:00:00",
            is_complete=True
        )

        assert session.upload_result is upload_result
        assert session.processing_result is processing_result
        assert len(session.export_results) == 1
        assert session.export_results[0] is export_result
        assert session.is_complete is True


class TestAnalysisOrchestratorIntegration:
    """Integration tests combining multiple orchestrator features."""

    def test_full_workflow_integration(self):
        """Test complete workflow from upload to export."""
        # Setup all dependencies with realistic behavior
        upload_handler = Mock(spec=UploadHandler)
        data_processor = Mock(spec=DataProcessor)
        result_exporter = Mock(spec=ResultExporter)
        cache_service = Mock(spec=CacheService)
        progress_tracker = Mock(spec=ProgressTracker)

        # Create realistic dataset
        sample = Sample(id=SampleId("Sample1"), ko_list=[KO("K00001"), KO("K00002")])
        dataset = Dataset()
        dataset.add_sample(sample)

        # Setup successful upload
        upload_result = UploadResultDTO(
            success=True,
            dataset=dataset,
            filename="samples.fasta",
            sample_count=1,
            ko_count=2,
            message="Upload successful",
            errors=None
        )
        upload_handler.process_upload = Mock(return_value=upload_result)

        # Setup successful processing
        processing_result = MergedDataDTO(
            biorempp_data=pd.DataFrame({
                "KO": ["K00001", "K00002"],
                "Compound": ["C00001", "C00002"]
            }),
            hadeg_data=None,
            toxcsm_data=None,
            match_count=2,
            total_records=2,
            cache_key="test_key",
            processing_time_seconds=2.5
        )
        data_processor.process = Mock(return_value=processing_result)

        # Setup successful exports
        csv_export = ExportResultDTO(
            success=True, format=ExportFormat.CSV, data=b"csv_data",
            filename="results.csv", size_bytes=8, message="OK", error=""
        )
        excel_export = ExportResultDTO(
            success=True, format=ExportFormat.EXCEL, data=b"xlsx_data",
            filename="results.xlsx", size_bytes=9, message="OK", error=""
        )
        result_exporter.export = Mock(side_effect=[csv_export, excel_export])

        orchestrator = AnalysisOrchestrator(
            upload_handler=upload_handler,
            data_processor=data_processor,
            result_exporter=result_exporter,
            cache_service=cache_service,
            progress_tracker=progress_tracker
        )

        # Execute complete workflow
        session = orchestrator.execute_workflow(
            content="base64_encoded_fasta",
            filename="samples.fasta",
            session_id="integration_test_123",
            export_formats=[ExportFormat.CSV, ExportFormat.EXCEL]
        )

        # Verify complete workflow execution
        assert session.session_id == "integration_test_123"
        assert session.is_complete is True
        assert session.upload_result.success is True
        assert session.processing_result.match_count == 2
        assert len(session.export_results) == 2

        # Verify all components were called
        upload_handler.process_upload.assert_called_once()
        data_processor.process.assert_called_once()
        assert result_exporter.export.call_count == 2

        # Verify session is stored and retrievable
        retrieved_session = orchestrator.get_session_state("integration_test_123")
        assert retrieved_session is session

    def test_multiple_sessions_independent(self):
        """Test that multiple sessions are independent."""
        orchestrator = AnalysisOrchestrator(
            upload_handler=Mock(),
            data_processor=Mock(),
            result_exporter=Mock(),
            cache_service=Mock(),
            progress_tracker=Mock()
        )

        # Create two different sessions
        session1 = AnalysisSessionDTO(
            session_id="session1",
            upload_result=None,
            processing_result=None,
            export_results=[],
            created_at=datetime.now().isoformat(),
            is_complete=False
        )

        session2 = AnalysisSessionDTO(
            session_id="session2",
            upload_result=None,
            processing_result=None,
            export_results=[],
            created_at=datetime.now().isoformat(),
            is_complete=True
        )

        orchestrator._sessions["session1"] = session1
        orchestrator._sessions["session2"] = session2

        # Verify both exist independently
        assert orchestrator.get_session_state("session1") is session1
        assert orchestrator.get_session_state("session2") is session2

        # Clear one
        orchestrator.clear_session("session1")

        # Verify only one cleared
        assert orchestrator.get_session_state("session1") is None
        assert orchestrator.get_session_state("session2") is session2
