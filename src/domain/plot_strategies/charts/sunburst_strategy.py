"""
Sunburst Strategy - Hierarchical Sunburst Visualizations.

This module implements the SunburstStrategy for generating hierarchical sunburst
visualizations with flexible configuration.

Classes
-------
SunburstStrategy
    Strategy for sunburst chart generation.

Notes
-----
- Supports hierarchical data visualization (up to 3 levels)
- Size-based weighting (unique gene counts)
- Color mapping with continuous scales
- Interactive drill-down capability

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class SunburstStrategy(BasePlotStrategy):
    """
    Strategy for hierarchical sunburst data visualization.

    This strategy creates radial hierarchical visualizations where each ring
    represents a level of the hierarchy and segment size represents a
    quantitative value.

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
        Validate input data for sunburst requirements
    process_data(df)
        Process and transform data for sunburst visualization
    create_figure(processed_df)
        Create Plotly sunburst figure from processed data

    Notes
    -----
    - Ideal for showing hierarchical relationships with proportional sizing
    - Supports up to 3 hierarchical levels
    - Color mapping with continuous or discrete scales
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
        logger.info(f"SunburstStrategy initialized for {use_case}")

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for sunburst requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, required columns missing, values column
            not numeric, or insufficient data.
        """
        logger.debug("Starting data validation for SunburstStrategy")

        # Check DataFrame not empty
        if df.empty:
            logger.error("DataFrame is empty")
            raise ValueError("Input DataFrame cannot be empty")

        logger.info(f"Validating data with shape: {df.shape}")

        # Get required columns from config
        path_columns = self.plotly_config.get("path_columns", [])
        values_column = self.plotly_config.get("values_column")

        if not path_columns:
            logger.error("No path_columns specified in config")
            raise ValueError("Configuration must specify 'path_columns' for hierarchy")

        if not values_column:
            logger.error("No values_column specified in config")
            raise ValueError("Configuration must specify 'values_column' for sizing")

        # Validate path columns exist
        missing_path_cols = [col for col in path_columns if col not in df.columns]
        if missing_path_cols:
            logger.error(
                f"Missing path columns: {missing_path_cols}. "
                f"Available: {df.columns.tolist()}"
            )
            raise ValueError(f"Required path columns not found: {missing_path_cols}")

        # Validate values column exists
        if values_column not in df.columns:
            logger.error(
                f"Values column '{values_column}' not found. "
                f"Available: {df.columns.tolist()}"
            )
            raise ValueError(f"Required values column '{values_column}' not found")

        # Validate values column is numeric
        if not pd.api.types.is_numeric_dtype(df[values_column]):
            logger.error(
                f"Values column '{values_column}' is not numeric. "
                f"Type: {df[values_column].dtype}"
            )
            raise ValueError(f"Values column '{values_column}' must be numeric")

        # Check for null values in critical columns
        critical_cols = path_columns + [values_column]
        null_counts = df[critical_cols].isnull().sum()
        if null_counts.any():
            logger.warning(
                f"Null values detected in critical columns: "
                f"{null_counts[null_counts > 0].to_dict()}"
            )

        # Validate minimum rows (from config or default to 1)
        min_rows = self.validation_rules.get("min_rows", 1)
        if len(df) < min_rows:
            logger.error(f"Insufficient data: {len(df)} rows < {min_rows} required")
            raise ValueError(f"DataFrame must have at least {min_rows} rows")

        logger.info("✓ Data validation passed for SunburstStrategy")

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process and transform data for sunburst visualization.

        Removes NaN values, ensures proper data types, and sorts by
        hierarchical levels.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.

        Returns
        -------
        pd.DataFrame
            Processed data ready for sunburst visualization.
        """
        logger.debug("Starting data processing for SunburstStrategy")

        # Copy to avoid modifying original
        processed_df = df.copy()

        # Get critical columns
        path_columns = self.plotly_config.get("path_columns", [])
        values_column = self.plotly_config.get("values_column")
        critical_cols = path_columns + [values_column]

        initial_count = len(processed_df)
        logger.info(f"Processing {initial_count} rows")

        # Remove rows with NaN in critical columns
        processed_df = processed_df.dropna(subset=critical_cols)
        final_count = len(processed_df)

        if final_count < initial_count:
            removed = initial_count - final_count
            logger.info(
                f"Removed {removed} rows with NaN values " f"({final_count} remaining)"
            )

        # Ensure values column is numeric
        processed_df[values_column] = pd.to_numeric(
            processed_df[values_column], errors="coerce"
        )

        # Remove rows where values became NaN after coercion
        processed_df = processed_df.dropna(subset=[values_column])

        if len(processed_df) == 0:
            logger.error("No valid data remaining after processing")
            raise ValueError(
                "All data removed during processing. " "Check data quality and types."
            )

        # Sort by hierarchical levels for visual consistency
        # This ensures sunburst segments appear in consistent order
        processed_df = processed_df.sort_values(by=path_columns)

        logger.info(
            f"✓ Data processing complete: {len(processed_df)} rows, "
            f"{processed_df[values_column].sum():.0f} total value"
        )

        return processed_df

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create Plotly sunburst figure from processed data.

        Constructs hierarchical sunburst visualization using Plotly Express
        and applies layout customizations.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data with hierarchy and values.

        Returns
        -------
        go.Figure
            Configured Plotly sunburst figure.
        """
        logger.debug("Creating sunburst figure")

        # Extract configuration
        path_columns = self.plotly_config.get("path_columns", [])
        values_column = self.plotly_config.get("values_column")
        color_column = self.plotly_config.get("color_column", values_column)

        # Color configuration
        color_mode = self.plotly_config.get("color_mode", "continuous")

        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        logger.info(f"Creating sunburst with path: {' → '.join(path_columns)}")
        logger.info(
            f"Values column: {values_column}, "
            f"Color column: {color_column}, "
            f"Color mode: {color_mode}"
        )

        # Validate that values sum is not zero (sunburst cannot handle this)
        if values_column and processed_df[values_column].sum() == 0:
            error_msg = "Cannot create sunburst: all values sum to zero"
            logger.error(error_msg)
            raise ValueError(f"Failed to create sunburst chart: {error_msg}")

        # Create sunburst using Plotly Express
        try:
            sunburst_kwargs = {
                "data_frame": processed_df,
                "path": path_columns,
                "values": values_column,
                "color": color_column,
                "hover_data": {values_column: ":.0f"},
                "branchvalues": chart_config.get("branchvalues", "total"),
            }

            # Add color configuration based on mode
            if color_mode == "continuous":
                color_scale = self.plotly_config.get(
                    "color_continuous_scale", ["#e9f7f1", "mediumseagreen", "#0b3d2e"]
                )
                sunburst_kwargs["color_continuous_scale"] = color_scale
            else:  # discrete
                color_sequence = self.plotly_config.get("color_discrete_sequence", None)
                if color_sequence:
                    sunburst_kwargs["color_discrete_sequence"] = color_sequence

            fig = px.sunburst(**sunburst_kwargs)

        except Exception as e:
            logger.error(f"Error creating sunburst: {e}", exc_info=True)
            raise ValueError(f"Failed to create sunburst chart: {e}")

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
            title_text = title_config.get("text", "")
            title_x = title_config.get("x", 0.5)
            title_font_size = title_config.get("font", {}).get("size", 16)

        # Get layout configuration
        use_autosize = layout_config.get("autosize", False)
        height = layout_config.get("height", 600)
        template = layout_config.get("template", "simple_white")

        # Get margin configuration
        margin_config = layout_config.get("margin", {})
        margin = dict(
            t=margin_config.get("t", 40),
            l=margin_config.get("l", 20),
            r=margin_config.get("r", 20),
            b=margin_config.get("b", 20),
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

        fig.update_layout(**layout_updates)

        # Colorbar configuration (for continuous mode)
        if color_mode == "continuous":
            colorbar_config = chart_config.get("colorbar", {})
            colorbar_title = colorbar_config.get("title", values_column)
            fig.update_layout(coloraxis_colorbar=dict(title=colorbar_title))

        # Trace styling
        text_font_size = chart_config.get("text_font_size", 12)
        fig.update_traces(textfont_size=text_font_size)

        logger.info(
            f"✓ Sunburst figure created: "
            f"Height: {height}px, "
            f"Autosize: {use_autosize}"
        )

        return fig
