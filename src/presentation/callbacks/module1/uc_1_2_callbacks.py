"""
UC-1.2 Callbacks - Regulatory Agency Compound Overlap Analysis.

This module implements callback functions for compound overlap analysis
across environmental regulatory agencies using UpSet plots.

Functions
---------
register_uc_1_2_callbacks
    Register all UC-1.2 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses UpSetStrategy for set intersection visualization
- Implements on-demand rendering for performance optimization

Version: 1.0.0
"""

import os
from typing import Any, Optional

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename
from src.shared.logging import get_logger

logger = get_logger(__name__)


def _find_compound_column(df: pd.DataFrame) -> Optional[str]:
    """
    Find compound name column in DataFrame (case-insensitive).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to search for compound column.

    Returns
    -------
    str or None
        Column name if found, None otherwise.

    Notes
    -----
    Searches for common compound column names:
    - 'Compound Name', 'compound_name', 'compound'
    - 'Chemical', 'chemical_name'
    - 'Name' (if unambiguous)
    """
    logger.debug(
        f"[UC-1.2] Searching for compound column in DataFrame with "
        f"columns: {list(df.columns)}"
    )

    # Based on BioRemPP CLI version: 'compoundname' (all lowercase, no separator)
    # Based on actual data: 'Compound_Name' (with underscore)
    candidates = [
        "compoundname",  # CLI version (all lowercase)
        "Compound_Name",  # Actual BioRemPP column
        "Compound Name",  # With space
        "compound_name",  # Snake case
        "compound",  # Short version
        "Chemical",
        "chemical_name",
    ]

    for candidate in candidates:
        if candidate in df.columns:
            logger.debug(f"[UC-1.2] Found compound column: '{candidate}'")
            return candidate

    # Case-insensitive fallback
    lower_cols = {col.lower(): col for col in df.columns}
    for candidate in [
        "compoundname",  # CLI version
        "compound_name",  # With underscore
        "compound name",  # With space
        "compound",
        "chemical",
    ]:
        if candidate in lower_cols:
            found_col = lower_cols[candidate]
            logger.debug(
                f"[UC-1.2] Found compound column (case-insensitive): " f"'{found_col}'"
            )
            return found_col

    logger.warning("[UC-1.2] No compound column found in DataFrame")
    return None


def _find_agency_column(df: pd.DataFrame) -> Optional[str]:
    """
    Find regulatory agency column in DataFrame (case-insensitive).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to search for agency column.

    Returns
    -------
    str or None
        Column name if found, None otherwise.

    Notes
    -----
    Searches for regulatory agency column names:
    - 'referenceAG', 'reference_ag', 'agency'
    - 'regulatory_agency', 'source'
    """
    logger.debug(
        f"[UC-1.2] Searching for agency column in DataFrame with "
        f"columns: {list(df.columns)}"
    )

    # Based on BioRemPP CLI version: 'referenceAG'
    # Based on actual data: 'Agency'
    candidates = [
        "referenceAG",  # CLI version (exact match)
        "reference_ag",
        "agency",  # Lowercase
        "regulatory_agency",
        "source",
    ]

    for candidate in candidates:
        if candidate in df.columns:
            logger.debug(f"[UC-1.2] Found agency column: '{candidate}'")
            return candidate

    # Case-insensitive fallback
    lower_cols = {col.lower(): col for col in df.columns}
    for candidate in [
        "referenceag",  # CLI version
        "agency",  # Actual column
        "reference_ag",
        "regulatory_agency",
        "source",
    ]:
        if candidate in lower_cols:
            found_col = lower_cols[candidate]
            logger.debug(
                f"[UC-1.2] Found agency column (case-insensitive): " f"'{found_col}'"
            )
            return found_col

    logger.warning("[UC-1.2] No agency column found in DataFrame")
    return None


def _normalize_compound(series: pd.Series) -> pd.Series:
    """
    Normalize compound names for consistent comparison.

    Parameters
    ----------
    series : pd.Series
        Series of compound names to normalize.

    Returns
    -------
    pd.Series
        Normalized compound names (trimmed, uppercase).

    Notes
    -----
    - Strips whitespace from both ends
    - Converts to uppercase for case-insensitive matching
    - Removes null/NaN values
    """
    return series.str.strip().str.upper().dropna()


