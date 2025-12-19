"""
Validation Panel - Composite UI Component.

Displays upload validation results and feedback.

Functions
---------
create_validation_panel
    Create panel showing upload validation status

Notes
-----
- Composite component
- Shows UploadResultDTO feedback
- Displays validation errors/warnings
"""

from typing import Any, Dict, Optional

import dash_bootstrap_components as dbc
from dash import html

from ..base import create_alert, create_button


def create_validation_panel(
    validation_data: Optional[Dict[str, Any]] = None
) -> html.Div:
    """
    Create validation panel component.

    Parameters
    ----------
    validation_data : Optional[Dict[str, Any]], optional
        Validation data from UploadResultDTO.to_dict(), by default None
        Expected keys: success, sample_count, ko_count,
        validation_errors, validation_warnings, filename

    Returns
    -------
    html.Div
        Panel showing validation results with alerts and statistics

    Examples
    --------
    >>> # No validation yet
    >>> panel = create_validation_panel()
    >>>
    >>> # With validation data
    >>> data = {
    ...     "success": True,
    ...     "sample_count": 150,
    ...     "ko_count": 1200,
    ...     "validation_errors": [],
    ...     "validation_warnings": ["Duplicate KO entries removed"],
    ...     "filename": "my_data.txt"
    ... }
    >>> panel = create_validation_panel(data)

    Notes
    -----
    - Hidden by default (display: none)
    - Shows success/error alerts
    - Displays data statistics
    - Lists validation errors/warnings
    - "Process Data" button appears on success
    """
    if validation_data is None:
        return html.Div(id="validation-panel", style={"display": "none"})

    success = validation_data.get("success", False)
    sample_count = validation_data.get("sample_count", 0)
    ko_count = validation_data.get("ko_count", 0)
    errors = validation_data.get("validation_errors", [])
    warnings = validation_data.get("validation_warnings", [])
    filename = validation_data.get("filename", "Unknown")

    # Main status alert
    if success:
        status_alert = create_alert(
            f" File '{filename}' validated successfully!", alert_type="success"
        )
    else:
        status_alert = create_alert(
            f"✗ Validation failed for '{filename}'", alert_type="error"
        )

    # Statistics
    stats = (
        html.Div(
            [
                html.H6("Data Summary:", className="text-success mb-2"),
                html.Ul(
                    [
                        html.Li(f"Samples detected: {sample_count}"),
                        html.Li(f"Total KO entries: {ko_count}"),
                        html.Li(
                            f"Average KOs per sample: {ko_count/sample_count:.1f}"
                            if sample_count > 0
                            else "N/A"
                        ),
                    ],
                    className="mb-3",
                ),
            ]
        )
        if success
        else html.Div()
    )

    # Warnings
    warnings_section = html.Div()
    if warnings:
        warning_items = [
            create_alert(warning, alert_type="warning", dismissable=True)
            for warning in warnings
        ]
        warnings_section = html.Div(
            [
                html.H6("Warnings:", className="text-warning mb-2"),
                html.Div(warning_items),
            ],
            className="mb-3",
        )

    # Errors
    errors_section = html.Div()
    if errors:
        error_items = [
            create_alert(error, alert_type="error", dismissable=True)
            for error in errors
        ]
        errors_section = html.Div(
            [html.H6("Errors:", className="text-danger mb-2"), html.Div(error_items)],
            className="mb-3",
        )

    # Process button (only if successful)
    process_button = html.Div()
    if success:
        process_button = html.Div(
            [
                create_button(
                    component_id="process-data-btn",
                    label="Process Data",
                    variant="success",
                    size="lg",
                    icon="fas fa-cogs",
                )
            ],
            className="d-flex justify-content-center mt-3",
        )

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-check-circle me-2"),
                    html.Span("Validation Results", className="font-weight-bold"),
                ],
                className="bg-info text-white",
            ),
            dbc.CardBody(
                [status_alert, stats, warnings_section, errors_section, process_button]
            ),
        ],
        className="mb-3",
        id="validation-panel",
    )
