"""
UC-5.3 Callbacks - Regulatory Relevance of Samples.

This module implements callback functions for visualizing sample-regulatory
agency interactions through chord diagram analysis with agency filtering.

Functions
---------
register_uc_5_3_callbacks
    Register all UC-5.3 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses ChordStrategy in aggregation mode with dropdown filtering
- BioRemPP database required for sample and referenceAG data
- Unique workflow: dropdown populates agencies, selection triggers render

Version: 1.0.0
"""

import logging
import os
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)


def register_uc_5_3_callbacks(app, plot_service) -> None:
    """
    Register all UC-5.3 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 3 callbacks: panel toggle, dropdown init, and chart render
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-5.3] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-5-3-collapse", "is_open"),
        Input("uc-5-3-collapse-button", "n_clicks"),
        State("uc-5-3-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_5_3_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """Toggle UC-5.3 informative panel collapse state."""
        if n_clicks:
            logger.debug(f"[UC-5.3] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Initialize Agency Dropdown
    # ========================================
    @app.callback(
        [
            Output("uc-5-3-agency-dropdown", "options"),
            Output("uc-5-3-agency-dropdown", "value"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-5-3-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_agency_dropdown(
        merged_data: Optional[Dict[str, Any]], active_item: Optional[str]
    ) -> Tuple[List[Dict[str, str]], Optional[str]]:
        """
        Initialize regulatory agency dropdown with BioRemPP data.

        Parameters
        ----------
        merged_data : dict, optional
            Store data with biorempp_df key.
        active_item : str, optional
            Accordion state trigger.

        Returns
        -------
        tuple of (list of dict, str or None)
            Dropdown options and default value (None).

        Notes
        -----
        - Extracts unique regulatory agencies from BioRemPP DataFrame
        - Filters out placeholder values (#N/D, #N/A, etc.)
        - Returns sorted list of agency options for dropdown
        """
        logger.info(f"[UC-5.3] Dropdown init triggered, " f"active_item: {active_item}")

        if not merged_data:
            logger.warning("[UC-5.3] No data available in store")
            raise PreventUpdate

        try:
            # Extract BioRemPP DataFrame
            if not isinstance(merged_data, dict):
                logger.warning("[UC-5.3] Invalid data structure")
                raise PreventUpdate

            biorempp_data = merged_data.get("biorempp_df")
            if biorempp_data is None or len(biorempp_data) == 0:
                logger.warning("[UC-5.3] No BioRemPP data in merged store")
                raise PreventUpdate

            # Convert list of dicts to DataFrame
            if isinstance(biorempp_data, list):
                df = pd.DataFrame(biorempp_data)
                logger.info(
                    f"[UC-5.3] BioRemPP DataFrame: {df.shape}, "
                    f"Columns: {df.columns.tolist()}"
                )
            else:
                df = biorempp_data

            # Find referenceAG column (case-insensitive)
            agency_col = None
            agency_candidates = [
                "referenceAG",
                "referenceag",
                "ReferenceAG",
                "reference_ag",
                "Agency",
                "agency",
            ]
            for col_name in agency_candidates:
                if col_name in df.columns:
                    agency_col = col_name
                    logger.debug(f"[UC-5.3] Found agency column: {col_name}")
                    break

            if agency_col is None:
                logger.error(
                    f"[UC-5.3] referenceAG column not found. "
                    f"Available: {df.columns.tolist()}"
                )
                raise PreventUpdate

            # Extract unique agencies
            df[agency_col] = df[agency_col].astype(str).str.strip()
            df = df[~df[agency_col].isin(["#N/D", "#N/A", "N/D", "", "nan"])]

            unique_agencies = sorted(df[agency_col].unique().tolist())

            if len(unique_agencies) == 0:
                logger.warning("[UC-5.3] No regulatory agencies found in data")
                raise PreventUpdate

            # Create dropdown options
            options = [{"label": agency, "value": agency} for agency in unique_agencies]

            logger.info(
                f"[UC-5.3] Dropdown initialized with "
                f"{len(options)} agencies: {unique_agencies[:5]}..."
            )
            return options, None

        except Exception as e:
            logger.error(f"[UC-5.3] Error initializing dropdown: {e}", exc_info=True)
            raise PreventUpdate

    # ========================================
    # Callback 3: Render Chord Diagram
    # ========================================
    @app.callback(
        Output("uc-5-3-chart", "children"),
        Input("uc-5-3-agency-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_5_3(
        selected_agency: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-5.3 chord diagram when an agency is selected.

        Parameters
        ----------
        selected_agency : str, optional
            Selected regulatory agency from dropdown.
        merged_data : dict, optional
            Dictionary containing merged result data with 'biorempp_df' key.

        Returns
        -------
        html.Div
            Container with chart or error message.

        Notes
        -----
        - Validates merged_data structure and extracts BioRemPP DataFrame
        - Maps column names flexibly (sample/referenceag with aliases)
        - Filters data by selected regulatory agency
        - Cleans data removing nulls and placeholder values
        - Passes filtered data to ChordStrategy via PlotService
        - Generates agency-specific chord diagram
        """
        logger.info(f"[UC-5.3] Render triggered, agency: {selected_agency}")

        # Check if agency is selected
        if not selected_agency:
            logger.debug("[UC-5.3] No agency selected. Showing prompt.")
            return html.Div(
                [
                    html.I(className="bi bi-hand-index me-2"),
                    html.Span(
                        "Please select a regulatory agency from the dropdown "
                        "above to visualize the chord diagram."
                    ),
                ],
                className="alert alert-info d-flex align-items-center mt-3",
                role="alert",
            )

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-5.3] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-5.3] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            if "biorempp_df" not in merged_data:
                logger.error("[UC-5.3] merged_data does not contain 'biorempp_df' key")
                return _create_error_message(
                    "BioRemPP data not found. This use case requires "
                    "BioRemPP database.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrame
            # ========================================
            logger.debug("[UC-5.3] Extracting DataFrame from merged_data")
            biorempp_data = merged_data["biorempp_df"]

            if not biorempp_data:
                logger.warning("[UC-5.3] biorempp_df is empty")
                return _create_error_message(
                    "BioRemPP dataset is empty. Please check your input data.",
                    "bi bi-inbox",
                )

            df = pd.DataFrame(biorempp_data)

            if df.empty:
                logger.warning("[UC-5.3] DataFrame is empty after conversion")
                return _create_error_message(
                    "No data available after processing.", "bi bi-inbox"
                )

            logger.info(
                f"[UC-5.3] Processing DataFrame: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )
            logger.debug(f"[UC-5.3] Available columns: {df.columns.tolist()}")

            # ========================================
            # Step 3: Map column names flexibly
            # ========================================
            col_map = {}

            # Sample column
            sample_candidates = [
                "sample",
                "Sample",
                "sample_id",
                "Sample_ID",
                "sampleID",
                "genome",
                "Genome",
            ]
            for col_name in sample_candidates:
                if col_name in df.columns:
                    col_map["sample"] = col_name
                    logger.debug(f"[UC-5.3] Mapped sample to '{col_name}'")
                    break

            # Reference Agency column
            agency_candidates = [
                "referenceAG",
                "referenceag",
                "ReferenceAG",
                "reference_ag",
                "Agency",
                "agency",
            ]
            for col_name in agency_candidates:
                if col_name in df.columns:
                    col_map["referenceag"] = col_name
                    logger.debug(f"[UC-5.3] Mapped referenceag to '{col_name}'")
                    break

            # ========================================
            # Step 4: Validate required columns found
            # ========================================
            required = ["sample", "referenceag"]
            missing_cols = [col for col in required if col not in col_map]

            if missing_cols:
                logger.error(
                    f"[UC-5.3] Missing columns: {missing_cols}. "
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
            df_for_plot = df[[col_map["sample"], col_map["referenceag"]]].rename(
                columns={
                    col_map["sample"]: "sample",
                    col_map["referenceag"]: "referenceag",
                }
            )

            # Clean data
            initial_count = len(df_for_plot)
            df_for_plot = df_for_plot.dropna()

            # Strip whitespace and remove placeholders
            for col in df_for_plot.columns:
                df_for_plot[col] = df_for_plot[col].astype(str).str.strip()

            df_for_plot = df_for_plot[
                ~df_for_plot["referenceag"].isin(["#N/D", "#N/A", "N/D", "", "nan"])
            ]
            df_for_plot = df_for_plot[
                ~df_for_plot["sample"].isin(["#N/D", "#N/A", "N/D", "", "nan"])
            ]

            # ========================================
            # Step 6: Filter by selected agency
            # ========================================
            df_filtered = df_for_plot[
                df_for_plot["referenceag"] == selected_agency
            ].copy()

            cleaned_count = len(df_filtered)
            logger.info(
                f"[UC-5.3] Data filtered for agency '{selected_agency}': "
                f"{initial_count} -> {cleaned_count} rows"
            )

            if df_filtered.empty:
                return _create_error_message(
                    f"No data available for agency: {selected_agency}", "bi bi-funnel"
                )

            # Log statistics
            n_samples = df_filtered["sample"].nunique()

            logger.info(
                f"[UC-5.3] Data statistics: "
                f"{n_samples} samples for agency '{selected_agency}'"
            )

            # ========================================
            # Step 7: Generate plot using PlotService
            # ========================================
            logger.debug("[UC-5.3] Calling PlotService to generate chord diagram")

            fig = plot_service.generate_plot(
                use_case_id="UC-5.3",
                data=df_filtered,
                filters={"agency": selected_agency},
                force_refresh=False,
            )

            logger.info("[UC-5.3] Chord diagram generation successful")

            # ========================================
            # Step 8: Prepare download filename and return chart component
            # ========================================
            try:
                suggested = sanitize_filename(
                    "UC-5.3", f"regulatory_relevance_{selected_agency}", "png"
                )
            except Exception:
                suggested = f"regulatory_relevance_{selected_agency}.png"
            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                id="uc-5-3-graph",
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
                        "width": 900,
                        "scale": 6,
                    },
                },
                style={"height": "800px", "width": "100%"},
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(
                f"[UC-5.3] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-5.3] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-5.3] All callbacks registered successfully")


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
