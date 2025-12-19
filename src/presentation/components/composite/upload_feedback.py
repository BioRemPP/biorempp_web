"""
Upload Feedback Component

Composite component for displaying upload validation feedback with different
severity levels (success, info, warning, danger).

This component provides a unified interface for showing upload results,
validation errors, and processing status to users.

Functions
---------
create_feedback_alert
    Creates a Bootstrap alert with custom styling based on severity
create_validation_report
    Creates detailed validation report card with warnings/errors
create_file_info_card
    Creates file information display card with statistics

Examples
--------
>>> from src.presentation.components.composite.upload_feedback import (
...     create_feedback_alert,
...     create_validation_report
... )
>>>
>>> # Success feedback
>>> alert = create_feedback_alert(
...     "success",
...     "File uploaded successfully!",
...     details={"samples": 50, "kos": 1000}
... )
>>>
>>> # Validation errors
>>> report = create_validation_report(
...     errors=["Invalid KO format on line 10"],
...     warnings=["Sample name sanitized"]
... )

Notes
-----
Uses Bootstrap 5 components for consistent styling.
All feedback is user-friendly and actionable.
"""

from typing import Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import html


def create_feedback_alert(
    severity: str,
    message: str,
    details: Optional[Dict] = None,
    icon: Optional[str] = None,
) -> dbc.Alert:
    """
    Create a Bootstrap alert with custom styling based on severity.

    Parameters
    ----------
    severity : str
        Alert severity level: 'success', 'info', 'warning', 'danger'
    message : str
        Main message to display
    details : Optional[Dict]
        Additional details to show (key-value pairs)
    icon : Optional[str]
        FontAwesome icon class (e.g., 'fa-check-circle')

    Returns
    -------
    dbc.Alert
        Styled Bootstrap alert component

    Examples
    --------
    >>> alert = create_feedback_alert(
    ...     "success",
    ...     "File uploaded successfully!",
    ...     details={"samples": 50, "kos": 1000},
    ...     icon="fa-check-circle"
    ... )

    >>> alert = create_feedback_alert(
    ...     "danger",
    ...     "Upload failed: File too large",
    ...     icon="fa-times-circle"
    ... )

    Notes
    -----
    Severity levels map to Bootstrap colors:
    - success: green (successful operations)
    - info: blue (informational messages)
    - warning: yellow (warnings, non-critical issues)
    - danger: red (errors, critical issues)
    """
    # Icon mapping based on severity
    icon_map = {
        "success": "fa-check-circle",
        "info": "fa-info-circle",
        "warning": "fa-exclamation-triangle",
        "danger": "fa-times-circle",
    }

    # Use provided icon or default based on severity
    icon_class = icon or icon_map.get(severity, "fa-circle")

    # Build alert content
    content = [
        html.I(className=f"fas {icon_class} me-2"),
        html.Strong(message) if severity == "danger" else html.Span(message),
    ]

    # Add details if provided
    if details:
        detail_items = []
        for key, value in details.items():
            detail_items.append(
                html.Div(
                    [html.Strong(f"{key}: "), html.Span(str(value))], className="ms-3"
                )
            )

        content.extend([html.Br(), html.Div(detail_items, className="mt-2")])

    return dbc.Alert(content, color=severity, className="mt-3")


