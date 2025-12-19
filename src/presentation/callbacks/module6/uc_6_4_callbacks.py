"""
UC-6.4 Callbacks - Overview of Enzymatic Activity and Substrate Scope.

This module implements callback functions for visualizing enzymatic activity
through treemap analysis of substrate diversity and chemical class distribution.

Functions
---------
register_uc_6_4_callbacks
    Register all UC-6.4 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses TreemapStrategy for hierarchical enzymatic activity visualization
- BioRemPP database required for Enzyme_Activity, Compound_Class, Gene_Symbol, Compound_Name data

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


def register_uc_6_4_callbacks(app, plot_service) -> None:
    """
    Register all UC-6.4 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and treemap rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-6.4] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-6-4-collapse", "is_open"),
        Input("uc-6-4-collapse-button", "n_clicks"),
        State("uc-6-4-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_6_4_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """Toggle UC-6.4 informative panel collapse state."""
        if n_clicks:
            logger.debug(f"[UC-6.4] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Render Treemap
    # ========================================
    @app.callback(
        Output("uc-6-4-chart", "children"),
        Input("uc-6-4-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_6_4(
        active_item: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-6.4 treemap when accordion is activated.

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

        Notes
        -----
        - Validates merged_data structure and extracts BioRemPP DataFrame
        - Maps 4 column names flexibly (Enzyme_Activity/Compound_Class/Gene_Symbol/Compound_Name)
        - Cleans data removing nulls and placeholder values
        - Passes prepared data to TreemapStrategy via PlotService
        - Generates hierarchical enzymatic activity treemap
        """
        logger.debug(f"[UC-6.4] Render callback triggered. Active item: {active_item}")

        # Check if UC-6.4 accordion is active
        if not active_item or active_item != "uc-6-4-accordion":
            logger.debug("[UC-6.4] Accordion not active. Preventing update.")
            raise PreventUpdate

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-6.4] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-6.4] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            if "biorempp_df" not in merged_data:
                logger.error("[UC-6.4] merged_data does not contain 'biorempp_df' key")
                return _create_error_message(
                    "BioRemPP data not found. This use case requires "
                    "BioRemPP database.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrame
            # ========================================
            logger.debug("[UC-6.4] Extracting DataFrame from merged_data")
            biorempp_data = merged_data["biorempp_df"]

            if not biorempp_data:
                logger.warning("[UC-6.4] biorempp_df is empty")
                return _create_error_message(
                    "BioRemPP dataset is empty. Please check your input data.",
                    "bi bi-inbox",
                )

            df = pd.DataFrame(biorempp_data)

            if df.empty:
                logger.warning("[UC-6.4] DataFrame is empty after conversion")
                return _create_error_message(
                    "No data available after processing.", "bi bi-inbox"
                )

            logger.info(
                f"[UC-6.4] Processing DataFrame: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )
            logger.debug(f"[UC-6.4] Available columns: {df.columns.tolist()}")

            # ========================================
            # Step 3: Map column names flexibly
            # ========================================
            col_map = {}

            # Enzyme_Activity column
            activity_candidates = [
                "Enzyme_Activity",
                "enzyme_activity",
                "enzymeactivity",
                "EnzymeActivity",
                "activity",
                "Activity",
            ]
            for col_name in activity_candidates:
                if col_name in df.columns:
                    col_map["Enzyme_Activity"] = col_name
                    logger.debug(f"[UC-6.4] Mapped Enzyme_Activity to '{col_name}'")
                    break

            # Compound_Class column
            class_candidates = [
                "Compound_Class",
                "compound_class",
                "compoundclass",
                "CompoundClass",
                "class",
                "Class",
                "chemical_class",
            ]
            for col_name in class_candidates:
                if col_name in df.columns:
                    col_map["Compound_Class"] = col_name
                    logger.debug(f"[UC-6.4] Mapped Compound_Class to '{col_name}'")
                    break

            # Gene_Symbol column
            gene_candidates = [
                "Gene_Symbol",
                "gene_symbol",
                "genesymbol",
                "GeneSymbol",
                "gene",
                "Gene",
                "symbol",
                "Symbol",
            ]
            for col_name in gene_candidates:
                if col_name in df.columns:
                    col_map["Gene_Symbol"] = col_name
                    logger.debug(f"[UC-6.4] Mapped Gene_Symbol to '{col_name}'")
                    break

            # Compound_Name column
            compound_candidates = [
                "Compound_Name",
                "compound_name",
                "compoundname",
                "CompoundName",
                "compound",
                "Compound",
            ]
            for col_name in compound_candidates:
                if col_name in df.columns:
                    col_map["Compound_Name"] = col_name
                    logger.debug(f"[UC-6.4] Mapped Compound_Name to '{col_name}'")
                    break

            # ========================================
            # Step 4: Validate required columns found
            # ========================================
            required = [
                "Enzyme_Activity",
                "Compound_Class",
                "Gene_Symbol",
                "Compound_Name",
            ]
            missing_cols = [col for col in required if col not in col_map]

            if missing_cols:
                logger.error(
                    f"[UC-6.4] Missing columns: {missing_cols}. "
                    f"Available: {df.columns.tolist()}"
                )
                return _create_error_message(
                    f"Required columns not found: {', '.join(missing_cols)}. "
                    f"Available columns: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            # ========================================
            # Step 5: Prepare data for strategy
            # ========================================
            df_for_plot = df[
                [
                    col_map["Enzyme_Activity"],
                    col_map["Compound_Class"],
                    col_map["Gene_Symbol"],
                    col_map["Compound_Name"],
                ]
            ].rename(
                columns={
                    col_map["Enzyme_Activity"]: "Enzyme_Activity",
                    col_map["Compound_Class"]: "Compound_Class",
                    col_map["Gene_Symbol"]: "Gene_Symbol",
                    col_map["Compound_Name"]: "Compound_Name",
                }
            )

            # Clean data
            initial_count = len(df_for_plot)
            df_for_plot = df_for_plot.dropna()

            # Strip whitespace and remove placeholders
            for col in df_for_plot.columns:
                df_for_plot[col] = df_for_plot[col].astype(str).str.strip()

            df_for_plot = df_for_plot[
                ~df_for_plot["Enzyme_Activity"].isin(["#N/D", "#N/A", "N/D", ""])
            ]

            cleaned_count = len(df_for_plot)
            logger.info(
                f"[UC-6.4] Data cleaned: {initial_count} -> {cleaned_count} "
                f"rows ({initial_count - cleaned_count} removed)"
            )

            if df_for_plot.empty:
                return _create_error_message(
                    "No valid data after cleaning.", "bi bi-funnel"
                )

            # Log statistics
            n_activities = df_for_plot["Enzyme_Activity"].nunique()
            n_classes = df_for_plot["Compound_Class"].nunique()
            n_genes = df_for_plot["Gene_Symbol"].nunique()
            n_compounds = df_for_plot["Compound_Name"].nunique()

            logger.info(
                f"[UC-6.4] Data statistics: "
                f"{n_activities} activities, {n_classes} classes, "
                f"{n_genes} genes, {n_compounds} unique compounds"
            )

            # ========================================
            # Step 6: Generate plot using PlotService
            # ========================================
            logger.debug("[UC-6.4] Calling PlotService to generate treemap")

            fig = plot_service.generate_plot(
                use_case_id="UC-6.4", data=df_for_plot, filters={}, force_refresh=False
            )

            logger.info("[UC-6.4] Treemap generation successful")

            # ========================================
            # Step 7: Prepare filename and return chart component
            # ========================================
            try:
                suggested = sanitize_filename(
                    "UC-6.4", "enzymatic_activity_treemap", "png"
                )
            except Exception:
                suggested = "enzymatic_activity_treemap.png"

            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                id="uc-6-4-graph",
                figure=fig,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "responsive": True,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 900,
                        "width": 1400,
                        "scale": 6,
                    },
                },
                style={"height": "700px", "width": "100%"},
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(
                f"[UC-6.4] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-6.4] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-6.4] All callbacks registered successfully")


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
