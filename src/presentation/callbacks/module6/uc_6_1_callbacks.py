"""
UC-6.1 Callbacks - Regulatory to Molecular Interaction Flow.

This module implements callback functions for visualizing regulatory-to-molecular
interaction flows through Sankey diagram analysis.

Functions
---------
register_uc_6_1_callbacks
    Register all UC-6.1 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses SankeyStrategy for multi-level flow visualization
- BioRemPP database required for referenceAG, sample, genesymbol, compoundname data

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


def register_uc_6_1_callbacks(app, plot_service) -> None:
    """
    Register all UC-6.1 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and Sankey diagram rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-6.1] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-6-1-collapse", "is_open"),
        Input("uc-6-1-collapse-button", "n_clicks"),
        State("uc-6-1-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_6_1_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """Toggle UC-6.1 informative panel collapse state."""
        if n_clicks:
            logger.debug(f"[UC-6.1] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Render Sankey Diagram
    # ========================================
    @app.callback(
        Output("uc-6-1-chart", "children"),
        [
            Input("merged-result-store", "data"),
            Input("uc-6-1-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def render_uc_6_1(
        merged_data: Optional[Dict[str, Any]], active_item: Optional[str]
    ) -> html.Div:
        """
        Render UC-6.1 Sankey diagram on accordion activation.

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
        - Maps 4 column names flexibly (referenceAG/sample/genesymbol/compoundname)
        - Cleans data removing nulls and placeholder values
        - Passes prepared data to SankeyStrategy via PlotService
        - Generates multi-level regulatory-to-molecular flow diagram
        """
        logger.info(f"[UC-6.1] Render triggered, active_item: {active_item}")

        # Check if accordion is active
        if active_item != "uc-6-1-accordion":
            logger.debug("[UC-6.1] Accordion not active. Skipping render.")
            raise PreventUpdate

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-6.1] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-6.1] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            if "biorempp_df" not in merged_data:
                logger.error("[UC-6.1] merged_data does not contain 'biorempp_df' key")
                return _create_error_message(
                    "BioRemPP data not found. This use case requires "
                    "BioRemPP database.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrame
            # ========================================
            logger.debug("[UC-6.1] Extracting DataFrame from merged_data")
            biorempp_data = merged_data["biorempp_df"]

            if not biorempp_data:
                logger.warning("[UC-6.1] biorempp_df is empty")
                return _create_error_message(
                    "BioRemPP dataset is empty. Please check your input data.",
                    "bi bi-inbox",
                )

            df = pd.DataFrame(biorempp_data)

            if df.empty:
                logger.warning("[UC-6.1] DataFrame is empty after conversion")
                return _create_error_message(
                    "No data available after processing.", "bi bi-inbox"
                )

            logger.info(
                f"[UC-6.1] Processing DataFrame: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )
            logger.debug(f"[UC-6.1] Available columns: {df.columns.tolist()}")

            # ========================================
            # Step 3: Map column names flexibly
            # ========================================
            col_map = {}

            # Regulatory agency column
            agency_candidates = [
                "referenceAG",
                "ReferenceAG",
                "reference_ag",
                "Agency",
                "agency",
                "regulatory_agency",
                "RegulatoryAgency",
            ]
            for col_name in agency_candidates:
                if col_name in df.columns:
                    col_map["referenceAG"] = col_name
                    logger.debug(f"[UC-6.1] Mapped referenceAG to '{col_name}'")
                    break

            # Sample column
            sample_candidates = [
                "sample",
                "Sample",
                "sample_name",
                "SampleName",
                "sample_id",
                "SampleID",
            ]
            for col_name in sample_candidates:
                if col_name in df.columns:
                    col_map["sample"] = col_name
                    logger.debug(f"[UC-6.1] Mapped sample to '{col_name}'")
                    break

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
                    logger.debug(f"[UC-6.1] Mapped genesymbol to '{col_name}'")
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
                    logger.debug(f"[UC-6.1] Mapped compoundname to '{col_name}'")
                    break

            # ========================================
            # Step 4: Validate required columns found
            # ========================================
            required = ["referenceAG", "sample", "genesymbol", "compoundname"]
            missing_cols = [col for col in required if col not in col_map]

            if missing_cols:
                logger.error(
                    f"[UC-6.1] Missing columns: {missing_cols}. "
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
                    col_map["referenceAG"],
                    col_map["sample"],
                    col_map["genesymbol"],
                    col_map["compoundname"],
                ]
            ].rename(
                columns={
                    col_map["referenceAG"]: "referenceAG",
                    col_map["sample"]: "sample",
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

            # Remove placeholder values
            placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None"]
            for col in df_for_plot.columns:
                df_for_plot = df_for_plot[~df_for_plot[col].isin(placeholder_values)]

            cleaned_count = len(df_for_plot)
            logger.info(
                f"[UC-6.1] Data cleaned: {initial_count} -> {cleaned_count} rows"
            )

            if df_for_plot.empty:
                return _create_error_message(
                    "No valid interaction flows found after cleaning.", "bi bi-funnel"
                )

            # Log statistics
            n_agencies = df_for_plot["referenceAG"].nunique()
            n_samples = df_for_plot["sample"].nunique()
            n_genes = df_for_plot["genesymbol"].nunique()
            n_compounds = df_for_plot["compoundname"].nunique()

            logger.info(
                f"[UC-6.1] Sankey statistics: "
                f"{n_agencies} agencies, {n_samples} samples, "
                f"{n_genes} genes, {n_compounds} compounds"
            )

            # ========================================
            # Step 6: Generate plot using PlotService
            # ========================================
            logger.debug("[UC-6.1] Calling PlotService to generate Sankey diagram")

            fig = plot_service.generate_plot(
                use_case_id="UC-6.1",
                data=df_for_plot,
                filters=None,
                force_refresh=False,
            )

            logger.info("[UC-6.1] Sankey diagram generation successful")

            # ========================================
            # Step 7: Prepare filename and return chart component
            # ========================================
            try:
                suggested = sanitize_filename(
                    "UC-6.1", "regulatory_molecular_flow", "png"
                )
            except Exception:
                suggested = "regulatory_molecular_flow.png"

            base_filename = os.path.splitext(suggested)[0]

            return html.Div(
                [
                    # Statistics summary
                    html.Div(
                        [
                            html.Small(
                                [
                                    html.I(className="bi bi-info-circle me-2"),
                                    f"Flow: {n_agencies} agencies -> {n_samples} samples -> "
                                    f"{n_genes} genes -> {n_compounds} compounds "
                                    f"({cleaned_count:,} interactions)",
                                ],
                                className="text-muted",
                            )
                        ],
                        className="mb-2",
                    ),
                    # Graph container with overflow control
                    html.Div(
                        [
                            dcc.Graph(
                                id="uc-6-1-graph",
                                figure=fig,
                                config={
                                    "displayModeBar": True,
                                    "displaylogo": False,
                                    "responsive": True,
                                    "modeBarButtonsToRemove": [
                                        "pan2d",
                                        "lasso2d",
                                        "select2d",
                                    ],
                                    "toImageButtonOptions": {
                                        "format": "png",
                                        "filename": base_filename,
                                        "height": 1000,
                                        "width": 1400,
                                        "scale": 6,
                                    },
                                },
                                style={
                                    "height": "900px",
                                    "width": "100%",
                                    "minWidth": "100%",
                                },
                                className="mt-3",
                            )
                        ],
                        style={
                            "width": "100%",
                            "overflowX": "auto",
                            "overflowY": "hidden",
                        },
                    ),
                ]
            )

        except ValueError as ve:
            logger.error(
                f"[UC-6.1] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-6.1] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-6.1] All callbacks registered successfully")


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
