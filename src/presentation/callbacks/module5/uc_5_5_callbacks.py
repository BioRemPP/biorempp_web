"""
UC-5.5 Callbacks - Gene-Gene Functional Interaction Network.

This module implements callback functions for visualizing gene-gene functional
relationships through similarity network analysis based on shared compound interactions.

Functions
---------
register_uc_5_5_callbacks
    Register all UC-5.5 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses NetworkStrategy in similarity mode for gene-gene relationships
- BioRemPP database required for genesymbol and compoundname data

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


def register_uc_5_5_callbacks(app, plot_service) -> None:
    """
    Register all UC-5.5 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and network diagram rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-5.5] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-5-5-collapse", "is_open"),
        Input("uc-5-5-collapse-button", "n_clicks"),
        State("uc-5-5-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_5_5_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """Toggle UC-5.5 informative panel collapse state."""
        if n_clicks:
            logger.debug(f"[UC-5.5] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Render Network Diagram
    # ========================================
    @app.callback(
        Output("uc-5-5-chart", "children"),
        [
            Input("merged-result-store", "data"),
            Input("uc-5-5-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def render_uc_5_5(
        merged_data: Optional[Dict[str, Any]], active_item: Optional[str]
    ) -> html.Div:
        """
        Render UC-5.5 gene-gene similarity network on accordion activation.

        Parameters
        ----------
        merged_data : dict, optional
            Dictionary containing merged result data with 'biorempp_df' key.
        active_item : str, optional
            Active accordion item ID.

        Returns
        -------
        html.Div
            Container with chart or error message.

        Notes
        -----
        - Validates merged_data structure and extracts BioRemPP DataFrame
        - Maps column names flexibly (genesymbol/compoundname with aliases)
        - Cleans data removing nulls and placeholder values
        - Passes prepared data to NetworkStrategy via PlotService
        - Computes gene-gene similarity based on shared compounds
        - Generates similarity network diagram
        """
        logger.info(f"[UC-5.5] Render triggered, active_item: {active_item}")

        # Check if accordion is active
        if active_item != "uc-5-5-accordion":
            logger.debug("[UC-5.5] Accordion not active. Skipping render.")
            raise PreventUpdate

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-5.5] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-5.5] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            if "biorempp_df" not in merged_data:
                logger.error("[UC-5.5] merged_data does not contain 'biorempp_df' key")
                return _create_error_message(
                    "BioRemPP data not found. This use case requires "
                    "BioRemPP database.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrame
            # ========================================
            logger.debug("[UC-5.5] Extracting DataFrame from merged_data")
            biorempp_data = merged_data["biorempp_df"]

            if not biorempp_data:
                logger.warning("[UC-5.5] biorempp_df is empty")
                return _create_error_message(
                    "BioRemPP dataset is empty. Please check your input data.",
                    "bi bi-inbox",
                )

            df = pd.DataFrame(biorempp_data)

            if df.empty:
                logger.warning("[UC-5.5] DataFrame is empty after conversion")
                return _create_error_message(
                    "No data available after processing.", "bi bi-inbox"
                )

            logger.info(
                f"[UC-5.5] Processing DataFrame: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )
            logger.debug(f"[UC-5.5] Available columns: {df.columns.tolist()}")

            # ========================================
            # Step 3: Map column names flexibly
            # ========================================
            col_map = {}

            # Gene symbol column
            gene_candidates = [
                "genesymbol",
                "Gene_Symbol",
                "gene_symbol",
                "GeneSymbol",
                "Gene",
                "gene",
                "geneName",
                "gene_name",
            ]
            for col_name in gene_candidates:
                if col_name in df.columns:
                    col_map["genesymbol"] = col_name
                    logger.debug(f"[UC-5.5] Mapped genesymbol to '{col_name}'")
                    break

            # Compound name column
            compound_candidates = [
                "compoundname",
                "Compound_Name",
                "compound_name",
                "CompoundName",
                "Compound",
                "compound",
                "compoundID",
                "Compound_ID",
            ]
            for col_name in compound_candidates:
                if col_name in df.columns:
                    col_map["compoundname"] = col_name
                    logger.debug(f"[UC-5.5] Mapped compoundname to '{col_name}'")
                    break

            # ========================================
            # Step 4: Validate required columns found
            # ========================================
            required = ["genesymbol", "compoundname"]
            missing_cols = [col for col in required if col not in col_map]

            if missing_cols:
                logger.error(
                    f"[UC-5.5] Missing columns: {missing_cols}. "
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
            df_for_plot = df[[col_map["genesymbol"], col_map["compoundname"]]].rename(
                columns={
                    col_map["genesymbol"]: "genesymbol",
                    col_map["compoundname"]: "compoundname",
                }
            )

            # Clean data
            initial_count = len(df_for_plot)
            df_for_plot = df_for_plot.dropna()

            # Strip whitespace and remove placeholders
            for col in df_for_plot.columns:
                df_for_plot[col] = df_for_plot[col].astype(str).str.strip()

            df_for_plot = df_for_plot[
                ~df_for_plot["genesymbol"].isin(
                    ["#N/D", "#N/A", "N/D", "", "nan", "None"]
                )
            ]
            df_for_plot = df_for_plot[
                ~df_for_plot["compoundname"].isin(
                    ["#N/D", "#N/A", "N/D", "", "nan", "None"]
                )
            ]

            cleaned_count = len(df_for_plot)
            logger.info(
                f"[UC-5.5] Data cleaned: {initial_count} -> {cleaned_count} rows"
            )

            if df_for_plot.empty:
                return _create_error_message(
                    "No valid gene-compound data found after cleaning.", "bi bi-funnel"
                )

            # Log statistics
            n_genes = df_for_plot["genesymbol"].nunique()
            n_compounds = df_for_plot["compoundname"].nunique()

            logger.info(
                f"[UC-5.5] Data statistics: "
                f"{n_genes} unique genes, {n_compounds} unique compounds"
            )

            # ========================================
            # Step 6: Generate plot using PlotService
            # ========================================
            logger.debug("[UC-5.5] Calling PlotService to generate similarity network")

            fig = plot_service.generate_plot(
                use_case_id="UC-5.5",
                data=df_for_plot,
                filters=None,
                force_refresh=False,
            )

            logger.info("[UC-5.5] Similarity network generation successful")

            # ========================================
            # Step 7: Prepare download filename and return chart component
            # ========================================
            try:
                suggested = sanitize_filename("UC-5.5", "gene_gene_network", "png")
            except Exception:
                suggested = "gene_gene_network.png"
            base_filename = os.path.splitext(suggested)[0]

            return html.Div(
                [
                    # Statistics summary
                    html.Div(
                        [
                            html.Small(
                                [
                                    html.I(className="bi bi-info-circle me-2"),
                                    f"Network built from {n_genes} genes sharing "
                                    f"{n_compounds} compounds",
                                ],
                                className="text-muted",
                            )
                        ],
                        className="mb-2",
                    ),
                    # Graph
                    dcc.Graph(
                        id="uc-5-5-graph",
                        figure=fig,
                        config={
                            "displayModeBar": True,
                            "displaylogo": False,
                            "responsive": True,
                            "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                            "toImageButtonOptions": {
                                "format": "png",
                                "filename": base_filename,
                                "height": 1000,
                                "width": 1200,
                                "scale": 6,
                            },
                        },
                        style={"height": "900px", "width": "100%"},
                        className="mt-3",
                    ),
                ]
            )

        except ValueError as ve:
            logger.error(
                f"[UC-5.5] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-5.5] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-5.5] All callbacks registered successfully")


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
