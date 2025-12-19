"""
UC-3.1 Layout - PCA Sample Relationships by KO Profile.

Provides layout for PCA scatter plot visualization showing sample
relationships and clustering patterns based on KO profiles.

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


def create_uc_3_1_layout() -> dbc.Card:
    """
    Create UC-3.1 layout for PCA sample relationships analysis.

    Returns
    -------
    dbc.Card
        Card component with PCA scatter plot showing sample relationships.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-3-1")

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
                                        "UC-3.1: PCA - Sample Relationships by "
                                        "KO Profile",
                                    ],
                                    className="mb-0",
                                )
                            ],
                            width="auto",
                        ),
                        dbc.Col(
                            [
                                create_download_button(
                                    use_case_id="UC-3.1",
                                    button_id="uc-3-1-download-btn",
                                    download_id="uc-3-1-download",
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
                    create_download_toast(toast_id="uc-3-1-download-toast"),
                    # ========================================
                    # Accordion: PCA Scatter Plot Visualization
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container (PCA Scatter Plot)
                                    html.Div(id="uc-3-1-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-3-1-accordion",
                            )
                        ],
                        id="uc-3-1-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-3-1-card",
    )
