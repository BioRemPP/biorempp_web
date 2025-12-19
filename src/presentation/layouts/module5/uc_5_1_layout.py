"""
UC-5.1 Layout - Sample-Compound Class Interaction Strength.

Provides layout for chord diagram visualization showing interaction strength
between microbial samples and chemical compound classes.

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


def create_uc_5_1_layout() -> dbc.Card:
    """
    Create UC-5.1 layout for sample-compound class interaction analysis.

    Returns
    -------
    dbc.Card
        Card component with chord diagram showing sample-compound interactions.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-5-1")

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
                                            "UC-5.1: Sample - Compound Class Interaction Strength",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-5.1",
                                        button_id="uc-5-1-download-btn",
                                        download_id="uc-5-1-download",
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
                    # Toast notification for download status
                    create_download_toast("uc-5-1-download-toast"),
                    # ========================================
                    # Accordion: Chord Diagram Visualization
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container (Chord Diagram)
                                    html.Div(id="uc-5-1-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-5-1-accordion",
                            )
                        ],
                        id="uc-5-1-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-5-1-card",
    )
