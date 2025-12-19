"""
UC-8.6 Layout - Pathway-Centric Consortium Design by KO Coverage.

Provides layout for UpSet plot visualization enabling rational design of
microbial consortia for specific metabolic pathways.

Notes
-----
- See official documentation for detailed use case description
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite.use_cases import create_panel_by_id


def create_uc_8_6_layout() -> dbc.Card:
    """
    Create UC-8.6 layout for pathway-centric consortium design.

    Returns
    -------
    dbc.Card
        Card component with dropdown and UpSet plot for consortium design.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-8-6")

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
                                            "UC-8.6: Pathway-Centric Consortium Design by KO Coverage",
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
                                                id="uc-8-6-info-icon",
                                            ),
                                            dbc.Tooltip(
                                                "⚠️ Currently unavailable",
                                                target="uc-8-6-info-icon",
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
                                                        "HADEG",
                                                        id="uc-8-6-db-hadeg",
                                                        color="success",
                                                        outline=False,
                                                        size="sm",
                                                        className="me-1",
                                                    ),
                                                    dbc.Button(
                                                        "KEGG",
                                                        id="uc-8-6-db-kegg",
                                                        color="success",
                                                        outline=True,
                                                        size="sm",
                                                    ),
                                                ],
                                                className="mb-3",
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # Dropdown for Target Pathway Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Target Pathway:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-8-6-pathway-dropdown",
                                                placeholder="Choose a metabolic pathway...",
                                                className="mb-3",
                                                clearable=False,
                                                searchable=True,
                                                style={"width": "100%"},
                                            ),
                                            # Help text for database-specific information
                                            html.Div(
                                                id="uc-8-6-pathway-help-text",
                                                className="text-muted small mt-2",
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Chart Container (Rendered on Selection)
                                    # ========================================
                                    html.Div(
                                        html.P(
                                            "Please select a pathway from the dropdown to "
                                            "generate the UpSet plot.",
                                            className="text-muted text-center p-5",
                                        ),
                                        id="uc-8-6-chart",
                                        className="mt-4 border rounded p-3",
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-8-6-accordion",
                            )
                        ],
                        id="uc-8-6-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4",
        id="uc-8-6-card",
    )
