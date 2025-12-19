"""
UC-7.3 Callbacks - Mapping of Genetic Response to High-Priority Threats.

This module implements callback functions for visualizing genetic response
to high-priority toxicological threats through heatmap analysis using
cross-database integration (BioRemPP + ToxCSM).

Functions
---------
register_uc_7_3_callbacks
    Register all UC-7.3 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses HeatmapStrategy for genetic toolkit diversity visualization
- Requires BOTH ToxCSM and BioRemPP databases (cross-database analysis)

Version: 1.0.0
"""

import logging
import os
from typing import Any, Dict, Optional, Tuple

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)
logger.propagate = False


def register_uc_7_3_callbacks(app, plot_service) -> None:
    """
    Register all UC-7.3 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle, dropdown initialization, and heatmap callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-7.3] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-7-3-collapse", "is_open"),
        Input("uc-7-3-collapse-button", "n_clicks"),
        State("uc-7-3-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_7_3_info_panel(n_clicks, is_open):
        """Toggle UC-7.3 informative panel collapse state."""
        if n_clicks:
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Initialize Dropdown
    # ========================================
    @app.callback(
        [
            Output("uc-7-3-category-dropdown", "options"),
            Output("uc-7-3-category-dropdown", "value"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-7-3-accordion", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_threat_category_dropdown(
        merged_data: Optional[Dict[str, Any]], active_item: Optional[str]
    ) -> Tuple[list, None]:
        """
        Initialize threat category dropdown with ToxCSM data.

        Parameters
        ----------
        merged_data : dict, optional
            Dictionary containing merged result data with 'toxcsm_df' key.
        active_item : str, optional
            Active accordion item ID.

        Returns
        -------
        tuple of (list, None)
            Dropdown options list and default value (None).

        Notes
        -----
        - Extracts unique 'super_category' values from ToxCSM dataset
        - Returns empty list if ToxCSM data unavailable
        """
        logger.info(f"[UC-7.3] 🔄 Dropdown init triggered")

        if not merged_data:
            logger.debug("[UC-7.3] No data in store")
            return [], None

        if not isinstance(merged_data, dict):
            logger.error(f"[UC-7.3] Invalid data format: {type(merged_data)}")
            raise PreventUpdate

        toxcsm_data = merged_data.get("toxcsm_df")
        if not toxcsm_data:
            logger.debug("[UC-7.3] No ToxCSM data found")
            return [], None

        try:
            df_tox = pd.DataFrame(toxcsm_data)

            # Validate super_category column
            cat_col = "super_category"
            if cat_col not in df_tox.columns:
                logger.warning(f"[UC-7.3] '{cat_col}' column not found in ToxCSM data")
                # Fallback: try to infer or use hardcoded list if data structure is different
                # For now, return empty to avoid errors
                return [], None

            # Extract unique categories
            categories = sorted(df_tox[cat_col].dropna().unique())

            options = [{"label": cat, "value": cat} for cat in categories]

            logger.info(f"[UC-7.3] Initialized dropdown with {len(options)} categories")
            return options, None

        except Exception as e:
            logger.error(f"[UC-7.3] Dropdown init error: {e}")
            raise PreventUpdate

    # ========================================
    # Callback 3: Render Heatmap
    # ========================================
    @app.callback(
        Output("uc-7-3-chart", "children"),
        Input("uc-7-3-category-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_7_3(
        selected_category: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-7.3 heatmap when threat category is selected.

        Parameters
        ----------
        selected_category : str, optional
            Selected toxicological super-category from dropdown.
        merged_data : dict, optional
            Dictionary containing 'toxcsm_df' and 'biorempp_df' keys.

        Returns
        -------
        html.Div
            Container with chart or error message.

        Notes
        -----
        - Filters ToxCSM for high-risk compounds in selected category
        - Filters BioRemPP for genetic interactions with those compounds
        - Aggregates unique genes per sample-compound pair
        - Passes prepared data to HeatmapStrategy via PlotService
        - Generates heatmap showing genetic toolkit diversity
        """
        logger.debug(
            f"[UC-7.3] Render callback triggered. Category: {selected_category}"
        )

        if not selected_category:
            raise PreventUpdate

        if not merged_data:
            return _create_error_message(
                "No data available. Please upload and process data first.",
                "fas fa-exclamation-triangle",
            )

        try:
            # Extract DataFrames
            toxcsm_data = merged_data.get("toxcsm_df")
            biorempp_data = merged_data.get("biorempp_df")

            if not toxcsm_data:
                return _create_error_message(
                    "ToxCSM data missing. Required for threat analysis.",
                    "fas fa-database",
                )

            if not biorempp_data:
                return _create_error_message(
                    "BioRemPP data missing. Required for genetic analysis.",
                    "fas fa-database",
                )

            df_tox = pd.DataFrame(toxcsm_data)
            df_bio = pd.DataFrame(biorempp_data)

            # 1. Filter ToxCSM for selected category
            if "super_category" not in df_tox.columns:
                return _create_error_message(
                    "Column 'super_category' not found in ToxCSM data.",
                    "fas fa-exclamation-circle",
                )

            category_compounds = df_tox[df_tox["super_category"] == selected_category]

            if category_compounds.empty:
                return _create_error_message(
                    f"No compounds found for category '{selected_category}'.",
                    "fas fa-search",
                )

            # 2. Identify High Risk Compounds
            # Check for label column or use score threshold
            label_cols = [
                c
                for c in category_compounds.columns
                if "label" in c.lower() or "class" in c.lower()
            ]

            if label_cols:
                label_col = label_cols[0]
                high_risk = category_compounds[
                    category_compounds[label_col]
                    .astype(str)
                    .str.contains("High", case=False)
                ]
                high_risk_compounds = high_risk["compoundname"].unique()
            else:
                # Fallback to score > 0.7
                logger.info(
                    "[UC-7.3] No label column found, using score > 0.7 threshold"
                )
                high_risk = category_compounds[
                    pd.to_numeric(category_compounds["toxicity_score"], errors="coerce")
                    > 0.7
                ]
                high_risk_compounds = high_risk["compoundname"].unique()

            if len(high_risk_compounds) == 0:
                return _create_error_message(
                    f"No high-toxicity compounds found for '{selected_category}'.",
                    "fas fa-check-circle",
                )

            # 3. Filter BioRemPP Data
            # Normalize compound column name
            bio_compound_col = "Compound_Name"
            if bio_compound_col not in df_bio.columns:
                for alt in ["compoundname", "CompoundName", "compound"]:
                    if alt in df_bio.columns:
                        bio_compound_col = alt
                        break

            if bio_compound_col not in df_bio.columns:
                return _create_error_message(
                    "Compound Name column not found in BioRemPP data.",
                    "fas fa-exclamation-triangle",
                )

            # Filter for interactions with high-risk compounds
            df_response = df_bio[
                df_bio[bio_compound_col].isin(high_risk_compounds)
            ].copy()

            if df_response.empty:
                return _create_error_message(
                    f"No samples found interacting with high-risk compounds in '{selected_category}'.",
                    "fas fa-inbox",
                )

            # 4. Prepare data for PlotService
            # Map columns to expected names: 'sample', 'compoundname', 'genesymbol'
            gene_col = "Gene_Symbol"
            if gene_col not in df_response.columns:
                if "genesymbol" in df_response.columns:
                    gene_col = "genesymbol"
                elif "Gene" in df_response.columns:
                    gene_col = "Gene"

            sample_col = "Sample"
            if sample_col not in df_response.columns:
                if "sample" in df_response.columns:
                    sample_col = "sample"

            df_response = df_response.rename(
                columns={
                    sample_col: "sample",
                    bio_compound_col: "compoundname",
                    gene_col: "genesymbol",
                }
            )

            # 5. Generate Plot
            fig = plot_service.generate_plot(
                use_case_id="UC-7.3",
                data=df_response,
                filters={"category": selected_category},
                force_refresh=False,
            )

            # Prepare safe basename for selected category (replace spaces)
            cat_safe = str(selected_category).replace(" ", "_")
            db_basename = f"heatmap_{cat_safe}"

            try:
                suggested = sanitize_filename("UC-7.3", db_basename, "png")
            except Exception:
                suggested = f"{db_basename}.png"

            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                id="uc-7-3-graph",
                figure=fig,
                config={
                    "displayModeBar": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 800,
                        "width": 1200,
                        "scale": 6,
                    },
                },
                style={"height": "800px"},
            )

        except Exception as e:
            logger.error(f"[UC-7.3] Error: {str(e)}", exc_info=True)
            return _create_error_message(f"An error occurred: {str(e)}", "fas fa-bug")


def _create_error_message(
    message: str, icon: str = "fas fa-exclamation-circle"
) -> html.Div:
    """
    Create error message component.

    Parameters
    ----------
    message : str
        Error message text to display.
    icon : str, optional
        Font Awesome icon class for the alert icon.
        Default: "fas fa-exclamation-circle"

    Returns
    -------
    html.Div
        Styled alert component with icon and message.
    """
    return html.Div(
        [
            html.I(className=f"{icon} me-2 text-danger"),
            html.Span(message, className="text-danger"),
        ],
        className="alert alert-danger mt-3",
        role="alert",
    )
