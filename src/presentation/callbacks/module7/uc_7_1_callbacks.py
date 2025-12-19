"""
UC-7.1 Callbacks - Faceted Heatmap of Predicted Compound Toxicity Profiles.

This module implements callback functions for visualizing compound toxicity
profiles through faceted heatmap analysis across five super-categories.

Functions
---------
register_uc_7_1_callbacks
    Register all UC-7.1 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses FacetedHeatmapStrategy for multi-category toxicity visualization
- ToxCSM database REQUIRED (BioRemPP/KEGG/HADEG not compatible)

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


def register_uc_7_1_callbacks(app, plot_service) -> None:
    """
    Register all UC-7.1 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and faceted heatmap rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-7.1] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-7-1-collapse", "is_open"),
        Input("uc-7-1-collapse-button", "n_clicks"),
        State("uc-7-1-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_7_1_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """
        Toggle UC-7.1 informative panel collapse state.

        Parameters
        ----------
        n_clicks : int, optional
            Number of times button was clicked.
        is_open : bool
            Current collapse state.

        Returns
        -------
        bool
            New collapse state (toggled).
        """
        if n_clicks:
            logger.debug(f"[UC-7.1] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Render Faceted Heatmap
    # ========================================
    @app.callback(
        Output("uc-7-1-chart", "children"),
        Input("uc-7-1-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_7_1(
        active_item: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-7.1 faceted heatmap when accordion is activated.

        Parameters
        ----------
        active_item : str, optional
            ID of the currently active accordion item.
        merged_data : dict, optional
            Dictionary containing merged result data with 'toxcsm_df' key.

        Returns
        -------
        html.Div
            Container with chart or error message.

        Raises
        ------
        PreventUpdate
            If the accordion is not active or data is not ready.

        Notes
        -----
        - Validates merged_data structure and extracts ToxCSM DataFrame
        - Validates columns: compoundname, endpoint, toxicity_score, super_category
        - Cleans data: removes nulls, ensures numeric scores
        - Passes prepared data to FacetedHeatmapStrategy via PlotService
        - Generates 5-facet heatmap (Nuclear Response, Stress Response, etc.)
        - Cell colors represent toxicity scores (0-1, Reds colorscale)
        """
        logger.debug(f"[UC-7.1] Render callback triggered. Active item: {active_item}")

        # Check if UC-7.1 accordion is active
        if not active_item or active_item != "uc-7-1-accordion":
            logger.debug("[UC-7.1] Accordion not active. Preventing update.")
            raise PreventUpdate

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-7.1] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-7.1] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            if "toxcsm_df" not in merged_data:
                logger.error("[UC-7.1] merged_data does not contain 'toxcsm_df' key")
                return _create_error_message(
                    "ToxCSM data not found. This use case requires ToxCSM database.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrame
            # ========================================
            logger.debug("[UC-7.1] Extracting DataFrame from merged_data")
            toxcsm_data = merged_data["toxcsm_df"]

            if not toxcsm_data or len(toxcsm_data) == 0:
                logger.warning("[UC-7.1] toxcsm_df is empty")
                return _create_error_message(
                    "ToxCSM dataset is empty. Please check your input data.",
                    "bi bi-inbox",
                )

            df = pd.DataFrame(toxcsm_data)

            if df.empty:
                logger.warning("[UC-7.1] DataFrame is empty after conversion")
                return _create_error_message(
                    "No data available after processing.", "bi bi-inbox"
                )

            logger.info(
                f"[UC-7.1] Processing DataFrame: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )
            logger.debug(f"[UC-7.1] Available columns: {df.columns.tolist()}")

            # ========================================
            # Step 3: Validate required columns
            # ========================================
            # ToxCSM data is already in long format with these columns
            required_cols = [
                "compoundname",
                "endpoint",
                "toxicity_score",
                "super_category",
            ]

            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                logger.error(
                    f"[UC-7.1] Missing required columns: {missing_cols}. "
                    f"Available: {df.columns.tolist()}"
                )
                return _create_error_message(
                    f"Required columns not found: {', '.join(missing_cols)}. "
                    f"Available: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            # ========================================
            # Step 4: Clean and prepare data
            # ========================================
            # Remove nulls in required columns
            initial_count = len(df)
            df_clean = df.dropna(subset=required_cols)

            # Ensure toxicity_score is numeric
            df_clean["toxicity_score"] = pd.to_numeric(
                df_clean["toxicity_score"], errors="coerce"
            )
            df_clean = df_clean.dropna(subset=["toxicity_score"])

            # Remove empty strings
            df_clean = df_clean[
                (df_clean["compoundname"].astype(str).str.strip() != "")
                & (df_clean["endpoint"].astype(str).str.strip() != "")
                & (df_clean["super_category"].astype(str).str.strip() != "")
            ]

            cleaned_count = len(df_clean)
            logger.info(
                f"[UC-7.1] Data cleaned: {initial_count} -> {cleaned_count} rows "
                f"({initial_count - cleaned_count} removed)"
            )

            if df_clean.empty:
                logger.warning("[UC-7.1] No valid data after cleaning")
                return _create_error_message(
                    "No valid toxicity data found after cleaning.", "bi bi-funnel"
                )

            # Log statistics
            n_compounds = df_clean["compoundname"].nunique()
            n_endpoints = df_clean["endpoint"].nunique()
            n_categories = df_clean["super_category"].nunique()

            logger.info(
                f"[UC-7.1] Data statistics: "
                f"{n_compounds} compounds, {n_endpoints} endpoints, "
                f"{n_categories} super-categories"
            )

            # ========================================
            # Step 5: Generate plot using PlotService
            # ========================================
            logger.debug("[UC-7.1] Calling PlotService to generate faceted heatmap")

            fig = plot_service.generate_plot(
                use_case_id="UC-7.1", data=df_clean, filters={}, force_refresh=False
            )

            logger.info("[UC-7.1] Faceted heatmap generation successful")

            # ========================================
            # Step 6: Prepare filename and return chart component
            # ========================================
            try:
                suggested = sanitize_filename(
                    "UC-7.1", "faceted_toxicity_heatmap", "png"
                )
            except Exception:
                suggested = "faceted_toxicity_heatmap.png"

            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                id="uc-7-1-graph",
                figure=fig,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 800,
                        "width": 1200,
                        "scale": 6,
                    },
                },
                style={"height": "800px"},
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(
                f"[UC-7.1] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-7.1] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-7.1] All callbacks registered successfully")


def _create_error_message(
    message: str, icon_class: str = "bi bi-exclamation-triangle"
) -> html.Div:
    """
    Create a user-friendly error message component.

    Parameters
    ----------
    message : str
        Error message text to display.
    icon_class : str, optional
        Bootstrap icon class for the alert icon.
        Default: "bi bi-exclamation-triangle"

    Returns
    -------
    html.Div
        Styled alert component with icon and message.
    """
    return html.Div(
        [html.I(className=f"{icon_class} me-2"), html.Span(message)],
        className="alert alert-warning d-flex align-items-center mt-3",
        role="alert",
    )
