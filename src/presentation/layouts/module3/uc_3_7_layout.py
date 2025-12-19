"""
UC-3.7 Layout - Compound Co-occurrence Patterns Across Samples.

Provides layout for correlogram visualization showing pairwise co-occurrence
relationships between chemical compounds across microbial samples.

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


def create_uc_3_7_layout() -> dbc.Card:
    """
    Create UC-3.7 layout for compound co-occurrence pattern analysis.

    Returns
    -------
    dbc.Card
        Card component with correlogram showing compound-compound co-occurrence.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-3-7")

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
                                            "UC-3.7: Compound Co-occurrence Patterns Across Samples",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                                className="flex-grow-1",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-3.7",
                                        button_id="uc-3-7-download-btn",
                                        download_id="uc-3-7-download",
                                        formats=["csv", "excel", "json"],
                                        button_text="Download Data",
                                    )
                                ],
                                width="auto",
                            ),
                        ],
                        align="center",
                        className="g-2",
                    )
                ]
            ),
            # ========================================
            # Card Body
            # ========================================
            dbc.CardBody(
                [
                    # Download Toast Notification
                    html.Div(
                        dbc.Toast(
                            id="uc-3-7-download-toast",
                            header="Download Status",
                            is_open=False,
                            dismissable=True,
                            duration=4000,
                            icon="info",
                            style={
                                "position": "fixed",
                                "top": 66,
                                "right": 10,
                                "width": 350,
                                "zIndex": 9999,
                            },
                        )
                    ),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Correlogram Visualization
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container (Correlogram)
                                    html.Div(id="uc-3-7-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-3-7-accordion",
                            )
                        ],
                        id="uc-3-7-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-3-7-card",
    )
