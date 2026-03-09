"""
New User Guide Modal Component

Provides a guided walkthrough for first-time users, following the header navigation flow.
"""

import dash_bootstrap_components as dbc
from dash import dcc, html

from ...routing import app_path


def create_new_user_guide_button():
    """
    Create the new user guide button with introductory text.

    Returns
    -------
    dbc.Card
        Card containing intro text and button to open guide modal
    """
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    # Icon and title
                    html.Div(
                        [
                            html.I(className="fas fa-compass fa-2x text-primary mb-3"),
                            html.H5(
                                "First Time Using BioRemPP?",
                                className="card-title mb-3",
                            ),
                        ],
                        className="text-center",
                    ),
                    # Description
                    html.P(
                        [
                            "New to bioremediation analysis or exploring BioRemPP for the first time? ",
                            "We've prepared a step-by-step guide to help you navigate the platform and ",
                            "make the most of its features.",
                        ],
                        className="text-muted text-center mb-3",
                    ),
                    # Button to open modal
                    html.Div(
                        [
                            dbc.Button(
                                [
                                    html.I(className="fas fa-map-marked-alt me-2"),
                                    "Start Quick Walkthrough",
                                ],
                                id="onboarding-walkthrough-open",
                                color="primary",
                                size="lg",
                                className="shadow-sm",
                            )
                        ],
                        className="d-grid",
                    ),
                    # Always-visible fallback in case browser extensions hide the main button
                    html.Div(
                        [
                            html.Small(
                                "View the full user guide",
                                className="text-muted d-block mb-2",
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-book-open me-2"),
                                    "Open User Guide",
                                ],
                                href=app_path("/user-guide"),
                                color="secondary",
                                outline=True,
                                size="sm",
                            ),
                        ],
                        className="text-center mt-3",
                    ),
                ]
            )
        ],
        className="shadow-sm mb-4 h-100",
    )


def create_example_dataset_card() -> dbc.Card:
    """
    Create a quick-access card for example KO dataset actions.

    Returns
    -------
    dbc.Card
        Card with info and download actions for example dataset
    """
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className="fas fa-database fa-2x text-success mb-3"),
                            html.H5(
                                "Need a KO Input Example?",
                                className="card-title mb-3",
                            ),
                        ],
                        className="text-center",
                    ),
                    html.P(
                        [
                            "Start with the curated example dataset to validate the "
                            "input format and begin your analysis pipeline from KO IDs.",
                        ],
                        className="text-muted text-center mb-3",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-circle-info me-2"),
                                        "View Info",
                                    ],
                                    id="sample-data-card",
                                    color="info",
                                    outline=True,
                                    className="w-100",
                                    n_clicks=0,
                                ),
                                md=12,
                                className="mb-2",
                            ),
                            dbc.Col(
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-download me-2"),
                                        "Download Example",
                                    ],
                                    id="sample-data-download-btn",
                                    color="success",
                                    className="w-100",
                                    n_clicks=0,
                                ),
                                md=12,
                            ),
                        ],
                        className="g-2",
                    ),
                    html.P(
                        "Don't have data? Click above to load an example dataset.",
                        className="text-center text-muted mt-3 mb-0",
                        style={"fontSize": "0.85rem"},
                    ),
                    dcc.Download(id="sample-data-download"),
                ]
            )
        ],
        className="shadow-sm mb-4 h-100",
    )


