"""
Real Upload Callbacks - BioRemPP v1.0
======================================

Callbacks for handling file uploads and validation.
"""

import base64
from pathlib import Path

from dash import Input, Output, State, callback, no_update
from dash.exceptions import PreventUpdate

from config.settings import get_settings
from src.domain.services.sanitization_service import SanitizationService
from src.domain.services.validation_service import ValidationService
from src.presentation.components.composite.upload_feedback import (
    create_error_alert,
    create_file_info_card,
)
from src.shared.logging import get_logger

# Get application settings
settings = get_settings()

# Configure logging
logger = get_logger(__name__)


def register_real_upload_callbacks(app):
    """
    Register real upload callbacks.

    Parameters
    ----------
    app : Dash
        Dash application instance
    """
    logger.info("=" * 60)
    logger.info("Registering REAL UPLOAD callbacks...")
    logger.info("=" * 60)

    @callback(
        [
            Output("upload-status", "children"),
            Output("upload-data-store", "data"),
            Output("file-info-display", "children"),
        ],
        Input("upload-component", "contents"),
        State("upload-component", "filename"),
        prevent_initial_call=True,
    )
    def handle_upload(contents, filename):
        """
        Handle file upload with comprehensive validation.

        Performs server-side validation including:
        - File size limits
        - Encoding validation (UTF-8/latin-1)
        - Filename sanitization
        - Content format validation
        - Sample and KO count limits
        - Sample name sanitization

        Parameters
        ----------
        contents : str
            Base64 encoded file contents
        filename : str
            Original filename

        Returns
        -------
        tuple
            (status_alert, file_data, file_info_card)
        """
        if contents is None:
            raise PreventUpdate

        try:
            # ============================================================
            # STEP 1: Decode Base64
            # ============================================================
            try:
                _, content_string = contents.split(",")
                decoded = base64.b64decode(content_string)
            except (ValueError, Exception) as e:
                logger.error(f"Base64 decode failed: {e}")
                return (
                    create_error_alert(
                        "Invalid File Format",
                        "Unable to read file. Please upload a valid text file.",
                        suggestions=[
                            "Ensure file is in text format (.txt)",
                            "Check file is not corrupted",
                        ],
                    ),
                    no_update,
                    None,  # Clear file info display on error
                )

            # ============================================================
            # STEP 2: Validate File Size (SERVER-SIDE)
            # ============================================================
            is_valid, error_msg = ValidationService.validate_file_size(
                size_bytes=len(decoded), max_bytes=settings.UPLOAD_MAX_SIZE_BYTES
            )

            if not is_valid:
                logger.warning(f"File size validation failed: {error_msg}")
                return (
                    create_error_alert(
                        "File Size Exceeded",
                        error_msg,
                        suggestions=[
                            f"Reduce file size to under {settings.UPLOAD_MAX_SIZE_MB} MB",
                            "Remove unnecessary samples or KO entries",
                            "Split into multiple smaller files",
                        ],
                    ),
                    no_update,
                    None,  # Clear file info display on error
                )

            # ============================================================
            # STEP 3: Validate and Decode Encoding
            # ============================================================
            is_valid, file_content, error_msg = ValidationService.validate_encoding(
                decoded
            )

            if not is_valid:
                logger.error(f"Encoding validation failed: {error_msg}")
                return (
                    create_error_alert(
                        "Encoding Error",
                        error_msg,
                        suggestions=[
                            "Save file with UTF-8 encoding",
                            "Use a text editor that supports UTF-8",
                            "Check for special characters",
                        ],
                    ),
                    no_update,
                    None,  # Clear file info display on error
                )

            # ============================================================
            # STEP 4: Sanitize Filename
            # ============================================================
            safe_filename = SanitizationService.sanitize_filename(filename)

            # ============================================================
            # STEP 5: Comprehensive Content Validation
            # ============================================================
            is_valid, error_msg = ValidationService.validate_raw_input(file_content)

            if not is_valid:
                logger.warning(f"Content validation failed: {error_msg}")
                return (
                    create_error_alert(
                        "Invalid File Format",
                        error_msg,
                        suggestions=[
                            "Check file format: lines starting with '>' for samples",
                            "Ensure KO IDs follow format: K + 5 digits (e.g., K00001)",
                            "See example file for reference",
                        ],
                    ),
                    no_update,
                    None,  # Clear file info display on error
                )

            # ============================================================
            # STEP 6: Count Samples and KOs for Limit Validation
            # ============================================================
            lines = file_content.strip().split("\n")
            sample_count = sum(1 for line in lines if line.startswith(">"))
            ko_count = sum(1 for line in lines if line.strip().startswith("K"))

            # ============================================================
            # STEP 7: Validate Sample Count Limit
            # ============================================================
            is_valid, error_msg = ValidationService.validate_sample_count(
                sample_count=sample_count, max_samples=settings.UPLOAD_SAMPLE_LIMIT
            )

            if not is_valid:
                logger.warning(f"Sample count limit exceeded: {error_msg}")
                return (
                    create_error_alert(
                        "Sample Limit Exceeded",
                        error_msg,
                        suggestions=[
                            f"Reduce to {settings.UPLOAD_SAMPLE_LIMIT} samples or fewer",
                            "Split dataset into multiple files",
                            "Remove duplicate or unnecessary samples",
                        ],
                    ),
                    no_update,
                    None,  # Clear file info display on error
                )

            # ============================================================
            # STEP 8: Validate KO Count Limit
            # ============================================================
            is_valid, error_msg = ValidationService.validate_ko_count(
                ko_count=ko_count, max_kos=settings.UPLOAD_KO_LIMIT
            )

            if not is_valid:
                logger.warning(f"KO count limit exceeded: {error_msg}")
                return (
                    create_error_alert(
                        "KO Entry Limit Exceeded",
                        error_msg,
                        suggestions=[
                            f"Reduce to {settings.UPLOAD_KO_LIMIT:,} KO entries or fewer",
                            "Remove duplicate KO entries",
                            "Split into multiple files",
                        ],
                    ),
                    no_update,
                    None,  # Clear file info display on error
                )

            # ============================================================
            # STEP 9: Sanitize Sample Names
            # ============================================================
            warnings = []
            for idx, line in enumerate(lines, 1):
                if line.startswith(">"):
                    sample_name = line[1:].strip()
                    is_valid, sanitized, error = (
                        SanitizationService.sanitize_sample_name(sample_name)
                    )
                    if not is_valid:
                        logger.warning(
                            f"Invalid sample name on line {idx}: {sample_name}"
                        )
                        return (
                            create_error_alert(
                                "Invalid Sample Name",
                                f"Line {idx}: {error}",
                                suggestions=[
                                    "Use only letters, numbers, underscore (_), dash (-), and dot (.)",
                                    "Example: Sample_001, Sample-2024.v1",
                                ],
                            ),
                            no_update,
                            None,  # Clear file info display on error
                        )

                    # Log if sanitization changed the name
                    if sanitized != sample_name:
                        warnings.append(
                            f"Line {idx}: Sample name '{sample_name}' sanitized"
                        )

            # ============================================================
            # STEP 10: All Validations Passed - Store Data
            # ============================================================
            file_data = {
                "content": file_content,
                "filename": safe_filename,
                "original_filename": filename,
                "sample_count": sample_count,
                "ko_count": ko_count,
                "file_size_bytes": len(decoded),
            }

            logger.info(
                f"File upload successful: {safe_filename}",
                extra={
                    "uploaded_file": safe_filename,
                    "samples": sample_count,
                    "kos": ko_count,
                    "size_bytes": len(decoded),
                    "warnings": len(warnings),
                },
            )

            # ============================================================
            # STEP 11: Create File Info Display (includes success state)
            # ============================================================
            file_info = create_file_info_card(
                filename=safe_filename,
                sample_count=sample_count,
                ko_count=ko_count,
                file_size_bytes=len(decoded),
                max_samples=settings.UPLOAD_SAMPLE_LIMIT,
                max_kos=settings.UPLOAD_KO_LIMIT,
                max_size_mb=settings.UPLOAD_MAX_SIZE_MB,
                warnings=warnings if warnings else None,
            )

            # Return: no status message (deprecated), only file info card
            return no_update, file_data, file_info

        except Exception as e:
            # Generic error - log full traceback, show generic message
            logger.exception(f"Unexpected error during upload: {e}", exc_info=True)
            return (
                create_error_alert(
                    "Unexpected Error",
                    "An unexpected error occurred during upload.",
                    suggestions=[
                        "Please try again",
                        "Check file format and contents",
                        "Contact support if problem persists",
                    ],
                ),
                no_update,
                None,  # Clear file info display on error
            )

    @callback(
        [
            Output("example-data-store", "data"),
            Output("upload-status", "children", allow_duplicate=True),
            Output("file-info-display", "children", allow_duplicate=True),
        ],
        Input("load-example-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def load_example_data(n_clicks):
        """
        Load example dataset from file.

        Loads the pre-configured example dataset and displays file information
        with statistics about samples and KO entries.

        Parameters
        ----------
        n_clicks : int
            Number of clicks on example button

        Returns
        -------
        tuple
            (example_data, status_message, file_info)

        Notes
        -----
        Uses feedback components for consistent UI styling.
        Logs all loading events with structured context.
        """
        if n_clicks is None:
            raise PreventUpdate

        try:
            # ============================================================
            # STEP 1: Locate Example File
            # ============================================================
            example_file = (
                Path(__file__).parent.parent.parent / "data" / "exemple_dataset.txt"
            )

            if not example_file.exists():
                logger.error(
                    f"Example dataset file not found: {example_file}",
                    extra={"expected_path": str(example_file)},
                )
                return (
                    no_update,
                    create_error_alert(
                        "Example File Not Found",
                        "The example dataset file is missing from the application.",
                        suggestions=[
                            "Contact support to restore example file",
                            "Upload your own dataset instead",
                        ],
                    ),
                    None,  # Clear file info display on error
                )

            # ============================================================
            # STEP 2: Load and Parse File
            # ============================================================
            try:
                with open(example_file, "r", encoding="utf-8") as f:
                    file_content = f.read()
            except UnicodeDecodeError:
                logger.error(
                    "Example dataset encoding error",
                    extra={"file_path": str(example_file)},
                )
                return (
                    no_update,
                    create_error_alert(
                        "Encoding Error",
                        "Unable to read example dataset due to encoding issues.",
                        suggestions=["Contact support to fix example file encoding"],
                    ),
                    None,  # Clear file info display on error
                )

            # ============================================================
            # STEP 3: Count Samples and KOs
            # ============================================================
            lines = file_content.strip().split("\n")
            sample_count = sum(1 for line in lines if line.startswith(">"))
            ko_count = sum(1 for line in lines if line.strip().startswith("K"))

            # ============================================================
            # STEP 4: Create Data Object
            # ============================================================
            example_data = {
                "content": file_content,
                "filename": "exemple_dataset.txt",
                "sample_count": sample_count,
                "ko_count": ko_count,
                "file_size_bytes": len(file_content.encode("utf-8")),
            }

            logger.info(
                "Example dataset loaded successfully",
                extra={
                    "example_file": "exemple_dataset.txt",
                    "samples": sample_count,
                    "kos": ko_count,
                    "size_bytes": example_data["file_size_bytes"],
                },
            )

            # ============================================================
            # STEP 5: Create File Info Display (includes success message)
            # ============================================================
            file_info = create_file_info_card(
                filename="exemple_dataset.txt",
                sample_count=sample_count,
                ko_count=ko_count,
                file_size_bytes=example_data["file_size_bytes"],
                max_samples=settings.UPLOAD_SAMPLE_LIMIT,
                max_kos=settings.UPLOAD_KO_LIMIT,
                max_size_mb=settings.UPLOAD_MAX_SIZE_MB,
                warnings=None,
            )

            # Return: no status message (deprecated), only file info card
            return example_data, no_update, file_info

        except Exception as e:
            # Generic error - log full details, show generic message
            logger.exception("Unexpected error loading example dataset", exc_info=True)
            return (
                no_update,
                create_error_alert(
                    "Unexpected Error",
                    "An unexpected error occurred while loading the example dataset.",
                    suggestions=[
                        "Try again",
                        "Upload your own dataset instead",
                        "Contact support if problem persists: biorempp@gmail.com",
                    ],
                ),
                None,  # Clear file info display on error
            )

    logger.info("[OK] Real upload callbacks registered successfully")
    logger.info("  - handle_file_upload: File upload handler")
    logger.info("  - load_example_data: Example data loader")
