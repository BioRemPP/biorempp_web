"""
UC-1.3 Callbacks - Percentage Distribution of KO Assignments.

This module implements callback functions for visualizing KO assignment
percentage distribution across reference agencies using stacked bar charts.

Functions
---------
register_uc_1_3_callbacks
    Register all UC-1.3 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses StackedBarChartStrategy for percentage visualization
- Implements on-demand rendering for performance optimization

Version: 1.0.0
"""

import logging
import os
from typing import Any, Dict, Optional

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)


def register_uc_1_3_callbacks(app, plot_service) -> None:
    """
    Register all UC-1.3 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and stacked bar chart rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("Registering UC-1.3 callbacks")

    @app.callback(
        Output("uc-1-3-collapse", "is_open"),
        Input("uc-1-3-collapse-button", "n_clicks"),
        State("uc-1-3-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_1_3_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """
        Toggle UC-1.3 information panel visibility.

        Parameters
        ----------
        n_clicks : int, optional
            Number of times collapse button was clicked.
        is_open : bool
            Current collapse state.

        Returns
        -------
        bool
            New collapse state (toggled).
        """
        if n_clicks:
            logger.debug(f"UC-1.3 info panel toggled. New state: {not is_open}")
            return not is_open
        return is_open

    @app.callback(
        Output("uc-1-3-chart", "children"),
        Input("uc-1-3-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_1_3(
        active_item: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-1.3 stacked bar chart when accordion is activated.

        Parameters
        ----------
        active_item : str, optional
            Active accordion item ID.
        merged_data : dict, optional
            Dictionary containing merged result data with 'biorempp_df' key.

        Returns
        -------
        html.Div
            Container with chart or error message.

        Raises
        ------
        PreventUpdate
            If accordion is not active or data is not ready.

        Notes
        -----
        - Extracts KO and reference AG data from BioRemPP DataFrame
        - Calculates percentage distribution and generates stacked bar chart
        - Uses StackedBarChartStrategy via PlotService
        """
        logger.debug(f"UC-1.3 render callback triggered. Active item: {active_item}")

        # Check if UC-1.3 accordion is active
        if not active_item or active_item != "uc-1-3-accordion":
            logger.debug("UC-1.3 accordion not active. Preventing update.")
            raise PreventUpdate

        try:
            # Validate merged_data structure
            if not merged_data:
                logger.warning("UC-1.3: merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please load or merge data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error("UC-1.3: merged_data does not contain 'biorempp_df' key")
                return _create_error_message(
                    "Invalid data structure. Expected 'biorempp_df' in merged data.",
                    "bi bi-x-circle",
                )

            # Extract DataFrame
            logger.debug("UC-1.3: Extracting DataFrame from merged_data")
            df = pd.DataFrame(merged_data["biorempp_df"])

            if df.empty:
                logger.warning("UC-1.3: DataFrame is empty")
                return _create_error_message(
                    "The dataset is empty. Please load data with KO and Reference AG information.",
                    "bi bi-inbox",
                )

            logger.info(
                f"UC-1.3: Processing DataFrame with {len(df)} rows and {len(df.columns)} columns"
            )

            # Map column names flexibly to handle different naming conventions
            col_map = {}

            # Try to find referenceAG/Agency column
            ref_ag_candidates = [
                "Agency",
                "agency",
                "Reference_AG",
                "referenceAG",
                "referenceag",
                "reference_ag",
                "ref_ag",
            ]
            for col_name in ref_ag_candidates:
                if col_name in df.columns:
                    col_map["referenceAG"] = col_name
                    logger.debug(f"UC-1.3: Mapped referenceAG to column '{col_name}'")
                    break

            # Try to find ko column
            ko_candidates = ["KO", "ko", "ko_id", "KO_ID", "ko_number"]
            for col_name in ko_candidates:
                if col_name in df.columns:
                    col_map["ko"] = col_name
                    logger.debug(f"UC-1.3: Mapped ko to column '{col_name}'")
                    break

            # Validate required columns were found
            if "referenceAG" not in col_map:
                logger.error(
                    f"UC-1.3: referenceAG column not found. "
                    f"Available: {df.columns.tolist()}"
                )
                return _create_error_message(
                    f"Required column 'referenceAG' (or variants) "
                    f"not found. Available: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            if "ko" not in col_map:
                logger.error(
                    f"UC-1.3: ko column not found. " f"Available: {df.columns.tolist()}"
                )
                return _create_error_message(
                    f"Required column 'ko' (or variants) not found. "
                    f"Available: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            # Extract mapped column names
            ref_ag_col = col_map["referenceAG"]
            ko_col = col_map["ko"]

            logger.debug(
                f"UC-1.3: Using columns - "
                f"referenceAG: '{ref_ag_col}', ko: '{ko_col}'"
            )

            # === DATA PREPARATION ===
            # Strategy expects raw data with columns: referenceAG, ko
            # Strategy will handle: cleaning, deduplication, aggregation, percentages

            # Rename columns to standard names expected by strategy
            df_for_plot = df[[ref_ag_col, ko_col]].rename(
                columns={ref_ag_col: "referenceAG", ko_col: "ko"}
            )

            # Basic validation before passing to strategy
            non_null_count = df_for_plot.dropna().shape[0]
            if non_null_count == 0:
                logger.warning("UC-1.3: All rows contain null values")
                return _create_error_message(
                    "No valid KO and Agency pairs found. "
                    "All rows contain null values.",
                    "bi bi-funnel",
                )

            logger.info(
                f"UC-1.3: Prepared {len(df_for_plot)} rows "
                f"({non_null_count} non-null) for StackedBarChartStrategy"
            )

            # === PLOT GENERATION ===
            logger.debug("UC-1.3: Calling PlotService to generate stacked bar chart")

            # Generate plot using PlotService with StackedBarChartStrategy
            # Strategy will handle all processing: clean, aggregate, percentages
            fig = plot_service.generate_plot(
                use_case_id="UC-1.3",
                data=df_for_plot,
                filters={},  # No filters needed for this use case
                force_refresh=False,
            )

            logger.info("UC-1.3: Chart generation successful")

            # Prepare sanitized filename and return chart
            try:
                suggested = sanitize_filename("UC-1.3", "ko_distribution", "png")
                base_filename = os.path.splitext(suggested)[0]
            except Exception:
                base_filename = "uc_1_3_ko_distribution"

            return dcc.Graph(
                id="uc-1-3-graph",
                figure=fig,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 900,
                        "width": 1400,
                        "scale": 2,
                    },
                },
                style={"height": "650px"},
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(
                f"UC-1.3: ValueError during processing - {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(
                f"UC-1.3: Unexpected error during chart rendering - {str(e)}",
                exc_info=True,
            )
            return _create_error_message(
                f"An error occurred while generating the chart: {str(e)}", "bi bi-bug"
            )


def _create_error_message(
    message: str, icon: str = "bi bi-exclamation-circle"
) -> html.Div:
    """
    Create Bootstrap-styled error message component.

    Parameters
    ----------
    message : str
        Error message to display.
    icon : str, optional
        Bootstrap icon class (default: "bi bi-exclamation-circle").

    Returns
    -------
    html.Div
        Formatted error message container.
    """
    return html.Div(
        [
            html.I(className=f"{icon} me-2", style={"fontSize": "1.2rem"}),
            html.Span(message, style={"fontSize": "0.95rem"}),
        ],
        className="alert alert-danger d-flex align-items-center",
        role="alert",
        style={"margin": "20px", "borderRadius": "8px"},
    )
