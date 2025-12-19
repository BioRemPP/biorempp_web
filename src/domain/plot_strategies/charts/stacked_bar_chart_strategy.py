"""
Stacked Bar Chart Strategy - 100% Stacked Proportional Visualizations.

This module implements the StackedBarChartStrategy for generating 100% stacked
bar chart visualizations showing proportional contributions of categories to
a total.

Classes
-------
StackedBarChartStrategy
    Strategy for stacked bar chart generation.

Notes
-----
- Validates input data structure
- Groups by category and aggregates values
- Calculates percentages and proportions
- Creates 100% stacked bar chart with Plotly

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class StackedBarChartStrategy(BasePlotStrategy):
    """
    Strategy for 100% stacked bar chart proportional visualizations.

    This strategy creates 100% stacked bar charts showing the proportional
    contribution of each category to the total.

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
    category_column : str
        Name of the column containing categories.
    value_column : str
        Name of the column containing values to aggregate.
    aggregation_function : str
        Aggregation function to apply ('nunique', 'sum', 'count').
    constant_x_label : str
        Label for the constant x-axis.

    Methods
    -------
    validate_data(df)
        Validate input data for stacked bar chart requirements
    process_data(df)
        Process data for stacked bar chart
    create_figure(processed_df)
        Create 100% stacked bar chart figure from processed data

    Notes
    -----
    - Supports flexible category and value columns
    - Configurable aggregation functions
    - Automatic percentage calculation
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
        self.category_column = self.plotly_config.get("category_column", "referenceAG")
        self.value_column = self.plotly_config.get("value_column", "ko")
        self.aggregation_function = self.plotly_config.get(
            "aggregation_function", "nunique"
        )
        self.constant_x_label = self.plotly_config.get("constant_x_label", "Total")

        logger.info(
            f"StackedBarChartStrategy initialized for {self.metadata.get('use_case_id', 'unknown')}: "
            f"category='{self.category_column}', value='{self.value_column}', agg='{self.aggregation_function}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for stacked bar chart requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, required columns missing, or no valid
            data found.
        """
        logger.debug("Starting data validation for StackedBarChartStrategy")

        # Check if DataFrame is empty
        if df.empty:
            raise ValueError("Input DataFrame is empty")

        # Check required columns exist
        required_cols = [self.category_column, self.value_column]
        missing_cols = set(required_cols) - set(df.columns)

        if missing_cols:
            logger.error(
                f"Missing required columns: {missing_cols}. "
                f"Available columns: {df.columns.tolist()}"
            )
            raise ValueError(
                f"Missing required columns for stacked bar chart: {missing_cols}"
            )

        # Check for at least some non-null data
        non_null_count = df[[self.category_column, self.value_column]].dropna().shape[0]
        if non_null_count == 0:
            raise ValueError(
                f"No valid data found: all rows have null values in "
                f"'{self.category_column}' or '{self.value_column}'"
            )

        logger.info(
            f"Data validation passed: {len(df)} rows, {non_null_count} valid rows"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for stacked bar chart: clean, group, aggregate, calculate percentages.

        Cleans data, groups by category, aggregates values, and calculates
        percentages for 100% stacked visualization.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with category and value columns.

        Returns
        -------
        pd.DataFrame
            Processed data with category, count, percent, percent_fmt, and
            x_axis columns.
        """
        logger.debug(
            f"Starting data processing: input shape={df.shape}, "
            f"columns={df.columns.tolist()}"
        )

        # Step 1: Select required columns and drop nulls
        processed_df = df[[self.category_column, self.value_column]].dropna().copy()
        logger.debug(f"After dropping nulls: {processed_df.shape[0]} rows")

        # Step 2: Clean and normalize strings
        # Convert to string and apply strip/upper
        processed_df[self.category_column] = (
            processed_df[self.category_column].astype(str).str.strip().str.upper()
        )
        processed_df[self.value_column] = (
            processed_df[self.value_column].astype(str).str.strip().str.upper()
        )
        logger.debug("String cleaning and normalization complete")

        # Step 3: Drop duplicates before aggregation
        processed_df = processed_df.drop_duplicates()
        logger.debug(f"After dropping duplicates: {processed_df.shape[0]} unique rows")

        # Step 4: Group by category and aggregate
        if self.aggregation_function == "nunique":
            # Count unique values
            counts = (
                processed_df.groupby(self.category_column, as_index=False)[
                    self.value_column
                ]
                .nunique()
                .rename(columns={self.value_column: "count"})
            )
        elif self.aggregation_function == "sum":
            # Sum values (assumes numeric value_column)
            processed_df[self.value_column] = pd.to_numeric(
                processed_df[self.value_column], errors="coerce"
            )
            counts = (
                processed_df.groupby(self.category_column, as_index=False)[
                    self.value_column
                ]
                .sum()
                .rename(columns={self.value_column: "count"})
            )
        elif self.aggregation_function == "count":
            # Count rows
            counts = (
                processed_df.groupby(self.category_column, as_index=False)
                .size()
                .rename(columns={"size": "count"})
            )
        else:
            raise ValueError(
                f"Unsupported aggregation function: '{self.aggregation_function}'. "
                f"Supported: 'nunique', 'sum', 'count'"
            )

        logger.debug(f"After aggregation: {len(counts)} categories")

        # Step 5: Calculate percentages
        total_count = counts["count"].sum()
        counts["percent"] = 100 * counts["count"] / total_count
        logger.debug(
            f"Total count: {total_count}, percentage sum: {counts['percent'].sum():.2f}%"
        )

        # Step 6: Format percentage strings
        counts["percent_fmt"] = counts["percent"].map(lambda x: f"{x:.1f}%")

        # Step 7: Add constant x-axis column
        counts["x_axis"] = self.constant_x_label

        logger.info(
            f"Data processing complete: {len(counts)} categories, "
            f"total={total_count}, columns={counts.columns.tolist()}"
        )

        return counts

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create 100% stacked bar chart figure from processed data.

        Creates Plotly figure with 100% stacked bars, percentage labels,
        and configured styling.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data with category, count, percent, percent_fmt, and
            x_axis columns.

        Returns
        -------
        go.Figure
            Configured Plotly figure with 100% stacked bar.
        """
        logger.debug("Creating stacked bar chart figure")

        # Get Plotly configuration
        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Extract color scheme
        color_scheme = chart_config.get(
            "color_discrete_sequence", px.colors.qualitative.Set3
        )
        if isinstance(color_scheme, str):
            # Handle color scheme name (e.g., "Set3")
            color_scheme = getattr(
                px.colors.qualitative, color_scheme, px.colors.qualitative.Set3
            )

        # Create base figure with Plotly Express
        # Prepare kwargs for px.bar
        bar_kwargs = {
            "data_frame": processed_df,
            "x": "x_axis",
            "y": "count",
            "color": self.category_column,
            "text": "percent_fmt",
            "template": layout_config.get("template", "simple_white"),
            "color_discrete_sequence": color_scheme,
            "height": layout_config.get("height", 520),
        }

        # Only add width if not using autosize
        if not layout_config.get("autosize", False):
            bar_kwargs["width"] = layout_config.get("width", 380)

        fig = px.bar(**bar_kwargs)

        logger.debug("Base figure created with Plotly Express")

        # Apply stacking and normalization
        fig.update_layout(
            barmode="stack",
            barnorm="percent",  # Critical for 100% stacking
        )

        # Apply title configuration
        title_config = chart_config.get("title", {})
        if title_config.get("text"):
            fig.update_layout(
                title={
                    "text": title_config.get("text", ""),
                    "font": {
                        "size": title_config.get("font", {}).get("size", 16),
                        "family": title_config.get("font", {}).get("family", "Arial"),
                        "color": title_config.get("font", {}).get("color", "#2c3e50"),
                    },
                    "x": title_config.get("x", 0.5),
                    "xanchor": title_config.get("xanchor", "center"),
                }
            )

        # Apply axis configuration
        xaxis_config = chart_config.get("xaxis", {})
        yaxis_config = chart_config.get("yaxis", {})

        fig.update_layout(
            xaxis_title=xaxis_config.get("title", None),
            xaxis=dict(
                showticklabels=xaxis_config.get("showticklabels", False),
                title_font=dict(
                    size=xaxis_config.get("title_font", {}).get("size", 14)
                ),
            ),
            yaxis=dict(
                ticksuffix=yaxis_config.get("ticksuffix", "%"),
                title=yaxis_config.get("title", "Percentage"),
                title_font=dict(
                    size=yaxis_config.get("title_font", {}).get("size", 14)
                ),
            ),
        )

        # Apply legend configuration
        legend_config = chart_config.get("legend", {})
        fig.update_layout(
            legend_title_text=legend_config.get(
                "title", self.category_column.capitalize()
            ),
            legend=dict(
                orientation=legend_config.get("orientation", "v"),
                yanchor=legend_config.get("yanchor", "middle"),
                y=legend_config.get("y", 0.5),
                xanchor=legend_config.get("xanchor", "left"),
                x=legend_config.get("x", 1.02),
            ),
        )

        # Apply margins
        margin_config = layout_config.get("margin", {})
        fig.update_layout(
            margin=dict(
                l=margin_config.get("l", 50),
                r=margin_config.get("r", 150),
                t=margin_config.get("t", 80),
                b=margin_config.get("b", 50),
            )
        )

        # Configure traces (text and hover)
        hover_template = chart_config.get(
            "hovertemplate",
            f"{self.category_column.capitalize()}=%{{customdata[0]}}<br>"
            f"Count=%{{y}}<br>"
            f"Share=%{{customdata[1]}}",
        )

        fig.update_traces(
            textposition="inside",
            insidetextanchor="middle",
            hovertemplate=hover_template,
            customdata=processed_df[[self.category_column, "percent_fmt"]].to_numpy(),
        )

        logger.info(
            f"Figure created: {len(processed_df)} categories, "
            f"barmode=stack, barnorm=percent"
        )

        return fig
