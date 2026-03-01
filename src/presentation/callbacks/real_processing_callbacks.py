"""
Real Processing Callbacks - BioRemPP v1.0
==========================================

Callbacks for data processing and result generation with robust
error handling and user feedback.

Uses background callbacks for progress tracking with structured
logging and comprehensive error recovery.
"""

import os
import time
import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate
from threading import Thread
from uuid import uuid4

from src.presentation.components.composite.processing_feedback import (
    create_merge_statistics_card,
    create_processing_alert,
    create_processing_error_alert,
    create_validation_summary,
)
from src.presentation.routing import app_path
from src.presentation.services import DataProcessingService, job_resume_service
from src.shared.exceptions import (
    CircuitBreakerOpenError,
    DataProcessingTimeoutError,
    EmptyDataFrameError,
    ProcessingError,
    RetryExhaustedError,
    StageProcessingError,
    ValidationError,
)
from src.shared.logging import build_log_ref, get_logger
from src.shared.metrics import (
    PROCESSING_DURATION_SECONDS,
    RESUME_PERSIST_DURATION_SECONDS,
    instrument_callback,
)

# Configure logging
logger = get_logger(__name__)

# Initialize data processing service (singleton)
_data_service = None
_RESUME_SAVE_TIMEOUT_SECONDS = max(
    float(os.getenv("BIOREMPP_RESUME_SAVE_TIMEOUT_SECONDS", "2.5")),
    0.1,
)


def _job_ref(job_id: str) -> str:
    """Return deterministic, redacted job reference for logs."""
    return build_log_ref(job_id, namespace="job")


def get_data_service():
    """Get or create data processing service instance."""
    global _data_service
    if _data_service is None:
        _data_service = DataProcessingService()
        logger.info("DataProcessingService initialized")
    return _data_service


def _persist_resume_payload_with_timeout(
    job_id: str,
    payload: dict,
    owner_token: str,
    ttl_seconds: int,
    timeout_seconds: float = _RESUME_SAVE_TIMEOUT_SECONDS,
) -> bool:
    """
    Persist resume payload with bounded wait time.

    Returns
    -------
    bool
        True on successful persistence, False on timeout or errors.
    """
    outcome = {"saved": False, "error": None}
    persist_started = time.perf_counter()

    def _worker() -> None:
        try:
            outcome["saved"] = job_resume_service.save_job_payload(
                job_id=job_id,
                payload=payload,
                owner_token=owner_token,
                ttl_seconds=ttl_seconds,
            )
        except Exception as exc:  # pragma: no cover - defensive fallback
            outcome["error"] = exc

    worker = Thread(
        target=_worker,
        name="resume-persistence",
        daemon=True,
    )
    worker.start()
    worker.join(timeout_seconds)

    if worker.is_alive():
        RESUME_PERSIST_DURATION_SECONDS.labels(outcome="timed_out").observe(
            max(time.perf_counter() - persist_started, 0.0)
        )
        logger.warning(
            "Resume payload persistence timed out",
            extra={
                "job_ref": _job_ref(job_id),
                "timeout_seconds": timeout_seconds,
            },
        )
        return False

    error = outcome["error"]
    if error is not None:
        RESUME_PERSIST_DURATION_SECONDS.labels(outcome="error").observe(
            max(time.perf_counter() - persist_started, 0.0)
        )
        logger.error(
            "Resume payload persistence failed with unexpected error",
            extra={"job_ref": _job_ref(job_id)},
            exc_info=(type(error), error, error.__traceback__),
        )
        return False

    saved = bool(outcome["saved"])
    RESUME_PERSIST_DURATION_SECONDS.labels(
        outcome="saved" if saved else "failed"
    ).observe(max(time.perf_counter() - persist_started, 0.0))
    return saved


def _observe_processing_duration(started_at: float, outcome: str) -> None:
    """Observe processing callback duration by coarse outcome class."""
    PROCESSING_DURATION_SECONDS.labels(outcome=outcome).observe(
        max(time.perf_counter() - started_at, 0.0)
    )


