"""
UC-3.1 Callbacks - PCA: Sample Relationships by KO Profile.

This module implements callback functions for visualizing sample relationships
through PCA analysis based on KEGG Orthology (KO) functional profiles.

Functions
---------
register_uc_3_1_callbacks
    Register all UC-3.1 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses PCAStrategy for dimensionality reduction
- BioRemPP database required for Sample and KO data

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


def register_uc_3_1_callbacks(app, plot_service) -> None:
    """
    Register all UC-3.1 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and PCA rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-3.1] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-3-1-collapse", "is_open"),
        Input("uc-3-1-collapse-button", "n_clicks"),
        State("uc-3-1-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_3_1_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """
        Toggle UC-3.1 informative panel collapse state.

        Parameters
        ----------
        n_clicks : int
            Number of times button was clicked.
        is_open : bool
            Current collapse state.

        Returns
        -------
        bool
            New collapse state (toggled).

        Notes
        -----
        Simple toggle: open -> close, close -> open.
        """
        if n_clicks:
            logger.debug(f"[UC-3.1] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Render PCA Scatter Plot
    # ========================================
    @app.callback(
        Output("uc-3-1-chart", "children"),
        Input("uc-3-1-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_3_1(
        active_item: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-3.1 PCA scatter plot when accordion is activated.

        Parameters
        ----------
        active_item : str, optional
            ID of the currently active accordion item.
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
        - Validates merged_data structure and extracts BioRemPP DataFrame
        - Maps column names flexibly (Sample/KO with multiple aliases)
        - Cleans data by stripping whitespace and removing nulls
        - Passes prepared data to PCAStrategy via PlotService
        - Generates scatter plot with PC1/PC2 components
        """
        logger.debug(f"[UC-3.1] Render callback triggered. Active item: {active_item}")

        # Check if UC-3.1 accordion is active
        if not active_item or active_item != "uc-3-1-accordion":
            logger.debug("[UC-3.1] Accordion not active. Preventing update.")
            raise PreventUpdate

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-3.1] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-3.1] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            if "biorempp_df" not in merged_data:
                logger.error("[UC-3.1] merged_data does not contain 'biorempp_df' key")
                return _create_error_message(
                    "BioRemPP data not found. This use case requires BioRemPP database.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrame
            # ========================================
            logger.debug("[UC-3.1] Extracting DataFrame from merged_data")
            biorempp_data = merged_data["biorempp_df"]

            if not biorempp_data:
                logger.warning("[UC-3.1] biorempp_df is empty")
                return _create_error_message(
                    "BioRemPP dataset is empty. Please check your input data.",
                    "bi bi-inbox",
                )

            df = pd.DataFrame(biorempp_data)

            if df.empty:
                logger.warning("[UC-3.1] DataFrame is empty after conversion")
                return _create_error_message(
                    "No data available after processing.", "bi bi-inbox"
                )

            logger.info(
                f"[UC-3.1] Processing DataFrame: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )
            logger.debug(f"[UC-3.1] Available columns: {df.columns.tolist()}")

            # ========================================
            # Step 3: Map column names flexibly
            # ========================================
            col_map = {}

            # Try to find Sample column
            sample_candidates = [
                "Sample",
                "sample",
                "sample_id",
                "Sample_ID",
                "sampleID",
                "genome",
                "Genome",
                "organism",
            ]
            for col_name in sample_candidates:
                if col_name in df.columns:
                    col_map["Sample"] = col_name
                    logger.debug(f"[UC-3.1] Mapped Sample to '{col_name}'")
                    break

            # Try to find KO column
            ko_candidates = [
                "KO",
                "ko",
                "ko_id",
                "KO_ID",
                "kegg_orthology",
                "KEGG_Orthology",
                "orthology",
            ]
            for col_name in ko_candidates:
                if col_name in df.columns:
                    col_map["KO"] = col_name
                    logger.debug(f"[UC-3.1] Mapped KO to '{col_name}'")
                    break

            # ========================================
            # Step 4: Validate required columns found
            # ========================================
            missing_cols = []

            if "Sample" not in col_map:
                missing_cols.append("Sample")
                logger.error(
                    f"[UC-3.1] Sample column not found. "
                    f"Available: {df.columns.tolist()}"
                )

            if "KO" not in col_map:
                missing_cols.append("KO")
                logger.error(
                    f"[UC-3.1] KO column not found. "
                    f"Available: {df.columns.tolist()}"
                )

            if missing_cols:
                return _create_error_message(
                    f"Required columns not found: {', '.join(missing_cols)}. "
                    f"Available columns: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            # Extract mapped column names
            sample_col = col_map["Sample"]
            ko_col = col_map["KO"]

            logger.debug(
                f"[UC-3.1] Using columns - " f"Sample: '{sample_col}', KO: '{ko_col}'"
            )

            # ========================================
            # Step 5: Prepare data for strategy
            # ========================================
            # Select and rename columns to standard names
            df_for_plot = df[[sample_col, ko_col]].rename(
                columns={sample_col: "Sample", ko_col: "KO"}
            )

            # Clean data: remove nulls
            initial_count = len(df_for_plot)
            df_for_plot = df_for_plot.dropna()

            # Strip whitespace from string columns
            df_for_plot["Sample"] = df_for_plot["Sample"].astype(str).str.strip()
            df_for_plot["KO"] = df_for_plot["KO"].astype(str).str.strip().str.upper()

            # Remove empty strings
            df_for_plot = df_for_plot[
                (df_for_plot["Sample"] != "") & (df_for_plot["KO"] != "")
            ]

            cleaned_count = len(df_for_plot)
            logger.info(
                f"[UC-3.1] Data cleaned: {initial_count} -> {cleaned_count} rows "
                f"({initial_count - cleaned_count} removed)"
            )

            if df_for_plot.empty:
                logger.warning("[UC-3.1] No valid data after cleaning")
                return _create_error_message(
                    "No valid Sample-KO combinations found after cleaning.",
                    "bi bi-funnel",
                )

            # Log statistics
            n_samples = df_for_plot["Sample"].nunique()
            n_kos = df_for_plot["KO"].nunique()

            logger.info(
                f"[UC-3.1] Data statistics: " f"{n_samples} samples, {n_kos} unique KOs"
            )

            # Check minimum requirements for PCA
            if n_samples < 2:
                return _create_error_message(
                    f"PCA requires at least 2 samples. Found: {n_samples}",
                    "bi bi-exclamation-triangle",
                )

            if n_kos < 2:
                return _create_error_message(
                    f"PCA requires at least 2 KO features. Found: {n_kos}",
                    "bi bi-exclamation-triangle",
                )

            # ========================================
            # Step 6: Generate plot using PlotService
            # ========================================
            logger.debug("[UC-3.1] Calling PlotService to generate PCA plot")

            fig = plot_service.generate_plot(
                use_case_id="UC-3.1", data=df_for_plot, filters={}, force_refresh=False
            )

            logger.info("[UC-3.1] PCA scatter plot generation successful")

            # ========================================
            # Step 7: Prepare download filename and return chart component
            # ========================================
            try:
                suggested = sanitize_filename("UC-3.1", "pca_ko_profile", "png")
            except Exception:
                suggested = "uc_3_1_pca_ko_profile.png"
            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                id="uc-3-1-graph",
                figure=fig,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 800,
                        "width": 800,
                        "scale": 6,
                    },
                },
                style={"height": "800px"},
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(
                f"[UC-3.1] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-3.1] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-3.1] All callbacks registered successfully")


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
