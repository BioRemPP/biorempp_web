"""
Documentation Page - BioRemPP v1.0.

Documentation hub page providing access to database and webservice documentation.

Functions
---------
create_documentation_card
    Create documentation card with icon, description, and link
create_documentation_page
    Create complete documentation page layout
get_layout
    Get documentation page layout (Dash entry point)

Notes
-----
- Two symmetric cards: Database Documentation and Webservice Documentation
- Responsive Bootstrap design
- Follows application design patterns and standards
- PEP 8, Black, and Flake8 compliant
"""

import dash_bootstrap_components as dbc
from dash import html

from ..components.base import create_footer, create_header


def create_documentation_card(
    title: str,
    description: str,
    icon_class: str,
    link_url: str,
    link_text: str = "Access Documentation",
    card_color: str = "success",
) -> dbc.Card:
    """
    Create documentation card with icon, description, and external link.

    Parameters
    ----------
    title : str
        Card title
    description : str
        Brief description of the documentation
    icon_class : str
        FontAwesome icon class (e.g., "fas fa-database")
    link_url : str
        External URL to documentation
    link_text : str, optional
        Text for the link button, by default "Access Documentation"
    card_color : str, optional
        Bootstrap color theme, by default "success"

    Returns
    -------
    dbc.Card
        Styled documentation card component

    Examples
    --------
    >>> card = create_documentation_card(
    ...     title="Database Documentation",
    ...     description="Comprehensive guide to the BioRemPP database",
    ...     icon_class="fas fa-database",
    ...     link_url="https://docs.biorempp.com/database"
    ... )

    Notes
    -----
    - Card includes icon, title, description, and external link button
    - Follows DRY principle for reusable card creation
    - Maintains consistent styling across documentation cards
    """
    return dbc.Card(
        [
            dbc.CardBody(
                [
                    # Icon
                    html.Div(
                        [
                            html.I(
                                className=f"{icon_class} text-{card_color}",
                                style={"fontSize": "4rem"},
                            )
                        ],
                        className="text-center mb-4",
                    ),
                    # Title
                    html.H3(title, className="text-center mb-3"),
                    # Logo placeholder (will be replaced by user)
                    html.Div(
                        [
                            html.Img(
                                src="/assets/BIOREMPP_LOGO.png",
                                alt="BioRemPP Logo",
                                style={
                                    "maxWidth": "200px",
                                    "height": "auto",
                                    "opacity": "0.8",
                                },
                                className="mb-4",
                            )
                        ],
                        className="text-center",
                    ),
                    # Description
                    html.P(
                        description,
                        className="text-center text-muted mb-4",
                        style={"fontSize": "1.05rem", "lineHeight": "1.6"},
                    ),
                    # External link button
                    html.Div(
                        [
                            dbc.Button(
                                [
                                    html.I(className="fas fa-external-link-alt me-2"),
                                    link_text,
                                ],
                                href=link_url,
                                target="_blank",
                                color=card_color,
                                size="lg",
                                className="w-100",
                                external_link=True,
                            )
                        ],
                        className="d-grid",
                    ),
                ]
            )
        ],
        className="h-100 shadow-sm",
        style={"border": f"2px solid var(--bs-{card_color})"},
    )


