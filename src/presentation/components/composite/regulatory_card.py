"""
Regulatory Card Component - BioRemPP v1.0.

Reusable card components for regulatory agencies and frameworks.

Functions
---------
create_regulatory_card
    Create card for regulatory agency/framework
create_reference_table
    Create table of regulatory references
create_info_alert
    Create informational alert box

Notes
-----
- Uses Dash Bootstrap Components
- Consistent styling with FAQ components
- Supports external links
"""

from typing import Dict, List

import dash_bootstrap_components as dbc
from dash import html


def create_regulatory_card(
    title: str,
    acronym: str,
    description: str,
    country: str,
    icon: str = "fa-landmark",
    color: str = "success",
) -> dbc.Card:
    """
    Create regulatory agency information card.

    Parameters
    ----------
    title : str
        Full name of regulatory agency/framework
    acronym : str
        Agency acronym
    description : str
        Description of agency's role and focus
    country : str
        Country or region
    icon : str, optional
        FontAwesome icon class (default: "fa-landmark")
    color : str, optional
        Bootstrap color for accent (default: "success")

    Returns
    -------
    dbc.Card
        Styled card component

    Examples
    --------
    >>> card = create_regulatory_card(
    ...     title="Environmental Protection Agency",
    ...     acronym="EPA",
    ...     description="Regulates pollutants...",
    ...     country="USA"
    ... )
    """
    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.Div(
                        [
                            html.I(className=f"fas {icon} fa-2x text-{color} mb-2"),
                            html.H5(acronym, className="mb-0 mt-2"),
                            html.Small(country, className="text-muted"),
                        ],
                        className="text-center",
                    )
                ],
                className=f"bg-light border-{color} border-top border-3",
            ),
            dbc.CardBody(
                [
                    html.H6(title, className="card-title text-center mb-3"),
                    html.P(description, className="card-text small"),
                ]
            ),
        ],
        className="h-100 shadow-sm hover-shadow",
    )


def create_reference_table(references: List[Dict[str, str]]) -> dbc.Table:
    """
    Create table of regulatory references with URLs.

    Parameters
    ----------
    references : List[Dict[str, str]]
        List of reference dictionaries with 'agency' and 'url' keys

    Returns
    -------
    dbc.Table
        Responsive table with references

    Examples
    --------
    >>> refs = [
    ...     {"agency": "ATSDR", "url": "https://..."},
    ...     {"agency": "EPA", "url": "https://..."}
    ... ]
    >>> table = create_reference_table(refs)
    """
    table_header = [
        html.Thead(
            [
                html.Tr(
                    [
                        html.Th(
                            "Agency / Framework", className="bg-success text-white"
                        ),
                        html.Th("Reference (URL)", className="bg-success text-white"),
                    ]
                )
            ]
        )
    ]

    table_rows = []
    for ref in references:
        table_rows.append(
            html.Tr(
                [
                    html.Td(html.Strong(ref["agency"]), className="align-middle"),
                    html.Td(
                        [
                            html.A(
                                [
                                    html.I(className="fas fa-external-link-alt me-2"),
                                    ref["url"],
                                ],
                                href=ref["url"],
                                target="_blank",
                                className="text-decoration-none small",
                            )
                        ],
                        className="align-middle",
                    ),
                ]
            )
        )

    table_body = [html.Tbody(table_rows)]

    return dbc.Table(
        table_header + table_body,
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        className="mb-0",
    )


def create_info_alert(
    message: str,
    alert_type: str = "info",
    icon: str = "fa-info-circle",
    dismissable: bool = False,
) -> dbc.Alert:
    """
    Create informational alert box.

    Parameters
    ----------
    message : str
        Alert message text
    alert_type : str, optional
        Bootstrap alert type (default: "info")
        Options: "info", "success", "warning", "danger"
    icon : str, optional
        FontAwesome icon class (default: "fa-info-circle")
    dismissable : bool, optional
        Whether alert can be dismissed (default: False)

    Returns
    -------
    dbc.Alert
        Styled alert component

    Examples
    --------
    >>> alert = create_info_alert(
    ...     "Important information",
    ...     alert_type="warning"
    ... )
    """
    return dbc.Alert(
        [html.I(className=f"fas {icon} me-2"), message],
        color=alert_type,
        dismissable=dismissable,
        className="mb-3",
    )


def create_pollutant_category_card(
    category: str, description: str, examples: List[str], icon: str = "fa-flask"
) -> dbc.Card:
    """
    Create card for pollutant category information.

    Parameters
    ----------
    category : str
        Pollutant category name
    description : str
        Description of category
    examples : List[str]
        List of example compounds
    icon : str, optional
        FontAwesome icon class (default: "fa-flask")

    Returns
    -------
    dbc.Card
        Styled card component

    Examples
    --------
    >>> card = create_pollutant_category_card(
    ...     category="Heavy Metals",
    ...     description="Toxic metallic elements...",
    ...     examples=["Lead", "Mercury", "Cadmium"]
    ... )
    """
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.Div(
                        [
                            html.I(className=f"fas {icon} fa-2x text-danger mb-3"),
                            html.H5(category, className="mb-3"),
                            html.P(description, className="mb-3"),
                            html.Hr(),
                            html.H6("Examples:", className="mb-2"),
                            html.Ul(
                                [
                                    html.Li(example, className="small")
                                    for example in examples
                                ]
                            ),
                        ]
                    )
                ]
            )
        ],
        className="h-100 shadow-sm",
    )
