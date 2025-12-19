"""
UC-4.2 Layout - Interactive Sample Ranking by Pathway Richness.

Provides layout for vertical bar chart ranking samples by unique KO counts
within a selected metabolic pathway.

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


def create_uc_4_2_layout() -> dbc.Card:
    """
    Create UC-4.2 layout for sample ranking by pathway.

    Returns
    -------
    dbc.Card
        Card component with dropdown and vertical bar chart.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-4-2")

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
                                            (
                                                "UC-4.2: Interactive Ranking of Samples "
                                                "by Pathway Richness (KEGG)"
                                            ),
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-4.2",
                                        button_id="uc-4-2-download-btn",
                                        download_id="uc-4-2-download",
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
                    # Informative panel (scientific context)
                    info_panel,
                    # Toast notification for download status
                    create_download_toast("uc-4-2-download-toast"),
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Dropdown for Pathway Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Metabolic Pathway:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-4-2-pathway-dropdown",
                                                placeholder="Choose a pathway to analyze...",
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
                                    html.Div(
                                        id="uc-4-2-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-4-2-accordion",
                            )
                        ],
                        id="uc-4-2-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-4-2-card",
    )
