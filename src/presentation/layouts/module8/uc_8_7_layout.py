"""
UC-8.7 Layout - Intersection of Genes Across Samples.

Provides layout for UpSet plot visualization enabling multi-sample gene set
intersection analysis to identify core genomes and functional overlap patterns.

Notes
-----
- See official documentation for detailed use case description
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite.use_cases import create_panel_by_id


def create_uc_8_7_layout() -> dbc.Card:
    """
    Create UC-8.7 layout for gene intersection analysis.

    Returns
    -------
    dbc.Card
        Card component with multi-select dropdown and UpSet plot.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-8-7")

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
                                            "UC-8.7: Intersection of Genes Across Samples",
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
                                                className="fas fa-exclamation-triangle text-warning",
                                                id="uc-8-7-info-icon",
                                            ),
                                            dbc.Tooltip(
                                                "⚠️ Currently unavailable",
                                                target="uc-8-7-info-icon",
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
                                    # Sample Selection (Multi-Select Dropdown)
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Samples for Intersection Analysis:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-8-7-sample-dropdown",
                                                placeholder="Choose 2 or more samples...",
                                                multi=True,
                                                className="mb-3",
                                                clearable=True,
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
                                        html.P(
                                            "Please select at least 2 samples from the dropdown "
                                            "to generate the UpSet plot.",
                                            className="text-muted text-center p-5",
                                        ),
                                        id="uc-8-7-chart",
                                        className="mt-4 border rounded p-3",
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-8-7-accordion",
                            )
                        ],
                        id="uc-8-7-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4",
        id="uc-8-7-card",
    )
