"""
Analysis Suggestions Offcanvas - BioRemPP v1.0
==============================================

Main offcanvas component with tabbed interface for analytical suggestions.

Components:
-----------
- Offcanvas container with tabs
- Tab navigation (Guiding Questions, Basic Exploration)
- Dynamic tab content loader

Author: BioRemPP Development Team
Date: 2025-12-05
"""

import dash_bootstrap_components as dbc
from dash import html


def create_suggestions_offcanvas() -> dbc.Offcanvas:
    """
    Create analytical suggestions offcanvas with tabbed interface.

    Returns
    -------
    dbc.Offcanvas
        Offcanvas component with tabs for analytical suggestions
    """
    return dbc.Offcanvas(
        [
            # Header
            html.Div(
                [
                    html.H4(
                        [
                            html.I(className="fas fa-compass me-2 text-warning"),
                            "Suggestions to Explore Your Results",
                        ],
                        className="mb-0",
                    )
                ]
            ),
            html.Hr(),
            html.P(
                "Use these guided suggestions to explore your bioremediation analysis results. "
                "Click on any use case to navigate directly to the visualization.",
                className="text-muted small mb-3",
            ),
            # Tabs Navigation
            dbc.Tabs(
                [
                    dbc.Tab(
                        label="Guiding Questions",
                        tab_id="tab-guiding",
                        tabClassName="suggestions-tab",
                        activeTabClassName="suggestions-tab-active",
                    ),
                    dbc.Tab(
                        label="Basic Exploration",
                        tab_id="tab-basic",
                        tabClassName="suggestions-tab",
                        activeTabClassName="suggestions-tab-active",
                    ),
                    dbc.Tab(
                        label="By Data Type",
                        tab_id="tab-datatype",
                        tabClassName="suggestions-tab",
                        activeTabClassName="suggestions-tab-active",
                    ),
                    dbc.Tab(
                        label="Practical Applications",
                        tab_id="tab-practical",
                        tabClassName="suggestions-tab",
                        activeTabClassName="suggestions-tab-active",
                    ),
                    dbc.Tab(
                        label="Current Trends",
                        tab_id="tab-trends",
                        tabClassName="suggestions-tab",
                        activeTabClassName="suggestions-tab-active",
                    ),
                ],
                id="suggestions-tabs",
                active_tab="tab-guiding",
                className="mb-3",
            ),
            # Tab Content Container
            html.Div(
                id="suggestions-tab-content", className="suggestions-content-area"
            ),
        ],
        id="suggestions-offcanvas",
        title="Analytical Suggestions",
        is_open=False,
        placement="end",  # Right side (same as Navigate)
        backdrop=True,
        scrollable=True,
        style={"width": "750px"},
    )


def create_suggestions_trigger_button() -> html.Div:
    """
    Create trigger button to open suggestions offcanvas.

    Returns
    -------
    html.Div
        Container with button and tooltip that toggles suggestions offcanvas
    """
    button = dbc.Button(
        html.I(className="fas fa-lightbulb"),
        id="suggestions-offcanvas-trigger",
        color="warning",
        outline=True,
        size="lg",
        className="suggestions-trigger-btn",
        style={
            "borderRadius": "50%",
            "width": "56px",
            "height": "56px",
            "padding": "0",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "fontSize": "20px",
        },
    )

    # Tooltip for the button
    tooltip = dbc.Tooltip(
        "Analytical Suggestions",
        target="suggestions-offcanvas-trigger",
        placement="left",
    )

    # Return button and tooltip directly - CSS handles positioning
    return html.Div([button, tooltip])
