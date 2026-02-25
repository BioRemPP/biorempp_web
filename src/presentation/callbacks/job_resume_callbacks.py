"""
Job Resume Callbacks - restore processed results by `job_id`.
"""

from uuid import uuid4

import dash_bootstrap_components as dbc
from dash import Input, Output, State, html, no_update
from dash.exceptions import PreventUpdate

from src.presentation.services import job_resume_service
from src.shared.logging import get_logger

logger = get_logger(__name__)


def _build_status_alert(message: str, color: str = "info") -> dbc.Alert:
    """Create standardized resume status alert."""
    icon_by_color = {
        "success": "fa-check-circle",
        "warning": "fa-exclamation-triangle",
        "danger": "fa-times-circle",
        "info": "fa-info-circle",
    }
    icon = icon_by_color.get(color, "fa-info-circle")
    return dbc.Alert([html.I(className=f"fas {icon} me-2"), message], color=color)


def initialize_resume_browser_token(existing_token: str):
    """
    Ensure browser resume token exists in local storage.

    Returns
    -------
    str | no_update
        Existing token is preserved; missing token gets a new UUID.
    """
    if isinstance(existing_token, str) and existing_token.strip():
        return no_update
    return str(uuid4())


def resolve_resume_request(job_id: str, owner_token: str):
    """
    Resolve resume flow outputs from job_id + owner_token.

    Returns
    -------
    tuple
        (merged_result_store_update, pathname_update, status_component)
    """
    normalized_job_id = (job_id or "").strip().upper()

    if not normalized_job_id:
        return (
            no_update,
            no_update,
            _build_status_alert("Provide a Job ID to resume an analysis.", "warning"),
        )

    if not isinstance(owner_token, str) or not owner_token.strip():
        return (
            no_update,
            no_update,
            _build_status_alert(
                "This browser context is not initialized for resume yet.",
                "danger",
            ),
        )

    if not job_resume_service.validate_job_id(normalized_job_id):
        return (
            no_update,
            no_update,
            _build_status_alert(
                "Invalid Job ID format. Use BRP-YYYYMMDD-HHMMSS-XXXXXX.",
                "danger",
            ),
        )

    payload, status = job_resume_service.load_job_payload(
        normalized_job_id, owner_token
    )

    if status == job_resume_service.STATUS_OK and payload is not None:
        return (
            payload,
            "/results",
            _build_status_alert(
                f"Job {normalized_job_id} loaded. Redirecting to results...",
                "success",
            ),
        )

    if status == job_resume_service.STATUS_TOKEN_MISMATCH:
        return (
            no_update,
            no_update,
            _build_status_alert(
                "This Job ID belongs to another browser context.", "danger"
            ),
        )

    if status == job_resume_service.STATUS_INCOMPATIBLE_VERSION:
        return (
            no_update,
            no_update,
            _build_status_alert(
                "Stored job data version is not compatible anymore. "
                "Please process the file again.",
                "danger",
            ),
        )

    return (
        no_update,
        no_update,
        _build_status_alert(
            "Job ID not found or expired. Run processing again to generate a new job.",
            "warning",
        ),
    )


def register_job_resume_callbacks(app):
    """Register callbacks related to resume-by-job-id flow."""
    logger.info("=" * 60)
    logger.info("Registering JOB RESUME callbacks...")
    logger.info("=" * 60)

    @app.callback(
        Output("resume-browser-token-store", "data"),
        Input("resume-browser-token-store", "modified_timestamp"),
        State("resume-browser-token-store", "data"),
    )
    def ensure_resume_browser_token(_, existing_token):
        token = initialize_resume_browser_token(existing_token)
        if token is no_update:
            raise PreventUpdate
        logger.info("Resume browser token initialized")
        return token

    @app.callback(
        [
            Output("merged-result-store", "data", allow_duplicate=True),
            Output("url", "pathname"),
            Output("resume-job-status", "children"),
        ],
        Input("resume-job-btn", "n_clicks"),
        [
            State("resume-job-id-input", "value"),
            State("resume-browser-token-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def resume_job_by_id(n_clicks, job_id, owner_token):
        if n_clicks is None:
            raise PreventUpdate

        return resolve_resume_request(job_id, owner_token)

    logger.info("[OK] Job resume callbacks registered successfully")
