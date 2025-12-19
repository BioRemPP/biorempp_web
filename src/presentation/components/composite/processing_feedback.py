"""
Processing Feedback Component

Composite component for displaying processing status, errors, and results
with different severity levels and progress tracking.

This component provides a unified interface for showing processing progress,
validation results, merge statistics, and error recovery suggestions.

Functions
---------
create_processing_alert
    Creates alert for processing status (success, error, warning)
create_processing_error_alert
    Creates detailed error alert with recovery suggestions
create_processing_report
    Creates detailed processing report with statistics
create_merge_statistics_card
    Creates card showing merge statistics and match rates
create_processing_spinner
    Creates spinner with elapsed time for ongoing processing
create_timeout_warning
    Creates warning for long-running processes

Examples
--------
>>> from src.presentation.components.composite.processing_feedback import (
...     create_processing_alert,
...     create_processing_report
... )
>>>
>>> # Success feedback
>>> alert = create_processing_alert(
...     "success",
...     "Data processed successfully!",
...     details={"samples": 50, "matched_kos": 800, "time": 5.2}
... )
>>>
>>> # Error with recovery
>>> error_alert = create_processing_error_alert(
...     "Database Connection Failed",
...     "Unable to connect to BioRemPP database",
...     error_type="ConnectionError",
...     recovery_suggestions=[
...         "Check network connection",
...         "Retry processing",
...         "Contact support if problem persists"
...     ]
... )

Notes
-----
Uses Bootstrap 5 components for consistent styling.
Reuses functions from upload_feedback.py for consistency.
All feedback is user-friendly and actionable.
"""

from typing import Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import html


