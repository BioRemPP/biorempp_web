"""
Faceted Heatmap Strategy - Toxicity Profile Visualizations.

This module implements the FacetedHeatmapStrategy for creating faceted
heatmap visualizations showing toxicity scores across multiple super-categories
(facets) for compounds analyzed by the ToxCSM model.

Classes
-------
FacetedHeatmapStrategy
    Strategy for faceted heatmap generation with toxicity profiles.

Notes
-----
- Creates faceted visualizations with multiple toxicity categories
- Shared Y-axis (compounds) across facets
- Unique X-axis (endpoints) per facet
- Color-coded toxicity scores (0-1 scale)

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class FacetedHeatmapStrategy(BasePlotStrategy):
    """
    Strategy for faceted heatmap toxicity profile visualizations.

    This strategy creates faceted heatmaps showing toxicity scores where
    facets represent super-categories, rows show compounds, columns show
    toxicological endpoints, and cell values represent toxicity scores.

    Parameters
    ----------
    config : Dict[str, Any]
        Complete configuration from YAML file.

    Attributes
    ----------
    data_config : Dict[str, Any]
        Data processing configuration.
    plotly_config : Dict[str, Any]
        Plotly-specific configuration.
    compound_column : str
        Column containing compound names (default: 'compoundname').
    endpoint_column : str
        Column containing endpoint names (default: 'endpoint').
    score_column : str
        Column containing toxicity scores (default: 'toxicity_score').
    category_column : str
        Column containing super-categories (default: 'super_category').
    category_order : List[str]
        Order of facets from left to right.

    Methods
    -------
    validate_data(df)
        Validate input data for faceted heatmap requirements
    process_data(df)
        Process data with cleaning and aggregation
    create_figure(processed_df)
        Create faceted heatmap figure from processed data

    Notes
    -----
    - Supports multiple toxicity response categories as facets
    - Shared Y-axis (compounds) across all facets
    - Color scale: 0 (low risk) to 1 (high risk)
    """

    # Default category order for facets
    DEFAULT_CATEGORY_ORDER = [
        "Nuclear Response",
        "Stress Response",
        "Genomic",
        "Environmental",
        "Organic",
    ]

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize strategy with configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            Complete configuration from YAML file.
        """
        super().__init__(config)
        self.data_config = config.get("data", {})
        self.plotly_config = self.viz_config.get("plotly", {})

        # Extract column names from config
        self.compound_column = self.plotly_config.get("compound_column", "compoundname")
        self.endpoint_column = self.plotly_config.get("endpoint_column", "endpoint")
        self.score_column = self.plotly_config.get("score_column", "toxicity_score")
        self.category_column = self.plotly_config.get(
            "category_column", "super_category"
        )

        # Get category order (facet arrangement)
        self.category_order = self.plotly_config.get(
            "category_order", self.DEFAULT_CATEGORY_ORDER
        )

        logger.info(
            f"FacetedHeatmapStrategy initialized for "
            f"{self.metadata.get('use_case_id', 'unknown')}: "
            f"compound='{self.compound_column}', "
            f"endpoint='{self.endpoint_column}', "
            f"score='{self.score_column}', "
            f"category='{self.category_column}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for faceted heatmap requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, required columns missing, score column
            not numeric, or no valid compounds/endpoints/categories found.
        """
        logger.debug(
            f"Validating data - Shape: {df.shape}, " f"Columns: {df.columns.tolist()}"
        )

        # Check DataFrame not empty
        if df.empty:
            raise ValueError("Input DataFrame is empty")

        # Required columns
        required_cols = [
            self.compound_column,
            self.endpoint_column,
            self.score_column,
            self.category_column,
        ]

        # Check required columns exist
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"Available columns: {df.columns.tolist()}"
            )

        # Drop rows with null values in critical columns
        df_clean = df.dropna(subset=required_cols)
        if df_clean.empty:
            raise ValueError(
                f"No valid data after removing nulls in columns: {required_cols}"
            )

        # Check numeric score column
        if not pd.api.types.is_numeric_dtype(df_clean[self.score_column]):
            # Try to convert
            try:
                pd.to_numeric(df_clean[self.score_column])
            except (ValueError, TypeError):
                raise ValueError(f"Score column '{self.score_column}' must be numeric")

        # Check at least one compound and endpoint
        n_compounds = df_clean[self.compound_column].nunique()
        n_endpoints = df_clean[self.endpoint_column].nunique()
        n_categories = df_clean[self.category_column].nunique()

        if n_compounds == 0:
            raise ValueError(f"No compounds found in column '{self.compound_column}'")
        if n_endpoints == 0:
            raise ValueError(f"No endpoints found in column '{self.endpoint_column}'")
        if n_categories == 0:
            raise ValueError(f"No categories found in column '{self.category_column}'")

        logger.info(
            f"Data validation passed - "
            f"{n_compounds} compounds, {n_endpoints} endpoints, "
            f"{n_categories} categories, {len(df_clean)} records"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for faceted heatmap visualization.

        Applies cleaning, aggregation, and sorting to prepare data for
        visualization.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with required columns.

        Returns
        -------
        pd.DataFrame
            Processed data ready for visualization.
        """
        logger.info("Processing data for faceted heatmap...")

        # Clean data: remove nulls
        df_clean = df.dropna(
            subset=[
                self.compound_column,
                self.endpoint_column,
                self.score_column,
                self.category_column,
            ]
        ).copy()

        # Ensure score is numeric
        df_clean[self.score_column] = pd.to_numeric(
            df_clean[self.score_column], errors="coerce"
        )
        df_clean = df_clean.dropna(subset=[self.score_column])

        logger.debug(
            f"After cleaning: {len(df_clean)} records "
            f"({len(df) - len(df_clean)} removed)"
        )

        # Aggregate by (compound, endpoint, category) using mean
        df_agg = df_clean.groupby(
            [self.compound_column, self.endpoint_column, self.category_column],
            as_index=False,
        )[self.score_column].mean()

        logger.info(
            f"Data processed - "
            f"{df_agg[self.compound_column].nunique()} compounds, "
            f"{df_agg[self.endpoint_column].nunique()} endpoints, "
            f"{df_agg[self.category_column].nunique()} categories"
        )

        return df_agg

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create faceted heatmap figure.

        Creates a subplot with one heatmap per super-category, with shared
        Y-axis (compounds) and unique X-axis per facet (endpoints).

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data with compound_order column for sorting.

        Returns
        -------
        go.Figure
            Configured Plotly faceted heatmap.
        """
        logger.debug("Creating faceted heatmap figure...")

        # Extract chart configuration
        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Get unique categories in specified order
        available_categories = processed_df[self.category_column].unique()
        categories = [cat for cat in self.category_order if cat in available_categories]

        # Add any categories not in default order
        for cat in available_categories:
            if cat not in categories:
                categories.append(cat)

        n_cols = len(categories)
        if n_cols == 0:
            raise ValueError("No categories found to plot")

        logger.debug(f"Creating {n_cols} facets: {categories}")

        # Create subplots with shared Y-axis
        fig = make_subplots(
            rows=1,
            cols=n_cols,
            shared_yaxes=True,
            horizontal_spacing=chart_config.get("horizontal_spacing", 0.02),
            subplot_titles=categories,
        )

        # Sort compounds by total toxicity score (descending)
        # This ensures highest-risk compounds appear at the top
        compound_totals = (
            processed_df.groupby(self.compound_column)[self.score_column]
            .sum()
            .sort_values(ascending=True)
        )

        # Get compound order (ascending so highest risk at top after reindex)
        all_compounds = compound_totals.index.tolist()

        # Show colorbar only on last column
        show_scale_on_col = n_cols

        # Get colorscale configuration
        colorscale = chart_config.get("colorscale", "Reds")
        colorbar_title = chart_config.get("colorbar_title", "Toxicity Score")

        # Create heatmap for each category
        for i, category in enumerate(categories, start=1):
            subset = processed_df[processed_df[self.category_column] == category]

            if subset.empty:
                logger.warning(f"No data for category: {category}")
                continue

            # Pivot to create heatmap matrix
            heatmap_data = subset.pivot_table(
                index=self.compound_column,
                columns=self.endpoint_column,
                values=self.score_column,
                aggfunc="mean",
            )

            # Reindex to ensure all compounds are present
            heatmap_data = heatmap_data.reindex(index=all_compounds)

            # Get endpoint names for this category
            endpoints = heatmap_data.columns.tolist()

            # Add heatmap trace
            fig.add_trace(
                go.Heatmap(
                    z=heatmap_data.values,
                    x=endpoints,
                    y=heatmap_data.index.tolist(),
                    colorscale=colorscale,
                    zmin=0,
                    zmax=1,
                    showscale=(i == show_scale_on_col),
                    colorbar=(
                        dict(
                            title=dict(text=colorbar_title, font=dict(size=12))
                        )
                        if i == show_scale_on_col
                        else None
                    ),
                    hovertemplate=(
                        "<b>Compound:</b> %{y}<br>"
                        "<b>Endpoint:</b> %{x}<br>"
                        "<b>Toxicity Score:</b> %{z:.3f}<extra></extra>"
                    ),
                ),
                row=1,
                col=i,
            )

        # Handle title configuration (support both string and dict)
        title_config = chart_config.get("title", {})
        if isinstance(title_config, str):
            # Backward compatibility: string title
            show_title = True
            title_text = title_config
            title_font_size = 16
        else:
            # New format: dict with show, text, font_size
            show_title = title_config.get("show", True)
            title_text = (
                title_config.get(
                    "text", "Faceted Heatmap of Compound Toxicity Profiles"
                )
                if show_title
                else ""
            )
            title_font_size = title_config.get("font_size", 16)

        # Get layout options
        height = layout_config.get("height", 800)
        use_autosize = layout_config.get("autosize", False)
        template = layout_config.get("template", "simple_white")

        # Get margin configuration
        margin_config = layout_config.get("margin", {})
        margin = dict(
            l=margin_config.get("l", 150),
            r=margin_config.get("r", 50),
            t=margin_config.get("t", 80),
            b=margin_config.get("b", 100),
        )

        # Build layout update dict
        layout_update = {
            "title": dict(
                text=title_text,
                x=0.5,
                xanchor="center",
                font=dict(size=title_font_size),
            ),
            "height": height,
            "margin": margin,
            "plot_bgcolor": "white",
            "template": template,
        }

        # Add autosize or width
        if use_autosize:
            layout_update["autosize"] = True
        else:
            if layout_config.get("width"):
                layout_update["width"] = layout_config.get("width", 1200)

        fig.update_layout(**layout_update)

        # Update X-axes: rotate labels
        xaxis_tickangle = chart_config.get("xaxis_tickangle", -45)
        for i in range(1, n_cols + 1):
            fig.update_xaxes(tickangle=xaxis_tickangle, row=1, col=i)

        # Update Y-axis: title and rotation on first column
        yaxis_title = chart_config.get("yaxis_title", "Compound")
        yaxis_tickangle = chart_config.get("yaxis_tickangle", 0)
        fig.update_yaxes(
            title_text=yaxis_title, tickangle=yaxis_tickangle, row=1, col=1
        )

        logger.info(
            f"Faceted heatmap created - "
            f"{n_cols} facets, {len(all_compounds)} compounds, "
            f"Size: {layout_update.get('width', 'auto')}x{height}px"
        )

        return fig