def _extract_biorempp_data(merged_data: dict) -> Optional[pd.DataFrame]:
    """
    Extract BioRemPP DataFrame from merged-result-store.

    Parameters
    ----------
    merged_data : dict
        Dictionary from merged-result-store containing database DataFrames.
        Expected structure:
        {
            'biorempp_df': [...],  # List of row dicts
            'hadeg_df': [...],
            'toxcsm_df': [...],
            'kegg_df': [...],
            'metadata': {...}
        }

    Returns
    -------
    pd.DataFrame or None
        BioRemPP DataFrame with compound and agency data, or None if error.

    Notes
    -----
    Converts serialized list of dicts back to pandas DataFrame.
    """
    logger.debug("[UC-1.2] Extracting BioRemPP data from merged-result-store")

    if not merged_data:
        logger.error("[UC-1.2] merged_data is None or empty")
        return None

    biorempp_list = merged_data.get("biorempp_df")
    if not biorempp_list:
        logger.error("[UC-1.2] 'biorempp_df' key not found in merged_data")
        return None

    try:
        biorempp_df = pd.DataFrame(biorempp_list)
        logger.info(
            f"[UC-1.2] Extracted BioRemPP DataFrame: "
            f"{len(biorempp_df)} rows, {len(biorempp_df.columns)} columns"
        )
        logger.debug(f"[UC-1.2] BioRemPP columns: {list(biorempp_df.columns)}")
        return biorempp_df

    except Exception as e:
        logger.error(
            f"[UC-1.2] Failed to convert biorempp_df to DataFrame: {str(e)}",
            exc_info=True,
        )
        return None


def _build_compound_sets(biorempp_df: pd.DataFrame) -> Optional[dict[str, set[str]]]:
    """
    Build dictionary of compound sets grouped by regulatory agency.

    Parameters
    ----------
    biorempp_df : pd.DataFrame
        BioRemPP DataFrame with compound and agency columns.

    Returns
    -------
    dict[str, set[str]] or None
        Dictionary mapping agency names to sets of compound names.
        Example: {'WFD': {'BENZENE', 'TOLUENE'}, 'CONAMA': {'BENZENE', ...}}

    Notes
    -----
    - Finds compound and agency columns automatically
    - Normalizes compound names (trim, uppercase)
    - Removes duplicates per agency
    - Skips agencies with no valid compounds
    """
    logger.debug("[UC-1.2] Building compound sets grouped by agency")

    # Find columns
    compound_col = _find_compound_column(biorempp_df)
    agency_col = _find_agency_column(biorempp_df)

    if not compound_col or not agency_col:
        logger.error(
            f"[UC-1.2] Missing required columns - "
            f"compound: {compound_col}, agency: {agency_col}"
        )
        return None

    # Extract and normalize
    df_subset = biorempp_df[[compound_col, agency_col]].copy()
    df_subset = df_subset.dropna()

    # Normalize compound names
    df_subset[compound_col] = _normalize_compound(df_subset[compound_col])

    # Group by agency and build sets
    compound_sets = {}
    grouped = df_subset.groupby(agency_col)[compound_col]

    for agency, compounds in grouped:
        compound_set = set(compounds.unique())
        if compound_set:  # Skip empty sets
            compound_sets[str(agency)] = compound_set
            logger.debug(
                f"[UC-1.2] Agency '{agency}': {len(compound_set)} unique compounds"
            )

    if not compound_sets:
        logger.error("[UC-1.2] No valid compound sets created")
        return None

    logger.info(
        f"[UC-1.2] Built compound sets for {len(compound_sets)} agencies: "
        f"{list(compound_sets.keys())}"
    )

    # Calculate total unique compounds across all agencies
    all_compounds = set()
    for compounds in compound_sets.values():
        all_compounds.update(compounds)

    logger.info(
        f"[UC-1.2] Total unique compounds across all agencies: " f"{len(all_compounds)}"
    )

    return compound_sets


