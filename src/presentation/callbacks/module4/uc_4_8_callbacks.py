"""
UC-4.8 Callbacks - Interactive Gene Inventory Explorer by Sample and Gene Symbol.

This module implements callback functions for exploring gene inventory through
flexible dual-dropdown filtering (sample/gene) and scatter plot visualization.

Functions
---------
register_uc_4_8_callbacks
    Register all UC-4.8 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses scatter plot for gene inventory exploration
- BioRemPP database REQUIRED
- Supports flexible filtering: sample only, gene only, or both

Version: 1.0.0
"""

import logging
import os
from typing import Any, Optional, Tuple

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename

logger = logging.getLogger(__name__)
logger.propagate = False  # Prevent duplicate logs


SelectionValue = Optional[str | list[str]]


def _normalize_selection(value: SelectionValue) -> list[str]:
    """Normalize dropdown values to a de-duplicated list preserving order."""
    if value is None:
        return []

    if isinstance(value, str):
        cleaned = value.strip()
        return [cleaned] if cleaned else []

    if not isinstance(value, list):
        return []

    seen: set[str] = set()
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        normalized.append(cleaned)

    return normalized


def _format_selection_label(kind: str, selected_list: list[str]) -> str:
    """Build a readable label for dynamic chart titles."""
    if not selected_list:
        return ""

    if len(selected_list) == 1:
        return f"{kind}: <b>{selected_list[0]}</b>"

    preview = ", ".join(selected_list[:3])
    if len(selected_list) > 3:
        preview += "..."

    return f"{kind}s ({len(selected_list)}): <b>{preview}</b>"


def _apply_dual_filter(
    df: pd.DataFrame,
    col_a: str,
    selected_a: list[str],
    col_b: str,
    selected_b: list[str],
) -> pd.DataFrame:
    """Apply conditional filtering with optional selections on two columns."""
    filtered_df = df

    if selected_a:
        filtered_df = filtered_df[filtered_df[col_a].isin(selected_a)]

    if selected_b:
        filtered_df = filtered_df[filtered_df[col_b].isin(selected_b)]

    return filtered_df


