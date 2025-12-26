import dash_bootstrap_components as dbc
from dash import html

from .info_modal import create_info_modal


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
                            href="/how-to-cite",
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
                            src="/assets/BIOREMPP_LOGO.png",
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
                                    "The Bioremediation Potential Profile (BioRemPP) is a scientific web application "
                                    "designed to explore the biotechnological potential of microbial, fungal, and plant "
                                    "genomes for bioremediation purposes.",
                                    className=text_class,
                                ),
                                html.P(
                                    "BioRemPP enables functional analysis of annotated genomes through integration with "
                                    "multiple curated bioremediation-related databases and supports the understanding of "
                                    "degradation mechanisms, metabolic pathways, enzymatic functions, and relationships "
                                    "between samples, genes, compounds, toxic compound associations, and other significant "
                                    "biological results.",
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
                    "BioRemPP is free and open to all users and there is no login requirement. ",
                    "No data are collected or saved, as BioRemPP works with session-based storage.",
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
