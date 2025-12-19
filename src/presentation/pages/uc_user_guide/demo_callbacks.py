"""
User Guide Demo Callbacks - Interactive Demonstration.

Callbacks for the interactive demo section in User Guide page.
These callbacks demonstrate how real use cases work without requiring
actual data processing.

Author: BioRemPP Development Team
Date: 2025-12-05
"""

from pathlib import Path

import dash_bootstrap_components as dbc
import yaml
from dash import Input, Output, State, callback

from .demo_layout import create_mock_bar_chart

# Load demo configuration
DEMO_CONFIG_PATH = Path(__file__).parent / "demo_config.yaml"


def load_demo_config():
    """Load demo configuration from YAML."""
    with open(DEMO_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def register_demo_callbacks(app):
    """
    Register all demo callbacks for user guide interactive section.

    Parameters
    ----------
    app : dash.Dash
        Dash application instance
    """

    # ========================================================================
    # Callback 1: Toggle Use Case Description Panel
    # ========================================================================
    @app.callback(
        Output("demo-guide-collapse", "is_open"),
        Input("demo-guide-collapse-button", "n_clicks"),
        State("demo-guide-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_demo_collapse(n_clicks, is_open):
        """Toggle collapsible use case description panel."""
        if n_clicks:
            return not is_open
        return is_open

    # ========================================================================
    # Callback 2: Database Selection (Button Toggle)
    # ========================================================================
    @app.callback(
        [
            Output("demo-guide-db-biorempp", "outline"),
            Output("demo-guide-db-hadeg", "outline"),
            Output("demo-guide-db-kegg", "outline"),
            Output("demo-guide-db-description", "children"),
            Output("demo-guide-chart", "figure"),
        ],
        [
            Input("demo-guide-db-biorempp", "n_clicks"),
            Input("demo-guide-db-hadeg", "n_clicks"),
            Input("demo-guide-db-kegg", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def update_demo_database_selection(bio_clicks, hadeg_clicks, kegg_clicks):
        """
        Update database selection and chart based on button clicks.

        Returns
        -------
        tuple
            (biorempp_outline, hadeg_outline, kegg_outline, description, figure)
        """
        # Load config
        config = load_demo_config()
        databases = config["mock_data"]["databases"]

        # Determine which button was clicked using callback context
        from dash import callback_context

        if not callback_context.triggered:
            # Default: BioRemPP selected
            selected_db = databases[0]
            return (
                False,
                True,
                True,
                _create_db_description(selected_db),
                create_mock_bar_chart(config, selected_db["name"]),
            )

        # Get trigger ID
        trigger_id = callback_context.triggered[0]["prop_id"].split(".")[0]

        # Map trigger to database
        if trigger_id == "demo-guide-db-biorempp":
            selected_db = databases[0]
            return (
                False,
                True,
                True,
                _create_db_description(selected_db),
                create_mock_bar_chart(config, selected_db["name"]),
            )
        elif trigger_id == "demo-guide-db-hadeg":
            selected_db = databases[1]
            return (
                True,
                False,
                True,
                _create_db_description(selected_db),
                create_mock_bar_chart(config, selected_db["name"]),
            )
        elif trigger_id == "demo-guide-db-kegg":
            selected_db = databases[2]
            return (
                True,
                True,
                False,
                _create_db_description(selected_db),
                create_mock_bar_chart(config, selected_db["name"]),
            )

        # Fallback
        selected_db = databases[0]
        return (
            False,
            True,
            True,
            _create_db_description(selected_db),
            create_mock_bar_chart(config, selected_db["name"]),
        )


def _create_db_description(database: dict) -> dbc.Alert:
    """
    Create database description alert.

    Parameters
    ----------
    database : dict
        Database information with 'name' and 'description'

    Returns
    -------
    dbc.Alert
        Alert component with database description
    """
    return dbc.Alert(
        database["description"], color="light", className="mt-2 mb-0 small"
    )
