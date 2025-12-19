"""
UC-3.6 Layout - Gene Co-occurrence Patterns Across Samples.

Provides layout for correlogram visualization showing pairwise co-occurrence
relationships between gene symbols across microbial samples.

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


def create_uc_3_6_layout() -> dbc.Card:
    """
    Create UC-3.6 layout for gene co-occurrence pattern analysis.

    Returns
    -------
    dbc.Card
        Card component with correlogram showing gene-gene co-occurrence.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-3-6")

    return dbc.Card(
        [
            # ========================================
            # Card Header with Download Button
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
                                            "UC-3.6: Gene Co-occurrence Patterns Across Samples",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-3.6",
                                        button_id="uc-3-6-download-btn",
                                        download_id="uc-3-6-download",
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
                    create_download_toast("uc-3-6-download-toast"),
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
                                    html.Div(id="uc-3-6-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-3-6-accordion",
                            )
                        ],
                        id="uc-3-6-accordion-group",
                        start_collapsed=True,
                        active_item=None,
                    ),
                ]
            ),
        ],
        className="mb-4 shadow-sm",
        id="uc-3-6-card",
    )
