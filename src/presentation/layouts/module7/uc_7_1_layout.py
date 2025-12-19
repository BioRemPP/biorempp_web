"""
UC-7.1 Layout - Faceted Heatmap of Predicted Compound Toxicity Profiles.

Provides layout for faceted heatmap visualization showing comprehensive
toxicological profiles across five major super-categories.

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


def create_uc_7_1_layout() -> dbc.Card:
    """
    Create UC-7.1 layout for faceted heatmap of toxicity profiles.

    Returns
    -------
    dbc.Card
        Card component with faceted heatmap showing toxicity profiles.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-7-1")

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
                                            "UC-7.1: Faceted Heatmap of Predicted Compound Toxicity Profiles",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-7.1",
                                        button_id="uc-7-1-download-btn",
                                        download_id="uc-7-1-download",
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
                    create_download_toast(toast_id="uc-7-1-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Faceted Heatmap Visualization
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container (Faceted Heatmap)
                                    html.Div(id="uc-7-1-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-7-1-accordion",
                            )
                        ],
                        id="uc-7-1-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-7-1-card",
    )
