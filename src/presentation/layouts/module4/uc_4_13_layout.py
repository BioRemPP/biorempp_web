"""
UC-4.13 Layout - Interactive Genetic Profile by Compound Pathway.

Provides layout for heatmap showing gene-sample associations with
unique KO counts for selected compound pathways.

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


def create_uc_4_13_layout() -> dbc.Card:
    """
    Create UC-4.13 layout for genetic profile by compound pathway.

    Returns
    -------
    dbc.Card
        Card component with dropdown and heatmap.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-4-13")

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
                                        (
                                            "UC-4.13: Interactive Genetic Profile by Compound Pathway "
                                            "(HADEG)"
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
                                    use_case_id="UC-4.13",
                                    button_id="uc-4-13-download-btn",
                                    download_id="uc-4-13-download",
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
                    create_download_toast(toast_id="uc-4-13-download-toast"),
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Dropdown for Compound Pathway Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Compound Pathway:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-4-13-compound-pathway-dropdown",
                                                placeholder="Choose a compound pathway to analyze...",
                                                className="mb-3",
                                                clearable=False,
                                                searchable=True,
                                                style={"width": "100%"},
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Chart Container (Rendered on Selection)
                                    # ========================================
                                    html.Div(
                                        id="uc-4-13-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-4-13-accordion",
                            )
                        ],
                        id="uc-4-13-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-4-13-card",
    )
