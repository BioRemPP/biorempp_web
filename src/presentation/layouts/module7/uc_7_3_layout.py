"""
UC-7.3 Layout - Mapping of Genetic Response to High-Priority Threats.

Provides layout for heatmap visualization showing genetic response of
microbial samples to high-priority toxicological threats.

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


def create_uc_7_3_layout() -> dbc.Card:
    """
    Create UC-7.3 layout for genetic response mapping.

    Returns
    -------
    dbc.Card
        Card component with dropdown and heatmap for threat analysis.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-7-3")

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
                                        "UC-7.3: Mapping of Genetic Response to High-Priority Threats",
                                    ],
                                    className="mb-0",
                                )
                            ],
                            width="auto",
                        ),
                        dbc.Col(
                            [
                                create_download_button(
                                    use_case_id="UC-7.3",
                                    button_id="uc-7-3-download-btn",
                                    download_id="uc-7-3-download",
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
                    create_download_toast(toast_id="uc-7-3-download-toast"),
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Dropdown for Threat Super-Category Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Threat Super-Category:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-7-3-category-dropdown",
                                                placeholder="Choose a threat category...",
                                                className="mb-3",
                                                clearable=False,
                                                searchable=True,
                                                style={"width": "100%"},
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Chart Container (Rendered on Selection)
                                    # ========================================
                                    dcc.Loading(
                                        id="uc-7-3-loading",
                                        type="default",
                                        children=html.Div(
                                            id="uc-7-3-chart", className="mt-4"
                                        ),
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-7-3-item",
                            )
                        ],
                        id="uc-7-3-accordion",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-7-3-card",
    )
