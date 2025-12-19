"""
Footer Component - Atomic UI Component.

Creates application footer with version, copyright, and links.

Functions
---------
create_footer
    Create footer component with metadata

Notes
-----
- Atomic component
- Shows version, copyright, contact info
- Links to external resources
"""

from typing import Any, Dict, List, Optional

import dash_bootstrap_components as dbc
from dash import html


def create_footer(
    version: str = "1.0.0",
    year: int = 2022,
    show_links: bool = True,
    additional_links: Optional[List[Dict[str, str]]] = None,
) -> html.Footer:
    """
    Create footer component.

    Parameters
    ----------
    version : str, optional
        Application version number, by default "1.0.0"
    year : int, optional
        Copyright year, by default 2025
    show_links : bool, optional
        Display resource links, by default True
    additional_links : Optional[List[Dict[str, str]]], optional
        Additional links to display, by default None
        Format: [{"label": "Link Text", "url": "https://..."}]

    Returns
    -------
    html.Footer
        Footer component with metadata and links

    Examples
    --------
    >>> footer = create_footer()
    >>> footer = create_footer(version="1.0.0", year=2025)
    >>> footer = create_footer(
    ...     additional_links=[
    ...         {"label": "GitHub", "url": "https://github.com/..."}
    ...     ]
    ... )

    Notes
    -----
    - Three columns: version info, links, contact
    - Responsive layout (stacks on mobile)
    - Subtle background color
    - Centered text alignment
    """
    version_info = html.Div(
        [
            html.P(
                f"BioRemPP v{version}", className="mb-1 font-weight-bold text-success"
            ),
            html.P(
                f"© {year} BioRemPP Development Team",
                className="mb-0 text-muted",
                style={"fontSize": "0.85rem"},
            ),
        ]
    )

    default_links = [
        {"label": "Documentation", "url": "/documentation"},
    ]

    if additional_links:
        default_links.extend(additional_links)

    links_section = html.Div()
    if show_links:
        link_items = [
            html.A(
                link["label"],
                href=link["url"],
                className="text-muted me-3",
                style={"fontSize": "0.85rem", "textDecoration": "none"},
                target="_blank" if link["url"].startswith("http") else None,
            )
            for link in default_links
        ]
        links_section = html.Div(
            link_items, className="d-flex flex-wrap justify-content-center"
        )

    contact_info = html.Div(
        [
            html.P(
                "Contact: biorempp@gmail.com",
                className="mb-0 text-muted",
                style={"fontSize": "0.85rem"},
            )
        ]
    )

    footer_content = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        version_info,
                        md=4,
                        className="text-center text-md-start mb-2 mb-md-0",
                    ),
                    dbc.Col(links_section, md=4, className="text-center mb-2 mb-md-0"),
                    dbc.Col(contact_info, md=4, className="text-center text-md-end"),
                ],
                align="center",
                className="py-3",
            )
        ],
        fluid=True,
    )

    return html.Footer(
        footer_content,
        className="bg-light border-top mt-5",
        style={"bottom": "0", "width": "100%"},
    )
