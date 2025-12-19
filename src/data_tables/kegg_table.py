"""
KEGG Table Section - Results Component.

Provides KEGG degradation pathway table with enhanced metadata,
database statistics, and on-demand rendering via accordion.

Functions
---------
create_kegg_section
    Create complete KEGG section with enhanced description and accordion
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from src.presentation.components.composite import create_database_description


def create_kegg_section() -> html.Div:
    """
    Create KEGG pathway results table section with enhanced metadata.

    Returns
    -------
    html.Div
        Complete section with database description, statistics card,
        accordion with on-demand table rendering, and download component.
        Container ID: 'kegg-container', Accordion ID: 'kegg-accordion'
    """
    # Custom components for KEGG-specific information
    custom_components = [
        # Database statistics card
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.I(className="fas fa-database me-2"),
                        html.Strong("KEGG Degradation Database Overview"),
                    ],
                    className="bg-info text-white",
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
                                                    "871", className="text-info mb-0"
                                                ),
                                                html.Small(
                                                    "Gene-Pathway Associations",
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
                                                    "517", className="text-primary mb-0"
                                                ),
                                                html.Small(
                                                    "Unique KO Numbers",
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
                                                    "20", className="text-success mb-0"
                                                ),
                                                html.Small(
                                                    "Degradation Pathways",
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
        # Top pathways card
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.I(className="fas fa-chart-bar me-2"),
                        html.Strong("Top Degradation Pathways"),
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
                                                        html.Strong("Aromatic: "),
                                                        "215 genes",
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.Strong("Benzoate: "),
                                                        "106 genes",
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.Strong("Aminobenzoate: "),
                                                        "89 genes",
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
                                                        html.Strong("Toluene: "),
                                                        "46 genes",
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.Strong(
                                                            "Cl. alkane/alkene: "
                                                        ),
                                                        "43 genes",
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.Strong("Others: "),
                                                        "15+ pathways",
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
            className="mb-3",
        ),
    ]

    # Create download button for merged database
    from src.presentation.components.download_component import create_download_button

    download_button = create_download_button(
        use_case_id="kegg-db",
        button_id="kegg-db-download-btn",
        download_id="kegg-db-download",
        formats=["csv", "excel", "json"],
        button_text="Download Data",
        button_color="success",
        button_outline=True,
        show_spinner=True,
    )

    # Enhanced database description
    description_component = create_database_description(
        title="KEGG Degradation Pathway Mapping",
        description=(
            "Integrates your data with the KEGG Degradation Database, mapping KO numbers "
            "to xenobiotic degradation pathways and gene symbols for metabolic context analysis."
        ),
        insights=(
            "Pathway Coverage: 20 degradation routes for major pollutant classes\n"
            "Gene Catalog: 517 unique KO numbers with degradation functions\n"
            "Major Pathways: Aromatic (215 genes), Benzoate (106), Aminobenzoate (89), Toluene (46), Chlorinated compounds (43)\n"
            "KEGG Integration: Direct links to metabolic pathway context"
        ),
        section_id="kegg-results-table",
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
                            "This table shows the intersection of your input data with the KEGG degradation database. "
                            "Each row represents a gene-pathway-KO relationship found in your samples.",
                        ],
                        color="info",
                        className="mb-3",
                    ),
                    # Table container
                    html.Div(id="kegg-container", className="chart-container"),
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
                                    html.Ul(
                                        [
                                            html.Li(
                                                [
                                                    html.Strong("ko: "),
                                                    "KEGG Orthology identifier linking to metabolic functions (e.g., K00001)",
                                                ]
                                            ),
                                            html.Li(
                                                [
                                                    html.Strong("pathname: "),
                                                    "Degradation pathway category (e.g., Aromatic, Benzoate, Toluene, Naphthalene)",
                                                ]
                                            ),
                                            html.Li(
                                                [
                                                    html.Strong("genesymbol: "),
                                                    "Gene symbol associated with the degradation enzyme (e.g., benA, xylC, nahAa)",
                                                ]
                                            ),
                                        ],
                                        className="mb-0",
                                    )
                                ]
                            ),
                        ],
                        className="mt-3",
                    ),
                ],
                title="View KEGG Degradation Pathway Table",
            )
        ],
        start_collapsed=True,
        id="kegg-accordion",
    )

    # Download component
    download = dcc.Download(id="download-kegg-csv")

    # Complete section with enhanced styling
    section = html.Div(
        [description_component, accordion, download, html.Hr(className="my-4")]
    )

    return section
