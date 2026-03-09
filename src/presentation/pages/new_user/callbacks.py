"""
New User Callbacks.

Handles modal interactions for new user guide and terms of use.
"""

from dash import Input, Output, State


def register_new_user_guide_callbacks(app):
    """
    Register callbacks for new user guide modal.

    Parameters
    ----------
    app : Dash
        Dash application instance
    """

    @app.callback(
        Output("onboarding-walkthrough-dialog", "is_open"),
        [
            Input("onboarding-walkthrough-open", "n_clicks"),
            Input("onboarding-walkthrough-close", "n_clicks"),
        ],
        [State("onboarding-walkthrough-dialog", "is_open")],
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

    @app.callback(
        Output("terms-modal", "is_open"),
        [
            Input("terms-btn", "n_clicks"),
            Input("terms-close", "n_clicks"),
        ],
        [State("terms-modal", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_terms_modal(open_clicks, close_clicks, is_open):
        """
        Toggle terms of use modal open/close.

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

    @app.callback(
        Output("how-to-cite-modal", "is_open"),
        [
            Input("how-to-cite-btn", "n_clicks"),
            Input("how-to-cite-close", "n_clicks"),
        ],
        [State("how-to-cite-modal", "is_open")],
        prevent_initial_call=True,
    )
    def toggle_how_to_cite_modal(open_clicks, close_clicks, is_open):
        """
        Toggle how-to-cite modal open/close.

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
