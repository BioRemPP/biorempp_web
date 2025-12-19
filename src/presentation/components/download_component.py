"""
Download Component - UI Component for Data Export.

This module provides reusable UI components for downloading data from use cases
with format selection (CSV, Excel, JSON) and loading feedback.

Components:
-----------
create_download_button()
    Creates a download button with dropdown menu for format selection

Author: BioRemPP Development Team
Date: 2025-11-28
Version: 1.0.0
"""

from typing import List, Optional

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_download_button(
    use_case_id: str,
    button_id: str,
    download_id: str,
    formats: Optional[List[str]] = None,
    button_text: str = "Download Data",
    button_color: str = "success",
    button_outline: bool = True,
    show_spinner: bool = True,
) -> dbc.Col:
    """
    Create download button with format dropdown menu.

    This component provides a complete download UI with:
    - Dropdown menu for format selection (CSV, Excel, JSON)
    - Download button with icon
    - Loading spinner with "Preparing download..." message
    - dcc.Download component for file delivery

    Parameters
    ----------
    use_case_id : str
        Use case identifier (e.g., "UC-2.1")
    button_id : str
        ID for the download button (e.g., "uc-2-1-download-btn")
    download_id : str
        ID for the dcc.Download component (e.g., "uc-2-1-download")
    formats : Optional[List[str]], optional
        List of available formats ['csv', 'excel', 'json'], by default all
    button_text : str, optional
        Text for the button, by default "Download Data"
    button_color : str, optional
        Bootstrap color name, by default "success"
    button_outline : bool, optional
        Use outline style, by default True
    show_spinner : bool, optional
        Show loading spinner during download, by default True

    Returns
    -------
    dbc.Col
        Bootstrap column containing the complete download UI

    Examples
    --------
    >>> from src.presentation.components.download_component import create_download_button
    >>> download_ui = create_download_button(
    ...     use_case_id="UC-2.1",
    ...     button_id="uc-2-1-download-btn",
    ...     download_id="uc-2-1-download"
    ... )

    Notes
    -----
    - Place this component in the same horizontal row as "View Results" button
    - Position it on the left side of the row
    - Dropdown menu appears on button click
    - Spinner activates during download preparation
    """
    if formats is None:
        formats = ["csv", "excel", "json"]

    # Format options for dropdown
    format_options = {
        "csv": {"label": "CSV (.csv)", "icon": "fas fa-file-csv"},
        "excel": {"label": "Excel (.xlsx)", "icon": "fas fa-file-excel"},
        "json": {"label": "JSON (.json)", "icon": "fas fa-file-code"},
    }

    # Create dropdown menu items
    dropdown_items = []
    for fmt in formats:
        if fmt in format_options:
            dropdown_items.append(
                dbc.DropdownMenuItem(
                    [
                        html.I(className=f"{format_options[fmt]['icon']} me-2"),
                        format_options[fmt]["label"],
                    ],
                    id=f"{button_id}-{fmt}",
                    n_clicks=0,
                )
            )

    # Loading spinner ID
    spinner_id = f"{button_id}-spinner"
    spinner_text_id = f"{button_id}-spinner-text"

    # Create dropdown button group
    # Note: DropdownMenu doesn't support 'outline' parameter in dbc 2.0.4
    # Use className to style if needed
    download_dropdown = dbc.DropdownMenu(
        dropdown_items,
        label=[html.I(className="fas fa-download me-2"), button_text],
        color=button_color,
        size="md",
        className="me-2",
    )

    # Loading spinner (hidden by default, shown during download)
    if show_spinner:
        spinner_component = html.Div(
            id=spinner_id,
            children=[
                dbc.Spinner(size="sm", color="primary"),
                html.Span(
                    "Preparing download...",
                    id=spinner_text_id,
                    className="ms-2 text-muted",
                ),
            ],
            style={"display": "none"},  # Hidden by default
        )
    else:
        spinner_component = html.Div(id=spinner_id, style={"display": "none"})

    # dcc.Download component (invisible, handles file download)
    download_component = dcc.Download(id=download_id)

    # Combine all components
    return dbc.Col(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [download_dropdown, spinner_component],
                        width="auto",
                        className="d-flex align-items-center",
                    )
                ]
            ),
            download_component,
        ],
        width="auto",
    )


