"""
UC-7.7 Callbacks - Sample Risk Mitigation Depth Profile by Genetic Investment.

This module implements callback functions for visualizing sample risk
mitigation depth through treemap analysis using cross-database integration
(BioRemPP + ToxCSM).

Functions
---------
register_uc_7_7_callbacks
    Register all UC-7.7 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses TreemapStrategy for hierarchical genetic investment visualization
- Requires BOTH BioRemPP and ToxCSM databases (cross-database analysis)

Version: 1.0.0
"""

import logging
import os
from typing import Any, Dict, Optional

import pandas as pd
import plotly.express as px
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)


def register_uc_7_7_callbacks(app, plot_service) -> None:
    """
    Register all UC-7.7 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and treemap rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-7.7] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-7-7-collapse", "is_open"),
        Input("uc-7-7-collapse-button", "n_clicks"),
        State("uc-7-7-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_7_7_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """Toggle UC-7.7 informative panel collapse state."""
        if n_clicks:
            logger.debug(f"[UC-7.7] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Render Treemap
    # ========================================
    @app.callback(
        Output("uc-7-7-chart", "children"),
        Input("uc-7-7-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_7_7(
        active_item: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-7.7 treemap when accordion is activated.

        Parameters
        ----------
        active_item : str, optional
            ID of the currently active accordion item.
        merged_data : dict, optional
            Dictionary containing 'biorempp_df' and 'toxcsm_df' keys.

        Returns
        -------
        html.Div
            Container with chart or error message.

        Notes
        -----
        - Validates presence of BOTH BioRemPP and ToxCSM data
        - Merges sample-compound links with toxicity predictions
        - Filters for high-risk compounds (toxicity_score > 0.5)
        - Counts ALL interactions per sample-category-compound (NOT unique)
        - Generates treemap with 4-level hierarchy: Root > Sample > Category > Compound
        """
        logger.debug(f"[UC-7.7] Render callback triggered. Active item: {active_item}")

        # Check if UC-7.7 accordion is active
        if not active_item or active_item != "uc-7-7-accordion":
            logger.debug("[UC-7.7] Accordion not active. Preventing update.")
            raise PreventUpdate

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-7.7] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-7.7] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            # Check for required datasets
            if "biorempp_df" not in merged_data:
                logger.error("[UC-7.7] biorempp_df not found in merged_data")
                return _create_error_message(
                    "BioRemPP data not found. This use case requires "
                    "BioRemPP database.",
                    "bi bi-database-x",
                )

            if "toxcsm_df" not in merged_data:
                logger.error("[UC-7.7] toxcsm_df not found in merged_data")
                return _create_error_message(
                    "ToxCSM data not found. This use case requires "
                    "ToxCSM database for toxicity predictions.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrames
            # ========================================
            logger.debug("[UC-7.7] Extracting DataFrames from merged_data")

            biorempp_data = merged_data["biorempp_df"]
            toxcsm_data = merged_data["toxcsm_df"]

            if not biorempp_data:
                logger.warning("[UC-7.7] biorempp_df is empty")
                return _create_error_message(
                    "BioRemPP dataset is empty.", "bi bi-inbox"
                )

            if not toxcsm_data:
                logger.warning("[UC-7.7] toxcsm_df is empty")
                return _create_error_message("ToxCSM dataset is empty.", "bi bi-inbox")

            df_biorempp = pd.DataFrame(biorempp_data)
            df_toxcsm = pd.DataFrame(toxcsm_data)

            logger.info(
                f"[UC-7.7] BioRemPP: {len(df_biorempp)} rows, "
                f"ToxCSM: {len(df_toxcsm)} rows"
            )

            # ========================================
            # Step 3: Map column names flexibly
            # ========================================
            # BioRemPP: Sample column
            sample_col = None
            sample_candidates = ["Sample", "sample", "sample_id", "Sample_ID", "genome"]
            for col_name in sample_candidates:
                if col_name in df_biorempp.columns:
                    sample_col = col_name
                    break

            # BioRemPP: Compound column
            compound_col_biorempp = None
            compound_candidates = [
                "Compound_Name",
                "compound_name",
                "compoundname",
                "CompoundName",
                "compound",
                "Compound",
            ]
            for col_name in compound_candidates:
                if col_name in df_biorempp.columns:
                    compound_col_biorempp = col_name
                    break

            # ToxCSM: Compound column (lowercase in ToxCSM)
            compound_col_toxcsm = None
            toxcsm_compound_candidates = [
                "compoundname",
                "compound_name",
                "Compound_Name",
                "compound",
            ]
            for col_name in toxcsm_compound_candidates:
                if col_name in df_toxcsm.columns:
                    compound_col_toxcsm = col_name
                    break

            # Validate required columns
            if not sample_col:
                return _create_error_message(
                    "Sample column not found in BioRemPP data.",
                    "bi bi-exclamation-octagon",
                )

            if not compound_col_biorempp:
                return _create_error_message(
                    "Compound column not found in BioRemPP data.",
                    "bi bi-exclamation-octagon",
                )

            if not compound_col_toxcsm:
                return _create_error_message(
                    "Compound column not found in ToxCSM data.",
                    "bi bi-exclamation-octagon",
                )

            # Check for super_category in ToxCSM
            if "super_category" not in df_toxcsm.columns:
                return _create_error_message(
                    "ToxCSM data missing 'super_category' column.",
                    "bi bi-exclamation-octagon",
                )

            # ========================================
            # Step 4: Filter ToxCSM for high-risk compounds
            # ========================================
            if "toxicity_score" in df_toxcsm.columns:
                df_risk = df_toxcsm[df_toxcsm["toxicity_score"] > 0.5].copy()
                logger.info(f"[UC-7.7] Filtered to {len(df_risk)} high-risk records")
            else:
                df_risk = df_toxcsm.copy()

            if df_risk.empty:
                return _create_error_message(
                    "No high-risk compounds found in ToxCSM data.", "bi bi-funnel"
                )

            # Get unique compound-category pairs
            df_risk_processed = df_risk[
                [compound_col_toxcsm, "super_category"]
            ].drop_duplicates()
            df_risk_processed = df_risk_processed.rename(
                columns={compound_col_toxcsm: "compoundname"}
            )

            # ========================================
            # Step 5: Prepare BioRemPP data
            # ========================================
            df_biorempp_clean = df_biorempp[[sample_col, compound_col_biorempp]].copy()
            df_biorempp_clean = df_biorempp_clean.rename(
                columns={sample_col: "Sample", compound_col_biorempp: "compoundname"}
            )
            df_biorempp_clean = df_biorempp_clean.dropna()

            # ========================================
            # Step 6: Merge BioRemPP with risk data
            # ========================================
            # Do NOT drop duplicates - we want to count all interactions
            df_merged = pd.merge(
                df_biorempp_clean, df_risk_processed, on="compoundname", how="inner"
            )

            logger.info(f"[UC-7.7] Merged data: {len(df_merged)} records")

            if df_merged.empty:
                return _create_error_message(
                    "No matching compounds found between BioRemPP and "
                    "ToxCSM high-risk data.",
                    "bi bi-link-45deg",
                )

            # ========================================
            # Step 7: Aggregate for treemap (count interactions)
            # ========================================
            # Count interactions per sample, category, and compound
            df_agg = (
                df_merged.groupby(["Sample", "super_category", "compoundname"])
                .size()
                .reset_index(name="interaction_count")
            )
            df_agg = df_agg.rename(columns={"super_category": "Toxicity Category"})
            df_agg["root"] = "All Samples"

            logger.info(
                f"[UC-7.7] Aggregated: {len(df_agg)} rows, "
                f"{df_agg['Sample'].nunique()} samples, "
                f"{df_agg['Toxicity Category'].nunique()} categories, "
                f"{df_agg['compoundname'].nunique()} compounds"
            )

            if df_agg.empty:
                return _create_error_message(
                    "No data after aggregation.", "bi bi-funnel"
                )

            # ========================================
            # Step 8: Generate Treemap
            # ========================================
            logger.debug("[UC-7.7] Generating treemap")

            color_sequence = px.colors.qualitative.Pastel1

            fig = px.treemap(
                df_agg,
                path=["root", "Sample", "Toxicity Category", "compoundname"],
                values="interaction_count",
                color="Toxicity Category",
                color_discrete_sequence=color_sequence,
                hover_data={"interaction_count": ":.0f"},
            )

            # Don't add text labels for deep hierarchies (visual clutter)
            fig.update_layout(
                title=dict(
                    text="Sample Risk Mitigation Depth Profile by Genetic Investment",
                    x=0.5,
                    xanchor="center",
                    font=dict(size=16),
                ),
                height=700,
                width=None,
                template="simple_white",
                margin=dict(t=50, l=25, r=25, b=25),
            )

            logger.info("[UC-7.7] Treemap generation successful")

            # ========================================
            # Step 9: Prepare filename and return chart component
            # ========================================
            try:
                suggested = sanitize_filename("UC-7.7", "risk_mitigation_depth", "png")
            except Exception:
                suggested = "risk_mitigation_depth.png"

            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                id="uc-7-7-graph",
                figure=fig,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "responsive": True,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 900,
                        "width": 1400,
                        "scale": 6,
                    },
                },
                style={"height": "700px", "width": "100%"},
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(
                f"[UC-7.7] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-7.7] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-7.7] All callbacks registered successfully")


def _create_error_message(
    message: str, icon_class: str = "bi bi-exclamation-triangle"
) -> html.Div:
    """
    Create a user-friendly error message component.

    Parameters
    ----------
    message : str
        Error message text to display.
    icon_class : str, optional
        Bootstrap icon class for the alert icon.
        Default: "bi bi-exclamation-triangle"

    Returns
    -------
    html.Div
        Styled alert component with icon and message.
    """
    return html.Div(
        [html.I(className=f"{icon_class} me-2"), html.Span(message)],
        className="alert alert-warning d-flex align-items-center mt-3",
        role="alert",
    )
