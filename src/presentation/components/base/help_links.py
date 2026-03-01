"""
Help Links Component - Atomic UI Component.

Creates help and guidance links section.

Functions
---------
create_help_links
    Create help links with icons and descriptions

Notes
-----
- Atomic component
- Quick access to documentation
- Icon-based navigation
"""

from typing import Any, Dict, List

import dash_bootstrap_components as dbc
from dash import html

from src.presentation.routing import app_path


def create_help_links(custom_links: List[Dict[str, Any]] = None) -> dbc.Card:
    """
    Create help links component.

    Parameters
    ----------
    custom_links : List[Dict[str, Any]], optional
        Custom help links to display, by default None
        Format: [{
            "title": "Link Title",
            "description": "Brief description",
            "icon": "fas fa-icon-name",
            "url": "/path"
        }]

    Returns
    -------
    dbc.Card
        Card containing help links

    Examples
    --------
    >>> help_section = create_help_links()
    >>> custom = [{
    ...     "title": "Tutorial",
    ...     "description": "Step-by-step guide",
    ...     "icon": "fas fa-graduation-cap",
    ...     "url": "/tutorial"
    ... }]
    >>> help_section = create_help_links(custom)

    Notes
    -----
    - Default links: Contact Support, Publications and Awards
    - Icons enhance visual recognition
    - Responsive grid layout (3 columns)
    - Hover effects for interactivity
    """
    # Import here to avoid circular import
    from ..composite.publications_modal import create_publications_modal

    default_links = [
        {
            "title": "Contact Support",
            "description": "Get help from our team",
            "icon": "fas fa-envelope",
            "url": app_path("/help/contact"),
        },
        {
            "title": "Publications and Awards",
            "description": "Scientific publications and recognitions",
            "icon": "fas fa-trophy",
            "url": app_path("/help/publications"),
        },
    ]

    links = custom_links if custom_links else default_links

    link_cards = []
    for link in links:
        # Create card body content
        card_body = dbc.CardBody(
            [
                html.Div(
                    [
                        html.I(className=f"{link['icon']} fa-2x text-success mb-2"),
                        html.H5(link["title"], className="card-title mt-2"),
                        html.P(
                            link["description"],
                            className="card-text text-muted",
                            style={"fontSize": "0.9rem"},
                        ),
                    ],
                    className="text-center",
                )
            ]
        )

        # Create card with or without ID depending on title
        if link["title"] == "Publications and Awards":
            # Wrap in html.Div with ID to capture clicks (modal)
            card_component = html.Div(
                dbc.Card(
                    [card_body],
                    className="h-100 shadow-sm",
                    style={"cursor": "pointer"},
                ),
                id="publications-card",
                n_clicks=0,
            )
        else:
            # Wrap in html.A to make it a clickable link
            card_component = html.A(
                dbc.Card(
                    [card_body],
                    className="h-100 shadow-sm",
                    style={"cursor": "pointer"},
                ),
                href=link["url"],
                style={"textDecoration": "none", "color": "inherit"},
            )

        md_cols = 6 if len(links) == 2 else 4
        card = dbc.Col([card_component], md=md_cols, className="mb-3")
        link_cards.append(card)

    return html.Div(
        [
            dbc.Card(
                [
                    dbc.CardHeader(
                        [
                            html.I(className="fas fa-life-ring me-2"),
                            html.Span("Other Links", className="font-weight-bold"),
                        ],
                        className="bg-light",
                    ),
                    dbc.CardBody(
                        [
                            html.P(
                                "Check out these resources", className="text-muted mb-3"
                            ),
                            dbc.Row(link_cards),
                        ]
                    ),
                ],
                className="mb-4",
            ),
            # Publications Modal
            create_publications_modal(),
        ]
    )
