"""
UC-5.4 Layout - Gene-Compound Interaction Network.

Provides layout for bipartite network visualization showing interactions
between gene symbols and compound names.

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


def create_uc_5_4_layout() -> dbc.Card:
    """
    Create UC-5.4 layout for gene-compound interaction network.

    Returns
    -------
    dbc.Card
        Card component with bipartite network visualization.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-5-4")

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
                                        "UC-5.4: Gene-Compound Interaction Network",
                                    ],
                                    className="mb-0",
                                )
                            ],
                            width="auto",
                        ),
                        dbc.Col(
                            [
                                create_download_button(
                                    use_case_id="UC-5.4",
                                    button_id="uc-5-4-download-btn",
                                    download_id="uc-5-4-download",
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
                    create_download_toast(toast_id="uc-5-4-download-toast"),
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
                                        id="uc-5-4-loading",
                                        type="circle",
                                        children=html.Div(
                                            id="uc-5-4-chart", className="mt-4"
                                        ),
                                    )
                                ],
                                title="View Results",
                                item_id="uc-5-4-accordion",
                            )
                        ],
                        id="uc-5-4-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-5-4-card",
    )
