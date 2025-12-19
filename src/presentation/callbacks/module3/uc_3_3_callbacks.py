"""
UC-3.3 Callbacks - Interactive Hierarchical Clustering of Samples.

This module implements callback functions for hierarchical clustering analysis
with interactive distance metric and linkage method selection.

Functions
---------
register_uc_3_3_callbacks
    Register all UC-3.3 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Ward linkage requires Euclidean distance metric
- Uses binary presence/absence matrix from Sample x KO data

Version: 1.0.0
"""

import logging
import os
from typing import Any, Optional

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)
logger.propagate = False  # Prevent duplicate logs


def register_uc_3_3_callbacks(app, plot_service) -> None:
    """
    Register UC-3.3 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance.

    Notes
    -----
    Registered callbacks:
    - toggle_uc_3_3_info_panel: Toggle informative panel collapse
    - render_uc_3_3: Main dendrogram rendering logic with validation
    """

    @app.callback(
        Output("uc-3-3-collapse", "is_open"),
        Input("uc-3-3-collapse-button", "n_clicks"),
        State("uc-3-3-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_3_3_info_panel(n_clicks, is_open):
        """Toggle UC-3.3 informative panel collapse."""
        if n_clicks:
            return not is_open
        return is_open

    @app.callback(
        Output("uc-3-3-chart-container", "children"),
        [
            Input("uc-3-3-metric-dropdown", "value"),
            Input("uc-3-3-method-dropdown", "value"),
        ],
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_3_3(
        metric: Optional[str], method: Optional[str], merged_data: Optional[dict]
    ) -> Any:
        """
        Render UC-3.3 dendrogram based on dropdown selections.

        Parameters
        ----------
        metric : str, optional
            Selected distance metric (jaccard, euclidean, cosine, etc).
        method : str, optional
            Selected clustering method (average, complete, single, ward).
        merged_data : dict, optional
            Merged data from store containing biorempp_df.

        Returns
        -------
        dcc.Graph or html.Div
            Dendrogram component or error message.

        Raises
        ------
        PreventUpdate
            If both dropdowns not selected or no data available.

        Notes
        -----
        - Renders when both dropdowns have valid values
        - Updates automatically when either dropdown changes
        - Creates binary matrix using pd.crosstab
        - Passes data and parameters to PlotService
        """
        logger.debug(f"UC-3.3 callback triggered: metric={metric}, method={method}")

        # Check data availability
        if not merged_data:
            logger.warning("UC-3.3: No data available in merged-result-store")
            raise PreventUpdate

        logger.debug(f"UC-3.3: Merged data keys: {merged_data.keys()}")

        # Check if both dropdowns have values
        if not metric or not method:
            logger.debug("UC-3.3: Both dropdowns must have values selected")
            raise PreventUpdate

        logger.info(f"UC-3.3: Starting render with metric={metric}, method={method}")

        # Generate plot
        try:
            logger.debug("UC-3.3: Starting data extraction")

            # Extract DataFrame from store
            if not isinstance(merged_data, dict):
                error_msg = f"Invalid data type: {type(merged_data)}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            if "biorempp_df" not in merged_data:
                error_msg = (
                    f"Data must contain 'biorempp_df' key. "
                    f"Available keys: {list(merged_data.keys())}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.debug("UC-3.3: Converting to DataFrame")
            df = pd.DataFrame(merged_data["biorempp_df"])
            logger.info(
                f"UC-3.3: biorempp_df loaded - "
                f"shape: {df.shape}, columns: {df.columns.tolist()}"
            )

            # Validate required columns
            if "Sample" not in df.columns or "KO" not in df.columns:
                error_msg = (
                    f"Data must contain 'Sample' and 'KO' columns. "
                    f"Found: {set(df.columns)}"
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.debug(
                f"UC-3.3: Sample count: {df['Sample'].nunique()}, "
                f"KO count: {df['KO'].nunique()}"
            )

            # DATA PROCESSING: Create binary presence/absence matrix
            logger.debug("UC-3.3: Creating binary matrix with pd.crosstab")
            binary_matrix = pd.crosstab(df["Sample"], df["KO"])
            logger.debug(f"UC-3.3: Crosstab created - shape: {binary_matrix.shape}")

            # Convert to strict binary (presence=1, absence=0)
            binary_matrix[binary_matrix > 0] = 1
            logger.info(
                f"UC-3.3: Binary matrix ready - "
                f"{binary_matrix.shape[0]} samples × "
                f"{binary_matrix.shape[1]} KOs"
            )

            # Validate minimum samples for clustering
            if binary_matrix.shape[0] < 2:
                error_msg = "Need at least 2 samples to perform clustering"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # Build filters with metric and method parameters
            filters = {
                "metric": metric,
                "method": method,
                "filters_hash": f"{metric}_{method}",
            }
            logger.debug(f"UC-3.3: Filters prepared: {filters}")

            # Generate plot via PlotService
            logger.debug("UC-3.3: Calling PlotService.generate_plot()")
            fig = plot_service.generate_plot(
                use_case_id="UC-3.3",
                data=binary_matrix,
                filters=filters,
                force_refresh=False,
            )
            logger.info("UC-3.3: Figure generated successfully")

            # Create chart component
            try:
                logger.debug("UC-3.3: Generating download filename")
                suggested = sanitize_filename(
                    "UC-3.3", f"hierarchical_clustering_{method}_{metric}", "png"
                )
                base_filename = os.path.splitext(suggested)[0]
                logger.debug(f"UC-3.3: Filename: {base_filename}")
            except Exception as e:
                logger.warning(
                    f"UC-3.3: Filename generation failed: {e}, " "using fallback"
                )
                base_filename = f"uc_3_3_dendrogram_{method}_{metric}"

            logger.debug("UC-3.3: Creating dcc.Graph component")
            chart_component = dcc.Graph(
                figure=fig,
                id="uc-3-3-dendrogram",
                config={
                    "displayModeBar": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 800,
                        "width": 1200,
                        "scale": 2,
                    },
                },
            )

            logger.info("UC-3.3: Dendrogram rendered successfully")
            return chart_component

        except ValueError as e:
            logger.error(f"UC-3.3 validation error: {e}", exc_info=True)
            return _create_error_message(
                f"Data validation failed: {str(e)}", icon="fas fa-exclamation-triangle"
            )

        except Exception as e:
            logger.error(
                f"UC-3.3 unexpected error: {type(e).__name__}: {e}", exc_info=True
            )
            return _create_error_message(
                f"Error generating dendrogram: {str(e)}. " "Check logs for details.",
                icon="fas fa-exclamation-circle",
            )


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
