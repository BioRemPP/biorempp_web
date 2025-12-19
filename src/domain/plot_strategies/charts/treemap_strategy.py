"""
Treemap Strategy - Hierarchical Data Visualizations.

This module implements the TreemapStrategy for generating treemap visualizations
that display hierarchical data structures with nested rectangles sized by
aggregated values.

Classes
-------
TreemapStrategy
    Strategy for hierarchical treemap generation.

Notes
-----
- Visualizes part-to-whole relationships in hierarchical data
- Compares proportions across multiple levels of a hierarchy
- Supports continuous and discrete color modes

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class TreemapStrategy(BasePlotStrategy):
    """
    Strategy for hierarchical treemap nested categorical data visualization.

    This strategy creates treemaps showing hierarchical relationships with
    nested rectangles sized by aggregated values.

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
    path_columns : List[str]
        Columns defining the hierarchy path (excluding root).
    value_column : str
        Column containing values for aggregation.
    aggregation : str
        Aggregation method: 'nunique', 'count', 'sum'.
    root_label : str
        Label for the root node of the treemap.
    color_column : Optional[str]
        Column for coloring (None = use value_column).
    color_mode : str
        'continuous' for numeric scale, 'discrete' for categorical.

    Methods
    -------
    validate_data(df)
        Validate input data for treemap requirements
    process_data(df)
        Process data and create aggregated treemap data
    create_figure(processed_df)
        Create treemap figure from aggregated data

    Notes
    -----
    - Path defines sequence of columns for hierarchy
    - Values determine rectangle sizes
    - Color can be continuous or discrete
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

        # Hierarchy configuration
        self.path_columns: List[str] = self.plotly_config.get("path_columns", [])
        self.root_label: str = self.plotly_config.get("root_label", "All Data")

        # Aggregation configuration
        self.value_column: str = self.plotly_config.get("value_column", "count")
        self.aggregation: str = self.plotly_config.get("aggregation", "nunique")

        # Color configuration
        self.color_mode: str = self.plotly_config.get("color_mode", "continuous")
        self.color_column: Optional[str] = self.plotly_config.get("color_column", None)

        # Store aggregated column name
        self._aggregated_value_column: str = ""

        logger.info(
            f"TreemapStrategy initialized for "
            f"{self.metadata.get('use_case_id', 'unknown')}: "
            f"path={self.path_columns}, "
            f"values='{self.value_column}', agg='{self.aggregation}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for treemap requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, path columns not configured, required
            columns missing, or no valid data after null removal.
        """
        logger.debug(
            f"Validating data - Shape: {df.shape}, " f"Columns: {df.columns.tolist()}"
        )

        if df.empty:
            raise ValueError("Input DataFrame is empty")

        if not self.path_columns:
            raise ValueError(
                "No path_columns configured. "
                "Treemap requires at least one hierarchy level."
            )

        # Required columns
        required_cols = self.path_columns + [self.value_column]

        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"Available columns: {df.columns.tolist()}"
            )

        # Check color column if specified
        if self.color_column and self.color_column not in df.columns:
            raise ValueError(f"Color column '{self.color_column}' not found.")

        # Validate data after null removal
        df_clean = df.dropna(subset=required_cols)
        if df_clean.empty:
            raise ValueError(f"No valid data after removing nulls in: {required_cols}")

        logger.info(
            f"Data validation passed - "
            f"{len(df_clean)} valid records, "
            f"{len(self.path_columns)} hierarchy levels"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data and create aggregated treemap data.

        Cleans data, removes placeholders, and aggregates by path columns
        using specified aggregation method.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with required columns.

        Returns
        -------
        pd.DataFrame
            Aggregated data ready for treemap visualization.
        """
        logger.info(f"Processing data with '{self.aggregation}' aggregation...")

        # Select relevant columns
        cols_to_use = self.path_columns + [self.value_column]
        if self.color_column and self.color_column not in cols_to_use:
            cols_to_use.append(self.color_column)

        df_treemap = df[cols_to_use].copy()

        # Clean data
        initial_count = len(df_treemap)
        df_treemap.dropna(inplace=True)

        # Sanitize placeholder tokens
        for col in self.path_columns:
            if df_treemap[col].dtype == "object":
                df_treemap[col] = df_treemap[col].astype(str).str.strip()
                df_treemap = df_treemap[
                    ~df_treemap[col].isin(["#N/D", "#N/A", "N/D", "", "nan"])
                ]

        cleaned_count = len(df_treemap)
        logger.debug(
            f"After cleaning: {cleaned_count} records "
            f"({initial_count - cleaned_count} removed)"
        )

        if df_treemap.empty:
            raise ValueError("No valid data after cleaning")

        # Determine aggregation function and column name
        if self.aggregation == "nunique":
            agg_func = "nunique"
            value_col_name = f"unique_{self.value_column}_count"
        elif self.aggregation == "count":
            agg_func = "count"
            value_col_name = f"{self.value_column}_count"
        elif self.aggregation == "sum":
            agg_func = "sum"
            value_col_name = f"{self.value_column}_sum"
        else:
            raise ValueError(
                f"Unknown aggregation: '{self.aggregation}'. "
                f"Supported: 'nunique', 'count', 'sum'"
            )

        # Aggregate by path columns
        df_agg = (
            df_treemap.groupby(self.path_columns)[self.value_column]
            .agg(agg_func)
            .reset_index()
        )
        df_agg.columns = self.path_columns + [value_col_name]

        # Store for create_figure
        self._aggregated_value_column = value_col_name

        # Add root column
        df_agg["root"] = self.root_label

        logger.info(
            f"Treemap data aggregated - "
            f"{len(df_agg)} nodes, "
            f"Value range: [{df_agg[value_col_name].min()}, "
            f"{df_agg[value_col_name].max()}]"
        )

        return df_agg

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create treemap figure from aggregated data.

        Constructs Plotly treemap with configured color mode and styling.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Aggregated treemap data.

        Returns
        -------
        go.Figure
            Configured Plotly treemap.
        """
        logger.debug("Creating treemap figure...")

        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Handle title configuration
        title_config = chart_config.get("title", {})
        if isinstance(title_config, str):
            # Backward compatibility: string title
            show_title = True
            title_text = title_config
            title_x = 0.5
            title_font_size = 16
        else:
            # New format: dict with show, text, x, font
            show_title = title_config.get("show", True)
            title_text = title_config.get("text", "Treemap") if show_title else ""
            title_x = title_config.get("x", 0.5)
            title_font_size = title_config.get("font", {}).get("size", 16)

        # Build path (includes root)
        path = ["root"] + self.path_columns

        # Value column
        value_col = self._aggregated_value_column

        # Create treemap based on color mode
        if self.color_mode == "continuous":
            color_col = self.color_column or value_col
            color_scale = self.plotly_config.get("color_continuous_scale", "Greens")

            fig = px.treemap(
                processed_df,
                path=path,
                values=value_col,
                color=color_col,
                color_continuous_scale=color_scale,
                hover_data={value_col: ":.0f"},
            )

        else:
            color_col = self.color_column or self.path_columns[0]
            color_sequence = self.plotly_config.get("color_discrete_sequence", None)

            treemap_kwargs = {
                "path": path,
                "values": value_col,
                "color": color_col,
                "hover_name": color_col,
                "hover_data": {value_col: ":.0f"},
            }

            if color_sequence:
                treemap_kwargs["color_discrete_sequence"] = color_sequence

            fig = px.treemap(processed_df, **treemap_kwargs)

        # Get layout configuration
        use_autosize = layout_config.get("autosize", False)
        height = layout_config.get("height", 800)
        template = layout_config.get("template", "simple_white")

        # Get margin configuration
        margin_config = layout_config.get("margin", {})
        margin = dict(
            t=margin_config.get("t", 50),
            l=margin_config.get("l", 25),
            r=margin_config.get("r", 25),
            b=margin_config.get("b", 25),
        )

        # Build layout update dict
        layout_updates = {"height": height, "margin": margin, "template": template}

        # Add title if enabled
        if show_title and title_text:
            layout_updates["title"] = {
                "text": title_text,
                "x": title_x,
                "xanchor": "center",
                "font": dict(size=title_font_size),
            }

        # Add autosize or width
        if use_autosize:
            layout_updates["autosize"] = True
        else:
            if layout_config.get("width"):
                layout_updates["width"] = layout_config.get("width")

        # Colorbar for continuous mode
        if self.color_mode == "continuous":
            colorbar_config = chart_config.get("colorbar", {})
            colorbar_title = colorbar_config.get("title", value_col)
            layout_updates["coloraxis_colorbar"] = dict(title=colorbar_title)

        fig.update_layout(**layout_updates)

        # Trace styling
        text_info = chart_config.get("text_info", "label+value")
        text_font_size = chart_config.get("text_font_size", 14)
        fig.update_traces(textinfo=text_info, textfont_size=text_font_size)

        logger.info(
            f"Treemap figure created - "
            f"Height: {height}px, "
            f"Path depth: {len(path)}, "
            f"Autosize: {use_autosize}"
        )

        return fig
