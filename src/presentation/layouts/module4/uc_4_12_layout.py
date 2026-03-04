"""
UC-4.12 Layout - Interactive Heatmap of Pathway Relationships by Sample.

Provides layout for heatmap showing functional richness at pathway-compound
pathway intersections for individual samples.

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


def create_uc_4_12_layout() -> dbc.Card:
    """
    Create UC-4.12 layout for pathway relationships by sample.

    Returns
    -------
    dbc.Card
        Card component with dropdown and heatmap.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-4-12")
    from src.presentation.pages.methods.methods_service import get_methods_service
    from src.presentation.pages.methods.workflow_modal import create_workflow_modal

    workflow = get_methods_service().get_workflow("UC-4.12")
    workflow_modal = create_workflow_modal(workflow) if workflow else html.Div()

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
                                            "UC-4.12: Interactive Heatmap of Pathway Relationships "
                                            "by Sample (HADEG)"
                                        ),
                                    ],
                                    className="mb-0",
                                )
                            ],
                            width="auto",
                        ),
                        dbc.Col(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Button(
                                                "Methods",
                                                id={"type": "link", "index": "UC-4.12"},
                                                color="primary",
                                                outline=False,
                                                size="sm",
                                                className="me-1",
                                                n_clicks=0,
                                                title=(
                                                    "View analytical workflow "
                                                    "for this use case"
                                                ),
                                            ),
                                            width="auto",
                                        ),
                                        create_download_button(
                                            use_case_id="UC-4.12",
                                            button_id="uc-4-12-download-btn",
                                            download_id="uc-4-12-download",
                                            formats=["csv", "excel", "json"],
                                            button_text="Download Data",
                                        ),
                                    ],
                                    align="center",
                                    className="g-1 flex-nowrap",
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
                    create_download_toast(toast_id="uc-4-12-download-toast"),
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Dropdown for Sample Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Sample:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-4-12-sample-dropdown",
                                                placeholder="Choose a sample to analyze...",
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
                                        id="uc-4-12-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-4-12-accordion",
                            )
                        ],
                        id="uc-4-12-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
            workflow_modal,
        ],
        className="shadow-sm mb-4",
        id="uc-4-12-card",
    )