def create_processing_alert(
    severity: str,
    message: str,
    details: Optional[Dict] = None,
    icon: Optional[str] = None,
) -> dbc.Alert:
    """
    Create Bootstrap alert for processing status.

    Parameters
    ----------
    severity : str
        Alert severity: 'success', 'info', 'warning', 'danger'
    message : str
        Main message to display
    details : Optional[Dict]
        Additional details (key-value pairs)
    icon : Optional[str]
        FontAwesome icon class (e.g., 'fa-check-circle')

    Returns
    -------
    dbc.Alert
        Styled Bootstrap alert component

    Examples
    --------
    >>> alert = create_processing_alert(
    ...     "success",
    ...     "Processing completed!",
    ...     details={"samples": 50, "time": 5.2},
    ...     icon="fa-check-circle"
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

    icon_class = icon or icon_map.get(severity, "fa-circle")

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


def create_processing_error_alert(
    error_title: str,
    error_message: str,
    error_type: str = "ProcessingError",
    recovery_suggestions: Optional[List[str]] = None,
    technical_details: Optional[str] = None,
) -> dbc.Alert:
    """
    Create detailed error alert with recovery suggestions.

    Parameters
    ----------
    error_title : str
        Error title (e.g., "Database Merge Failed")
    error_message : str
        Detailed error message
    error_type : str
        Type of error for logging (default: "ProcessingError")
    recovery_suggestions : Optional[List[str]]
        List of recovery suggestions
    technical_details : Optional[str]
        Technical details for debugging (collapsed by default)

    Returns
    -------
    dbc.Alert
        Error alert with recovery suggestions

    Examples
    --------
    >>> alert = create_processing_error_alert(
    ...     "Merge Failed",
    ...     "Unable to merge with KEGG database",
    ...     error_type="MergeError",
    ...     recovery_suggestions=[
    ...         "Check database availability",
    ...         "Retry processing"
    ...     ],
    ...     technical_details="Connection timeout after 30s"
    ... )

    Notes
    -----
    Always displays in 'danger' color (red).
    Shows actionable recovery suggestions.
    Technical details can be collapsed for cleaner UI.
    """
    content = [
        html.Div(
            [html.I(className="fas fa-times-circle me-2"), html.Strong(error_title)],
            className="mb-2",
        ),
        html.Div(error_message, className="ms-4 mb-2"),
        html.Small(
            f"Error Type: {error_type}", className="text-muted ms-4 d-block mb-3"
        ),
    ]

    # Add recovery suggestions
    if recovery_suggestions:
        content.append(html.Hr())
        content.append(
            html.Div(
                [
                    html.I(className="fas fa-lightbulb me-2 text-warning"),
                    html.Strong("Recovery Suggestions:", className="text-warning"),
                ],
                className="mb-2",
            )
        )
        content.append(
            html.Ul(
                [html.Li(suggestion) for suggestion in recovery_suggestions],
                className="ms-4",
            )
        )

    # Add technical details (collapsible)
    if technical_details:
        content.append(html.Hr())
        content.append(
            dbc.Accordion(
                [
                    dbc.AccordionItem(
                        [html.Code(technical_details, className="text-muted small")],
                        title="Technical Details",
                    )
                ],
                start_collapsed=True,
                className="mt-2",
            )
        )

    return dbc.Alert(content, color="danger", className="mt-3")


def create_processing_report(
    stage_results: Dict[str, Dict],
    errors: Optional[List[str]] = None,
    warnings: Optional[List[str]] = None,
    info: Optional[List[str]] = None,
) -> dbc.Card:
    """
    Create detailed processing report with stage-by-stage results.

    Parameters
    ----------
    stage_results : Dict[str, Dict]
        Results for each processing stage
        Format: {"stage_name": {"status": "success/failed", "details": {...}}}
    errors : Optional[List[str]]
        List of error messages
    warnings : Optional[List[str]]
        List of warning messages
    info : Optional[List[str]]
        List of informational messages

    Returns
    -------
    dbc.Card
        Processing report card

    Examples
    --------
    >>> report = create_processing_report(
    ...     stage_results={
    ...         "BioRemPP Merge": {"status": "success", "details": {"matched": 800}},
    ...         "KEGG Merge": {"status": "success", "details": {"matched": 750}}
    ...     },
    ...     warnings=["10 KO IDs not found in database"]
    ... )

    Notes
    -----
    Shows stage-by-stage results with status icons.
    Displays errors, warnings, and info in separate sections.
    """
    sections = []

    # Stage results section
    if stage_results:
        stage_items = []
        for stage_name, result in stage_results.items():
            status = result.get("status", "unknown")
            details = result.get("details", {})

            # Status icon
            status_icon = (
                "fa-check-circle text-success"
                if status == "success"
                else "fa-times-circle text-danger"
            )

            stage_items.append(
                html.Div(
                    [
                        html.I(className=f"fas {status_icon} me-2"),
                        html.Strong(stage_name),
                        html.Div(
                            [html.Small(f"{k}: {v}") for k, v in details.items()],
                            className="ms-4 text-muted",
                        ),
                    ],
                    className="mb-2",
                )
            )

        sections.append(
            html.Div(
                [
                    html.H6(
                        [
                            html.I(className="fas fa-tasks me-2 text-primary"),
                            "Processing Stages",
                        ],
                        className="text-primary mb-3",
                    ),
                    html.Div(stage_items),
                ],
                className="mb-3",
            )
        )

    # Error section
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

    # Warning section
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

    # Info section
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
                [html.I(className="fas fa-clipboard-list me-2"), "Processing Report"]
            ),
            dbc.CardBody(sections),
        ],
        className="mt-3 border-primary",
    )


def create_merge_statistics_card(
    biorempp_stats: Dict,
    kegg_stats: Optional[Dict] = None,
    hadeg_stats: Optional[Dict] = None,
    toxcsm_stats: Optional[Dict] = None,
    processing_time: float = 0.0,
) -> dbc.Card:
    """
    Create card showing merge statistics for all databases.

    Parameters
    ----------
    biorempp_stats : Dict
        BioRemPP merge statistics
        Format: {"total": int, "matched": int, "match_rate": float}
    kegg_stats : Optional[Dict]
        KEGG merge statistics (same format)
    hadeg_stats : Optional[Dict]
        HADEG merge statistics (same format)
    toxcsm_stats : Optional[Dict]
        ToxCSM merge statistics (same format)
    processing_time : float
        Total processing time in seconds

    Returns
    -------
    dbc.Card
        Merge statistics card with progress bars

    Examples
    --------
    >>> card = create_merge_statistics_card(
    ...     biorempp_stats={"total": 1000, "matched": 800, "match_rate": 80.0},
    ...     kegg_stats={"total": 800, "matched": 750, "match_rate": 93.75},
    ...     processing_time=5.2
    ... )

    Notes
    -----
    Shows match rates as progress bars with color coding:
    - Green: >= 70% match rate
    - Yellow: 50-70% match rate
    - Red: < 50% match rate
    """

    def get_match_color(match_rate: float) -> str:
        """Determine color based on match rate."""
        if match_rate >= 70:
            return "success"
        elif match_rate >= 50:
            return "warning"
        else:
            return "danger"

    def create_database_stat(name: str, stats: Dict) -> html.Div:
        """Create statistics section for a database."""
        match_rate = stats.get("match_rate", 0.0)
        matched = stats.get("matched", 0)
        total = stats.get("total", 0)
        color = get_match_color(match_rate)

        return html.Div(
            [
                html.Div(
                    [
                        html.Strong(f"{name}: "),
                        html.Span(
                            f"{matched:,} / {total:,}", className=f"badge bg-{color}"
                        ),
                        html.Small(
                            f" ({match_rate:.1f}%)", className="text-muted ms-2"
                        ),
                    ],
                    className="mb-1",
                ),
                dbc.Progress(
                    value=match_rate,
                    color=color,
                    className="mb-3",
                    style={"height": "10px"},
                ),
            ]
        )

    content = [
        # BioRemPP (required)
        create_database_stat("BioRemPP Database", biorempp_stats)
    ]

    # Optional databases
    if kegg_stats:
        content.append(create_database_stat("KEGG Pathways", kegg_stats))

    if hadeg_stats:
        content.append(create_database_stat("HADEG Database", hadeg_stats))

    if toxcsm_stats:
        content.append(create_database_stat("ToxCSM Predictions", toxcsm_stats))

    # Processing time
    content.append(html.Hr())
    content.append(
        html.Div(
            [
                html.I(className="fas fa-clock me-2 text-muted"),
                html.Strong("Processing Time: "),
                html.Span(f"{processing_time:.2f}s", className="text-muted"),
            ]
        )
    )

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H6(
                        [
                            html.I(className="fas fa-chart-bar me-2 text-success"),
                            "Merge Statistics",
                        ],
                        className="text-success mb-3",
                    ),
                    html.Div(content),
                ]
            )
        ],
        className="border-success mt-3",
    )


def create_processing_spinner(
    elapsed_time: float,
    current_stage: Optional[str] = None,
    progress_percent: Optional[float] = None,
) -> html.Div:
    """
    Create spinner with elapsed time for ongoing processing.

    Parameters
    ----------
    elapsed_time : float
        Elapsed time in seconds
    current_stage : Optional[str]
        Current processing stage name
    progress_percent : Optional[float]
        Progress percentage (0-100)

    Returns
    -------
    html.Div
        Spinner component with status

    Examples
    --------
    >>> spinner = create_processing_spinner(
    ...     elapsed_time=3.5,
    ...     current_stage="BioRemPP Merge",
    ...     progress_percent=45.0
    ... )

    Notes
    -----
    Simple spinner suitable for lightweight applications.
    Shows current stage if provided.
    Shows progress bar if percentage provided.
    """
    content = [
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
    ]

    # Add current stage if provided
    if current_stage:
        content.append(
            html.Div(
                f"Stage: {current_stage}",
                className="mt-2 text-primary",
                style={"fontSize": "0.95rem"},
            )
        )

    # Add progress bar if provided
    if progress_percent is not None:
        content.append(
            html.Div(
                [
                    dbc.Progress(
                        value=progress_percent,
                        color="success",
                        className="mt-3",
                        style={"height": "8px", "width": "300px", "margin": "0 auto"},
                    ),
                    html.Small(
                        f"{progress_percent:.0f}%", className="text-muted d-block mt-1"
                    ),
                ]
            )
        )

    # Add elapsed time
    content.append(
        html.Div(
            f"Elapsed time: {elapsed_time:.1f}s",
            className="mt-2 text-muted",
            style={"fontSize": "0.9rem"},
        )
    )

    return html.Div(content, className="text-center py-4")


def create_timeout_warning(
    elapsed_time: float, timeout_threshold: float = 30.0
) -> Optional[dbc.Alert]:
    """
    Create warning for long-running processes.

    Parameters
    ----------
    elapsed_time : float
        Current elapsed time in seconds
    timeout_threshold : float
        Threshold in seconds to trigger warning (default: 30s)

    Returns
    -------
    Optional[dbc.Alert]
        Warning alert if threshold exceeded, None otherwise

    Examples
    --------
    >>> warning = create_timeout_warning(elapsed_time=35.0, timeout_threshold=30.0)
    >>> if warning:
    ...     # Display warning

    Notes
    -----
    Helps users understand when processing is taking longer than expected.
    Provides reassurance and actionable suggestions.
    """
    if elapsed_time < timeout_threshold:
        return None

    return dbc.Alert(
        [
            html.I(className="fas fa-hourglass-half me-2"),
            html.Strong("Processing is taking longer than expected"),
            html.Br(),
            html.Small(
                [
                    f"Elapsed time: {elapsed_time:.1f}s. ",
                    "This may be normal for large datasets. ",
                    "If it continues, you may need to refresh the page and try again.",
                ],
                className="text-muted",
            ),
        ],
        color="info",
        className="mt-3",
    )


def create_validation_summary(
    ignored_kos: int = 0,
    duplicate_samples: int = 0,
    sanitized_names: int = 0,
    total_samples: int = 0,
    total_kos: int = 0,
) -> Optional[dbc.Card]:
    """
    Create summary of parsing and validation results.

    Parameters
    ----------
    ignored_kos : int
        Number of invalid KOs ignored during parsing
    duplicate_samples : int
        Number of duplicate samples found
    sanitized_names : int
        Number of sample names that were sanitized
    total_samples : int
        Total number of samples parsed
    total_kos : int
        Total number of KOs parsed

    Returns
    -------
    Optional[dbc.Card]
        Validation summary card, None if nothing to report

    Examples
    --------
    >>> summary = create_validation_summary(
    ...     ignored_kos=5,
    ...     duplicate_samples=2,
    ...     sanitized_names=3,
    ...     total_samples=50,
    ...     total_kos=1000
    ... )

    Notes
    -----
    Provides transparency about data quality issues found during parsing.
    Helps users understand what was modified or ignored.
    """
    has_issues = any([ignored_kos, duplicate_samples, sanitized_names])

    if not has_issues:
        return None

    issues = []

    if ignored_kos > 0:
        issues.append(
            html.Li(
                [
                    html.Span(className="badge bg-warning me-2", children="WARNING"),
                    f"{ignored_kos} invalid KO IDs were ignored during parsing",
                ],
                className="mb-2",
            )
        )

    if duplicate_samples > 0:
        issues.append(
            html.Li(
                [
                    html.Span(className="badge bg-warning me-2", children="WARNING"),
                    f"{duplicate_samples} duplicate sample names were found",
                ],
                className="mb-2",
            )
        )

    if sanitized_names > 0:
        issues.append(
            html.Li(
                [
                    html.Span(className="badge bg-info me-2", children="INFO"),
                    f"{sanitized_names} sample names were sanitized for safety",
                ],
                className="mb-2",
            )
        )

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-exclamation-triangle me-2"),
                    "Parsing Summary",
                ]
            ),
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.Strong(
                                f"Successfully parsed: {total_samples} samples, {total_kos:,} KO IDs"
                            ),
                            html.Hr(),
                            html.Ul(issues, className="list-unstyled"),
                        ]
                    )
                ]
            ),
        ],
        className="mt-3 border-warning",
    )
