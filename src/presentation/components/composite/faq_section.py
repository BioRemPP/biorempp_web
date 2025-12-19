"""
FAQ Section Component - Composite UI Component.

Creates organized FAQ sections grouped by category.

Functions
---------
create_faq_section
    Create FAQ section with multiple items

Notes
-----
- Groups related FAQ items by topic
- Uses accordion for expandable items
- Supports icons and custom styling
"""

from typing import List

import dash_bootstrap_components as dbc
from dash import html


def create_faq_section(
    title: str,
    items: List[dbc.AccordionItem],
    section_icon: str = "fa-folder-open",
    section_id: str = None,
) -> html.Div:
    """
    Create FAQ section with grouped items.

    Parameters
    ----------
    title : str
        Section title (e.g., "Getting Started", "File Upload")
    items : List[dbc.AccordionItem]
        List of FAQ accordion items
    section_icon : str, optional
        FontAwesome icon for section header, by default "fa-folder-open"
    section_id : str, optional
        HTML ID for the section, by default None

    Returns
    -------
    html.Div
        Complete FAQ section with header and accordion

    Examples
    --------
    >>> from .faq_item import create_faq_item
    >>> items = [
    ...     create_faq_item(
    ...         "What is BioRemPP?",
    ...         "A bioremediation analysis tool.",
    ...         "faq-1"
    ...     ),
    ...     create_faq_item(
    ...         "How do I start?",
    ...         "Upload your file file.",
    ...         "faq-2"
    ...     )
    ... ]
    >>> section = create_faq_section(
    ...     title="Getting Started",
    ...     items=items,
    ...     section_id="faq-getting-started"
    ... )

    Notes
    -----
    - Section header styled with green accent
    - Items grouped in accordion
    - Responsive layout
    - Supports unlimited items per section
    """
    section_header = html.H4(
        [html.I(className=f"fas {section_icon} me-2 text-success"), title],
        className="mb-3 mt-4",
    )

    accordion = dbc.Accordion(
        children=items,
        id=section_id or f"faq-section-{title.lower().replace(' ', '-')}",
        start_collapsed=True,
        flush=False,
        className="mb-4",
    )

    return html.Div([section_header, accordion], className="faq-section mb-5")


def create_faq_search_bar() -> dbc.Input:
    """
    Create search bar for filtering FAQ items.

    Returns
    -------
    dbc.Input
        Search input field

    Examples
    --------
    >>> search = create_faq_search_bar()

    Notes
    -----
    - Placeholder text guides users
    - Can be connected to callback for live filtering
    - Styled with search icon
    """
    return html.Div(
        [
            html.Div(
                [
                    html.I(
                        className="fas fa-search position-absolute text-muted",
                        style={
                            "top": "50%",
                            "left": "15px",
                            "transform": "translateY(-50%)",
                        },
                    ),
                    dbc.Input(
                        id="faq-search-input",
                        type="text",
                        placeholder=(
                            "Search FAQ... (e.g., 'upload', 'format', 'error')"
                        ),
                        className="ps-5",
                        debounce=True,
                    ),
                ],
                className="position-relative mb-4",
            )
        ]
    )


def create_faq_quick_links(sections: List[dict]) -> dbc.Card:
    """
    Create quick navigation links to FAQ sections.

    Parameters
    ----------
    sections : List[dict]
        List of section dictionaries with 'title' and 'id' keys

    Returns
    -------
    dbc.Card
        Card with quick navigation links

    Examples
    --------
    >>> sections = [
    ...     {"title": "Getting Started", "id": "getting-started"},
    ...     {"title": "File Upload", "id": "file-upload"},
    ...     {"title": "Troubleshooting", "id": "troubleshooting"}
    ... ]
    >>> quick_links = create_faq_quick_links(sections)

    Notes
    -----
    - Sticky positioning option
    - Links scroll to section
    - Compact design
    """
    links = []
    for section in sections:
        link = html.Li(
            [
                html.A(
                    [
                        html.I(className="fas fa-arrow-right me-2 text-success"),
                        section["title"],
                    ],
                    href=f"#{section['id']}",
                    className="text-decoration-none text-dark",
                )
            ],
            className="mb-2",
        )
        links.append(link)

    return dbc.Card(
        [
            dbc.CardHeader(
                [
                    html.I(className="fas fa-compass me-2"),
                    html.Strong("Quick Navigation"),
                ],
                className="bg-light",
            ),
            dbc.CardBody([html.Ul(links, className="list-unstyled mb-0")]),
        ],
        className="shadow-sm mb-4",
    )
