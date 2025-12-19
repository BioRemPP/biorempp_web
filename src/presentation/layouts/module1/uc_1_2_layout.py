"""
UC-1.2 Layout - Regulatory Agency Compound Overlap Analysis.

Provides layout for UpSet plot visualization showing compound overlaps
across different environmental regulatory agencies.

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


def create_uc_1_2_layout() -> dbc.Card:
    """
    Create UC-1.2 layout for regulatory agency compound overlap analysis.

    Returns
    -------
    dbc.Card
        Card component with UpSet plot showing compound overlaps across
        regulatory agencies.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-1-2")

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
                                            "UC-1.2: Regulatory Agency Compound Overlap",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-1.2",
                                        button_id="uc-1-2-download-btn",
                                        download_id="uc-1-2-download",
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
                    # Toast notification for download feedback
                    create_download_toast("uc-1-2-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: UpSet Plot Visualization
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Chart Container (UpSet Plot)
                                    html.Div(id="uc-1-2-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-1-2-accordion",
                            )
                        ],
                        id="uc-1-2-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-1-2-card",
    )
