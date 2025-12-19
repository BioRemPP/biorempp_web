"""
UC-8.6 Callbacks - Pathway-Centric Consortium Design by KO Coverage.

This module implements callback functions for visualizing KO distribution
across samples for consortium design using UpSet plot analysis.

Functions
---------
register_uc_8_6_callbacks
    Register all UC-8.6 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses UpSetStrategy for KO distribution visualization
- Supports HADEG and KEGG databases

Version: 1.0.0
"""

from typing import Optional

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.shared.logging import get_logger

logger = get_logger(__name__)
import os

from src.presentation.components.download_component import sanitize_filename

# =============================================================================
# Helper Functions
# =============================================================================


def _extract_kegg_data(merged_data: dict) -> Optional[pd.DataFrame]:
    """
    Extract KEGG DataFrame from merged-result-store.

    Parameters
    ----------
    merged_data : dict
        Dictionary from merged-result-store containing processed data.

    Returns
    -------
    pd.DataFrame or None
        KEGG DataFrame if found, None otherwise.

    Notes
    -----
    Expected structure:
    {
        'biorempp_df': list[dict],
        'hadeg_df': list[dict],
        'kegg_df': list[dict],  ← This one!
        'toxcsm_df': list[dict],
        ...
    }
    """
    logger.info("[UC-8.6] Extracting KEGG DataFrame from merged data")

    if not merged_data:
        logger.warning("[UC-8.6] No merged data available")
        return None

    logger.debug(f"[UC-8.6] merged_data type: {type(merged_data)}")
    keys_info = (
        list(merged_data.keys()) if isinstance(merged_data, dict) else "Not a dict"
    )
    logger.debug(f"[UC-8.6] merged_data keys: {keys_info}")

    kegg_data = merged_data.get("kegg_df")
    if kegg_data is None:
        logger.warning(
            "[UC-8.6] KEGG DataFrame not found in merged data. "
            f"Available keys: {list(merged_data.keys())}"
        )
        return None

    # Convert from list of dicts to DataFrame
    kegg_df = pd.DataFrame(kegg_data)

    logger.info(
        f"[UC-8.6] Extracted KEGG DataFrame: {len(kegg_df)} rows, "
        f"{len(kegg_df.columns)} columns"
    )
    logger.debug(f"[UC-8.6] KEGG columns: {list(kegg_df.columns)}")
    logger.debug(f"[UC-8.6] KEGG dtypes:\n{kegg_df.dtypes}")

    # Log sample of data
    if len(kegg_df) > 0:
        logger.debug(f"[UC-8.6] KEGG sample (first 3 rows):\n{kegg_df.head(3)}")

    return kegg_df


def _extract_hadeg_data(merged_data: dict) -> Optional[pd.DataFrame]:
    """
    Extract HADEG DataFrame from merged-result-store.

    Parameters
    ----------
    merged_data : dict
        Dictionary from merged-result-store containing processed data.

    Returns
    -------
    pd.DataFrame or None
        HADEG DataFrame if found, None otherwise.

    Notes
    -----
    Expected structure:
    {
        'biorempp_df': list[dict],
        'hadeg_df': list[dict],  ← This one!
        'kegg_df': list[dict],
        ...
    }
    """
    logger.info("[UC-8.6] Extracting HADEG DataFrame from merged data")

    if not merged_data:
        logger.warning("[UC-8.6] No merged data available")
        return None

    logger.debug(f"[UC-8.6] merged_data type: {type(merged_data)}")
    keys_info = (
        list(merged_data.keys()) if isinstance(merged_data, dict) else "Not a dict"
    )
    logger.debug(f"[UC-8.6] merged_data keys: {keys_info}")

    hadeg_data = merged_data.get("hadeg_df")
    if hadeg_data is None:
        logger.warning(
            "[UC-8.6] HADEG DataFrame not found in merged data. "
            f"Available keys: {list(merged_data.keys())}"
        )
        return None

    # Convert from list of dicts to DataFrame
    hadeg_df = pd.DataFrame(hadeg_data)

    logger.info(
        f"[UC-8.6] Extracted HADEG DataFrame: {len(hadeg_df)} rows, "
        f"{len(hadeg_df.columns)} columns"
    )
    logger.debug(f"[UC-8.6] HADEG columns: {list(hadeg_df.columns)}")
    logger.debug(f"[UC-8.6] HADEG dtypes:\n{hadeg_df.dtypes}")

    # Log sample of data
    if len(hadeg_df) > 0:
        logger.debug(f"[UC-8.6] HADEG sample (first 3 rows):\n{hadeg_df.head(3)}")

    return hadeg_df