def create_validation_report(
    errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    info: Optional[List[str]] = None,
) -> Optional[dbc.Card]:
    """
    Create detailed validation report card with warnings/errors.

    Parameters
    ----------
    errors : Optional[List[str]]
        List of error messages
    warnings : Optional[List[str]]
        List of warning messages
    info : Optional[List[str]]
        List of informational messages

    Returns
    -------
    Optional[dbc.Card]
        Validation report card, or None if no messages

    Examples
    --------
    >>> report = create_validation_report(
    ...     errors=["Invalid KO format on line 10", "Empty sample name on line 25"],
    ...     warnings=["Sample name 'Test-01' sanitized to 'Test_01'"]
    ... )

    >>> # Info only
    >>> report = create_validation_report(
    ...     info=["All validations passed", "Ready to process"]
    ... )

    Notes
    -----
    Displays messages in order: errors, warnings, info.
    Uses color-coded badges for each severity level.
    Returns None if no messages provided.
    """
    if not (errors or warnings or info):
        return None

    sections = []

    # Error section (critical - red)
    if errors:
        error_items = [
            html.Li(
                [
                    html.Span(className="badge bg-danger me-2", children="ERROR"),
                    html.Span(error),
                ],
                className="mb-2",
            )
            for error in errors
        ]

        sections.append(
            html.Div(
                [
                    html.H6(
                        [
                            html.I(className="fas fa-times-circle text-danger me-2"),
                            f"Errors ({len(errors)})",
                        ],
                        className="text-danger",
                    ),
                    html.Ul(error_items, className="list-unstyled"),
                ],
                className="mb-3",
            )
        )

    # Warning section (non-critical - yellow)
    if warnings:
        warning_items = [
            html.Li(
                [
                    html.Span(className="badge bg-warning me-2", children="WARNING"),
                    html.Span(warning),
                ],
                className="mb-2",
            )
            for warning in warnings
        ]

        sections.append(
            html.Div(
                [
                    html.H6(
                        [
                            html.I(
                                className="fas fa-exclamation-triangle text-warning me-2"
                            ),
                            f"Warnings ({len(warnings)})",
                        ],
                        className="text-warning",
                    ),
                    html.Ul(warning_items, className="list-unstyled"),
                ],
                className="mb-3",
            )
        )

    # Info section (informational - blue)
    if info:
        info_items = [
            html.Li(
                [
                    html.Span(className="badge bg-info me-2", children="INFO"),
                    html.Span(inf),
                ],
                className="mb-2",
            )
            for inf in info
        ]

        sections.append(
            html.Div(
                [
                    html.H6(
                        [
                            html.I(className="fas fa-info-circle text-info me-2"),
                            f"Information ({len(info)})",
                        ],
                        className="text-info",
                    ),
                    html.Ul(info_items, className="list-unstyled"),
                ]
            )
        )

    return dbc.Card(
        [
            dbc.CardHeader(
                [html.I(className="fas fa-clipboard-list me-2"), "Validation Report"]
            ),
            dbc.CardBody(sections),
        ],
        className="mt-3 border-primary",
    )


