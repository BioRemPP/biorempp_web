"""
UC-7.4 Layout - Toxicity Score Distribution by Endpoint Category.

Provides layout for box plot visualization showing statistical distribution
of toxicity scores across endpoints within toxicological domains.

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


def create_uc_7_4_layout() -> dbc.Card:
    """
    Create UC-7.4 layout for toxicity score distribution analysis.

    Returns
    -------
    dbc.Card
        Card component with dropdown and box plots for endpoint filtering.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-7-4")

    return dbc.Card(
        [
            # ========================================
            # Card Header (Title + Download Button)
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
                                                "UC-7.4: Toxicity Score Distribution by "
                                                "Endpoint Category"
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
                                        use_case_id="UC-7.4",
                                        button_id="uc-7-4-download-btn",
                                        download_id="uc-7-4-download",
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
                    # Toast notification for download feedback
                    create_download_toast("uc-7-4-download-toast"),
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Dropdown for Toxicity Super-Category Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Toxicity Super-Category:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-7-4-category-dropdown",
                                                placeholder="Choose a toxicity domain...",
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
                                        id="uc-7-4-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-7-4-item",
                            )
                        ],
                        id="uc-7-4-accordion",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-7-4-card",
    )