def _get_unique_pathways(hadeg_df: pd.DataFrame) -> list[str]:
    """
    Extract unique pathway names from HADEG DataFrame.

    Parameters
    ----------
    hadeg_df : pd.DataFrame
        HADEG DataFrame with 'Pathway' column.

    Returns
    -------
    list of str
        Sorted list of unique pathway names.

    Notes
    -----
    Column name: 'Pathway' (case-sensitive based on hadeg_db.csv)
    """
    logger.info("[UC-8.6] Extracting unique pathways from HADEG")

    if "Pathway" not in hadeg_df.columns:
        logger.error(
            f"[UC-8.6] 'Pathway' column not found in HADEG. "
            f"Available columns: {list(hadeg_df.columns)}"
        )
        return []

    # Get unique pathways, remove NaN, sort
    unique_pathways = hadeg_df["Pathway"].dropna().unique().tolist()
    unique_pathways.sort()

    logger.info(f"[UC-8.6] Found {len(unique_pathways)} unique pathways")
    sample_paths = unique_pathways[:5] if len(unique_pathways) > 5 else unique_pathways
    logger.debug(f"[UC-8.6] Sample pathways: {sample_paths}")

    return unique_pathways


def _filter_pathway_data(
    hadeg_df: pd.DataFrame, pathway_name: str
) -> Optional[pd.DataFrame]:
    """
    Filter HADEG DataFrame for a specific pathway.

    Parameters
    ----------
    hadeg_df : pd.DataFrame
        HADEG DataFrame with 'Pathway', 'Gene', 'ko' columns.
    pathway_name : str
        Target pathway name to filter.

    Returns
    -------
    pd.DataFrame or None
        Filtered DataFrame with 'Gene' and 'ko' columns, or None if empty.

    Notes
    -----
    Columns used:
    - Pathway: Filter condition
    - Sample: Sample/gene identifier (equivalent to CLI's 'sample')
    - KO: KEGG Orthology identifier (uppercase)
    """
    logger.info(f"[UC-8.6] Filtering HADEG data for pathway: '{pathway_name}'")

    # Validate columns
    required_cols = ["Pathway", "Sample", "KO"]
    missing_cols = [col for col in required_cols if col not in hadeg_df.columns]

    if missing_cols:
        logger.error(
            f"[UC-8.6] Missing required columns: {missing_cols}. "
            f"Available: {list(hadeg_df.columns)}"
        )
        return None

    # Filter by pathway
    pathway_mask = hadeg_df["Pathway"] == pathway_name
    filtered_df = hadeg_df[pathway_mask][["Sample", "KO"]].copy()

    # Drop NaN values
    filtered_df = filtered_df.dropna()

    # Drop duplicates
    initial_count = len(filtered_df)
    filtered_df = filtered_df.drop_duplicates()
    duplicates_removed = initial_count - len(filtered_df)

    logger.info(
        f"[UC-8.6] Filtered pathway data: {len(filtered_df)} Sample-KO pairs "
        f"({duplicates_removed} duplicates removed)"
    )

    if len(filtered_df) == 0:
        logger.warning(f"[UC-8.6] No data found for pathway '{pathway_name}'")
        return None

    # Log sample
    logger.debug(f"[UC-8.6] Sample filtered data (first 5 rows):\n{filtered_df.head()}")

    return filtered_df


