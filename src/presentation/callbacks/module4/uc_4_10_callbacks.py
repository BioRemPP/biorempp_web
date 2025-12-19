"""
UC-4.10 Callbacks - Genetic Diversity of Enzymatic Activities Across Samples.

This module implements callback functions for visualizing genetic diversity
of enzymatic activities across all samples through bubble chart analysis.

Functions
---------
register_uc_4_10_callbacks
    Register all UC-4.10 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses bubble chart for genetic diversity mapping
- BioRemPP database REQUIRED (with enzyme_activity column)
- Renders automatically when accordion opens (no dropdown required)

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


def register_uc_4_10_callbacks(app, plot_service) -> None:
    """
    Register UC-4.10 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 2 callbacks: panel toggle and bubble chart rendering
    - Chart renders automatically when accordion opens
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-4-10-collapse", "is_open"),
        Input("uc-4-10-collapse-button", "n_clicks"),
        State("uc-4-10-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_4_10_info_panel(n_clicks, is_open):
        """
        Toggle UC-4.10 informative panel collapse.

        Parameters
        ----------
        n_clicks : int
            Number of clicks on collapse button.
        is_open : bool
            Current collapse state.

        Returns
        -------
        bool
            New collapse state (toggled).
        """
        logger.info(
            f"[UC-4.10] 🔘 Toggle clicked! n_clicks={n_clicks}, " f"is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-4.10] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-4.10] ⊘ No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        Output("uc-4-10-chart-container", "children"),
        [
            Input("uc-4-10-accordion-group", "active_item"),
            Input("merged-result-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def render_uc_4_10(active_item: Optional[str], merged_data: Optional[dict]) -> Any:
        """
        Render UC-4.10 bubble chart when accordion opens.

        Rendering Logic:
        - Accordion opens: Render bubble chart automatically
        - No filtering required (displays all data)

        Data Processing (inline + config):
        1. Extract BioRemPP data from store
        2. Validate required columns: 'sample', 'enzyme_activity', 'genesymbol'
        3. Pass data to PlotService
        4. PlotService applies YAML config processing:
           - Filter: enzyme_activity != '#N/D'
           - GroupBy ['sample', 'enzyme_activity']
           - Count unique genesymbol (nunique)
           - Create bubble chart (X=enzyme_activity, Y=sample,
             Size/Color=unique_gene_count)

        Parameters
        ----------
        active_item : Optional[str]
            Currently active accordion item (triggers rendering).
        merged_data : Optional[dict]
            Merged data from store with 'biorempp_df' key.

        Returns
        -------
        dcc.Graph or html.Div
            Bubble chart component or error/placeholder message.

        Raises
        ------
        PreventUpdate
            If accordion not opened or no data available.
        """
        # Check if accordion is opened
        if not active_item or active_item != "uc-4-10-accordion":
            logger.debug("[UC-4.10] Accordion not opened")
            raise PreventUpdate

        # Check data availability
        if not merged_data:
            logger.warning("[UC-4.10] No data available")
            return _create_error_message("No data available for visualization")

        try:
            # Extract BioRemPP DataFrame from store
            logger.debug(f"[UC-4.10] Received data type: {type(merged_data)}")

            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error(
                    f"[UC-4.10] Invalid data format: expected dict with "
                    f"'biorempp_df'"
                )
                return _create_error_message(
                    "BioRemPP database data not found. "
                    "Please ensure BioRemPP data is loaded."
                )

            df = pd.DataFrame(merged_data["biorempp_df"])

            # Validate required columns (with variant checking)
            required_cols = {
                "sample": ["sample", "Sample", "sample_id"],
                "enzyme_activity": [
                    "enzyme_activity",
                    "Enzyme_Activity",
                    "EnzymeActivity",
                    "enzyme",
                ],
                "genesymbol": [
                    "genesymbol",
                    "GeneSymbol",
                    "gene_symbol",
                    "Gene_Symbol",
                ],
            }

            col_mapping = {}
            for required, candidates in required_cols.items():
                found = False
                for candidate in candidates:
                    if candidate in df.columns:
                        col_mapping[required] = candidate
                        found = True
                        break
                if not found:
                    logger.error(
                        f"[UC-4.10] Required column '{required}' not found. "
                        f"Available: {df.columns.tolist()}"
                    )
                    return _create_error_message(f"Missing required column: {required}")

            # Normalize column names if needed
            if col_mapping["sample"] != "sample":
                df = df.rename(columns={col_mapping["sample"]: "sample"})
            if col_mapping["enzyme_activity"] != "enzyme_activity":
                df = df.rename(
                    columns={col_mapping["enzyme_activity"]: "enzyme_activity"}
                )
            if col_mapping["genesymbol"] != "genesymbol":
                df = df.rename(columns={col_mapping["genesymbol"]: "genesymbol"})

            # Check if data is empty after normalization
            if df.empty:
                logger.warning("[UC-4.10] No data found after normalization")
                return _create_error_message(
                    "No genetic diversity data available for visualization"
                )

            logger.info(f"[UC-4.10] Processing data with {len(df)} rows")

            # Generate plot using PlotService
            # (Further processing defined in uc_4_10_config.yaml:
            #  - Filter enzyme_activity != '#N/D'
            #  - GroupBy [sample, enzyme_activity]
            #  - Count unique genesymbol)
            use_case_id = "UC-4.10"

            logger.info(
                f"[UC-4.10] Calling PlotService for {use_case_id} "
                f"with {len(df)} rows"
            )

            fig = plot_service.generate_plot(use_case_id=use_case_id, data=df)

            logger.info(f"[UC-4.10] [OK] Plot generated successfully")

            try:
                suggested = sanitize_filename("UC-4.10", "pathway_trends", "png")
            except Exception:
                suggested = "pathway_trends.png"

            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                figure=fig,
                config={
                    "displayModeBar": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                    },
                },
                style={"height": "650px"},
            )

        except ValueError as ve:
            logger.error(f"[UC-4.10] Value error: {ve}")
            return _create_error_message(str(ve))
        except Exception as e:
            logger.error(f"[UC-4.10] Rendering error: {e}", exc_info=True)
            return _create_error_message(f"Error generating chart: {str(e)}")


def _create_error_message(message: str) -> html.Div:
    """
    Create error message component.

    Parameters
    ----------
    message : str
        Error message to display.

    Returns
    -------
    html.Div
        Error message component with alert styling.
    """
    return html.Div(
        [html.I(className="fas fa-exclamation-triangle me-2"), message],
        className="alert alert-warning mt-3",
    )