def create_documentation_page() -> html.Div:
    """
    Create documentation page layout.

    Returns
    -------
    html.Div
        Complete documentation page with header, intro, cards, and footer

    Examples
    --------
    >>> doc_layout = create_documentation_page()

    Notes
    -----
    Page Structure:
    1. Header with navigation
    2. Page title and introduction
    3. Framework description
    4. Two symmetric documentation cards:
       - Database Documentation
       - Webservice Documentation
    5. Footer

    Design Principles:
    - SOLID: Single responsibility for each function
    - DRY: Reusable card creation function
    - Clean Code: Clear naming and documentation
    - Responsive: Bootstrap grid system for all screen sizes
    """
    # Header
    header = create_header(show_nav=True, logo_size="60px")

    # Page title and intro
    page_intro = html.Div(
        [
            html.H1(
                [
                    html.I(className="fas fa-book me-3 text-success"),
                    "Documentation",
                ],
                className="text-center mb-3",
            ),
            html.P(
                "Access comprehensive documentation for the BioRemPP framework",
                className="text-center text-muted mb-4 lead",
            ),
            html.Hr(),
        ],
        className="mb-5",
    )

    # Framework description
    framework_description = dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H4(
                        [
                            html.I(className="fas fa-info-circle me-2 text-success"),
                            "About BioRemPP Framework",
                        ],
                        className="mb-3",
                    ),
                    html.P(
                        [
                            html.Strong("BioRemPP"),
                            " is a comprehensive framework composed of two main components:",
                        ],
                        className="mb-3",
                        style={"fontSize": "1.05rem"},
                    ),
                    html.Ul(
                        [
                            html.Li(
                                [
                                    html.Strong("Database: "),
                                    "An integrated resource designed to support environmental "
                                    "bioremediation research by systematically linking chemical "
                                    "compounds, genes, enzymes, and regulatory references.",
                                ],
                                className="mb-2",
                            ),
                            html.Li(
                                [
                                    html.Strong("Webservice: "),
                                    "A powerful web-based platform built to provide interactive "
                                    "analysis, visualization, and exploration of bioremediation data.",
                                ],
                                className="mb-2",
                            ),
                        ],
                        style={"fontSize": "1rem"},
                    ),
                    html.P(
                        [
                            "Together, these components enable researchers to explore and analyze "
                            "bioremediation potential through an intuitive, data-driven interface."
                        ],
                        className="text-muted mt-3",
                        style={"fontSize": "0.95rem"},
                    ),
                ]
            )
        ],
        className="shadow-sm mb-5",
    )

    # Documentation cards section
    documentation_cards = html.Div(
        [
            html.H2(
                [
                    html.I(className="fas fa-file-alt me-2 text-success"),
                    "Documentation Resources",
                ],
                className="text-center mb-4",
            ),
            dbc.Row(
                [
                    # Database Documentation Card
                    dbc.Col(
                        [
                            create_documentation_card(
                                title="Database Documentation",
                                description=(
                                    "Comprehensive guide to the BioRemPP database structure, "
                                    "data sources, schema design, and usage instructions. "
                                    "Learn about chemical compounds, genes, enzymes, and "
                                    "regulatory information integrated in our system."
                                ),
                                icon_class="fas fa-database",
                                link_url="https://readthedocs.org",
                                link_text="View Database Docs",
                                card_color="success",
                            )
                        ],
                        width=12,
                        md=6,
                        className="mb-4",
                    ),
                    # Webservice Documentation Card
                    dbc.Col(
                        [
                            create_documentation_card(
                                title="Webservice Documentation",
                                description=(
                                    "Complete guide to the BioRemPP webservice platform. "
                                    "Explore API endpoints, analysis workflows, visualization "
                                    "tools, and integration examples. Learn how to leverage "
                                    "the platform for your bioremediation research."
                                ),
                                icon_class="fas fa-server",
                                link_url="https://readthedocs.org",
                                link_text="View Webservice Docs",
                                card_color="primary",
                            )
                        ],
                        width=12,
                        md=6,
                        className="mb-4",
                    ),
                ],
                className="justify-content-center",
            ),
        ],
        className="mb-5",
    )

    # Footer
    footer = create_footer(version="1.0.0", year=2024)

    # Assemble complete layout
    layout = html.Div(
        [
            header,
            dbc.Container(
                [page_intro, framework_description, documentation_cards],
                fluid=False,
                className="px-4 py-4",
            ),
            footer,
        ],
        id="documentation-page",
    )

    return layout


def get_layout() -> html.Div:
    """
    Get documentation page layout (alias for create_documentation_page).

    Returns
    -------
    html.Div
        Documentation page layout

    Notes
    -----
    This function is called by Dash when rendering the documentation page.
    Entry point for the Dash multi-page application routing system.
    """
    return create_documentation_page()
