"""
Upload Callbacks - Backend Integration for Upload Workflow.

Handles file upload, sample data loading, and validation.

Functions
---------
register_upload_callbacks
    Register all upload-related callbacks

Notes
-----
- Integrates with UploadHandler from Application Layer
- Updates upload-result-store with UploadResultDTO
- Shows validation panel with feedback
"""

import base64
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from dash import Input, Output, State, callback, ctx, no_update
from dash.exceptions import PreventUpdate

# Import from Application Layer
# Note: Adjust import paths based on actual project structure
try:
    from application.dto.upload_dto import UploadResultDTO
    from application.services.upload_handler import UploadHandler
except ImportError:
    # Fallback for development/testing
    UploadHandler = None
    UploadResultDTO = None


def register_upload_callbacks(app, upload_handler: Optional[UploadHandler] = None):
    """
    Register upload callbacks.

    Parameters
    ----------
    app : Dash
        Dash application instance
    upload_handler : Optional[UploadHandler], optional
        UploadHandler instance from Application Layer, by default None
        If None, creates new instance

    Notes
    -----
    DESATIVADO - Usando real_upload_callbacks.py

    Este arquivo contém callbacks da Application Layer que foram
    substituídos pelos callbacks reais.
    """
    # DESATIVADO - Callbacks duplicados, usando real_upload_callbacks.py
    return

    # CALLBACK DESATIVADO - Conflita com real_upload_callbacks.py
    # @callback(
    #     [
    #         Output("upload-result-store", "data"),
    #         Output("upload-data-filename", "children")
    #     ],
    #     [
    #         Input("upload-data", "contents"),
    #         Input("load-sample-btn", "n_clicks")
    #     ],
    #     [
    #         State("upload-data", "filename")
    #     ],
    #     prevent_initial_call=True
    # )
    def process_upload_disabled(
        contents: Optional[str], sample_clicks: Optional[int], filename: Optional[str]
    ) -> Tuple[Optional[Dict[str, Any]], str]:
        """
        Process file upload or load sample data.

        Parameters
        ----------
        contents : Optional[str]
            Base64 encoded file contents
        sample_clicks : Optional[int]
            Number of clicks on sample data button
        filename : Optional[str]
            Uploaded filename

        Returns
        -------
        Tuple[Optional[Dict[str, Any]], str]
            - UploadResultDTO as dict
            - Filename display text

        Notes
        -----
        - Triggered by upload or sample button click
        - Decodes base64 content
        - Calls UploadHandler.process_upload()
        - Returns DTO for validation panel
        """
        triggered_id = ctx.triggered_id

        # Handle sample data button
        if triggered_id == "load-sample-btn":
            try:
                # Load sample data file
                sample_path = Path("data/sample_data.txt")
                if not sample_path.exists():
                    sample_path = Path("biorempp_web/data/sample_data.txt")

                with open(sample_path, "r") as f:
                    sample_content = f.read()

                # Process sample data
                result = upload_handler.process_upload(
                    file_content=sample_content, filename="sample_data.txt"
                )

                filename_msg = "[OK] Sample data loaded: sample_data.txt"
                return result.to_dict(), filename_msg

            except Exception as e:
                # Return error result
                error_result = {
                    "success": False,
                    "sample_count": 0,
                    "ko_count": 0,
                    "validation_errors": [f"Failed to load sample data: {str(e)}"],
                    "validation_warnings": [],
                    "filename": "sample_data.txt",
                }
                return error_result, "✗ Error loading sample data"

        # Handle file upload
        if triggered_id == "upload-data" and contents:
            try:
                # Decode base64 content
                content_type, content_string = contents.split(",")
                decoded = base64.b64decode(content_string)
                file_content = decoded.decode("utf-8")

                # Process upload
                result = upload_handler.process_upload(
                    file_content=file_content, filename=filename
                )

                return result.to_dict(), f"[OK] File uploaded: {filename}"

            except Exception as e:
                # Return error result
                error_result = {
                    "success": False,
                    "sample_count": 0,
                    "ko_count": 0,
                    "validation_errors": [f"Failed to process file: {str(e)}"],
                    "validation_warnings": [],
                    "filename": filename or "unknown",
                }
                return error_result, "✗ Error processing file"

        raise PreventUpdate

    # CALLBACK DESATIVADO - Conflita com real_upload_callbacks.py
    # @callback(
    #     [
    #         Output("validation-panel", "style"),
    #         Output("validation-panel", "children")
    #     ],
    #     [Input("upload-result-store", "data")],
    #     prevent_initial_call=True
    # )
    def show_validation_disabled(
        upload_result: Optional[Dict[str, Any]]
    ) -> Tuple[Dict, Any]:
        """
        Show validation panel with results.

        Parameters
        ----------
        upload_result : Optional[Dict[str, Any]]
            UploadResultDTO data from store

        Returns
        -------
        Tuple[Dict, Any]
            - Style dict (display: block/none)
            - Validation panel component

        Notes
        -----
        - Creates validation_panel with upload results
        - Makes panel visible
        - Shows success/error alerts and statistics
        """
        if not upload_result:
            return {"display": "none"}, no_update

        # Import here to avoid circular dependency
        from ..components.composite import create_validation_panel

        panel = create_validation_panel(validation_data=upload_result)

        return {"display": "block"}, panel.children
