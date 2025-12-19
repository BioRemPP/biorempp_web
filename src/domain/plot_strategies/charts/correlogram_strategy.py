"""
Correlogram Strategy.

This module implements the CorrelogramStrategy class following the Strategy
Pattern, providing specific logic for generating correlogram (correlation
heatmap) visualizations based on presence/absence matrices.

Classes
-------
CorrelogramStrategy
    Concrete strategy for correlogram generation

Notes
-----
This strategy supports two correlation modes:

1. **Sample-Sample Correlation** (mode='sample'):
   - Builds presence/absence matrix: rows=samples, cols=features
   - Computes correlation between samples based on shared features

2. **Feature-Feature Correlation** (mode='feature'):
   - Builds presence/absence matrix: rows=samples, cols=features
   - Computes correlation between features based on co-occurrence in samples

Data Requirements:
- Two columns: row_column (sample) and col_column (feature)
- BioRemPP database with columns like: Sample, KO, Compound_Name, Gene_Symbol

Data Sanitization:
- Filters zero-variance features (present in all or no samples) to prevent NaN
- Replaces any remaining NaN correlations with 0 (no correlation)
- Logs warnings when features are filtered or NaN values detected

For supported use cases, refer to the official documentation.

Version: 1.1.0
"""

import logging
from typing import Any, Dict, Literal

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class CorrelogramStrategy(BasePlotStrategy):
    """
    Correlogram strategy for similarity/co-occurrence visualizations.

    This strategy creates correlation heatmaps (correlograms) showing:
    - Sample-sample similarity based on shared features, OR
    - Feature-feature co-occurrence based on presence in samples

    Attributes
    ----------
    data_config : Dict[str, Any]
        Data processing configuration
    plotly_config : Dict[str, Any]
        Plotly-specific configuration
    correlation_mode : str
        'sample' for sample-sample correlation, 'feature' for feature-feature
    row_column : str
        Column containing row entities (typically 'Sample')
    col_column : str
        Column containing column entities (KO, Compound, Gene Symbol)
    correlation_method : str
        Correlation method ('pearson', 'spearman', 'kendall')

    Notes
    -----
    Refer to the official documentation for supported use cases and
    detailed configuration examples.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize correlogram strategy.

        Parameters
        ----------
        config : Dict[str, Any]
            Complete configuration from YAML file containing:
            - visualization.plotly.correlation_mode: 'sample' or 'feature'
            - visualization.plotly.row_column: Row entity column name
            - visualization.plotly.col_column: Column entity column name
            - visualization.plotly.correlation_method: 'pearson', 'spearman',
              'kendall'
            - visualization.plotly.chart: Chart configuration
            - visualization.plotly.layout: Layout configuration
        """
        super().__init__(config)
        self.data_config = config.get("data", {})
        self.plotly_config = self.viz_config.get("plotly", {})

        # Extract strategy-specific parameters
        self.correlation_mode: Literal["sample", "feature"] = self.plotly_config.get(
            "correlation_mode", "sample"
        )
        self.row_column = self.plotly_config.get("row_column", "Sample")
        self.col_column = self.plotly_config.get("col_column", "KO")
        self.correlation_method = self.plotly_config.get(
            "correlation_method", "pearson"
        )

        logger.info(
            f"CorrelogramStrategy initialized for "
            f"{self.metadata.get('use_case_id', 'unknown')}: "
            f"mode='{self.correlation_mode}', "
            f"row='{self.row_column}', col='{self.col_column}', "
            f"method='{self.correlation_method}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for correlogram requirements.

        Validation rules:
        - DataFrame not empty
        - Required columns exist (row_column, col_column)
        - At least 2 unique values in correlation dimension
        - No completely null columns

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate

        Raises
        ------
        ValueError
            If any validation rule fails
        """
        logger.debug(
            f"Validating data - Shape: {df.shape}, " f"Columns: {df.columns.tolist()}"
        )

        # Check DataFrame not empty
        if df.empty:
            raise ValueError("Input DataFrame is empty")

        # Required columns
        required_cols = [self.row_column, self.col_column]

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

        # Check minimum entities for correlation
        n_rows = df_clean[self.row_column].nunique()
        n_cols = df_clean[self.col_column].nunique()

        if self.correlation_mode == "sample":
            if n_rows < 2:
                raise ValueError(
                    f"Need at least 2 unique {self.row_column} values "
                    f"to compute sample-sample correlation. Found: {n_rows}"
                )
        else:  # feature mode
            if n_cols < 2:
                raise ValueError(
                    f"Need at least 2 unique {self.col_column} values "
                    f"to compute feature-feature correlation. Found: {n_cols}"
                )

        logger.info(
            f"Data validation passed - "
            f"{n_rows} {self.row_column}s, {n_cols} {self.col_column}s, "
            f"{len(df_clean)} records"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data and compute correlation matrix.

        Processing steps:
        1. Clean data (remove nulls, strip whitespace)
        2. Build presence/absence matrix using crosstab
        3. Convert to binary (1 if present, 0 otherwise)
        4. Filter zero-variance features (prevent NaN correlations)
        5. Compute correlation matrix based on mode
        6. Handle any remaining NaN values

        Parameters
        ----------
        df : pd.DataFrame
            Input data with required columns

        Returns
        -------
        pd.DataFrame
            Correlation matrix (symmetric, values from -1 to 1, NaN-free)
        """
        logger.info(
            f"Processing data for correlogram (mode: {self.correlation_mode})..."
        )

        # Clean data: remove nulls and strip whitespace
        df_clean = df.dropna(subset=[self.row_column, self.col_column]).copy()
        df_clean[self.row_column] = df_clean[self.row_column].astype(str).str.strip()
        df_clean[self.col_column] = df_clean[self.col_column].astype(str).str.strip()

        # Remove empty strings
        df_clean = df_clean[
            (df_clean[self.row_column] != "") & (df_clean[self.col_column] != "")
        ]

        logger.debug(
            f"After cleaning: {len(df_clean)} records "
            f"({len(df) - len(df_clean)} removed)"
        )

        # Build presence/absence matrix using crosstab
        # Rows = row_column (samples), Columns = col_column (features)
        logger.debug("Building presence/absence matrix...")
        presence_matrix = pd.crosstab(
            df_clean[self.row_column], df_clean[self.col_column]
        )

        # Convert to binary (1 if present, 0 otherwise)
        binary_matrix = (presence_matrix > 0).astype(int)

        logger.debug(
            f"Binary matrix shape: {binary_matrix.shape} "
            f"(rows={self.row_column}, cols={self.col_column})"
        )

        # ========================================
        # SANITIZATION: Filter zero-variance features
        # ========================================
        # Features with zero variance (all 0s or all 1s) cause NaN correlations
        # because Pearson correlation involves division by standard deviation

        if self.correlation_mode == "sample":
            # For sample-sample correlation, check row variance
            variances = binary_matrix.var(axis=1)
            zero_var_mask = variances > 0
            n_filtered = (~zero_var_mask).sum()

            if n_filtered > 0:
                logger.warning(
                    f"Filtering {n_filtered} {self.row_column}(s) with zero variance "
                    f"(present in all or no {self.col_column}s)"
                )
                filtered_items = binary_matrix.index[~zero_var_mask].tolist()
                logger.debug(f"Filtered {self.row_column}s: {filtered_items[:5]}...")

            binary_matrix = binary_matrix.loc[zero_var_mask]

        else:  # feature mode
            # For feature-feature correlation, check column variance
            variances = binary_matrix.var(axis=0)
            zero_var_mask = variances > 0
            n_filtered = (~zero_var_mask).sum()

            if n_filtered > 0:
                logger.warning(
                    f"Filtering {n_filtered} {self.col_column}(s) with zero variance "
                    f"(present in all or no {self.row_column}s)"
                )
                filtered_items = binary_matrix.columns[~zero_var_mask].tolist()
                logger.debug(f"Filtered {self.col_column}s: {filtered_items[:5]}...")

            binary_matrix = binary_matrix.loc[:, zero_var_mask]

        logger.debug(
            f"After variance filtering: {binary_matrix.shape} "
            f"({n_filtered} features removed)"
        )

        # Compute correlation based on mode
        if self.correlation_mode == "sample":
            # Sample-sample correlation: correlate rows (samples)
            # Need to transpose and correlate, then the result is sample × sample
            logger.debug("Computing sample-sample correlation...")
            correlation_matrix = binary_matrix.T.corr(method=self.correlation_method)
        else:
            # Feature-feature correlation: correlate columns (features)
            # Direct correlation gives feature × feature
            logger.debug("Computing feature-feature correlation...")
            correlation_matrix = binary_matrix.corr(method=self.correlation_method)

        # ========================================
        # SANITIZATION: Handle remaining NaN values
        # ========================================
        # Replace any remaining NaN values with 0 (no correlation)
        # This handles edge cases where variance filtering didn't catch all issues
        nan_count = correlation_matrix.isna().sum().sum()

        if nan_count > 0:
            logger.warning(
                f"Found {nan_count} NaN values in correlation matrix. "
                f"Replacing with 0 (no correlation)."
            )
            # Get positions of NaN values for logging
            nan_positions = correlation_matrix.isna()
            if nan_positions.any().any():
                nan_indices = [
                    (idx, col)
                    for idx in correlation_matrix.index
                    for col in correlation_matrix.columns
                    if pd.isna(correlation_matrix.loc[idx, col])
                ]
                logger.debug(f"NaN positions (first 5): {nan_indices[:5]}")

            correlation_matrix = correlation_matrix.fillna(0)

        # Ensure consistent ordering
        order = correlation_matrix.index.tolist()
        correlation_matrix = correlation_matrix.loc[order, order]

        logger.info(
            f"Correlation matrix computed - "
            f"Shape: {correlation_matrix.shape}, "
            f"Value range: [{correlation_matrix.min().min():.3f}, "
            f"{correlation_matrix.max().max():.3f}], "
            f"NaN count: 0 (sanitized)"
        )

        return correlation_matrix

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create correlogram figure from correlation matrix.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Correlation matrix (symmetric)

        Returns
        -------
        go.Figure
            Configured Plotly correlogram heatmap
        """
        logger.debug("Creating correlogram figure...")

        # Extract chart configuration
        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Get title configuration
        title_config = chart_config.get("title", {})
        show_title = title_config.get("show", True)
        title_text = title_config.get("text", "Correlogram") if show_title else ""

        # Get axis labels based on mode (with custom override support)
        if self.correlation_mode == "sample":
            default_label = self.row_column
        else:
            default_label = self.col_column

        xaxis_title = chart_config.get(
            "xaxis_title", chart_config.get("axis_label", default_label)
        )
        yaxis_title = chart_config.get(
            "yaxis_title", chart_config.get("axis_label", default_label)
        )

        # Get color configuration
        color_scale = chart_config.get("color_continuous_scale", "RdBu_r")
        color_label = chart_config.get("color_label", "Pearson r")

        # Get template
        template = layout_config.get("template", "simple_white")

        # Create heatmap using plotly express
        fig = px.imshow(
            processed_df,
            labels=dict(x=xaxis_title, y=yaxis_title, color=color_label),
            zmin=-1,
            zmax=1,
            text_auto=chart_config.get("text_auto", False),
            aspect="auto",
            template=template,
            color_continuous_scale=color_scale,
        )

        # Apply layout configuration
        height = layout_config.get("height", 600)
        use_autosize = layout_config.get("autosize", False)

        margin_config = layout_config.get("margin", {})
        margin = dict(
            l=margin_config.get("l", 80),
            r=margin_config.get("r", 30),
            t=margin_config.get("t", 60),
            b=margin_config.get("b", 60),
        )

        # Get axis angles
        xaxis_tickangle = chart_config.get("xaxis_tickangle", -45)
        yaxis_tickangle = chart_config.get("yaxis_tickangle", 0)

        # Build layout update dict
        layout_update = {
            "title": dict(
                text=title_text,
                x=0.5,
                xanchor="center",
                font=dict(size=title_config.get("font_size", 16)),
            ),
            "height": height,
            "margin": margin,
        }

        # Add autosize or width
        if use_autosize:
            layout_update["autosize"] = True
        else:
            if layout_config.get("width"):
                layout_update["width"] = layout_config.get("width", 600)

        fig.update_layout(**layout_update)

        # Update axes
        fig.update_xaxes(
            showgrid=False, tickangle=xaxis_tickangle, title=dict(text=xaxis_title)
        )
        fig.update_yaxes(
            showgrid=False,
            autorange="reversed",  # Align heatmap orientation
            tickangle=yaxis_tickangle,
            title=dict(text=yaxis_title),
        )

        # Update colorbar
        colorbar_config = chart_config.get("colorbar", {})
        fig.update_coloraxes(
            colorbar=dict(
                title=dict(
                    text=colorbar_config.get("title", color_label),
                    font=dict(size=colorbar_config.get("title_font_size", 12))
                ),
            )
        )

        logger.info(
            f"Correlogram created - "
            f"Size: {'auto' if use_autosize else layout_update.get('width', 600)}x{height}px, "
            f"Mode: {self.correlation_mode}, "
            f"Entities: {len(processed_df)}"
        )

        return fig
