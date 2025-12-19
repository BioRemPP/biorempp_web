"""
UC-7.2 Layout - Concordance Between Predicted Risk and Regulatory Focus.

Provides layout for chord diagram visualization showing overlap between
regulatory-monitored compounds and high-risk predictions.

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


def create_uc_7_2_layout() -> dbc.Card:
    """
    Create UC-7.2 layout for risk-regulatory concordance analysis.

    Returns
    -------
    dbc.Card
        Card component with dropdown and chord diagram for threshold filtering.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-7-2")

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
                                            "UC-7.2: Concordance Between Predicted Risk and Regulatory Focus",
                                        ],
                                        className="mb-0",
                                    )
                                ],
                                width="auto",
                            ),
                            dbc.Col(
                                [
                                    create_download_button(
                                        use_case_id="UC-7.2",
                                        button_id="uc-7-2-download-btn",
                                        download_id="uc-7-2-download",
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
                    # Download Toast Notification
                    create_download_toast(toast_id="uc-7-2-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Dropdown for Toxicity Threshold Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Toxicity Threshold:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-7-2-threshold-dropdown",
                                                options=[
                                                    {
                                                        "label": "High Risk (≥0.7)",
                                                        "value": 0.7,
                                                    },
                                                    {
                                                        "label": "Moderate Risk (≥0.5)",
                                                        "value": 0.5,
                                                    },
                                                    {
                                                        "label": "Low Risk (≥0.3)",
                                                        "value": 0.3,
                                                    },
                                                ],
                                                value=None,
                                                placeholder="Choose a toxicity threshold...",
                                                className="mb-3",
                                                clearable=False,
                                                searchable=False,
                                                style={"width": "100%"},
                                            ),
                                        ],
                                        className="mb-4",
                                    ),
                                    # ========================================
                                    # Chart Container (Rendered on Selection)
                                    # ========================================
                                    html.Div(id="uc-7-2-chart", className="mt-4"),
                                ],
                                title="View Results",
                                item_id="uc-7-2-accordion",
                            )
                        ],
                        id="uc-7-2-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
        ],
        className="shadow-sm mb-4",
        id="uc-7-2-card",
    )