def create_new_user_guide_modal():
    """
    Create the new user guide modal with step-by-step walkthrough.

    Returns
    -------
    dbc.Modal
        Modal containing guided tour steps
    """
    return dbc.Modal(
        [
            dbc.ModalHeader(
                [
                    html.I(className="fas fa-compass me-2"),
                    "Welcome to BioRemPP - Your Guided Tour",
                ],
                close_button=True,
            ),
            dbc.ModalBody(
                [
                    # Introduction
                    dbc.Alert(
                        [
                            html.I(className="fas fa-info-circle me-2"),
                            html.Strong("About This Guide: "),
                            "Follow these steps to understand BioRemPP's core principles, features, and workflow. "
                            "Each section links to the corresponding page in the navigation menu.",
                        ],
                        color="info",
                        className="mb-4",
                    ),
                    # Step 1: Regulatory References
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("1", className="badge bg-primary me-2"),
                                    html.I(className="fas fa-balance-scale me-2"),
                                    "Regulatory References",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "Start by understanding the ",
                                    html.Strong("core principles"),
                                    " of BioRemPP. Learn about the regulatory frameworks (IARC, EPA, ATSDR, WFD, PSL, EPC, CONAMA) "
                                    "that classify environmental pollutants and guide bioremediation strategies.",
                                ],
                                className="text-muted mb-2",
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-external-link-alt me-2"),
                                    "Explore Regulatory Frameworks",
                                ],
                                href=app_path("/regulatory"),
                                color="primary",
                                outline=True,
                                size="sm",
                                className="mb-4",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Step 2: User Guide
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("2", className="badge bg-success me-2"),
                                    html.I(className="fas fa-book-open me-2"),
                                    "User Guide",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "Familiarize yourself with the ",
                                    html.Strong("platform layout"),
                                    " and features. The User Guide explains how to upload data, navigate modules, "
                                    "and interpret results.",
                                ],
                                className="text-muted mb-2",
                            ),
                            dbc.Alert(
                                [
                                    html.I(className="fas fa-lightbulb me-2"),
                                    html.Strong("Pro Tip: "),
                                    "On the Results page, check the ",
                                    html.Strong("Analysis Suggestions panel"),
                                    " in the bottom for guided analytical workflows!",
                                ],
                                color="warning",
                                className="mb-2",
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-external-link-alt me-2"),
                                    "Read User Guide",
                                ],
                                href=app_path("/user-guide"),
                                color="success",
                                outline=True,
                                size="sm",
                                className="mb-4",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Step 3: Methods
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("3", className="badge bg-info me-2"),
                                    html.I(className="fas fa-flask me-2"),
                                    "Methods & Use Cases",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "Get a ",
                                    html.Strong("high-level understanding"),
                                    " of the 56 analytical use cases across 8 modules. Each use case provides "
                                    "detailed workflows for specific bioremediation analyses.",
                                ],
                                className="text-muted mb-2",
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-external-link-alt me-2"),
                                    "Explore Methods",
                                ],
                                href=app_path("/methods"),
                                color="info",
                                outline=True,
                                size="sm",
                                className="mb-4",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Step 4: Official Documentation
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("4", className="badge bg-warning me-2"),
                                    html.I(className="fas fa-file-alt me-2"),
                                    "Official Documentation",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "For in-depth technical details, API references, and advanced features, "
                                    "consult the ",
                                    html.Strong("official documentation"),
                                    ".",
                                ],
                                className="text-muted mb-2",
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-book me-2"),
                                    "View Documentation",
                                ],
                                href="https://biormepp-web.readthedocs.io/en/latest/",  # Official documentation
                                target="_blank",
                                color="warning",
                                outline=True,
                                size="sm",
                                className="mb-4",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Step 5: FAQ
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("5", className="badge bg-secondary me-2"),
                                    html.I(className="fas fa-question-circle me-2"),
                                    "FAQ & Troubleshooting",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "Find answers to ",
                                    html.Strong("common questions"),
                                    " and troubleshooting tips. The FAQ covers data formats, analysis workflows, "
                                    "interpretation guidelines, and technical issues.",
                                ],
                                className="text-muted mb-2",
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-external-link-alt me-2"),
                                    "Browse FAQ",
                                ],
                                href=app_path("/faq"),
                                color="secondary",
                                outline=True,
                                size="sm",
                                className="mb-4",
                            ),
                        ]
                    ),
                    html.Hr(),
                    # Step 6: Contact
                    html.Div(
                        [
                            html.H5(
                                [
                                    html.Span("6", className="badge bg-dark me-2"),
                                    html.I(className="fas fa-envelope me-2"),
                                    "Get in Touch",
                                ],
                                className="mb-3",
                            ),
                            html.P(
                                [
                                    "Have questions, suggestions, or interested in collaborations? ",
                                    html.Strong("We'd love to hear from you! "),
                                    "Whether it's feedback, feature requests, bug reports, or partnership opportunities, "
                                    "feel free to reach out through our contact page.",
                                ],
                                className="text-muted mb-2",
                            ),
                            dbc.Button(
                                [
                                    html.I(className="fas fa-paper-plane me-2"),
                                    "Contact Us",
                                ],
                                href=app_path("/contact"),
                                color="dark",
                                outline=True,
                                size="sm",
                                className="mb-2",
                            ),
                        ]
                    ),
                    # Footer note
                    html.Hr(),
                    dbc.Alert(
                        [
                            html.I(className="fas fa-rocket me-2"),
                            html.Strong("Ready to Start? "),
                            "Upload your KO annotation data and begin exploring bioremediation potential!",
                        ],
                        color="success",
                        className="mb-0",
                    ),
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Close",
                        id="onboarding-walkthrough-close",
                        color="secondary",
                        outline=True,
                    )
                ]
            ),
        ],
        id="onboarding-walkthrough-dialog",
        size="lg",
        centered=True,
        scrollable=True,
        is_open=False,
    )
