"""
UC-4.4 Callbacks - Interactive Functional Fingerprint of Samples by Pathway.

This module implements callback functions for visualizing functional fingerprint
of samples through interactive sample selection and radar chart analysis.

Functions
---------
register_uc_4_4_callbacks
    Register all UC-4.4 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses radar chart for functional fingerprint visualization
- KEGG database REQUIRED

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


def register_uc_4_4_callbacks(app, plot_service) -> None:
    """
    Register UC-4.4 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 3 callbacks: panel toggle, sample dropdown initialization,
      and radar chart rendering
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-4-4-collapse", "is_open"),
        Input("uc-4-4-collapse-button", "n_clicks"),
        State("uc-4-4-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_4_4_info_panel(n_clicks, is_open):
        """
        Toggle UC-4.4 informative panel collapse.

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
            f"[UC-4.4] 🔘 Toggle clicked! n_clicks={n_clicks}, " f"is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-4.4] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-4.4] ⊘ No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-4-4-sample-dropdown", "options"),
            Output("uc-4-4-sample-dropdown", "value"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-4-4-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_sample_dropdown_uc_4_4(
        merged_data: Optional[dict], active_item: Optional[str]
    ) -> Tuple[list, None]:
        """
        Initialize sample dropdown with KEGG data.

        This callback populates the dropdown menu with available samples
        extracted from processed KEGG data, enabling users to select
        specific samples for functional fingerprint analysis.

        Data Processing (inline):
        1. Extract KEGG data from store
        2. Validate 'Sample' column exists
        3. Extract unique samples
        4. Sort alphabetically
        5. Create dropdown options

        Parameters
        ----------
        merged_data : Optional[dict]
            Pre-processed merged data stored in merged-result-store.
            Expected structure: dict with 'kegg_df' key.
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
            f"[UC-4.4] 🔄 Dropdown init triggered, " f"data type: {type(merged_data)}"
        )

        if not merged_data:
            logger.debug("[UC-4.4] No data in store, preventing dropdown init")
            return [], None

        # Check if this is initial call with empty/invalid data
        if isinstance(merged_data, dict) and not merged_data:
            logger.debug("[UC-4.4] Empty dict in store, preventing dropdown init")
            return [], None

        try:
            # Extract KEGG DataFrame from store
            if not isinstance(merged_data, dict) or "kegg_df" not in merged_data:
                logger.error(
                    f"[UC-4.4] Invalid data format: expected dict with "
                    f"'kegg_df', got {type(merged_data)}"
                )
                raise PreventUpdate

            df = pd.DataFrame(merged_data["kegg_df"])

            # Validate 'Sample' column exists (check variants)
            sample_col_variants = ["Sample", "sample", "sample_id", "SampleID"]

            sample_col = None
            for variant in sample_col_variants:
                if variant in df.columns:
                    sample_col = variant
                    logger.debug(f"[UC-4.4] Found sample column: '{variant}'")
                    break

            if not sample_col:
                logger.error(
                    f"[UC-4.4] Required column 'Sample' not found. "
                    f"Available columns: {df.columns.tolist()}"
                )
                raise PreventUpdate

            # Extract unique samples
            samples = sorted(df[sample_col].dropna().unique())

            logger.debug(
                f"[UC-4.4] Extracted {len(samples)} unique samples: "
                f"{samples[:5]}..."  # Show first 5
            )

            # Create dropdown options
            options = [{"label": sample, "value": sample} for sample in samples]

            logger.info(
                f"[UC-4.4] Dropdown initialized with {len(options)} " f"samples"
            )

            return options, None

        except Exception as e:
            logger.error(f"[UC-4.4] Dropdown initialization error: {e}")
            raise PreventUpdate

    @app.callback(
        Output("uc-4-4-chart-container", "children"),
        Input("uc-4-4-sample-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_4_4(
        selected_sample: Optional[str], merged_data: Optional[dict]
    ) -> Any:
        """
        Render UC-4.4 radar chart for selected sample.

        This callback generates a radar chart visualization showing the
        functional fingerprint of the selected sample across all metabolic
        pathways based on unique KO counts.

        Data Processing (inline):
        1. Extract KEGG data from store
        2. Validate required columns
        3. Filter by selected sample
        4. Pass filtered data to PlotService
        5. RadarChartStrategy processes:
           - Groups by Pathway
           - Counts unique KOs
           - Creates radar chart

        Parameters
        ----------
        selected_sample : Optional[str]
            Selected sample from dropdown.
        merged_data : Optional[dict]
            Merged data from store with 'kegg_df' key.

        Returns
        -------
        dcc.Graph or html.Div
            Radar chart component or informative/error message.

        Raises
        ------
        PreventUpdate
            If no sample selected or no data available.
        """
        if not selected_sample:
            logger.debug("[UC-4.4] No sample selected, preventing update")
            raise PreventUpdate

        if not merged_data:
            logger.warning("[UC-4.4] No data available")
            return _create_error_message("No data available for visualization")

        try:
            # Extract KEGG DataFrame from store
            logger.debug(f"[UC-4.4] Received data type: {type(merged_data)}")

            if not isinstance(merged_data, dict) or "kegg_df" not in merged_data:
                logger.error(
                    "[UC-4.4] Invalid data format: expected dict with " "'kegg_df'"
                )
                return _create_error_message(
                    "KEGG database data not found. "
                    "Please ensure KEGG data is loaded."
                )

            df = pd.DataFrame(merged_data["kegg_df"])

            # Validate required columns with variants
            required_cols_variants = {
                "sample": ["Sample", "sample", "sample_id"],
                "pathway": ["Pathway", "pathway", "pathname", "Pathname"],
                "ko": ["KO", "ko", "ko_id"],
            }

            col_mapping = {}
            for required, variants in required_cols_variants.items():
                found = False
                for variant in variants:
                    if variant in df.columns:
                        col_mapping[required] = variant
                        found = True
                        logger.debug(f"[UC-4.4] Mapped '{required}' → '{variant}'")
                        break
                if not found:
                    logger.error(
                        f"[UC-4.4] Required column '{required}' not found. "
                        f"Available: {df.columns.tolist()}"
                    )
                    return _create_error_message(f"Missing required column: {required}")

            # Normalize column names
            rename_mapping = {}
            if col_mapping["sample"] != "Sample":
                rename_mapping[col_mapping["sample"]] = "Sample"
            if col_mapping["pathway"] != "Pathway":
                rename_mapping[col_mapping["pathway"]] = "Pathway"
            if col_mapping["ko"] != "KO":
                rename_mapping[col_mapping["ko"]] = "KO"

            if rename_mapping:
                df = df.rename(columns=rename_mapping)
                logger.debug(f"[UC-4.4] Renamed columns: {rename_mapping}")

            # Filter by selected sample
            filtered_df = df[df["Sample"] == selected_sample].copy()

            if filtered_df.empty:
                logger.warning(
                    f"[UC-4.4] No data found for sample: " f"'{selected_sample}'"
                )
                return _create_error_message(
                    f"No data found for sample '{selected_sample}'. "
                    f"Try selecting a different sample."
                )

            logger.info(
                f"[UC-4.4] Filtered data: {len(filtered_df)} rows for "
                f"sample '{selected_sample}'"
            )

            # Remove NaNs from required columns
            filtered_df = filtered_df.dropna(subset=["Pathway", "KO"])

            if filtered_df.empty:
                logger.warning("[UC-4.4] No valid data after removing NaNs")
                return _create_error_message("No valid data found after data cleaning.")

            # Generate plot using PlotService
            # RadarChartStrategy handles aggregation
            use_case_id = "UC-4.4"

            logger.info(
                f"[UC-4.4] Calling PlotService for {use_case_id} "
                f"with {len(filtered_df)} rows"
            )

            fig = plot_service.generate_plot(use_case_id=use_case_id, data=filtered_df)

            # Update title dynamically
            fig.update_layout(
                title=f"Functional Fingerprint for {selected_sample}", title_x=0.5
            )

            logger.info("[UC-4.4] [OK] Radar chart generated successfully")

            try:
                suggested = sanitize_filename("UC-4.4", "functional_fingerprint", "png")
            except Exception:
                suggested = "functional_fingerprint.png"

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
            logger.error(f"[UC-4.4] Value error: {ve}")
            return _create_error_message(str(ve))
        except Exception as e:
            logger.error(f"[UC-4.4] Rendering error: {e}", exc_info=True)
            return _create_error_message(f"Error generating radar chart: {str(e)}")


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
