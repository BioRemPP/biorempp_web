"""
UC-2.5 Callbacks - Distribution of KO Across Samples.

This module implements callback functions for visualizing statistical
distribution of unique KO counts across samples and databases using
box-scatter plots.

Functions
---------
register_uc_2_5_callbacks
    Register all UC-2.5 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Supports BioRemPP, HADEG, and KEGG databases
- Uses BoxScatterStrategy for distribution visualization

Version: 1.0.0
"""

import os
from typing import Any, Optional, Tuple

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename
from src.shared.logging import get_logger

logger = get_logger(__name__)


def _create_error_message(
    message: str, icon: str = "fas fa-exclamation-circle"
) -> html.Div:
    """
    Create standardized error message component.

    Parameters
    ----------
    message : str
        Error message to display.
    icon : str, optional
        FontAwesome icon class (default: "fas fa-exclamation-circle").

    Returns
    -------
    html.Div
        Bootstrap alert component with error message.
    """
    return html.Div(
        [
            html.Div(
                [
                    html.I(className=f"{icon} fa-2x text-danger mb-3"),
                    html.P(message, className="mb-0"),
                ],
                className="text-center p-4",
            )
        ],
        className="alert alert-danger border border-danger",
    )


def _resolve_column_name(
    df: pd.DataFrame, possible_names: list[str], column_description: str
) -> str:
    """
    Resolve column name from list of possible variations.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to search for columns.
    possible_names : list of str
        List of possible column names (checked in order).
    column_description : str
        Human-readable description for error message.

    Returns
    -------
    str
        First matching column name found in DataFrame.

    Raises
    ------
    KeyError
        If no matching column found.
    """
    for col_name in possible_names:
        if col_name in df.columns:
            return col_name

    # No match found - raise error with suggestions
    raise KeyError(
        f"Could not find {column_description} column. "
        f"Tried: {possible_names}. "
        f"Available columns: {df.columns.tolist()}"
    )


def _is_chart_rendered(container_content: Any) -> bool:
    """
    Check if chart is already rendered in container.

    Parameters
    ----------
    container_content : Any
        Current content of chart container.

    Returns
    -------
    bool
        True if chart (dcc.Graph) is rendered, False otherwise.
    """
    if container_content is None:
        return False

    # Check if it's a dcc.Graph component
    if hasattr(container_content, "type"):
        return container_content.type == "Graph"

    return False


