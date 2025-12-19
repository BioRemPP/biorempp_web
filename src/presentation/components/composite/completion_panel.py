"""
Completion Panel - Composite UI Component.

Shows processing completion message and results navigation.

Functions
---------
create_completion_panel
    Create panel with View Results button (initially hidden)

Notes
-----
- Composite component
- Shows after successful processing
- Navigation button to results page
"""

import dash_bootstrap_components as dbc
from dash import html


def create_completion_panel() -> dbc.Card:
    """
    Create completion panel component.

    Returns
    -------
    dbc.Card
        Panel with View Results button (initially hidden)

    Notes
    -----
    - Hidden by default (display: none)
    - Shown via callback after processing completes
    - Button navigates to /results page
    - Uses dbc.Button with success color
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                [html.I(className="fas fa-check-circle me-2"), "Processing Complete"],
                className="bg-success text-white",
            ),
            dbc.CardBody(
                [
                    html.Div(id="completion-message", className="mb-3"),
                    html.Div(
                        [
                            dbc.Button(
                                [
                                    html.I(className="fas fa-chart-bar me-2"),
                                    "View Results",
                                ],
                                id="view-results-btn",
                                color="success",
                                size="lg",
                                href="/results",
                                className="w-100",
                            )
                        ],
                        className="d-grid",
                    ),
                ]
            ),
        ],
        id="completion-panel",
        style={"display": "none"},
        className="mb-4",
    )