def register_uc_4_8_callbacks(app, plot_service) -> None:
    """
    Register UC-4.8 callbacks with Dash app.

    Parameters
    ----------
    app : Dash
        Dash application instance.
    plot_service : PlotService
        Singleton PlotService instance (shared across all callbacks).

    Notes
    -----
    - Registers 3 callbacks: panel toggle, dual-dropdown initialization,
      and conditional scatter plot rendering
    - Refer to official documentation for filtering logic details
    """

    @app.callback(
        Output("uc-4-8-collapse", "is_open"),
        Input("uc-4-8-collapse-button", "n_clicks"),
        State("uc-4-8-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_4_8_info_panel(n_clicks, is_open):
        """Toggle UC-4.8 informative panel collapse."""
        logger.info(
            f"[UC-4.8] Toggle clicked! n_clicks={n_clicks}, " f"is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-4.8] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-4.8] No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-4-8-sample-dropdown", "options"),
            Output("uc-4-8-gene-dropdown", "options"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-4-8-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_uc_4_8_dropdowns(
        merged_data: Optional[dict],
        active_item: Optional[str],
    ) -> Tuple[list, list]:
        """Initialize dropdowns with full stable catalogs from BioRemPP data."""
        logger.info(
            "[UC-4.8] Dropdowns init triggered, data type: %s, active_item=%s",
            type(merged_data),
            active_item,
        )

        if not merged_data:
            logger.debug("[UC-4.8] No data in store, returning empty options")
            return [], []

        if isinstance(merged_data, dict) and not merged_data:
            logger.debug("[UC-4.8] Empty dict in store, returning empty options")
            return [], []

        try:
            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error(
                    "[UC-4.8] Invalid data format: expected dict with 'biorempp_df', got %s",
                    type(merged_data),
                )
                raise PreventUpdate

            df = pd.DataFrame(merged_data["biorempp_df"])

            required_cols = {
                "sample": ["sample", "Sample", "sample_id"],
                "genesymbol": [
                    "genesymbol",
                    "GeneSymbol",
                    "gene_symbol",
                    "Gene_Symbol",
                ],
            }

            col_mapping = {}
            for required, candidates in required_cols.items():
                found = False
                for candidate in candidates:
                    if candidate in df.columns:
                        col_mapping[required] = candidate
                        found = True
                        break
                if not found:
                    logger.error(
                        "[UC-4.8] Required column '%s' not found in BioRemPP data. Available columns: %s",
                        required,
                        df.columns.tolist(),
                    )
                    raise PreventUpdate

            sample_col = col_mapping["sample"]
            gene_col = col_mapping["genesymbol"]

            base_df = df[[sample_col, gene_col]].dropna()
            sample_values = sorted(base_df[sample_col].unique().tolist())
            gene_values = sorted(base_df[gene_col].unique().tolist())

            sample_options = [{"label": sample, "value": sample} for sample in sample_values]
            gene_options = [{"label": gene, "value": gene} for gene in gene_values]

            logger.info(
                "[UC-4.8] Dropdowns initialized with stable catalogs: %s samples, %s genes",
                len(sample_options),
                len(gene_options),
            )

            return sample_options, gene_options

        except Exception as e:
            logger.error(f"[UC-4.8] Dropdowns error: {e}")
            raise PreventUpdate

    @app.callback(
        Output("uc-4-8-chart-container", "children"),
        [
            Input("uc-4-8-sample-dropdown", "value"),
            Input("uc-4-8-gene-dropdown", "value"),
        ],
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_4_8(
        selected_sample: SelectionValue,
        selected_gene: SelectionValue,
        merged_data: Optional[dict],
    ) -> Any:
        """Render UC-4.8 scatter plot with multiselect-aware conditional filtering."""
        selected_samples = _normalize_selection(selected_sample)
        selected_genes = _normalize_selection(selected_gene)

        if not selected_samples and not selected_genes:
            logger.debug("[UC-4.8] No filter selected, showing informative message")
            return html.Div(
                [
                    html.I(className="fas fa-filter me-2"),
                    "Please select one or more samples and/or genes from the dropdown menus above to explore genetic inventory.",
                ],
                className="alert alert-info mt-3",
            )

        if not merged_data:
            logger.warning("[UC-4.8] No data available")
            return _create_error_message("No data available for visualization")

        try:
            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error(
                    "[UC-4.8] Invalid data format: expected dict with 'biorempp_df'"
                )
                return _create_error_message(
                    "BioRemPP database data not found. "
                    "Please ensure BioRemPP data is loaded."
                )

            df = pd.DataFrame(merged_data["biorempp_df"])

            required_cols = {
                "sample": ["sample", "Sample", "sample_id"],
                "compoundname": [
                    "compoundname",
                    "Compound_Name",
                    "CompoundName",
                    "compound",
                ],
                "genesymbol": [
                    "genesymbol",
                    "GeneSymbol",
                    "gene_symbol",
                    "Gene_Symbol",
                ],
                "ko": ["ko", "KO", "ko_id"],
            }

            col_mapping = {}
            for required, candidates in required_cols.items():
                found = False
                for candidate in candidates:
                    if candidate in df.columns:
                        col_mapping[required] = candidate
                        found = True
                        break
                if not found:
                    logger.error(
                        "[UC-4.8] Required column '%s' not found. Available: %s",
                        required,
                        df.columns.tolist(),
                    )
                    return _create_error_message(f"Missing required column: {required}")

            if col_mapping["sample"] != "sample":
                df = df.rename(columns={col_mapping["sample"]: "sample"})
            if col_mapping["compoundname"] != "compoundname":
                df = df.rename(columns={col_mapping["compoundname"]: "compoundname"})
            if col_mapping["genesymbol"] != "genesymbol":
                df = df.rename(columns={col_mapping["genesymbol"]: "genesymbol"})
            if col_mapping["ko"] != "ko":
                df = df.rename(columns={col_mapping["ko"]: "ko"})

            filtered_df = _apply_dual_filter(
                df,
                "sample",
                selected_samples,
                "genesymbol",
                selected_genes,
            )

            title_parts = []
            sample_label = _format_selection_label("Sample", selected_samples)
            gene_label = _format_selection_label("Gene", selected_genes)

            if sample_label:
                title_parts.append(sample_label)
            if gene_label:
                title_parts.append(gene_label)

            plot_title = (
                "Gene Inventory for " + " & ".join(title_parts)
                if title_parts
                else "Gene Inventory"
            )

            if filtered_df.empty:
                filter_desc = []
                if selected_samples:
                    filter_desc.append(f"{len(selected_samples)} sample(s)")
                if selected_genes:
                    filter_desc.append(f"{len(selected_genes)} gene(s)")

                logger.warning("[UC-4.8] No data found for selected filters")
                return _create_error_message(
                    "No gene presence found for the selected filters "
                    f"({', '.join(filter_desc)}). Try a different combination."
                )

            logger.info(
                "[UC-4.8] Filtered data: %s rows (samples=%s, genes=%s)",
                len(filtered_df),
                len(selected_samples),
                len(selected_genes),
            )

            filtered_df = filtered_df.dropna(
                subset=["sample", "compoundname", "genesymbol", "ko"]
            )

            if filtered_df.empty:
                logger.warning("[UC-4.8] No valid data after removing NaNs")
                return _create_error_message(
                    "No valid gene inventory found after data cleaning."
                )

            use_case_id = "UC-4.8"

            logger.info(
                "[UC-4.8] Calling PlotService for %s with %s rows",
                use_case_id,
                len(filtered_df),
            )

            fig = plot_service.generate_plot(use_case_id=use_case_id, data=filtered_df)
            fig.update_layout(title=plot_title, title_x=0.5)

            logger.info("[UC-4.8] [OK] Plot generated successfully")

            try:
                suggested = sanitize_filename("UC-4.8", "compound_network", "png")
            except Exception:
                suggested = "compound_network.png"

            base_filename = os.path.splitext(suggested)[0]

            return dcc.Graph(
                figure=fig,
                config={
                    "displayModeBar": True,
                    "toImageButtonOptions": {
                        "format": "svg",
                        "filename": base_filename,
                    },
                },
                style={"height": "600px"},
            )

        except ValueError as ve:
            logger.error(f"[UC-4.8] Value error: {ve}")
            return _create_error_message(str(ve))
        except Exception as e:
            logger.error(f"[UC-4.8] Rendering error: {e}", exc_info=True)
            return _create_error_message(f"Error generating chart: {str(e)}")


def _create_error_message(message: str) -> html.Div:
    """Create error message component."""
    return html.Div(
        [html.I(className="fas fa-exclamation-triangle me-2"), message],
        className="alert alert-warning mt-3",
    )