def _build_gene_ko_sets(pathway_df: pd.DataFrame) -> dict[str, set[str]]:
    """
    Build dictionary of KO sets grouped by Sample.

    Parameters
    ----------
    pathway_df : pd.DataFrame
        Filtered DataFrame with 'Sample' and 'KO' columns.

    Returns
    -------
    dict of str to set of str
        Dictionary mapping sample names to sets of KO identifiers.
        Example:
        {'Acinetobacter Baumanii - acb': {'K24119', 'K03386'},
         'Pseudomonas aeruginosa - pae': {'K03387'},
         'Escherichia coli - eco': {'K00496'}}

    Notes
    -----
    Processing steps:
    1. Group by 'Sample' column
    2. For each sample, collect unique KO identifiers
    3. Normalize KO identifiers (uppercase, trim)
    4. Build sets for UpSet analysis
    """
    logger.info("[UC-8.6] Building KO sets grouped by Sample")

    sample_ko_sets = {}

    for sample_name, group in pathway_df.groupby("Sample"):
        # Extract KO values
        ko_values = group["KO"].values

        # Normalize: trim, uppercase, filter NaN
        normalized_kos = {
            str(ko).strip().upper()
            for ko in ko_values
            if pd.notna(ko) and str(ko).strip()
        }

        sample_ko_sets[sample_name] = normalized_kos

        logger.debug(
            f"[UC-8.6] Sample '{sample_name}': " f"{len(normalized_kos)} unique KOs"
        )

    total_samples = len(sample_ko_sets)
    total_ko_entries = sum(len(s) for s in sample_ko_sets.values())
    unique_kos = len(set().union(*sample_ko_sets.values())) if sample_ko_sets else 0

    logger.info(
        f"[UC-8.6] Built KO sets: {total_samples} samples, "
        f"{total_ko_entries} total KO entries, "
        f"{unique_kos} unique KOs across all samples"
    )

    return sample_ko_sets


def _create_error_message(message: str, alert_type: str = "warning") -> html.Div:
    """
    Create styled error/warning message.

    Parameters
    ----------
    message : str
        Message text (supports markdown).
    alert_type : str, optional
        Alert style: 'warning', 'danger', 'info' (default: 'warning').

    Returns
    -------
    html.Div
        Styled message container.
    """
    return html.Div(
        dcc.Markdown(message, className=f"text-{alert_type}"), className="p-4"
    )


# =============================================================================
# Callbacks
# =============================================================================


