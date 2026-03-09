"""
UC-1.5 Layout - Regulatory Compliance Scorecard.

Provides layout for heatmap scorecard showing compliance of microbial samples
with regulatory agency priorities.

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


def create_uc_1_5_layout() -> dbc.Card:
    """
    Create UC-1.5 layout for regulatory compliance scorecard.

    Returns
    -------
    dbc.Card
        Card component with heatmap showing compliance scores of samples
        with regulatory agency priorities.

    Notes
    -----
    - See official documentation for use case details
    """
    # Create informative panel from YAML configuration
    info_panel = create_panel_by_id("uc-1-5")

    # Assemble complete card layout
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
                                            "UC-1.5: Regulatory Compliance Scorecard",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Button(
                                                    "Methods",
                                                    id={
                                                        "type": "results-methods-link",
                                                        "index": "UC-1.5",
                                                    },
                                                    color="primary",
                                                    outline=False,
                                                    size="sm",
                                                    className="me-1",
                                                    n_clicks=0,
                                                    title=(
                                                        "View analytical workflow "
                                                        "for this use case"
                                                    ),
                                                ),
                                                width="auto",
                                            ),
                                            create_download_button(
                                                use_case_id="UC-1.5",
                                                button_id="uc-1-5-download-btn",
                                                download_id="uc-1-5-download",
                                                formats=["csv", "excel", "json"],
                                                button_text="Download Data",
                                            ),
                                        ],
                                        align="center",
                                        className="g-1 flex-nowrap",
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
                    # Informative panel (scientific context)
                    info_panel,
                    # Download toast notification
                    create_download_toast(toast_id="uc-1-5-download-toast"),
                    # Accordion: Heatmap Scorecard Visualization
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container with Loading Spinner
                                    dcc.Loading(
                                        id="uc-1-5-loading",
                                        type="circle",
                                        color="#0d6efd",
                                        children=html.Div(
                                            id="uc-1-5-chart",
                                            className="mt-3",
                                        ),
                                    )
                                ],
                                title="View Results",
                                item_id="uc-1-5-accordion",
                            )
                        ],
                        id="uc-1-5-accordion-group",
                        start_collapsed=True,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-1-5-card",
    )
