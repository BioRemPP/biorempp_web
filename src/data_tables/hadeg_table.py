"""
HADEG Table Section - Results Component.

Provides HADEG pathway analysis table with enhanced metadata,
database statistics, and on-demand rendering via accordion.

Functions
---------
create_hadeg_section
    Create complete HADEG section with enhanced description and accordion
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite import create_database_description


def create_hadeg_section() -> html.Div:
    """
    Create HADEG results table section with enhanced metadata.

    Returns
    -------
    html.Div
        Complete section with database description, statistics card,
        accordion with on-demand table rendering, and download component.
        Container ID: 'hadeg-container', Accordion ID: 'hadeg-accordion'
    """
    # Custom components for HADEG-specific information
    custom_components = [
        # Database statistics card
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.I(className="fas fa-database me-2"),
                        html.Strong("HADEG Database Overview"),
                    ],
                    className="bg-success text-white",
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
                                                    "1,168",
                                                    className="text-success mb-0",
                                                ),
                                                html.Small(
                                                    "Gene-Pathway Relations",
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
                                                    "339", className="text-primary mb-0"
                                                ),
                                                html.Small(
                                                    "Unique KO Numbers",
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
                                                    "71", className="text-info mb-0"
                                                ),
                                                html.Small(
                                                    "Degradation Pathways",
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
                                                    "5", className="text-warning mb-0"
                                                ),
                                                html.Small(
                                                    "Compound Categories",
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
        use_case_id="hadeg-db",
        button_id="hadeg-db-download-btn",
        download_id="hadeg-db-download",
        formats=["csv", "excel", "json"],
        button_text="Download Data",
        button_color="success",
        button_outline=True,
        show_spinner=True,
    )

    # Enhanced database description
    description_component = create_database_description(
        title="HADEG Pathway Analysis",
        description=(
            "Integrates your data with the HADEG database (Hydrocarbon Aerobic Degrading Enzymes and Genes), "
            "linking KO numbers to genes, degradation pathways, and target compounds."
        ),
        insights=(
            "Aerobic Pathways: 71 distinct degradation routes for environmental hydrocarbons\n"
            "Compound Types: Polymers (598 genes), Aromatics (361), Alkanes (107), Biosurfactants (52), Alkenes (50)\n"
            "Gene-Pathway Links: Connects genes to specific degradation mechanisms\n"
            "Specialization: Focused on aerobic hydrocarbon bioremediation"
        ),
        section_id="hadeg-results-table",
        custom_components=custom_components,
        download_button=download_button,  # Add download button to header
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
                            "This table shows the intersection of your input data with the HADEG database. "
                            "Each row represents a gene-pathway-compound relationship found in your samples.",
                        ],
                        color="success",
                        className="mb-3",
                    ),
                    # Table container
                    html.Div(id="hadeg-container", className="chart-container"),
                    # Column descriptions
                    dbc.Card(
                        [
                            dbc.CardHeader(
                                [
                                    html.I(className="fas fa-table me-2"),
                                    html.Strong("Column Descriptions"),
                                ],
                                className="bg-light",
                            ),
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "Gene: "
                                                                    ),
                                                                    "Gene symbol or identifier (e.g., alkB, benA)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong("ko: "),
                                                                    "KEGG Orthology identifier (e.g., K00496)",
                                                                ]
                                                            ),
                                                        ],
                                                        className="mb-0",
                                                    )
                                                ],
                                                md=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "Pathway: "
                                                                    ),
                                                                    "Degradation pathway name (e.g., A_Terminal/biterminal_oxidation)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "compound_pathway: "
                                                                    ),
                                                                    "Target compound category (Polymers, Aromatics, Alkanes, etc.)",
                                                                ]
                                                            ),
                                                        ],
                                                        className="mb-0",
                                                    )
                                                ],
                                                md=6,
                                            ),
                                        ]
                                    )
                                ]
                            ),
                        ],
                        className="mt-3",
                    ),
                ],
                title="View HADEG Pathway Analysis Table",
            )
        ],
        start_collapsed=True,
        id="hadeg-accordion",
    )

    # Download component
    download = dcc.Download(id="download-hadeg-csv")

    # Complete section with enhanced styling
    section = html.Div(
        [description_component, accordion, download, html.Hr(className="my-4")]
    )

    return section
