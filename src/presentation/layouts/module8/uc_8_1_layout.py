"""
UC-8.1 Layout - Minimal Sample Grouping for Complete Compound Coverage.

Provides layout for faceted scatter plot showing minimum functional
profiles required for complete compound coverage within chemical classes.

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


def create_uc_8_1_layout() -> dbc.Card:
    """
    Create UC-8.1 layout for minimal sample grouping analysis.

    Returns
    -------
    dbc.Card
        Card component with dropdown and faceted scatter for grouping analysis.

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
                                            "UC-8.1 | Minimal Sample Grouping for Complete "
                                            "Compound Coverage",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-8.1",
                                        button_id="uc-8-1-download-btn",
                                        download_id="uc-8-1-download",
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
                    # Download toast notifications
                    create_download_toast(toast_id="uc-8-1-download-toast"),
                    # Informative Panel (collapsible)
                    create_panel_by_id("uc-8-1"),
                    # Accordion for visualization
                    dbc.Accordion(
                        dbc.AccordionItem(
                            [
                                # Dropdown inside accordion
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            [
                                                dbc.Label(
                                                    "Filter by Compound Class:",
                                                    html_for="uc-8-1-compoundclass-dropdown",
                                                    className="fw-bold",
                                                ),
                                                dcc.Dropdown(
                                                    id="uc-8-1-compoundclass-dropdown",
                                                    placeholder="Select a Compound Class to generate visualization...",
                                                    clearable=False,
                                                    className="mb-3",
                                                ),
                                            ],
                                            md=6,
                                        ),
                                    ],
                                    className="mb-3",
                                ),
                                # Chart container
                                dcc.Loading(
                                    id="loading-uc-8-1",
                                    type="default",
                                    children=html.Div(
                                        id="uc-8-1-chart",
                                        style={"minHeight": "650px"},
                                    ),
                                ),
                            ],
                            title="View Results",
                            item_id="uc-8-1-accordion",
                        ),
                        id="uc-8-1-accordion-group",
                        start_collapsed=True,
                    ),
                ]
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-8-1-card",
    )
