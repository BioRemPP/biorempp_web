"""
UC-8.3 Layout - Compound-Specific KO Completeness Scorecard.

Provides layout for heatmap scorecard showing completeness of functional
genetic toolkits (KOs) for each sample across individual chemical compounds.

Notes
-----
- See official documentation for detailed use case description
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite.use_cases import create_panel_by_id
from src.presentation.components.download_component import (
    create_download_button,
    create_download_toast,
)


def create_uc_8_3_layout() -> dbc.Card:
    """
    Create UC-8.3 layout for compound-specific completeness scorecard.

    Returns
    -------
    dbc.Card
        Card component with heatmap showing compound-specific scores.

    Notes
    -----
    - See official documentation for use case details
    """
    return dbc.Card(
        [
            # Card Header
            dbc.CardHeader(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H5(
                                        [
                                            html.I(className="fas fa-chart-area me-2"),
                                            "UC-8.3 | Compound-Specific KO Completeness Scorecard",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-8.3",
                                        button_id="uc-8-3-download-btn",
                                        download_id="uc-8-3-download",
                                        formats=["csv", "excel", "json"],
                                        button_text="Download Data",
                                    )
                                ],
                                width="auto",
                                className="ms-auto",
                            ),
                        ],
                        align="center",
                        className="g-0",
                    )
                ]
            ),
            # Card Body
            dbc.CardBody(
                [
                    # Informative Panel (collapsible)
                    create_panel_by_id("uc-8-3"),
                    # Download toast notification
                    create_download_toast(toast_id="uc-8-3-download-toast"),
                    # Accordion for visualization
                    dbc.Accordion(
                        dbc.AccordionItem(
                            [
                                dcc.Loading(
                                    id="loading-uc-8-3",
                                    type="default",
                                    children=html.Div(
                                        id="uc-8-3-chart",
                                        style={"minHeight": "650px"},
                                    ),
                                )
                            ],
                            title="View Results",
                            item_id="uc-8-3-accordion",
                        ),
                        id="uc-8-3-accordion-group",
                        start_collapsed=True,
                    ),
                ]
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-8-3-card",
    )
