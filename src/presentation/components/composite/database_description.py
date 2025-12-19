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
    insights: str,
    section_id: Optional[str] = None,
    custom_components: Optional[List[Union[html.Div, dbc.Card, dbc.Alert]]] = None,
    use_markdown: bool = False,  # Legacy parameter, ignored
    download_button: Optional[
        Union[dbc.Col, html.Div]
    ] = None,  # NEW: Download button for header
) -> html.Div:
    """
    Create a standardized database description section.

    Parameters
    ----------
    title : str
        Section title (supports emoji)
    description : str
        Brief description of the database and its purpose
    insights : str
        Key insights as newline-separated items (will be rendered as bullet list)
    section_id : Optional[str], optional
        HTML id for the section
    custom_components : Optional[List], optional
        Custom Dash components to insert after description
    use_markdown : bool, optional
        Legacy parameter, ignored (kept for compatibility)
    download_button : Optional[Union[dbc.Col, html.Div]], optional
        Download button component to display in header (right-aligned), by default None

    Returns
    -------
    html.Div
        Complete database description section
    """
    # Title with optional download button
    if download_button:
        # Title with button (flexbox layout)
        title_component = dbc.Row(
            [
                dbc.Col(
                    [html.H3(title, className="mb-0", style={"color": "#2c3e50"})],
                    width="auto",
                ),
                dbc.Col([download_button], width="auto", className="ms-auto"),
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

    # Key features header
    components.append(
        html.H5(
            "Key Database Features:", className="mt-3 mb-2", style={"color": "#34495e"}
        )
    )

    # Parse insights into list items
    # Remove bullet characters and split by newlines
    insight_lines = [
        line.strip().lstrip("•").lstrip("*").strip()
        for line in insights.split("\n")
        if line.strip() and line.strip() not in ["•", "*", "-"]
    ]

    # Create native HTML unordered list
    insights_list = html.Ul(
        [html.Li(line, className="mb-1") for line in insight_lines],
        className="text-muted",
    )

    components.append(insights_list)

    # "Your Results" section
    components.append(
        html.P(
            [
                html.Strong("Your Results "),
                html.Span(
                    "show which entries from your samples match known database records, "
                    "enabling targeted assessment of bioremediation potential for specific compounds.",
                    className="text-muted",
                ),
            ],
            className="mt-3",
        )
    )

    # Wrap in container
    return html.Div(components, id=section_id, className="mb-4")