def create_spinner_message(elapsed_time):
    """
    Create simple spinner with elapsed time.

    Parameters
    ----------
    elapsed_time : float
        Elapsed time in seconds

    Returns
    -------
    html.Div
        Spinner with message
    """
    return html.Div(
        [
            dbc.Spinner(
                color="success",
                size="lg",
                spinner_style={"width": "3rem", "height": "3rem"},
            ),
            html.Div(
                "Processing your data...",
                className="mt-3 fw-bold text-success",
                style={"fontSize": "1.1rem"},
            ),
            html.Div(
                f"Elapsed time: {elapsed_time:.1f}s",
                className="mt-2 text-muted",
                style={"fontSize": "0.9rem"},
            ),
        ],
        className="text-center py-4",
    )


def register_real_processing_callbacks(app):
    """
    Register real processing callbacks with progress tracking.

    Parameters
    ----------
    app : Dash
        Dash application instance
    """
    logger.info("=" * 60)
    logger.info("Registering REAL PROCESSING callbacks with long_callback...")
    logger.info("=" * 60)
    use_background_callbacks = bool(
        app.server.config.get("BIOREMPP_BACKGROUND_CALLBACKS_ENABLED", True)
    )
    execution_mode = "background" if use_background_callbacks else "synchronous"
    logger.info(f"Processing callback execution mode: {execution_mode}")

    # Background callback for data processing with simple spinner
    @app.callback(
        output=[
            Output("processing-status", "children"),
            Output("merged-result-store", "data"),
            Output("completion-panel", "style"),
            Output("processing-progress", "style"),
            Output("resume-browser-token-store", "data", allow_duplicate=True),
        ],
        inputs=Input("process-data-btn", "n_clicks"),
        state=[
            State("upload-data-store", "data"),
            State("example-data-store", "data"),
            State("resume-browser-token-store", "data"),
        ],
        running=[
            (
                Output("process-data-btn", "disabled"),
                True,  # Disable during processing
                False,  # Enable when complete
            )
        ],
        background=use_background_callbacks,
        prevent_initial_call=True,
    )
    @instrument_callback("processing.process_data_with_spinner")
    def process_data_with_spinner(n_clicks, upload_data, example_data, owner_token):
        """
        Process uploaded or example data with real-time progress tracking.

        Parameters
        ----------
        set_progress : callable
            Function to update progress UI
        n_clicks : int
            Process button clicks
        upload_data : dict
            Uploaded file data
        example_data : dict
            Example file data
        owner_token : str
            Browser ownership token used for resume-by-job-id binding

        Returns
        -------
        tuple
            (
                status_message,
                merged_data,
                completion_panel_style,
                progress_panel_style,
                owner_token_store_update,
            )
        """
        if n_clicks is None:
            raise PreventUpdate
        callback_started_at = time.perf_counter()

        # Determine data source
        file_data = upload_data or example_data

        if not file_data:
            _observe_processing_duration(callback_started_at, "no_data")
            return (
                dbc.Alert(
                    [
                        html.I(className="fas fa-exclamation-circle me-2"),
                        "No data to process. Please upload a file or "
                        "load example data first.",
                    ],
                    color="warning",
                ),
                no_update,
                no_update,
                {"display": "none"},  # Keep progress hidden
                no_update,
            )

        processing_outcome = "unknown"
        try:
            service = get_data_service()
            job_id = DataProcessingService.generate_job_id()
            effective_owner_token = owner_token or str(uuid4())
            generated_owner_token = not bool(owner_token)

            logger.info(
                "Starting data processing",
                extra={
                    "job_ref": _job_ref(job_id),
                    "file_name": file_data.get("filename", "unknown"),
                    "sample_count": file_data.get("sample_count"),
                    "ko_count": file_data.get("ko_count"),
                },
            )
            if generated_owner_token:
                logger.info(
                    "Resume owner token was missing and has been generated for this run",
                    extra={"job_ref": _job_ref(job_id)},
                )

            # Process data (all merges happen here)
            result = service.process_upload(
                content=file_data["content"],
                filename=file_data["filename"],
                job_id=job_id,
            )

            logger.info(
                "Processing completed successfully",
                extra={
                    "metadata": result.get("metadata", {}),
                    "biorempp_rows": result["biorempp_df"].shape[0],
                    "kegg_rows": result["kegg_df"].shape[0],
                    "hadeg_rows": result["hadeg_df"].shape[0],
                    "toxcsm_rows": result["toxcsm_df"].shape[0],
                },
            )

            # Log DataFrame structures for debugging
            logger.debug(
                "DataFrame structures",
                extra={
                    "biorempp": {
                        "shape": result["biorempp_df"].shape,
                        "columns": result["biorempp_df"].columns.tolist(),
                    },
                    "hadeg": {
                        "shape": result["hadeg_df"].shape,
                        "columns": result["hadeg_df"].columns.tolist(),
                    },
                    "toxcsm": {
                        "shape": result["toxcsm_df"].shape,
                        "columns": result["toxcsm_df"].columns.tolist(),
                    },
                    "kegg": {
                        "shape": result["kegg_df"].shape,
                        "columns": result["kegg_df"].columns.tolist(),
                    },
                },
            )

            # Debug logging for ToxCSM fields before serialization
            logger.info(f"[DEBUG] ToxCSM fields before serialization:")
            logger.info(f"  - toxcsm_raw_df in result: {'toxcsm_raw_df' in result}")
            if "toxcsm_raw_df" in result:
                toxcsm_raw = result["toxcsm_raw_df"]
                logger.info(f"  - toxcsm_raw_df type: {type(toxcsm_raw)}")
                logger.info(
                    f"  - toxcsm_raw_df shape: {toxcsm_raw.shape if hasattr(toxcsm_raw, 'shape') else 'N/A'}"
                )

            # Convert DataFrames to dict for JSON serialization
            serialized_result = {
                "biorempp_df": result["biorempp_df"].to_dict("records"),
                "biorempp_raw_df": result["biorempp_raw_df"].to_dict("records"),
                "hadeg_df": result["hadeg_df"].to_dict("records"),
                "hadeg_raw_df": result["hadeg_raw_df"].to_dict("records"),
                "toxcsm_df": result["toxcsm_df"].to_dict(
                    "records"
                ),  # Processed (5 cols for graphs)
                "toxcsm_raw_df": result["toxcsm_raw_df"].to_dict(
                    "records"
                ),  # Merged (66 cols for table & download)
                "kegg_df": result["kegg_df"].to_dict("records"),
                "kegg_raw_df": result["kegg_raw_df"].to_dict("records"),
                "metadata": result["metadata"],
            }

            logger.info(f"[DEBUG] After serialization:")
            logger.info(
                f"  - toxcsm_raw_df records: {len(serialized_result.get('toxcsm_raw_df', []))}"
            )

            logger.info("DataFrames serialized successfully")

            # Persist serialized payload for resume-by-job-id flow (non-blocking)
            metadata = result["metadata"]
            persisted_job_id = metadata.get("job_id", job_id)
            resume_saved = _persist_resume_payload_with_timeout(
                job_id=persisted_job_id,
                payload=serialized_result,
                owner_token=effective_owner_token,
                ttl_seconds=job_resume_service.get_resume_ttl_seconds(),
            )
            payload_size_bytes = job_resume_service.estimate_payload_size_bytes(
                serialized_result
            )

            logger.info(
                "Resume payload persistence result",
                extra={
                    "job_ref": _job_ref(persisted_job_id),
                    "resume_saved": resume_saved,
                    "payload_size_bytes": payload_size_bytes,
                    "resume_max_payload_mb": job_resume_service.get_resume_max_payload_mb(),
                },
            )

            if not resume_saved:
                logger.warning(
                    "Resume payload unavailable for this run",
                    extra={"job_ref": _job_ref(persisted_job_id)},
                )

            status_message = create_processing_alert(
                "success",
                "Processing completed successfully!",
                details={"Job ID": persisted_job_id},
                notes=[
                    "This identifier lets you resume analysis without reprocessing.",
                    "On the results page, you can copy it for later use.",
                ],
            )

            # Return results
            processing_outcome = "success"
            return (
                status_message,
                serialized_result,
                {"display": "block"},  # Show completion panel
                {"display": "none"},  # Hide progress panel
                effective_owner_token,
            )

        # Validation errors (expected)
        except ValidationError as e:
            processing_outcome = "validation_error"
            logger.warning(
                f"Data validation error: {str(e)}",
                extra={
                    "file_name": file_data.get("filename", "unknown"),
                    "error_type": "ValidationError",
                },
            )

            return (
                create_processing_error_alert(
                    "Data Validation Error",
                    "Unable to process data due to validation issues.",
                    error_type="ValidationError",
                    recovery_suggestions=[
                        "Check file format and structure",
                        "Ensure KO IDs follow the correct pattern (K + 5 digits)",
                        "Verify sample names are valid",
                        "Try the example dataset to confirm app is working",
                    ],
                    technical_details=str(e),
                ),
                no_update,
                no_update,
                {"display": "none"},
                no_update,
            )

        # Timeout errors
        except DataProcessingTimeoutError as e:
            processing_outcome = "timeout"
            logger.error(
                f"Processing timeout: {str(e)}",
                extra={"file_name": file_data.get("filename", "unknown")},
            )

            return (
                create_processing_error_alert(
                    "Processing Timeout",
                    "Processing took too long and was stopped.",
                    error_type="TimeoutError",
                    recovery_suggestions=[
                        "The file may be too large or complex",
                        "Try reducing the number of samples",
                        "Retry the processing",
                        "Contact support if problem persists",
                    ],
                    technical_details=str(e),
                ),
                no_update,
                no_update,
                {"display": "none"},
                no_update,
            )

        # Empty DataFrame errors
        except EmptyDataFrameError as e:
            processing_outcome = "empty_dataframe"
            logger.error(
                f"Empty DataFrame error: {str(e)}",
                extra={"file_name": file_data.get("filename", "unknown")},
            )

            return (
                create_processing_error_alert(
                    "No Data Matched",
                    "No data was found in the database for your input.",
                    error_type="EmptyDataError",
                    recovery_suggestions=[
                        "Check that your KO IDs exist in the database",
                        "Verify the KO ID format is correct",
                        "Try with different samples",
                        "Use the example dataset to verify functionality",
                    ],
                    technical_details=str(e),
                ),
                no_update,
                no_update,
                {"display": "none"},
                no_update,
            )

        # Circuit breaker errors
        except CircuitBreakerOpenError as e:
            processing_outcome = "circuit_breaker"
            logger.error(
                f"Circuit breaker open: {str(e)}",
                extra={"file_name": file_data.get("filename", "unknown")},
            )

            return (
                create_processing_error_alert(
                    "Service Temporarily Unavailable",
                    "A database service is currently unavailable.",
                    error_type="CircuitBreakerError",
                    recovery_suggestions=[
                        "Wait a moment and try again",
                        "The service should recover automatically",
                        "Contact support if problem persists",
                    ],
                    technical_details=str(e),
                ),
                no_update,
                no_update,
                {"display": "none"},
                no_update,
            )

        # Retry exhausted errors
        except RetryExhaustedError as e:
            processing_outcome = "retry_exhausted"
            logger.error(
                f"Retry exhausted: {str(e)}",
                extra={"file_name": file_data.get("filename", "unknown")},
            )

            return (
                create_processing_error_alert(
                    "Processing Failed After Retries",
                    "Processing failed after multiple retry attempts.",
                    error_type="RetryExhaustedError",
                    recovery_suggestions=[
                        "Check your network connection",
                        "Wait a moment and try again",
                        "Try with a smaller dataset",
                        "Contact support if problem persists",
                    ],
                    technical_details=str(e),
                ),
                no_update,
                no_update,
                {"display": "none"},
                no_update,
            )

        # Stage processing errors
        except StageProcessingError as e:
            processing_outcome = "stage_error"
            logger.error(
                f"Stage processing failed: {e.stage_name}",
                extra={
                    "file_name": file_data.get("filename", "unknown"),
                    "stage": e.stage_name,
                    "error": str(e.original_error),
                },
            )

            return (
                create_processing_error_alert(
                    f"Processing Failed: {e.stage_name}",
                    f"An error occurred during {e.stage_name}.",
                    error_type="StageProcessingError",
                    recovery_suggestions=[
                        "This stage may be temporarily unavailable",
                        "Wait a moment and try again",
                        "Try with different data",
                        "Contact support if problem persists",
                    ],
                    technical_details=str(e.original_error),
                ),
                no_update,
                no_update,
                {"display": "none"},
                no_update,
            )

        # Generic processing errors
        except ProcessingError as e:
            processing_outcome = "processing_error"
            logger.error(
                f"Processing error: {str(e)}",
                extra={"file_name": file_data.get("filename", "unknown")},
            )

            return (
                create_processing_error_alert(
                    "Processing Error",
                    "An error occurred while processing your data.",
                    error_type="ProcessingError",
                    recovery_suggestions=[
                        "Please try again",
                        "Try with the example dataset first",
                        "Check that your file follows the correct format",
                        "Contact support if problem persists",
                    ],
                    technical_details=str(e),
                ),
                no_update,
                no_update,
                {"display": "none"},
                no_update,
            )

        # Unexpected errors
        except Exception as e:
            processing_outcome = "unexpected_error"
            logger.exception(
                "Unexpected error during data processing",
                exc_info=True,
                extra={
                    "file_name": file_data.get("filename", "unknown"),
                    "sample_count": file_data.get("sample_count"),
                    "ko_count": file_data.get("ko_count"),
                    "error_type": type(e).__name__,
                },
            )

            return (
                create_processing_error_alert(
                    "Unexpected Error",
                    "An unexpected error occurred while processing.",
                    error_type=type(e).__name__,
                    recovery_suggestions=[
                        "Please try again",
                        "If using custom data, try the example dataset first",
                        "Check that your file follows the correct format",
                        "Contact support if problem persists",
                    ],
                    technical_details=str(e),
                ),
                no_update,
                no_update,
                {"display": "none"},
                no_update,
            )
        finally:
            _observe_processing_duration(callback_started_at, processing_outcome)

    # Callback to show progress panel immediately when button is clicked

    @app.callback(
        Output("processing-progress", "style", allow_duplicate=True),
        Input("process-data-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def show_progress_on_click(n_clicks):
        """
        Show progress panel immediately when process button is clicked.
        This ensures the panel appears BEFORE the background callback starts.

        Parameters
        ----------
        n_clicks : int
            Button click count

        Returns
        -------
        dict
            Style to show progress panel
        """
        if n_clicks:
            return {"display": "block"}
        return {"display": "none"}

    # Regular callback for enabling/disabling process button
    @app.callback(
        Output("process-data-btn", "disabled", allow_duplicate=True),
        [Input("upload-data-store", "data"), Input("example-data-store", "data")],
        prevent_initial_call=True,
    )
    def enable_process_button(upload_data, example_data):
        """
        Enable process button when data is available.

        Parameters
        ----------
        upload_data : dict
            Uploaded file data
        example_data : dict
            Example file data

        Returns
        -------
        bool
            True if button should be disabled
        """
        return not (upload_data or example_data)

    @app.callback(
        Output("url", "pathname", allow_duplicate=True),
        Input("view-results-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def navigate_to_results(n_clicks):
        """
        Navigate to results page when completion button is clicked.

        Parameters
        ----------
        n_clicks : int
            Button click count

        Returns
        -------
        str
            URL pathname for results route
        """
        if not n_clicks:
            raise PreventUpdate
        return app_path("/results")

    logger.info("[OK] Real processing callbacks registered successfully")
    logger.info(
        "  - process_data_with_spinner: Background callback with simple spinner"
    )
    logger.info("  - show_progress_on_click: Show panel immediately on click")
    logger.info("  - enable_process_button: Button enable/disable")
    logger.info("  - navigate_to_results: Redirect to /results from completion panel")
