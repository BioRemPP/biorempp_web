"""
UC-1.1 Callbacks - Database Overlap Analysis.

This module implements callback functions for database overlap and unique
contributions analysis using UpSet plots.

Functions
---------
register_uc_1_1_callbacks
    Register all UC-1.1 callbacks with Dash app.

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


def _find_ko_column(df: pd.DataFrame) -> Optional[str]:
    """
    Find KO column in DataFrame (case-insensitive).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to search for KO column.

    Returns
    -------
    str or None
        Column name if found, None otherwise.

    Notes
    -----
    Searches for common KO column names:
    - 'ko', 'KO' (BioRemPP, HADEG)
    - 'gene', 'Gene' (KEGG)
    - 'kegg_ko', 'KEGG_KO' (alternative naming)
    """
    logger.debug(
        f"Searching for KO column in DataFrame with " f"columns: {list(df.columns)}"
    )

    candidates = ["ko", "KO", "gene", "Gene", "kegg_ko", "KEGG_KO"]

    for candidate in candidates:
        if candidate in df.columns:
            logger.debug(f"Found KO column: '{candidate}'")
            return candidate

    # Case-insensitive fallback
    lower_cols = {col.lower(): col for col in df.columns}
    for candidate in ["ko", "gene", "kegg_ko"]:
        if candidate in lower_cols:
            found_col = lower_cols[candidate]
            logger.debug(f"Found KO column (case-insensitive): '{found_col}'")
            return found_col

    logger.warning(f"No KO column found. Available columns: {list(df.columns)}")
    return None


def _normalize_ko(series: pd.Series) -> pd.Series:
    """
    Normalize KO identifiers (trim whitespace, uppercase).

    Parameters
    ----------
    series : pd.Series
        Series with KO identifiers.

    Returns
    -------
    pd.Series
        Normalized series (trimmed, uppercase, no NaN).

    Examples
    --------
    >>> _normalize_ko(pd.Series([' k00001 ', 'K00002', None]))
    0    K00001
    1    K00002
    2
    dtype: object
    """
    original_count = len(series)
    null_count = series.isna().sum()

    normalized = series.fillna("").astype(str).str.strip().str.upper()

    empty_count = (normalized == "").sum()
    valid_count = original_count - empty_count

    logger.debug(
        f"Normalized KO series: {original_count} total, "
        f"{null_count} nulls, {empty_count} empty, {valid_count} valid"
    )

    return normalized


def _extract_database_data(merged_data: list) -> tuple:
    """
    Extract database DataFrames from merged result store.

    Parameters
    ----------
    merged_data : list
        List of dictionaries from merged-result-store.

    Returns
    -------
    tuple
        (biorempp_df, hadeg_df, kegg_df) or (None, None, None) if error.

    Notes
    -----
    Expected structure:
    - merged_data[0]['data']: BioRemPP data
    - merged_data[1]['data']: HADEG data
    - merged_data[2]['data']: KEGG data
    """
    try:
        logger.debug(
            f"Extracting DataFrames from merged_data with " f"{len(merged_data)} items"
        )
        logger.debug(f"merged_data type: {type(merged_data)}")
        keys_info = (
            list(merged_data.keys())
            if isinstance(merged_data, dict)
            else f"List of {len(merged_data)} items"
        )
        logger.debug(f"merged_data keys/indices: {keys_info}")

        # Check if it's a dict or list
        if isinstance(merged_data, dict):
            logger.debug("merged_data is a dict, extracting by keys...")
            keys = list(merged_data.keys())
            logger.debug(f"Available keys: {keys}")

            # Extract based on actual structure: biorempp_df, hadeg_df, kegg_df
            biorempp_data = merged_data.get("biorempp_df")
            hadeg_data = merged_data.get("hadeg_df")
            kegg_data = merged_data.get("kegg_df")

            if biorempp_data is None or hadeg_data is None or kegg_data is None:
                logger.error(
                    f"Could not find all databases in merged_data. "
                    f"Available keys: {keys}"
                )
                return None, None, None

            logger.debug(
                f"Data types: biorempp={type(biorempp_data)}, "
                f"hadeg={type(hadeg_data)}, kegg={type(kegg_data)}"
            )

            # Data is already serialized as list of dicts
            biorempp_df = pd.DataFrame(biorempp_data)
            hadeg_df = pd.DataFrame(hadeg_data)
            kegg_df = pd.DataFrame(kegg_data)

        else:
            # Original list-based approach
            if not merged_data or len(merged_data) < 3:
                logger.error(
                    f"Insufficient data: expected 3 databases, got "
                    f"{len(merged_data) if merged_data else 0}"
                )
                return None, None, None

            biorempp_df = pd.DataFrame(merged_data[0]["data"])
            hadeg_df = pd.DataFrame(merged_data[1]["data"])
            kegg_df = pd.DataFrame(merged_data[2]["data"])

        logger.debug(
            f"DataFrames created: "
            f"BioRemPP={len(biorempp_df)}x{len(biorempp_df.columns)}, "
            f"HADEG={len(hadeg_df)}x{len(hadeg_df.columns)}, "
            f"KEGG={len(kegg_df)}x{len(kegg_df.columns)}"
        )

        return biorempp_df, hadeg_df, kegg_df

    except (KeyError, IndexError, TypeError) as e:
        logger.error(
            f"Error extracting database data: {type(e).__name__} - {str(e)}",
            exc_info=True,
        )
        return None, None, None


def _build_ko_sets(
    biorempp_df: pd.DataFrame, hadeg_df: pd.DataFrame, kegg_df: pd.DataFrame
) -> Optional[dict]:
    """
    Build KO sets for each database.

    Parameters
    ----------
    biorempp_df : pd.DataFrame
        BioRemPP DataFrame with KO column.
    hadeg_df : pd.DataFrame
        HADEG DataFrame with KO column.
    kegg_df : pd.DataFrame
        KEGG DataFrame with Gene column.

    Returns
    -------
    dict or None
        Dictionary {database_name: set(KOs)} or None if error.

    Examples
    --------
    >>> _build_ko_sets(biorempp_df, hadeg_df, kegg_df)
    {
        'BioRemPP': {'K00001', 'K00002', ...},
        'HADEG': {'K00001', 'K00003', ...},
        'KEGG': {'K00002', 'K00004', ...}
    }
    """
    logger.debug("Finding KO columns in each database")

    # Find KO columns
    biorempp_col = _find_ko_column(biorempp_df)
    hadeg_col = _find_ko_column(hadeg_df)
    kegg_col = _find_ko_column(kegg_df)

    if not biorempp_col:
        logger.error("KO column not found in BioRemPP DataFrame")
    if not hadeg_col:
        logger.error("KO column not found in HADEG DataFrame")
    if not kegg_col:
        logger.error("KO column not found in KEGG DataFrame")

    if not biorempp_col or not hadeg_col or not kegg_col:
        return None

    logger.debug(
        f"KO columns found: BioRemPP='{biorempp_col}', "
        f"HADEG='{hadeg_col}', KEGG='{kegg_col}'"
    )

    # Normalize and build sets
    logger.debug("Normalizing KO identifiers")
    biorempp_ko = _normalize_ko(biorempp_df[biorempp_col])
    hadeg_ko = _normalize_ko(hadeg_df[hadeg_col])
    kegg_ko = _normalize_ko(kegg_df[kegg_col])

    # Remove empty strings
    logger.debug("Building sets (removing empty strings)")
    ko_sets = {
        "BioRemPP": set(biorempp_ko[biorempp_ko != ""]),
        "HADEG": set(hadeg_ko[hadeg_ko != ""]),
        "KEGG": set(kegg_ko[kegg_ko != ""]),
    }

    logger.info(
        f"KO sets built: "
        f"BioRemPP={len(ko_sets['BioRemPP'])} unique KOs, "
        f"HADEG={len(ko_sets['HADEG'])} unique KOs, "
        f"KEGG={len(ko_sets['KEGG'])} unique KOs"
    )

    return ko_sets


def register_uc_1_1_callbacks(app, plot_service) -> None:
    """
    Register UC-1.1 callbacks with Dash app.

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
    logger.info("[UC-1.1] ========== REGISTERING UC-1.1 CALLBACKS ==========")
    logger.info("[UC-1.1] Using shared PlotService singleton instance")

    @app.callback(
        Output("uc-1-1-collapse", "is_open"),
        Input("uc-1-1-collapse-button", "n_clicks"),
        State("uc-1-1-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_1_1_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """
        Toggle UC-1.1 informative panel visibility.

        Parameters
        ----------
        n_clicks : int, optional
            Number of times collapse button was clicked.
        is_open : bool
            Current collapse state (True = open, False = closed).

        Returns
        -------
        bool
            New collapse state (inverted from current state).
        """
        if n_clicks is None:
            raise PreventUpdate

        return not is_open

    @app.callback(
        Output("uc-1-1-chart", "children"),
        Input("uc-1-1-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_1_1(active_item: Optional[str], merged_data: Optional[list]) -> Any:
        """
        Generate UpSet plot for database overlap analysis.

        Parameters
        ----------
        active_item : str, optional
            Active accordion item ID.
        merged_data : list, optional
            Merged result data from store.

        Returns
        -------
        dcc.Graph or html.Div
            UpSet plot or error message.

        Notes
        -----
        - Extracts and normalizes KO sets from databases
        - Generates visualization using UpSetStrategy via PlotService
        """
        logger.info(
            "UC-1.1 render_uc_1_1 callback triggered",
            extra={"active_item": active_item, "has_data": bool(merged_data)},
        )

        # Validate trigger
        if not active_item or active_item != "uc-1-1-accordion":
            logger.debug(
                "Preventing update: accordion not active",
                extra={"active_item": active_item},
            )
            raise PreventUpdate

        # Validate data
        if not merged_data:
            logger.warning("No merged data available in store")
            return html.Div(
                "No data available. Please load data first.",
                className="alert alert-warning",
            )

        # Extract database DataFrames
        logger.debug("Extracting database DataFrames from merged store")
        biorempp_df, hadeg_df, kegg_df = _extract_database_data(merged_data)

        if biorempp_df is None:
            logger.error(
                "Failed to extract database DataFrames",
                extra={"merged_data_len": len(merged_data)},
            )
            return html.Div(
                "Error extracting database data. Please check data format.",
                className="alert alert-danger",
            )

        logger.info(
            "DataFrames extracted successfully",
            extra={
                "biorempp_rows": len(biorempp_df),
                "hadeg_rows": len(hadeg_df),
                "kegg_rows": len(kegg_df),
            },
        )

        # Build KO sets
        logger.debug("Building KO sets for each database")
        ko_sets = _build_ko_sets(biorempp_df, hadeg_df, kegg_df)

        if ko_sets is None:
            logger.error("Failed to build KO sets - KO column not found")
            return html.Div(
                "Error: Could not find KO column in one or more databases.",
                className="alert alert-danger",
            )

        logger.info(
            "KO sets built successfully",
            extra={
                "biorempp_kos": len(ko_sets.get("BioRemPP", set())),
                "hadeg_kos": len(ko_sets.get("HADEG", set())),
                "kegg_kos": len(ko_sets.get("KEGG", set())),
            },
        )

        # Validate sets
        if not any(ko_sets.values()):
            logger.warning("No KO identifiers found after normalization")
            return html.Div(
                "No KO identifiers found in any database.",
                className="alert alert-warning",
            )

        # Prepare data for UpSet plot
        # Convert to DataFrame with category and identifier columns
        logger.debug("Converting KO sets to DataFrame format for UpSetStrategy")
        upset_data = []
        for db_name, ko_set in ko_sets.items():
            for ko in ko_set:
                upset_data.append({"category": db_name, "identifier": ko})

        upset_df = pd.DataFrame(upset_data)

        logger.debug(
            "UpSet DataFrame prepared",
            extra={"total_rows": len(upset_df), "columns": list(upset_df.columns)},
        )

        # Generate plot
        try:
            logger.info(
                "Calling PlotService to generate UpSet plot",
                extra={"use_case_id": "UC-1.1"},
            )

            fig = plot_service.generate_plot(use_case_id="UC-1.1", data=upset_df)

            logger.info("UpSet plot generated successfully")
            logger.debug(
                "Returning dcc.Graph component",
                extra={"figure_type": type(fig).__name__},
            )

            # Prepare a sanitized base filename for image downloads (no extension)
            try:
                suggested = sanitize_filename("UC-1.1", "upset", "png")
                base_filename = os.path.splitext(suggested)[0]
            except Exception:
                base_filename = "UC-1-1_upset"

            return dcc.Graph(
                figure=fig,
                config={
                    "displayModeBar": True,
                    "displaylogo": False,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 800,
                        "width": 1000,
                        "scale": 2,
                    },
                },
            )

        except Exception as e:
            logger.error(f"Error generating UpSet plot: {str(e)}", exc_info=True)
            return html.Div(
                f"Error generating UpSet plot: {str(e)}", className="alert alert-danger"
            )

    logger.info("[UC-1.1] ========== CALLBACKS REGISTERED SUCCESSFULLY ==========")

    #     - Empty intersection: Display "No overlaps found" message
    #     """
    #     pass
