"""
UC-4.6 Layout - Interactive Functional Potential by Chemical Compound.

Provides layout for bubble chart showing functional potential (KO diversity)
across samples and compounds within selected chemical classes.

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


def create_uc_4_6_layout() -> dbc.Card:
    """
    Create UC-4.6 layout for functional potential by compound.

    Returns
    -------
    dbc.Card
        Card component with dropdown and bubble chart.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-4-6")
    from src.presentation.pages.methods.methods_service import get_methods_service
    from src.presentation.pages.methods.workflow_modal import create_workflow_modal

    workflow = get_methods_service().get_workflow("UC-4.6")
    workflow_modal = create_workflow_modal(workflow) if workflow else html.Div()

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
                                            (
                                                "UC-4.6: Interactive Analysis of Functional Potential by "
                                                "Chemical Compound"
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
                                                    id={"type": "link", "index": "UC-4.6"},
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
                                                use_case_id="UC-4.6",
                                                button_id="uc-4-6-download-btn",
                                                download_id="uc-4-6-download",
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
                ]
            ),
            # ========================================
            # Card Body
            # ========================================
            dbc.CardBody(
                [
                    # Download Toast Notification
                    create_download_toast(toast_id="uc-4-6-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Interactive Controls
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # Dropdown for Compound Class Selection
                                    html.Div(
                                        [
                                            html.Label(
                                                "Select Chemical Compound Class:",
                                                className="fw-bold mb-2",
                                            ),
                                            dcc.Dropdown(
                                                id="uc-4-6-compound-class-dropdown",
                                                placeholder="Choose a compound class to visualize...",
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
                                        id="uc-4-6-chart-container", className="mt-4"
                                    ),
                                ],
                                title="View Results",
                                item_id="uc-4-6-accordion",
                            )
                        ],
                        id="uc-4-6-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
            workflow_modal,
        ],
        className="shadow-sm mb-4",
        id="uc-4-6-card",
    )
