"""
Radar Chart Strategy - Polar/Radar Chart Visualizations.

This module implements the RadarChartStrategy for generating radar/polar chart
visualizations with flexible configuration.

Classes
-------
RadarChartStrategy
    Strategy for radar chart generation.

Notes
-----
- Supports polar/radar chart visualization
- Data aggregation by category and group
- Unique value counting (e.g., unique KO counts)
- Radial axis auto-scaling with padding

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict

import pandas as pd
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class RadarChartStrategy(BasePlotStrategy):
    """
    Strategy for radar chart comparative multi-dimensional visualization.

    This strategy creates polar/radar charts to compare entities across
    multiple categories.

    Parameters
    ----------
    config : Dict[str, Any]
        Complete configuration from YAML file.

    Attributes
    ----------
    data_config : Dict[str, Any]
        Data processing configuration from YAML.
    plotly_config : Dict[str, Any]
        Plotly-specific configuration from YAML.

    Methods
    -------
    validate_data(df)
        Validate input data for radar chart requirements
    process_data(df)
        Process and aggregate data for radar chart visualization
    create_figure(processed_df)
        Create Plotly radar chart from processed data

    Notes
    -----
    - Displays values radiating from center point
    - Each spoke represents a different category
    - Distance from center indicates magnitude
    - Supports multiple aggregation methods (nunique, count, sum, mean)
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
        use_case = self.metadata.get("use_case_id")
        logger.info(f"RadarChartStrategy initialized for {use_case}")

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for radar chart requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, required columns missing, or
            configuration invalid.
        """
        logger.debug("Starting data validation for RadarChartStrategy")

        # Check DataFrame not empty
        if df.empty:
            raise ValueError("DataFrame is empty - cannot create radar chart")

        # Get required columns from config
        theta_col = self.plotly_config.get("theta_column")
        r_col = self.plotly_config.get("r_column")

        if not theta_col or not r_col:
            raise ValueError(
                "Configuration error: 'theta_column' and 'r_column' "
                "must be specified in plotly config"
            )

        # Validate required columns exist
        required_cols = [theta_col, r_col]
        missing_cols = set(required_cols) - set(df.columns)

        if missing_cols:
            logger.error(
                f"Missing columns: {missing_cols}. " f"Available: {df.columns.tolist()}"
            )
            raise ValueError(
                f"Missing required columns for radar chart: {missing_cols}"
            )

        logger.info(
            f"Data validation passed: {len(df)} rows, "
            f"theta='{theta_col}', r='{r_col}'"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and aggregate data for radar chart visualization.

        Groups data by theta column and aggregates r column using specified
        method (nunique, count, sum, mean).

        Parameters
        ----------
        df : pd.DataFrame
            Validated input data.

        Returns
        -------
        pd.DataFrame
            Processed data with columns: theta (category labels), r
            (aggregated values).
        """
        logger.debug("Starting data processing for RadarChartStrategy")

        # Extract configuration
        theta_col = self.plotly_config.get("theta_column")
        r_col = self.plotly_config.get("r_column")
        aggregation = self.plotly_config.get("aggregation", "nunique")

        logger.info(f"Processing: groupby('{theta_col}')['{r_col}'].{aggregation}()")

        # Group and aggregate
        grouped = df.groupby(theta_col)[r_col]

        if aggregation == "nunique":
            aggregated = grouped.nunique()
        elif aggregation == "count":
            aggregated = grouped.count()
        elif aggregation == "sum":
            aggregated = grouped.sum()
        elif aggregation == "mean":
            aggregated = grouped.mean()
        else:
            logger.warning(
                f"Unknown aggregation '{aggregation}', defaulting to nunique"
            )
            aggregated = grouped.nunique()

        # Reset index to DataFrame
        processed_df = aggregated.reset_index()
        processed_df.columns = ["theta", "r"]

        logger.info(
            f"Data processed: {len(processed_df)} categories, "
            f"r range: [{processed_df['r'].min()}, {processed_df['r'].max()}]"
        )

        return processed_df

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create Plotly radar chart from processed data.

        Creates polar/radar chart with auto-scaled radial axis and
        configurable styling.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data with columns: theta, r

        Returns
        -------
        go.Figure
            Configured Plotly figure with radar chart.
        """
        logger.debug("Creating radar chart figure")

        # Extract chart configuration
        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Get styling parameters with defaults
        fill = chart_config.get("fill", "toself")
        marker_color = chart_config.get("marker_color", "mediumseagreen")
        line_color = chart_config.get("line_color", marker_color)
        line_width = chart_config.get("line_width", 2)
        fillcolor = chart_config.get(
            "fillcolor", "rgba(60,179,113,0.35)"  # Semi-transparent green
        )
        trace_name = chart_config.get("name", "Value")

        # Create figure
        fig = go.Figure()

        # Add radar trace
        fig.add_trace(
            go.Scatterpolar(
                r=processed_df["r"].tolist(),
                theta=processed_df["theta"].tolist(),
                fill=fill,
                name=trace_name,
                marker_color=marker_color,
                line=dict(color=line_color, width=line_width),
                fillcolor=fillcolor,
            )
        )

        # Calculate radial axis range with 10% padding
        max_value = processed_df["r"].max()
        radial_range = [0, max(1, max_value * 1.1)]

        # Get polar configuration
        polar_config = layout_config.get("polar", {})
        radialaxis_config = polar_config.get("radialaxis", {})
        angularaxis_config = polar_config.get("angularaxis", {})

        # Override range if not specified in config
        if (
            radialaxis_config.get("range") is None
            or radialaxis_config.get("range", [])[1] is None
        ):
            radialaxis_config["range"] = radial_range

        # Ensure visibility is set
        if "visible" not in radialaxis_config:
            radialaxis_config["visible"] = True

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
            title_text = title_config.get("text", "") if show_title else ""
            title_x = title_config.get("x", 0.5)
            title_font_size = title_config.get("font", {}).get("size", 16)

        # Get layout configuration
        use_autosize = layout_config.get("autosize", False)
        template = layout_config.get("template", "plotly_white")
        height = layout_config.get("height", 600)
        showlegend = layout_config.get("showlegend", False)

        # Build layout update dict
        layout_update = dict(
            template=template,
            height=height,
            showlegend=showlegend,
            polar=dict(radialaxis=radialaxis_config, angularaxis=angularaxis_config),
        )

        # Add title if enabled
        if show_title and title_text:
            layout_update["title"] = dict(
                text=title_text,
                x=title_x,
                xanchor="center",
                font=dict(size=title_font_size),
            )

        # Add autosize or width
        if use_autosize:
            layout_update["autosize"] = True
        else:
            if layout_config.get("width"):
                layout_update["width"] = layout_config.get("width")

        fig.update_layout(**layout_update)

        logger.info(
            f"Radar chart created: {len(processed_df)} categories, "
            f"radial range: {radialaxis_config['range']}"
        )

        return fig
