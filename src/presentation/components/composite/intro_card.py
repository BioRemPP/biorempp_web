import dash_bootstrap_components as dbc
from dash import html

from .info_modal import create_info_modal
from src.presentation.routing import app_path


def create_intro_card() -> html.Div:
    """
    Create an introduction block with the BioRemPP logo, description,
    a privacy/info alert, and a styled "How to cite" section (no Toast).

    Returns
    -------
    html.Div
        A container holding the intro content.
    """
    text_class = "text-dark"

    how_to_cite_card = dbc.Card(
        [
            dbc.CardHeader(
                "How to cite",
                className="text-center fw-semibold",
                style={
                    "fontSize": "1.25rem",
                    "backgroundColor": "transparent",
                    "borderBottom": "1px solid #e9ecef",
                    "paddingTop": "0.9rem",
                    "paddingBottom": "0.9rem",
                },
            ),
            dbc.CardBody(
                [
                    html.P(
                        [
                            html.I("Citation placeholder "),
                        ],
                        className="text-dark mb-3",
                        style={"fontSize": "1.02rem"},
                    ),
                    html.Div(
                        dbc.Button(
                            [
                                html.I(className="fas fa-quote-right me-2"),
                                "How to Cite",
                            ],
                            href=app_path("/how-to-cite"),
                            color="success",
                            outline=True,
                            size="sm",
                        ),
                        className="text-center",
                    ),
                ],
                className="text-center",
                style={"paddingTop": "1.2rem", "paddingBottom": "1.2rem"},
            ),
        ],
        className="w-100 shadow-sm rounded-3 mb-5",
        style={
            "backgroundColor": "#ffffff",
            "border": "1px solid #e9ecef",
            "marginBottom": "4rem",  # extra spacing from the section below
        },
    )

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
                                # More Info button
                                html.Div(
                                    dbc.Button(
                                        "More Info",
                                        id="info-modal-open-button",
                                        color="primary",
                                        outline=True,
                                        size="md",
                                        className="mt-2",
                                        n_clicks=0,
                                    ),
                                    className="text-center",
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
                    "This web service is free and open to all users and does not require login. "
                    "It is not usable for commercial product claims without experimental confirmation. "
                    "See the license page for detailed terms of use.",
                ],
                color="success",
                className="mt-2 mb-3 text-center",
                is_open=True,
            ),
            # Styled "How to cite" section (replaces Toast)
            how_to_cite_card,
            # More Info Modal
            create_info_modal(),
        ],
        className="mb-4",
        style={"backgroundColor": "transparent"},
    )