def register_uc_8_6_callbacks(app, plot_service):
    """
    Register all UC-8.6 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 5 callbacks: panel toggle, database selection, chart clear,
      pathway dropdown population, and UpSet plot rendering
    - Supports dual-database mode (HADEG default, KEGG optional)
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-8.6] Registering callbacks...")

    @app.callback(
        Output("uc-8-6-collapse", "is_open"),
        Input("uc-8-6-collapse-button", "n_clicks"),
        State("uc-8-6-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_8_6_info_panel(n_clicks: int, is_open: bool) -> bool:
        """
        Toggle UC-8.6 informative panel collapse state.

        Parameters
        ----------
        n_clicks : int
            Number of button clicks.
        is_open : bool
            Current collapse state.

        Returns
        -------
        bool
            New collapse state (inverted).
        """
        if n_clicks:
            logger.debug(f"[UC-8.6] Toggling info panel: {is_open} → {not is_open}")
            return not is_open
        return is_open

    @app.callback(
        [Output("uc-8-6-db-hadeg", "outline"), Output("uc-8-6-db-kegg", "outline")],
        [Input("uc-8-6-db-hadeg", "n_clicks"), Input("uc-8-6-db-kegg", "n_clicks")],
        prevent_initial_call=True,
    )
    def toggle_uc_8_6_database_buttons(
        hadeg_clicks: int, kegg_clicks: int
    ) -> tuple[bool, bool]:
        """
        Toggle database selection buttons for UC-8.6.

        Parameters
        ----------
        hadeg_clicks : int
            Number of clicks on HADEG button.
        kegg_clicks : int
            Number of clicks on KEGG button.

        Returns
        -------
        tuple of (bool, bool)
            Outline states for (HADEG, KEGG).
            False = selected, True = not selected.
        """
        from dash import callback_context

        ctx = callback_context
        if not ctx.triggered:
            return False, True  # HADEG selected by default

        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

        if button_id == "uc-8-6-db-hadeg":
            logger.debug("[UC-8.6] Database switched to HADEG")
            return False, True
        elif button_id == "uc-8-6-db-kegg":
            logger.debug("[UC-8.6] Database switched to KEGG")
            return True, False

        return False, True  # Default to HADEG

    @app.callback(
        Output("uc-8-6-chart", "children", allow_duplicate=True),
        [Input("uc-8-6-db-hadeg", "n_clicks"), Input("uc-8-6-db-kegg", "n_clicks")],
        prevent_initial_call=True,
    )
    def clear_chart_on_database_change(
        hadeg_clicks: Optional[int], kegg_clicks: Optional[int]
    ) -> html.Div:
        """
        Clear chart when database is changed.

        Returns empty div to reset visualization state when user
        switches between HADEG and KEGG databases.
        """
        logger.debug("[UC-8.6] Database changed, clearing chart")
        return html.Div(
            html.P(
                "Please select a pathway from the dropdown to generate "
                "the UpSet plot.",
                className="text-muted text-center p-5",
            ),
            className="border rounded p-3",
        )

    @app.callback(
        [
            Output("uc-8-6-pathway-dropdown", "options"),
            Output("uc-8-6-pathway-dropdown", "value"),
            Output("uc-8-6-pathway-help-text", "children"),
        ],
        [
            Input("uc-8-6-accordion-group", "active_item"),
            Input("uc-8-6-db-hadeg", "n_clicks"),
            Input("uc-8-6-db-kegg", "n_clicks"),
        ],
        [
            State("merged-result-store", "data"),
            State("uc-8-6-db-hadeg", "outline"),
            State("uc-8-6-db-kegg", "outline"),
        ],
        prevent_initial_call=True,
    )
    def populate_uc_8_6_pathway_dropdown(
        active_item: Optional[str],
        hadeg_clicks: Optional[int],
        kegg_clicks: Optional[int],
        merged_data: dict,
        hadeg_outline: bool,
        kegg_outline: bool,
    ) -> tuple[list[dict], Optional[str], str]:
        """
        Populate pathway dropdown when accordion is opened or database is changed.

        Parameters
        ----------
        active_item : str or None
            Active accordion item ID ('uc-8-6-accordion' when opened).
        hadeg_clicks : int or None
            Number of clicks on HADEG button.
        kegg_clicks : int or None
            Number of clicks on KEGG button.
        merged_data : dict
            Dictionary from merged-result-store.
        hadeg_outline : bool
            Whether HADEG button is outlined (not selected).
        kegg_outline : bool
            Whether KEGG button is outlined (not selected).

        Returns
        -------
        tuple of (list of dict, str or None, str)
            - Pathway options: [{'label': 'Name', 'value': 'Name'}, ...]
            - Default value: First pathway or None
            - Help text: Database-specific description

        Notes
        -----
        Triggered when:
        - Accordion is opened (initial load with HADEG default)
        - Database button is clicked (switch between HADEG/KEGG)

        Database Support:
        - HADEG: 58 pathways for degradation analysis (default)
        - KEGG: 19 pathways for general metabolism
        """
        from dash import callback_context

        logger.info("[UC-8.6] populate_pathway_dropdown callback triggered")

        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate

        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        logger.debug(f"[UC-8.6] Triggered by: {trigger_id}")

        # Determine selected database based on trigger OR current state
        # Priority: If triggered by button click, use that button
        # Otherwise, use current state (outline values)
        if trigger_id == "uc-8-6-db-hadeg":
            selected_db_key = "hadeg_df"
            db_name = "HADEG"
        elif trigger_id == "uc-8-6-db-kegg":
            selected_db_key = "kegg_df"
            db_name = "KEGG"
        elif not hadeg_outline:
            # HADEG is selected (outline=False)
            selected_db_key = "hadeg_df"
            db_name = "HADEG"
        elif not kegg_outline:
            # KEGG is selected (outline=False)
            selected_db_key = "kegg_df"
            db_name = "KEGG"
        else:
            # Default to HADEG if no button selected
            selected_db_key = "hadeg_df"
            db_name = "HADEG"

        # Set help text based on selected database
        if db_name == "HADEG":
            help_text = (
                "HADEG Database: Pathways for biodegradation and "
                "environmental remediation. Analyze KO distribution across "
                "samples to design consortia for degradation of specific "
                "compounds."
            )
        else:  # KEGG
            help_text = (
                "KEGG Database: General metabolic pathways. Analyze KO "
                "distribution to understand functional complementarity and "
                "redundancy in metabolic processes."
            )

        logger.info(f"[UC-8.6] Selected database: {db_name}")

        # Extract database data
        if selected_db_key == "hadeg_df":
            df = _extract_hadeg_data(merged_data)
        else:  # kegg_df
            df = _extract_kegg_data(merged_data)

        if df is None or len(df) == 0:
            logger.warning(f"[UC-8.6] {db_name} data not available")
            return (
                [],
                None,
                f"⚠️ {db_name} data not available. Please load data " f"first.",
            )

        # Get unique pathways
        unique_pathways = _get_unique_pathways(df)

        if not unique_pathways:
            logger.warning(f"[UC-8.6] No pathways found in {db_name} data")
            return [], None, f"⚠️ No pathways found in {db_name} database."

        # Create dropdown options
        pathway_options = [
            {"label": pathway, "value": pathway} for pathway in unique_pathways
        ]

        # Don't set default value - let user choose explicitly
        default_value = None

        logger.info(
            f"[UC-8.6] Dropdown populated with {len(pathway_options)} "
            f"{db_name} pathways, no default selection (user must choose)"
        )

        return pathway_options, default_value, help_text

    @app.callback(
        Output("uc-8-6-chart", "children"),
        Input("uc-8-6-pathway-dropdown", "value"),
        [
            State("merged-result-store", "data"),
            State("uc-8-6-db-hadeg", "outline"),
            State("uc-8-6-db-kegg", "outline"),
        ],
        prevent_initial_call=True,
    )
    def render_uc_8_6(
        selected_pathway: Optional[str],
        merged_data: dict,
        hadeg_outline: bool,
        kegg_outline: bool,
    ) -> html.Div:
        """
        Generate UpSet plot for selected pathway from selected database.

        Parameters
        ----------
        selected_pathway : str or None
            Selected pathway name from dropdown.
        merged_data : dict
            Dictionary from merged-result-store.
        hadeg_outline : bool
            Whether HADEG button is outlined (not selected).
        kegg_outline : bool
            Whether KEGG button is outlined (not selected).

        Returns
        -------
        html.Div
            Container with UpSet plot or error message.

        Notes
        -----
        Rendering logic:
        1. Triggered by pathway dropdown selection
        2. Determines selected database (HADEG or KEGG)
        3. Extracts data from appropriate database
        4. Filters data for selected pathway
        5. Builds KO sets grouped by Sample
        6. Creates UpSet DataFrame format
        7. Passes to PlotService for visualization

        Database Support:
        - HADEG: Biodegradation pathways
        - KEGG: General metabolic pathways

        Error Handling:
        - No pathway selected → Prevent update
        - No data → Error message
        - Missing columns → Error message
        - No KOs for pathway → Warning message
        - Plot generation error → Error message with details
        """
        logger.info("[UC-8.6] render_uc_8_6 callback triggered")
        logger.debug(f"[UC-8.6] Selected pathway: '{selected_pathway}'")

        # Validate pathway selection
        if not selected_pathway:
            logger.debug("[UC-8.6] No pathway selected, preventing update")
            raise PreventUpdate

        # Determine selected database
        if not hadeg_outline:
            selected_db_key = "hadeg_df"
            db_name = "HADEG"
        elif not kegg_outline:
            selected_db_key = "kegg_df"
            db_name = "KEGG"
        else:
            # Default to HADEG
            selected_db_key = "hadeg_df"
            db_name = "HADEG"

        logger.info(
            f"[UC-8.6] Generating UpSet plot for pathway '{selected_pathway}' "
            f"from {db_name} database"
        )

        # Extract data from selected database
        if selected_db_key == "hadeg_df":
            df = _extract_hadeg_data(merged_data)
        else:  # kegg_df
            df = _extract_kegg_data(merged_data)

        if df is None or len(df) == 0:
            logger.error(f"[UC-8.6] {db_name} data not available")
            return _create_error_message(
                f"❌ **Error**: {db_name} data not available. Please upload "
                f"and process data first.",
                "danger",
            )

        # Filter data for selected pathway
        pathway_df = _filter_pathway_data(df, selected_pathway)

        if pathway_df is None or len(pathway_df) == 0:
            logger.warning(
                f"[UC-8.6] No data found for pathway '{selected_pathway}' "
                f"in {db_name} database"
            )
            return _create_error_message(
                f"⚠️ **No data available** for pathway "
                f"**{selected_pathway}** in {db_name} database.\n\n"
                f"This pathway may not be present in the {db_name} dataset, "
                f"or no KOs are associated with it. "
                f"Please select a different pathway.",
                "warning",
            )

        # Build KO sets grouped by Sample
        sample_ko_sets = _build_gene_ko_sets(pathway_df)

        if not sample_ko_sets:
            logger.error("[UC-8.6] Failed to build Sample-KO sets")
            return _create_error_message(
                "❌ **Error**: Failed to process KO data. Please check the "
                "dataset format and try again.",
                "danger",
            )

        # Create UpSet DataFrame from sets
        # Format: [{'category': sample_name, 'identifier': ko_id}, ...]
        upset_data = []
        for sample_name, ko_set in sample_ko_sets.items():
            for ko_id in ko_set:
                upset_data.append({"category": sample_name, "identifier": ko_id})

        upset_df = pd.DataFrame(upset_data)

        logger.info(
            f"[UC-8.6] Created UpSet DataFrame: {len(upset_df)} rows, "
            f"{len(sample_ko_sets)} samples, "
            f"{len(set(upset_df['identifier']))} unique KOs"
        )
        logger.debug(
            f"[UC-8.6] UpSet DataFrame sample (first 10 rows):\n" f"{upset_df.head(10)}"
        )

        # Generate plot using PlotService
        try:
            logger.info("[UC-8.6] Calling PlotService.generate_plot...")

            # Instantiate PlotService

            # Generate plot
            fig = plot_service.generate_plot(data=upset_df, use_case_id="UC-8.6")

            logger.info("[UC-8.6] Plot generated successfully")

            # Build a short, safe basename for the exported filename
            pathway_safe = str(selected_pathway).replace(" ", "_")
            db_short = db_name.lower()
            try:
                suggested = sanitize_filename(
                    "UC-8.6", f"upset_{db_short}_{pathway_safe}", "png"
                )
            except Exception:
                suggested = f"upset_{db_short}_{pathway_safe}.png"

            base_filename = os.path.splitext(suggested)[0]

            return html.Div(
                [
                    dcc.Graph(
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
                ]
            )

        except Exception as e:
            logger.error(f"[UC-8.6] Error generating plot: {str(e)}", exc_info=True)
            return _create_error_message(
                f"❌ **Error generating plot**: {str(e)}\n\n"
                f"Please check the logs for more details.",
                "danger",
            )

    logger.info("[UC-8.6] Callbacks registered successfully")
