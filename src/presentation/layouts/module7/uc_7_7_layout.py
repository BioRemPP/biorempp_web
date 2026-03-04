"""
UC-7.7 Layout - Sample Risk Mitigation Depth Profile by Genetic Investment.

Provides layout for treemap visualization showing depth of genetic
investment in risk mitigation across microbial samples.

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


def create_uc_7_7_layout() -> dbc.Card:
    """
    Create UC-7.7 layout for sample risk mitigation depth analysis.

    Returns
    -------
    dbc.Card
        Card component with treemap showing mitigation depth profiles.

    Notes
    -----
    - See official documentation for use case details
    """
    # Load informative panel from YAML config
    info_panel = create_panel_by_id("uc-7-7")
    from src.presentation.pages.methods.methods_service import get_methods_service
    from src.presentation.pages.methods.workflow_modal import create_workflow_modal

    workflow = get_methods_service().get_workflow("UC-7.7")
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
                                            "UC-7.7: Sample Risk Mitigation Depth Profile by "
                                            "Genetic Investment",
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
                                                    id={"type": "link", "index": "UC-7.7"},
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
                                                use_case_id="UC-7.7",
                                                button_id="uc-7-7-download-btn",
                                                download_id="uc-7-7-download",
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
                    # Download toast notification
                    create_download_toast(toast_id="uc-7-7-download-toast"),
                    # Informative panel (scientific context)
                    info_panel,
                    # ========================================
                    # Accordion: Chart Container
                    # ========================================
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    # ========================================
                                    # Chart Container (Rendered on Accordion Open)
                                    # ========================================
                                    html.Div(id="uc-7-7-chart", className="mt-3")
                                ],
                                title="View Results",
                                item_id="uc-7-7-accordion",
                            )
                        ],
                        id="uc-7-7-accordion-group",
                        start_collapsed=True,
                    ),
                ],
                className="p-4",
            ),
            workflow_modal,
        ],
        className="shadow-sm mb-4",
        id="uc-7-7-card",
    )
