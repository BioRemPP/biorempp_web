"""
Error Pages - BioRemPP v1.0.

Custom 400 and 500 pages following the standard application UI shell.
"""

import dash_bootstrap_components as dbc
from dash import html

from ..errors.http_error_catalog import HttpErrorSpec, get_http_error_spec
from ..components.base import create_footer, create_header
from ..routing import app_path


def _create_error_page(
    spec: HttpErrorSpec,
) -> html.Div:
    """
    Create a standardized error page layout.

    Parameters
    ----------
    spec : HttpErrorSpec
        Catalog-backed error specification.

    Returns
    -------
    html.Div
        Full page layout with header, body, and footer.
    """
    header = create_header(show_nav=True, logo_size="60px")

    content = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardBody(
                                        [
                                            html.Div(
                                                [
                                                    html.Img(
                                                        src=app_path(
                                                            "/assets/HAZARD_LOGO.png"
                                                        ),
                                                        alt="Hazard Warning",
                                                        style={
                                                            "maxWidth": "140px",
                                                            "height": "auto",
                                                        },
                                                        className="mb-3",
                                                    ),
                                                ],
                                                className="text-center",
                                            ),
                                            html.H1(
                                                str(spec.status_code),
                                                className="text-center text-warning mb-2",
                                                style={"fontWeight": "700"},
                                            ),
                                            html.H3(
                                                spec.title,
                                                className="text-center mb-3",
                                            ),
                                            html.P(
                                                spec.message,
                                                className="text-center text-muted mb-2",
                                                style={"fontSize": "1.05rem"},
                                            ),
                                            html.P(
                                                spec.guidance,
                                                className="text-center mb-4",
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        dbc.Button(
                                                            [
                                                                html.I(
                                                                    className=(
                                                                        "fas fa-home me-2"
                                                                    )
                                                                ),
                                                                "Back to Home",
                                                            ],
                                                            href=app_path("/"),
                                                            color="success",
                                                            className="w-100",
                                                        ),
                                                        md=6,
                                                        className="mb-2 mb-md-0",
                                                    ),
                                                    dbc.Col(
                                                        dbc.Button(
                                                            [
                                                                html.I(
                                                                    className=(
                                                                        "fas fa-life-ring me-2"
                                                                    )
                                                                ),
                                                                "Contact Support",
                                                            ],
                                                            href=app_path(
                                                                "/help/contact"
                                                            ),
                                                            color="secondary",
                                                            className="w-100",
                                                        ),
                                                        md=6,
                                                    ),
                                                ],
                                                className="g-2",
                                            ),
                                        ]
                                    )
                                ],
                                className="shadow-sm",
                                style={"border": "2px solid #f0ad4e"},
                            )
                        ],
                        md=10,
                        lg=8,
                        xl=7,
                    )
                ],
                className="justify-content-center",
            )
        ],
        className="py-5",
    )

    footer = create_footer()

    return html.Div([header, content, footer])


def create_error_400_page() -> html.Div:
    """
    Create the Bad Request page (HTTP 400).

    Returns
    -------
    html.Div
        Error page layout for malformed/invalid requests.
    """
    return _create_error_page(get_http_error_spec(400))


def create_error_500_page() -> html.Div:
    """
    Create the Internal Server Error page (HTTP 500).

    Returns
    -------
    html.Div
        Error page layout for unexpected internal failures.
    """
    return _create_error_page(get_http_error_spec(500))
