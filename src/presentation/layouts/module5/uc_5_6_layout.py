"""
UC-5.6 Layout - Compound-Compound Functional Similarity Network.

Provides layout for similarity network visualization showing functional
relationships between compounds based on shared gene interactions.

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


def create_uc_5_6_layout() -> dbc.Card:
    """
    Create UC-5.6 layout for compound-compound functional similarity network.

    Returns
    -------
    dbc.Card
        Card component with compound similarity network visualization.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-5-6")

    return dbc.Card(
        [
            # ========================================
            # Card Header
            # ========================================
            dbc.CardHeader(
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H5(
                                    [
                                        html.I(className="fas fa-chart-area me-2"),
                                        "UC-5.6: Compound-Compound Functional "
                                        "Similarity Network",
                                    ],
                                    className="mb-0",
                                )
                            ],
                            width="auto",
                        ),
                        dbc.Col(
                            [
                                create_download_button(
                                    use_case_id="UC-5.6",
                                    button_id="uc-5-6-download-btn",
                                    download_id="uc-5-6-download",
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
            ),
            # ========================================
            # Card Body
            # ========================================
            dbc.CardBody(
                [
                    # Informative panel (scientific context)
                    info_panel,
                    # Download toast notification
                    create_download_toast(toast_id="uc-5-6-download-toast"),
                    # ========================================
                    # Accordion: Chart Container
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # ========================================
                                    # Loading Spinner & Chart Container
                                    # ========================================
                                    dcc.Loading(
                                        id="uc-5-6-loading",
                                        type="circle",
                                        children=html.Div(
                                            id="uc-5-6-chart", className="mt-4"
                                        ),
                                    )
                                ],
                                title="View Results",
                                item_id="uc-5-6-accordion",
                            )
                        ],
                        id="uc-5-6-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-5-6-card",
    )
