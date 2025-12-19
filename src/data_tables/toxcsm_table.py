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
        # Toxicity categories card
        dbc.Card(
            [
                dbc.CardHeader(
                    [
                        html.I(className="fas me-2"),
                        html.Strong("Toxicity Prediction Categories"),
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
                                                            "Nuclear Response (NR): "
                                                        ),
                                                        "10 endpoints",
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.Strong(
                                                            "Stress Response (SR): "
                                                        ),
                                                        "6 endpoints",
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.Strong(
                                                            "Genotoxicity (Gen): "
                                                        ),
                                                        "3 endpoints",
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
                                                            "Environmental (Env): "
                                                        ),
                                                        "6 endpoints",
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.Strong(
                                                            "Organ-Specific (Org): "
                                                        ),
                                                        "9 endpoints",
                                                    ]
                                                ),
                                                html.Li(
                                                    [
                                                        html.Strong(
                                                            "Total Predictions: "
                                                        ),
                                                        "34 toxicity assays",
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
        use_case_id="toxcsm-db",
        button_id="toxcsm-db-download-btn",
        download_id="toxcsm-db-download",
        formats=["csv", "excel", "json"],
        button_text="Download Data",
        button_color="success",
        button_outline=True,
        show_spinner=True,
    )

    # Enhanced database description
    description_component = create_database_description(
        title="toxCSM Toxicity Prediction Analysis",
        description=(
            "Integrates your data with the ToxCSM database (Toxicity Prediction via Machine Learning), "
            "providing in silico toxicity predictions across 34 biological endpoints using validated ML models."
        ),
        insights=(
            "Compound Coverage: 323 environmental compounds with toxicity profiles\n"
            "Prediction Categories: 5 major groups (Nuclear Response, Stress Response, Genotoxicity, Environmental, Organ-Specific)\n"
            "Nuclear Response: Androgen, Estrogen, Aromatase, PPAR-γ, Glucocorticoid, Thyroid receptors (10 endpoints)\n"
            "Stress Response: ARE, ATAD5, HSE, MMP, p53 pathways (6 endpoints)\n"
            "Genotoxicity: AMES mutagenesis, carcinogenesis, micronucleus (3 endpoints)\n"
            "Environmental: Aquatic toxicity, biodegradation, avian effects (6 endpoints)\n"
            "Organ Toxicity: Skin, hERG, liver, eye, respiratory (9 endpoints)"
        ),
        section_id="toxcsm-results-table",
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
                            "This table shows the complete ToxCSM database merged with your input data. "
                            "Each row represents a compound with all 66 columns including SMILES structure, identifiers, "
                            "and toxicity predictions (value + label) for all 34 endpoints.",
                        ],
                        color="warning",
                        className="mb-3",
                    ),
                    # Table container
                    html.Div(id="toxcsm-container", className="chart-container"),
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
                                                    html.H6(
                                                        "Compound Identifiers:",
                                                        className="text-primary",
                                                    ),
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "SMILES: "
                                                                    ),
                                                                    "Chemical structure notation",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "cpd: "
                                                                    ),
                                                                    "KEGG compound ID (e.g., C00001)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "ChEBI: "
                                                                    ),
                                                                    "ChEBI database ID",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "compoundname: "
                                                                    ),
                                                                    "Common compound name",
                                                                ]
                                                            ),
                                                        ],
                                                        className="mb-3",
                                                    ),
                                                    html.H6(
                                                        "Toxicity Predictions:",
                                                        className="text-danger",
                                                    ),
                                                    html.P(
                                                        [
                                                            "Each endpoint has 2 columns: ",
                                                            html.Code("value_*"),
                                                            " (numerical score 0-1) and ",
                                                            html.Code("label_*"),
                                                            " (High/Medium/Low Safety or Toxicity)",
                                                        ],
                                                        className="small",
                                                    ),
                                                ],
                                                md=6,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.H6(
                                                        "Endpoint Categories:",
                                                        className="text-warning",
                                                    ),
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "NR_*: "
                                                                    ),
                                                                    "Nuclear receptor assays (AR, ER, AhR, Aromatase, PPAR-γ, GR, TR)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "SR_*: "
                                                                    ),
                                                                    "Stress response pathways (ARE, ATAD5, HSE, MMP, p53)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "Gen_*: "
                                                                    ),
                                                                    "Genotoxicity (AMES, Carcinogenesis, Micronucleus)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "Env_*: "
                                                                    ),
                                                                    "Environmental toxicity (Fathead Minnow, T. Pyriformis, Honey Bee, Biodegradation, Crustacean, Avian)",
                                                                ]
                                                            ),
                                                            html.Li(
                                                                [
                                                                    html.Strong(
                                                                        "Org_*: "
                                                                    ),
                                                                    "Organ toxicity (Skin, hERG I/II, Liver I/II, Eye Irritation/Corrosion, Respiratory)",
                                                                ]
                                                            ),
                                                        ],
                                                        className="small mb-0",
                                                    ),
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
