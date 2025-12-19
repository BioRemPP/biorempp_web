"""
Results Table Callbacks - BioRemPP v1.0
========================================

Callbacks for on-demand table rendering in accordions.
"""

import logging

import pandas as pd
from dash import Input, Output, State, callback
from dash.exceptions import PreventUpdate

from ..components.composite import create_ag_grid_table

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.propagate = False  # Prevent duplicate logs from parent loggers
# Only add handler if not already present (prevents duplicates on reimport)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(name)s: %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def register_results_callbacks(app):
    """
    Register callbacks for on-demand table rendering.

    Parameters
    ----------
    app : Dash
        Dash application instance

    Notes
    -----
    Tables render on-demand when accordion is expanded.
    Uses accordion item_id as trigger.
    """
    logger.info("=" * 60)
    logger.info("Registering RESULTS callbacks (on-demand accordions)...")
    logger.info("=" * 60)

    @callback(
        Output("biorempp-container", "children"),
        Input("biorempp-accordion", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_biorempp_table(active_item, merged_data):
        """Render BioRemPP table when accordion opens."""
        if not active_item or not merged_data:
            raise PreventUpdate

        df = pd.DataFrame(merged_data.get("biorempp_df", []))
        return create_ag_grid_table(
            table_id="biorempp-table",
            data=df,
            title=None,
            page_size=50,
            card_wrapper=False,
        )

    @callback(
        Output("hadeg-container", "children"),
        Input("hadeg-accordion", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_hadeg_table(active_item, merged_data):
        """Render HADEG table when accordion opens."""
        if not active_item or not merged_data:
            raise PreventUpdate

        df = pd.DataFrame(merged_data.get("hadeg_df", []))
        return create_ag_grid_table(
            table_id="hadeg-table",
            data=df,
            title=None,
            page_size=50,
            card_wrapper=False,
        )

    @callback(
        Output("toxcsm-container", "children"),
        Input("toxcsm-accordion", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_toxcsm_table(active_item, merged_data):
        """Render ToxCSM table when accordion opens.

        Uses toxcsm_raw_df to display merged data (user's compounds + ToxCSM data + Sample column).
        This shows only the compounds that matched the user's input, in wide format (66 columns).
        """
        if not active_item or not merged_data:
            raise PreventUpdate

        # Use toxcsm_raw_df for table display (merged data with Sample column)
        toxcsm_data = merged_data.get("toxcsm_raw_df", [])
        logger.info(f"[DEBUG] ToxCSM table callback triggered")
        logger.info(f"  - toxcsm_raw_df available: {'toxcsm_raw_df' in merged_data}")
        logger.info(f"  - toxcsm_raw_df rows: {len(toxcsm_data)}")

        df = pd.DataFrame(toxcsm_data)
        logger.info(
            f"  - DataFrame created with {len(df)} rows, {len(df.columns) if not df.empty else 0} columns"
        )

        if not df.empty and "Sample" in df.columns:
            logger.info(
                f"  - Sample column present: {df['Sample'].nunique()} unique samples"
            )

        return create_ag_grid_table(
            table_id="toxcsm-table",
            data=df,
            title=None,
            page_size=50,
            card_wrapper=False,
        )

    @callback(
        Output("kegg-container", "children"),
        Input("kegg-accordion", "active_item"),
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_kegg_table(active_item, merged_data):
        """Render KEGG table when accordion opens."""
        if not active_item or not merged_data:
            raise PreventUpdate

        df = pd.DataFrame(merged_data.get("kegg_df", []))
        return create_ag_grid_table(
            table_id="kegg-table", data=df, title=None, page_size=50, card_wrapper=False
        )

    logger.info("[OK] Results callbacks registered successfully")
    logger.info("  - Tables render when accordion expands")
    logger.info("  - 4 AG Grid tables: BioRemPP, HADEG, ToxCSM, KEGG")
    logger.info("  - Built-in filters, sorting, and pagination enabled")
