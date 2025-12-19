"""
UC-6.1 Layout - Regulatory to Molecular Interaction Flow.

Provides layout for Sankey diagram visualization showing end-to-end flow
from regulatory agencies through samples and genes to compounds.

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


def create_uc_6_1_layout() -> dbc.Card:
    """
    Create UC-6.1 layout for regulatory-to-molecular interaction flow.

    Returns
    -------
    dbc.Card
        Card component with Sankey diagram showing interaction flow.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-6-1")

    return dbc.Card(
        [
            # ========================================
            # Card Header
            # ========================================
            dbc.CardHeader(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H5(
                                        [
                                            html.I(className="fas fa-chart-area me-2"),
                                            "UC-6.1: Regulatory to Molecular Interaction Flow",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-6.1",
                                        button_id="uc-6-1-download-btn",
                                        download_id="uc-6-1-download",
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
            # ========================================
            # Card Body
            # ========================================
            dbc.CardBody(
                [
                    # Download toast notification
                    create_download_toast(toast_id="uc-6-1-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
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
                                        id="uc-6-1-loading",
                                        type="circle",
                                        children=html.Div(
                                            id="uc-6-1-chart", className="mt-4"
                                        ),
                                    )
                                ],
                                title="View Results",
                                item_id="uc-6-1-accordion",
                            )
                        ],
                        id="uc-6-1-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-6-1-card",
    )
