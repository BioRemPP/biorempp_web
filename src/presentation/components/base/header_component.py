"""
Header Component - Atomic UI Component.

Creates the BioRemPP header with logo, title, and navigation links.

Functions
---------
create_header
    Create header component with logo and navigation

Notes
-----
- Atomic component (no sub-components from this package)
- Reusable across pages
- DashBootstrap styling
- Logo and title link to /about
- Version set to 1.0.0-beta
- Responsive navbar with hamburger menu for mobile
"""

import dash_bootstrap_components as dbc
from dash import html


def create_header(show_nav: bool = True, logo_size: str = "70px") -> dbc.Navbar:
    """
    Create BioRemPP header component with responsive navbar.

    Parameters
    ----------
    show_nav : bool, optional
        Whether to show navigation links, by default True.
    logo_size : str, optional
        CSS size for the logo image, by default "70px".

    Returns
    -------
    dbc.Navbar
        Responsive navbar with logo, title, and collapsible navigation.

    Notes
    -----
    - Logo on the left and clickable (routes to /about)
    - Title/subtitle left-aligned and clickable (routes to /about)
    - Navigation links collapse into hamburger menu on mobile
    - Fully responsive layout
    """

    # Brand section (logo + title)
    brand = html.A(
        dbc.Row(
            [
                dbc.Col(
                    html.Img(
                        src="/assets/BIOREMPP_LOGO.png",
                        style={"height": logo_size, "width": "auto"},
                        alt="BioRemPP Logo",
                    ),
                    width="auto",
                ),
                dbc.Col(
                    html.Div(
                        [
                            html.H3(
                                "BioRemPP 1.0.0-beta",
                                className="mb-0 text-success fw-bold",
                                style={"lineHeight": "1.1", "fontSize": "1.5rem"},
                            ),
                            html.Div(
                                "Bioremediation Potential Profile",
                                className="text-muted d-none d-sm-block",
                                style={"fontSize": "0.85rem"},
                            ),
                        ]
                    ),
                    width="auto",
                ),
            ],
            align="center",
            className="g-2",
        ),
        href="/about",
        style={"textDecoration": "none"},
        className="navbar-brand",
    )

    # Navigation links
    nav_items = []
    if show_nav:
        nav_items = [
            dbc.NavItem(dbc.NavLink("Home", href="/about", className="px-2")),
            dbc.NavItem(dbc.NavLink("Methods", href="/methods", className="px-2")),
            dbc.NavItem(
                dbc.NavLink("User Guide", href="/help/user-guide", className="px-2")
            ),
            dbc.NavItem(dbc.NavLink("FAQ", href="/faq", className="px-2")),
            dbc.NavItem(
                dbc.NavLink("Regulatory", href="/regulatory", className="px-2")
            ),
            dbc.NavItem(
                dbc.NavLink("Documentation", href="/documentation", className="px-2")
            ),
            dbc.NavItem(dbc.NavLink("Contact", href="/help/contact", className="px-2")),
        ]

    # Create responsive navbar
    navbar = dbc.Navbar(
        dbc.Container(
            [
                brand,
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    dbc.Nav(nav_items, className="ms-auto", navbar=True),
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ],
            fluid=True,
        ),
        color="white",
        dark=False,
        className="border-bottom shadow-sm",
    )

    return navbar