def create_download_button_simple(
    use_case_id: str,
    button_id: str,
    download_id: str,
    default_format: str = "excel",
    button_text: str = "Download Data",
    button_color: str = "success",
) -> dbc.Col:
    """
    Create simple download button (single format, no dropdown).

    Simplified version for use cases that only need one format.

    Parameters
    ----------
    use_case_id : str
        Use case identifier
    button_id : str
        Button component ID
    download_id : str
        Download component ID
    default_format : str, optional
        Format to download ('csv', 'excel', 'json'), by default "excel"
    button_text : str, optional
        Button text, by default "Download Data"
    button_color : str, optional
        Button color, by default "success"

    Returns
    -------
    dbc.Col
        Bootstrap column with simple download button

    Examples
    --------
    >>> download_btn = create_download_button_simple(
    ...     use_case_id="UC-2.1",
    ...     button_id="uc-2-1-download-btn",
    ...     download_id="uc-2-1-download",
    ...     default_format="excel"
    ... )
    """
    format_icons = {
        "csv": "fas fa-file-csv",
        "excel": "fas fa-file-excel",
        "json": "fas fa-file-code",
    }

    icon_class = format_icons.get(default_format, "fas fa-download")

    return dbc.Col(
        [
            dbc.Button(
                [html.I(className=f"{icon_class} me-2"), button_text],
                id=button_id,
                color=button_color,
                outline=True,
                size="md",
                n_clicks=0,
            ),
            dcc.Download(id=download_id),
            # Hidden div to store format selection
            html.Div(
                default_format, id=f"{button_id}-format", style={"display": "none"}
            ),
        ],
        width="auto",
    )


def create_download_toast(toast_id: str) -> dbc.Toast:
    """
    Create toast notification for download feedback.

    Shows success/error messages after download attempt.

    Parameters
    ----------
    toast_id : str
        Toast component ID

    Returns
    -------
    dbc.Toast
        Toast notification component

    Examples
    --------
    >>> toast = create_download_toast("uc-2-1-download-toast")
    """
    return dbc.Toast(
        id=toast_id,
        header="Download Status",
        is_open=False,
        dismissable=True,
        duration=4000,
        icon="success",
        style={
            "position": "fixed",
            "top": 80,
            "right": 20,
            "zIndex": 9999,
            "minWidth": "300px",
        },
    )


def sanitize_filename(use_case_id: str, database: str, ext: str) -> str:
    """
    Generate safe, descriptive filename for downloads.

    Handles special characters and ensures valid filenames across OS.

    Parameters
    ----------
    use_case_id : str
        Use case identifier (e.g., "UC-2.1")
    database : str
        Database name (e.g., "biorempp_df")
    ext : str
        File extension without dot (e.g., "csv", "xlsx", "json")

    Returns
    -------
    str
        Sanitized filename

    Examples
    --------
    >>> sanitize_filename("UC-2.1", "biorempp_df", "csv")
    'UC-2-1_biorempp_df_20251128_143022.csv'

    >>> sanitize_filename("UC-1.1", "all_databases", "xlsx")
    'UC-1-1_all_databases_20251128_143022.xlsx'

    Notes
    -----
    - Replaces dots with hyphens in use case ID
    - Adds timestamp for uniqueness
    - Ensures cross-platform compatibility
    """
    from datetime import datetime

    # Replace dots with hyphens in use case ID
    safe_uc_id = use_case_id.replace(".", "-")

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Build filename
    filename = f"{safe_uc_id}_{database}_{timestamp}.{ext}"

    return filename
