"""
UC-8.4 Callbacks - Pathway Completeness Scorecard for HADEG Pathways.

This module implements callback functions for visualizing HADEG pathway
completeness through heatmap scorecard analysis.

Functions
---------
register_uc_8_4_callbacks
    Register all UC-8.4 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses HeatmapScoredStrategy for pathway completeness visualization
- HADEG database REQUIRED

Version: 1.0.0
"""

import logging
from typing import Any, Dict, Optional

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

logger = logging.getLogger(__name__)
import os

from src.presentation.components.download_component import sanitize_filename


def register_uc_8_4_callbacks(app, plot_service) -> None:
    """
    Register all callbacks for UC-8.4.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers information panel toggle and heatmap rendering callbacks
    - Refer to official documentation for processing logic details
    """
    logger.info("Registering UC-8.4 callbacks")

    @app.callback(
        Output("uc-8-4-collapse", "is_open"),
        Input("uc-8-4-collapse-button", "n_clicks"),
        State("uc-8-4-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_8_4_info_panel(n_clicks: Optional[int], is_open: bool) -> bool:
        """
        Toggle UC-8.4 information panel visibility.

        Parameters
        ----------
        n_clicks : int, optional
            Number of times collapse button has been clicked.
        is_open : bool
            Current state of collapse component.

        Returns
        -------
        bool
            New state of collapse component (True = open, False = closed).
        """
        if n_clicks:
            logger.debug(f"UC-8.4 info panel toggled. New state: {not is_open}")
            return not is_open
        return is_open

    @app.callback(
        Output("uc-8-4-chart", "children"),
        Input("uc-8-4-accordion-group", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_8_4(
        active_item: Optional[str], merged_data: Optional[Dict[str, Any]]
    ) -> html.Div:
        """
        Render UC-8.4 heatmap scorecard when accordion is activated.

        Parameters
        ----------
        active_item : str, optional
            ID of currently active accordion item.
        merged_data : dict, optional
            Dictionary containing 'hadeg_df' key.

        Returns
        -------
        html.Div
            Container with loading spinner and heatmap or error message.

        Raises
        ------
        PreventUpdate
            If accordion not active or data not ready.
        ValueError
            If required columns are missing or data invalid.

        Notes
        -----
        - Extracts HADEG DataFrame and maps column names flexibly
        - Calculates completeness scores: (sample KOs / pathway KOs) × 100%
        - Generates heatmap with samples (rows) × pathways (columns)
        - Uses PlotService with HeatmapScoredStrategy
        """
        logger.debug(f"UC-8.4 render callback triggered. Active item: {active_item}")

        # Check if UC-8.4 accordion is active
        if not active_item or active_item != "uc-8-4-accordion":
            logger.debug("UC-8.4 accordion not active. Preventing update.")
            raise PreventUpdate

        try:
            # Validate merged_data structure
            if not merged_data:
                logger.warning("UC-8.4: merged_data is None or empty")
                return _create_error_message(
                    "No data available. Please load or merge data first.",
                    "bi bi-exclamation-triangle",
                )

            if not isinstance(merged_data, dict) or "hadeg_df" not in merged_data:
                logger.error("UC-8.4: merged_data does not contain 'hadeg_df' key")
                return _create_error_message(
                    "Invalid data structure. Expected 'hadeg_df' in merged data.",
                    "bi bi-x-circle",
                )

            # Extract DataFrame
            logger.debug("UC-8.4: Extracting DataFrame from merged_data")
            df = pd.DataFrame(merged_data["hadeg_df"])

            if df.empty:
                logger.warning("UC-8.4: DataFrame is empty")
                return _create_error_message(
                    "The HADEG dataset is empty. Please load data with KO, Sample, and Pathway information.",
                    "bi bi-inbox",
                )

            logger.info(
                f"UC-8.4: Processing DataFrame with {len(df)} rows and {len(df.columns)} columns"
            )
            logger.debug(f"UC-8.4: Available columns: {df.columns.tolist()}")

            # Map column names flexibly to handle different naming conventions
            col_map = {}

            # Try to find sample column
            sample_candidates = [
                "Sample",
                "sample",
                "sample_id",
                "Sample_ID",
                "sampleID",
                "genome",
                "Genome",
                "organism",
            ]
            for col_name in sample_candidates:
                if col_name in df.columns:
                    col_map["Sample"] = col_name
                    logger.debug(f"UC-8.4: Mapped Sample to column '{col_name}'")
                    break

            # Try to find KO column
            ko_candidates = ["KO", "ko", "ko_id", "KO_ID", "ko_number"]
            for col_name in ko_candidates:
                if col_name in df.columns:
                    col_map["KO"] = col_name
                    logger.debug(f"UC-8.4: Mapped KO to column '{col_name}'")
                    break

            # Try to find Pathway column
            pathway_candidates = [
                "Pathway",
                "pathway",
                "compound_pathway",
                "Compound_Pathway",
                "PathwayName",
                "pathway_name",
            ]
            for col_name in pathway_candidates:
                if col_name in df.columns:
                    col_map["Pathway"] = col_name
                    logger.debug(f"UC-8.4: Mapped Pathway to column '{col_name}'")
                    break

            # Validate required columns were found
            required_fields = ["Sample", "KO", "Pathway"]
            missing_fields = [
                field for field in required_fields if field not in col_map
            ]

            if missing_fields:
                logger.error(f"UC-8.4: Missing required columns: {missing_fields}")
                return _create_error_message(
                    f"Missing required columns: {', '.join(missing_fields)}. "
                    f"Available columns: {', '.join(df.columns.tolist())}",
                    "bi bi-x-circle",
                )

            # Rename columns to standard names for processing
            df_processed = df.rename(columns={v: k for k, v in col_map.items()})

            # Clean data: strip whitespace, handle nulls
            logger.debug("UC-8.4: Cleaning data")
            df_processed = df_processed.copy()
            df_processed["Sample"] = df_processed["Sample"].astype(str).str.strip()
            df_processed["KO"] = df_processed["KO"].astype(str).str.strip().str.upper()
            df_processed["Pathway"] = df_processed["Pathway"].astype(str).str.strip()

            # Remove null/empty entries
            df_processed = df_processed[
                (df_processed["Sample"] != "")
                & (df_processed["Sample"] != "nan")
                & (df_processed["KO"] != "")
                & (df_processed["KO"] != "NAN")
                & (df_processed["Pathway"] != "")
                & (df_processed["Pathway"] != "nan")
            ]

            if df_processed.empty:
                logger.warning("UC-8.4: No valid data after cleaning")
                return _create_error_message(
                    "No valid data available after cleaning. Check for null values.",
                    "bi bi-inbox",
                )

            logger.info(
                f"UC-8.4: Cleaned data - {len(df_processed)} records, "
                f"{df_processed['Sample'].nunique()} samples, "
                f"{df_processed['Pathway'].nunique()} pathways"
            )

            # Generate heatmap using PlotService
            logger.debug("UC-8.4: Generating heatmap via PlotService")

            fig = plot_service.generate_plot(
                data=df_processed,
                use_case_id="UC-8.4",
                filters={},
                customizations={},
            )

            logger.info("UC-8.4: Heatmap generated successfully")

            # Canonical filename for UC-8.4
            try:
                suggested = sanitize_filename("UC-8.4", "pathway_completeness", "png")
            except Exception:
                suggested = "pathway_completeness.png"

            base_filename = os.path.splitext(suggested)[0]

            return html.Div(
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
                ),
                style={"minHeight": "650px"},
            )

        except ValueError as ve:
            logger.error(f"UC-8.4: Validation error - {str(ve)}", exc_info=True)
            return _create_error_message(
                f"Data validation error: {str(ve)}",
                "bi bi-exclamation-triangle",
            )

        except KeyError as ke:
            logger.error(f"UC-8.4: Missing key error - {str(ke)}", exc_info=True)
            return _create_error_message(
                f"Configuration error: Missing key '{str(ke)}'. "
                "Please ensure uc_8_4_config.yaml exists and is properly configured.",
                "bi bi-gear",
            )

        except Exception as e:
            logger.error(f"UC-8.4: Unexpected error - {str(e)}", exc_info=True)
            return _create_error_message(
                f"An unexpected error occurred while rendering the heatmap: {str(e)}",
                "bi bi-bug",
            )


def _create_error_message(message: str, icon: str) -> html.Div:
    """
    Create a styled error message container.

    Parameters
    ----------
    message : str
        Error message text to display.
    icon : str
        Bootstrap icon class name (e.g., "bi bi-exclamation-triangle").

    Returns
    -------
    html.Div
        Styled error message container with icon.
    """
    import dash_bootstrap_components as dbc

    return html.Div(
        dbc.Alert(
            [
                html.I(className=f"{icon} me-2"),
                html.Span(message),
            ],
            color="warning",
            className="mt-3",
        ),
        style={
            "minHeight": "650px",
            "display": "flex",
            "alignItems": "center",
        },
    )
