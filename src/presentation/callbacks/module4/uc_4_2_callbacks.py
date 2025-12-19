"""
UC-4.2 Callbacks - Interactive Sample Ranking by Pathway Richness.

This module implements callback functions for visualizing sample ranking based
on pathway richness through interactive pathway selection and vertical bar chart analysis.

Functions
---------
register_uc_4_2_callbacks
    Register all UC-4.2 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses vertical bar chart for sample ranking visualization
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


def register_uc_4_2_callbacks(app, plot_service) -> None:
    """
    Register UC-4.2 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 3 callbacks: panel toggle, pathway dropdown initialization,
      and vertical bar chart rendering
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-4-2-collapse", "is_open"),
        Input("uc-4-2-collapse-button", "n_clicks"),
        State("uc-4-2-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_4_2_info_panel(n_clicks, is_open):
        """
        Toggle UC-4.2 informative panel collapse.

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
            f"[UC-4.2] 🔘 Toggle clicked! n_clicks={n_clicks}, is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-4.2] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-4.2] ⊘ No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-4-2-pathway-dropdown", "options"),
            Output("uc-4-2-pathway-dropdown", "value"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-4-2-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_pathway_dropdown_uc_4_2(
        merged_data: Optional[dict], active_item: Optional[str]
    ) -> Tuple[list, None]:
        """
        Initialize pathway dropdown with KEGG data.

        This callback populates the dropdown menu with available pathways
        extracted from processed KEGG data, enabling users to select
        specific pathways for sample ranking analysis.

        Data Processing (inline):
        1. Extract KEGG data from store
        2. Validate 'Pathway' column exists
        3. Extract unique pathways
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
              label/value pairs for pathway selection. Empty list
              if no data available.
            - Second element: Default selection value (None for no
              initial selection).

        Raises
        ------
        PreventUpdate
            If no data available or 'Pathway' column not found.
        """
        logger.info(
            f"[UC-4.2] 🔄 Dropdown init triggered, data type: {type(merged_data)}"
        )

        if not merged_data:
            logger.debug("[UC-4.2] No data in store, preventing dropdown init")
            return [], None

        # Check if this is initial call with empty/invalid data
        if isinstance(merged_data, dict) and not merged_data:
            logger.debug("[UC-4.2] Empty dict in store, preventing dropdown init")
            return [], None

        try:
            # Extract KEGG DataFrame from store
            if not isinstance(merged_data, dict) or "kegg_df" not in merged_data:
                logger.error(
                    f"[UC-4.2] Invalid data format: expected dict with 'kegg_df', "
                    f"got {type(merged_data)}"
                )
                raise PreventUpdate

            df = pd.DataFrame(merged_data["kegg_df"])

            # Validate 'Pathway' column exists
            pathway_col = None
            for col_name in ["Pathway", "pathname", "pathway_name"]:
                if col_name in df.columns:
                    pathway_col = col_name
                    break

            if pathway_col is None:
                logger.error(
                    f"[UC-4.2] 'Pathway' column not found in KEGG data. "
                    f"Available columns: {df.columns.tolist()}"
                )
                raise PreventUpdate

            # DATA PROCESSING: Extract unique pathways (inline)
            pathways = sorted(df[pathway_col].dropna().unique())

            # Create dropdown options
            options = [{"label": pathway, "value": pathway} for pathway in pathways]

            logger.info(f"[UC-4.2] Dropdown initialized with {len(options)} pathways")

            return options, None

        except Exception as e:
            logger.error(f"[UC-4.2] Dropdown error: {e}")
            raise PreventUpdate

    @app.callback(
        Output("uc-4-2-chart-container", "children"),
        Input("uc-4-2-pathway-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_4_2(
        selected_pathway: Optional[str], merged_data: Optional[dict]
    ) -> Any:
        """
        Render UC-4.2 vertical bar chart based on selected pathway.

        Rendering Logic:
        - Dropdown selection: Render chart for selected pathway
        - No auto-update (single trigger)

        Data Processing (inline):
        1. Extract KEGG data from store
        2. Validate required columns: 'Sample', 'Pathway', 'KO'
        3. Filter by selected pathway
        4. Pass filtered data to PlotService
        5. PlotService applies YAML config processing:
           - GroupBy 'Sample'
           - Count unique KO (nunique)
           - Sort by count (descending for vertical bars)

        Parameters
        ----------
        selected_pathway : Optional[str]
            Selected pathway from dropdown.
        merged_data : Optional[dict]
            Merged data from store with 'kegg_df' key.

        Returns
        -------
        dcc.Graph or html.Div
            Vertical bar chart component or error message.

        Raises
        ------
        PreventUpdate
            If no pathway selected or no data available.
        """
        # Check dropdown selection
        if not selected_pathway:
            logger.debug("[UC-4.2] No pathway selected")
            raise PreventUpdate

        # Check data availability
        if not merged_data:
            logger.warning("[UC-4.2] No data available")
            return _create_error_message("No data available for visualization")

        try:
            # Extract KEGG DataFrame from store
            logger.debug(f"[UC-4.2] Received data type: {type(merged_data)}")

            if not isinstance(merged_data, dict) or "kegg_df" not in merged_data:
                logger.error(
                    f"[UC-4.2] Invalid data format: expected dict with 'kegg_df'"
                )
                return _create_error_message(
                    "KEGG database data not found. "
                    "Please ensure KEGG data is loaded."
                )

            df = pd.DataFrame(merged_data["kegg_df"])

            # Validate required columns
            required_cols = {
                "Sample": ["Sample", "sample", "sample_id"],
                "Pathway": ["Pathway", "pathname", "pathway_name"],
                "KO": ["KO", "ko", "ko_id"],
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
                        f"[UC-4.2] Required column '{required}' not found. "
                        f"Available: {df.columns.tolist()}"
                    )
                    return _create_error_message(f"Missing required column: {required}")

            # Normalize column names if needed
            if col_mapping["Sample"] != "Sample":
                df = df.rename(columns={col_mapping["Sample"]: "Sample"})
            if col_mapping["Pathway"] != "Pathway":
                df = df.rename(columns={col_mapping["Pathway"]: "Pathway"})
            if col_mapping["KO"] != "KO":
                df = df.rename(columns={col_mapping["KO"]: "KO"})

            # DATA PROCESSING: Filter by selected pathway
            pathway_data = df[df["Pathway"] == selected_pathway].copy()

            if pathway_data.empty:
                logger.warning(
                    f"[UC-4.2] No data found for pathway '{selected_pathway}'"
                )
                return _create_error_message(
                    f"No sample data found for pathway: {selected_pathway}"
                )

            logger.info(
                f"[UC-4.2] Filtered data for pathway '{selected_pathway}': "
                f"{len(pathway_data)} rows"
            )

            # Generate plot using PlotService
            # (Further processing defined in uc_4_2_config.yaml)
            use_case_id = "UC-4.2"

            logger.info(
                f"[UC-4.2] Calling PlotService for {use_case_id} "
                f"with {len(pathway_data)} rows"
            )

            fig = plot_service.generate_plot(use_case_id=use_case_id, data=pathway_data)

            logger.info(f"[UC-4.2] [OK] Plot generated successfully")

            try:
                suggested = sanitize_filename("UC-4.2", "pathway_distribution", "png")
            except Exception:
                suggested = "pathway_distribution.png"

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
            logger.error(f"[UC-4.2] Value error: {ve}")
            return _create_error_message(str(ve))
        except Exception as e:
            logger.error(f"[UC-4.2] Rendering error: {e}", exc_info=True)
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
