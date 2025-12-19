"""
UC-7.5 Callbacks - Interactive Distribution of Toxicity Scores by Endpoint.

This module implements callback functions for visualizing toxicity score
distributions through density plot analysis with overlaid KDE curves across
endpoints within selected toxicity super-categories.

Functions
---------
register_uc_7_5_callbacks
    Register all UC-7.5 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses DensityPlotStrategy for KDE visualization
- ToxCSM database REQUIRED (contains toxicity prediction data)

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


def register_uc_7_5_callbacks(app, plot_service) -> None:
    """
    Register UC-7.5 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle, dropdown initialization, and density plot callbacks
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-7-5-collapse", "is_open"),
        Input("uc-7-5-collapse-button", "n_clicks"),
        State("uc-7-5-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_7_5_info_panel(n_clicks, is_open):
        """
        Toggle UC-7.5 informative panel collapse.

        Parameters
        ----------
        n_clicks : int, optional
            Number of clicks on collapse button.
        is_open : bool
            Current collapse state.

        Returns
        -------
        bool
            New collapse state (toggled).
        """
        logger.info(
            f"[UC-7.5] 🔘 Toggle clicked! " f"n_clicks={n_clicks}, is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-7.5] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-7.5] ⊘ No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-7-5-category-dropdown", "options"),
            Output("uc-7-5-category-dropdown", "value"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-7-5-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_category_dropdown_uc_7_5(
        merged_data: Optional[dict], active_item: Optional[str]
    ) -> Tuple[list, None]:
        """
        Initialize toxicity super-category dropdown with ToxCSM data.

        Parameters
        ----------
        merged_data : dict, optional
            Pre-processed merged data with 'toxcsm_df' key containing
            ToxCSM data with super_category column.
        active_item : str, optional
            Currently active accordion item (triggers re-initialization).

        Returns
        -------
        tuple of (list, None)
            Dropdown options list and default value (None).

        Raises
        ------
        PreventUpdate
            If no data available or ToxCSM data not found.

        Notes
        -----
        - Extracts unique super-category values from pre-processed ToxCSM data
        - ToxCSM data includes: compoundname, endpoint, toxicity_score, super_category
        - Returns empty list if data unavailable
        """
        logger.info(f"[UC-7.5] 🔄 Dropdown init triggered")
        logger.debug(f"[UC-7.5] merged_data type: {type(merged_data)}")
        logger.debug(f"[UC-7.5] active_item: {active_item}")

        # Validate merged_data exists
        if not merged_data:
            logger.warning("[UC-7.5] ⚠️ No data in store, preventing dropdown init")
            return [], None

        # Check if this is initial call with empty/invalid data
        if isinstance(merged_data, dict) and not merged_data:
            logger.warning(
                "[UC-7.5] ⚠️ Empty dict in store, " "preventing dropdown init"
            )
            return [], None

        try:
            # Debug: Log available keys
            logger.debug(f"[UC-7.5] merged_data keys: {list(merged_data.keys())}")

            # Extract ToxCSM DataFrame from store
            if not isinstance(merged_data, dict):
                logger.error(
                    f"[UC-7.5] ❌ Invalid data format: "
                    f"expected dict, got {type(merged_data)}"
                )
                raise PreventUpdate

            if "toxcsm_df" not in merged_data:
                logger.error(
                    f"[UC-7.5] ❌ 'toxcsm_df' key not found. "
                    f"Available keys: {list(merged_data.keys())}"
                )
                raise PreventUpdate

            toxcsm_data = merged_data["toxcsm_df"]
            logger.debug(f"[UC-7.5] toxcsm_df type: {type(toxcsm_data)}")
            data_len = len(toxcsm_data) if toxcsm_data else 0
            logger.debug(f"[UC-7.5] toxcsm_df length: {data_len}")

            # Validate toxcsm_data is not empty
            if not toxcsm_data:
                logger.warning("[UC-7.5] ⚠️ ToxCSM data is empty")
                raise PreventUpdate

            # Convert to DataFrame
            df = pd.DataFrame(toxcsm_data)
            logger.info(f"[UC-7.5] [OK] DataFrame created: shape={df.shape}")
            logger.debug(f"[UC-7.5] Available columns: {df.columns.tolist()}")

            # Debug: Show first row
            if len(df) > 0:
                logger.debug(f"[UC-7.5] Sample row:\n{df.iloc[0].to_dict()}")

            # Validate required column exists
            if "super_category" not in df.columns:
                logger.error(
                    f"[UC-7.5] ❌ 'super_category' column not found. "
                    f"Available columns: {df.columns.tolist()}"
                )
                raise PreventUpdate

            # Extract unique super-categories (data already processed!)
            categories = sorted(df["super_category"].dropna().unique())

            if not categories or len(categories) == 0:
                logger.error("[UC-7.5] ❌ No valid super-categories found")
                raise PreventUpdate

            logger.info(
                f"[UC-7.5] [OK] Found {len(categories)} "
                f"super-categories: {categories}"
            )

            # Create dropdown options
            options = [
                {"label": category, "value": category} for category in categories
            ]

            logger.info(
                f"[UC-7.5] ✅ Dropdown initialized successfully "
                f"with {len(options)} options"
            )

            return options, None

        except PreventUpdate:
            raise
        except Exception as e:
            logger.error(f"[UC-7.5] ❌ Dropdown error: {e}", exc_info=True)
            raise PreventUpdate

    @app.callback(
        Output("uc-7-5-chart-container", "children"),
        Input("uc-7-5-category-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_7_5(
        selected_category: Optional[str], merged_data: Optional[dict]
    ) -> Any:
        """
        Render UC-7.5 density plot for selected super-category.

        Parameters
        ----------
        selected_category : str, optional
            Selected super-category from dropdown (e.g., "Genomic").
        merged_data : dict, optional
            Merged data from store with 'toxcsm_df' key.

        Returns
        -------
        dcc.Graph or html.Div
            Density plot component or error message.

        Raises
        ------
        PreventUpdate
            If no category selected or no data available.

        Notes
        -----
        - Extracts pre-processed ToxCSM data with super_category column
        - Filters by selected super-category
        - Passes filtered data to DensityPlotStrategy via PlotService
        - Generates overlaid KDE curves for toxicity score distributions
        """
        logger.info(f"[UC-7.5] 📊 Render triggered for: {selected_category}")

        # Check dropdown selection
        if not selected_category:
            logger.debug("[UC-7.5] No category selected")
            raise PreventUpdate

        # Check data availability
        if not merged_data:
            logger.warning("[UC-7.5] No data available")
            return _create_error_message("No data available for visualization")

        try:
            # Extract ToxCSM DataFrame from store
            logger.debug(f"[UC-7.5] Received data type: {type(merged_data)}")

            if not isinstance(merged_data, dict) or "toxcsm_df" not in merged_data:
                logger.error(
                    "[UC-7.5] Invalid data format: " "expected dict with 'toxcsm_df'"
                )
                return _create_error_message(
                    "ToxCSM database data not found. "
                    "Please ensure ToxCSM data is loaded."
                )

            # Convert to DataFrame (data already processed!)
            df = pd.DataFrame(merged_data["toxcsm_df"])
            logger.info(f"[UC-7.5] [OK] DataFrame loaded: shape={df.shape}")
            logger.debug(f"[UC-7.5] Available columns: {df.columns.tolist()}")

            # Validate required columns exist
            required_cols = ["super_category", "endpoint", "toxicity_score"]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                logger.error(f"[UC-7.5] Missing required columns: {missing}")
                return _create_error_message(f"Missing required columns: {missing}")

            # Filter by selected super-category (data already processed!)
            category_data = df[df["super_category"] == selected_category].copy()

            if category_data.empty:
                logger.warning(
                    f"[UC-7.5] No data found for " f"category '{selected_category}'"
                )
                return _create_error_message(
                    f"No toxicity data found for " f"category: {selected_category}"
                )

            logger.info(
                f"[UC-7.5] Filtered data for '{selected_category}': "
                f"{len(category_data)} rows, "
                f"{category_data['endpoint'].nunique()} endpoints"
            )
            logger.debug(
                f"[UC-7.5] Endpoints: " f"{sorted(category_data['endpoint'].unique())}"
            )

            # Generate plot using PlotService
            # (DensityPlotStrategy configured in uc_7_5_config.yaml)
            use_case_id = "UC-7.5"

            logger.info(
                f"[UC-7.5] Calling PlotService for {use_case_id} "
                f"with {len(category_data)} rows"
            )

            fig = plot_service.generate_plot(
                use_case_id=use_case_id, data=category_data
            )

            # Update title dynamically with selected category
            fig.update_layout(
                title={
                    "text": (f"Toxicity Score Distribution: {selected_category}"),
                    "x": 0.5,
                    "xanchor": "center",
                }
            )

            logger.info("[UC-7.5] ✅ Plot generated successfully")

            # Prepare a safe basename for exports
            cat_safe = str(selected_category).replace(" ", "_")
            db_basename = f"density_{cat_safe}"
            try:
                suggested = sanitize_filename("UC-7.5", db_basename, "png")
            except Exception:
                suggested = f"{db_basename}.png"

            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                figure=fig,
                config={
                    "displayModeBar": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "scale": 6,
                    },
                },
                style={"height": "850px"},
            )

        except ValueError as ve:
            logger.error(f"[UC-7.5] Value error: {ve}")
            return _create_error_message(str(ve))
        except Exception as e:
            logger.error(f"[UC-7.5] Rendering error: {e}", exc_info=True)
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
