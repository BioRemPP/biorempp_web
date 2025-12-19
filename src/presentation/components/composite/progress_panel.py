"""
Progress Panel - Composite UI Component.

Shows real-time processing progress with updates.

Functions
---------
create_progress_panel
    Create panel with progress bar and stage info

Notes
-----
- Composite component
- Displays ProcessingProgressDTO data
- Real-time updates via interval component
"""

from typing import Any, Dict, Optional

import dash_bootstrap_components as dbc
from dash import dcc, html

from ..base import create_button, create_progress_bar


def create_progress_panel(progress_data: Optional[Dict[str, Any]] = None) -> html.Div:
    """
    Create progress panel component.

    Parameters
    ----------
    progress_data : Optional[Dict[str, Any]], optional
        Progress data from ProcessingProgressDTO.to_dict(), by default None
        Expected keys: current_stage, total_stages, stage_name,
        message, percentage, estimated_time_remaining

    Returns
    -------
    html.Div
        Panel with progress bar and interval component for updates

    Examples
    --------
    >>> # Initial state
    >>> panel = create_progress_panel()
    >>>
    >>> # With progress data
    >>> data = {
    ...     "current_stage": 5,
    ...     "total_stages": 8,
    ...     "stage_name": "Merging data",
    ...     "message": "Combining KEGG and ToxCSM results...",
    ...     "percentage": 62.5,
    ...     "estimated_time_remaining": 30
    ... }
    >>> panel = create_progress_panel(data)

    Notes
    -----
    - Hidden by default (display: none)
    - Updates every 1 second via dcc.Interval
    - Shows 8-stage workflow progress
    - Displays estimated time remaining
    - Stages: Parse → KEGG → HadegDB → ToxCSM → Merge → Validate → Cache → Complete
    """
    # Simple spinner for processing
    spinner_display = html.Div(
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
        ],
        id="progress-display",
        className="text-center py-4",
    )

    # Process button (initially visible)
    process_button = html.Div(
        [
            create_button(
                component_id="process-data-btn",
                label="Process Data",
                variant="success",
                icon="fas fa-play",
                size="lg",
                disabled=True,  # Enabled by callback when data is available
            ),
            html.Div(id="processing-status", className="mt-3"),
        ],
        className="text-center mb-3",
    )

    panel_content = html.Div(
        [
            process_button,
            html.Div(
                id="processing-progress",
                style={"display": "none"},
                children=[spinner_display],
            ),
        ]
    )

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-cogs me-2"),
                    html.Span("Step 2: Process Data", className="font-weight-bold"),
                ],
                className="bg-success text-white",
            ),
            dbc.CardBody(panel_content),
        ],
        className="mb-3",
        id="progress-panel",
    )
