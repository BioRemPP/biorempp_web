"""
Analytical highlight badge component for BioRemPP application.

This module provides a styled badge component that displays an analytical
highlight indicator using Bootstrap badge styling. The component serves
as a visual element to draw attention to important analytical sections
or features within the application interface.

The component utilizes Dash Bootstrap Components for consistent styling
and responsive design, providing a professional appearance that integrates
seamlessly with the overall application design system.

Functions
---------
analytical_highlight_component : function
    Creates analytical highlight badge with success styling and pill design
"""

import dash_bootstrap_components as dbc
from dash import html


def analytical_highlight_component():
    """
    Create analytical highlight badge component.

    Creates a Bootstrap badge component styled as a success pill badge
    for highlighting analytical sections or important features within
    the application interface. The badge is centered and sized to fit
    content width with appropriate spacing.

    Returns
    -------
    dash_bootstrap_components.Badge
        Success-colored pill badge with "Analytical Highlight" text,
        centered alignment, and responsive styling for visual emphasis

    Notes
    -----
    The component uses Bootstrap's success color scheme and pill styling
    for consistent visual integration with the application design system.
    """
    return dbc.Badge(
        "Analytical Highlight",
        color="success",
        className="mx-auto mb-2 d-block",
        pill=True,
        style={"width": "fit-content"},
    )
