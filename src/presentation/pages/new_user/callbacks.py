"""
New User Guide Callbacks

Handles modal open/close interactions for the new user guide.
"""

from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate


def register_new_user_guide_callbacks(app):
    """
    Register callbacks for new user guide modal.

    Parameters
    ----------
    app : Dash
        Dash application instance
    """

    @app.callback(
        Output("new-user-guide-modal", "is_open"),
        [
            Input("new-user-guide-btn", "n_clicks"),
            Input("new-user-guide-close", "n_clicks"),
        ],
        [State("new-user-guide-modal", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_new_user_guide_modal(open_clicks, close_clicks, is_open):
        """
        Toggle new user guide modal open/close.

        Parameters
        ----------
        open_clicks : int
            Number of clicks on open button
        close_clicks : int
            Number of clicks on close button
        is_open : bool
            Current modal state

        Returns
        -------
        bool
            New modal state
        """
        return not is_open
