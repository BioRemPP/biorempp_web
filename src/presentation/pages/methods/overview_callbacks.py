"""
Scientific Methods Overview Callbacks - BioRemPP v1.0.

Handles modal interactions for scientific references display.

Functions
---------
toggle_ko_modal
    Toggle KO richness references modal
toggle_compound_modal
    Toggle compound richness references modal
toggle_guilds_modal
    Toggle functional guilds references modal
"""

from dash import Input, Output, callback


@callback(
    Output("ko-refs-modal", "is_open"),
    [Input("ko-refs-modal-open", "n_clicks"), Input("ko-refs-modal-close", "n_clicks")],
    prevent_initial_call=True,
)
def toggle_ko_modal(open_clicks, close_clicks):
    """
    Toggle KO Richness references modal.

    Parameters
    ----------
    open_clicks : int
        Number of open button clicks
    close_clicks : int
        Number of close button clicks

    Returns
    -------
    bool
        Modal open state
    """
    from dash import ctx

    if ctx.triggered_id == "ko-refs-modal-open":
        return True
    return False


@callback(
    Output("compound-refs-modal", "is_open"),
    [
        Input("compound-refs-modal-open", "n_clicks"),
        Input("compound-refs-modal-close", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def toggle_compound_modal(open_clicks, close_clicks):
    """
    Toggle Compound Richness references modal.

    Parameters
    ----------
    open_clicks : int
        Number of open button clicks
    close_clicks : int
        Number of close button clicks

    Returns
    -------
    bool
        Modal open state
    """
    from dash import ctx

    if ctx.triggered_id == "compound-refs-modal-open":
        return True
    return False


@callback(
    Output("guilds-refs-modal", "is_open"),
    [
        Input("guilds-refs-modal-open", "n_clicks"),
        Input("guilds-refs-modal-close", "n_clicks"),
    ],
    prevent_initial_call=True,
)
def toggle_guilds_modal(open_clicks, close_clicks):
    """
    Toggle Functional Guilds references modal.

    Parameters
    ----------
    open_clicks : int
        Number of open button clicks
    close_clicks : int
        Number of close button clicks

    Returns
    -------
    bool
        Modal open state
    """
    from dash import ctx

    if ctx.triggered_id == "guilds-refs-modal-open":
        return True
    return False
