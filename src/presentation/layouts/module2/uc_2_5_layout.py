"""
UC-2.5 Layout - Distribution of KO Across Samples.

Provides layout for combined box plot and scatter visualization showing
statistical distribution of functional richness across samples.

Notes
-----
- See official documentation for detailed use case description
"""

import dash_bootstrap_components as dbc
from dash import html

from src.presentation.components.composite.use_cases import create_panel_by_id


def create_uc_2_5_layout() -> dbc.Card:
    """
    Create UC-2.5 layout for KO distribution analysis.

    Returns
    -------
    dbc.Card
        Card component with database selection and combined box + scatter plot.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-2-5")

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
                                            "UC-2.5: Distribution of KO Across Samples",
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
                                                id="uc-2-5-info-icon",
                                            ),
                                            dbc.Tooltip(
                                                "ℹ️ Same data as UC-2.1",
                                                target="uc-2-5-info-icon",
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
                                                        id="uc-2-5-db-biorempp",
                                                        color="primary",
                                                        outline=False,
                                                        size="sm",
                                                        className="me-1",
                                                    ),
                                                    dbc.Button(
                                                        "HADEG",
                                                        id="uc-2-5-db-hadeg",
                                                        color="primary",
                                                        outline=True,
                                                        size="sm",
                                                        className="me-1",
                                                    ),
                                                    dbc.Button(
                                                        "KEGG",
                                                        id="uc-2-5-db-kegg",
                                                        color="primary",
                                                        outline=True,
                                                        size="sm",
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Chart Container (Rendered on Selection)
                                    # ========================================
                                    html.Div(
                                        id="uc-2-5-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-2-5-item",
                            )
                        ],
                        id="uc-2-5-accordion",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-2-5-card",
    )
