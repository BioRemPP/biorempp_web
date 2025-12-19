"""
UC-1.6 Layout - Sample-Agency Functional Potential Heatmap.

Provides layout for heatmap showing unique KO counts at the intersection
of samples and regulatory agencies.

Notes
-----
- See official documentation for detailed use case description
"""

import dash_bootstrap_components as dbc
from dash import html

from src.presentation.components.composite.use_cases import create_panel_by_id
from src.presentation.components.download_component import (
    create_download_button,
    create_download_toast,
)


def create_uc_1_6_layout() -> dbc.Card:
    """
    Create UC-1.6 layout for sample-agency functional potential heatmap.

    Returns
    -------
    dbc.Card
        Card component with heatmap showing unique KO counts at the
        intersection of samples and regulatory agencies.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-1-6")

    return dbc.Card(
        [
            # ========================================
            # Card Header
            # ========================================
            dbc.CardHeader(
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                html.H5(
                                    [
                                        html.I(className="fas fa-chart-area me-2"),
                                        "UC-1.6: Sample-Agency Functional Potential Heatmap",
                                    ],
                                    className="mb-0",
                                )
                            ],
                            width="auto",
                        ),
                        dbc.Col(
                            [
                                create_download_button(
                                    use_case_id="UC-1.6",
                                    button_id="uc-1-6-download-btn",
                                    download_id="uc-1-6-download",
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
            ),
            # ========================================
            # Card Body
            # ========================================
            dbc.CardBody(
                [
                    # Informative panel (scientific context)
                    info_panel,
                    # Download toast notification
                    create_download_toast(toast_id="uc-1-6-download-toast"),
                    # ========================================
                    # Accordion: Heatmap Visualization
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container (Heatmap)
                                    html.Div(id="uc-1-6-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-1-6-accordion",
                            )
                        ],
                        id="uc-1-6-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-1-6-card",
    )
