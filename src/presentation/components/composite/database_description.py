"""
Database Description Component - BioRemPP v1.0
==============================================

Flexible component for database result descriptions using native Dash components.

Functions
---------
create_database_description
    Create standardized database description section with Bootstrap styling

Notes
-----
- Uses native html.Ul and html.Li for lists
- No markdown parsing
- Pure Dash Bootstrap Components styling
"""

from typing import List, Optional, Union

import dash_bootstrap_components as dbc
from dash import html


def create_database_description(
    title: str,
    description: str,
    insights: Optional[str] = None,  # Deprecated: no longer displayed
    section_id: Optional[str] = None,
    custom_components: Optional[List[Union[html.Div, dbc.Card, dbc.Alert]]] = None,
    use_markdown: bool = False,  # Legacy parameter, ignored
    download_button: Optional[
        Union[dbc.Col, html.Div]
    ] = None,  # Download button for header
    info_button: Optional[
        Union[dbc.Col, html.Div]
    ] = None,  # Database Info button for header
) -> html.Div:
    """
    Create a standardized database description section.

    Parameters
    ----------
    title : str
        Section title (supports emoji)
    description : str
        Brief description of the database and its purpose
    insights : Optional[str], optional
        Deprecated: Key insights parameter (no longer displayed, kept for compatibility)
    section_id : Optional[str], optional
        HTML id for the section
    custom_components : Optional[List], optional
        Custom Dash components to insert after description
    use_markdown : bool, optional
        Legacy parameter, ignored (kept for compatibility)
    download_button : Optional[Union[dbc.Col, html.Div]], optional
        Download button component to display in header (right-aligned), by default None
    info_button : Optional[Union[dbc.Col, html.Div]], optional
        Database Info button component to open schema page (opens in new tab), by default None

    Returns
    -------
    html.Div
        Complete database description section
    """
    # Title with optional buttons (download + info)
    if download_button or info_button:
        # Build button group
        button_cols = []
        if info_button:
            button_cols.append(dbc.Col([info_button], width="auto", className="me-2"))
        if download_button:
            button_cols.append(dbc.Col([download_button], width="auto"))
        
        # Title with buttons (flexbox layout)
        title_component = dbc.Row(
            [
                dbc.Col(
                    [html.H3(title, className="mb-0", style={"color": "#2c3e50"})],
                    width="auto",
                ),
                dbc.Col(
                    dbc.Row(button_cols, className="g-0"),
                    width="auto",
                    className="ms-auto",
                ),
            ],
            className="align-items-center mb-3",
        )
    else:
        # Title only (centered)
        title_component = html.H3(
            title, className="text-center mb-3", style={"color": "#2c3e50"}
        )

    # Description
    description_component = html.P(description, className="text-muted text-center mb-3")

    # Build components list
    components = [title_component, description_component]

    # Add custom components if provided
    if custom_components:
        components.extend(custom_components)

    # Wrap in container
    return html.Div(components, id=section_id, className="mb-4")