def create_file_info_card(
    filename: str,
    sample_count: int,
    ko_count: int,
    file_size_bytes: int,
    max_samples: int,
    max_kos: int,
    max_size_mb: int,
    warnings: Optional[List[str]] = None,
) -> dbc.Card:
    """
    Create file information display card with statistics.

    Parameters
    ----------
    filename : str
        Name of uploaded file
    sample_count : int
        Number of samples detected
    ko_count : int
        Number of KO entries detected
    file_size_bytes : int
        File size in bytes
    max_samples : int
        Maximum allowed samples
    max_kos : int
        Maximum allowed KO entries
    max_size_mb : int
        Maximum allowed file size in MB
    warnings : Optional[List[str]]
        List of warnings to display

    Returns
    -------
    dbc.Card
        File information card with progress bars and statistics

    Examples
    --------
    >>> card = create_file_info_card(
    ...     filename="samples.txt",
    ...     sample_count=50,
    ...     ko_count=1000,
    ...     file_size_bytes=102400,
    ...     max_samples=100,
    ...     max_kos=500000,
    ...     max_size_mb=10
    ... )

    Notes
    -----
    Shows progress bars for samples, KOs, and file size.
    Uses color coding: green (safe), yellow (warning), red (exceeded).
    Displays warnings if any validations failed.
    """
    # Calculate percentages
    sample_percent = (sample_count / max_samples) * 100 if max_samples > 0 else 0
    ko_percent = (ko_count / max_kos) * 100 if max_kos > 0 else 0
    size_mb = file_size_bytes / (1024 * 1024)
    size_percent = (size_mb / max_size_mb) * 100 if max_size_mb > 0 else 0

    # Determine colors based on usage
    def get_color(percent):
        if percent < 70:
            return "success"
        elif percent < 90:
            return "warning"
        else:
            return "danger"

    sample_color = get_color(sample_percent)
    ko_color = get_color(ko_percent)
    size_color = get_color(size_percent)

    content = [
        # Filename
        html.Div(
            [html.Strong("Filename: "), html.Span(filename, className="text-muted")],
            className="mb-3",
        ),
        # Samples progress
        html.Div(
            [
                html.Div(
                    [
                        html.Strong("Samples: "),
                        html.Span(
                            f"{sample_count}", className=f"badge bg-{sample_color}"
                        ),
                        html.Small(
                            f" / {max_samples} max", className="text-muted ms-2"
                        ),
                    ],
                    className="mb-1",
                ),
                dbc.Progress(
                    value=sample_percent,
                    color=sample_color,
                    className="mb-3",
                    style={"height": "8px"},
                ),
            ]
        ),
        # KOs progress
        html.Div(
            [
                html.Div(
                    [
                        html.Strong("KO IDs: "),
                        html.Span(f"{ko_count:,}", className=f"badge bg-{ko_color}"),
                        html.Small(f" / {max_kos:,} max", className="text-muted ms-2"),
                    ],
                    className="mb-1",
                ),
                dbc.Progress(
                    value=ko_percent,
                    color=ko_color,
                    className="mb-3",
                    style={"height": "8px"},
                ),
            ]
        ),
        # File size progress
        html.Div(
            [
                html.Div(
                    [
                        html.Strong("File Size: "),
                        html.Span(
                            f"{size_mb:.2f} MB", className=f"badge bg-{size_color}"
                        ),
                        html.Small(
                            f" / {max_size_mb} MB max", className="text-muted ms-2"
                        ),
                    ],
                    className="mb-1",
                ),
                dbc.Progress(
                    value=size_percent, color=size_color, style={"height": "8px"}
                ),
            ]
        ),
    ]

    # Add warnings section if any
    if warnings:
        content.append(html.Hr())
        content.append(
            html.Div(
                [
                    html.I(className="fas fa-exclamation-triangle text-warning me-2"),
                    html.Strong("Warnings:", className="text-warning"),
                ]
            )
        )
        for warning in warnings:
            content.append(
                html.Div(
                    [html.Small(f"• {warning}", className="text-muted d-block ms-4")]
                )
            )

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H6(
                        [
                            html.I(className="fas fa-file-alt me-2 text-success"),
                            "File Information",
                        ],
                        className="text-success mb-3",
                    ),
                    html.Div(content),
                ]
            )
        ],
        className="border-success mt-3",
    )


def create_error_alert(
    error_type: str, error_message: str, suggestions: Optional[List[str]] = None
) -> dbc.Alert:
    """
    Create detailed error alert with suggestions.

    Parameters
    ----------
    error_type : str
        Type of error (e.g., "File Size Exceeded", "Invalid Format")
    error_message : str
        Detailed error message
    suggestions : Optional[List[str]]
        List of suggestions to fix the error

    Returns
    -------
    dbc.Alert
        Error alert with suggestions

    Examples
    --------
    >>> alert = create_error_alert(
    ...     "File Size Exceeded",
    ...     "File size (15 MB) exceeds maximum allowed (10 MB)",
    ...     suggestions=[
    ...         "Reduce file size by removing unnecessary samples",
    ...         "Split into multiple files"
    ...     ]
    ... )

    Notes
    -----
    Always displays in 'danger' color (red).
    Shows actionable suggestions when provided.
    """
    content = [
        html.Div(
            [html.I(className="fas fa-times-circle me-2"), html.Strong(error_type)],
            className="mb-2",
        ),
        html.Div(error_message, className="ms-4"),
    ]

    if suggestions:
        content.append(html.Hr())
        content.append(
            html.Div(
                [
                    html.Strong("Suggestions:"),
                    html.Ul([html.Li(suggestion) for suggestion in suggestions]),
                ],
                className="mt-2",
            )
        )

    return dbc.Alert(content, color="danger", className="mt-3")
