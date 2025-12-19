"""
UC-1.5 Callbacks - Regulatory Compliance Scorecard.

This module implements callback functions for visualizing regulatory compliance
scores across samples and agencies using heatmap scorecards.

Functions
---------
register_uc_1_5_callbacks
    Register all UC-1.5 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses HeatmapScoredStrategy for compliance visualization
- Implements on-demand rendering for performance optimization

Version: 1.0.0
"""

import logging
import os
from typing import Any, Dict, Optional

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

logger = logging.getLogger(__name__)

from src.presentation.components.download_component import sanitize_filename


def register_uc_1_5_callbacks(app, plot_service) -> None:
    """
    Register all UC-1.5 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and heatmap scorecard rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("Registering UC-1.5 callbacks")

    @app.callback(
        Output("uc-1-5-collapse", "is_open"),
        Input("uc-1-5-collapse-button", "n_clicks"),
        State("uc-1-5-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_1_5_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """
        Toggle UC-1.5 information panel visibility.

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
            logger.debug(f"UC-1.5 info panel toggled. New state: {not is_open}")
            return not is_open
        return is_open

    @app.callback(
        Output("uc-1-5-chart", "children"),
        Input("uc-1-5-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_1_5(
        active_item: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-1.5 heatmap scorecard when accordion is activated.

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
        - Extracts Sample, Compound, and Agency data from BioRemPP DataFrame
        - Calculates compliance scores: (sample compounds / agency compounds) × 100%
        - Uses HeatmapScoredStrategy via PlotService
        """
        logger.debug(f"UC-1.5 render callback triggered. Active item: {active_item}")

        # Check if UC-1.5 accordion is active
        if not active_item or active_item != "uc-1-5-accordion":
            logger.debug("UC-1.5 accordion not active. Preventing update.")
            raise PreventUpdate

        try:
            # Validate merged_data structure
            if not merged_data:
                logger.warning("UC-1.5: merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please load or merge data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error("UC-1.5: merged_data does not contain 'biorempp_df' key")
                return _create_error_message(
                    "Invalid data structure. Expected 'biorempp_df' in merged data.",
                    "bi bi-x-circle",
                )

            # Extract DataFrame
            logger.debug("UC-1.5: Extracting DataFrame from merged_data")
            df = pd.DataFrame(merged_data["biorempp_df"])

            if df.empty:
                logger.warning("UC-1.5: DataFrame is empty")
                return _create_error_message(
                    "The dataset is empty. Please load data with Sample, Compound, and Agency information.",
                    "bi bi-inbox",
                )

            logger.info(
                f"UC-1.5: Processing DataFrame with {len(df)} rows and {len(df.columns)} columns"
            )

            # Map column names flexibly to handle different naming conventions
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
                    logger.debug(f"UC-1.5: Mapped Sample to column '{col_name}'")
                    break

            # Try to find Compound column
            compound_candidates = [
                "Compound_Name",
                "compound",
                "compoundname",
                "compound_name",
                "Compound",
                "COMPOUND",
                "compound_id",
            ]
            for col_name in compound_candidates:
                if col_name in df.columns:
                    col_map["Compound"] = col_name
                    logger.debug(f"UC-1.5: Mapped Compound to column '{col_name}'")
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
            ]
            for col_name in agency_candidates:
                if col_name in df.columns:
                    col_map["Agency"] = col_name
                    logger.debug(f"UC-1.5: Mapped Agency to column '{col_name}'")
                    break

            # Validate required columns were found
            if "Sample" not in col_map:
                logger.error(
                    f"UC-1.5: Sample column not found. Available: {df.columns.tolist()}"
                )
                return _create_error_message(
                    f"Required column 'Sample' (or variants) not found. Available: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            if "Compound" not in col_map:
                logger.error(
                    f"UC-1.5: Compound column not found. Available: {df.columns.tolist()}"
                )
                return _create_error_message(
                    f"Required column 'Compound' (or variants) not found. Available: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            if "Agency" not in col_map:
                logger.error(
                    f"UC-1.5: Agency column not found. Available: {df.columns.tolist()}"
                )
                return _create_error_message(
                    f"Required column 'Agency' (or variants) not found. Available: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            # Extract mapped column names
            sample_col = col_map["Sample"]
            compound_col = col_map["Compound"]
            agency_col = col_map["Agency"]

            logger.debug(
                f"UC-1.5: Using columns - "
                f"Sample: '{sample_col}', Compound: '{compound_col}', Agency: '{agency_col}'"
            )

            # === DATA PREPARATION ===
            # Rename columns to standard names expected by strategy
            df_for_plot = df[[sample_col, compound_col, agency_col]].rename(
                columns={
                    sample_col: "Sample",
                    compound_col: "Compound",
                    agency_col: "Agency",
                }
            )

            # Clean data: remove nulls and strip whitespace
            df_for_plot = df_for_plot.dropna()
            df_for_plot["Sample"] = df_for_plot["Sample"].str.strip()
            df_for_plot["Compound"] = df_for_plot["Compound"].str.strip()
            df_for_plot["Agency"] = df_for_plot["Agency"].str.strip()

            # Remove duplicates
            df_for_plot = df_for_plot.drop_duplicates()

            if df_for_plot.empty:
                logger.warning("UC-1.5: All rows contain null values after cleaning")
                return _create_error_message(
                    "No valid Sample-Compound-Agency combinations found after data cleaning.",
                    "bi bi-funnel",
                )

            logger.info(
                f"UC-1.5: Prepared {len(df_for_plot)} rows for HeatmapScoredStrategy"
            )

            # === PLOT GENERATION ===
            logger.debug("UC-1.5: Calling PlotService to generate heatmap scorecard")

            # Generate plot using PlotService with HeatmapScoredStrategy
            # Strategy will calculate compliance scores automatically
            fig = plot_service.generate_plot(
                use_case_id="UC-1.5",
                data=df_for_plot,
                filters={},  # No filters needed for this use case
                force_refresh=False,
            )

            logger.info("UC-1.5: Chart generation successful")

            # Return chart with loading spinner
            try:
                suggested = sanitize_filename(
                    "UC-1.5", "regulatory_compliance_scorecard", "png"
                )
                base_filename = os.path.splitext(suggested)[0]
            except Exception:
                base_filename = "uc_1_5_regulatory_compliance_scorecard"

            return dcc.Graph(
                id="uc-1-5-graph",
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
                        "scale": 2,
                    },
                },
                style={"height": "600px", "width": "100%"},
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(
                f"UC-1.5: ValueError during processing - {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"UC-1.5: Unexpected error - {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred while generating the chart: {str(e)}",
                "bi bi-bug",
            )


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
        [
            html.I(className=f"{icon_class} me-2"),
            html.Span(message),
        ],
        className="alert alert-warning d-flex align-items-center mt-3",
        role="alert",
    )
