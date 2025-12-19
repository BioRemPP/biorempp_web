"""
Application Layer - Analysis Orchestrator.

This module orchestrates the complete workflow from upload to export,
coordinating between multiple application services and core operations.

Classes
-------
AnalysisOrchestrator
    High-level coordinator for the complete analysis workflow.

Notes
-----
- Follows Clean Architecture (depends on abstractions)
- Coordinates but doesn't duplicate logic
- Uses Dependency Injection for testability
- Maintains workflow state through DTOs
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Protocol

import pandas as pd

from src.application.core.data_processor import DataProcessor
from src.application.core.result_exporter import (
    ExportFormat,
    ExportResultDTO,
    ResultExporter,
)
from src.application.core.upload_handler import UploadHandler
from src.application.dto.merged_data_dto import MergedDataDTO
from src.application.dto.processing_progress_dto import ProcessingProgressDTO
from src.application.dto.upload_result_dto import UploadResultDTO
from src.application.services.cache_service import CacheService
from src.application.services.progress_tracker import ProgressTracker


@dataclass(frozen=True)
class AnalysisSessionDTO:
    """
    Data Transfer Object for analysis session state.

    Attributes
    ----------
    session_id : str
        Unique identifier for the session
    upload_result : Optional[UploadResultDTO]
        Result of file upload
    processing_result : Optional[MergedDataDTO]
        Result of data processing
    export_results : List[ExportResultDTO]
        List of export operations performed
    created_at : str
        ISO format timestamp of session creation
    is_complete : bool
        Whether analysis is complete
    """

    session_id: str
    upload_result: Optional[UploadResultDTO]
    processing_result: Optional[MergedDataDTO]
    export_results: List[ExportResultDTO]
    created_at: str
    is_complete: bool


class AnalysisOrchestrator:
    """
    Orchestrate the complete analysis workflow.

    Coordinates the entire analysis pipeline from file upload through
    processing to export. Uses composition and dependency injection to
    maintain clean architecture principles.

    Parameters
    ----------
    upload_handler : UploadHandler
        Handler for file uploads
    data_processor : DataProcessor
        Processor for data merging and analysis
    result_exporter : ResultExporter
        Exporter for results
    cache_service : CacheService
        Service for caching data
    progress_tracker : ProgressTracker
        Tracker for progress updates

    Methods
    -------
    execute_workflow(content, filename, session_id, export_formats)
        Execute complete workflow from upload to export
    process_upload(content, filename)
        Process file upload step
    process_data(dataset, session_id)
        Process data merging step
    export_results(data, session_id, formats)
        Export results in multiple formats
    get_session_state(session_id)
        Retrieve current session state

    Notes
    -----
    - Uses dependency injection for all operations
    - Maintains session state via DTOs
    - Handles errors gracefully with detailed messages
    - Updates progress at each workflow step
    - Caches intermediate results
    """

    def __init__(
        self,
        upload_handler: UploadHandler,
        data_processor: DataProcessor,
        result_exporter: ResultExporter,
        cache_service: CacheService,
        progress_tracker: ProgressTracker,
    ):
        """
        Initialize the AnalysisOrchestrator with dependencies.

        Parameters
        ----------
        upload_handler : UploadHandler
            Handler for file uploads
        data_processor : DataProcessor
            Processor for data merging
        result_exporter : ResultExporter
            Exporter for results
        cache_service : CacheService
            Service for caching
        progress_tracker : ProgressTracker
            Tracker for progress

        Notes
        -----
        All dependencies are injected for testability.
        """
        self._upload_handler = upload_handler
        self._data_processor = data_processor
        self._result_exporter = result_exporter
        self._cache_service = cache_service
        self._progress_tracker = progress_tracker
        self._sessions: dict[str, AnalysisSessionDTO] = {}

    def execute_workflow(
        self,
        content: str,
        filename: str,
        session_id: str,
        export_formats: Optional[List[ExportFormat]] = None,
    ) -> AnalysisSessionDTO:
        """
        Execute the complete analysis workflow.

        Coordinates the entire pipeline:
        1. Upload and validate file
        2. Process and merge data
        3. Export results in requested formats
        4. Update session state

        Parameters
        ----------
        content : str
            Base64-encoded file content
        filename : str
            Original filename
        session_id : str
            Unique session identifier
        export_formats : Optional[List[ExportFormat]], default=None
            Formats to export (CSV, Excel, JSON), defaults to [CSV]

        Returns
        -------
        AnalysisSessionDTO
            Complete session state with results

        Notes
        -----
        - Creates new session if doesn't exist
        - Updates progress at each step
        - Handles errors without stopping entire workflow
        - Caches results for performance
        """
        if export_formats is None:
            export_formats = [ExportFormat.CSV]

        # Initialize session
        created_at = datetime.now().isoformat()

        # Step 1: Process upload
        self._progress_tracker.update_progress(
            session_id=session_id,
            current_stage="upload",
            stage_number=1,
            total_stages=8,
            message="Processing file upload...",
        )

        upload_result = self._upload_handler.process_upload(content, filename)

        if not upload_result.success:
            # Upload failed - return early
            session = AnalysisSessionDTO(
                session_id=session_id,
                upload_result=upload_result,
                processing_result=None,
                export_results=[],
                created_at=created_at,
                is_complete=False,
            )
            self._sessions[session_id] = session
            return session

        # Step 2: Process data
        self._progress_tracker.update_progress(
            session_id=session_id,
            current_stage="processing",
            stage_number=2,
            total_stages=8,
            message="Processing and merging data...",
        )

        processing_result = self._data_processor.process(
            dataset=upload_result.dataset, session_id=session_id
        )

        # Step 3: Export results
        self._progress_tracker.update_progress(
            session_id=session_id,
            current_stage="exporting",
            stage_number=7,
            total_stages=8,
            message="Exporting results...",
        )

        export_results = []
        for fmt in export_formats:
            export_result = self._export_result_by_format(
                processing_result=processing_result, format=fmt, session_id=session_id
            )
            export_results.append(export_result)

        # Step 4: Finalize
        self._progress_tracker.update_progress(
            session_id=session_id,
            current_stage="complete",
            stage_number=8,
            total_stages=8,
            message="Analysis complete!",
        )

        session = AnalysisSessionDTO(
            session_id=session_id,
            upload_result=upload_result,
            processing_result=processing_result,
            export_results=export_results,
            created_at=created_at,
            is_complete=True,
        )

        self._sessions[session_id] = session
        return session

    def _export_result_by_format(
        self, processing_result: MergedDataDTO, format: ExportFormat, session_id: str
    ) -> ExportResultDTO:
        """
        Export processing result in specified format.

        Parameters
        ----------
        processing_result : MergedDataDTO
            The data to export
        format : ExportFormat
            Export format
        session_id : str
            Session identifier for filename

        Returns
        -------
        ExportResultDTO
            Export operation result
        """
        # Generate filename based on format
        if format == ExportFormat.CSV:
            filename = f"biorempp_results_{session_id}.csv"
            data = processing_result.biorempp_data
        elif format == ExportFormat.EXCEL:
            filename = f"biorempp_results_{session_id}.xlsx"
            data = processing_result.biorempp_data
        elif format == ExportFormat.JSON:
            filename = f"biorempp_results_{session_id}.json"
            data = processing_result.biorempp_data
        else:
            # Unsupported format
            return ExportResultDTO(
                success=False,
                format=format,
                data=None,
                filename="",
                size_bytes=0,
                message="Export failed",
                error=f"Unsupported format: {format}",
            )

        return self._result_exporter.export(data, format, filename)

    def process_upload(self, content: str, filename: str) -> UploadResultDTO:
        """
        Process file upload independently.

        Parameters
        ----------
        content : str
            Base64-encoded file content
        filename : str
            Original filename

        Returns
        -------
        UploadResultDTO
            Upload processing result

        Notes
        -----
        Can be used for upload-only operations without full workflow execution.
        """
        return self._upload_handler.process_upload(content, filename)

    def process_data(self, dataset, session_id: str) -> MergedDataDTO:
        """
        Process data merging independently.

        Parameters
        ----------
        dataset : Dataset
            Domain entity with samples
        session_id : str
            Session identifier

        Returns
        -------
        MergedDataDTO
            Processing result

        Notes
        -----
        Can be used when upload is already complete and only processing is
        needed.
        """
        return self._data_processor.process(dataset, session_id)

    def export_results(
        self,
        data: pd.DataFrame,
        session_id: str,
        formats: Optional[List[ExportFormat]] = None,
    ) -> List[ExportResultDTO]:
        """
        Export results in multiple formats.

        Parameters
        ----------
        data : pd.DataFrame
            Data to export
        session_id : str
            Session identifier for filenames
        formats : Optional[List[ExportFormat]], default=None
            Export formats, defaults to [CSV]

        Returns
        -------
        List[ExportResultDTO]
            List of export results

        Notes
        -----
        Can be used for exporting existing data without running the full
        workflow.
        """
        if formats is None:
            formats = [ExportFormat.CSV]

        results = []
        for fmt in formats:
            filename = f"biorempp_results_{session_id}"
            result = self._result_exporter.export(data, fmt, filename)
            results.append(result)

        return results

    def get_session_state(self, session_id: str) -> Optional[AnalysisSessionDTO]:
        """
        Retrieve current session state.

        Parameters
        ----------
        session_id : str
            Session identifier

        Returns
        -------
        Optional[AnalysisSessionDTO]
            Session state or None if not found

        Notes
        -----
        Returns None if session doesn't exist.
        """
        return self._sessions.get(session_id)

    def get_progress(self, session_id: str) -> Optional[ProcessingProgressDTO]:
        """
        Get current progress for a session.

        Parameters
        ----------
        session_id : str
            Session identifier

        Returns
        -------
        Optional[ProcessingProgressDTO]
            Current progress or None
        """
        return self._progress_tracker.get_progress(session_id)

    def clear_session(self, session_id: str) -> None:
        """
        Clear session data and cache.

        Parameters
        ----------
        session_id : str
            Session identifier to clear

        Notes
        -----
        Removes session from memory and clears cache.
        """
        if session_id in self._sessions:
            del self._sessions[session_id]

        # Clear cache for this session
        self._cache_service.clear()
