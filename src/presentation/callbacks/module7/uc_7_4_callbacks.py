"""
UC-7.4 Callbacks - Toxicity Score Distribution by Endpoint Category.

This module implements callback functions for visualizing toxicity score
distributions through box plot analysis across endpoints within selected
toxicity super-categories.

Functions
---------
register_uc_7_4_callbacks
    Register all UC-7.4 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses box plot visualization for score distribution analysis
- ToxCSM database REQUIRED (BioRemPP/KEGG do not contain toxicity data)

Version: 1.0.0
"""

import logging
import os
from typing import Any, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)
logger.propagate = False


def register_uc_7_4_callbacks(app, plot_service) -> None:
    """
    Register UC-7.4 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers description toggle, dropdown initialization, and box plot callbacks
    - Refer to official documentation for processing logic details
    """

    # Callback 1: View Use Case Description
    @app.callback(
        Output("uc-7-4-collapse", "is_open"),
        Input("uc-7-4-collapse-button", "n_clicks"),
        State("uc-7-4-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_7_4_description(n_clicks, is_open):
        """Toggle UC-7.4 use case description panel."""
        if n_clicks:
            logger.info(f"[UC-7.4] 📖 Description toggle: {not is_open}")
            return not is_open
        return is_open

    # Callback 2: Initialize dropdown
    @app.callback(
        [
            Output("uc-7-4-category-dropdown", "options"),
            Output("uc-7-4-category-dropdown", "value"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-7-4-accordion", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_toxicity_category_dropdown(
        merged_data: Optional[list], active_item: Optional[str]
    ) -> Tuple[list, None]:
        """
        Initialize toxicity super-category dropdown with ToxCSM data.

        Parameters
        ----------
        merged_data : list, optional
            Store data with toxcsm_df key.
        active_item : str, optional
            Accordion state trigger.

        Returns
        -------
        tuple of (list, None)
            Dropdown options list and default value (None).

        Notes
        -----
        - Extracts unique 'super_category' values from ToxCSM dataset
        - ToxCSM data is in long format with super_category column
        - Returns empty list if ToxCSM data unavailable
        """
        logger.info(
            f"[UC-7.4] 🔄 Dropdown init triggered, " f"data type: {type(merged_data)}"
        )

        if not merged_data:
            logger.warning("[UC-7.4] ⚠️ No data available in store")
            raise PreventUpdate

        try:
            # Extract ToxCSM DataFrame (already in long format)
            if isinstance(merged_data, dict):
                toxcsm_data = merged_data.get("toxcsm_df")
                if toxcsm_data is None or len(toxcsm_data) == 0:
                    logger.warning("[UC-7.4] ⚠️ No ToxCSM data in merged store")
                    raise PreventUpdate

                # Convert list of dicts to DataFrame
                if isinstance(toxcsm_data, list):
                    df_long = pd.DataFrame(toxcsm_data)
                    logger.info(
                        f"[UC-7.4] 📊 ToxCSM DataFrame: {df_long.shape}, "
                        f"Columns: {df_long.columns.tolist()}"
                    )
                else:
                    df_long = toxcsm_data
            else:
                logger.warning("[UC-7.4] ⚠️ Invalid data structure")
                raise PreventUpdate

            # Check for super_category column (data is already in long format)
            if "super_category" not in df_long.columns:
                logger.error(
                    "[UC-7.4] ❌ super_category column not found. "
                    f"Available: {df_long.columns.tolist()}"
                )
                raise PreventUpdate

            # Extract unique super-categories
            unique_categories = sorted(df_long["super_category"].unique().tolist())

            if len(unique_categories) == 0:
                logger.warning("[UC-7.4] ⚠️ No super-categories found in data")
                raise PreventUpdate

            # Create dropdown options
            options = [
                {"label": category, "value": category} for category in unique_categories
            ]

            logger.info(
                f"[UC-7.4] [OK] Dropdown initialized with "
                f"{len(options)} categories: {unique_categories}"
            )
            return options, None

        except Exception as e:
            logger.error(f"[UC-7.4] ❌ Error initializing dropdown: {e}", exc_info=True)
            raise PreventUpdate

    @app.callback(
        Output("uc-7-4-chart-container", "children"),
        Input("uc-7-4-category-dropdown", "value"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_7_4(
        selected_category: Optional[str], merged_data: Optional[dict]
    ) -> Any:
        """
        Render UC-7.4 box plot showing toxicity score distribution by endpoint.

        Parameters
        ----------
        selected_category : str, optional
            Super-category from dropdown (e.g., 'Genomic', 'Environmental').
        merged_data : dict, optional
            Store data with 'toxcsm_df' key.

        Returns
        -------
        dcc.Graph or html.Div
            Box plot figure or error message.

        Notes
        -----
        - Extracts ToxCSM DataFrame (already in long format)
        - Filters by selected super-category
        - Generates box plot with jittered compound points overlay
        - Adds threshold lines (0.3 safety, 0.5 moderate, 0.7 high risk)
        - Sorts endpoints by median toxicity score (descending)
        """
        logger.info(f"[UC-7.4] 📊 Render triggered, category: {selected_category}")

        if not selected_category:
            logger.warning("[UC-7.4] ⚠️ No category selected")
            raise PreventUpdate

        if not merged_data:
            logger.warning("[UC-7.4] ⚠️ No data in store")
            return _create_empty_state("No data available. Please process data first.")

        try:
            # Extract ToxCSM DataFrame (already in long format from processing)
            toxcsm_data = merged_data.get("toxcsm_df")
            if toxcsm_data is None or len(toxcsm_data) == 0:
                logger.warning("[UC-7.4] ⚠️ No ToxCSM data available")
                return _create_empty_state("ToxCSM data not available.")

            # Convert to DataFrame (data is already in long format)
            if isinstance(toxcsm_data, list):
                df_long = pd.DataFrame(toxcsm_data)
                logger.info(
                    f"[UC-7.4] 📊 Data loaded: {df_long.shape}, "
                    f"Columns: {df_long.columns.tolist()}"
                )
            else:
                df_long = toxcsm_data

            # Validate required columns
            required_cols = [
                "compoundname",
                "endpoint",
                "toxicity_score",
                "super_category",
            ]
            missing_cols = [col for col in required_cols if col not in df_long.columns]

            if missing_cols:
                logger.error(
                    f"[UC-7.4] ❌ Missing columns: {missing_cols}. "
                    f"Available: {df_long.columns.tolist()}"
                )
                return _create_error_message(
                    f"Invalid data structure. Missing columns: {missing_cols}"
                )

            # ==================================================================
            # FILTERING: Apply Super-Category Selection
            # ==================================================================
            df_filtered = df_long[df_long["super_category"] == selected_category].copy()

            if df_filtered.empty:
                logger.warning(f"[UC-7.4] ⚠️ No data for category: {selected_category}")
                return _create_empty_state(
                    f"No data available for category: {selected_category}"
                )

            logger.info(
                f"[UC-7.4] 📈 Generating box plot: {len(df_filtered)} "
                f"records, {df_filtered['endpoint'].nunique()} endpoints"
            )

            # ==================================================================
            # VISUALIZATION: Create Box Plot with Jittered Points
            # ==================================================================
            fig = go.Figure()

            # Get unique endpoints sorted by median toxicity (descending)
            endpoint_medians = (
                df_filtered.groupby("endpoint")["toxicity_score"]
                .median()
                .sort_values(ascending=False)
            )
            endpoints = endpoint_medians.index.tolist()

            # Random seed for reproducible jitter
            rng = np.random.default_rng(42)

            # Create traces for each endpoint
            for i, endpoint in enumerate(endpoints):
                endpoint_data = df_filtered[df_filtered["endpoint"] == endpoint]
                n = len(endpoint_data)

                # Box plot trace
                fig.add_trace(
                    go.Box(
                        y=endpoint_data["toxicity_score"],
                        x=np.full(n, i),
                        name=endpoint,
                        boxpoints=False,
                        marker_color="#dc3545",
                        line_color="#721c24",
                        fillcolor="rgba(220, 53, 69, 0.3)",
                        width=0.7,
                    )
                )

                # Jittered scatter points
                jitter = rng.uniform(low=-0.3, high=0.3, size=n)
                fig.add_trace(
                    go.Scatter(
                        x=np.full(n, i) + jitter,
                        y=endpoint_data["toxicity_score"],
                        mode="markers",
                        marker=dict(color="black", size=4, opacity=0.6),
                        showlegend=False,
                        customdata=endpoint_data[["compoundname"]],
                        hovertemplate=(
                            "<b>Compound:</b> %{customdata[0]}<br>"
                            "<b>Score:</b> %{y:.3f}<extra></extra>"
                        ),
                    )
                )

            # Update layout
            fig.update_layout(
                title=dict(
                    text=(
                        f"<b>Toxicity Score Distribution:</b> " f"{selected_category}"
                    ),
                    x=0.5,
                    xanchor="center",
                    font=dict(size=18),
                ),
                height=650,
                width=1200,
                plot_bgcolor="white",
                yaxis=dict(
                    gridcolor="lightgray",
                    title="Predicted Toxicity Score",
                    range=[0, 1.05],
                    dtick=0.1,
                ),
                xaxis=dict(
                    title="Toxicological Endpoint",
                    tickmode="array",
                    tickvals=list(range(len(endpoints))),
                    ticktext=endpoints,
                    tickangle=-45,
                ),
                showlegend=False,
                boxmode="group",
                margin=dict(l=80, r=120, t=100, b=150),  # Increased right margin
            )

            # Add threshold lines
            fig.add_hline(
                y=0.3,
                line_dash="dash",
                line_color="#28a745",
                line_width=2,
                annotation_text="Safety",
                annotation_position="right",
            )
            fig.add_hline(
                y=0.5,
                line_dash="dash",
                line_color="#ffc107",
                line_width=2,
                annotation_text="Moderate Risk",
                annotation_position="right",
            )
            fig.add_hline(
                y=0.7,
                line_dash="dash",
                line_color="#dc3545",
                line_width=2,
                annotation_text="High Risk",
                annotation_position="right",
            )

            # Prepare safe basename and export configuration
            cat_safe = str(selected_category).replace(" ", "_")
            db_basename = f"toxicity_distribution_{cat_safe}"
            try:
                suggested = sanitize_filename("UC-7.4", db_basename, "png")
            except Exception:
                suggested = f"{db_basename}.png"

            base_filename = os.path.splitext(suggested)[0]

            config = {
                "toImageButtonOptions": {
                    "format": "png",
                    "filename": base_filename,
                    "scale": 6,
                }
            }

            logger.info("[UC-7.4] ✅ Box plot generated successfully")

            return dcc.Graph(figure=fig, config=config, className="border rounded p-2")

        except Exception as e:
            logger.error(f"[UC-7.4] ❌ Error rendering chart: {e}", exc_info=True)
            return _create_error_message(str(e))


def _create_empty_state(message: str) -> html.Div:
    """
    Create styled empty state message.

    Parameters
    ----------
    message : str
        Message text to display.

    Returns
    -------
    html.Div
        Styled empty state component.
    """
    return html.Div(message, className="text-muted text-center py-5")


def _create_error_message(error: str) -> html.Div:
    """
    Create styled error message.

    Parameters
    ----------
    error : str
        Error message text to display.

    Returns
    -------
    html.Div
        Styled error component.
    """
    return html.Div(
        f"Error generating chart: {error}", className="text-danger text-center py-5"
    )
