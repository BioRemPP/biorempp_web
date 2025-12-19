"""
UC-8.7 Callbacks - Intersection of Genes Across Samples.

This module implements callback functions for visualizing multi-sample gene set
intersections using UpSet plot analysis.

Functions
---------
register_uc_8_7_callbacks
    Register all UC-8.7 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses UpSetStrategy for gene set intersection visualization
- Supports BioRemPP, HADEG, and KEGG databases

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


def _extract_biorempp_data(merged_data: dict) -> Optional[pd.DataFrame]:
    """
    Extract BioRemPP DataFrame from merged-result-store.

    Parameters
    ----------
    merged_data : dict
        Dictionary from merged-result-store containing processed data.

    Returns
    -------
    pd.DataFrame or None
        BioRemPP DataFrame if found, None otherwise.

    Notes
    -----
    Expected structure:
    {
        'biorempp_df': list[dict],  ← This one!
        'hadeg_df': list[dict],
        'kegg_df': list[dict],
        ...
    }
    """
    logger.info("[UC-8.7] Extracting BioRemPP DataFrame from merged data")

    if not merged_data:
        logger.warning("[UC-8.7] No merged data available")
        return None

    logger.debug(f"[UC-8.7] merged_data type: {type(merged_data)}")
    keys_info = (
        list(merged_data.keys()) if isinstance(merged_data, dict) else "Not a dict"
    )
    logger.debug(f"[UC-8.7] merged_data keys: {keys_info}")

    biorempp_data = merged_data.get("biorempp_df")
    if biorempp_data is None:
        logger.warning(
            "[UC-8.7] BioRemPP DataFrame not found in merged data. "
            f"Available keys: {list(merged_data.keys())}"
        )
        return None

    # Convert from list of dicts to DataFrame
    biorempp_df = pd.DataFrame(biorempp_data)

    logger.info(
        f"[UC-8.7] Extracted BioRemPP DataFrame: {len(biorempp_df)} rows, "
        f"{len(biorempp_df.columns)} columns"
    )
    logger.debug(f"[UC-8.7] BioRemPP columns: {list(biorempp_df.columns)}")
    logger.debug(f"[UC-8.7] BioRemPP dtypes:\n{biorempp_df.dtypes}")

    # Log sample of data
    if len(biorempp_df) > 0:
        logger.debug(f"[UC-8.7] BioRemPP sample (first 3 rows):\n{biorempp_df.head(3)}")

    return biorempp_df


def _prepare_upsetplot_data(
    biorempp_df: pd.DataFrame, selected_samples: list
) -> pd.DataFrame:
    """
    Process BioRemPP data for UpSet plot intersection analysis.

    This function filters and prepares biological interaction data for
    UpSet plot visualization, ensuring data quality and proper structure
    for multi-sample set intersection analysis.

    Parameters
    ----------
    biorempp_df : pd.DataFrame
        BioRemPP DataFrame containing sample-KO associations.
        Required columns: 'Sample', 'KO'
    selected_samples : list of str
        Sample identifiers to include in the intersection analysis.

    Returns
    -------
    pd.DataFrame
        Processed DataFrame containing unique sample-KO pairs.
        Ready for UpSet plot generation.

    Raises
    ------
    ValueError
        If required columns ('Sample', 'KO') are missing.

    Notes
    -----
    Processing steps:
    1. Validates presence of required columns
    2. Filters data to include only selected samples
    3. Removes duplicate sample-KO pairs to ensure uniqueness
    4. Returns processed DataFrame ready for UpSet plot generation

    Based on CLI reference: docs/CLI_UC/8.7/processing.py
    """
    logger.info("[UC-8.7] Preparing data for UpSet plot...")

    # Column verification
    required_cols = {"Sample", "KO"}
    if not required_cols.issubset(biorempp_df.columns):
        missing = required_cols - set(biorempp_df.columns)
        raise ValueError(f"Missing required column(s): {missing}")

    logger.info(f"[UC-8.7] Filtering for {len(selected_samples)} selected samples...")
    filtered_df = biorempp_df[biorempp_df["Sample"].isin(selected_samples)]

    logger.info("[UC-8.7] Dropping duplicate sample/KO pairs...")
    unique_ko_df = filtered_df.drop_duplicates(subset=["Sample", "KO"])

    logger.info(f"[UC-8.7] Returning DataFrame with {len(unique_ko_df)} rows")
    return unique_ko_df


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


def register_uc_8_7_callbacks(app, plot_service):
    """
    Register all UC-8.7 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 3 callbacks: panel toggle, sample dropdown population,
      and UpSet plot rendering
    - Requires minimum 2 samples for UpSet plot generation
    - Refer to official documentation for processing logic details
    """
    logger.info("[UC-8.7] Registering callbacks...")

    @app.callback(
        Output("uc-8-7-collapse", "is_open"),
        Input("uc-8-7-collapse-button", "n_clicks"),
        State("uc-8-7-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_8_7_info_panel(n_clicks: int, is_open: bool) -> bool:
        """
        Toggle UC-8.7 informative panel collapse state.

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
            logger.debug(f"[UC-8.7] Toggling info panel: {is_open} → {not is_open}")
            return not is_open
        return is_open

    @app.callback(
        Output("uc-8-7-sample-dropdown", "options"),
        Input("uc-8-7-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def populate_uc_8_7_sample_dropdown(
        active_item: Optional[str], merged_data: dict
    ) -> list[dict]:
        """
        Populate sample dropdown when accordion is opened.

        Parameters
        ----------
        active_item : str or None
            Active accordion item ID ('uc-8-7-accordion' when opened).
        merged_data : dict
            Dictionary from merged-result-store.

        Returns
        -------
        list of dict
            Sample options: [{'label': 'Name', 'value': 'Name'}, ...]

        Notes
        -----
        Triggered when accordion is opened.
        Extracts unique sample identifiers from BioRemPP database.
        """
        logger.info("[UC-8.7] populate_sample_dropdown callback triggered")
        logger.debug(f"[UC-8.7] active_item: {active_item}")

        # Only populate when accordion is opened
        if active_item != "uc-8-7-accordion":
            logger.debug("[UC-8.7] Accordion not opened, preventing update")
            raise PreventUpdate

        logger.info("[UC-8.7] Accordion opened, populating sample dropdown...")

        # Extract BioRemPP data
        biorempp_df = _extract_biorempp_data(merged_data)
        if biorempp_df is None or biorempp_df.empty:
            logger.error("[UC-8.7] No BioRemPP data available")
            return []

        # Verify required column exists
        if "Sample" not in biorempp_df.columns:
            logger.error(
                f"[UC-8.7] 'Sample' column not found. "
                f"Available columns: {list(biorempp_df.columns)}"
            )
            return []

        # Extract unique sample names
        samples = biorempp_df["Sample"].dropna().unique()
        samples = sorted([s for s in samples if s and str(s).strip()])

        logger.info(f"[UC-8.7] Found {len(samples)} unique samples: {samples}")

        # Create dropdown options
        options = [{"label": sample, "value": sample} for sample in samples]

        logger.info(f"[UC-8.7] Returning {len(options)} dropdown options")

        return options

    @app.callback(
        Output("uc-8-7-chart", "children"),
        Input("uc-8-7-sample-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_8_7(selected_samples: Optional[list], merged_data: dict) -> html.Div:
        """
        Generate UpSet plot for selected samples.

        Parameters
        ----------
        selected_samples : list of str or None
            Selected sample identifiers from dropdown.
        merged_data : dict
            Dictionary from merged-result-store.

        Returns
        -------
        html.Div
            Container with UpSet plot or error message.

        Notes
        -----
        Rendering logic:
        1. Triggered by sample dropdown selection
        2. Validates minimum 2 samples selected
        3. Extracts sample-KO associations from BioRemPP database
        4. Builds KO sets for each selected sample
        5. Creates UpSet plot data structure
        6. Passes to PlotService for visualization

        Error Handling:
        - Less than 2 samples → Error message
        - No data → Error message
        - Missing columns → Error message
        - Plot generation error → Error message with details

        Based on CLI reference: docs/CLI_UC/8.7/plot.py
        """
        logger.info("[UC-8.7] render_uc_8_7 callback triggered")
        logger.debug(f"[UC-8.7] Selected samples: {selected_samples}")

        # Validate input
        if not selected_samples or len(selected_samples) < 2:
            logger.warning(
                f"[UC-8.7] Insufficient samples selected: "
                f"{len(selected_samples) if selected_samples else 0}"
            )
            return _create_error_message(
                "❌ **Error**: Please select at least **2 samples** to "
                "generate the UpSet plot.\n\n"
                "The UpSet plot requires multiple samples to show "
                "meaningful intersections. Select 2 or more samples from "
                "the dropdown above.",
                "warning",
            )

        logger.info(
            f"[UC-8.7] Generating UpSet plot for {len(selected_samples)} "
            f"samples: {selected_samples}"
        )

        try:
            # Extract BioRemPP data
            biorempp_df = _extract_biorempp_data(merged_data)
            if biorempp_df is None or biorempp_df.empty:
                logger.error("[UC-8.7] No BioRemPP data available")
                return _create_error_message(
                    "❌ **Error**: No data available.\n\n"
                    "The merged result store does not contain BioRemPP data. "
                    "Please ensure data has been properly loaded.",
                    "danger",
                )

            # Prepare data for UpSet plot
            filtered_df = _prepare_upsetplot_data(biorempp_df, selected_samples)

            if filtered_df.empty:
                logger.warning(
                    f"[UC-8.7] No data found for selected samples: "
                    f"{selected_samples}"
                )
                return _create_error_message(
                    "⚠️ **Warning**: No data found for selected samples.\n\n"
                    f"The selected samples ({', '.join(selected_samples)}) "
                    "do not have any KO associations in the database.",
                    "warning",
                )

            logger.info(
                f"[UC-8.7] Filtered data: {len(filtered_df)} unique " "sample-KO pairs"
            )

            # Build KO memberships (which samples have which KOs)
            # Format: {KO_identifier: [sample1, sample2, ...]}
            logger.info("[UC-8.7] Generating KO to sample memberships...")
            memberships = (
                filtered_df.groupby("KO")["Sample"]
                .apply(lambda x: list(set(x)))
                .to_dict()
            )

            if not memberships:
                logger.error("[UC-8.7] No valid KO/sample memberships found")
                return _create_error_message(
                    "❌ **Error**: No valid gene associations found.\n\n"
                    "Unable to build KO memberships for the selected samples.",
                    "danger",
                )

            logger.info(f"[UC-8.7] Generated memberships for {len(memberships)} KOs")
            logger.debug(
                f"[UC-8.7] Sample memberships (first 3): "
                f"{dict(list(memberships.items())[:3])}"
            )

            # Prepare data for UpSet plot strategy
            # Format: [{category: sample, identifier: ko}, ...]
            upset_data = []
            for ko, samples in memberships.items():
                for sample in samples:
                    upset_data.append({"category": sample, "identifier": ko})

            # Convert to DataFrame (required by PlotService)
            upset_df = pd.DataFrame(upset_data)

            logger.info(
                f"[UC-8.7] Created UpSet DataFrame: {len(upset_df)} rows, "
                f"{len(selected_samples)} samples, "
                f"{len(memberships)} unique KOs"
            )
            logger.debug(
                f"[UC-8.7] UpSet DataFrame sample (first 10 rows):\n"
                f"{upset_df.head(10)}"
            )

            # Generate plot using PlotService
            logger.info("[UC-8.7] Calling PlotService to generate UpSet plot...")

            fig = plot_service.generate_plot(data=upset_df, use_case_id="UC-8.7")

            if fig is None:
                logger.error("[UC-8.7] PlotService returned None")
                return _create_error_message(
                    "❌ **Error**: Plot generation failed.\n\n"
                    "PlotService returned None. Check logs for details.",
                    "danger",
                )

            logger.info("[UC-8.7] [OK] UpSet plot generated successfully")

            # Prepare safe filename based on selected samples (use first 3 names)
            sample_label_parts = [
                str(s).replace(" ", "_") for s in selected_samples[:3]
            ]
            sample_label = "-".join(sample_label_parts)
            try:
                suggested = sanitize_filename(
                    "UC-8.7", f"samples_{len(selected_samples)}_{sample_label}", "png"
                )
            except Exception:
                suggested = f"samples_{len(selected_samples)}_{sample_label}.png"

            base_filename = os.path.splitext(suggested)[0]

            # Return plot in a Graph component with canonical filename
            return html.Div(
                dcc.Graph(
                    id="uc-8-7-upset-plot",
                    figure=fig,
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "modeBarButtonsToRemove": ["lasso2d", "select2d"],
                        "toImageButtonOptions": {
                            "format": "png",
                            "filename": base_filename,
                            "height": 800,
                            "width": 1000,
                            "scale": 2,
                        },
                    },
                ),
                className="mt-3",
            )

        except ValueError as ve:
            logger.error(f"[UC-8.7] ValueError: {ve}", exc_info=True)
            return _create_error_message(
                f"❌ **Validation Error**: {str(ve)}\n\n"
                "Please check your data and try again.",
                "danger",
            )

        except Exception as e:
            logger.error(
                f"[UC-8.7] Unexpected error generating plot: {e}", exc_info=True
            )
            return _create_error_message(
                f"❌ **Error**: Plot generation failed.\n\n"
                f"**Details**: {str(e)}\n\n"
                "Please check the console logs for more information.",
                "danger",
            )

    logger.info("[UC-8.7] Callbacks registered successfully")
