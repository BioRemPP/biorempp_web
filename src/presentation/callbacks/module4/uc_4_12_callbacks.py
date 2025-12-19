"""
UC-4.12 Callbacks - Interactive Pathway Relationships by Sample (HADEG).

This module implements callback functions for visualizing pathway-compound
relationships through interactive sample selection and heatmap analysis.

Functions
---------
register_uc_4_12_callbacks
    Register all UC-4.12 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses heatmap for pathway-compound pathway matrix visualization
- HADEG database REQUIRED
- Matrix shows unique KO counts per (Pathway, Compound) combination

Version: 1.0.0
"""

import logging
import os
from typing import Any, Optional, Tuple

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)
logger.propagate = False  # Prevent duplicate logs


def register_uc_4_12_callbacks(app, plot_service) -> None:
    """
    Register UC-4.12 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 3 callbacks: panel toggle, sample dropdown initialization,
      and heatmap rendering
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-4-12-collapse", "is_open"),
        Input("uc-4-12-collapse-button", "n_clicks"),
        State("uc-4-12-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_4_12_info_panel(n_clicks, is_open):
        """
        Toggle UC-4.12 informative panel collapse.

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
            f"[UC-4.12] 🔘 Toggle clicked! n_clicks={n_clicks}, " f"is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-4.12] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-4.12] ⊘ No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-4-12-sample-dropdown", "options"),
            Output("uc-4-12-sample-dropdown", "value"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-4-12-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_sample_dropdown_uc_4_12(
        merged_data: Optional[dict], active_item: Optional[str]
    ) -> Tuple[list, None]:
        """
        Initialize sample dropdown with HADEG data.

        This callback populates the dropdown menu with available samples
        extracted from processed HADEG data, enabling users to select
        specific samples for pathway relationship analysis.

        Data Processing (inline):
        1. Extract HADEG data from store
        2. Validate 'Sample' column exists
        3. Extract unique samples
        4. Sort alphabetically
        5. Create dropdown options

        Parameters
        ----------
        merged_data : Optional[dict]
            Pre-processed merged data stored in merged-result-store.
            Expected structure: dict with 'hadeg_df' key.
        active_item : Optional[str]
            Currently active accordion item (triggers re-initialization).

        Returns
        -------
        Tuple[list, None]
            - First element: List of dropdown option dictionaries with
              label/value pairs for sample selection. Empty list
              if no data available.
            - Second element: Default selection value (None for no
              initial selection).

        Raises
        ------
        PreventUpdate
            If no data available or required column not found.
        """
        logger.info(
            f"[UC-4.12] 🔄 Dropdown init triggered, " f"data type: {type(merged_data)}"
        )

        if not merged_data:
            logger.debug("[UC-4.12] No data in store, preventing dropdown init")
            return [], None

        # Check if this is initial call with empty/invalid data
        if isinstance(merged_data, dict) and not merged_data:
            logger.debug("[UC-4.12] Empty dict in store, preventing dropdown init")
            return [], None

        try:
            # Extract HADEG DataFrame from store
            if not isinstance(merged_data, dict) or "hadeg_df" not in merged_data:
                logger.error(
                    f"[UC-4.12] Invalid data format: expected dict with "
                    f"'hadeg_df', got {type(merged_data)}"
                )
                raise PreventUpdate

            df = pd.DataFrame(merged_data["hadeg_df"])

            # Validate 'Sample' column exists
            sample_col_variants = ["Sample", "sample", "sample_id", "Sample_ID"]

            sample_col = None
            for variant in sample_col_variants:
                if variant in df.columns:
                    sample_col = variant
                    logger.debug(f"[UC-4.12] Found sample column: '{variant}'")
                    break

            if not sample_col:
                logger.error(
                    f"[UC-4.12] Required column 'Sample' not found. "
                    f"Available columns: {df.columns.tolist()}"
                )
                raise PreventUpdate

            # Extract unique samples
            samples = sorted(df[sample_col].dropna().unique())

            logger.debug(
                f"[UC-4.12] Extracted {len(samples)} unique samples: "
                f"{samples[:5]}..."  # Show first 5
            )

            # Create dropdown options
            options = [{"label": sample, "value": sample} for sample in samples]

            logger.info(
                f"[UC-4.12] Dropdown initialized with {len(options)} " f"samples"
            )

            return options, None

        except Exception as e:
            logger.error(f"[UC-4.12] Dropdown initialization error: {e}")
            raise PreventUpdate

    @app.callback(
        Output("uc-4-12-chart-container", "children"),
        Input("uc-4-12-sample-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_4_12(
        selected_sample: Optional[str], merged_data: Optional[dict]
    ) -> Any:
        """
        Render UC-4.12 heatmap for selected sample.

        This callback generates a heatmap visualization showing the
        pathway-compound pathway matrix (Pathway × Compound Pathway)
        with unique KO counts for the selected sample.

        Data Processing (inline):
        1. Extract HADEG data from store
        2. Validate required columns
        3. Filter by selected sample
        4. Pass filtered data to PlotService
        5. HeatmapStrategy processes:
           - Groups by (Pathway, compound_pathway)
           - Counts unique KOs
           - Pivots to matrix
           - Sorts by totals
           - Creates heatmap

        Parameters
        ----------
        selected_sample : Optional[str]
            Selected sample from dropdown.
        merged_data : Optional[dict]
            Merged data from store with 'hadeg_df' key.

        Returns
        -------
        dcc.Graph or html.Div
            Heatmap chart component or informative/error message.

        Raises
        ------
        PreventUpdate
            If no sample selected or no data available.
        """
        if not selected_sample:
            logger.debug("[UC-4.12] No sample selected, preventing update")
            raise PreventUpdate

        if not merged_data:
            logger.warning("[UC-4.12] No data available")
            return _create_error_message("No data available for visualization")

        try:
            # Extract HADEG DataFrame from store
            logger.debug(f"[UC-4.12] Received data type: {type(merged_data)}")

            if not isinstance(merged_data, dict) or "hadeg_df" not in merged_data:
                logger.error(
                    "[UC-4.12] Invalid data format: expected dict with " "'hadeg_df'"
                )
                return _create_error_message(
                    "HADEG database data not found. "
                    "Please ensure HADEG data is loaded."
                )

            df = pd.DataFrame(merged_data["hadeg_df"])

            # Validate required columns with variants
            required_cols_variants = {
                "sample": ["Sample", "sample", "sample_id"],
                "Pathway": ["Pathway", "pathway", "Path"],
                "compound_pathway": [
                    "Compound",
                    "compound",
                    "compound_pathway",
                    "Compound_Pathway",
                    "CompoundPathway",
                ],
                "ko": ["KO", "ko", "ko_id"],
            }

            col_mapping = {}
            for required, variants in required_cols_variants.items():
                found = False
                for variant in variants:
                    if variant in df.columns:
                        col_mapping[required] = variant
                        found = True
                        logger.debug(f"[UC-4.12] Mapped '{required}' → '{variant}'")
                        break
                if not found:
                    logger.error(
                        f"[UC-4.12] Required column '{required}' not "
                        f"found. Available: {df.columns.tolist()}"
                    )
                    return _create_error_message(f"Missing required column: {required}")

            # Normalize column names
            rename_mapping = {}
            if col_mapping["sample"] != "sample":
                rename_mapping[col_mapping["sample"]] = "sample"
            if col_mapping["Pathway"] != "Pathway":
                rename_mapping[col_mapping["Pathway"]] = "Pathway"
            if col_mapping["compound_pathway"] != "compound_pathway":
                rename_mapping[col_mapping["compound_pathway"]] = "compound_pathway"
            if col_mapping["ko"] != "ko":
                rename_mapping[col_mapping["ko"]] = "ko"

            if rename_mapping:
                df = df.rename(columns=rename_mapping)
                logger.debug(f"[UC-4.12] Renamed columns: {rename_mapping}")

            # Filter by selected sample
            filtered_df = df[df["sample"] == selected_sample].copy()

            if filtered_df.empty:
                logger.warning(
                    f"[UC-4.12] No data found for sample: " f"'{selected_sample}'"
                )
                return _create_error_message(
                    f"No data found for sample '{selected_sample}'. "
                    f"Try selecting a different sample."
                )

            logger.info(
                f"[UC-4.12] Filtered data: {len(filtered_df)} rows for "
                f"sample '{selected_sample}'"
            )

            # Remove NaNs from required columns
            filtered_df = filtered_df.dropna(
                subset=["Pathway", "compound_pathway", "ko"]
            )

            if filtered_df.empty:
                logger.warning("[UC-4.12] No valid data after removing NaNs")
                return _create_error_message("No valid data found after data cleaning.")

            # Generate plot using PlotService
            # HeatmapStrategy handles aggregation and matrix creation
            use_case_id = "UC-4.12"

            logger.info(
                f"[UC-4.12] Calling PlotService for {use_case_id} "
                f"with {len(filtered_df)} rows"
            )

            fig = plot_service.generate_plot(use_case_id=use_case_id, data=filtered_df)

            # Update title dynamically
            fig.update_layout(
                title=f"Pathway Functional Map for {selected_sample}", title_x=0.5
            )

            logger.info("[UC-4.12] [OK] Heatmap generated successfully")

            try:
                suggested = sanitize_filename("UC-4.12", "pathway_heatmap", "png")
            except Exception:
                suggested = "pathway_heatmap.png"

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
                style={"height": "700px"},
            )

        except ValueError as ve:
            logger.error(f"[UC-4.12] Value error: {ve}")
            return _create_error_message(str(ve))
        except Exception as e:
            logger.error(f"[UC-4.12] Rendering error: {e}", exc_info=True)
            return _create_error_message(f"Error generating heatmap: {str(e)}")


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
