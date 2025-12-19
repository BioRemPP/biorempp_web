"""
UC-2.3 Callbacks - Ranking of Compounds by Sample Diversity per Chemical Class.

This module implements callback functions for ranking compounds by sample
diversity within selected chemical classes using dropdown selection.

Functions
---------
register_uc_2_3_callbacks
    Register all UC-2.3 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Dropdown-driven rendering (no auto-update)
- BioRemPP database required for compound class data

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


def register_uc_2_3_callbacks(app, plot_service) -> None:
    """
    Register UC-2.3 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle, dropdown initialization, and chart rendering callbacks
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-2-3-collapse", "is_open"),
        Input("uc-2-3-collapse-button", "n_clicks"),
        State("uc-2-3-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_2_3_info_panel(n_clicks, is_open):
        """Toggle UC-2.3 informative panel collapse."""
        logger.info(
            f"[UC-2.3] 🔘 Toggle clicked! n_clicks={n_clicks}, is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-2.3] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-2.3] ⊘ No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-2-3-class-dropdown", "options"),
            Output("uc-2-3-class-dropdown", "value"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-2-3-accordion", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_compound_class_dropdown(
        merged_data: Optional[list], active_item: Optional[str]
    ) -> Tuple[list, None]:
        """
        Initialize compound class dropdown with BioRemPP data.

        Parameters
        ----------
        merged_data : list, optional
            Pre-processed BioRemPP data from store.
        active_item : str, optional
            Currently active accordion item.

        Returns
        -------
        tuple
            (dropdown_options, default_value)

        Raises
        ------
        PreventUpdate
            If no data available or compound class column not found.

        Notes
        -----
        - Extracts unique compound classes from BioRemPP DataFrame
        - Returns sorted list of options with no initial selection
        """
        logger.info(
            f"[UC-2.3] 🔄 Dropdown init triggered, data type: {type(merged_data)}"
        )
        if not merged_data:
            logger.debug("[UC-2.3] No data in store, preventing dropdown init")
            return [], None

        # Check if this is initial call with empty/invalid data
        if isinstance(merged_data, dict) and not merged_data:
            logger.debug("[UC-2.3] Empty dict in store, preventing dropdown init")
            return [], None

        try:
            # Extract DataFrame from store
            if isinstance(merged_data, dict) and "biorempp_df" in merged_data:
                df = pd.DataFrame(merged_data["biorempp_df"])
            elif isinstance(merged_data, list):
                df = pd.DataFrame(merged_data)
            else:
                logger.error(f"UC-2.3: Invalid data format {type(merged_data)}")
                raise ValueError(
                    f"Invalid data format: expected dict or list, "
                    f"got {type(merged_data)}"
                )

            # Validate column (try both original and processed names)
            class_col = None
            for col_name in ["Compound_Class", "compoundclass"]:
                if col_name in df.columns:
                    class_col = col_name
                    break

            if class_col is None:
                logger.error(
                    f"UC-2.3: Compound class column not found in {df.columns.tolist()}"
                )
                raise PreventUpdate

            # DATA PROCESSING: Extract unique compound classes (inline logic)
            compound_classes = sorted(df[class_col].dropna().unique())

            # Create dropdown options
            options = [{"label": cls, "value": cls} for cls in compound_classes]

            logger.info(f"UC-2.3: Dropdown initialized with {len(options)} classes")

            return options, None

        except Exception as e:
            logger.error(f"UC-2.3 dropdown error: {e}")
            raise PreventUpdate

    @app.callback(
        Output("uc-2-3-chart-container", "children"),
        Input("uc-2-3-class-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_2_3(
        selected_class: Optional[str], merged_data: Optional[list]
    ) -> Any:
        """
        Render UC-2.3 bar chart based on selected compound class.

        Parameters
        ----------
        selected_class : str, optional
            Selected compound class from dropdown.
        merged_data : list, optional
            Merged data from store.

        Returns
        -------
        dcc.Graph or html.Div
            Chart component or error message.

        Raises
        ------
        PreventUpdate
            If no class selected or no data available.

        Notes
        -----
        - Filters data by selected compound class
        - Counts unique samples per compound
        - Generates ranking chart via PlotService
        """
        # Check dropdown selection
        if not selected_class:
            logger.debug("UC-2.3: No compound class selected")
            raise PreventUpdate

        # Check data availability
        if not merged_data:
            logger.warning("UC-2.3: No data available")
            return _create_error_message("No data available for visualization")

        try:
            # Extract DataFrame from store (ONLY biorempp_df)
            logger.debug(f"UC-2.3: Received data type: {type(merged_data)}")

            if isinstance(merged_data, dict) and "biorempp_df" in merged_data:
                df = pd.DataFrame(merged_data["biorempp_df"])
                logger.info(
                    f"UC-2.3: Using biorempp_df from store, " f"shape: {df.shape}"
                )
                logger.debug(f"UC-2.3: Available columns: {df.columns.tolist()}")
            elif isinstance(merged_data, list):
                df = pd.DataFrame(merged_data)
                logger.info(f"UC-2.3: Using direct data format, shape: {df.shape}")
            else:
                raise ValueError(
                    f"Invalid data format: expected dict or list, "
                    f"got {type(merged_data)}"
                )

            # Map column names (support both original and processed)
            col_map = {}

            # Compound class column
            for col_name in ["Compound_Class", "compoundclass"]:
                if col_name in df.columns:
                    col_map["compoundclass"] = col_name
                    break

            # Compound name column
            for col_name in ["Compound_Name", "compoundname"]:
                if col_name in df.columns:
                    col_map["compoundname"] = col_name
                    break

            # Sample column (lowercase or capitalized)
            for col_name in ["Sample", "sample"]:
                if col_name in df.columns:
                    col_map["sample"] = col_name
                    break

            # Validate all required columns found
            required_cols = ["compoundclass", "compoundname", "sample"]
            missing = [col for col in required_cols if col not in col_map]

            if missing:
                raise ValueError(
                    f"Required columns not found: {missing}. "
                    f"Available: {df.columns.tolist()}"
                )

            logger.info(f"UC-2.3: Column mapping: {col_map}")

            logger.info(
                f"UC-2.3: Data validation successful. "
                f"Total rows before filtering: {len(df)}"
            )

            # Extract actual column names
            class_col = col_map["compoundclass"]
            name_col = col_map["compoundname"]
            sample_col = col_map["sample"]

            logger.debug(
                f"UC-2.3: Using columns - class: '{class_col}', "
                f"name: '{name_col}', sample: '{sample_col}'"
            )

            # DATA PROCESSING: Filter by compound class (inline logic)
            filtered_df = df[df[class_col] == selected_class].copy()

            logger.info(
                f"UC-2.3: Filtered {len(filtered_df)} rows for class "
                f"'{selected_class}' (from {len(df)} total rows)"
            )

            if filtered_df.empty:
                logger.warning(
                    f"UC-2.3: No compounds found for class '{selected_class}'"
                )
                return _create_error_message(
                    f"No compounds found for class '{selected_class}'",
                    icon="fas fa-info-circle",
                )

            # Remove rows with missing values in essential columns
            filtered_df = filtered_df.dropna(subset=[sample_col, class_col, name_col])
            logger.debug(f"UC-2.3: After dropna, {len(filtered_df)} rows remaining")

            # DATA PROCESSING: Calculate compound-sample ranking (inline)
            compound_ranking = (
                filtered_df.groupby(name_col)[sample_col]
                .nunique()
                .reset_index(name="sample_count")
                .rename(columns={name_col: "compound"})
                .sort_values("sample_count", ascending=False)
            )

            logger.info(
                f"UC-2.3: Ranking generated - " f"{len(compound_ranking)} compounds"
            )

            if compound_ranking.empty:
                return _create_error_message(
                    f"No valid data for class '{selected_class}'",
                    icon="fas fa-info-circle",
                )

            # Build filters for plot service
            filters = {
                "uc-2-3-class-dropdown": selected_class,
                "selected_database": "biorempp_df",
            }

            # Generate plot using PlotService
            fig = plot_service.generate_plot(
                use_case_id="UC-2.3",
                data=compound_ranking,
                filters=filters,
                force_refresh=False,
            )

            logger.info(
                f"UC-2.3: Chart generated successfully for " f"class '{selected_class}'"
            )

            try:
                suggested = sanitize_filename(
                    "UC-2.3", "compound_sample_ranking", "png"
                )
                base_filename = os.path.splitext(suggested)[0]
            except Exception:
                base_filename = "uc_2_3_compound_sample_ranking"

            return dcc.Graph(
                figure=fig,
                id="uc-2-3-bar-chart",
                config={
                    "displayModeBar": True,
                    "responsive": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 800,
                        "width": 1200,
                        "scale": 2,
                    },
                },
                style={"height": "600px"},
            )

        except ValueError as e:
            logger.error(f"UC-2.3 validation error: {e}", exc_info=True)
            return _create_error_message(f"Data validation failed: {str(e)}")

        except Exception as e:
            logger.error(f"UC-2.3 error: {e}", exc_info=True)
            return _create_error_message(f"Error generating visualization: {str(e)}")


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
