"""
Heatmap Strategy - Count-Based Matrix Visualizations.

This module implements the HeatmapStrategy for creating heatmap visualizations
that show counts of unique values at the intersection of two categorical
dimensions.

Classes
-------
HeatmapStrategy
    Strategy for count-based heatmap generation.

Notes
-----
- Shows absolute counts of unique values (not percentages)
- Supports multiple aggregation methods (nunique, count, sum)
- Automatically sorts by totals for readability

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class HeatmapStrategy(BasePlotStrategy):
    """
    Strategy for count-based heatmap matrix visualizations.

    This strategy creates heatmaps showing counts of unique values where rows
    and columns represent categorical dimensions, and cell values represent
    aggregated counts.

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
    row_column : str
        Column for heatmap rows (y-axis).
    col_column : str
        Column for heatmap columns (x-axis).
    value_column : str
        Column containing values to count unique occurrences.
    aggregation : str
        Aggregation method: 'nunique' (default), 'count', 'sum'.

    Methods
    -------
    validate_data(df)
        Validate input data for heatmap requirements
    process_data(df)
        Process data and create count matrix
    create_figure(processed_df)
        Create heatmap figure from count matrix

    Notes
    -----
    - Supports multiple aggregation methods
    - Automatically sorts rows and columns by totals
    - Shows absolute counts (not percentages)
    """

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

        # Extract strategy-specific parameters
        self.row_column = self.plotly_config.get("row_column", "referenceAG")
        self.col_column = self.plotly_config.get("col_column", "sample")
        self.value_column = self.plotly_config.get("value_column", "ko")
        self.aggregation = self.plotly_config.get("aggregation", "nunique")

        logger.info(
            f"HeatmapStrategy initialized for "
            f"{self.metadata.get('use_case_id', 'unknown')}: "
            f"rows='{self.row_column}', cols='{self.col_column}', "
            f"values='{self.value_column}', agg='{self.aggregation}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for heatmap requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, required columns missing, or no valid
            row/column categories found.
        """
        logger.debug(
            f"Validating data - Shape: {df.shape}, " f"Columns: {df.columns.tolist()}"
        )

        # Check DataFrame not empty
        if df.empty:
            raise ValueError("Input DataFrame is empty")

        # Required columns
        required_cols = [self.row_column, self.col_column, self.value_column]

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

        # Check at least one row and column category
        n_rows = df_clean[self.row_column].nunique()
        n_cols = df_clean[self.col_column].nunique()

        if n_rows == 0:
            raise ValueError(f"No categories found in row column '{self.row_column}'")
        if n_cols == 0:
            raise ValueError(f"No categories found in column '{self.col_column}'")

        logger.info(
            f"Data validation passed - "
            f"{n_rows} row categories, {n_cols} column categories, "
            f"{len(df_clean)} records"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data and create count matrix.

        Cleans data, normalizes strings, groups by row and column dimensions,
        aggregates values, and creates a sorted matrix.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with required columns.

        Returns
        -------
        pd.DataFrame
            Heatmap matrix with row categories as index, column categories
            as columns, and aggregated counts as values.
        """
        logger.info(f"Processing data with '{self.aggregation}' aggregation...")

        # Clean data: remove nulls
        df_clean = df.dropna(
            subset=[self.row_column, self.col_column, self.value_column]
        ).copy()

        logger.debug(
            f"After null removal: {len(df_clean)} records "
            f"({len(df) - len(df_clean)} removed)"
        )

        # Normalize string columns
        for col in [self.row_column, self.col_column, self.value_column]:
            if df_clean[col].dtype == "object":
                df_clean[col] = df_clean[col].str.strip()
                # Uppercase for row and value columns (typically categorical)
                if col in [self.row_column, self.value_column]:
                    df_clean[col] = df_clean[col].str.upper()

        # Aggregate values per (row, column) pair
        if self.aggregation == "nunique":
            # Count unique values
            aggregated = df_clean.groupby([self.row_column, self.col_column])[
                self.value_column
            ].nunique()
        elif self.aggregation == "count":
            # Count all occurrences
            aggregated = df_clean.groupby([self.row_column, self.col_column])[
                self.value_column
            ].count()
        elif self.aggregation == "sum":
            # Sum values (requires numeric column)
            aggregated = df_clean.groupby([self.row_column, self.col_column])[
                self.value_column
            ].sum()
        else:
            raise ValueError(
                f"Unknown aggregation method: '{self.aggregation}'. "
                f"Supported: 'nunique', 'count', 'sum'"
            )

        logger.debug(f"Aggregated {len(aggregated)} (row, column) pairs")

        # Pivot to 2D matrix: rows = row_column, cols = col_column
        heatmap_matrix = aggregated.unstack(level=self.col_column).fillna(0)

        # Convert to int if all values are whole numbers
        if (heatmap_matrix % 1 == 0).all().all():
            heatmap_matrix = heatmap_matrix.astype(int)

        # Sort rows and columns by total counts for readability
        heatmap_matrix = heatmap_matrix.loc[
            heatmap_matrix.sum(axis=1).sort_values(ascending=False).index,
            heatmap_matrix.sum(axis=0).sort_values(ascending=False).index,
        ]

        logger.info(
            f"Heatmap matrix created - "
            f"Shape: {heatmap_matrix.shape}, "
            f"Value range: [{heatmap_matrix.min().min()}, "
            f"{heatmap_matrix.max().max()}]"
        )

        return heatmap_matrix

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create heatmap figure from count matrix.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Heatmap matrix (rows × columns).

        Returns
        -------
        go.Figure
            Configured Plotly heatmap.
        """
        logger.debug("Creating heatmap figure...")

        # Extract chart configuration
        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Handle title configuration (support both string and dict)
        title_config = chart_config.get("title", {})
        if isinstance(title_config, str):
            # Backward compatibility: string title
            show_title = True
            title_text = title_config
        else:
            # New format: dict with show, text
            show_title = title_config.get("show", True)
            title_text = (
                title_config.get("text", "Unique Value Count Heatmap")
                if show_title
                else ""
            )

        # Get axis labels
        x_label = chart_config.get("xaxis", {}).get("title", "Sample")
        y_label = chart_config.get("yaxis", {}).get("title", "Category")
        color_label = chart_config.get("color_label", "Unique Count")

        # Get text display setting
        # For count matrices, show integer values
        total_cells = processed_df.size
        show_text = total_cells <= 400  # Enable text only for smaller matrices
        text_auto = chart_config.get("text_auto", True if show_text else False)

        # Get color scale
        color_scale = chart_config.get("color_continuous_scale", "Greens")

        # Create heatmap using plotly express
        fig = px.imshow(
            processed_df,
            labels=dict(x=x_label, y=y_label, color=color_label),
            text_auto=text_auto,
            aspect="auto",
            color_continuous_scale=color_scale,
        )

        # Apply layout configuration
        template = layout_config.get("template", "simple_white")

        # Calculate dynamic height based on number of rows
        n_rows = processed_df.shape[0]
        default_height = max(500, min(1200, 40 * n_rows + 160))
        height = layout_config.get("height", default_height)
        use_autosize = layout_config.get("autosize", False)

        # Get margin configuration
        margin_config = layout_config.get("margin", {})
        margin = dict(
            l=margin_config.get("l", 80),
            r=margin_config.get("r", 30),
            t=margin_config.get("t", 70),
            b=margin_config.get("b", 60),
        )

        # Get axis angles
        xaxis_tickangle = chart_config.get("xaxis_tickangle", -45)
        yaxis_tickangle = chart_config.get("yaxis_tickangle", 0)

        # Get colorbar configuration
        colorbar_config = chart_config.get("colorbar", {})
        colorbar_title = colorbar_config.get("title", color_label)

        # Build layout update dict
        layout_update = {
            "height": height,
            "template": template,
            "xaxis_tickangle": xaxis_tickangle,
            "margin": margin,
            "plot_bgcolor": "white",
            "coloraxis_colorbar": dict(title=colorbar_title),
        }

        # Add title if enabled
        if show_title and title_text:
            layout_update["title"] = {"text": title_text, "x": 0.5, "xanchor": "center"}

        # Add autosize or width
        if use_autosize:
            layout_update["autosize"] = True
        else:
            if layout_config.get("width"):
                layout_update["width"] = layout_config.get("width")

        fig.update_layout(**layout_update)

        # Remove grid lines for cleaner look
        fig.update_xaxes(showgrid=False)

        # Update Y-axis with rotation
        fig.update_yaxes(showgrid=False, tickangle=yaxis_tickangle)

        # Update text font size if configured
        text_font_size = chart_config.get("text_font_size", 10)
        if text_auto:
            fig.update_traces(textfont_size=text_font_size)

        logger.info(
            f"Heatmap figure created - "
            f"Size: {layout_update.get('width', 'auto')}x{height}px, "
            f"Template: {template}"
        )

        return fig
