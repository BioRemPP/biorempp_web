"""
UC-4.10 Layout - Genetic Diversity of Enzymatic Activities Across Samples.

Provides layout for bubble chart showing genetic diversity (unique gene count)
across samples and enzymatic activities.

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


def create_uc_4_10_layout() -> dbc.Card:
    """
    Create UC-4.10 layout for genetic diversity of enzymatic activities.

    Returns
    -------
    dbc.Card
        Card component with automatic bubble chart rendering.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-4-10")

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
                                                "UC-4.10: Genetic Diversity of Enzymatic Activities "
                                                "Across Samples"
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
                                        use_case_id="UC-4.10",
                                        button_id="uc-4-10-download-btn",
                                        download_id="uc-4-10-download",
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
                    # Download toast notifications
                    create_download_toast(toast_id="uc-4-10-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Information Message (No Dropdown Required)
                                    html.Div(
                                        [
                                            html.I(className="fas fa-info-circle me-2"),
                                            html.Span(
                                                (
                                                    "This visualization automatically displays genetic "
                                                    "diversity across all enzyme activities and samples. "
                                                    "No filtering is required."
                                                ),
                                                className="text-muted",
                                            ),
                                        ],
                                        className="alert alert-info mb-4",
                                    ),
                                    # Note about data requirements
                                    # ========================================
                                    # Chart Container (Rendered on Accordion Open)
                                    # ========================================
                                    html.Div(
                                        id="uc-4-10-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-4-10-accordion",
                            )
                        ],
                        id="uc-4-10-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-4-10-card",
    )
