"""
UC-4.7 Callbacks - Interactive Gene-Compound Association Explorer.

This module implements callback functions for exploring gene-compound associations
through flexible dual-dropdown filtering and scatter plot visualization.

Functions
---------
register_uc_4_7_callbacks
    Register all UC-4.7 callbacks with Dash app.

Notes
-----
- Refer to official documentation for use case details
- Uses scatter plot for gene-compound association exploration
- BioRemPP database REQUIRED
- Supports flexible filtering: compound only, gene only, or both

Version: 1.0.0
"""

import logging
import os
from typing import Any, Optional, Tuple

import pandas as pd
from dash import Input, Output, State, dcc, html
from dash.exceptions import PreventUpdate

from src.presentation.components.download_component import sanitize_filename
from src.presentation.services.results_payload_resolver import resolve_results_payload

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


def register_uc_4_7_callbacks(app, plot_service) -> None:
    """
    Register UC-4.7 callbacks with Dash app.

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
        Output("uc-4-7-collapse", "is_open"),
        Input("uc-4-7-collapse-button", "n_clicks"),
        State("uc-4-7-collapse", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_uc_4_7_info_panel(n_clicks, is_open):
        """
        Toggle UC-4.7 informative panel collapse.

        Parameters
        ----------
        n_clicks : int
            Number of clicks on collapse button.
        is_open : bool
            Current collapse state.

        Returns
        -------
        bool
            New collapse state (toggled).
        """
        logger.info(
            f"[UC-4.7] Toggle clicked! n_clicks={n_clicks}, " f"is_open={is_open}"
        )
        if n_clicks:
            new_state = not is_open
            logger.info(f"[UC-4.7] [OK] Panel toggled to: {new_state}")
            return new_state
        logger.info(f"[UC-4.7] No clicks, keeping is_open={is_open}")
        return is_open

    @app.callback(
        [
            Output("uc-4-7-compound-dropdown", "options"),
            Output("uc-4-7-gene-dropdown", "options"),
        ],
        [
            Input("merged-result-store", "data"),
            Input("uc-4-7-accordion-group", "active_item"),
        ],
        prevent_initial_call=True,
    )
    def initialize_uc_4_7_dropdowns(
        merged_data: Optional[dict],
        active_item: Optional[str],
    ) -> Tuple[list, list]:
        """Initialize dropdowns with full stable catalogs from BioRemPP data."""
        merged_data = resolve_results_payload(merged_data)
        logger.info(
            "[UC-4.7] Dropdowns init triggered, data type: %s, active_item=%s",
            type(merged_data),
            active_item,
        )

        if not merged_data:
            logger.debug("[UC-4.7] No data in store, returning empty options")
            return [], []

        if isinstance(merged_data, dict) and not merged_data:
            logger.debug("[UC-4.7] Empty dict in store, returning empty options")
            return [], []

        try:
            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error(
                    "[UC-4.7] Invalid data format: expected dict with 'biorempp_df', got %s",
                    type(merged_data),
                )
                raise PreventUpdate

            df = pd.DataFrame(merged_data["biorempp_df"])

            required_cols = {
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
                        "[UC-4.7] Required column '%s' not found. Available columns: %s",
                        required,
                        df.columns.tolist(),
                    )
                    raise PreventUpdate

            compound_col = col_mapping["compoundname"]
            gene_col = col_mapping["genesymbol"]

            base_df = df[[compound_col, gene_col]].dropna()
            compound_values = sorted(base_df[compound_col].unique().tolist())
            gene_values = sorted(base_df[gene_col].unique().tolist())

            compound_options = [
                {"label": compound, "value": compound} for compound in compound_values
            ]
            gene_options = [{"label": gene, "value": gene} for gene in gene_values]

            logger.info(
                "[UC-4.7] Dropdowns initialized with stable catalogs: %s compounds, %s genes",
                len(compound_options),
                len(gene_options),
            )

            return compound_options, gene_options

        except Exception as e:
            logger.error(f"[UC-4.7] Dropdowns error: {e}")
            raise PreventUpdate

    @app.callback(
        Output("uc-4-7-chart-container", "children"),
        [
            Input("uc-4-7-compound-dropdown", "value"),
            Input("uc-4-7-gene-dropdown", "value"),
        ],
        State("merged-result-store", "data"),
        prevent_initial_call=True,
    )
    def render_uc_4_7(
        selected_compound: SelectionValue,
        selected_gene: SelectionValue,
        merged_data: Optional[dict],
    ) -> Any:
        """Render UC-4.7 scatter plot with multiselect-aware conditional filtering."""
        merged_data = resolve_results_payload(merged_data)
        selected_compounds = _normalize_selection(selected_compound)
        selected_genes = _normalize_selection(selected_gene)

        if not selected_compounds and not selected_genes:
            logger.debug("[UC-4.7] No filter selected, showing informative message")
            return html.Div(
                [
                    html.I(className="fas fa-filter me-2"),
                    "Please select one or more compounds and/or genes from the dropdown menus above to explore associations.",
                ],
                className="alert alert-info mt-3",
            )

        if not merged_data:
            logger.warning("[UC-4.7] No data available")
            return _create_error_message("No data available for visualization")

        try:
            logger.debug("[UC-4.7] Received data type: %s", type(merged_data))

            if not isinstance(merged_data, dict) or "biorempp_df" not in merged_data:
                logger.error(
                    "[UC-4.7] Invalid data format: expected dict with 'biorempp_df'"
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
                        "[UC-4.7] Required column '%s' not found. Available: %s",
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
                "compoundname",
                selected_compounds,
                "genesymbol",
                selected_genes,
            )

            title_parts = []
            compound_label = _format_selection_label("Compound", selected_compounds)
            gene_label = _format_selection_label("Gene", selected_genes)

            if compound_label:
                title_parts.append(compound_label)
            if gene_label:
                title_parts.append(gene_label)

            plot_title = (
                "Gene-Compound Associations for " + " & ".join(title_parts)
                if title_parts
                else "Gene-Compound Associations"
            )

            if filtered_df.empty:
                filter_desc = []
                if selected_compounds:
                    filter_desc.append(f"{len(selected_compounds)} compound(s)")
                if selected_genes:
                    filter_desc.append(f"{len(selected_genes)} gene(s)")

                logger.warning("[UC-4.7] No data found for selected filters")
                return _create_error_message(
                    "No associations found for the selected filters "
                    f"({', '.join(filter_desc)}). Try a different combination."
                )

            logger.info(
                "[UC-4.7] Filtered data: %s rows (compounds=%s, genes=%s)",
                len(filtered_df),
                len(selected_compounds),
                len(selected_genes),
            )

            filtered_df = filtered_df.dropna(
                subset=["sample", "compoundname", "genesymbol", "ko"]
            )

            if filtered_df.empty:
                logger.warning("[UC-4.7] No valid data after removing NaNs")
                return _create_error_message(
                    "No valid associations found after data cleaning."
                )

            use_case_id = "UC-4.7"
            logger.info(
                "[UC-4.7] Calling PlotService for %s with %s rows",
                use_case_id,
                len(filtered_df),
            )

            fig = plot_service.generate_plot(use_case_id=use_case_id, data=filtered_df)
            fig.update_layout(title=plot_title, title_x=0.5)

            logger.info("[UC-4.7] [OK] Plot generated successfully")

            try:
                suggested = sanitize_filename("UC-4.7", "pathway_similarity", "png")
            except Exception:
                suggested = "pathway_similarity.png"

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
            logger.error(f"[UC-4.7] Value error: {ve}")
            return _create_error_message(str(ve))
        except Exception as e:
            logger.error(f"[UC-4.7] Rendering error: {e}", exc_info=True)
            return _create_error_message(f"Error generating chart: {str(e)}")


def _create_error_message(message: str) -> html.Div:
    """
    Create error message component.

    Parameters
    ----------
    message : str
        Error message to display.

    Returns
    -------
    html.Div
        Error message component with alert styling.
    """
    return html.Div(
        [html.I(className="fas fa-exclamation-triangle me-2"), message],
        className="alert alert-warning mt-3",
    )
