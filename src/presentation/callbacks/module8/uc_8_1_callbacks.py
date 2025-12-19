"""
UC-8.1 Callbacks - Minimal Sample Grouping for Complete Compound Coverage.

This module implements callback functions for visualizing minimal sample
groupings through faceted scatter analysis using set cover optimization.

Functions
---------
register_uc_8_1_callbacks
    Register all UC-8.1 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses Frozenset set Strategy for minimal group visualization
- Applies greedy set cover algorithm for optimization
- BioRemPP database REQUIRED

Version: 1.0.0
"""

import logging
import os
from typing import Any, Dict, List, Optional, Set

import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html
from plotly.subplots import make_subplots

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)


def register_uc_8_1_callbacks(app, plot_service) -> None:
    """
    Register all UC-8.1 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle, dropdown initialization, and faceted scatter callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-8.1] Registering callbacks")

    # ========================================
    # Callback 1: Toggle Informative Panel
    # ========================================
    @app.callback(
        Output("uc-8-1-collapse", "is_open"),
        Input("uc-8-1-collapse-button", "n_clicks"),
        State("uc-8-1-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_8_1_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """Toggle UC-8.1 informative panel collapse state."""
        if n_clicks:
            logger.debug(f"[UC-8.1] Toggling info panel: {is_open} -> {not is_open}")
            return not is_open
        return is_open

    # ========================================
    # Callback 2: Initialize Compound Class Dropdown
    # ========================================
    @app.callback(
        Output("uc-8-1-compoundclass-dropdown", "options"),
        [
            Input("uc-8-1-accordion-group", "active_item"),
            Input("merged-result-store", "data"),
        ],
        prevent_initial_call=True,
    )
    def initialize_uc_8_1_dropdown(
        active_item: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> list:
        """
        Populate compound class dropdown with available classes.

        Parameters
        ----------
        active_item : str, optional
            Active accordion item ID.
        merged_data : dict, optional
            Dictionary containing 'biorempp_df' key.

        Returns
        -------
        list
            Dropdown options list.

        Notes
        -----
        - Triggered when accordion opens or data changes
        - Extracts unique compound classes from BioRemPP data
        - Returns empty list if accordion not active or data unavailable
        """
        logger.info(
            f"[UC-8.1] [CALLBACK 2] Dropdown init triggered, "
            f"active_item: {active_item}"
        )
        logger.debug(f"[UC-8.1] [CALLBACK 2] merged_data type: {type(merged_data)}")
        if isinstance(merged_data, dict):
            logger.debug(f"[UC-8.1] [CALLBACK 2] keys: {merged_data.keys()}")

        # Only populate when accordion is open
        if active_item != "uc-8-1-accordion":
            logger.debug("[UC-8.1] [CALLBACK 2] Accordion not active, skip")
            return []

        if not merged_data or "biorempp_df" not in merged_data:
            logger.warning(
                "[UC-8.1] [CALLBACK 2] No BioRemPP data available for dropdown"
            )
            return []

        try:
            df = pd.DataFrame(merged_data["biorempp_df"])
            logger.debug(
                f"[UC-8.1] [CALLBACK 2] DataFrame created: "
                f"{len(df)} rows, columns: {df.columns.tolist()}"
            )

            if df.empty:
                logger.warning("[UC-8.1] [CALLBACK 2] DataFrame is empty")
                return []

            # Find compound class column
            class_col = _find_column(
                df, ["Compound_Class", "compound_class", "CompoundClass", "class"]
            )

            if not class_col:
                logger.warning(
                    f"[UC-8.1] [CALLBACK 2] Compound class column not found. "
                    f"Available: {df.columns.tolist()}"
                )
                return []

            # Get unique compound classes
            classes = sorted(df[class_col].dropna().unique().tolist())
            options = [{"label": c, "value": c} for c in classes]

            logger.info(
                f"[UC-8.1] [CALLBACK 2] Dropdown populated: " f"{len(classes)} classes"
            )
            logger.debug(f"[UC-8.1] [CALLBACK 2] Classes: {classes[:5]}...")

            return options

        except Exception as e:
            logger.error(
                f"[UC-8.1] [CALLBACK 2] Error initializing dropdown: {e}", exc_info=True
            )
            return []

    # ========================================
    # Callback 3: Render Faceted Scatter
    # ========================================
    @app.callback(
        Output("uc-8-1-chart", "children"),
        Input("uc-8-1-compoundclass-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_8_1(
        selected_class: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-8.1 faceted scatter on compound class dropdown selection.

        Parameters
        ----------
        selected_class : str, optional
            Selected compound class from dropdown.
        merged_data : dict, optional
            Dictionary containing 'biorempp_df' key.

        Returns
        -------
        html.Div
            Container with chart or error message.

        Notes
        -----
        - Filters BioRemPP data by selected compound class
        - Groups samples by frozenset of compounds (identical profiles)
        - Applies greedy set cover algorithm for minimal group selection
        - Calculates unique KO counts per compound for color scaling
        - Generates faceted scatter with one subplot per minimized group
        """
        logger.info(f"[UC-8.1] [CALLBACK 3] ========== RENDER TRIGGERED ==========")
        logger.info(f"[UC-8.1] [CALLBACK 3] selected_class: '{selected_class}'")
        logger.debug(f"[UC-8.1] [CALLBACK 3] merged_data type: {type(merged_data)}")
        logger.debug(f"[UC-8.1] [CALLBACK 3] is None: {merged_data is None}")

        # Validate compound class selection
        if not selected_class:
            logger.debug("[UC-8.1] No compound class selected")
            return _create_info_message(
                "Please select a Compound Class from the dropdown above.",
                "bi bi-arrow-up-circle",
            )

        try:
            # ========================================
            # Step 1: Validate merged_data structure
            # ========================================
            if not merged_data:
                logger.warning("[UC-8.1] merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please upload and process data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict):
                logger.error("[UC-8.1] merged_data is not a dictionary")
                return _create_error_message(
                    "Invalid data structure. Please reload the application.",
                    "bi bi-x-circle",
                )

            if "biorempp_df" not in merged_data:
                logger.error("[UC-8.1] merged_data does not contain 'biorempp_df' key")
                return _create_error_message(
                    "BioRemPP data not found. This use case requires "
                    "BioRemPP database.",
                    "bi bi-database-x",
                )

            # ========================================
            # Step 2: Extract DataFrame
            # ========================================
            logger.debug("[UC-8.1] Extracting DataFrame from merged_data")
            biorempp_data = merged_data["biorempp_df"]

            if not biorempp_data:
                logger.warning("[UC-8.1] biorempp_df is empty")
                return _create_error_message(
                    "BioRemPP dataset is empty. Please check your input data.",
                    "bi bi-inbox",
                )

            df = pd.DataFrame(biorempp_data)

            if df.empty:
                logger.warning("[UC-8.1] DataFrame is empty after conversion")
                return _create_error_message(
                    "No data available after processing.", "bi bi-inbox"
                )

            logger.info(
                f"[UC-8.1] Processing DataFrame: {len(df)} rows, "
                f"{len(df.columns)} columns"
            )

            # ========================================
            # Step 3: Map column names flexibly
            # ========================================
            col_map = {}

            # Sample column
            sample_col = _find_column(
                df, ["Sample", "sample", "sample_name", "SampleName"]
            )
            if sample_col:
                col_map["sample"] = sample_col

            # Compound name column
            compound_col = _find_column(
                df, ["Compound_Name", "compound_name", "CompoundName", "Compound"]
            )
            if compound_col:
                col_map["compoundname"] = compound_col

            # Compound class column
            class_col = _find_column(
                df, ["Compound_Class", "compound_class", "CompoundClass", "class"]
            )
            if class_col:
                col_map["compoundclass"] = class_col

            # KO column (optional, for color)
            ko_col = _find_column(df, ["KO", "ko", "ko_id", "KO_ID"])
            if ko_col:
                col_map["ko"] = ko_col

            # ========================================
            # Step 4: Validate required columns found
            # ========================================
            required = ["sample", "compoundname", "compoundclass"]
            missing_cols = [col for col in required if col not in col_map]

            if missing_cols:
                logger.error(
                    f"[UC-8.1] Missing columns: {missing_cols}. "
                    f"Available: {df.columns.tolist()}"
                )
                return _create_error_message(
                    f"Required columns not found: {', '.join(missing_cols)}. "
                    f"Available columns: {', '.join(df.columns[:5])}...",
                    "bi bi-exclamation-octagon",
                )

            # ========================================
            # Step 5: Prepare data
            # ========================================
            # Rename columns to standard names
            rename_map = {v: k for k, v in col_map.items()}
            df_work = df.rename(columns=rename_map).copy()

            # Filter by selected compound class
            df_filtered = df_work[df_work["compoundclass"] == selected_class].copy()

            if df_filtered.empty:
                logger.warning(f"[UC-8.1] No data for class '{selected_class}'")
                return _create_error_message(
                    f"No data found for compound class: {selected_class}",
                    "bi bi-search",
                )

            # Clean data
            df_filtered = df_filtered.dropna(subset=["sample", "compoundname"])

            for col in ["sample", "compoundname"]:
                df_filtered[col] = df_filtered[col].astype(str).str.strip()

            # Remove placeholder values
            placeholder_values = ["#N/D", "#N/A", "N/D", "", "nan", "None"]
            for col in ["sample", "compoundname"]:
                df_filtered = df_filtered[~df_filtered[col].isin(placeholder_values)]

            if df_filtered.empty:
                return _create_error_message(
                    f"No valid data for compound class: {selected_class}",
                    "bi bi-funnel",
                )

            logger.info(
                f"[UC-8.1] Filtered to {len(df_filtered)} rows for "
                f"class '{selected_class}'"
            )

            # ========================================
            # Step 6: Group samples by compound profile
            # ========================================
            grouped_df, groups = _group_by_compound_profile(df_filtered)

            if grouped_df.empty or not groups:
                return _create_error_message(
                    "No sample groups found after grouping.", "bi bi-diagram-3"
                )

            logger.info(f"[UC-8.1] Created {len(groups)} groups")

            # ========================================
            # Step 7: Minimize groups with set cover
            # ========================================
            minimized_groups = _minimize_groups(grouped_df)

            if not minimized_groups:
                return _create_error_message(
                    "Could not determine minimal groups.", "bi bi-exclamation-circle"
                )

            # Filter to minimized groups only
            final_df = grouped_df[grouped_df["_group"].isin(minimized_groups)].copy()

            logger.info(f"[UC-8.1] Minimized to {len(minimized_groups)} groups")

            # ========================================
            # Step 8: Calculate KO counts (for color)
            # ========================================
            if "ko" in col_map:
                ko_counts = _calculate_ko_counts(df_filtered)
                if ko_counts is not None:
                    final_df = final_df.merge(
                        ko_counts, left_on="compoundname", right_index=True, how="left"
                    )
                    final_df["_unique_ko_count"] = (
                        final_df["_unique_ko_count"].fillna(0).astype(int)
                    )
                else:
                    final_df["_unique_ko_count"] = 1
            else:
                final_df["_unique_ko_count"] = 1

            # ========================================
            # Step 9: Generate plot
            # ========================================
            fig = _create_frozenset_figure(final_df, minimized_groups, selected_class)

            logger.info("[UC-8.1] Faceted scatter generation successful")

            # ========================================
            # Step 10: Return chart component
            # ========================================
            n_groups = len(minimized_groups)
            n_samples = final_df["sample"].nunique()
            n_compounds = final_df["compoundname"].nunique()

            # Prepare a safe download filename using canonical helper
            selected_class_safe = str(selected_class).replace(" ", "_")
            try:
                suggested = sanitize_filename(
                    "UC-8.1", f"minimal_grouping_{selected_class_safe}", "png"
                )
            except Exception:
                suggested = f"minimal_grouping_{selected_class_safe}.png"

            base_filename = os.path.splitext(suggested)[0]

            return html.Div(
                [
                    # Statistics summary
                    html.Div(
                        [
                            html.Small(
                                [
                                    html.I(className="bi bi-info-circle me-2"),
                                    f"Minimal Coverage: {n_groups} functional guilds | "
                                    f"{n_samples} samples | {n_compounds} compounds | "
                                    f"Class: {selected_class}",
                                ],
                                className="text-muted",
                            )
                        ],
                        className="mb-2",
                    ),
                    # Graph container with overflow control
                    html.Div(
                        [
                            dcc.Graph(
                                id="uc-8-1-graph",
                                figure=fig,
                                config={
                                    "displayModeBar": True,
                                    "displaylogo": False,
                                    "responsive": True,
                                    "modeBarButtonsToRemove": [
                                        "pan2d",
                                        "lasso2d",
                                        "select2d",
                                    ],
                                    "toImageButtonOptions": {
                                        "format": "png",
                                        "filename": base_filename,
                                        "height": 600,
                                        "width": 900,
                                        "scale": 6,
                                    },
                                },
                                style={
                                    "height": "600px",
                                    "width": "100%",
                                    "minWidth": "100%",
                                },
                                className="mt-3",
                            )
                        ],
                        style={
                            "width": "100%",
                            "overflowX": "auto",
                            "overflowY": "hidden",
                        },
                    ),
                ]
            )

        except ValueError as ve:
            logger.error(
                f"[UC-8.1] ValueError during processing: {str(ve)}", exc_info=True
            )
            return _create_error_message(
                f"Data validation error: {str(ve)}", "bi bi-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"[UC-8.1] Unexpected error: {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred: {str(e)}", "bi bi-bug"
            )

    logger.info("[UC-8.1] All callbacks registered successfully")


# ========================================
# Helper Functions
# ========================================


def _find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Find first matching column from candidate list."""
    for col_name in candidates:
        if col_name in df.columns:
            return col_name
    return None


def _group_by_compound_profile(df: pd.DataFrame) -> tuple:
    """
    Group samples by their compound profile (frozenset of compounds).

    Returns
    -------
    tuple
        (DataFrame with '_group' column, list of group dicts)
    """
    logger.debug(
        f"[UC-8.1] [_group_by_compound_profile] Starting with " f"{len(df)} rows"
    )
    compound_profile_to_group: Dict[int, int] = {}
    groups: List[Dict[str, Any]] = []

    unique_samples = df["sample"].unique()
    logger.debug(
        f"[UC-8.1] [_group_by_compound_profile] Found "
        f"{len(unique_samples)} unique samples"
    )

    for sample in unique_samples:
        compounds = frozenset(df.loc[df["sample"] == sample, "compoundname"].unique())

        if compounds:
            profile_hash = hash(compounds)

            if profile_hash in compound_profile_to_group:
                group_idx = compound_profile_to_group[profile_hash]
                groups[group_idx]["samples"].append(sample)
            else:
                new_group = {"compounds": list(compounds), "samples": [sample]}
                groups.append(new_group)
                compound_profile_to_group[profile_hash] = len(groups) - 1

    # Add group labels to dataframe
    df_grouped = df.copy()
    df_grouped["_group"] = None

    for i, group in enumerate(groups):
        label = f"Group {i + 1}"
        df_grouped.loc[df_grouped["sample"].isin(group["samples"]), "_group"] = label

    result = df_grouped.dropna(subset=["_group"])
    logger.debug(
        f"[UC-8.1] [_group_by_compound_profile] Created {len(groups)} groups, "
        f"result has {len(result)} rows"
    )
    return result, groups


def _minimize_groups(df: pd.DataFrame) -> List[str]:
    """
    Apply greedy set cover algorithm to minimize groups.

    Returns
    -------
    List[str]
        List of selected group labels.
    """
    logger.debug("[UC-8.1] [_minimize_groups] Starting set cover algorithm")

    if df.empty:
        logger.warning("[UC-8.1] [_minimize_groups] DataFrame is empty")
        return []

    group_compounds = df.groupby("_group")["compoundname"].apply(set).reset_index()
    logger.debug(f"[UC-8.1] [_minimize_groups] Found {len(group_compounds)} groups")

    all_compounds: Set[str] = set(df["compoundname"].unique())
    logger.debug(
        f"[UC-8.1] [_minimize_groups] Total compounds to cover: "
        f"{len(all_compounds)}"
    )
    selected_groups: List[str] = []

    while all_compounds:
        best_group = None
        max_cover = -1

        for _, row in group_compounds.iterrows():
            coverage = len(all_compounds.intersection(row["compoundname"]))
            if coverage > max_cover:
                max_cover = coverage
                best_group = row["_group"]

        if best_group is None or max_cover == 0:
            break

        selected_groups.append(best_group)

        covered = group_compounds.loc[
            group_compounds["_group"] == best_group, "compoundname"
        ].iloc[0]
        all_compounds -= covered

        group_compounds = group_compounds[group_compounds["_group"] != best_group]

    logger.info(f"[UC-8.1] [_minimize_groups] Selected {len(selected_groups)} groups")
    return selected_groups


def _calculate_ko_counts(df: pd.DataFrame) -> Optional[pd.Series]:
    """
    Calculate unique KO counts per compound.

    Returns
    -------
    Optional[pd.Series]
        Series mapping compound name to unique KO count.
    """
    if "ko" not in df.columns:
        return None

    df_ko = df.dropna(subset=["compoundname", "ko"])

    if df_ko.empty:
        return None

    ko_counts = df_ko.groupby("compoundname")["ko"].nunique().rename("_unique_ko_count")

    return ko_counts


def _create_frozenset_figure(
    df: pd.DataFrame, groups: List[str], selected_class: str
) -> go.Figure:
    """
    Create faceted scatter figure from processed data.

    Parameters
    ----------
    df : pd.DataFrame
        Processed data with group labels and KO counts.
    groups : List[str]
        List of minimized group labels.
    selected_class : str
        Selected compound class name.

    Returns
    -------
    go.Figure
        Configured Plotly figure with subplots.
    """
    logger.debug(
        f"[UC-8.1] [_create_frozenset_figure] Creating figure with "
        f"{len(groups)} groups, {len(df)} rows"
    )
    unique_groups = sorted(groups)
    n_groups = len(unique_groups)

    if n_groups == 0:
        logger.error("[UC-8.1] [_create_frozenset_figure] No groups!")
        raise ValueError("No groups to visualize")

    # Create subplots
    fig = make_subplots(
        rows=1,
        cols=n_groups,
        shared_yaxes=True,
        subplot_titles=unique_groups,
        horizontal_spacing=0.03,
    )

    # Get color range
    cmin = int(df["_unique_ko_count"].min())
    cmax = int(df["_unique_ko_count"].max())
    if cmin == cmax and cmax == 0:
        cmax = 1

    # Add traces for each group
    for i, group in enumerate(unique_groups, 1):
        group_df = df[df["_group"] == group]

        fig.add_trace(
            go.Scatter(
                x=group_df["sample"],
                y=group_df["compoundname"],
                mode="markers",
                name=str(group),
                showlegend=False,
                marker=dict(
                    size=10,
                    color=group_df["_unique_ko_count"],
                    colorscale="Greens",
                    cmin=cmin,
                    cmax=cmax,
                    showscale=(i == 1),
                    colorbar=dict(title="Unique<br>KO Count", thickness=15, len=0.8),
                ),
                customdata=group_df[["_unique_ko_count"]].values,
                hovertemplate=(
                    "Sample: %{x}<br>"
                    "Compound: %{y}<br>"
                    "Unique KOs: %{customdata[0]}<extra></extra>"
                ),
            ),
            row=1,
            col=i,
        )

    # Layout
    fig.update_layout(
        title=dict(
            text=f"Minimal Sample-Group Visualization: {selected_class}",
            x=0.5,
            xanchor="center",
            font=dict(size=16),
        ),
        template="simple_white",
        height=600,
        margin=dict(l=150, r=50, t=80, b=50),
        paper_bgcolor="white",
    )

    fig.update_xaxes(tickangle=-45)

    logger.info("[UC-8.1] [_create_frozenset_figure] Figure created OK")
    return fig


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


def _create_info_message(
    message: str, icon_class: str = "bi bi-info-circle"
) -> html.Div:
    """
    Create a user-friendly info message component.

    Parameters
    ----------
    message : str
        Info message text to display.
    icon_class : str, optional
        Bootstrap icon class for the info icon.
        Default: "bi bi-info-circle"

    Returns
    -------
    html.Div
        Styled info alert component with icon and message.
    """
    return html.Div(
        [html.I(className=f"{icon_class} me-2"), html.Span(message)],
        className="alert alert-info d-flex align-items-center mt-3",
        role="alert",
    )
