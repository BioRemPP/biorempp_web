"""
Progress Bar Component - Atomic UI Component.

Creates progress bar with stage tracking for processing workflow.

Functions
---------
create_progress_bar
    Create progress bar from ProcessingProgressDTO

Notes
-----
- Atomic component
- Displays 8-stage workflow progress
- Shows current stage, message, estimated time
"""

from typing import Any, Dict, Optional

import dash_bootstrap_components as dbc
from dash import html


def create_progress_bar(
    progress_data: Optional[Dict[str, Any]] = None, component_id: str = "progress-bar"
) -> html.Div:
    """
    Create progress bar component.

    Parameters
    ----------
    progress_data : Optional[Dict[str, Any]], optional
        Progress data from ProcessingProgressDTO.to_dict(), by default None
        Expected keys: current_stage, total_stages, stage_name,
        message, percentage, estimated_time_remaining
    component_id : str, optional
        ID for the progress bar container, by default "progress-bar"

    Returns
    -------
    html.Div
        Progress bar with stage info and estimated time

    Examples
    --------
    >>> # No progress
    >>> progress = create_progress_bar()
    >>>
    >>> # With progress data
    >>> data = {
    ...     "current_stage": 3,
    ...     "total_stages": 8,
    ...     "stage_name": "Processing KEGG data",
    ...     "message": "Matching KO entries...",
    ...     "percentage": 37.5,
    ...     "estimated_time_remaining": 45
    ... }
    >>> progress = create_progress_bar(data)

    Notes
    -----
    - Green color (#28a745) for active progress
    - Shows stage X/Y
    - Displays current message
    - Estimated time in seconds
    """
    if progress_data is None:
        progress_data = {
            "current_stage": 0,
            "total_stages": 8,
            "stage_name": "Initializing",
            "message": "Waiting to start...",
            "percentage": 0,
            "estimated_time_remaining": None,
        }

    current = progress_data.get("current_stage", 0)
    total = progress_data.get("total_stages", 8)
    stage_name = progress_data.get("stage_name", "Processing")
    message = progress_data.get("message", "")
    percentage = progress_data.get("percentage", 0)
    eta = progress_data.get("estimated_time_remaining")

    stage_label = html.Div(
        [
            html.Strong(f"Stage {current}/{total}: "),
            html.Span(stage_name, className="text-success"),
        ],
        className="mb-2",
    )

    progress_bar = dbc.Progress(
        value=percentage,
        striped=True,
        animated=True if percentage > 0 and percentage < 100 else False,
        color="success",
        style={"height": "25px"},
        className="mb-2",
    )

    message_text = html.Div(
        message, className="text-muted", style={"fontSize": "0.9rem"}
    )

    eta_text = html.Div()
    if eta is not None and eta > 0:
        eta_formatted = f"{eta:.0f}s" if eta < 60 else f"{eta/60:.1f}min"
        eta_text = html.Div(
            f"Estimated time remaining: {eta_formatted}",
            className="text-info mt-1",
            style={"fontSize": "0.85rem"},
        )

    return html.Div(
        [stage_label, progress_bar, message_text, eta_text],
        id=component_id,
        className="mb-3",
    )
