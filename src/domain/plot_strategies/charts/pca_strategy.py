"""
PCA Strategy - Principal Component Analysis Visualization.

This module implements the PCAStrategy for creating PCA scatter plots to
visualize sample relationships and clustering patterns based on feature
profiles.

Classes
-------
PCAStrategy
    Strategy for PCA scatter plot generation.

Notes
-----
- Uses scikit-learn for PCA computation
- Creates 2D scatter plots (PC1 vs PC2)
- Displays explained variance on axes
- Interactive hover information with Plotly

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class PCAStrategy(BasePlotStrategy):
    """
    Strategy for creating PCA scatter plots.

    This strategy reduces high-dimensional data to 2D for visualization,
    preserving as much variance as possible.

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
    sample_column : str
        Column name for samples.
    feature_column : str
        Column name for features (KO or Compound).
    n_components : int
        Number of principal components (default: 2).

    Methods
    -------
    validate_data(df)
        Validate input data for PCA requirements
    process_data(df)
        Process data into presence/absence matrix and apply PCA
    create_figure(processed_df)
        Create PCA scatter plot from processed data

    Notes
    -----
    - Requires minimum 2 samples and 2 features
    - Creates binary presence/absence matrix
    - Standardizes data before PCA
    - Visualizes PC1 vs PC2 with explained variance
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

        # Extract configuration sections
        self.data_config = config.get("data", {})
        self.plotly_config = self.viz_config.get("plotly", {})

        # Extract column mappings
        self.sample_column = self.data_config.get("sample_column", "Sample")
        self.feature_column = self.data_config.get("feature_column", "KO")

        # PCA parameters
        self.n_components = self.plotly_config.get("n_components", 2)

        logger.info(f"PCAStrategy initialized for {self.metadata.get('use_case_id')}")
        logger.info(
            f"Sample column: '{self.sample_column}', "
            f"Feature column: '{self.feature_column}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for PCA requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, required columns missing, or fewer than
            2 samples/features found.
        """
        logger.debug("Starting data validation for PCAStrategy")

        # Check if DataFrame is empty
        if df.empty:
            raise ValueError(
                "PCA Error: DataFrame is empty. " "Cannot perform PCA on empty data."
            )

        # Check required columns
        required_cols = [self.sample_column, self.feature_column]
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(
                f"PCA Error: Missing required columns: {missing_cols}. "
                f"Available columns: {df.columns.tolist()}"
            )

        # Check for null values in critical columns
        null_samples = df[self.sample_column].isna().sum()
        null_features = df[self.feature_column].isna().sum()

        if null_samples > 0:
            logger.warning(
                f"Found {null_samples} null values in '{self.sample_column}'. "
                "These rows will be dropped."
            )

        if null_features > 0:
            logger.warning(
                f"Found {null_features} null values in '{self.feature_column}'. "
                "These rows will be dropped."
            )

        # Check minimum number of samples
        n_samples = df[self.sample_column].nunique()
        if n_samples < 2:
            raise ValueError(
                f"PCA Error: Need at least 2 samples, found {n_samples}. "
                "PCA requires multiple samples for comparison."
            )

        # Check minimum number of features
        n_features = df[self.feature_column].nunique()
        if n_features < 2:
            raise ValueError(
                f"PCA Error: Need at least 2 features, found {n_features}. "
                "PCA requires multiple features for dimensionality reduction."
            )

        logger.info(
            f"Data validation passed: {n_samples} samples, " f"{n_features} features"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data into presence/absence matrix and apply PCA.

        Creates binary matrix, standardizes features, and applies PCA
        transformation.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with sample and feature columns.

        Returns
        -------
        pd.DataFrame
            DataFrame with columns: ['Sample', 'PC1', 'PC2'] containing
            principal component scores.
        """
        logger.debug("Starting data processing for PCAStrategy")

        # Drop null values in critical columns
        clean_df = df.dropna(subset=[self.sample_column, self.feature_column])

        logger.info(
            f"Building presence/absence matrix from " f"{len(clean_df)} records..."
        )

        # Create presence/absence matrix
        # Rows = samples, Columns = features, Values = counts
        presence_matrix = pd.crosstab(
            clean_df[self.sample_column], clean_df[self.feature_column]
        )

        # Convert to binary (presence=1, absence=0)
        binary_matrix = (presence_matrix > 0).astype(int)

        logger.info(
            f"Matrix shape: {binary_matrix.shape[0]} samples × "
            f"{binary_matrix.shape[1]} features"
        )

        # Standardize the data
        logger.debug("Standardizing features...")
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(binary_matrix)

        # Apply PCA
        logger.debug(f"Running PCA with {self.n_components} components...")
        pca = PCA(n_components=self.n_components)
        principal_components = pca.fit_transform(scaled_data)

        # Store explained variance for axis labels
        self.explained_variance = pca.explained_variance_ratio_ * 100

        logger.info(
            f"PCA complete. Explained variance: "
            f"PC1={self.explained_variance[0]:.2f}%, "
            f"PC2={self.explained_variance[1]:.2f}%"
        )

        # Create result DataFrame
        pca_df = pd.DataFrame(
            data=principal_components,
            columns=[f"PC{i+1}" for i in range(self.n_components)],
            index=binary_matrix.index,
        )

        # Add sample column for easier reference
        pca_df["Sample"] = pca_df.index

        logger.debug(f"Processed data shape: {pca_df.shape}")
        return pca_df

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create PCA scatter plot from processed data.

        Creates interactive scatter plot with PC1 vs PC2, sample coloring,
        and explained variance in axis labels.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data with PC1, PC2, and Sample columns.

        Returns
        -------
        go.Figure
            Configured Plotly figure ready for display.
        """
        logger.debug("Creating PCA scatter plot figure")

        # Get styling configuration
        layout_config = self.plotly_config.get("layout", {})
        chart_config = self.plotly_config.get("chart", {})

        color_palette = self.plotly_config.get("color_palette", "Plotly")

        # Get color sequence (support both string name and list)
        if isinstance(color_palette, str):
            color_sequence = getattr(
                px.colors.qualitative, color_palette, px.colors.qualitative.Plotly
            )
        else:
            color_sequence = color_palette

        # Get template
        template = layout_config.get("template", "simple_white")

        # Create axis labels with explained variance
        show_variance = chart_config.get("show_explained_variance", True)

        if show_variance:
            x_label = f"Principal Component 1 " f"({self.explained_variance[0]:.2f}%)"
            y_label = f"Principal Component 2 " f"({self.explained_variance[1]:.2f}%)"
        else:
            x_label = "Principal Component 1"
            y_label = "Principal Component 2"

        # Allow custom axis titles to be appended
        xaxis_config = chart_config.get("xaxis", {})
        yaxis_config = chart_config.get("yaxis", {})

        if xaxis_config.get("title"):
            x_label = xaxis_config["title"]
        if yaxis_config.get("title"):
            y_label = yaxis_config["title"]

        # Create scatter plot
        fig = px.scatter(
            processed_df,
            x="PC1",
            y="PC2",
            color="Sample",
            labels={"PC1": x_label, "PC2": y_label},
            hover_name="Sample",
            template=template,
            color_discrete_sequence=color_sequence,
        )

        # Apply layout configuration from YAML
        layout_updates = {}

        # Title configuration
        title_config = layout_config.get("title", {})
        if title_config:
            show_title = title_config.get("show", True)
            if show_title:
                layout_updates["title"] = {
                    "text": title_config.get("text", ""),
                    "x": title_config.get("x", 0.5),
                    "xanchor": "center",
                }

        # Dimensions (autosize or fixed)
        use_autosize = layout_config.get("autosize", False)

        if use_autosize:
            layout_updates["autosize"] = True
        else:
            if "height" in layout_config:
                layout_updates["height"] = layout_config["height"]
            if "width" in layout_config:
                layout_updates["width"] = layout_config["width"]

        # Legend
        legend_config = layout_config.get("legend", {})
        if legend_config:
            layout_updates["legend"] = {
                "title": {"text": legend_config.get("title", "Sample")},
                "orientation": legend_config.get("orientation", "v"),
                "yanchor": legend_config.get("yanchor", "top"),
                "y": legend_config.get("y", 1),
                "xanchor": legend_config.get("xanchor", "left"),
                "x": legend_config.get("x", 1.02),
            }

        # Margins
        margins = layout_config.get("margin", {})
        if margins:
            layout_updates["margin"] = margins

        # Apply all layout updates
        if layout_updates:
            fig.update_layout(**layout_updates)

        # Update trace settings (marker configuration)
        marker_config = chart_config.get("marker", {})
        marker_size = marker_config.get("size", 10)
        marker_line_width = marker_config.get("line", {}).get("width", 1)
        marker_line_color = marker_config.get("line", {}).get("color", "white")

        fig.update_traces(
            marker=dict(
                size=marker_size,
                line=dict(width=marker_line_width, color=marker_line_color),
            ),
            textposition="top center",
        )

        logger.info(
            f"PCA figure created successfully - "
            f"PC1: {self.explained_variance[0]:.2f}%, "
            f"PC2: {self.explained_variance[1]:.2f}%"
        )
        return fig
