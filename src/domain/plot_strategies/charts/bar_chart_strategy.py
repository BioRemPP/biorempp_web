"""
Bar Chart Strategy.

This module implements the BarChartStrategy class following the
Strategy Pattern, providing specific logic for generating bar chart
visualizations with flexible configuration.

Classes
-------
BarChartStrategy
    Concrete strategy for bar chart generation

Notes
-----
This strategy supports:
- Horizontal and vertical bar orientations
- Data filtering before aggregation
- Flexible grouping and counting operations
- Custom styling from YAML configuration

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class BarChartStrategy(BasePlotStrategy):
    """
    Bar chart strategy for ranking and comparison visualizations.

    This strategy supports both horizontal and vertical bar charts with
    flexible data processing including filtering, grouping, counting,
    and sorting operations.

    Attributes
    ----------
    data_config : Dict[str, Any]
        Data processing configuration
    plotly_config : Dict[str, Any]
        Plotly-specific configuration

    Notes
    -----
    Refer to the official documentation for supported use cases and
    detailed configuration examples.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize bar chart strategy.

        Parameters
        ----------
        config : Dict[str, Any]
            Complete configuration from YAML file
        """
        super().__init__(config)
        self.data_config = config.get("data", {})
        self.plotly_config = self.viz_config.get("plotly", {})
        use_case = self.metadata.get("use_case_id")
        logger.info(f"BarChartStrategy initialized for {use_case}")

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for bar chart requirements.

        Validation rules applied (from YAML config):
        - DataFrame not empty
        - Required columns exist ('sample', 'KO')
        - No null values in critical columns
        - Minimum number of samples

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate

        Raises
        ------
        ValueError
            If any validation rule fails
        """
        logger.debug("Starting data validation for BarChartStrategy")

        # Get validation rules from config
        rules = self.validation_rules.get("rules", [])

        logger.debug(f"Validating with {len(rules)} rules")
        logger.debug(f"DataFrame columns: {df.columns.tolist()}")

        for rule in rules:
            rule_name = rule.get("rule")
            logger.debug(f"Applying rule: {rule_name}")

            if rule_name == "not_empty":
                if df.empty:
                    raise ValueError(rule.get("message", "DataFrame is empty"))

            elif rule_name == "required_columns":
                required_cols = rule.get("columns", [])
                logger.debug(f"Required columns: {required_cols}")
                missing_cols = set(required_cols) - set(df.columns)
                if missing_cols:
                    logger.error(
                        f"Missing columns: {missing_cols}. "
                        f"Available: {df.columns.tolist()}"
                    )
                    raise ValueError(
                        f"{rule.get('message', 'Missing columns')}: " f"{missing_cols}"
                    )

            elif rule_name == "no_nulls":
                null_cols = rule.get("columns", [])
                for col in null_cols:
                    if col in df.columns and df[col].isnull().any():
                        raise ValueError(
                            f"{rule.get('message', 'Null values found')}: column '{col}'"
                        )

            elif rule_name == "minimum_samples":
                min_count = rule.get("min_count", 1)
                if len(df) < min_count:
                    raise ValueError(
                        f"{rule.get('message', 'Insufficient samples')}: "
                        f"{len(df)} < {min_count}"
                    )

        logger.info(f"Data validation passed: {len(df)} rows")

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for bar chart: filter, group, count, sort.

        Processing pipeline (from YAML config):
        1. Validate structure (handled by validate_data)
        2. Filter data (optional - remove unwanted rows)
        3. Group by specified column
        4. Count/aggregate values per group
        5. Rename result column
        6. Sort by count (ascending or descending)

        Parameters
        ----------
        df : pd.DataFrame
            Input data with required columns

        Returns
        -------
        pd.DataFrame
            Processed data ready for visualization (sorted by aggregated
            values)
        """
        processing_steps = self.data_config.get("processing", {}).get("steps", [])
        processed_df = df.copy()

        for step in processing_steps:
            if not step.get("enabled", True):
                continue

            step_name = step.get("name")
            params = step.get("params", {})

            if step_name == "validate":
                # Validation already done in validate_data()
                continue

            elif step_name == "filter":
                # Filter data based on conditions
                filter_col = params.get("column")
                filter_op = params.get("operator", "!=")
                filter_val = params.get("value")

                logger.debug(f"Filtering: {filter_col} {filter_op} {filter_val}")

                initial_count = len(processed_df)

                if filter_op == "!=":
                    processed_df = processed_df[processed_df[filter_col] != filter_val]
                elif filter_op == "==":
                    processed_df = processed_df[processed_df[filter_col] == filter_val]
                elif filter_op == ">":
                    processed_df = processed_df[processed_df[filter_col] > filter_val]
                elif filter_op == "<":
                    processed_df = processed_df[processed_df[filter_col] < filter_val]
                elif filter_op == ">=":
                    processed_df = processed_df[processed_df[filter_col] >= filter_val]
                elif filter_op == "<=":
                    processed_df = processed_df[processed_df[filter_col] <= filter_val]
                elif filter_op == "in":
                    processed_df = processed_df[
                        processed_df[filter_col].isin(filter_val)
                    ]
                elif filter_op == "not_in":
                    processed_df = processed_df[
                        ~processed_df[filter_col].isin(filter_val)
                    ]

                filtered_count = len(processed_df)
                logger.info(
                    f"After filtering: {initial_count} -> {filtered_count} rows "
                    f"({initial_count - filtered_count} removed)"
                )

            elif step_name == "group_and_count":
                # Group by column and count/aggregate values
                group_col = params.get("group_by", "sample")
                agg_col = params.get("agg_column", "KO")
                agg_func = params.get("agg_function", "nunique")
                result_col = params.get("result_column", "ko_count")

                logger.debug(
                    f"Grouping by '{group_col}' and applying "
                    f"'{agg_func}' on '{agg_col}'"
                )

                processed_df = (
                    processed_df.groupby(group_col)[agg_col]
                    .agg(agg_func)
                    .reset_index()
                    .rename(columns={agg_col: result_col})
                )

                logger.info(
                    f"After grouping: shape={processed_df.shape}, "
                    f"columns={processed_df.columns.tolist()}"
                )

            elif step_name == "sort":
                # Sort by specified column
                sort_col = params.get("by", "ko_count")
                ascending = params.get("ascending", False)

                logger.debug(f"Sorting by '{sort_col}' (ascending={ascending})")

                processed_df = processed_df.sort_values(
                    by=sort_col, ascending=ascending
                )

        logger.info(f"Data processing complete: {len(processed_df)} rows processed")
        return processed_df

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create bar chart figure from processed data.

        Uses Plotly Express for initial figure creation, then applies
        additional layout customizations from YAML configuration.

        Configuration applied:
        - Chart type (bar) with horizontal/vertical orientation
        - Colors (color_discrete_sequence)
        - Text labels on bars (optional)
        - Title (text, font, position)
        - Axis labels and styling
        - Layout (height, width, template, margins)
        - Hover behavior

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data with configured columns

        Returns
        -------
        go.Figure
            Configured Plotly bar chart
        """

        # Extract configuration
        x_col = self.plotly_config.get("x", "sample")
        y_col = self.plotly_config.get("y", "ko_count")
        orientation = self.plotly_config.get("orientation", "v")
        title_config = self.plotly_config.get("title", {})
        labels = self.plotly_config.get("labels", {})
        colors = self.plotly_config.get("color_discrete_sequence", ["#4682B4"])

        # Get color configuration (for continuous scales)
        color_col = self.plotly_config.get("color")
        color_continuous_scale = self.plotly_config.get("color_continuous_scale")

        # Create bar chart
        # NOTE: px.bar automatically handles orientation internally
        # For orientation='h': x is numeric (values), y is categorical (labels)
        # For orientation='v': x is categorical (labels), y is numeric (values)

        # Build px.bar arguments
        bar_args = {
            "data_frame": processed_df,
            "x": x_col,
            "y": y_col,
            "orientation": orientation,
            "labels": labels,
        }

        # Add color configuration if specified
        if color_col and color_continuous_scale:
            bar_args["color"] = color_col
            bar_args["color_continuous_scale"] = color_continuous_scale
            logger.debug(
                f"Using continuous color scale: {color_continuous_scale} on column '{color_col}'"
            )
        else:
            bar_args["color_discrete_sequence"] = colors
            logger.debug(f"Using discrete color sequence: {colors}")

        fig = px.bar(**bar_args)

        logger.info(f"Bar chart created successfully with orientation='{orientation}'")

        # Apply layout configuration
        layout_config = self.plotly_config.get("layout", {})

        # Get title display setting
        show_title = title_config.get("show", True)

        # Get autosize setting
        use_autosize = layout_config.get("autosize", False)

        # Build layout update dict
        layout_update = {
            "height": layout_config.get("height", 500),
            "template": layout_config.get("template", "simple_white"),
            "xaxis": layout_config.get("xaxis", {}),
            "yaxis": layout_config.get("yaxis", {}),
            "hovermode": layout_config.get("hovermode", "closest"),
            "hoverlabel": layout_config.get("hoverlabel", {}),
            "margin": layout_config.get("margin", {}),
        }

        # Add autosize if enabled
        if use_autosize:
            layout_update["autosize"] = True
            logger.debug("Autosize enabled - width will not be set")
        else:
            # Only set width if not using autosize
            if layout_config.get("width"):
                layout_update["width"] = layout_config.get("width")
                logger.debug(f"Fixed width set: {layout_config.get('width')}")

        # Add title if enabled
        if show_title and title_config.get("text"):
            layout_update["title"] = {
                "text": title_config.get("text", ""),
                "x": title_config.get("x", 0.5),
                "xanchor": title_config.get("xanchor", "center"),
                "font": title_config.get("font", {}),
            }

        fig.update_layout(**layout_update)

        logger.info("Bar chart figure created successfully")
        return fig
