"""
UC-4.3 Layout - Interactive Sample Comparison by Pathway.

Provides layout for radar chart showing comparative functional richness
of samples for a selected metabolic pathway.

Notes
-----
- See official documentation for detailed use case description
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite.use_cases import create_panel_by_id


def create_uc_4_3_layout() -> dbc.Card:
    """
    Create UC-4.3 layout for sample comparison by pathway.

    Returns
    -------
    dbc.Card
        Card component with dropdown and radar chart.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-4-3")

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
                                                "UC-4.3: Interactive Comparison of Sample Performance "
                                                "by Pathway (KEGG)"
                                            ),
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    html.Span(
                                        [
                                            html.I(
                                                className="fas fa-info-circle text-info",
                                                id="uc-4-3-info-icon",
                                            ),
                                            dbc.Tooltip(
                                                "ℹ️ Same data as UC-4.1",
                                                target="uc-4-3-info-icon",
                                                placement="left",
                                            ),
                                        ]
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
                                                id="uc-4-3-pathway-dropdown",
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
                                        id="uc-4-3-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-4-3-accordion",
                            )
                        ],
                        id="uc-4-3-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-4-3-card",
    )
