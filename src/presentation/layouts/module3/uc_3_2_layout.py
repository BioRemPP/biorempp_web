"""
UC-3.2 Layout - PCA Sample Relationships by Chemical Profile.

Provides layout for PCA scatter plot visualization showing sample
relationships and clustering patterns based on chemical profiles.

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


def create_uc_3_2_layout() -> dbc.Card:
    """
    Create UC-3.2 layout for PCA sample relationships by chemical profile.

    Returns
    -------
    dbc.Card
        Card component with PCA scatter plot showing sample relationships.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-3-2")

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
                                            "UC-3.2: PCA - Sample Relationships by Chemical Profile",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-3.2",
                                        button_id="uc-3-2-download-btn",
                                        download_id="uc-3-2-download",
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
                    # Download toast notification
                    create_download_toast(toast_id="uc-3-2-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: PCA Scatter Plot Visualization
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container (PCA Scatter Plot)
                                    html.Div(id="uc-3-2-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-3-2-accordion",
                            )
                        ],
                        id="uc-3-2-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-3-2-card",
    )
