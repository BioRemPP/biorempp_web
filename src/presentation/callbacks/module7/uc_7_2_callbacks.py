"""
UC-7.2 Callbacks - Concordance Between Predicted Risk and Regulatory Focus.

This module implements callback functions for visualizing risk-regulatory
concordance through chord diagram analysis using cross-database integration
(BioRemPP + ToxCSM).

Functions
---------
register_uc_7_2_callbacks
    Register all UC-7.2 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses ChordStrategy for risk-regulatory overlap visualization
- Requires BOTH BioRemPP and ToxCSM databases (cross-database analysis)

Version: 1.0.0
"""

import logging
import os
from itertools import combinations
from typing import Any, Dict, Optional

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)


def register_uc_7_2_callbacks(app, plot_service) -> None:
    """
    Register all UC-7.2 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and chord diagram rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-7.2] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-7-2-collapse", "is_open"),
        Input("uc-7-2-collapse-button", "n_clicks"),
        State("uc-7-2-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_7_2_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """Toggle UC-7.2 informative panel collapse state."""
        if n_clicks:
            logger.debug(f"[UC-7.2] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Render Chord Diagram
    # ========================================
    @app.callback(
        Output("uc-7-2-chart", "children"),
        Input("uc-7-2-threshold-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_7_2(
        selected_threshold: Optional[float], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-7.2 chord diagram when threshold is selected.

        Parameters
        ----------
        selected_threshold : float, optional
            Selected toxicity threshold from dropdown (e.g., 0.7, 0.5, 0.3).
        merged_data : dict, optional
            Dictionary containing merged result data with 'biorempp_df' and
            'toxcsm_df' keys.

        Returns
        -------
        html.Div
            Container with chart or error message.

        Notes
        -----
        - Validates presence of BOTH BioRemPP and ToxCSM data
        - Extracts high-risk compounds from ToxCSM (score >= threshold)
        - Extracts regulatory agency compound sets from BioRemPP
        - Computes pairwise intersections between all sets
        - Passes intersection data to ChordStrategy via PlotService
        - Generates chord diagram showing overlap magnitudes
        """
        logger.info(f"[UC-7.2] Render triggered, threshold: {selected_threshold}")

        # Check if threshold is selected
        if selected_threshold is None:
            logger.debug("[UC-7.2] No threshold selected. Showing prompt.")
            return html.Div(
                [
                    html.I(className="bi bi-hand-index me-2"),
                    html.Span(
                        "Please select a toxicity threshold from the dropdown "
                        "above to visualize the chord diagram."
                    ),
                ],
                className="alert alert-info d-flex align-items-center mt-3",
                role="alert",
            )

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-7.2] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-7.2] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            # Check for required databases
            if "biorempp_df" not in merged_data:
                logger.error("[UC-7.2] BioRemPP data not found")
                return _create_error_message(
                    "BioRemPP data not found. This use case requires both "
                    "BioRemPP and ToxCSM databases.",
                    "bi bi-database-x",
                )

            if "toxcsm_df" not in merged_data:
                logger.error("[UC-7.2] ToxCSM data not found")
                return _create_error_message(
                    "ToxCSM data not found. This use case requires both "
                    "BioRemPP and ToxCSM databases.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrames
            # ========================================
            logger.debug("[UC-7.2] Extracting DataFrames from merged_data")

            biorempp_data = merged_data["biorempp_df"]
            toxcsm_data = merged_data["toxcsm_df"]

            if not biorempp_data or not toxcsm_data:
                return _create_error_message(
                    "One or more datasets are empty. Please check input data.",
                    "bi bi-inbox",
                )

            df_biorempp = pd.DataFrame(biorempp_data)
            df_toxcsm = pd.DataFrame(toxcsm_data)

            logger.info(
                f"[UC-7.2] BioRemPP: {len(df_biorempp)} rows, "
                f"ToxCSM: {len(df_toxcsm)} rows"
            )

            # ========================================
            # Step 3: Map column names flexibly
            # ========================================

            # BioRemPP - referenceAG column
            agency_col = None
            agency_candidates = [
                "referenceAG",
                "referenceag",
                "ReferenceAG",
                "reference_ag",
                "Agency",
                "agency",
            ]
            for col_name in agency_candidates:
                if col_name in df_biorempp.columns:
                    agency_col = col_name
                    break

            # BioRemPP - compoundname column
            biorempp_compound_col = None
            compound_candidates = [
                "compoundname",
                "Compound_Name",
                "compound_name",
                "CompoundName",
                "compound",
                "Compound",
            ]
            for col_name in compound_candidates:
                if col_name in df_biorempp.columns:
                    biorempp_compound_col = col_name
                    break

            # ToxCSM - compoundname column
            toxcsm_compound_col = None
            for col_name in compound_candidates:
                if col_name in df_toxcsm.columns:
                    toxcsm_compound_col = col_name
                    break

            # ToxCSM - toxicity_score column
            score_col = None
            score_candidates = ["toxicity_score", "ToxicityScore", "score", "Score"]
            for col_name in score_candidates:
                if col_name in df_toxcsm.columns:
                    score_col = col_name
                    break

            # Validate required columns
            missing = []
            if not agency_col:
                missing.append("referenceAG (BioRemPP)")
            if not biorempp_compound_col:
                missing.append("compoundname (BioRemPP)")
            if not toxcsm_compound_col:
                missing.append("compoundname (ToxCSM)")
            if not score_col:
                missing.append("toxicity_score (ToxCSM)")

            if missing:
                logger.error(f"[UC-7.2] Missing columns: {missing}")
                return _create_error_message(
                    f"Required columns not found: {', '.join(missing)}",
                    "bi bi-exclamation-octagon",
                )

            # ========================================
            # Step 4: Extract High-Risk Compounds (ToxCSM)
            # ========================================
            logger.debug(
                f"[UC-7.2] Extracting high-risk compounds "
                f"(threshold >= {selected_threshold})"
            )

            # Clean ToxCSM data
            df_toxcsm_clean = df_toxcsm[[toxcsm_compound_col, score_col]].dropna()
            df_toxcsm_clean[score_col] = pd.to_numeric(
                df_toxcsm_clean[score_col], errors="coerce"
            )
            df_toxcsm_clean = df_toxcsm_clean.dropna()

            # Filter by threshold
            high_risk_df = df_toxcsm_clean[
                df_toxcsm_clean[score_col] >= selected_threshold
            ]
            high_risk_compounds = set(
                high_risk_df[toxcsm_compound_col].astype(str).str.strip().unique()
            )

            logger.info(
                f"[UC-7.2] Found {len(high_risk_compounds)} high-risk "
                f"compounds (>= {selected_threshold})"
            )

            if len(high_risk_compounds) == 0:
                return _create_error_message(
                    f"No compounds found with toxicity score >= "
                    f"{selected_threshold}. Try a lower threshold.",
                    "bi bi-funnel",
                )

            # ========================================
            # Step 5: Extract Agency Compound Sets (BioRemPP)
            # ========================================
            logger.debug("[UC-7.2] Extracting agency compound sets")

            # Clean BioRemPP data
            df_biorempp_clean = df_biorempp[
                [agency_col, biorempp_compound_col]
            ].dropna()

            # Strip whitespace and remove placeholders
            df_biorempp_clean[agency_col] = (
                df_biorempp_clean[agency_col].astype(str).str.strip()
            )
            df_biorempp_clean[biorempp_compound_col] = (
                df_biorempp_clean[biorempp_compound_col].astype(str).str.strip()
            )

            # Remove invalid values
            df_biorempp_clean = df_biorempp_clean[
                ~df_biorempp_clean[agency_col].isin(["#N/D", "#N/A", "N/D", "", "nan"])
            ]
            df_biorempp_clean = df_biorempp_clean[
                ~df_biorempp_clean[biorempp_compound_col].isin(
                    ["#N/D", "#N/A", "N/D", "", "nan"]
                )
            ]

            # Group compounds by agency
            agency_compound_sets = (
                df_biorempp_clean.groupby(agency_col)[biorempp_compound_col]
                .apply(set)
                .to_dict()
            )

            logger.info(
                f"[UC-7.2] Found {len(agency_compound_sets)} regulatory "
                f"agencies: {list(agency_compound_sets.keys())}"
            )

            if len(agency_compound_sets) == 0:
                return _create_error_message(
                    "No regulatory agencies found in BioRemPP data.", "bi bi-funnel"
                )

            # ========================================
            # Step 6: Combine Sets and Compute Intersections
            # ========================================
            logger.debug("[UC-7.2] Computing pairwise intersections")

            # Combine all sets
            all_sets = agency_compound_sets.copy()
            all_sets["High Predicted Risk"] = high_risk_compounds

            # Compute pairwise intersections
            set_names = list(all_sets.keys())
            links_list = []

            for name1, name2 in combinations(set_names, 2):
                intersection_size = len(all_sets[name1].intersection(all_sets[name2]))
                if intersection_size > 0:
                    links_list.append(
                        {"source": name1, "target": name2, "value": intersection_size}
                    )

            if len(links_list) == 0:
                return _create_error_message(
                    "No overlapping compounds found between agencies and "
                    "high-risk category.",
                    "bi bi-diagram-3",
                )

            # Create DataFrame for plotting
            df_links = pd.DataFrame(links_list)

            logger.info(f"[UC-7.2] Computed {len(df_links)} pairwise intersections")

            # ========================================
            # Step 7: Generate plot using PlotService
            # ========================================
            logger.debug("[UC-7.2] Calling PlotService to generate chord")

            fig = plot_service.generate_plot(
                use_case_id="UC-7.2",
                data=df_links,
                filters={"threshold": selected_threshold},
                force_refresh=False,
            )

            logger.info("[UC-7.2] Chord diagram generation successful")

            # ========================================
            # Step 8: Return chart component
            # ========================================
            threshold_label = {0.7: "High", 0.5: "Moderate", 0.3: "Low"}.get(
                selected_threshold, str(selected_threshold)
            )

            # Prepare a safe database basename (avoid spaces)
            db_basename = f"risk_regulatory_concordance_{str(threshold_label)}"
            db_basename = db_basename.replace(" ", "_")

            try:
                suggested = sanitize_filename("UC-7.2", db_basename, "png")
            except Exception:
                suggested = f"{db_basename}.png"

            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                id="uc-7-2-graph",
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
                        "width": 900,
                        "scale": 6,
                    },
                },
                style={"height": "800px", "width": "100%"},
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(
                f"[UC-7.2] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-7.2] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-7.2] All callbacks registered successfully")


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
