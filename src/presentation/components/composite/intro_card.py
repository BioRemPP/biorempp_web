import dash_bootstrap_components as dbc
from dash import html

from .info_modal import create_info_modal
from src.presentation.routing import app_path


def create_how_to_cite_modal() -> dbc.Modal:
    """Create compact How to Cite modal accessible from intro actions."""
    return dbc.Modal(
        [
            dbc.ModalHeader(
                [html.I(className="fas fa-quote-right me-2"), "How to Cite"],
                close_button=True,
            ),
            dbc.ModalBody(
                [
                    html.P(
                        html.I("Citation placeholder"),
                        className="mb-3 text-dark",
                    ),
                    html.P(
                        "For full citation templates, BibTeX entries, and DOI updates, "
                        "open the complete citation page.",
                        className="text-muted mb-3",
                    ),
                    dbc.Button(
                        [
                            html.I(className="fas fa-external-link-alt me-2"),
                            "Open Full Citation Page",
                        ],
                        href=app_path("/how-to-cite"),
                        color="success",
                        className="w-100",
                    ),
                ]
            ),
            dbc.ModalFooter(
                dbc.Button(
                    "Close",
                    id="how-to-cite-close",
                    color="secondary",
                    n_clicks=0,
                )
            ),
        ],
        id="how-to-cite-modal",
        is_open=False,
        centered=True,
        size="lg",
    )


def create_intro_card() -> html.Div:
    """
    Create an introduction block with the BioRemPP logo, description,
    a privacy/info alert, and top action buttons.

    Returns
    -------
    html.Div
        A container holding the intro content.
    """
    text_class = "text-dark"

    return html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        html.Img(
                            src=app_path("/assets/BIOREMPP_LOGO.png"),
                            style={"maxWidth": "100%", "height": "auto"},
                            alt="BioRemPP Logo",
                        ),
                        width=3,
                        className="d-flex align-items-center justify-content-center p-3",
                    ),
                    dbc.Col(
                        html.Div(
                            [
                                html.P(
                                    "The Bioremediation Potential Profile (BioRemPP) is a scientific "
                                    "web service designed for the integrative functional "
                                    "exploration of annotated genomes in the context of bioremediation research",
                                    className=text_class,
                                ),
                                html.P(                                    
                                    "By combining multiple curated bioremediation-related databases, "
                                    "BioRemPP supports the interpretation of metabolic pathways, "
                                    "enzymatic functions, and associations among genes, compounds, "
                                    "samples, and toxicity-related annotations",
                                    className=text_class,
                                ),
                                # Top actions
                                html.Div(
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Button(
                                                    "More Info",
                                                    id="info-modal-open-button",
                                                    color="primary",
                                                    size="md",
                                                    className="mt-2 intro-action-btn",
                                                    n_clicks=0,
                                                ),
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    [
                                                        html.I(
                                                            className="fas fa-exclamation-triangle me-2"
                                                        ),
                                                        "Terms of Use",
                                                    ],
                                                    id="terms-btn",
                                                    color="warning",
                                                    size="md",
                                                    className="mt-2 intro-action-btn",
                                                    n_clicks=0,
                                                ),
                                                width="auto",
                                            ),
                                            dbc.Col(
                                                dbc.Button(
                                                    [
                                                        html.I(
                                                            className="fas fa-quote-right me-2"
                                                        ),
                                                        "How to Cite",
                                                    ],
                                                    id="how-to-cite-btn",
                                                    color="success",
                                                    size="md",
                                                    className="mt-2 intro-action-btn",
                                                    n_clicks=0,
                                                ),
                                                width="auto",
                                            ),
                                        ],
                                        className="g-2 justify-content-center",
                                    ),
                                    className="text-center mt-1",
                                ),
                            ],
                            className="p-3 text-center",
                        ),
                        width=9,
                    ),
                ],
                className="g-0 align-items-center",
            ),
            # Privacy / no-login message
            dbc.Alert(
                [
                    html.Div(
                        "This web service is free and open to all users and does not require login."
                    ),
                    html.Div(
                        "It is not usable for commercial product claims without experimental confirmation."
                    ),
                    html.Div("See the license page for detailed terms of use."),
                ],
                color="success",
                className="mt-2 mb-3 text-center",
                is_open=True,
            ),
            # More Info Modal
            create_info_modal(),
            # How to Cite Modal
            create_how_to_cite_modal(),
        ],
        className="mb-4",
        style={"backgroundColor": "transparent"},
    )
