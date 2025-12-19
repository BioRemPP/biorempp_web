"""
UC-2.2 Callbacks - Ranking of Samples by Compound Richness.

This module implements callback functions for ranking samples based on compound
counts with database selection and range filtering capabilities.

Functions
---------
register_uc_2_2_callbacks
    Register all UC-2.2 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Supports on-demand rendering and auto-update on filter changes
- BioRemPP database recommended for compound richness analysis

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


def register_uc_2_2_callbacks(app, plot_service) -> None:
    """
    Register UC-2.2 callbacks with Dash app.

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
        Output("uc-2-2-collapse", "is_open"),
        Input("uc-2-2-collapse-button", "n_clicks"),
        State("uc-2-2-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_2_2_info_panel(n_clicks, is_open):
        """Toggle UC-2.2 informative panel collapse."""
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        [Output("uc-2-2-db-biorempp", "outline"), Output("uc-2-2-db-kegg", "outline")],
        [Input("uc-2-2-db-biorempp", "n_clicks"), Input("uc-2-2-db-kegg", "n_clicks")],
        prevent_initial_call=True,
    )
    def toggle_uc_2_2_database_buttons(biorempp_clicks, kegg_clicks):
        """
        Toggle UC-2.2 database selection buttons.

        Parameters
        ----------
        biorempp_clicks : Optional[int]
            Number of clicks on BioRemPP button.
        kegg_clicks : Optional[int]
            Number of clicks on KEGG button.

        Returns
        -------
        Tuple[bool, bool]
            Outline states for (BioRemPP, KEGG).
            False = selected, True = not selected.
        """
        ctx = callback_context
        if not ctx.triggered:
            return False, True

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "uc-2-2-db-biorempp":
            return False, True
        elif button_id == "uc-2-2-db-kegg":
            return True, False

        return False, True

    @app.callback(
        Output("uc-2-2-chart-container", "children"),
        [
            Input("uc-2-2-accordion", "active_item"),
            Input("uc-2-2-range-slider", "value"),
            Input("uc-2-2-db-biorempp", "n_clicks"),
            Input("uc-2-2-db-kegg", "n_clicks"),
        ],
        [
            State("merged-result-store", "data"),
            State("uc-2-2-chart-container", "children"),
            State("uc-2-2-db-biorempp", "outline"),
            State("uc-2-2-db-kegg", "outline"),
        ],
        prevent_initial_call=True,
    )
    def render_uc_2_2(
        accordion_active: Optional[str],
        range_slider_values: list,
        biorempp_clicks: Optional[int],
        kegg_clicks: Optional[int],
        merged_data: Optional[list],
        current_container: Any,
        biorempp_outline: bool,
        kegg_outline: bool,
    ) -> Any:
        """
        Render UC-2.2 bar chart with on-demand and auto-update logic.

        Parameters
        ----------
        accordion_active : str, optional
            Active accordion item ID.
        range_slider_values : list
            Range slider values [min, max].
        biorempp_clicks : int, optional
            Number of clicks on BioRemPP button.
        kegg_clicks : int, optional
            Number of clicks on KEGG button.
        merged_data : list, optional
            Merged data from store.
        current_container : Any
            Current container content.
        biorempp_outline : bool
            Whether BioRemPP button is outlined (not selected).
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
        - Processes compound counts per sample with range filtering
        """
        # Check data availability
        if not merged_data:
            logger.warning("No data available for UC-2.2")
            raise PreventUpdate

        # Determine trigger
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        logger.debug(f"UC-2.2 triggered by: {trigger_id}")

        # Database selection logic
        db_map = {"uc-2-2-db-biorempp": "biorempp_df", "uc-2-2-db-kegg": "kegg_df"}

        if trigger_id in db_map:
            selected_db_key = db_map[trigger_id]
        else:
            if not biorempp_outline:
                selected_db_key = "biorempp_df"
            elif not kegg_outline:
                selected_db_key = "kegg_df"
            else:
                selected_db_key = "biorempp_df"

        logger.debug(f"UC-2.2 selected database: {selected_db_key}")

        # VALIDATION: KEGG doesn't support compound data
        if selected_db_key == "kegg_df":
            error_msg = (
                "KEGG database does not contain compound information. "
                "Please select BioRemPP database for compound richness analysis."
            )
            logger.warning(f"UC-2.2: {error_msg}")
            return _create_error_message(error_msg, icon="fas fa-info-circle")

        # Check if chart already rendered
        chart_already_rendered = _is_chart_rendered(current_container)

        # Rendering decision
        accordion_opened = (
            trigger_id == "uc-2-2-accordion" and accordion_active == "uc-2-2-item"
        )
        slider_changed_with_chart = (
            trigger_id == "uc-2-2-range-slider" and chart_already_rendered
        )
        database_changed_with_chart = trigger_id in db_map and chart_already_rendered
        should_render = (
            accordion_opened or slider_changed_with_chart or database_changed_with_chart
        )

        if not should_render:
            logger.debug("UC-2.2: Render conditions not met")
            raise PreventUpdate

        # Generate plot
        try:
            # Extract DataFrame from store
            if isinstance(merged_data, dict) and selected_db_key in merged_data:
                df = pd.DataFrame(merged_data[selected_db_key])
                logger.info(
                    f"UC-2.2: Using {selected_db_key}, "
                    f"shape: {df.shape}, columns: {df.columns.tolist()}"
                )

                # Find compound column (flexible naming)
                cpd_col = None
                for col_name in ["cpd", "Compound_ID", "Compound", "compound"]:
                    if col_name in df.columns:
                        cpd_col = col_name
                        break

                # Validate Sample column
                if "Sample" not in df.columns:
                    if "sample" in df.columns:
                        df = df.rename(columns={"sample": "Sample"})
                    else:
                        raise ValueError(
                            f"Data must contain 'Sample' column. "
                            f"Found: {set(df.columns)}"
                        )

                if cpd_col is None:
                    raise ValueError(
                        f"Data must contain compound column "
                        f"(cpd, Compound_ID, Compound, or compound). "
                        f"Found: {set(df.columns)}"
                    )

                logger.info(f"UC-2.2: Using '{cpd_col}' as compound column")

            elif isinstance(merged_data, list):
                df = pd.DataFrame(merged_data)
                logger.info("UC-2.2: Using direct data format")

                # Find compound column
                cpd_col = None
                for col_name in ["cpd", "Compound_ID", "Compound"]:
                    if col_name in df.columns:
                        cpd_col = col_name
                        break

                if "Sample" not in df.columns or cpd_col is None:
                    raise ValueError(
                        f"Data must contain 'Sample' and compound columns. "
                        f"Found: {set(df.columns)}"
                    )
            else:
                raise ValueError(
                    f"Invalid data format: expected dict or list, "
                    f"got {type(merged_data)}"
                )

            # DATA PROCESSING: Calculate compound counts per sample (inline logic)
            compound_counts = df.groupby("Sample")[cpd_col].nunique().reset_index()
            compound_counts.columns = ["Sample", "Compound_Count"]

            # Apply range filter
            min_val, max_val = range_slider_values
            filtered = compound_counts[
                (compound_counts["Compound_Count"] >= min_val)
                & (compound_counts["Compound_Count"] <= max_val)
            ]

            logger.info(
                f"UC-2.2: Filtered {len(filtered)} samples "
                f"(range: {min_val}-{max_val})"
            )

            if filtered.empty:
                return _create_error_message(
                    "No samples match the selected compound count range.",
                    icon="fas fa-info-circle",
                )

            # Sort by compound count (ascending for horizontal bar chart)
            filtered = filtered.sort_values("Compound_Count", ascending=True)

            # Build filters for plot service
            filters = {
                "uc-2-2-range-slider": range_slider_values,
                "selected_database": selected_db_key,
            }

            # Generate plot using PlotService
            fig = plot_service.generate_plot(
                use_case_id="UC-2.2",
                data=filtered,
                filters=filters,
                force_refresh=False,  # Temporarily True to clear cache
            )

            logger.info("UC-2.2: Chart generated successfully")

            try:
                suggested = sanitize_filename(
                    "UC-2.2", "sample_compound_ranking", "png"
                )
                base_filename = os.path.splitext(suggested)[0]
            except Exception:
                base_filename = "uc_2_2_sample_compound_ranking"

            return dcc.Graph(
                figure=fig,
                id="uc-2-2-bar-chart",
                config={
                    "displayModeBar": True,
                    "responsive": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 800,
                        "width": 1200,
                        "scale": 2,
                    },
                },
                style={"height": "600px"},
            )

        except ValueError as e:
            logger.error(f"UC-2.2 validation error: {e}", exc_info=True)
            return _create_error_message(f"Data validation failed: {str(e)}")

        except Exception as e:
            logger.error(f"UC-2.2 error: {e}", exc_info=True)
            return _create_error_message(f"Error generating visualization: {str(e)}")

    @app.callback(
        [
            Output("uc-2-2-range-slider", "max"),
            Output("uc-2-2-range-slider", "value"),
            Output("uc-2-2-range-slider", "marks"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-2-2-db-biorempp", "n_clicks"),
            Input("uc-2-2-db-kegg", "n_clicks"),
        ],
        [State("uc-2-2-db-biorempp", "outline"), State("uc-2-2-db-kegg", "outline")],
    )
    def update_uc_2_2_range_slider(
        merged_data: Optional[list],
        biorempp_clicks: Optional[int],
        kegg_clicks: Optional[int],
        biorempp_outline: bool,
        kegg_outline: bool,
    ) -> Tuple[int, list, dict]:
        """
        Update range slider properties dynamically based on selected database.

        Parameters
        ----------
        merged_data : list, optional
            Merged data from store.
        biorempp_clicks : int, optional
            Number of clicks on BioRemPP button.
        kegg_clicks : int, optional
            Number of clicks on KEGG button.
        biorempp_outline : bool
            Whether BioRemPP button is outlined (not selected).
        kegg_outline : bool
            Whether KEGG button is outlined (not selected).

        Returns
        -------
        tuple
            (max_value, default_range, marks_dict)

        Notes
        -----
        - Calculates maximum compound count across all samples
        - Generates slider marks at appropriate intervals
        """
        if not merged_data:
            logger.debug("[UC-2.2] No data in store, preventing update")
            raise PreventUpdate

        # Check if this is initial call with empty/invalid data
        if isinstance(merged_data, dict) and not merged_data:
            logger.debug("[UC-2.2] Empty dict in store, preventing update")
            raise PreventUpdate

        try:
            # Determine selected database
            ctx = callback_context
            trigger_id = (
                ctx.triggered[0]["prop_id"].split(".")[0]
                if ctx.triggered
                else "merged-result-store"
            )

            logger.debug(f"[UC-2.2 SLIDER] Triggered by: {trigger_id}")

            db_map = {"uc-2-2-db-biorempp": "biorempp_df", "uc-2-2-db-kegg": "kegg_df"}

            if trigger_id in db_map:
                selected_db_key = db_map[trigger_id]
            else:
                if not biorempp_outline:
                    selected_db_key = "biorempp_df"
                elif not kegg_outline:
                    selected_db_key = "kegg_df"
                else:
                    selected_db_key = "biorempp_df"

            # Extract DataFrame
            if isinstance(merged_data, dict) and selected_db_key in merged_data:
                df = pd.DataFrame(merged_data[selected_db_key])
            elif isinstance(merged_data, list):
                df = pd.DataFrame(merged_data)
            else:
                raise PreventUpdate

            # Find compound column
            cpd_col = None
            for col_name in ["cpd", "Compound_ID", "Compound", "compound"]:
                if col_name in df.columns:
                    cpd_col = col_name
                    break

            # Validate Sample column
            if "Sample" not in df.columns:
                if "sample" in df.columns:
                    df = df.rename(columns={"sample": "Sample"})
                else:
                    raise PreventUpdate

            if cpd_col is None:
                raise PreventUpdate

            # DATA PROCESSING: Calculate compound counts per sample (inline logic)
            compound_counts = df.groupby("Sample")[cpd_col].nunique()

            max_count = int(compound_counts.max())
            min_count = 0

            # Generate marks at intervals
            interval = max(1, max_count // 10)
            marks = {i: str(i) for i in range(min_count, max_count + 1, interval)}

            default_value = [min_count, max_count]

            logger.info(
                f"UC-2.2 range slider updated: max={max_count}, " f"interval={interval}"
            )

            return max_count, default_value, marks

        except Exception as e:
            logger.error(f"Error updating UC-2.2 range slider: {e}")
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
