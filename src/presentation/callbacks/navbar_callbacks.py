"""
Navbar Callbacks - BioRemPP v1.0

Handles navbar toggler functionality for responsive mobile menu.

Functions
---------
toggle_navbar_collapse
    Toggle navbar collapse state when hamburger menu is clicked
"""

from dash import Input, Output, State, callback


@callback(
    Output("navbar-collapse", "is_open"),
    [Input("navbar-toggler", "n_clicks")],
    [State("navbar-collapse", "is_open")],
)
def toggle_navbar_collapse(n_clicks, is_open):
    """
    Toggle navbar collapse when hamburger menu button is clicked.

    Parameters
    ----------
    n_clicks : int
        Number of times the navbar toggler has been clicked
    is_open : bool
        Current state of the navbar collapse

    Returns
    -------
    bool
        New state of navbar collapse (True = open, False = closed)

    Notes
    -----
    - Called when user clicks hamburger menu icon on mobile
    - Toggles between open and closed states
    - No initial call (prevent_initial_call=False by default)
    """
    if n_clicks:
        return not is_open
    return is_open
