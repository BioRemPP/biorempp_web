"""
UC-4.8 Layout - Interactive Gene Inventory Explorer by Sample and Gene.

Provides layout for scatter plot showing genetic inventory through
flexible dual-filter dropdown menus.

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


def create_uc_4_8_layout() -> dbc.Card:
    """
    Create UC-4.8 layout for gene inventory explorer.

    Returns
    -------
    dbc.Card
        Card component with dual dropdowns and scatter plot.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-4-8")

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
                                                "UC-4.8: Interactive Gene Inventory Explorer by Sample and "
                                                "Gene Symbol"
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
                                        use_case_id="UC-4.8",
                                        button_id="uc-4-8-download-btn",
                                        download_id="uc-4-8-download",
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
                    create_download_toast(toast_id="uc-4-8-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Information Message
                                    html.Div(
                                        [
                                            html.I(className="fas fa-info-circle me-2"),
                                            html.Span(
                                                (
                                                    "Use one or both dropdown menus to filter genetic inventory. "
                                                    "Select a sample to see all its genes, a gene to see all "
                                                    "samples that possess it, or both to validate a specific "
                                                    "gene's presence in a sample."
                                                ),
                                                className="text-muted",
                                            ),
                                        ],
                                        className="alert alert-info mb-4",
                                    ),
                                    # Dropdown Section - Two Filters
                                    dbc.Row(
                                        [
                                            # Dropdown 1: Sample
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Select Sample (Optional):",
                                                        className="fw-bold mb-2",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="uc-4-8-sample-dropdown",
                                                        placeholder="Choose a sample to filter...",
                                                        className="mb-3",
                                                        clearable=True,
                                                        searchable=True,
                                                        style={"width": "100%"},
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                            # Dropdown 2: Gene Symbol
                                            dbc.Col(
                                                [
                                                    html.Label(
                                                        "Select Gene Symbol (Optional):",
                                                        className="fw-bold mb-2",
                                                    ),
                                                    dcc.Dropdown(
                                                        id="uc-4-8-gene-dropdown",
                                                        placeholder="Choose a gene to filter...",
                                                        className="mb-3",
                                                        clearable=True,
                                                        searchable=True,
                                                        style={"width": "100%"},
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # Note about data requirements
                                    # ========================================
                                    # Chart Container (Rendered on Selection)
                                    # ========================================
                                    html.Div(
                                        id="uc-4-8-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-4-8-accordion",
                            )
                        ],
                        id="uc-4-8-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-4-8-card",
    )
