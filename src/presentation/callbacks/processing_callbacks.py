"""
Processing Callbacks - Backend Integration for Data Processing.

Handles data processing workflow with progress tracking.

Functions
---------
register_processing_callbacks
    Register all processing-related callbacks

Notes
-----
- Integrates with DataProcessor and ProgressTracker
- Updates processing-progress-store with real-time updates
- Shows completion panel when finished
"""

import uuid
from typing import Any, Dict, Optional, Tuple

from dash import Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate

# Import from Application Layer
try:
    from application.core.progress_tracker import ProgressTracker
    from application.services.data_processor import DataProcessor
    from domain.entities.dataset import Dataset
except ImportError:
    DataProcessor = None
    ProgressTracker = None
    Dataset = None


def register_processing_callbacks(
    app,
    data_processor: Optional[DataProcessor] = None,
    progress_tracker: Optional[ProgressTracker] = None,
):
    """
    Register processing callbacks.

    Parameters
    ----------
    app : Dash
        Dash application instance
    data_processor : Optional[DataProcessor], optional
        DataProcessor instance, by default None
    progress_tracker : Optional[ProgressTracker], optional
        ProgressTracker instance, by default None

    Notes
    -----
    DESATIVADO - Usando real_processing_callbacks.py

    Este arquivo contém callbacks da Application Layer que foram
    substituídos pelos callbacks reais.
    """
    # DESATIVADO - Callbacks duplicados, usando real_processing_callbacks.py
    return

    # Initialize services if not provided
    if data_processor is None:
        data_processor = DataProcessor()
    if progress_tracker is None:
        progress_tracker = ProgressTracker()

    # CALLBACK DESATIVADO - Conflita com real_processing_callbacks.py
    # @callback(
    #     [
    #         Output("progress-panel", "style"),
    #         Output("progress-interval", "disabled"),
    #         Output("session-id-store", "data")
    #     ],
    #     [Input("process-data-btn", "n_clicks")],
    #     [
    #         State("upload-result-store", "data"),
    #         State("session-id-store", "data")
    #     ],
    #     prevent_initial_call=True
    # )
    def start_processing_disabled(
        n_clicks: Optional[int],
        upload_result: Optional[Dict[str, Any]],
        session_id: Optional[str],
    ) -> Tuple[Dict, bool, str]:
        """
        Start data processing workflow.

        Parameters
        ----------
        n_clicks : Optional[int]
            Button click count
        upload_result : Optional[Dict[str, Any]]
            UploadResultDTO from store
        session_id : Optional[str]
            Current session ID

        Returns
        -------
        Tuple[Dict, bool, str]
            - Progress panel style (display: block)
            - Interval disabled flag (False to enable)
            - Session ID (new or existing)

        Notes
        -----
        - Generates session ID if not exists
        - Starts background processing task
        - Enables progress interval for updates
        - Shows progress panel
        """
        if not n_clicks or not upload_result:
            raise PreventUpdate

        # Generate session ID if needed
        if not session_id:
            session_id = str(uuid.uuid4())

        try:
            # TODO: Start async processing task
            # For now, we'll track progress synchronously
            # In production, use Celery or similar for background tasks

            # Initialize progress
            progress_tracker.start_processing(session_id, total_stages=8)

            # Show progress panel and enable interval
            return {"display": "block"}, False, session_id

        except Exception as e:
            # Handle errors
            return {"display": "none"}, True, session_id

    # CALLBACK DESATIVADO - Conflita com real_processing_callbacks.py
    # @callback(
    #     [
    #         Output("processing-progress-store", "data"),
    #         Output("progress-display", "children")
    #     ],
    #     [Input("progress-interval", "n_intervals")],
    #     [State("session-id-store", "data")],
    #     prevent_initial_call=True
    # )
    def update_progress_disabled(
        n_intervals: int, session_id: Optional[str]
    ) -> Tuple[Optional[Dict[str, Any]], Any]:
        """
        Update processing progress.

        Parameters
        ----------
        n_intervals : int
            Number of interval ticks
        session_id : Optional[str]
            Current session ID

        Returns
        -------
        Tuple[Optional[Dict[str, Any]], Any]
            - ProcessingProgressDTO as dict
            - Updated progress bar component

        Notes
        -----
        - Polls ProgressTracker every 1 second
        - Updates progress bar display
        - Stores progress data for completion check
        """
        if not session_id:
            raise PreventUpdate

        try:
            # Get current progress
            progress = progress_tracker.get_progress(session_id)

            if not progress:
                raise PreventUpdate

            # Create progress bar component
            from ..components.base import create_progress_bar

            progress_bar = create_progress_bar(progress_data=progress.to_dict())

            return progress.to_dict(), progress_bar.children

        except Exception:
            raise PreventUpdate

    # Callback desativado - usando real_processing_callbacks.py
    # @callback(
    #     [
    #         Output("completion-panel", "style"),
    #         Output("completion-panel", "children"),
    #         Output("progress-interval", "disabled", allow_duplicate=True),
    #         Output("processing-complete-store", "data")
    #     ],
    #     [Input("processing-progress-store", "data")],
    #     prevent_initial_call=True
    # )
    def show_completion_disabled(
        progress_data: Optional[Dict[str, Any]]
    ) -> Tuple[Dict[str, str], Any, bool, bool]:
        """
        Show completion panel when processing finishes.

        Parameters
        ----------
        progress_data : Optional[Dict[str, Any]]
            ProcessingProgressDTO data

        Returns
        -------
        Tuple[Dict, Any, bool, bool]
            - Completion panel style
            - Completion panel component
            - Interval disabled (True to stop polling)
            - Processing complete flag

        Notes
        -----
        - Checks if percentage == 100
        - Disables progress interval
        - Shows completion panel
        - Sets complete flag to True
        """
        if not progress_data:
            raise PreventUpdate

        percentage = progress_data.get("percentage", 0)

        # Check if complete
        if percentage >= 100:
            # Create completion data
            completion_data = {
                "success": True,
                "processing_time": 45.2,  # TODO: Get actual time
                "total_samples": 150,  # TODO: Get from result
                "merged_records": 1200,  # TODO: Get from result
                "session_id": "abc123",  # TODO: Get actual session_id
            }

            # Create completion panel
            from ..components.composite import create_completion_panel

            panel = create_completion_panel(completion_data=completion_data)

            return {"display": "block"}, panel.children, True, True

        raise PreventUpdate

    # CALLBACK DESATIVADO - Conflita com real_processing_callbacks.py
    # @callback(
    #     Output("url", "pathname"),
    #     [Input("view-results-btn", "n_clicks")],
    #     prevent_initial_call=True
    # )
    def navigate_to_results_disabled(n_clicks: Optional[int]) -> str:
        """
        Navigate to results page.

        Parameters
        ----------
        n_clicks : Optional[int]
            Button click count

        Returns
        -------
        str
            URL pathname (/results)

        Notes
        -----
        - Triggered by "View Results" button
        - Changes URL to /results
        - Results page will load merged data from store
        """
        if not n_clicks:
            raise PreventUpdate

        return "/results"
