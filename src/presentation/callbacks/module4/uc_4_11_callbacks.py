"""
UC-4.11 Callbacks - Global Hierarchical View of Genetic Diversity in HADEG Pathways.

This module implements callback functions for visualizing global hierarchical
genetic diversity through sunburst visualization with database switching capability.

Functions
---------
register_uc_4_11_callbacks
    Register all UC-4.11 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses sunburst chart for hierarchical genetic diversity visualization
- Supports BioRemPP and HADEG databases with toggle switching
- Renders automatically when accordion opens (no dropdown required)
- Hierarchy: root → Compound/Class → Pathway/Name

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


def register_uc_4_11_callbacks(app, plot_service) -> None:
    """
    Register UC-4.11 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 3 callbacks: panel toggle, database button toggle,
      and sunburst chart rendering
    - Supports database switching between BioRemPP and HADEG
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-4-11-collapse", "is_open"),
        Input("uc-4-11-collapse-button", "n_clicks"),
        State("uc-4-11-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_4_11_info_panel(n_clicks, is_open):
        """
        Toggle UC-4.11 informative panel collapse.

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
            f"[UC-4.11] 🔘 Toggle clicked! n_clicks={n_clicks}, is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-4.11] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-4.11] ⊘ No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-4-11-db-biorempp", "outline"),
            Output("uc-4-11-db-hadeg", "outline"),
        ],
        [
            Input("uc-4-11-db-biorempp", "n_clicks"),
            Input("uc-4-11-db-hadeg", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def toggle_uc_4_11_database_buttons(biorempp_clicks, hadeg_clicks):
        """
        Toggle database selection buttons for UC-4.11.

        Parameters
        ----------
        biorempp_clicks : int
            Number of clicks on BioRemPP button.
        hadeg_clicks : int
            Number of clicks on HADEG button.

        Returns
        -------
        tuple of (bool, bool)
            Outline states for (BioRemPP, HADEG).
            False = selected, True = not selected.
        """
        from dash import callback_context

        ctx = callback_context
        if not ctx.triggered:
            return False, True  # BioRemPP selected by default

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "uc-4-11-db-biorempp":
            logger.info("[UC-4.11] Database switched to BioRemPP")
            return False, True  # BioRemPP selected
        elif button_id == "uc-4-11-db-hadeg":
            logger.info("[UC-4.11] Database switched to HADEG")
            return True, False  # HADEG selected

        return False, True  # Default: BioRemPP

    @app.callback(
        Output("uc-4-11-chart-container", "children"),
        [
            Input("uc-4-11-accordion-group", "active_item"),
            Input("uc-4-11-db-biorempp", "outline"),
            Input("uc-4-11-db-hadeg", "outline"),
        ],
        [
            State("merged-result-store", "data"),
            State("uc-4-11-chart-container", "children"),
        ],
        prevent_initial_call=True,
    )
    def render_uc_4_11(
        active_item: Optional[str],
        biorempp_outline: bool,
        hadeg_outline: bool,
        merged_data: Optional[dict],
        current_container: Any,
    ) -> Any:
        """
        Render UC-4.11 sunburst chart showing global genetic diversity hierarchy.

        This callback automatically generates a sunburst visualization when the
        accordion opens, displaying the complete hierarchical structure of
        genetic diversity. Default database is BioRemPP (can be switched to HADEG).

        Rendering Logic:
        - Accordion opens (active_item = "uc-4-11-accordion") → Render chart
        - Database selection changes (outline state) → Re-render with new data
        - Accordion closes (active_item = None) → PreventUpdate

        Data Processing (inline):
        1. Extract data from selected database (BioRemPP or HADEG)
        2. Validate required columns based on database:
           - BioRemPP: 'Compound_Class', 'Compound_Name', 'Gene_Symbol'
           - HADEG: 'Compound', 'Pathway', 'Gene'
        3. Drop rows with NaN in critical columns
        4. GROUP BY [level1, level2] (hierarchy levels)
        5. Aggregate: COUNT(DISTINCT genes) AS 'unique_gene_count'
        6. Add 'root' column = 'All Pathways' for sunburst center
        7. Pass to PlotService with "UC-4.11" identifier
        8. PlotService + SunburstStrategy handle visualization

        PlotService Processing (from uc_4_11_config.yaml):
        - Path hierarchy (BioRemPP): ['root', 'Compound_Class', 'Compound_Name']
        - Path hierarchy (HADEG): ['root', 'Compound', 'Pathway']
        - Values: 'unique_gene_count'
        - Color: Continuous scale based on 'unique_gene_count'
        - Interactivity: Click to zoom into hierarchy branches

        Parameters
        ----------
        active_item : Optional[str]
            Currently active accordion item ID. Chart renders when
            active_item == "uc-4-11-accordion".
        biorempp_outline : bool
            State of BioRemPP button outline (False = selected).
        hadeg_outline : bool
            State of HADEG button outline (False = selected).
        merged_data : Optional[dict]
            Merged data from store with 'biorempp_df' and 'hadeg_df' keys
            containing respective database DataFrames. BioRemPP is used by default.
        current_container : Any
            Current chart container content.

        Returns
        -------
        dcc.Graph or html.Div
            Sunburst chart component showing hierarchical genetic diversity,
            or error message if data validation fails.

        Raises
        ------
        PreventUpdate
            If accordion is not open or no data available.

        Examples
        --------
        >>> # User opens accordion
        >>> # active_item = "uc-4-11-accordion"
        >>> # → Chart renders automatically
        >>>
        >>> # User closes accordion
        >>> # active_item = None
        >>> # → PreventUpdate (no re-render)
        """
        # Determine trigger
        from dash import callback_context

        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        logger.debug(f"[UC-4.11] Triggered by: {trigger_id}")

        # Determine selected database based on button outline state
        # outline=False means selected, outline=True means not selected
        # Default: BioRemPP (outline=False in layout)
        if not biorempp_outline:
            selected_db = "biorempp_df"
            db_name = "BioRemPP"
        elif not hadeg_outline:
            selected_db = "hadeg_df"
            db_name = "HADEG"
        else:
            # Fallback if both somehow have outline=True
            selected_db = "biorempp_df"
            db_name = "BioRemPP"

        logger.info(f"[UC-4.11] Selected database: {db_name}")

        # Check if chart already rendered
        chart_already_rendered = current_container is not None and not isinstance(
            current_container, (str, type(None))
        )

        # Rendering decision logic
        # Render when: accordion opens OR database selection changes
        accordion_opened = (
            trigger_id == "uc-4-11-accordion-group"
            and active_item == "uc-4-11-accordion"
        )
        database_selection_changed = trigger_id in [
            "uc-4-11-db-biorempp",
            "uc-4-11-db-hadeg",
        ]
        should_render = accordion_opened or database_selection_changed

        if not should_render:
            logger.debug("[UC-4.11] Render conditions not met")
            raise PreventUpdate

        # Check data availability
        if not merged_data:
            logger.warning("[UC-4.11] No data available in store")
            return _create_error_message("No data available for visualization")

        try:
            # Extract DataFrame from selected database
            logger.debug(f"[UC-4.11] Received data type: {type(merged_data)}")

            if not isinstance(merged_data, dict) or selected_db not in merged_data:
                logger.error(
                    f"[UC-4.11] Invalid data format: expected dict with "
                    f"'{selected_db}', got {type(merged_data)} with keys "
                    f"{merged_data.keys() if isinstance(merged_data, dict) else 'N/A'}"
                )
                return _create_error_message(
                    f"{db_name} database data not found. "
                    f"Please ensure data is loaded."
                )

            df = pd.DataFrame(merged_data[selected_db])
            logger.info(f"[UC-4.11] Loaded {db_name} data: {df.shape}")

            # Define required columns based on database
            if db_name == "HADEG":
                required_cols = ["Compound", "Pathway", "Gene"]
                level1_col = "Compound"
                level2_col = "Pathway"
                value_col = "Gene"
            else:  # BioRemPP
                required_cols = ["Compound_Class", "Compound_Name", "Gene_Symbol"]
                level1_col = "Compound_Class"
                level2_col = "Compound_Name"
                value_col = "Gene_Symbol"

            # Validate required columns
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                logger.error(
                    f"[UC-4.11] Missing required columns: {missing_cols}. "
                    f"Available columns: {df.columns.tolist()}"
                )
                return _create_error_message(
                    f"Missing required columns for {db_name}: "
                    f"{', '.join(missing_cols)}. "
                    f"Available: {', '.join(df.columns.tolist())}"
                )

            # DATA PROCESSING: Hierarchical aggregation
            # Step 1: Remove NaN values in critical columns
            initial_count = len(df)
            df_clean = df.dropna(subset=required_cols).copy()
            final_count = len(df_clean)

            if final_count < initial_count:
                removed = initial_count - final_count
                logger.info(
                    f"[UC-4.11] Removed {removed} rows with NaN values "
                    f"({final_count} remaining)"
                )

            if df_clean.empty:
                logger.warning("[UC-4.11] No valid data after removing NaN values")
                return _create_error_message(
                    "No valid HADEG data available after cleaning. "
                    "All rows contain missing values in critical columns."
                )

            # Step 2: Group by hierarchy and count unique values
            logger.info(
                f"[UC-4.11] Aggregating: "
                f"GROUP BY [{level1_col}, {level2_col}] → "
                f"COUNT(DISTINCT {value_col})"
            )

            aggregated = (
                df_clean.groupby([level1_col, level2_col])[value_col]
                .nunique()
                .reset_index()
                .rename(columns={value_col: "unique_gene_count"})
            )

            logger.info(
                f"[UC-4.11] Aggregation complete: "
                f"{len(aggregated)} unique ({level1_col}, {level2_col}) "
                f"combinations, "
                f"{aggregated['unique_gene_count'].sum():.0f} total unique values"
            )

            # Step 3: Add root level for sunburst center
            aggregated["root"] = "All Pathways"

            # Rename columns to match SunburstStrategy expectations
            aggregated = aggregated.rename(
                columns={level1_col: "Compound", level2_col: "Pathway"}
            )

            logger.info(
                f"[UC-4.11] Added root level and normalized columns for " f"{db_name}"
            )

            # Log sample of processed data
            logger.debug(
                f"[UC-4.11] Sample data (first 3 rows):\n"
                f"{aggregated.head(3).to_string()}"
            )

            # Generate plot using PlotService
            use_case_id = "UC-4.11"

            logger.info(
                f"[UC-4.11] Calling PlotService for {use_case_id} "
                f"with {len(aggregated)} hierarchical nodes from {db_name}"
            )

            fig = plot_service.generate_plot(use_case_id=use_case_id, data=aggregated)

            logger.info(f"[UC-4.11] [OK] Sunburst plot generated successfully")

            try:
                suggested = sanitize_filename(
                    "UC-4.11", "genetic_diversity_hierarchy", "png"
                )
            except Exception:
                suggested = "genetic_diversity_hierarchy.png"

            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                figure=fig,
                config={
                    "displayModeBar": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "scale": 6,  # High resolution for publication
                    },
                },
                style={"height": "650px"},  # Extra space for sunburst
            )

        except ValueError as ve:
            logger.error(f"[UC-4.11] Value error during processing: {ve}")
            return _create_error_message(str(ve))
        except KeyError as ke:
            logger.error(f"[UC-4.11] Key error (missing column): {ke}")
            return _create_error_message(
                f"Data structure error: {ke}. "
                "Please ensure HADEG data contains required columns."
            )
        except Exception as e:
            logger.error(
                f"[UC-4.11] Unexpected error during rendering: {e}", exc_info=True
            )
            return _create_error_message(f"Error generating sunburst chart: {str(e)}")


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
