"""
Analysis Suggestions Callbacks - BioRemPP v1.0
==============================================

Callbacks for analytical suggestions feature.

Author: BioRemPP Development Team
Date: 2025-12-05
"""

import json
import logging

from dash import ALL, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate

from .basic_exploration import create_basic_exploration_content
from .guiding_questions import create_guiding_questions_content

logger = logging.getLogger(__name__)


def register_suggestions_callbacks(app):
    """
    Register all callbacks for analytical suggestions feature.

    Parameters
    ----------
    app : dash.Dash
        Dash application instance
    """

    # ========================================================================
    # Callback 1: Toggle Suggestions Offcanvas
    # ========================================================================
    @app.callback(
        Output("suggestions-offcanvas", "is_open"),
        Input("suggestions-offcanvas-trigger", "n_clicks"),
        State("suggestions-offcanvas", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_suggestions_offcanvas(n_clicks, is_open):
        """
        Toggle suggestions offcanvas visibility.

        Returns
        -------
        bool
            New offcanvas state
        """
        if n_clicks:
            return not is_open
        return is_open

    # ========================================================================
    # Callback 2: Switch Tab Content
    # ========================================================================
    @app.callback(
        Output("suggestions-tab-content", "children"),
        Input("suggestions-tabs", "active_tab"),
    )
    def render_tab_content(active_tab):
        """
        Render content for active tab.

        Parameters
        ----------
        active_tab : str
            ID of active tab

        Returns
        -------
        Component
            Tab content component
        """
        logger.info(f"[SUGGESTIONS] Rendering tab: {active_tab}")

        try:
            if active_tab == "tab-guiding":
                logger.info("[SUGGESTIONS] Loading guiding questions content")
                content = create_guiding_questions_content()
                logger.info(
                    "[SUGGESTIONS] Guiding questions content loaded successfully"
                )
                return content

            elif active_tab == "tab-basic":
                logger.info("[SUGGESTIONS] Loading basic exploration content")
                content = create_basic_exploration_content()
                logger.info(
                    "[SUGGESTIONS] Basic exploration content loaded successfully"
                )
                return content

            elif active_tab == "tab-datatype":
                logger.info("[SUGGESTIONS] Loading data type exploration content")
                from .data_type_exploration import create_data_type_exploration_content

                content = create_data_type_exploration_content()
                logger.info(
                    "[SUGGESTIONS] Data type exploration content loaded successfully"
                )
                return content

            elif active_tab == "tab-practical":
                logger.info("[SUGGESTIONS] Loading practical applications content")
                from .practical_applications import (
                    create_practical_applications_content,
                )

                content = create_practical_applications_content()
                logger.info(
                    "[SUGGESTIONS] Practical applications content loaded successfully"
                )
                return content

            elif active_tab == "tab-trends":
                logger.info("[SUGGESTIONS] Loading current trends content")
                from .current_trends import create_current_trends_content

                content = create_current_trends_content()
                logger.info("[SUGGESTIONS] Current trends content loaded successfully")
                return content

            else:
                logger.warning(
                    f"[SUGGESTIONS] Unknown tab: {active_tab}, using default"
                )
                return create_guiding_questions_content()

        except Exception as e:
            logger.error(
                f"[SUGGESTIONS] Error rendering tab {active_tab}: {e}", exc_info=True
            )
            import dash_bootstrap_components as dbc
            from dash import html

            return dbc.Alert(
                [
                    html.H5("Error Loading Content", className="alert-heading"),
                    html.P(f"Failed to load content for tab: {active_tab}"),
                    html.Hr(),
                    html.P(f"Error: {str(e)}", className="mb-0 small text-muted"),
                ],
                color="danger",
            )
