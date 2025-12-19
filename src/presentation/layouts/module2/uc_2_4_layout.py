"""
UC-2.4 Layout - Ranking of Compounds by Genetic Interaction.

Provides layout for bar chart visualization showing compound-gene
interactions filtered by chemical class.

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


def create_uc_2_4_layout() -> dbc.Card:
    """
    Create UC-2.4 layout for compound ranking by genetic interaction.

    Returns
    -------
    dbc.Card
        Card component with dropdown selector for chemical class filtering.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-2-4")

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
                                                "UC-2.4: Ranking of Compounds by Genetic Interaction "
                                                "within Chemical Classes"
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
                                        use_case_id="UC-2.4",
                                        button_id="uc-2-4-download-btn",
                                        download_id="uc-2-4-download",
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
                    create_download_toast("uc-2-4-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Dropdown for Chemical Class Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Compound Class:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-2-4-class-dropdown",
                                                placeholder="Choose a chemical class...",
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
                                        id="uc-2-4-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-2-4-item",
                            )
                        ],
                        id="uc-2-4-accordion",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-2-4-card",
    )
