"""
Methods Page Callbacks

Dash callbacks for Methods page interactivity.
"""

import dash_bootstrap_components as dbc
from dash import ALL, MATCH, Input, Output, State, ctx, html

from .methods_service import get_methods_service
from .module_section import create_module_section
from .pagination import create_pagination


def register_callbacks(app):
    """
    Register all callbacks for the Methods page.

    Args:
        app: Dash application instance
    """

    # Main callback to update content based on current module
    @app.callback(
        [
            Output("methods-module-content", "children"),
            Output("methods-pagination-bottom", "children"),
        ],
        [
            Input("methods-current-module", "data"),
        ],
        prevent_initial_call=False,
    )
    def update_module_content(current_module):
        """
        Update module content and pagination based on current module.

        Args:
            current_module: Currently selected module number

        Returns:
            Tuple of (module_content, bottom_pagination)
        """
        # Default to module 1 if no current module
        if current_module is None:
            current_module = 1

        # Load workflows for the module
        try:
            service = get_methods_service()
            workflows = service.get_workflows_by_module(current_module)

            # Create module section
            module_content = create_module_section(current_module, workflows)

            # Create pagination (bottom only)
            pagination = create_pagination(current_module)

            return module_content, pagination

        except Exception as e:
            # Error handling
            error_content = dbc.Alert(
                [
                    html.H4("Error Loading Workflows", className="alert-heading"),
                    html.P(f"An error occurred while loading the workflows: {str(e)}"),
                    html.Hr(),
                    html.P(
                        "Please try refreshing the page or contact support if the problem persists.",
                        className="mb-0",
                    ),
                ],
                color="danger",
                className="mt-4",
            )

            pagination = create_pagination(current_module)

            return error_content, pagination

    # Callback to handle pagination button clicks
    @app.callback(
        Output("methods-current-module", "data"),
        [
            Input("methods-pagination-prev", "n_clicks"),
            Input("methods-pagination-next", "n_clicks"),
            Input("methods-pagination-1", "n_clicks"),
            Input("methods-pagination-2", "n_clicks"),
            Input("methods-pagination-3", "n_clicks"),
            Input("methods-pagination-4", "n_clicks"),
            Input("methods-pagination-5", "n_clicks"),
            Input("methods-pagination-6", "n_clicks"),
            Input("methods-pagination-7", "n_clicks"),
            Input("methods-pagination-8", "n_clicks"),
        ],
        [State("methods-current-module", "data")],
        prevent_initial_call=True,
    )
    def handle_pagination_click(
        prev_click, next_click, m1, m2, m3, m4, m5, m6, m7, m8, current_module
    ):
        """
        Handle pagination button clicks and update current module.

        Args:
            prev_click: Previous button clicks
            next_click: Next button clicks
            m1-m8: Module button clicks
            current_module: Currently displayed module

        Returns:
            New module number
        """
        # Determine which button was clicked
        triggered_id = ctx.triggered_id

        # Default to module 1 if no current module
        if current_module is None:
            current_module = 1

        # Calculate new module based on trigger
        new_module = current_module

        if triggered_id == "methods-pagination-prev":
            new_module = max(1, current_module - 1)
        elif triggered_id == "methods-pagination-next":
            new_module = min(8, current_module + 1)
        elif triggered_id and triggered_id.startswith("methods-pagination-"):
            # Extract module number from ID
            try:
                module_num = int(triggered_id.split("-")[-1])
                if 1 <= module_num <= 8:
                    new_module = module_num
            except (ValueError, IndexError):
                pass

        return new_module

    # Callback to handle modal open/close
    @app.callback(
        Output({"type": "modal", "index": MATCH}, "is_open"),
        [
            Input({"type": "link", "index": MATCH}, "n_clicks"),
            Input({"type": "modal-close", "index": MATCH}, "n_clicks"),
        ],
        [State({"type": "modal", "index": MATCH}, "is_open")],
        prevent_initial_call=True,
    )
    def toggle_modal(link_clicks, close_clicks, is_open):
        """
        Toggle modal open/close state.

        Args:
            link_clicks: Number of clicks on the workflow link
            close_clicks: Number of clicks on the close button
            is_open: Current modal state

        Returns:
            New modal state (True/False)
        """
        # Toggle modal state
        if ctx.triggered_id:
            return not is_open
        return is_open
