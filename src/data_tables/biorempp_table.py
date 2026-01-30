"""
BioRemPP Table Section - Results Component.

Provides BioRemPP integrated results table with enhanced metadata,
database statistics, and on-demand rendering via accordion.

Functions
---------
create_biorempp_section
    Create complete BioRemPP section with enhanced description and accordion
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite import create_database_description


def create_biorempp_section() -> html.Div:
    """
    Create BioRemPP results table section with enhanced metadata.

    Returns
    -------
    html.Div
        Complete section with database description, statistics card,
        accordion with on-demand table rendering, and download component.
        Container ID: 'biorempp-container', Accordion ID: 'biorempp-accordion'
    """
    # Custom components for BioRemPP-specific information
    custom_components = [
        # Database statistics card
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.I(className="fas fa-database me-2"),
                        html.Strong("BioRemPP Database Overview"),
                    ],
                    className="bg-primary text-white",
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
                                                    "10,869",
                                                    className="text-primary mb-0",
                                                ),
                                                html.Small(
                                                    "Enzyme-Compound Relations",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    "384",
                                                    className="text-success mb-0",
                                                ),
                                                html.Small(
                                                    "Environmental Compounds",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    "12", className="text-info mb-0"
                                                ),
                                                html.Small(
                                                    "Compound Classes",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=3,
                                ),
                                dbc.Col(
                                    [
                                        html.Div(
                                            [
                                                html.H4(
                                                    "9", className="text-warning mb-0"
                                                ),
                                                html.Small(
                                                    "Regulatory Frameworks",
                                                    className="text-muted",
                                                ),
                                            ],
                                            className="text-center",
                                        )
                                    ],
                                    md=3,
                                ),
                            ]
                        )
                    ]
                ),
            ],
            className="mb-3 shadow-sm",
        )
    ]

    # Create download button for merged database
    from src.presentation.components.download_component import create_download_button

    download_button = create_download_button(
        use_case_id="biorempp-db",
        button_id="biorempp-db-download-btn",
        download_id="biorempp-db-download",
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
        href="/schemas/biorempp",
        target="_blank",
        rel="noopener noreferrer",
        className="btn btn-outline-info btn-sm",
    )

    # Enhanced database description
    description_component = create_database_description(
        title="BioRemPP Integrated Database",
        description=(
            "Integrates your data with the BioRemPP curated database of "
            "bioremediation-associated genes, enzymes, and pathways, enabling "
            "comprehensive annotation and functional analysis."
        ),
        section_id="biorempp-results-table",
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
                            "This table shows the intersection of your input data with the BioRemPP database. "
                            "Each row represents a KO-compound-enzyme relationship found in your samples.",
                        ],
                        color="info",
                        className="mb-3",
                    ),
                    # Table container
                    html.Div(id="biorempp-container", className="chart-container"),
                ],
                title="View BioRemPP Integrated Results Table",
            )
        ],
        start_collapsed=True,
        id="biorempp-accordion",
    )

    # Download component
    download = dcc.Download(id="download-merged-csv")

    # Complete section with enhanced styling
    section = html.Div(
        [description_component, accordion, download, html.Hr(className="my-4")]
    )

    return section