def register_uc_1_2_callbacks(app, plot_service) -> None:
    """
    Register all UC-1.2 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle and plot rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-1.2] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-1-2-collapse", "is_open"),
        Input("uc-1-2-collapse-button", "n_clicks"),
        State("uc-1-2-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_1_2_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """
        Toggle UC-1.2 informative panel collapse state.

        Parameters
        ----------
        n_clicks : int
            Number of times button was clicked.
        is_open : bool
            Current collapse state.

        Returns
        -------
        bool
            New collapse state (toggled).

        Notes
        -----
        Simple toggle: open → close, close → open
        """
        if n_clicks:
            logger.debug(f"[UC-1.2] Toggling info panel: {is_open} → {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Render UpSet Plot
    # ========================================
    @app.callback(
        Output("uc-1-2-chart", "children"),
        Input("uc-1-2-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_1_2(active_item: Optional[str], merged_data: Optional[dict]) -> Any:
        """
        Render UC-1.2 UpSet plot showing compound overlap across agencies.

        Parameters
        ----------
        active_item : str or None
            Active accordion item ID (triggers rendering when opened).
        merged_data : dict or None
            Data from merged-result-store.

        Returns
        -------
        dcc.Graph or html.Div
            UpSet plot figure or error message.

        Notes
        -----
        - Extracts and normalizes compound sets grouped by regulatory agency
        - Generates visualization using UpSetStrategy via PlotService
        """
        logger.info(f"[UC-1.2] ========== RENDER CALLBACK TRIGGERED ==========")
        logger.info(f"[UC-1.2] active_item received: '{active_item}'")
        logger.info(
            f"[UC-1.2] merged_data present: "
            f"{merged_data is not None and len(merged_data) > 0}"
        )

        # Validate accordion is open
        if not active_item:
            logger.debug("[UC-1.2] active_item is None, accordion not opened yet")
            raise PreventUpdate

        if active_item != "uc-1-2-accordion":
            logger.warning(
                f"[UC-1.2] Unexpected active_item: '{active_item}' "
                f"(expected 'uc-1-2-accordion')"
            )
            raise PreventUpdate

        logger.info("[UC-1.2] Accordion opened, starting plot generation")

        # Validate merged_data
        if not merged_data:
            logger.error("[UC-1.2] No data available in merged-result-store")
            return html.Div(
                "No data loaded. Please upload data first.",
                className="alert alert-warning",
            )

        # Extract BioRemPP DataFrame
        logger.info("[UC-1.2] Step 1: Extracting BioRemPP data...")
        biorempp_df = _extract_biorempp_data(merged_data)

        if biorempp_df is None or biorempp_df.empty:
            logger.error(
                "[UC-1.2] FAILED: Could not extract BioRemPP data "
                f"(None: {biorempp_df is None}, "
                f"Empty: {biorempp_df.empty if biorempp_df is not None else 'N/A'})"
            )
            return html.Div(
                "Error: BioRemPP data not available.", className="alert alert-danger"
            )

        logger.info(
            f"[UC-1.2] SUCCESS: Extracted BioRemPP DataFrame - "
            f"{len(biorempp_df)} rows × {len(biorempp_df.columns)} columns"
        )

        # Build compound sets
        logger.info("[UC-1.2] Step 2: Building compound sets by agency...")
        compound_sets = _build_compound_sets(biorempp_df)

        if compound_sets is None:
            logger.error(
                "[UC-1.2] FAILED: Could not build compound sets "
                "(check compound/agency columns)"
            )
            return html.Div(
                "Error: Could not build compound sets. " "Please check data structure.",
                className="alert alert-danger",
            )

        logger.info(
            f"[UC-1.2] SUCCESS: Built {len(compound_sets)} compound sets - "
            f"Agencies: {list(compound_sets.keys())}"
        )
        for agency, compounds in compound_sets.items():
            logger.debug(f"[UC-1.2]   - {agency}: {len(compounds)} compounds")

        # Convert to DataFrame format expected by UpSetStrategy
        logger.info("[UC-1.2] Step 3: Converting to UpSet DataFrame format...")
        upset_data = []
        for agency, compounds in compound_sets.items():
            for compound in compounds:
                upset_data.append({"category": agency, "identifier": compound})

        upset_df = pd.DataFrame(upset_data)
        logger.info(
            f"[UC-1.2] SUCCESS: Created UpSet DataFrame - "
            f"{len(upset_df)} rows × {len(upset_df.columns)} columns"
        )
        logger.debug(f"[UC-1.2] DataFrame columns: {list(upset_df.columns)}")
        logger.debug(f"[UC-1.2] DataFrame head (5 rows):\n{upset_df.head()}")

        # Generate plot using PlotService
        logger.info("[UC-1.2] Step 4: Generating UpSet plot...")
        try:
            logger.debug("[UC-1.2] PlotService instantiated, calling generate_plot()")

            fig = plot_service.generate_plot(data=upset_df, use_case_id="UC-1.2")

            logger.info("[UC-1.2] SUCCESS: UpSet plot generated successfully!")
            logger.debug(f"[UC-1.2] Figure type: {type(fig)}")

            # Return as Dash Graph component
            logger.info("[UC-1.2] Step 5: Returning dcc.Graph component")

            try:
                suggested = sanitize_filename("UC-1.2", "compound_overlap", "png")
                base_filename = os.path.splitext(suggested)[0]
            except Exception:
                base_filename = "uc_1_2_compound_overlap"

            graph_component = dcc.Graph(
                figure=fig,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 900,
                        "width": 1400,
                        "scale": 2,
                    },
                },
            )
            logger.info("[UC-1.2] ========== RENDER COMPLETE ==========")
            return graph_component

        except Exception as e:
            logger.error(f"[UC-1.2] ========== RENDER FAILED ==========")
            logger.error(
                f"[UC-1.2] Error type: {type(e).__name__}",
            )
            logger.error(f"[UC-1.2] Error message: {str(e)}", exc_info=True)
            return html.Div(
                f"Error generating plot: {str(e)}", className="alert alert-danger"
            )

    logger.info("[UC-1.2] All callbacks registered successfully")
