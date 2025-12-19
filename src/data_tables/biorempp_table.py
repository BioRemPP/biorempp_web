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

    # Enhanced database description
    description_component = create_database_description(
        title="BioRemPP Integrated Results",
        description=(
            "Integrates your KO annotations with the BioRemPP database, linking KEGG Orthology numbers "
            "to pollutants, enzyme activities, compound classes, and regulatory frameworks."
        ),
        insights=(
            "Enzyme-Pollutant Links: Connects KO numbers to gene symbols, enzyme names, and degradation targets\n"
            "Compound Coverage: 384 environmental pollutants (Aromatic, Aliphatic, Chlorinated, Metal, Nitrogen-containing)\n"
            "Regulatory Mapping: Compounds classified by 9 international frameworks (IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA, and others)\n"
            "Activity Classification: 205 enzyme mechanisms (dehydrogenase, oxidase, reductase, hydrolase)"
        ),
        section_id="biorempp-results-table",
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
                            "This table shows the intersection of your input data with the BioRemPP database. "
                            "Each row represents a KO-compound-enzyme relationship found in your samples.",
                        ],
                        color="info",
                        className="mb-3",
                    ),
                    # Table container
                    html.Div(id="biorempp-container", className="chart-container"),
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
                                                                    html.Strong("ko: "),
                                                                    "KEGG Orthology identifier (e.g., K00001)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "genesymbol: "
                                                                    ),
                                                                    "Gene symbol or enzyme code (e.g., E1.1.1.1)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "genename: "
                                                                    ),
                                                                    "Full enzyme name (e.g., alcohol dehydrogenase)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "cpd: "
                                                                    ),
                                                                    "KEGG Compound ID for the pollutant",
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
                                                                        "compoundclass: "
                                                                    ),
                                                                    "Chemical classification (Aromatic, Chlorinated, Metal, etc.)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "referenceAG: "
                                                                    ),
                                                                    "Regulatory agency (IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "compoundname: "
                                                                    ),
                                                                    "Common name of the pollutant",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "enzyme_activity: "
                                                                    ),
                                                                    "Type of enzymatic activity (dehydrogenase, oxidase, reductase, etc.)",
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
