"""
Density Plot Strategy.

This module implements the DensityPlotStrategy class following the
Strategy Pattern, providing specific logic for generating overlaid
density distribution visualizations with flexible configuration.

Classes
-------
DensityPlotStrategy
    Concrete strategy for density plot generation

Notes
-----
This strategy supports:
- Overlaid density curves for multiple groups
- Semi-transparent fill under curves
- Probability density estimation (KDE)
- Custom styling from YAML configuration
- Horizontal legend below chart

Technical Details:
- Uses Plotly's figure_factory.create_distplot for KDE
- Supports grouping by categorical variables
- Hides histogram and rug plot (shows only density curves)
- Auto-configures legend positioning
- Applies opacity for visual clarity when curves overlap

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict, List

import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class DensityPlotStrategy(BasePlotStrategy):
    """
    Density plot strategy for distribution visualization.

    This strategy creates overlaid probability density curves to visualize
    and compare distributions across multiple groups.

    The density plot uses Kernel Density Estimation (KDE) to show smooth
    probability distributions, making it ideal for comparing continuous
    distributions across categorical groups.

    Attributes
    ----------
    data_config : Dict[str, Any]
        Data processing configuration from YAML
    plotly_config : Dict[str, Any]
        Plotly-specific configuration from YAML

    Notes
    -----
    Configuration Structure (YAML):
        visualization:
          strategy: "DensityPlotStrategy"
          plotly:
            # Required: Data configuration
            value_column: "toxicity_score"      # Numeric column for density
            group_column: "endpoint"            # Categorical grouping column

            # Optional: Chart styling
            chart:
              title:
                text: "Distribution Plot"
              show_hist: false                  # Hide histogram bars
              show_rug: false                   # Hide rug plot
              fill: "tozeroy"                   # Fill under curve
              opacity: 0.5                      # Curve transparency

            # Optional: Layout configuration
            layout:
              template: "simple_white"          # Plotly template
              height: 800                       # Chart height
              width: 1200                       # Chart width
              xaxis:
                title: "Value"
              yaxis:
                title: "Probability Density"
                gridcolor: "lightgray"
              legend:
                orientation: "h"                # Horizontal legend
                yanchor: "bottom"
                y: 0                            # Legend position
                xanchor: "center"
                x: 0.5
                title_text: "Group"

    Refer to the official documentation for supported use cases and
    detailed configuration examples.

    See Also
    --------
    BasePlotStrategy : Abstract base class
    plotly.figure_factory.create_distplot : Plotly density plot documentation
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize density plot strategy.

        Parameters
        ----------
        config : Dict[str, Any]
            Complete configuration from YAML file
        """
        super().__init__(config)
        self.data_config = config.get("data", {})
        self.plotly_config = self.viz_config.get("plotly", {})
        use_case = self.metadata.get("use_case_id")
        logger.info(f"DensityPlotStrategy initialized for {use_case}")

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for density plot requirements.

        Validation rules applied:
        - DataFrame not empty
        - Required columns exist (value_column, group_column)
        - value_column contains numeric data
        - At least one group exists
        - Each group has sufficient data points for KDE

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate

        Raises
        ------
        ValueError
            If any validation rule fails
        """
        logger.debug("Starting data validation for DensityPlotStrategy")

        # Check DataFrame not empty
        if df.empty:
            raise ValueError("DataFrame is empty - cannot create density plot")

        # Get required columns from config
        value_col = self.plotly_config.get("value_column")
        group_col = self.plotly_config.get("group_column")

        if not value_col or not group_col:
            raise ValueError(
                "Configuration error: 'value_column' and 'group_column' "
                "must be specified in plotly config"
            )

        # Validate required columns exist
        required_cols = [value_col, group_col]
        missing_cols = set(required_cols) - set(df.columns)

        if missing_cols:
            logger.error(
                f"Missing columns: {missing_cols}. " f"Available: {df.columns.tolist()}"
            )
            raise ValueError(
                f"Missing required columns for density plot: {missing_cols}"
            )

        # Validate value_column is numeric
        if not pd.api.types.is_numeric_dtype(df[value_col]):
            raise ValueError(
                f"Column '{value_col}' must be numeric for density plot. "
                f"Found type: {df[value_col].dtype}"
            )

        # Check for at least one valid group
        unique_groups = df[group_col].dropna().unique()
        if len(unique_groups) == 0:
            raise ValueError(f"No valid groups found in column '{group_col}'")

        # Check each group has sufficient data (minimum 2 points for KDE)
        for group in unique_groups:
            group_data = df[df[group_col] == group][value_col].dropna()
            if len(group_data) < 2:
                logger.warning(
                    f"Group '{group}' has only {len(group_data)} data points. "
                    f"Minimum 2 required for KDE. Group will be skipped."
                )

        logger.info(
            f"Data validation passed: {len(df)} rows, "
            f"{len(unique_groups)} groups, "
            f"value='{value_col}', group='{group_col}'"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for density plot visualization.

        Processing steps:
        1. Extract configuration (value_column, group_column)
        2. Remove NaN values from both columns
        3. Sort groups alphabetically for consistent ordering
        4. Filter out groups with insufficient data points
        5. Return cleaned DataFrame

        Parameters
        ----------
        df : pd.DataFrame
            Validated input data

        Returns
        -------
        pd.DataFrame
            Processed data ready for density plot (contains only rows with
            valid value and group data)
        """
        logger.debug("Starting data processing for DensityPlotStrategy")

        # Extract configuration
        value_col = self.plotly_config.get("value_column")
        group_col = self.plotly_config.get("group_column")

        logger.info(f"Processing: value='{value_col}', group='{group_col}'")

        # Remove NaN values
        processed_df = df[[value_col, group_col]].copy()
        initial_rows = len(processed_df)
        processed_df = processed_df.dropna()
        removed_rows = initial_rows - len(processed_df)

        if removed_rows > 0:
            logger.info(f"Removed {removed_rows} rows with NaN values")

        # Get unique groups and their counts
        group_counts = processed_df[group_col].value_counts()
        logger.info(
            f"Groups found: {len(group_counts)}, "
            f"data range: [{processed_df[value_col].min():.3f}, "
            f"{processed_df[value_col].max():.3f}]"
        )

        # Log groups with insufficient data
        insufficient = group_counts[group_counts < 2]
        if len(insufficient) > 0:
            logger.warning(
                f"Groups with <2 points (will be filtered): "
                f"{insufficient.index.tolist()}"
            )
            # Filter out groups with insufficient data
            processed_df = processed_df[
                processed_df[group_col].isin(group_counts[group_counts >= 2].index)
            ]

        logger.info(
            f"Data processed: {len(processed_df)} rows, "
            f"{processed_df[group_col].nunique()} valid groups"
        )

        return processed_df

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create Plotly density plot from processed data.

        Creates overlaid density curves using figure_factory.create_distplot:
        - One curve per group
        - Semi-transparent fill under curves
        - Kernel Density Estimation (KDE) for smooth curves
        - Horizontal legend below chart
        - No histogram or rug plot

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data with value and group columns

        Returns
        -------
        go.Figure
            Configured Plotly figure with density plot

        Notes
        -----
        Chart Configuration:
        - Overlaid KDE curves
        - Fill to zero (tozeroy)
        - Configurable opacity for overlaps
        - Horizontal legend
        - Grid lines on y-axis
        """
        logger.debug("Creating density plot figure")

        # Extract configuration
        value_col = self.plotly_config.get("value_column")
        group_col = self.plotly_config.get("group_column")
        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Get styling parameters with defaults
        show_hist = chart_config.get("show_hist", False)
        show_rug = chart_config.get("show_rug", False)
        opacity = chart_config.get("opacity", 0.5)
        fill = chart_config.get("fill", "tozeroy")

        # Prepare data for create_distplot
        # Need list of arrays, one per group
        groups = sorted(processed_df[group_col].unique())
        hist_data: List[pd.Series] = []
        group_labels: List[str] = []

        for group in groups:
            group_data = processed_df[processed_df[group_col] == group][value_col]

            # Only include groups with sufficient data
            if len(group_data) >= 2:
                hist_data.append(group_data)
                group_labels.append(str(group))
                logger.debug(
                    f"Group '{group}': {len(group_data)} points, "
                    f"range [{group_data.min():.3f}, {group_data.max():.3f}]"
                )

        if not hist_data:
            logger.error("No valid groups with sufficient data for KDE")
            raise ValueError(
                "No valid groups found. Each group needs at least 2 data points."
            )

        logger.info(
            f"Creating density plot for {len(hist_data)} groups: " f"{group_labels}"
        )

        # Create distribution plot
        fig = ff.create_distplot(
            hist_data, group_labels, show_hist=show_hist, show_rug=show_rug
        )

        # Apply fill and opacity to each trace
        for trace in fig.data:
            trace.fill = fill
            trace.opacity = opacity

        # Extract layout configuration
        title_config = chart_config.get("title", {})
        show_title = title_config.get("show", True)
        title_text = title_config.get("text", "") if show_title else ""
        title_x = title_config.get("x", 0.5)

        xaxis_config = layout_config.get("xaxis", {})
        yaxis_config = layout_config.get("yaxis", {})
        legend_config = layout_config.get("legend", {})

        # Get height and autosize
        height = layout_config.get("height", 800)
        use_autosize = layout_config.get("autosize", False)

        # Build layout update dict
        layout_update = {
            "title": title_text,
            "title_x": title_x,
            "template": layout_config.get("template", "simple_white"),
            "height": height,
            "xaxis": dict(
                title=xaxis_config.get("title", "Value"),
                **{k: v for k, v in xaxis_config.items() if k != "title"},
            ),
            "yaxis": dict(
                title=yaxis_config.get("title", "Probability Density"),
                gridcolor=yaxis_config.get("gridcolor", "lightgray"),
                **{
                    k: v
                    for k, v in yaxis_config.items()
                    if k not in ["title", "gridcolor"]
                },
            ),
            "legend": dict(
                orientation=legend_config.get("orientation", "h"),
                yanchor=legend_config.get("yanchor", "bottom"),
                y=legend_config.get("y", 0),
                xanchor=legend_config.get("xanchor", "center"),
                x=legend_config.get("x", 0.5),
                title_text=legend_config.get("title_text", "Group"),
            ),
        }

        # Add autosize or width
        if use_autosize:
            layout_update["autosize"] = True
        else:
            if layout_config.get("width"):
                layout_update["width"] = layout_config.get("width", 1200)

        fig.update_layout(**layout_update)

        logger.info(
            f"Density plot created: {len(hist_data)} curves, "
            f"opacity={opacity}, fill={fill}"
        )

        return fig
