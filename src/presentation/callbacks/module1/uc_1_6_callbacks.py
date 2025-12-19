"""
UC-1.6 Callbacks - Sample-Agency Functional Potential Heatmap.

This module implements callback functions for visualizing functional potential
across samples and regulatory agencies using count-based heatmaps.

Functions
---------
register_uc_1_6_callbacks
    Register all UC-1.6 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses HeatmapStrategy for count-based visualization
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


def register_uc_1_6_callbacks(app, plot_service) -> None:
    """
    Register all UC-1.6 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and heatmap rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-1.6] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-1-6-collapse", "is_open"),
        Input("uc-1-6-collapse-button", "n_clicks"),
        State("uc-1-6-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_1_6_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """
        Toggle UC-1.6 informative panel collapse state.

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
        Simple toggle: open -> close, close -> open
        """
        if n_clicks:
            logger.debug(f"[UC-1.6] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Render Heatmap
    # ========================================
    @app.callback(
        Output("uc-1-6-chart", "children"),
        Input("uc-1-6-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_1_6(
        active_item: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-1.6 heatmap when accordion is activated.

        Parameters
        ----------
        active_item : str, optional
            Active accordion item ID.
        merged_data : dict, optional
            Dictionary containing merged result data with 'biorempp_df' key.

        Returns
        -------
        html.Div
            Container with heatmap chart or error message.

        Raises
        ------
        PreventUpdate
            If accordion is not active or data is not ready.

        Notes
        -----
        - Extracts Sample, KO, and Agency data from BioRemPP DataFrame
        - Calculates unique KO counts per (Agency, Sample) combination
        - Uses HeatmapStrategy via PlotService
        """
        logger.debug(f"[UC-1.6] Render callback triggered. Active item: {active_item}")

        # Check if UC-1.6 accordion is active
        if not active_item or active_item != "uc-1-6-accordion":
            logger.debug("[UC-1.6] Accordion not active. Preventing update.")
            raise PreventUpdate

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-1.6] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-1.6] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            if "biorempp_df" not in merged_data:
                logger.error("[UC-1.6] merged_data does not contain 'biorempp_df' key")
                return _create_error_message(
                    "BioRemPP data not found. This use case requires BioRemPP database.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrame
            # ========================================
            logger.debug("[UC-1.6] Extracting DataFrame from merged_data")
            biorempp_data = merged_data["biorempp_df"]

            if not biorempp_data:
                logger.warning("[UC-1.6] biorempp_df is empty")
                return _create_error_message(
                    "BioRemPP dataset is empty. Please check your input data.",
                    "bi bi-inbox",
                )

            df = pd.DataFrame(biorempp_data)

            if df.empty:
                logger.warning("[UC-1.6] DataFrame is empty after conversion")
                return _create_error_message(
                    "No data available after processing.", "bi bi-inbox"
                )

            logger.info(
                f"[UC-1.6] Processing DataFrame: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )
            logger.debug(f"[UC-1.6] Available columns: {df.columns.tolist()}")

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
                    col_map["sample"] = col_name
                    logger.debug(f"[UC-1.6] Mapped sample to '{col_name}'")
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
                    col_map["ko"] = col_name
                    logger.debug(f"[UC-1.6] Mapped ko to '{col_name}'")
                    break

            # Try to find Agency column
            agency_candidates = [
                "Agency",
                "agency",
                "referenceAG",
                "Regulatory_Agency",
                "regulatory_agency",
                "reg_agency",
                "AGENCY",
                "ReferenceAG",
            ]
            for col_name in agency_candidates:
                if col_name in df.columns:
                    col_map["referenceAG"] = col_name
                    logger.debug(f"[UC-1.6] Mapped referenceAG to '{col_name}'")
                    break

            # ========================================
            # Step 4: Validate required columns found
            # ========================================
            missing_cols = []

            if "sample" not in col_map:
                missing_cols.append("Sample")
                logger.error(
                    f"[UC-1.6] Sample column not found. "
                    f"Available: {df.columns.tolist()}"
                )

            if "ko" not in col_map:
                missing_cols.append("KO")
                logger.error(
                    f"[UC-1.6] KO column not found. "
                    f"Available: {df.columns.tolist()}"
                )

            if "referenceAG" not in col_map:
                missing_cols.append("Agency/referenceAG")
                logger.error(
                    f"[UC-1.6] Agency column not found. "
                    f"Available: {df.columns.tolist()}"
                )

            if missing_cols:
                return _create_error_message(
                    f"Required columns not found: {', '.join(missing_cols)}. "
                    f"Available columns: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            # Extract mapped column names
            sample_col = col_map["sample"]
            ko_col = col_map["ko"]
            agency_col = col_map["referenceAG"]

            logger.debug(
                f"[UC-1.6] Using columns - "
                f"sample: '{sample_col}', ko: '{ko_col}', agency: '{agency_col}'"
            )

            # ========================================
            # Step 5: Prepare data for strategy
            # ========================================
            # Select and rename columns to standard names
            df_for_plot = df[[sample_col, ko_col, agency_col]].rename(
                columns={sample_col: "sample", ko_col: "ko", agency_col: "referenceAG"}
            )

            # Clean data: remove nulls
            initial_count = len(df_for_plot)
            df_for_plot = df_for_plot.dropna()

            # Strip whitespace from string columns
            df_for_plot["sample"] = df_for_plot["sample"].astype(str).str.strip()
            df_for_plot["ko"] = df_for_plot["ko"].astype(str).str.strip().str.upper()
            df_for_plot["referenceAG"] = (
                df_for_plot["referenceAG"].astype(str).str.strip().str.upper()
            )

            # Remove empty strings
            df_for_plot = df_for_plot[
                (df_for_plot["sample"] != "")
                & (df_for_plot["ko"] != "")
                & (df_for_plot["referenceAG"] != "")
            ]

            cleaned_count = len(df_for_plot)
            logger.info(
                f"[UC-1.6] Data cleaned: {initial_count} -> {cleaned_count} rows "
                f"({initial_count - cleaned_count} removed)"
            )

            if df_for_plot.empty:
                logger.warning("[UC-1.6] No valid data after cleaning")
                return _create_error_message(
                    "No valid Sample-KO-Agency combinations found after cleaning.",
                    "bi bi-funnel",
                )

            # Log statistics
            n_samples = df_for_plot["sample"].nunique()
            n_kos = df_for_plot["ko"].nunique()
            n_agencies = df_for_plot["referenceAG"].nunique()

            logger.info(
                f"[UC-1.6] Data statistics: "
                f"{n_samples} samples, {n_kos} unique KOs, {n_agencies} agencies"
            )

            # ========================================
            # Step 6: Generate plot using PlotService
            # ========================================
            logger.debug("[UC-1.6] Calling PlotService to generate heatmap")

            fig = plot_service.generate_plot(
                use_case_id="UC-1.6", data=df_for_plot, filters={}, force_refresh=False
            )

            logger.info("[UC-1.6] Heatmap generation successful")

            # ========================================
            # Step 7: Return chart component
            # ========================================
            try:
                suggested = sanitize_filename(
                    "UC-1.6", "sample_agency_functional_potential", "png"
                )
                base_filename = os.path.splitext(suggested)[0]
            except Exception:
                base_filename = "uc_1_6_sample_agency_functional_potential"

            return dcc.Graph(
                id="uc-1-6-graph",
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
                style={"height": "600px"},
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(
                f"[UC-1.6] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-1.6] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-1.6] All callbacks registered successfully")


def _create_error_message(
    message: str, icon_class: str = "bi bi-exclamation-triangle"
) -> html.Div:
    """
    Create user-friendly error message component.

    Parameters
    ----------
    message : str
        Error message text to display.
    icon_class : str, optional
        Bootstrap icon class (default: "bi bi-exclamation-triangle").

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
