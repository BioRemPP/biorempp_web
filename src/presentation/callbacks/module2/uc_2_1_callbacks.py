"""
UC-2.1 Callbacks - Ranking of Samples by Functional Richness.

This module implements callback functions for ranking samples based on KO
(KEGG Orthology) counts with database selection and range filtering.

Functions
---------
register_uc_2_1_callbacks
    Register all UC-2.1 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Supports on-demand rendering and auto-update on filter changes
- Works with BioRemPP, HADEG, and KEGG databases

Version: 1.0.0
"""

import logging
import os
from typing import Any, Optional, Tuple

import pandas as pd
from dash import Input, Output, State, callback_context, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)
logger.propagate = False  # Prevent duplicate logs


def register_uc_2_1_callbacks(app, plot_service) -> None:
    """
    Register UC-2.1 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle, database selection, chart rendering, and slider update callbacks
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-2-1-collapse", "is_open"),
        Input("uc-2-1-collapse-button", "n_clicks"),
        State("uc-2-1-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_2_1_info_panel(n_clicks, is_open):
        """Toggle UC-2.1 informative panel collapse."""
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        [
            Output("uc-2-1-db-biorempp", "outline"),
            Output("uc-2-1-db-hadeg", "outline"),
            Output("uc-2-1-db-kegg", "outline"),
        ],
        [
            Input("uc-2-1-db-biorempp", "n_clicks"),
            Input("uc-2-1-db-hadeg", "n_clicks"),
            Input("uc-2-1-db-kegg", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def toggle_database_buttons(biorempp_clicks, hadeg_clicks, kegg_clicks):
        """
        Toggle database selection buttons for UC-2.1.

        Parameters
        ----------
        biorempp_clicks : int
            Number of clicks on BioRemPP button.
        hadeg_clicks : int
            Number of clicks on HADEG button.
        kegg_clicks : int
            Number of clicks on KEGG button.

        Returns
        -------
        tuple of (bool, bool, bool)
            Outline states for (BioRemPP, HADEG, KEGG).
            False = selected, True = not selected.
        """
        ctx = callback_context
        if not ctx.triggered:
            return False, True, True

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "uc-2-1-db-biorempp":
            return False, True, True
        elif button_id == "uc-2-1-db-hadeg":
            return True, False, True
        elif button_id == "uc-2-1-db-kegg":
            return True, True, False

        return False, True, True

    @app.callback(
        Output("uc-2-1-chart-container", "children"),
        [
            Input("uc-2-1-accordion", "active_item"),
            Input("uc-2-1-range-slider", "value"),
            Input("uc-2-1-db-biorempp", "n_clicks"),
            Input("uc-2-1-db-hadeg", "n_clicks"),
            Input("uc-2-1-db-kegg", "n_clicks"),
        ],
        [
            State("merged-result-store", "data"),
            State("uc-2-1-chart-container", "children"),
            State("uc-2-1-db-biorempp", "outline"),
            State("uc-2-1-db-hadeg", "outline"),
            State("uc-2-1-db-kegg", "outline"),
        ],
        prevent_initial_call=True,
    )
    def render_uc_2_1(
        accordion_active: Optional[str],
        range_slider_values: list,
        biorempp_clicks: Optional[int],
        hadeg_clicks: Optional[int],
        kegg_clicks: Optional[int],
        biorempp_data: Optional[list],
        current_container: Any,
        biorempp_outline: bool,
        hadeg_outline: bool,
        kegg_outline: bool,
    ) -> Any:
        """
        Render UC-2.1 bar chart with on-demand and auto-update logic.

        Parameters
        ----------
        accordion_active : str, optional
            Active accordion item ID.
        range_slider_values : list
            Range slider values [min, max].
        biorempp_clicks : int, optional
            Number of clicks on BioRemPP button.
        hadeg_clicks : int, optional
            Number of clicks on HADEG button.
        kegg_clicks : int, optional
            Number of clicks on KEGG button.
        biorempp_data : list, optional
            Merged data from store.
        current_container : Any
            Current container content.
        biorempp_outline : bool
            Whether BioRemPP button is outlined (not selected).
        hadeg_outline : bool
            Whether HADEG button is outlined (not selected).
        kegg_outline : bool
            Whether KEGG button is outlined (not selected).

        Returns
        -------
        dcc.Graph or html.Div
            Chart component or error message.

        Raises
        ------
        PreventUpdate
            If conditions for rendering not met.

        Notes
        -----
        - Accordion open triggers initial render
        - Slider/database changes trigger auto-update if chart already rendered
        - Validates Sample and KO columns before processing
        """
        # Check data availability
        if not biorempp_data:
            logger.warning("No data available for UC-2.1")
            raise PreventUpdate

        # Determine trigger
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        logger.debug(f"UC-2.1 triggered by: {trigger_id}")

        # Database selection logic
        db_map = {
            "uc-2-1-db-biorempp": "biorempp_df",
            "uc-2-1-db-hadeg": "hadeg_df",
            "uc-2-1-db-kegg": "kegg_df",
        }

        if trigger_id in db_map:
            selected_db_key = db_map[trigger_id]
        else:
            if not biorempp_outline:
                selected_db_key = "biorempp_df"
            elif not hadeg_outline:
                selected_db_key = "hadeg_df"
            elif not kegg_outline:
                selected_db_key = "kegg_df"
            else:
                selected_db_key = "biorempp_df"

        logger.debug(f"UC-2.1 selected database: {selected_db_key}")

        # Check if chart already rendered
        chart_already_rendered = _is_chart_rendered(current_container)

        # Rendering decision
        accordion_opened = (
            trigger_id == "uc-2-1-accordion" and accordion_active == "uc-2-1-item"
        )
        slider_changed_with_chart = (
            trigger_id == "uc-2-1-range-slider" and chart_already_rendered
        )
        database_changed_with_chart = trigger_id in db_map and chart_already_rendered
        should_render = (
            accordion_opened or slider_changed_with_chart or database_changed_with_chart
        )

        if not should_render:
            logger.debug("UC-2.1: Render conditions not met")
            raise PreventUpdate

        # Generate plot
        try:
            # Extract DataFrame from store
            if isinstance(biorempp_data, dict) and selected_db_key in biorempp_data:
                df = pd.DataFrame(biorempp_data[selected_db_key])
                logger.info(
                    f"UC-2.1: Using {selected_db_key}, "
                    f"shape: {df.shape}, columns: {df.columns.tolist()}"
                )

                # Validate required columns
                if "Sample" not in df.columns or "KO" not in df.columns:
                    error_msg = (
                        f"Data from {selected_db_key} must contain "
                        f"'Sample' and 'KO' columns. Found: {set(df.columns)}"
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg)

            elif isinstance(biorempp_data, list):
                df = pd.DataFrame(biorempp_data)
                logger.info("UC-2.1: Using direct data format")
            else:
                raise ValueError(
                    f"Invalid data format. Expected dict with "
                    f"'{selected_db_key}' or list of records"
                )

            # Build filters
            filters = {"uc-2-1-range-slider": range_slider_values}

            # Generate plot via PlotService
            fig = plot_service.generate_plot(
                use_case_id="UC-2.1", data=df, filters=filters, force_refresh=False
            )
            logger.info("UC-2.1: Figure generated successfully")

            # Create chart component
            try:
                suggested = sanitize_filename("UC-2.1", "sample_ko_ranking", "png")
                base_filename = os.path.splitext(suggested)[0]
            except Exception:
                base_filename = "uc_2_1_sample_ko_ranking"

            chart_component = dcc.Graph(
                figure=fig,
                id="uc-2-1-bar-chart",
                config={
                    "displayModeBar": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 800,
                        "width": 1200,
                        "scale": 2,
                    },
                },
            )

            logger.info("UC-2.1 chart rendered successfully")
            return chart_component

        except ValueError as e:
            logger.error(f"UC-2.1 validation error: {e}", exc_info=True)
            return _create_error_message(
                f"Data validation failed: {str(e)}", icon="fas fa-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"UC-2.1 error: {e}", exc_info=True)
            return _create_error_message(
                "Error generating chart. Please try again.",
                icon="fas fa-exclamation-circle",
            )

    @app.callback(
        [
            Output("uc-2-1-range-slider", "max"),
            Output("uc-2-1-range-slider", "value"),
            Output("uc-2-1-range-slider", "marks"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-2-1-db-biorempp", "n_clicks"),
            Input("uc-2-1-db-hadeg", "n_clicks"),
            Input("uc-2-1-db-kegg", "n_clicks"),
        ],
        [
            State("uc-2-1-db-biorempp", "outline"),
            State("uc-2-1-db-hadeg", "outline"),
            State("uc-2-1-db-kegg", "outline"),
        ],
    )
    def update_uc_2_1_range_slider(
        biorempp_data: Optional[list],
        biorempp_clicks: Optional[int],
        hadeg_clicks: Optional[int],
        kegg_clicks: Optional[int],
        biorempp_outline: bool,
        hadeg_outline: bool,
        kegg_outline: bool,
    ) -> Tuple[int, list, dict]:
        """
        Update range slider properties dynamically based on selected database.

        Parameters
        ----------
        biorempp_data : list, optional
            Merged data from store.
        biorempp_clicks : int, optional
            Number of clicks on BioRemPP button.
        hadeg_clicks : int, optional
            Number of clicks on HADEG button.
        kegg_clicks : int, optional
            Number of clicks on KEGG button.
        biorempp_outline : bool
            Whether BioRemPP button is outlined (not selected).
        hadeg_outline : bool
            Whether HADEG button is outlined (not selected).
        kegg_outline : bool
            Whether KEGG button is outlined (not selected).

        Returns
        -------
        tuple
            (max_value, default_range, marks_dict)

        Notes
        -----
        - Calculates maximum KO count across all samples
        - Generates slider marks at appropriate intervals
        """
        if not biorempp_data:
            logger.debug("[UC-2.1] No data in store, preventing update")
            raise PreventUpdate

        # Check if this is initial call with empty/invalid data
        if isinstance(biorempp_data, dict) and not biorempp_data:
            logger.debug("[UC-2.1] Empty dict in store, preventing update")
            raise PreventUpdate

        try:
            # Determine selected database
            ctx = callback_context
            trigger_id = (
                ctx.triggered[0]["prop_id"].split(".")[0]
                if ctx.triggered
                else "merged-result-store"
            )

            logger.debug(f"[UC-2.1 SLIDER] Triggered by: {trigger_id}")

            db_map = {
                "uc-2-1-db-biorempp": "biorempp_df",
                "uc-2-1-db-hadeg": "hadeg_df",
                "uc-2-1-db-kegg": "kegg_df",
            }

            if trigger_id in db_map:
                selected_db_key = db_map[trigger_id]
            else:
                if not biorempp_outline:
                    selected_db_key = "biorempp_df"
                elif not hadeg_outline:
                    selected_db_key = "hadeg_df"
                elif not kegg_outline:
                    selected_db_key = "kegg_df"
                else:
                    selected_db_key = "biorempp_df"

            # Extract DataFrame
            if isinstance(biorempp_data, dict) and selected_db_key in biorempp_data:
                df = pd.DataFrame(biorempp_data[selected_db_key])
            elif isinstance(biorempp_data, list):
                df = pd.DataFrame(biorempp_data)
            else:
                raise PreventUpdate

            # Validate columns
            if "Sample" not in df.columns or "KO" not in df.columns:
                if "sample" in df.columns:
                    df = df.rename(columns={"sample": "Sample"})
                else:
                    raise PreventUpdate

            # DATA PROCESSING: Calculate KO counts per sample (inline logic)
            ko_counts = df.groupby("Sample")["KO"].nunique()

            max_count = int(ko_counts.max())
            min_count = 0

            # Generate marks at intervals
            interval = max(1, max_count // 10)
            marks = {i: str(i) for i in range(min_count, max_count + 1, interval)}

            default_value = [min_count, max_count]

            logger.info(
                f"UC-2.1 range slider updated: max={max_count}, " f"interval={interval}"
            )

            return max_count, default_value, marks

        except Exception as e:
            logger.error(f"Error updating range slider: {e}")
            raise PreventUpdate


def _is_chart_rendered(container: Any) -> bool:
    """
    Check if chart is already rendered in container.

    Parameters
    ----------
    container : Any
        Container content.

    Returns
    -------
    bool
        True if chart is rendered, False otherwise.
    """
    if not container:
        return False

    if isinstance(container, dict):
        return container.get("type") == "Graph"

    if isinstance(container, (list, tuple)) and len(container) > 0:
        first = container[0]
        if isinstance(first, dict):
            return first.get("type") == "Graph"

    return False


def _create_error_message(
    message: str, icon: str = "fas fa-exclamation-circle"
) -> html.Div:
    """
    Create error message component.

    Parameters
    ----------
    message : str
        Error message text.
    icon : str, default="fas fa-exclamation-circle"
        Font Awesome icon class.

    Returns
    -------
    html.Div
        Error message component.
    """
    return html.Div(
        [
            html.I(className=f"{icon} me-2 text-danger"),
            html.Span(message, className="text-danger"),
        ],
        className="alert alert-danger mt-3",
    )
