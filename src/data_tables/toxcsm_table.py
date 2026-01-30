"""
ToxCSM Table Section - Results Component.

Provides ToxCSM toxicity prediction table with enhanced metadata,
database statistics, and on-demand rendering via accordion.

Functions
---------
create_toxcsm_section
    Create complete ToxCSM section with enhanced description and accordion
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite import create_database_description


def create_toxcsm_section() -> html.Div:
    """
    Create ToxCSM results table section with enhanced metadata.

    Returns
    -------
    html.Div
        Complete section with database description, statistics card,
        accordion with on-demand table rendering, and download component.
        Container ID: 'toxcsm-container', Accordion ID: 'toxcsm-accordion'
    """
    # Custom components for ToxCSM-specific information
    custom_components = [
        # Database statistics card
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.I(className="fas fa-database me-2"),
                        html.Strong("ToxCSM Database Overview"),
                    ],
                    className="bg-warning text-dark",
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    "323", className="text-warning mb-0"
                                                ),
                                                html.Small(
                                                    "Environmental Compounds",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    "66", className="text-danger mb-0"
                                                ),
                                                html.Small(
                                                    "Toxicity Endpoints",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=4,
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    "5", className="text-info mb-0"
                                                ),
                                                html.Small(
                                                    "Toxicity Categories",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=4,
                                ),
                            ]
                        )
                    ]
                ),
            ],
            className="mb-3 shadow-sm",
        ),
    ]

    # Create download button for merged database
    from src.presentation.components.download_component import create_download_button

    download_button = create_download_button(
        use_case_id="toxcsm-db",
        button_id="toxcsm-db-download-btn",
        download_id="toxcsm-db-download",
        formats=["csv", "excel", "json"],
        button_text="Download Data",
        button_color="success",
        button_outline=True,
        show_spinner=True,
    )

    # Create Database Info button that opens schema page in new tab
    # Using html.A instead of dbc.Button to bypass Dash router and open in new tab
    info_button = html.A(
        [
            html.I(className="fas fa-info-circle me-2"),
            "Database Info",
        ],
        href="/schemas/toxcsm",
        target="_blank",
        rel="noopener noreferrer",
        className="btn btn-outline-info btn-sm",
    )

    # Enhanced database description
    description_component = create_database_description(
        title="toxCSM Toxicity Prediction Analysis",
        description=(
            "Integrates your data with the ToxCSM database (Toxicity Prediction via Machine Learning), "
            "providing in silico toxicity predictions across 34 biological endpoints using validated ML models."
        ),
        section_id="toxcsm-results-table",
        custom_components=custom_components,
        download_button=download_button,
        info_button=info_button,
    )

    # Accordion with on-demand table and enhanced title
    accordion = dbc.Accordion(
        [
            dbc.AccordionItem(
                [
                    # Info alert before table
                    dbc.Alert(
                        [
                            html.I(className="fas fa-info-circle me-2"),
                            html.Strong("Table Contents: "),
                            "This table shows the complete ToxCSM database merged with your input data. "
                            "Each row represents a compound with all 66 columns including SMILES structure, identifiers, "
                            "and toxicity predictions (value + label) for all 34 endpoints.",
                        ],
                        color="warning",
                        className="mb-3",
                    ),
                    # Table container
                    html.Div(id="toxcsm-container", className="chart-container"),
                ],
                title=" View ToxCSM Toxicity Prediction Table",
            )
        ],
        start_collapsed=True,
        id="toxcsm-accordion",
    )

    # Download component
    download = dcc.Download(id="download-toxcsm-csv")

    # Complete section with enhanced styling
    section = html.Div(
        [description_component, accordion, download, html.Hr(className="my-4")]
    )

    return section
