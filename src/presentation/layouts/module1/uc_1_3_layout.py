"""
UC-1.3 Layout - Proportional Contribution of References.

Provides layout for 100% stacked bar chart showing proportional contributions
of regulatory agencies to total unique KO diversity.

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


def create_uc_1_3_layout() -> dbc.Card:
    """
    Create UC-1.3 layout for proportional contribution analysis.

    Returns
    -------
    dbc.Card
        Card component with 100% stacked bar chart showing proportional
        contributions of regulatory agencies to total KO diversity.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-1-3")

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
                                            "UC-1.3: Proportional Contribution of Reference "
                                            "Agencies",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-1.3",
                                        button_id="uc-1-3-download-btn",
                                        download_id="uc-1-3-download",
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
                    create_download_toast(toast_id="uc-1-3-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Stacked Bar Chart Visualization
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container with Loading Spinner
                                    dcc.Loading(
                                        id="uc-1-3-loading",
                                        type="circle",
                                        color="#0d6efd",
                                        children=html.Div(
                                            id="uc-1-3-chart",
                                            className="mt-3",
                                        ),
                                    )
                                ],
                                title="View Results",
                                item_id="uc-1-3-accordion",
                            )
                        ],
                        id="uc-1-3-accordion-group",
                        start_collapsed=True,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-1-3-card",
    )
