"""
Dot Plot Strategy - Scatter and Bubble Chart Visualizations.

This module implements the DotPlotStrategy for creating scatter plots and
bubble charts using Plotly. Supports both simple scatter plots with uniform
markers and bubble charts with size/color encoding for quantitative variables.

Classes
-------
DotPlotStrategy
    Strategy for creating scatter and bubble chart visualizations.

Notes
-----
- Supports simple scatter plots and bubble charts
- Flexible axis mappings (categorical or continuous)
- Data aggregation and filtering capabilities

For supported use cases, refer to the official documentation.
"""

from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy
from src.shared.logging import get_logger

logger = get_logger(__name__)


class DotPlotStrategy(BasePlotStrategy):
    """
    Strategy for creating scatter and bubble chart visualizations.

    This strategy creates scatter-based visualizations with flexible
    configuration for both simple scatter plots and bubble charts with
    size and color encoding.

    Parameters
    ----------
    config : Dict[str, Any]
        Complete configuration dictionary from YAML.
        Must contain 'visualization' section with plot parameters.

    Attributes
    ----------
    config : Dict[str, Any]
        Stored configuration dictionary.
    data_config : Dict[str, Any]
        Data processing configuration.
    plotly_config : Dict[str, Any]
        Plotly-specific visualization config.

    Methods
    -------
    validate_data(df)
        Validate input data for dot plot requirements
    process_data(df)
        Process data with filtering, grouping, and sorting
    create_figure(processed_df)
        Create dot plot figure from processed data
    generate(data)
        Generate complete dot plot visualization

    Notes
    -----
    - Supports simple scatter and bubble chart modes
    - Flexible axis mappings (categorical or continuous)
    - Data aggregation and filtering capabilities
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
        logger.info("DotPlotStrategy initialized")

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for dot plot requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, required columns missing, or x/y columns
            not found in data.
        """
        logger.debug("Starting data validation for DotPlotStrategy")

        # Check if DataFrame is empty
        if df.empty:
            raise ValueError("DataFrame is empty")

        # Get required columns from config
        required_cols = self.data_config.get("required_columns", [])

        if required_cols:
            missing_cols = set(required_cols) - set(df.columns)
            if missing_cols:
                raise ValueError(
                    f"Missing required columns: {missing_cols}. "
                    f"Available: {df.columns.tolist()}"
                )

        # Validate x and y columns from scatter config
        scatter_config = self.plotly_config.get("scatter", {})
        x_col = scatter_config.get("x")
        y_col = scatter_config.get("y")

        if not x_col or not y_col:
            raise ValueError(
                "Configuration must specify 'x' and 'y' in "
                "'visualization.plotly.scatter'"
            )

        if x_col not in df.columns:
            raise ValueError(f"X column '{x_col}' not found in data")

        if y_col not in df.columns:
            raise ValueError(f"Y column '{y_col}' not found in data")

        # Validate size/color columns if bubble mode
        # NOTE: Skip validation for columns created during processing
        # (e.g., 'unique_ko_count' created by group_and_count step)
        mode = scatter_config.get("mode", "simple")
        if mode == "bubble":
            size_col = scatter_config.get("size")
            color_col = scatter_config.get("color")

            # Check if column will be created during processing
            processing_steps = self.data_config.get("processing", {}).get("steps", [])
            result_columns = []
            for step in processing_steps:
                if step.get("name") == "group_and_count":
                    result_col = step.get("params", {}).get("result_column")
                    if result_col:
                        result_columns.append(result_col)

            # Only validate if column is not created by processing
            if (
                size_col
                and size_col not in df.columns
                and size_col not in result_columns
            ):
                raise ValueError(
                    f"Size column '{size_col}' not found in data and "
                    f"not created by processing steps"
                )

            if (
                color_col
                and color_col not in df.columns
                and color_col not in result_columns
            ):
                raise ValueError(
                    f"Color column '{color_col}' not found in data and "
                    f"not created by processing steps"
                )

        logger.info(f"Data validation passed: {len(df)} rows")

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for dot plot visualization.

        Applies processing steps defined in configuration including filtering,
        grouping, aggregation, and sorting.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.

        Returns
        -------
        pd.DataFrame
            Processed data ready for visualization.
        """
        logger.debug(f"Processing data: {len(df)} rows")

        processed_df = df.copy()

        # Get processing steps from config
        processing_steps = self.data_config.get("processing", {}).get("steps", [])

        for step in processing_steps:
            step_name = step.get("name")
            enabled = step.get("enabled", True)

            if not enabled:
                logger.debug(f"Skipping disabled step: {step_name}")
                continue

            params = step.get("params", {})

            if step_name == "filter":
                processed_df = self._apply_filter_step(processed_df, params)
            elif step_name == "group_and_count":
                processed_df = self._apply_grouping_step(processed_df, params)
            elif step_name == "sort":
                processed_df = self._apply_sort_step(processed_df, params)
            else:
                logger.warning(f"Unknown processing step: {step_name}")

        logger.info(
            f"Data processing completed: {len(processed_df)} rows "
            f"(from {len(df)} original rows)"
        )

        return processed_df

    def _apply_filter_step(
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Apply filter step to data.

        Parameters
        ----------
        df : pd.DataFrame
            Data to filter.
        params : Dict[str, Any]
            Filter parameters:
            - column: Column name to filter
            - operator: Comparison operator ('==', '!=', '>', '<', etc.)
            - value: Value to compare against

        Returns
        -------
        pd.DataFrame
            Filtered data.
        """
        column = params.get("column")
        operator = params.get("operator")
        value = params.get("value")

        if not all([column, operator]):
            logger.warning("Filter step missing required parameters")
            return df

        if column not in df.columns:
            logger.warning(f"Filter column '{column}' not found in data")
            return df

        initial_rows = len(df)

        if operator == "==":
            filtered_df = df[df[column] == value]
        elif operator == "!=":
            filtered_df = df[df[column] != value]
        elif operator == ">":
            filtered_df = df[df[column] > value]
        elif operator == "<":
            filtered_df = df[df[column] < value]
        elif operator == ">=":
            filtered_df = df[df[column] >= value]
        elif operator == "<=":
            filtered_df = df[df[column] <= value]
        else:
            logger.warning(f"Unknown operator: {operator}")
            return df

        logger.info(
            f"Filter applied: {column} {operator} {value} - "
            f"{initial_rows} → {len(filtered_df)} rows"
        )

        return filtered_df

    def _apply_grouping_step(
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Apply group and count aggregation step.

        Parameters
        ----------
        df : pd.DataFrame
            Data to aggregate.
        params : Dict[str, Any]
            Grouping parameters:
            - group_by: Column(s) to group by (str or list)
            - agg_column: Column to aggregate
            - agg_function: Aggregation function ('nunique', 'count', 'sum')
            - result_column: Name for result column

        Returns
        -------
        pd.DataFrame
            Aggregated data.
        """
        group_by = params.get("group_by")
        agg_column = params.get("agg_column")
        agg_function = params.get("agg_function", "nunique")
        result_column = params.get("result_column", "count")

        if not group_by or not agg_column:
            logger.warning("Grouping step missing required parameters")
            return df

        # Ensure group_by is a list
        if isinstance(group_by, str):
            group_by = [group_by]

        # Check if columns exist
        missing_cols = set(group_by + [agg_column]) - set(df.columns)
        if missing_cols:
            logger.warning(f"Grouping columns not found: {missing_cols}")
            return df

        initial_rows = len(df)

        # Apply aggregation
        if agg_function == "nunique":
            agg_df = (
                df.groupby(group_by)[agg_column]
                .nunique()
                .reset_index()
                .rename(columns={agg_column: result_column})
            )
        elif agg_function == "count":
            agg_df = (
                df.groupby(group_by)[agg_column]
                .count()
                .reset_index()
                .rename(columns={agg_column: result_column})
            )
        elif agg_function == "sum":
            agg_df = (
                df.groupby(group_by)[agg_column]
                .sum()
                .reset_index()
                .rename(columns={agg_column: result_column})
            )
        else:
            logger.warning(f"Unknown aggregation function: {agg_function}")
            return df

        logger.info(
            f"Grouping applied: GROUP BY {group_by}, "
            f"{agg_function}({agg_column}) - "
            f"{initial_rows} → {len(agg_df)} rows"
        )

        return agg_df

    def _apply_sort_step(
        self, df: pd.DataFrame, params: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Apply sorting step to data.

        Parameters
        ----------
        df : pd.DataFrame
            Data to sort.
        params : Dict[str, Any]
            Sorting parameters:
            - by: Column(s) to sort by
            - ascending: Sort order (default: True)

        Returns
        -------
        pd.DataFrame
            Sorted data.
        """
        sort_by = params.get("by")
        ascending = params.get("ascending", True)

        if not sort_by:
            logger.warning("Sort step missing 'by' parameter")
            return df

        if isinstance(sort_by, str):
            sort_by = [sort_by]

        missing_cols = set(sort_by) - set(df.columns)
        if missing_cols:
            logger.warning(f"Sort columns not found: {missing_cols}")
            return df

        sorted_df = df.sort_values(by=sort_by, ascending=ascending)

        logger.info(f"Sorting applied: by={sort_by}, ascending={ascending}")

        return sorted_df

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create dot plot figure from processed data.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data ready for visualization.

        Returns
        -------
        go.Figure
            Plotly figure (scatter or bubble chart).
        """
        return self.generate(processed_df)

    def generate(self, data: pd.DataFrame) -> go.Figure:
        """
        Generate dot plot (scatter or bubble chart).

        Parameters
        ----------
        data : pd.DataFrame
            Processed data ready for visualization.

        Returns
        -------
        go.Figure
            Plotly figure with scatter plot or bubble chart.

        Raises
        ------
        ValueError
            If data is empty or required configuration missing.
        """
        logger.info("Generating dot plot", extra={"rows": len(data)})

        # Validate data
        if data.empty:
            raise ValueError("Cannot create plot: DataFrame is empty")

        # Extract configuration
        scatter_config = self.plotly_config.get("scatter", {})
        layout_config = self.plotly_config.get("layout", {})

        # Get plot mode
        mode = scatter_config.get("mode", "simple")

        # Create figure based on mode
        if mode == "bubble":
            fig = self._create_bubble_chart(data, scatter_config)
        else:
            fig = self._create_simple_scatter(data, scatter_config)

        # Apply layout
        fig = self._apply_layout(fig, layout_config, scatter_config)

        logger.info(
            "Dot plot generated successfully", extra={"mode": mode, "points": len(data)}
        )

        return fig

    def _create_simple_scatter(
        self, data: pd.DataFrame, scatter_config: Dict[str, Any]
    ) -> go.Figure:
        """
        Create simple scatter plot with fixed marker properties.

        Parameters
        ----------
        data : pd.DataFrame
            Data for plotting.
        scatter_config : Dict[str, Any]
            Scatter configuration from YAML.

        Returns
        -------
        go.Figure
            Plotly scatter plot figure.
        """
        x_col = scatter_config.get("x")
        y_col = scatter_config.get("y")
        hover_name = scatter_config.get("hover_name")
        hover_data = scatter_config.get("hover_data", {})

        # Get marker configuration
        marker_config = scatter_config.get("marker", {})
        marker_color = marker_config.get("color", "mediumseagreen")
        marker_size = marker_config.get("size", 10)

        fig = px.scatter(
            data, x=x_col, y=y_col, hover_name=hover_name, hover_data=hover_data
        )

        # Update marker style
        fig.update_traces(marker=dict(size=marker_size, color=marker_color))

        logger.debug(f"Simple scatter created: {len(data)} points")

        return fig

    def _create_bubble_chart(
        self, data: pd.DataFrame, scatter_config: Dict[str, Any]
    ) -> go.Figure:
        """
        Create bubble chart with size and color encoding.

        Parameters
        ----------
        data : pd.DataFrame
            Data for plotting.
        scatter_config : Dict[str, Any]
            Scatter configuration from YAML.

        Returns
        -------
        go.Figure
            Plotly figure with bubble chart.
        """
        x_col = scatter_config.get("x")
        y_col = scatter_config.get("y")
        size_col = scatter_config.get("size")
        color_col = scatter_config.get("color")
        hover_name = scatter_config.get("hover_name")
        hover_data = scatter_config.get("hover_data", {})
        color_scale = scatter_config.get("color_continuous_scale", "Viridis")
        size_max = scatter_config.get("size_max", 30)

        fig = px.scatter(
            data,
            x=x_col,
            y=y_col,
            size=size_col,
            color=color_col,
            hover_name=hover_name,
            hover_data=hover_data,
            color_continuous_scale=color_scale,
            size_max=size_max,
        )

        # Configure integer ticks for color bar if needed
        if color_col and color_col in data.columns:
            min_val = int(data[color_col].min())
            max_val = int(data[color_col].max())

            if max_val > min_val and max_val - min_val <= 15:
                tick_values = list(range(min_val, max_val + 1))
                fig.update_layout(
                    coloraxis_colorbar=dict(
                        title=scatter_config.get("colorbar_title", color_col),
                        tickvals=tick_values,
                        ticktext=[str(v) for v in tick_values],
                    )
                )

        logger.debug(f"Bubble chart created: {len(data)} points")

        return fig

    def _apply_layout(
        self,
        fig: go.Figure,
        layout_config: Dict[str, Any],
        scatter_config: Dict[str, Any],
    ) -> go.Figure:
        """
        Apply layout configuration to figure.

        Parameters
        ----------
        fig : go.Figure
            Figure to apply layout to.
        layout_config : Dict[str, Any]
            Layout configuration from YAML.
        scatter_config : Dict[str, Any]
            Scatter configuration (for additional context).

        Returns
        -------
        go.Figure
            Figure with layout applied.
        """
        # Get axis configurations
        xaxis_config = layout_config.get("xaxis", {})
        yaxis_config = layout_config.get("yaxis", {})

        # Handle title configuration (support both string and dict)
        title_config = layout_config.get("title", {})
        if isinstance(title_config, str):
            # Backward compatibility: string title
            show_title = bool(title_config)
            title_text = title_config
            title_x = 0.5
        else:
            # New format: dict with show, text, x
            show_title = title_config.get("show", True)
            title_text = title_config.get("text", "") if show_title else ""
            title_x = title_config.get("x", 0.5)

        # Get layout options
        template = layout_config.get("template", "simple_white")
        height = layout_config.get("height", 600)
        use_autosize = layout_config.get("autosize", False)
        plot_bgcolor = layout_config.get("plot_bgcolor", "white")
        paper_bgcolor = layout_config.get("paper_bgcolor", "white")
        font_config = layout_config.get("font", {})
        margin_config = layout_config.get("margin", {})
        hovermode = layout_config.get("hovermode", "closest")

        # Get legend configuration
        legend_config = layout_config.get("legend", {})

        # Build layout update dict
        layout_update = {
            "title": dict(text=title_text, x=title_x, xanchor="center"),
            "xaxis": dict(
                title=xaxis_config.get("title", ""),
                tickangle=xaxis_config.get("tickangle", -45),
                showgrid=xaxis_config.get("showgrid", True),
                gridcolor=xaxis_config.get("gridcolor", "#e0e0e0"),
                **{
                    k: v
                    for k, v in xaxis_config.items()
                    if k not in ["title", "tickangle", "showgrid", "gridcolor"]
                },
            ),
            "yaxis": dict(
                title=yaxis_config.get("title", ""),
                tickangle=yaxis_config.get("tickangle", 0),
                showgrid=yaxis_config.get("showgrid", True),
                gridcolor=yaxis_config.get("gridcolor", "#e0e0e0"),
                **{
                    k: v
                    for k, v in yaxis_config.items()
                    if k not in ["title", "tickangle", "showgrid", "gridcolor"]
                },
            ),
            "template": template,
            "height": height,
            "plot_bgcolor": plot_bgcolor,
            "paper_bgcolor": paper_bgcolor,
            "font": font_config,
            "margin": margin_config,
            "hovermode": hovermode,
        }

        # Add legend configuration if provided
        if legend_config:
            layout_update["legend"] = dict(
                orientation=legend_config.get("orientation", "v"),
                yanchor=legend_config.get("yanchor", "top"),
                y=legend_config.get("y", 1),
                xanchor=legend_config.get("xanchor", "left"),
                x=legend_config.get("x", 1.02),
                title_text=legend_config.get("title_text", ""),
                **{
                    k: v
                    for k, v in legend_config.items()
                    if k
                    not in ["orientation", "yanchor", "y", "xanchor", "x", "title_text"]
                },
            )

        # Add autosize or width
        if use_autosize:
            layout_update["autosize"] = True
        else:
            if layout_config.get("width"):
                layout_update["width"] = layout_config.get("width", 800)

        fig.update_layout(**layout_update)

        return fig
