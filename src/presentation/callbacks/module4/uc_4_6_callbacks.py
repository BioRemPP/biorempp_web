"""
UC-4.6 Callbacks - Interactive Analysis of Functional Potential by Chemical Compound.

This module implements callback functions for visualizing functional potential
mapping through interactive compound class selection and bubble chart analysis.

Functions
---------
register_uc_4_6_callbacks
    Register all UC-4.6 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses bubble chart for functional potential mapping visualization
- BioRemPP database REQUIRED (with Compound_Class and Compound_Name columns)

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


def register_uc_4_6_callbacks(app, plot_service) -> None:
    """
    Register UC-4.6 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 3 callbacks: panel toggle, compound class dropdown initialization,
      and bubble chart rendering
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-4-6-collapse", "is_open"),
        Input("uc-4-6-collapse-button", "n_clicks"),
        State("uc-4-6-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_4_6_info_panel(n_clicks, is_open):
        """
        Toggle UC-4.6 informative panel collapse.

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
            f"[UC-4.6] 🔘 Toggle clicked! n_clicks={n_clicks}, is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-4.6] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-4.6] ⊘ No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-4-6-compound-class-dropdown", "options"),
            Output("uc-4-6-compound-class-dropdown", "value"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-4-6-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_compound_class_dropdown_uc_4_6(
        merged_data: Optional[dict], active_item: Optional[str]
    ) -> Tuple[list, None]:
        """
        Initialize compound class dropdown with BioRemPP data.

        This callback populates the dropdown menu with available compound
        classes extracted from processed BioRemPP data, enabling users to
        select specific chemical classes for functional potential mapping.

        Data Processing (inline):
        1. Extract BioRemPP data from store
        2. Validate 'Compound_Class' column exists
        3. Extract unique compound classes
        4. Sort alphabetically
        5. Create dropdown options

        Parameters
        ----------
        merged_data : Optional[dict]
            Pre-processed merged data stored in merged-result-store.
            Expected structure: dict with 'biorempp_df' key.
        active_item : Optional[str]
            Currently active accordion item (triggers re-initialization).

        Returns
        -------
        Tuple[list, None]
            - First element: List of dropdown option dictionaries with
              label/value pairs for compound class selection. Empty list
              if no data available.
            - Second element: Default selection value (None for no
              initial selection).

        Raises
        ------
        PreventUpdate
            If no data available or 'Compound_Class' column not found.
        """
        logger.info(
            f"[UC-4.6] 🔄 Dropdown init triggered, data type: {type(merged_data)}"
        )

        if not merged_data:
            logger.debug("[UC-4.6] No data in store, preventing dropdown init")
            return [], None

        # Check if this is initial call with empty/invalid data
        if isinstance(merged_data, dict) and not merged_data:
            logger.debug("[UC-4.6] Empty dict in store, preventing dropdown init")
            return [], None

        try:
            # Extract BioRemPP DataFrame from store
            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error(
                    f"[UC-4.6] Invalid data format: expected dict with 'biorempp_df', "
                    f"got {type(merged_data)}"
                )
                raise PreventUpdate

            df = pd.DataFrame(merged_data["biorempp_df"])

            # Validate 'Compound_Class' column exists
            compound_class_col = None
            for col_name in [
                "Compound_Class",
                "compound_class",
                "CompoundClass",
                "Class",
            ]:
                if col_name in df.columns:
                    compound_class_col = col_name
                    break

            if compound_class_col is None:
                logger.error(
                    f"[UC-4.6] 'Compound_Class' column not found in BioRemPP data. "
                    f"Available columns: {df.columns.tolist()}"
                )
                raise PreventUpdate

            # DATA PROCESSING: Extract unique compound classes (inline)
            compound_classes = sorted(df[compound_class_col].dropna().unique())

            # Create dropdown options
            options = [
                {"label": compound_class, "value": compound_class}
                for compound_class in compound_classes
            ]

            logger.info(
                f"[UC-4.6] Dropdown initialized with {len(options)} compound classes"
            )

            return options, None

        except Exception as e:
            logger.error(f"[UC-4.6] Dropdown error: {e}")
            raise PreventUpdate

    @app.callback(
        Output("uc-4-6-chart-container", "children"),
        Input("uc-4-6-compound-class-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_4_6(
        selected_compound_class: Optional[str], merged_data: Optional[dict]
    ) -> Any:
        """
        Render UC-4.6 bubble chart based on selected compound class.

        Rendering Logic:
        - Dropdown selection: Render bubble chart for selected compound class
        - No auto-update (single trigger)

        Data Processing (inline):
        1. Extract BioRemPP data from store
        2. Validate required columns: 'Sample', 'Compound_Class', 'Compound_Name', 'KO'
        3. Filter by selected compound class
        4. Pass filtered data to PlotService
        5. PlotService applies YAML config processing:
           - GroupBy ['Sample', 'Compound_Name']
           - Count unique KO (nunique)
           - Create bubble chart (X=Sample, Y=Compound_Name, Size/Color=unique_ko_count)

        Parameters
        ----------
        selected_compound_class : Optional[str]
            Selected compound class from dropdown.
        merged_data : Optional[dict]
            Merged data from store with 'biorempp_df' key.

        Returns
        -------
        dcc.Graph or html.Div
            Bubble chart component or error message.

        Raises
        ------
        PreventUpdate
            If no compound class selected or no data available.
        """
        # Check dropdown selection
        if not selected_compound_class:
            logger.debug("[UC-4.6] No compound class selected")
            raise PreventUpdate

        # Check data availability
        if not merged_data:
            logger.warning("[UC-4.6] No data available")
            return _create_error_message("No data available for visualization")

        try:
            # Extract BioRemPP DataFrame from store
            logger.debug(f"[UC-4.6] Received data type: {type(merged_data)}")

            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error(
                    f"[UC-4.6] Invalid data format: expected dict with 'biorempp_df'"
                )
                return _create_error_message(
                    "BioRemPP database data not found. "
                    "Please ensure BioRemPP data is loaded."
                )

            df = pd.DataFrame(merged_data["biorempp_df"])

            # Validate required columns
            required_cols = {
                "Sample": ["Sample", "sample", "sample_id"],
                "Compound_Class": [
                    "Compound_Class",
                    "compound_class",
                    "CompoundClass",
                    "Class",
                ],
                "Compound_Name": [
                    "Compound_Name",
                    "compound_name",
                    "CompoundName",
                    "Compound",
                ],
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
                        f"[UC-4.6] Required column '{required}' not found. "
                        f"Available: {df.columns.tolist()}"
                    )
                    return _create_error_message(f"Missing required column: {required}")

            # Normalize column names if needed
            if col_mapping["Sample"] != "Sample":
                df = df.rename(columns={col_mapping["Sample"]: "Sample"})
            if col_mapping["Compound_Class"] != "Compound_Class":
                df = df.rename(
                    columns={col_mapping["Compound_Class"]: "Compound_Class"}
                )
            if col_mapping["Compound_Name"] != "Compound_Name":
                df = df.rename(columns={col_mapping["Compound_Name"]: "Compound_Name"})
            if col_mapping["KO"] != "KO":
                df = df.rename(columns={col_mapping["KO"]: "KO"})

            # DATA PROCESSING: Filter by selected compound class
            compound_class_data = df[
                df["Compound_Class"] == selected_compound_class
            ].copy()

            if compound_class_data.empty:
                logger.warning(
                    f"[UC-4.6] No data found for compound class '{selected_compound_class}'"
                )
                return _create_error_message(
                    f"No compound data found for class: {selected_compound_class}"
                )

            logger.info(
                f"[UC-4.6] Filtered data for compound class '{selected_compound_class}': "
                f"{len(compound_class_data)} rows"
            )

            # Remove rows with missing Compound_Name
            compound_class_data = compound_class_data.dropna(subset=["Compound_Name"])

            if compound_class_data.empty:
                logger.warning(
                    f"[UC-4.6] No compound names found for class '{selected_compound_class}'"
                )
                return _create_error_message(
                    f"No compound names found for class: {selected_compound_class}"
                )

            # Generate plot using PlotService
            # (Further processing defined in uc_4_6_config.yaml)
            use_case_id = "UC-4.6"

            logger.info(
                f"[UC-4.6] Calling PlotService for {use_case_id} "
                f"with {len(compound_class_data)} rows"
            )

            fig = plot_service.generate_plot(
                use_case_id=use_case_id, data=compound_class_data
            )

            logger.info(f"[UC-4.6] [OK] Plot generated successfully")

            try:
                suggested = sanitize_filename("UC-4.6", "ko_distribution", "png")
            except Exception:
                suggested = "ko_distribution.png"

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
                style={"height": "750px"},
            )

        except ValueError as ve:
            logger.error(f"[UC-4.6] Value error: {ve}")
            return _create_error_message(str(ve))
        except Exception as e:
            logger.error(f"[UC-4.6] Rendering error: {e}", exc_info=True)
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
