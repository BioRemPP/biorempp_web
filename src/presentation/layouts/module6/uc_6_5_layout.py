"""
UC-6.5 Layout - Chemical-Enzymatic Landscape by Substrate Scope.

Provides layout for treemap visualization showing hierarchical structure
from chemical classes through enzymes to genes by compound count.

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


def create_uc_6_5_layout() -> dbc.Card:
    """
    Create UC-6.5 layout for chemical-enzymatic landscape visualization.

    Returns
    -------
    dbc.Card
        Card component with treemap showing chemo-enzymatic hierarchy.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-6-5")

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
                                            "UC-6.5: Chemical-Enzymatic Landscape by "
                                            "Substrate Scope",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-6.5",
                                        button_id="uc-6-5-download-btn",
                                        download_id="uc-6-5-download",
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
                    create_download_toast(toast_id="uc-6-5-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Treemap Visualization
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container (Treemap)
                                    html.Div(id="uc-6-5-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-6-5-accordion",
                            )
                        ],
                        id="uc-6-5-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-6-5-card",
    )
