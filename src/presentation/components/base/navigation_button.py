"""
Navigation Button Component - BioRemPP v1.0
===========================================

Floating navigation button for quick access to modules and use cases.

Functions
---------
create_navigation_button
    Create floating navigation button positioned in bottom

Notes
-----
- Fixed position button (similar to Dash debug button)
- Bootstrap primary color with shadow
- Font Awesome compass icon
- Z-index ensures visibility above content
- Only visible on results page
"""

import dash_bootstrap_components as dbc
from dash import html


def create_navigation_button() -> html.Div:
    """
    Create floating navigation button.

    Returns
    -------
    html.Div
        Floating button container with navigation toggle button

    Notes
    -----
    Button Properties:
    - Position: Fixed bottom-right (20px from edges)
    - Icon: fa-compass (navigation theme)
    - Color: Bootstrap primary
    - Shadow: Large shadow for prominence
    - Z-index: 1050 (above modals, below toasts)
    - Tooltip: "Navigate" (left placement)

    Interaction:
    - Click toggles offcanvas navigation panel
    - Callback ID: 'nav-toggle-button'

    Examples
    --------
    >>> button = create_navigation_button()
    >>> # Add to results page layout

    See Also
    --------
    create_navigation_offcanvas : Offcanvas panel component
    navigation_callbacks : Button interaction callbacks
    """
    button = dbc.Button(
        html.I(className="fas fa-compass"),
        id="nav-toggle-button",
        color="primary",
        className="shadow-lg nav-button-v2",
        size="lg",
        n_clicks=0,
        style={
            "borderRadius": "50%",
            "width": "56px",
            "height": "56px",
            "padding": "0",
            "display": "flex",
            "alignItems": "center",
            "justifyContent": "center",
            "fontSize": "20px",
        },
    )

    # Tooltip for the button
    tooltip = dbc.Tooltip("Navigate", target="nav-toggle-button", placement="left")

    # Floating container
    floating_container = html.Div(
        [button, tooltip],
        id="navigation-button-container",
        style={
            "position": "fixed",
            "bottom": "80px",  # Above footer
            "right": "20px",
            "zIndex": "999",  # Below footer but above content
        },
    )

    return floating_container
