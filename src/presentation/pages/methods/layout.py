"""
Methods Page Layout

Main layout for the Methods page displaying analytical workflows.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from ...components.base import create_footer, create_header


def create_methods_layout() -> html.Div:
    """
    Create the main layout for the Methods page.

    Returns:
        html.Div containing the complete page layout.
    """
    # Header
    header = create_header(show_nav=True, logo_size="60px")

    # Page content
    content = html.Div(
        [
            # Page Header
            dbc.Container(
                [
                    html.Div(
                        [
                            html.H1(
                                "Analytical Methods",
                                className="display-4 mb-3",
                                style={"fontWeight": "600"},
                            ),
                            html.P(
                                "Comprehensive analytical workflows for all 56 use cases across 8 modules",
                                className="lead text-muted mb-4",
                            ),
                            html.Hr(),
                        ],
                        className="text-center py-4",
                    )
                ],
                fluid=True,
                className="bg-light",
            ),
            # Scientific Overview Card
            dbc.Container(
                [
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    html.H4(
                                                        [
                                                            html.I(
                                                                className="fas fa-microscope me-2"
                                                            ),
                                                            "Scientific Foundations",
                                                        ],
                                                        className="mb-3",
                                                    ),
                                                    html.P(
                                                        "Learn about the scientific methods, data science techniques, "
                                                        "and multi-omics integration strategies that underpin BioRemPP's "
                                                        "analytical capabilities.",
                                                        className="text-muted mb-3",
                                                    ),
                                                    html.Ul(
                                                        [
                                                            html.Li(
                                                                "Core scientific metrics (KO richness, Compound richness, Functional guilds)"
                                                            ),
                                                            html.Li(
                                                                "Feature engineering and machine learning methods"
                                                            ),
                                                            html.Li(
                                                                "FAIR principles and database integration"
                                                            ),
                                                            html.Li(
                                                                "Multi-omics integration strategies"
                                                            ),
                                                        ],
                                                        className="mb-3",
                                                    ),
                                                ],
                                                md=8,
                                            ),
                                            dbc.Col(
                                                [
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                [
                                                                    html.I(
                                                                        className="fas fa-book-open me-2"
                                                                    ),
                                                                    "View Scientific Overview",
                                                                ],
                                                                href="/methods/overview",
                                                                color="primary",
                                                                size="lg",
                                                                className="w-100 mb-2",
                                                            ),
                                                            html.P(
                                                                "Understand the methodology before exploring workflows",
                                                                className="text-muted small text-center",
                                                            ),
                                                        ],
                                                        className="d-flex flex-column justify-content-center h-100",
                                                    )
                                                ],
                                                md=4,
                                            ),
                                        ]
                                    )
                                ]
                            )
                        ],
                        className="shadow-sm border-primary mb-4",
                    )
                ],
                fluid=True,
                className="mt-4",
            ),
            # Main Content Container
            dbc.Container(
                [
                    # Module Content
                    html.Div(id="methods-module-content", className="my-4"),
                    # Bottom Pagination
                    html.Div(id="methods-pagination-bottom", className="mb-4"),
                    # Loading Overlay
                    dcc.Loading(
                        id="methods-loading",
                        type="default",
                        children=html.Div(id="methods-loading-output"),
                    ),
                ],
                fluid=True,
            ),
            # Store Components
            dcc.Store(id="methods-current-module", data=1),
            dcc.Location(id="methods-url", refresh=False),
        ]
    )

    # Footer
    footer = create_footer(version="1.0.0", year=2024)

    # Complete layout
    layout = html.Div([header, content, footer])

    return layout
