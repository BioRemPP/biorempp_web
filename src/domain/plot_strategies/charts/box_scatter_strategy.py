"""
Box Scatter Strategy.

Strategy for creating combined box plot with jittered scatter plot
visualizations using Plotly. Ideal for showing statistical distributions
while preserving visibility of individual data points.

Classes
-------
BoxScatterStrategy
    Strategy combining box plot with jittered scatter overlay

Notes
-----
This strategy is particularly useful for:
- Comparing distributions across categories
- Identifying outliers while seeing all data points
- Visualizing statistical summaries with raw data overlay

For supported use cases, refer to the official documentation.
"""

from typing import Any, Dict

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy
from src.shared.logging import get_logger

logger = get_logger(__name__)


class BoxScatterStrategy(BasePlotStrategy):
    """
    Strategy for creating box plot with jittered scatter overlay.

    This strategy combines two visualization types:
    1. Box plot: Shows statistical distribution (median, IQR, outliers)
    2. Scatter plot: Shows individual data points with horizontal jitter

    The combination provides both statistical summary and granular detail,
    making it ideal for distribution analysis with moderate sample sizes.

    Parameters
    ----------
    config : Dict[str, Any]
        Complete configuration dictionary from YAML (must contain
        'visualization' section with plot parameters)

    Attributes
    ----------
    config : Dict[str, Any]
        Stored configuration dictionary

    Notes
    -----
    Configuration Structure (YAML):
        visualization:
          strategy: "BoxScatterStrategy"
          plotly:
            box:
              y: "unique_ko_count"
              marker:
                color: "#198754"
            scatter:
              y: "unique_ko_count"
              mode: "markers"
              marker:
                color: "rgba(0,0,0,0.5)"
                size: 8
              jitter: 0.01
              hovertemplate: "<b>%{customdata[0]}</b><br>..."
              customdata_columns: ["sample", "rank"]
            layout:
              yaxis:
                title: "Unique KO Count"

    Refer to the official documentation for supported use cases and
    detailed configuration examples.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize BoxScatterStrategy with configuration.

        Parameters
        ----------
        config : Dict[str, Any]
            Complete configuration from YAML file
        """
        super().__init__(config)
        self.data_config = config.get("data", {})
        self.plotly_config = self.viz_config.get("plotly", {})
        logger.info("BoxScatterStrategy initialized")

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for box scatter plot requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate (already aggregated by callback)

        Raises
        ------
        ValueError
            If validation fails

        Notes
        -----
        Expected columns in aggregated data:
        - 'sample': Sample identifier
        - 'unique_ko_count': Aggregated count of unique KOs
        - 'rank': Ranking within database
        """
        logger.debug("Starting data validation for BoxScatterStrategy")

        # Check if DataFrame is empty
        if df.empty:
            raise ValueError("DataFrame is empty")

        # Get required columns from config
        required_cols = self.data_config.get("required_columns", [])

        # If no required columns specified, use default for aggregated data
        if not required_cols:
            required_cols = ["sample", "unique_ko_count", "rank"]
            logger.debug(
                "No required columns in config, using defaults: " f"{required_cols}"
            )

        # Validate required columns exist
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"Missing required columns: {missing_cols}. "
                f"Available: {df.columns.tolist()}"
            )

        logger.info(f"Data validation passed: {len(df)} rows")

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for box scatter visualization.

        For BoxScatterStrategy, data is expected to already be aggregated
        by the callback (grouped by sample with unique KO counts and ranks).
        This method performs minimal processing - just ensures clean copy.

        Parameters
        ----------
        df : pd.DataFrame
            Input data (already aggregated by callback)
            Expected columns: ['sample', 'unique_ko_count', 'rank']

        Returns
        -------
        pd.DataFrame
            Processed data ready for visualization (unchanged copy)

        Notes
        -----
        The aggregation pipeline is handled in the callback:
        1. Extract raw data from store (Sample, KO columns)
        2. Clean data (remove empty, duplicates)
        3. Aggregate: groupby('sample')['ko'].nunique()
        4. Calculate rank
        5. Sort by unique_ko_count descending

        Strategy receives final aggregated data.
        """
        logger.debug(f"Processing data: {len(df)} rows")

        # Data is already processed by callback
        # Just ensure it's a clean copy
        processed = df.copy()

        logger.info(
            f"Data processing completed: {len(processed)} rows "
            f"(pre-aggregated by callback)"
        )
        return processed

    def create_figure(self, df: pd.DataFrame) -> go.Figure:
        """
        Create box scatter figure from processed data.

        Parameters
        ----------
        df : pd.DataFrame
            Processed data ready for visualization

        Returns
        -------
        go.Figure
            Plotly figure with box plot and scatter overlay
        """
        return self.generate(df)

    def generate(self, data: pd.DataFrame) -> go.Figure:
        """
        Generate box plot with jittered scatter overlay.

        Parameters
        ----------
        data : pd.DataFrame
            Processed data ready for visualization (must contain column
            specified in plotly.scatter.y)

        Returns
        -------
        go.Figure
            Plotly figure with box plot and scatter overlay

        Raises
        ------
        ValueError
            If data is empty or required columns missing
        """
        logger.info("Generating box scatter plot", extra={"rows": len(data)})

        # Validate data
        if data.empty:
            raise ValueError("Cannot create plot: DataFrame is empty")

        # Extract configuration
        box_config = self.plotly_config.get("box", {})
        scatter_config = self.plotly_config.get("scatter", {})
        layout_config = self.plotly_config.get("layout", {})

        # Get y-column from scatter config
        y_col = scatter_config.get("y")
        if not y_col:
            raise ValueError("Configuration missing 'visualization.plotly.scatter.y'")

        if y_col not in data.columns:
            raise ValueError(f"Column '{y_col}' not found in data")

        # Create figure
        fig = go.Figure()

        # Add box plot trace
        fig = self._add_box_trace(fig, data, y_col, box_config)

        # Add scatter trace with jitter
        fig = self._add_scatter_trace(fig, data, y_col, scatter_config)

        # Apply layout
        fig = self._apply_layout(fig, layout_config)

        logger.info(
            "Box scatter plot generated successfully", extra={"traces": len(fig.data)}
        )

        return fig

    def _add_box_trace(
        self, fig: go.Figure, data: pd.DataFrame, y_col: str, box_config: Dict[str, Any]
    ) -> go.Figure:
        """
        Add box plot trace to figure.

        Parameters
        ----------
        fig : go.Figure
            Figure to add trace to
        data : pd.DataFrame
            Data containing y-values
        y_col : str
            Column name for y-axis values
        box_config : Dict[str, Any]
            Box plot configuration from YAML

        Returns
        -------
        go.Figure
            Figure with box trace added
        """
        n = len(data)
        x_position = box_config.get("x", None)

        # Extract marker configuration
        marker_config = box_config.get("marker", {})
        box_color = marker_config.get("color", "#198754")

        # If x is None, create single box at position 1
        if x_position is None:
            x_values = [1] * n
        else:
            x_values = [x_position] * n

        fig.add_trace(
            go.Box(
                y=data[y_col],
                x=x_values,
                boxpoints=False,
                name=box_config.get("name", ""),
                marker=dict(color=box_color),
                line=dict(color=box_color),
                fillcolor=box_color,
                opacity=0.7,
                boxmean=box_config.get("boxmean", True),
            )
        )

        logger.debug(f"Box trace added: {n} points")
        return fig

    def _add_scatter_trace(
        self,
        fig: go.Figure,
        data: pd.DataFrame,
        y_col: str,
        scatter_config: Dict[str, Any],
    ) -> go.Figure:
        """
        Add jittered scatter trace to figure.

        Parameters
        ----------
        fig : go.Figure
            Figure to add trace to
        data : pd.DataFrame
            Data containing y-values
        y_col : str
            Column name for y-axis values
        scatter_config : Dict[str, Any]
            Scatter plot configuration from YAML

        Returns
        -------
        go.Figure
            Figure with scatter trace added
        """
        n = len(data)

        # Get jitter configuration
        jitter_scale = scatter_config.get("jitter", 0.01)
        x_position = scatter_config.get("x", None)

        if x_position is None:
            x_position = 1.0

        # Generate jittered x-coordinates
        x_jittered = self._apply_jitter(
            x_position=x_position, n_points=n, jitter_scale=jitter_scale
        )

        # Prepare customdata
        customdata = None
        customdata_columns = scatter_config.get("customdata_columns", [])
        if customdata_columns:
            arrays = [data[col].values for col in customdata_columns]
            customdata = np.stack(arrays, axis=1)

        # Get marker configuration
        marker_config = scatter_config.get("marker", {})
        point_color = marker_config.get("color", "rgba(0, 0, 0, 0.5)")
        point_size = marker_config.get("size", 8)
        line_config = marker_config.get("line", {})

        # Get hover template
        hover_template = scatter_config.get("hovertemplate")

        fig.add_trace(
            go.Scatter(
                x=x_jittered,
                y=data[y_col],
                mode=scatter_config.get("mode", "markers"),
                name=scatter_config.get("name", "Samples"),
                marker=dict(
                    color=point_color,
                    size=point_size,
                    line=dict(
                        color=line_config.get("color", "white"),
                        width=line_config.get("width", 1),
                    ),
                ),
                customdata=customdata,
                hovertemplate=hover_template,
                showlegend=False,
            )
        )

        logger.debug(f"Scatter trace added: {n} points with jitter={jitter_scale}")
        return fig

    def _apply_jitter(
        self,
        x_position: float,
        n_points: int,
        jitter_scale: float,
        random_seed: int = 42,
    ) -> np.ndarray:
        """
        Apply Gaussian jitter to x-coordinates.

        Parameters
        ----------
        x_position : float
            Center position for jitter
        n_points : int
            Number of points to generate
        jitter_scale : float
            Standard deviation of Gaussian distribution
        random_seed : int, default=42
            Random seed for reproducibility

        Returns
        -------
        np.ndarray
            Array of jittered x-coordinates

        Notes
        -----
        Uses numpy's random number generator with fixed seed for
        reproducible jitter. Applies Gaussian noise centered at
        x_position with configurable standard deviation.
        """
        rng = np.random.default_rng(random_seed)
        noise = rng.normal(loc=0.0, scale=jitter_scale, size=n_points)
        x_jittered = x_position + noise

        logger.debug(
            f"Jitter applied: mean={np.mean(x_jittered):.4f}, "
            f"std={np.std(x_jittered):.4f}"
        )

        return x_jittered

    def _apply_layout(self, fig: go.Figure, layout_config: Dict[str, Any]) -> go.Figure:
        """
        Apply layout configuration to figure.

        Parameters
        ----------
        fig : go.Figure
            Figure to apply layout to
        layout_config : Dict[str, Any]
            Layout configuration from YAML

        Returns
        -------
        go.Figure
            Figure with layout applied
        """
        # Get axis configurations
        xaxis_config = layout_config.get("xaxis", {})
        yaxis_config = layout_config.get("yaxis", {})

        # Get other layout options
        plot_bgcolor = layout_config.get("plot_bgcolor", "white")
        paper_bgcolor = layout_config.get("paper_bgcolor", "white")
        font_config = layout_config.get("font", {})
        showlegend = layout_config.get("showlegend", False)
        legend_config = layout_config.get("legend", {})
        margin_config = layout_config.get("margin", {})
        hovermode = layout_config.get("hovermode", "closest")

        fig.update_layout(
            xaxis=dict(
                title=xaxis_config.get("title", ""),
                showticklabels=xaxis_config.get("showticklabels", False),
                showgrid=xaxis_config.get("showgrid", False),
                zeroline=xaxis_config.get("zeroline", False),
            ),
            yaxis=dict(
                title=yaxis_config.get("title", "No. of Unique KOs per Sample"),
                gridcolor=yaxis_config.get("gridcolor", "#e0e0e0"),
                zeroline=True,
                zerolinecolor="#cccccc",
                zerolinewidth=1,
            ),
            showlegend=showlegend,
            legend=legend_config,
            hovermode=hovermode,
            plot_bgcolor=plot_bgcolor,
            paper_bgcolor=paper_bgcolor,
            font=font_config,
            margin=margin_config,
        )

        return fig
