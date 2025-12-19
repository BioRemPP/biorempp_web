"""
Real Processing Callbacks - BioRemPP v1.0
==========================================

Callbacks for data processing and result generation with robust
error handling and user feedback.

Uses background callbacks for progress tracking with structured
logging and comprehensive error recovery.
"""

import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate

from src.presentation.components.composite.processing_feedback import (
    create_merge_statistics_card,
    create_processing_alert,
    create_processing_error_alert,
    create_validation_summary,
)
from src.presentation.services import DataProcessingService
from src.shared.exceptions import (
    CircuitBreakerOpenError,
    DataProcessingTimeoutError,
    EmptyDataFrameError,
    ProcessingError,
    RetryExhaustedError,
    StageProcessingError,
    ValidationError,
)
from src.shared.logging import get_logger

# Configure logging
logger = get_logger(__name__)

# Initialize data processing service (singleton)
_data_service = None


def get_data_service():
    """Get or create data processing service instance."""
    global _data_service
    if _data_service is None:
        _data_service = DataProcessingService()
        logger.info("DataProcessingService initialized")
    return _data_service


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

    # Background callback for data processing with simple spinner
    @app.callback(
        output=[
            Output("processing-status", "children"),
            Output("merged-result-store", "data"),
            Output("completion-panel", "style"),
            Output("processing-progress", "style"),
        ],
        inputs=Input("process-data-btn", "n_clicks"),
        state=[State("upload-data-store", "data"), State("example-data-store", "data")],
        running=[
            (
                Output("process-data-btn", "disabled"),
                True,  # Disable during processing
                False,  # Enable when complete
            )
        ],
        background=True,
        prevent_initial_call=True,
    )
    def process_data_with_spinner(n_clicks, upload_data, example_data):
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

        Returns
        -------
        tuple
            (status_message, merged_data, completion_panel_style)
        """
        if n_clicks is None:
            raise PreventUpdate

        # Determine data source
        file_data = upload_data or example_data

        if not file_data:
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
            )

        try:
            service = get_data_service()

            logger.info(
                "Starting data processing",
                extra={
                    "file_name": file_data.get("filename", "unknown"),
                    "sample_count": file_data.get("sample_count"),
                    "ko_count": file_data.get("ko_count"),
                },
            )

            # Process data (all merges happen here)
            result = service.process_upload(
                content=file_data["content"], filename=file_data["filename"]
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

            # Success message with metadata
            metadata = result["metadata"]
            status_message = create_processing_alert(
                "success",
                "Processing completed successfully!",
                details={
                    "Samples": metadata["sample_count"],
                    "KO IDs": metadata["ko_count"],
                    "Matched KOs": f"{metadata['matched_kos']}/{metadata['total_kos']}",
                    "Processing Time": f"{metadata['processing_time']:.2f}s",
                },
            )

            # Return results
            return (
                status_message,
                serialized_result,
                {"display": "block"},  # Show completion panel
                {"display": "none"},  # Hide progress panel
            )

        # Validation errors (expected)
        except ValidationError as e:
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
            )

        # Timeout errors
        except DataProcessingTimeoutError as e:
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
            )

        # Empty DataFrame errors
        except EmptyDataFrameError as e:
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
            )

        # Circuit breaker errors
        except CircuitBreakerOpenError as e:
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
            )

        # Retry exhausted errors
        except RetryExhaustedError as e:
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
            )

        # Stage processing errors
        except StageProcessingError as e:
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
            )

        # Generic processing errors
        except ProcessingError as e:
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
            )

        # Unexpected errors
        except Exception as e:
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
            )

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

    logger.info("[OK] Real processing callbacks registered successfully")
    logger.info(
        "  - process_data_with_spinner: Background callback with simple spinner"
    )
    logger.info("  - show_progress_on_click: Show panel immediately on click")
    logger.info("  - enable_process_button: Button enable/disable")
