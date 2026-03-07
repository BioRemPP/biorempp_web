"""
UC-5.3 Layout - Regulatory Relevance of Samples.

Provides layout for chord diagram visualization showing interaction strength
between microbial samples and regulatory agencies.

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


def create_uc_5_3_layout() -> dbc.Card:
    """
    Create UC-5.3 layout for regulatory relevance analysis.

    Returns
    -------
    dbc.Card
        Card component with dropdown and chord diagram for agency filtering.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-5-3")

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
                                            "UC-5.3: Regulatory Relevance of Samples",
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
                                                    id={"type": "results-methods-link", "index": "UC-5.3"},
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
                                                use_case_id="UC-5.3",
                                                button_id="uc-5-3-download-btn",
                                                download_id="uc-5-3-download",
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
            # ========================================
            # Card Body
            # ========================================
            dbc.CardBody(
                [
                    # Download Toast Notification
                    create_download_toast(toast_id="uc-5-3-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Dropdown for Regulatory Agency Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Regulatory Agency:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-5-3-agency-dropdown",
                                                placeholder="Choose a regulatory agency...",
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
                                        id="uc-5-3-loading",
                                        type="circle",
                                        color="#0d6efd",
                                        children=html.Div(
                                            id="uc-5-3-chart",
                                            className="mt-4",
                                        ),
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-5-3-accordion",
                            )
                        ],
                        id="uc-5-3-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-5-3-card",
    )