def register_uc_2_5_callbacks(app, plot_service) -> None:
    """
    Register UC-2.5 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers panel toggle, database selection, and chart rendering callbacks
    - Refer to official documentation for processing logic details
    """

    @app.callback(
        Output("uc-2-5-collapse", "is_open"),
        Input("uc-2-5-collapse-button", "n_clicks"),
        State("uc-2-5-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_2_5_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """
        Toggle UC-2.5 information panel visibility.

        Parameters
        ----------
        n_clicks : int, optional
            Number of clicks on collapse button.
        is_open : bool
            Current collapse state.

        Returns
        -------
        bool
            New collapse state (toggled).
        """
        if n_clicks:
            logger.debug(
                f"UC-2.5: Toggling info panel "
                f"(current state: {'open' if is_open else 'closed'})"
            )
            return not is_open
        return is_open

    @app.callback(
        [
            Output("uc-2-5-db-biorempp", "outline"),
            Output("uc-2-5-db-hadeg", "outline"),
            Output("uc-2-5-db-kegg", "outline"),
        ],
        [
            Input("uc-2-5-db-biorempp", "n_clicks"),
            Input("uc-2-5-db-hadeg", "n_clicks"),
            Input("uc-2-5-db-kegg", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def toggle_uc_2_5_database(
        biorempp_clicks: Optional[int],
        hadeg_clicks: Optional[int],
        kegg_clicks: Optional[int],
    ) -> Tuple[bool, bool, bool]:
        """
        Toggle database button selection for UC-2.5.

        Parameters
        ----------
        biorempp_clicks : int, optional
            Number of clicks on BioRemPP button.
        hadeg_clicks : int, optional
            Number of clicks on HADEG button.
        kegg_clicks : int, optional
            Number of clicks on KEGG button.

        Returns
        -------
        tuple
            (biorempp_outline, hadeg_outline, kegg_outline)
            False = selected, True = not selected.

        Notes
        -----
        - Implements mutually exclusive button selection
        - Only one database selected at a time
        """
        from dash import ctx

        # Determine which button was clicked
        if not ctx.triggered:
            raise PreventUpdate

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        logger.debug(f"UC-2.5: Database button clicked: {button_id}")

        # Return outline states (False = selected/filled, True = outline)
        if button_id == "uc-2-5-db-biorempp":
            return False, True, True  # BioRemPP selected
        elif button_id == "uc-2-5-db-hadeg":
            return True, False, True  # HADEG selected
        elif button_id == "uc-2-5-db-kegg":
            return True, True, False  # KEGG selected

        # Default: BioRemPP selected
        return False, True, True

    @app.callback(
        Output("uc-2-5-chart-container", "children"),
        [
            Input("uc-2-5-accordion", "active_item"),
            Input("uc-2-5-db-biorempp", "n_clicks"),
            Input("uc-2-5-db-hadeg", "n_clicks"),
            Input("uc-2-5-db-kegg", "n_clicks"),
        ],
        [
            State("merged-result-store", "data"),
            State("uc-2-5-chart-container", "children"),
        ],
        prevent_initial_call=True,
    )
    def render_uc_2_5(
        accordion_active: Optional[str],
        biorempp_clicks: Optional[int],
        hadeg_clicks: Optional[int],
        kegg_clicks: Optional[int],
        merged_data: Optional[dict],
        current_container: Any,
    ) -> Any:
        """
        Render UC-2.5 box-scatter plot for selected database.

        Parameters
        ----------
        accordion_active : str, optional
            Active accordion item ID.
        biorempp_clicks : int, optional
            Number of clicks on BioRemPP button.
        hadeg_clicks : int, optional
            Number of clicks on HADEG button.
        kegg_clicks : int, optional
            Number of clicks on KEGG button.
        merged_data : dict, optional
            Merged analysis results from data store.
        current_container : Any
            Current chart container content.

        Returns
        -------
        dcc.Graph or html.Div
            Chart component or error message.

        Raises
        ------
        PreventUpdate
            If no trigger or data unavailable.

        Notes
        -----
        - Accordion open triggers initial render with BioRemPP (default)
        - Button click updates chart with selected database
        - Aggregates unique KO counts per sample
        - Calculates ranks within database
        - Generates box-scatter plot via BoxScatterStrategy
        """
        from dash import ctx

        # Determine which component triggered the callback
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

        logger.debug(f"UC-2.5 triggered by: {trigger_id}")

        # Map button ID to database name and key
        database_map = {
            "uc-2-5-db-biorempp": ("BioRemPP", "biorempp_df"),
            "uc-2-5-db-hadeg": ("HADEG", "hadeg_df"),
            "uc-2-5-db-kegg": ("KEGG", "kegg_df"),
        }

        # Determine selected database based on trigger
        if trigger_id in database_map:
            # Button clicked - use clicked button
            selected_database, db_key = database_map[trigger_id]
        elif trigger_id == "uc-2-5-accordion":
            # Accordion opened - default to BioRemPP
            selected_database, db_key = "BioRemPP", "biorempp_df"
        else:
            logger.warning(f"UC-2.5: Unknown trigger: {trigger_id}")
            raise PreventUpdate

        # Rendering decision logic
        accordion_opened = (
            trigger_id == "uc-2-5-accordion" and accordion_active == "uc-2-5-item"
        )
        database_changed = trigger_id in database_map

        should_render = accordion_opened or database_changed

        if not should_render:
            logger.debug("UC-2.5: Render conditions not met")
            raise PreventUpdate

        logger.info(
            f"UC-2.5: Rendering plot for database: {selected_database} "
            f"(key: {db_key})"
        )

        # Validate data availability
        if not merged_data:
            logger.warning("UC-2.5: No data available in merged-result-store")
            return _create_error_message(
                "No data available. Please process data first.",
                icon="fas fa-exclamation-triangle",
            )

        try:
            # Extract DataFrame from store
            if not isinstance(merged_data, dict) or db_key not in merged_data:
                error_msg = (
                    f"Data store missing '{db_key}'. "
                    f"Available keys: {list(merged_data.keys())}"
                )
                logger.error(f"UC-2.5: {error_msg}")
                return _create_error_message(
                    f"Database '{selected_database}' not found in data store.",
                    icon="fas fa-database",
                )

            df = pd.DataFrame(merged_data[db_key])

            logger.info(
                f"UC-2.5: Loaded {db_key} - "
                f"Shape: {df.shape}, Columns: {df.columns.tolist()}"
            )

            # Resolve column names (flexible naming)
            sample_col = _resolve_column_name(df, ["Sample", "sample"], "sample")
            ko_col = _resolve_column_name(df, ["KO", "ko", "Gene"], "KO/gene")

            logger.debug(
                f"UC-2.5: Resolved columns - " f"sample: '{sample_col}', ko: '{ko_col}'"
            )

            # Prepare data for aggregation
            df_clean = df[[sample_col, ko_col]].copy()

            # Clean data
            df_clean[sample_col] = (
                df_clean[sample_col].fillna("").astype(str).str.strip()
            )
            df_clean[ko_col] = (
                df_clean[ko_col].fillna("").astype(str).str.strip().str.upper()
            )

            # Remove empty rows
            df_clean = df_clean[(df_clean[sample_col] != "") & (df_clean[ko_col] != "")]

            # Remove duplicate sample-KO combinations
            df_clean = df_clean.drop_duplicates(subset=[sample_col, ko_col])

            logger.debug(f"UC-2.5: After cleaning - {len(df_clean)} valid rows")

            if df_clean.empty:
                logger.warning(f"UC-2.5: No valid data after cleaning for {db_key}")
                return _create_error_message(
                    f"No valid sample-KO data found in "
                    f"{selected_database} database.",
                    icon="fas fa-filter",
                )

            # Aggregate: COUNT(DISTINCT ko) per sample
            ko_counts = (
                df_clean.groupby(sample_col, as_index=False)[ko_col]
                .nunique()
                .rename(columns={sample_col: "sample", ko_col: "unique_ko_count"})
            )

            # Ensure numeric type
            ko_counts["unique_ko_count"] = (
                pd.to_numeric(ko_counts["unique_ko_count"], errors="coerce")
                .fillna(0)
                .astype(int)
            )

            # Calculate rank (1 = highest count)
            ko_counts["rank"] = (
                ko_counts["unique_ko_count"]
                .rank(method="min", ascending=False)
                .astype(int)
            )

            # Sort by unique_ko_count descending
            ko_counts = ko_counts.sort_values(
                "unique_ko_count", ascending=False
            ).reset_index(drop=True)

            logger.info(
                f"UC-2.5: Aggregated {len(ko_counts)} samples - "
                f"Range: {ko_counts['unique_ko_count'].min()}-"
                f"{ko_counts['unique_ko_count'].max()} KOs"
            )

            # Generate plot via PlotService
            fig = plot_service.generate_plot(
                use_case_id="UC-2.5",
                data=ko_counts,
                filters={"database": selected_database},
                force_refresh=False,
            )

            logger.info(f"UC-2.5: Plot generated successfully for {selected_database}")

            # Create chart component
            try:
                suggested = sanitize_filename("UC-2.5", "ko_distribution", "png")
                base_filename = os.path.splitext(suggested)[0]
            except Exception:
                base_filename = "uc_2_5_ko_distribution"

            chart_component = dcc.Graph(
                figure=fig,
                id="uc-2-5-box-scatter-chart",
                config={
                    "displayModeBar": True,
                    "toImageButtonOptions": {
                        "format": "png",
                        "filename": base_filename,
                        "height": 900,
                        "width": 1400,
                        "scale": 2,
                    },
                },
            )

            return chart_component

        except KeyError as e:
            logger.error(f"UC-2.5: Column resolution error: {e}", exc_info=True)
            return _create_error_message(
                f"Required column not found: {str(e)}. "
                f"Expected 'Sample'/'sample' and 'KO'/'ko'/'Gene' columns.",
                icon="fas fa-table",
            )

        except ValueError as e:
            logger.error(f"UC-2.5: Data validation error: {e}", exc_info=True)
            return _create_error_message(
                f"Data validation failed: {str(e)}", icon="fas fa-exclamation-triangle"
            )

        except Exception as e:
            logger.error(f"UC-2.5: Unexpected error: {e}", exc_info=True)
            return _create_error_message(
                "Error generating chart. Please check logs for details.",
                icon="fas fa-exclamation-circle",
            )


# ============================================================
# End of UC-2.5 Callbacks
# ============================================================
