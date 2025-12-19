"""
UC-2.2 Layout - Ranking of Samples by Compound Richness.

Provides layout for bar chart visualization showing compound diversity
across samples by counting unique compound identifiers.

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


def create_uc_2_2_layout() -> dbc.Card:
    """
    Create UC-2.2 layout for sample ranking by compound richness.

    Returns
    -------
    dbc.Card
        Card component with database selection, range slider, and bar chart.

    Notes
    -----
    - See official documentation for use case details
    """
    # Informative panel with scientific context
    info_panel = create_panel_by_id("uc-2-2")

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
                                            "UC-2.2: Ranking of Samples by Compound Richness",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-2.2",
                                        button_id="uc-2-2-download-btn",
                                        download_id="uc-2-2-download",
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
                    # Toast notification for download feedback
                    create_download_toast("uc-2-2-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Database Selection (Button Group)
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Database:",
                                                className="fw-bold mb-2",
                                            ),
                                            dbc.ButtonGroup(
                                                [
                                                    dbc.Button(
                                                        "BioRemPP",
                                                        id="uc-2-2-db-biorempp",
                                                        color="primary",
                                                        outline=False,
                                                        size="sm",
                                                        className="me-1",
                                                    ),
                                                    dbc.Tooltip(
                                                        "KEGG database does not contain compound data",
                                                        target="uc-2-2-db-kegg",
                                                        placement="top",
                                                    ),
                                                    dbc.Button(
                                                        "KEGG",
                                                        id="uc-2-2-db-kegg",
                                                        color="secondary",
                                                        outline=True,
                                                        size="sm",
                                                        disabled=True,
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Range Slider for Compound Count Filtering
                                    # ========================================
                                    html.Div(
                                        [
                                            html.Label(
                                                "Filter by Compound Count Range:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.RangeSlider(
                                                id="uc-2-2-range-slider",
                                                min=0,
                                                max=10,
                                                step=1,
                                                value=[0, 10],
                                                marks={0: "0", 10: "10"},
                                                tooltip={
                                                    "placement": "bottom",
                                                    "always_visible": True,
                                                },
                                                className="mb-4",
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Chart Container (Rendered on Demand)
                                    # ========================================
                                    html.Div(
                                        id="uc-2-2-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-2-2-item",
                            )
                        ],
                        id="uc-2-2-accordion",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-2-2-card",
    )
