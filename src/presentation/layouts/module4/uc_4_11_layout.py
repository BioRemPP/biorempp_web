"""
UC-4.11 Layout - Global Hierarchical View of Genetic Diversity in HADEG.

Provides layout for sunburst chart showing hierarchical distribution
of genetic diversity across HADEG database pathways.

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


def create_uc_4_11_layout() -> dbc.Card:
    """
    Create UC-4.11 layout for global genetic diversity hierarchy.

    Returns
    -------
    dbc.Card
        Card component with sunburst chart.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-4-11")

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
                                                "UC-4.11: Global Hierarchical View of Genetic Diversity "
                                                "in HADEG Pathways (HADEG)"
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
                                        use_case_id="UC-4.11",
                                        button_id="uc-4-11-download-btn",
                                        download_id="uc-4-11-download",
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
                    create_download_toast("uc-4-11-download-toast"),
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
                                                        id="uc-4-11-db-biorempp",
                                                        color="success",
                                                        outline=False,
                                                        size="sm",
                                                        className="me-1",
                                                    ),
                                                    dbc.Button(
                                                        "HADEG",
                                                        id="uc-4-11-db-hadeg",
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
                                    # Informational Note
                                    html.Div(
                                        [
                                            html.P(
                                                [
                                                    html.Strong(
                                                        "About this visualization:"
                                                    ),
                                                    " This sunburst chart displays the hierarchical "
                                                    "structure of genetic diversity. Select a database "
                                                    "above to view different hierarchies.",
                                                ],
                                                className="mb-2",
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Chart Container (Rendered on Accordion Open)
                                    # ========================================
                                    html.Div(
                                        id="uc-4-11-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-4-11-accordion",
                            )
                        ],
                        id="uc-4-11-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-4-11-card",
    )
