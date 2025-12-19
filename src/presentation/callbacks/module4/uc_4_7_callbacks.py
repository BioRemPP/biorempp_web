"""
UC-4.7 Callbacks - Interactive Gene-Compound Association Explorer.

This module implements callback functions for exploring gene-compound associations
through flexible dual-dropdown filtering and scatter plot visualization.

Functions
---------
register_uc_4_7_callbacks
    Register all UC-4.7 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses scatter plot for gene-compound association exploration
- BioRemPP database REQUIRED
- Supports flexible filtering: compound only, gene only, or both

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


def register_uc_4_7_callbacks(app, plot_service) -> None:
    """
    Register UC-4.7 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 3 callbacks: panel toggle, dual-dropdown initialization,
      and conditional scatter plot rendering
    - Refer to official documentation for filtering logic details
    """

    @app.callback(
        Output("uc-4-7-collapse", "is_open"),
        Input("uc-4-7-collapse-button", "n_clicks"),
        State("uc-4-7-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_4_7_info_panel(n_clicks, is_open):
        """
        Toggle UC-4.7 informative panel collapse.

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
            f"[UC-4.7] 🔘 Toggle clicked! n_clicks={n_clicks}, " f"is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-4.7] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-4.7] ⊘ No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-4-7-compound-dropdown", "options"),
            Output("uc-4-7-gene-dropdown", "options"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-4-7-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_uc_4_7_dropdowns(
        merged_data: Optional[dict], active_item: Optional[str]
    ) -> Tuple[list, list]:
        """
        Initialize both dropdowns (compound and gene) with BioRemPP data.

        This callback populates both dropdown menus with available compounds
        and genes extracted from processed BioRemPP data, enabling users to
        explore gene-compound associations from multiple perspectives.

        Data Processing (inline):
        1. Extract BioRemPP data from store
        2. Validate 'compoundname' and 'genesymbol' columns exist
        3. Extract unique compounds and genes
        4. Sort alphabetically
        5. Create dropdown options for both

        Parameters
        ----------
        merged_data : Optional[dict]
            Pre-processed merged data stored in merged-result-store.
            Expected structure: dict with 'biorempp_df' key.
        active_item : Optional[str]
            Currently active accordion item (triggers re-initialization).

        Returns
        -------
        Tuple[list, list]
            - First element: List of compound dropdown options
            - Second element: List of gene dropdown options
            Both are empty lists if no data available.

        Raises
        ------
        PreventUpdate
            If no data available or required columns not found.
        """
        logger.info(
            f"[UC-4.7] 🔄 Dropdowns init triggered, data type: {type(merged_data)}"
        )

        if not merged_data:
            logger.debug("[UC-4.7] No data in store, preventing dropdowns init")
            return [], []

        # Check if this is initial call with empty/invalid data
        if isinstance(merged_data, dict) and not merged_data:
            logger.debug("[UC-4.7] Empty dict in store, preventing dropdowns init")
            return [], []

        try:
            # Extract BioRemPP DataFrame from store
            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error(
                    f"[UC-4.7] Invalid data format: expected dict with 'biorempp_df', "
                    f"got {type(merged_data)}"
                )
                raise PreventUpdate

            df = pd.DataFrame(merged_data["biorempp_df"])

            # Validate required columns
            required_cols = {
                "compoundname": [
                    "compoundname",
                    "Compound_Name",
                    "CompoundName",
                    "compound",
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
                        f"[UC-4.7] Required column '{required}' not found in BioRemPP data. "
                        f"Available columns: {df.columns.tolist()}"
                    )
                    raise PreventUpdate

            # Extract unique values
            compounds = sorted(df[col_mapping["compoundname"]].dropna().unique())
            genes = sorted(df[col_mapping["genesymbol"]].dropna().unique())

            # Create dropdown options
            compound_options = [
                {"label": compound, "value": compound} for compound in compounds
            ]

            gene_options = [{"label": gene, "value": gene} for gene in genes]

            logger.info(
                f"[UC-4.7] Dropdowns initialized: "
                f"{len(compound_options)} compounds, {len(gene_options)} genes"
            )

            return compound_options, gene_options

        except Exception as e:
            logger.error(f"[UC-4.7] Dropdowns error: {e}")
            raise PreventUpdate

    @app.callback(
        Output("uc-4-7-chart-container", "children"),
        [
            Input("uc-4-7-compound-dropdown", "value"),
            Input("uc-4-7-gene-dropdown", "value"),
        ],
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_4_7(
        selected_compound: Optional[str],
        selected_gene: Optional[str],
        merged_data: Optional[dict],
    ) -> Any:
        """
        Render UC-4.7 scatter plot with conditional filtering.

        Rendering Logic:
        - No selection: Show message "Please select at least one filter"
        - Compound only: Filter data by compound, show all associated genes
        - Gene only: Filter data by gene, show all associated compounds
        - Both: Filter by both, show specific interaction

        Data Processing (inline):
        1. Extract BioRemPP data from store
        2. Validate required columns
        3. Apply conditional filtering based on dropdown selections
        4. Pass filtered data to PlotService (no aggregation in config)
        5. PlotService creates simple scatter plot (X=genesymbol, Y=compoundname)

        Parameters
        ----------
        selected_compound : Optional[str]
            Selected compound from dropdown (None if not selected).
        selected_gene : Optional[str]
            Selected gene from dropdown (None if not selected).
        merged_data : Optional[dict]
            Merged data from store with 'biorempp_df' key.

        Returns
        -------
        dcc.Graph or html.Div
            Scatter chart component or informative/error message.

        Raises
        ------
        PreventUpdate
            If no data available.
        """
        # Check if at least one filter is selected
        if not selected_compound and not selected_gene:
            logger.debug("[UC-4.7] No filter selected, showing informative message")
            return html.Div(
                [
                    html.I(className="fas fa-filter me-2"),
                    "Please select a compound and/or a gene from the dropdown menus above to explore associations.",
                ],
                className="alert alert-info mt-3",
            )

        # Check data availability
        if not merged_data:
            logger.warning("[UC-4.7] No data available")
            return _create_error_message("No data available for visualization")

        try:
            # Extract BioRemPP DataFrame from store
            logger.debug(f"[UC-4.7] Received data type: {type(merged_data)}")

            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error(
                    f"[UC-4.7] Invalid data format: expected dict with 'biorempp_df'"
                )
                return _create_error_message(
                    "BioRemPP database data not found. "
                    "Please ensure BioRemPP data is loaded."
                )

            df = pd.DataFrame(merged_data["biorempp_df"])

            # Validate required columns
            required_cols = {
                "sample": ["sample", "Sample", "sample_id"],
                "compoundname": [
                    "compoundname",
                    "Compound_Name",
                    "CompoundName",
                    "compound",
                ],
                "genesymbol": [
                    "genesymbol",
                    "GeneSymbol",
                    "gene_symbol",
                    "Gene_Symbol",
                ],
                "ko": ["ko", "KO", "ko_id"],
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
                        f"[UC-4.7] Required column '{required}' not found. "
                        f"Available: {df.columns.tolist()}"
                    )
                    return _create_error_message(f"Missing required column: {required}")

            # Normalize column names
            if col_mapping["sample"] != "sample":
                df = df.rename(columns={col_mapping["sample"]: "sample"})
            if col_mapping["compoundname"] != "compoundname":
                df = df.rename(columns={col_mapping["compoundname"]: "compoundname"})
            if col_mapping["genesymbol"] != "genesymbol":
                df = df.rename(columns={col_mapping["genesymbol"]: "genesymbol"})
            if col_mapping["ko"] != "ko":
                df = df.rename(columns={col_mapping["ko"]: "ko"})

            # CONDITIONAL FILTERING LOGIC
            filtered_df = df.copy()

            # Build dynamic title based on current filters
            title_parts = []

            if selected_compound:
                filtered_df = filtered_df[
                    filtered_df["compoundname"] == selected_compound
                ]
                title_parts.append(f"Compound: <b>{selected_compound}</b>")

            if selected_gene:
                filtered_df = filtered_df[filtered_df["genesymbol"] == selected_gene]
                title_parts.append(f"Gene: <b>{selected_gene}</b>")

            plot_title = (
                "Gene-Compound Associations for " + " & ".join(title_parts)
                if title_parts
                else "Gene-Compound Associations"
            )

            # Check if filtered data is empty
            if filtered_df.empty:
                filter_desc = []
                if selected_compound:
                    filter_desc.append(f"compound '{selected_compound}'")
                if selected_gene:
                    filter_desc.append(f"gene '{selected_gene}'")

                logger.warning(
                    f"[UC-4.7] No data found for {' and '.join(filter_desc)}"
                )
                return _create_error_message(
                    f"No associations found for {' and '.join(filter_desc)}. "
                    f"Try a different combination."
                )

            logger.info(
                f"[UC-4.7] Filtered data: {len(filtered_df)} rows "
                f"(Compound={selected_compound}, Gene={selected_gene})"
            )

            # Remove NaNs from required columns
            filtered_df = filtered_df.dropna(
                subset=["sample", "compoundname", "genesymbol", "ko"]
            )

            if filtered_df.empty:
                logger.warning(f"[UC-4.7] No valid data after removing NaNs")
                return _create_error_message(
                    "No valid associations found after data cleaning."
                )

            # Generate plot using PlotService
            # (No processing in config - raw scatter plot)
            use_case_id = "UC-4.7"

            logger.info(
                f"[UC-4.7] Calling PlotService for {use_case_id} "
                f"with {len(filtered_df)} rows"
            )

            fig = plot_service.generate_plot(use_case_id=use_case_id, data=filtered_df)

            # Update title dynamically
            fig.update_layout(title=plot_title, title_x=0.5)

            logger.info(f"[UC-4.7] [OK] Plot generated successfully")

            try:
                suggested = sanitize_filename("UC-4.7", "pathway_similarity", "png")
            except Exception:
                suggested = "pathway_similarity.png"

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
                style={"height": "600px"},
            )

        except ValueError as ve:
            logger.error(f"[UC-4.7] Value error: {ve}")
            return _create_error_message(str(ve))
        except Exception as e:
            logger.error(f"[UC-4.7] Rendering error: {e}", exc_info=True)
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
