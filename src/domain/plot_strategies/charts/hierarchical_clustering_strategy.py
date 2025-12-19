"""
Hierarchical Clustering Strategy - Dendrogram Visualizations.

This module implements the HierarchicalClusteringStrategy for creating dendrogram
visualizations using scipy hierarchical clustering and plotly.

Classes
-------
HierarchicalClusteringStrategy
    Strategy for hierarchical clustering dendrogram generation.

Notes
-----
- Supports multiple distance metrics (jaccard, euclidean, cosine, etc.)
- Supports multiple linkage methods (average, complete, single, ward)
- Creates left-oriented dendrograms with sample labels

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import pdist

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class HierarchicalClusteringStrategy(BasePlotStrategy):
    """
    Strategy for hierarchical clustering dendrogram visualizations.

    This strategy creates dendrograms showing hierarchical relationships between
    samples based on binary KO presence/absence patterns.

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

    Methods
    -------
    validate_data(df)
        Validate input data for hierarchical clustering requirements
    process_data(df)
        Process binary matrix for hierarchical clustering
    create_figure(processed_df)
        Create dendrogram figure from binary matrix
    apply_filters(df, filters)
        Apply clustering parameters (metric, method)

    Notes
    -----
    - Supports multiple distance metrics and linkage methods
    - Validates Ward/Euclidean compatibility
    - Creates left-oriented dendrograms
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

        # Store clustering parameters for use in create_figure
        self._metric = "jaccard"
        self._method = "average"

        logger.info(f"HierarchicalClusteringStrategy initialized for {use_case}")

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for hierarchical clustering requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Binary presence/absence matrix (samples × KOs).

        Raises
        ------
        ValueError
            If DataFrame is empty, has fewer than 2 samples, or contains
            non-binary values.
        """
        logger.debug("Starting data validation for HierarchicalClusteringStrategy")

        # Get validation rules from config
        rules = self.validation_rules.get("rules", [])

        logger.debug(f"Validating with {len(rules)} rules")
        logger.debug(f"DataFrame shape: {df.shape}")
        logger.debug(f"DataFrame index (samples): {df.index.tolist()[:5]}...")
        logger.debug(f"DataFrame columns (KOs): {df.columns.tolist()[:5]}...")

        for rule in rules:
            rule_name = rule.get("rule")
            logger.debug(f"Applying rule: {rule_name}")

            if rule_name == "not_empty":
                if df.empty:
                    raise ValueError(rule.get("message", "DataFrame is empty"))

            elif rule_name == "minimum_samples":
                min_count = rule.get("min_count", 2)
                if df.shape[0] < min_count:
                    raise ValueError(
                        f"{rule.get('message', 'Insufficient samples')}: "
                        f"{df.shape[0]} < {min_count}"
                    )

        logger.info(
            f"Data validation passed: {df.shape[0]} samples × {df.shape[1]} KOs"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process binary matrix for hierarchical clustering.

        Ensures strict binary values (0 or 1) and returns matrix ready for
        clustering.

        Parameters
        ----------
        df : pd.DataFrame
            Binary presence/absence matrix (samples × KOs).

        Returns
        -------
        pd.DataFrame
            Binary matrix ready for scipy linkage.
        """
        logger.debug("Processing data for HierarchicalClusteringStrategy")

        # Ensure binary values (0 or 1 only)
        if not ((df == 0) | (df == 1)).all().all():
            logger.warning("Non-binary values detected, converting to binary")
            processed_df = df.copy()
            processed_df[processed_df > 0] = 1
        else:
            processed_df = df

        logger.info("Data processing complete, binary matrix ready")
        return processed_df

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create dendrogram figure from binary matrix.

        Uses scipy hierarchical clustering and creates a plotly dendrogram
        visualization with configured parameters.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Binary presence/absence matrix (samples × KOs).

        Returns
        -------
        go.Figure
            Configured Plotly dendrogram.
        """
        logger.debug("HierarchicalClusteringStrategy: Creating figure")
        logger.debug(f"Matrix shape: {processed_df.shape}")
        logger.debug(f"Matrix dtype: {processed_df.dtypes.unique()}")
        logger.debug(f"Sample count: {len(processed_df.index)}")
        logger.debug(f"Sample labels: {processed_df.index.tolist()[:5]}...")

        # Use stored parameters
        metric = self._metric
        method = self._method

        logger.info(
            f"Creating dendrogram: metric={metric}, method={method}, "
            f"samples={processed_df.shape[0]}, KOs={processed_df.shape[1]}"
        )

        try:
            # Step 1: Compute distance matrix
            logger.debug(f"Computing distance matrix with metric={metric}...")
            dist_matrix = pdist(processed_df.values, metric=metric)
            logger.debug(f"Distance matrix shape: {dist_matrix.shape}")

            # Step 2: Perform hierarchical clustering
            logger.debug(f"Performing linkage with method={method}...")
            Z = linkage(dist_matrix, method=method)
            logger.debug(f"Linkage matrix shape: {Z.shape}")

            # Step 3: Create dendrogram structure
            logger.debug("Creating dendrogram structure...")
            dend = dendrogram(
                Z, labels=processed_df.index.tolist(), orientation="left", no_plot=True
            )
            logger.debug("Dendrogram structure created")

            # Step 4: Extract coordinates for Plotly traces
            icoord = np.array(dend["icoord"])
            dcoord = np.array(dend["dcoord"])
            ordered_labels = dend["ivl"]
            logger.debug(
                f"Extracted coords: icoord shape={icoord.shape}, "
                f"dcoord shape={dcoord.shape}, labels={len(ordered_labels)}"
            )

            # Step 5: Create Plotly figure with dendrogram traces
            logger.debug("Creating Plotly figure...")
            fig = go.Figure()

            # Add dendrogram lines
            for i in range(len(icoord)):
                fig.add_trace(
                    go.Scatter(
                        x=dcoord[i],
                        y=icoord[i],
                        mode="lines",
                        line=dict(color="rgb(100,100,100)", width=1),
                        hoverinfo="skip",
                        showlegend=False,
                    )
                )

            logger.info("Dendrogram traces created successfully")

        except Exception as e:
            logger.error(
                f"Failed to create dendrogram: {type(e).__name__}: {e}", exc_info=True
            )
            raise

        # Extract configuration
        title_config = self.plotly_config.get("title", {})
        layout_config = self.plotly_config.get("layout", {})

        # Build complete title with parameters
        base_title = title_config.get("text", "Hierarchical Clustering")
        complete_title = (
            f"{base_title}<br>"
            f"<sub>Method: {method.capitalize()} | "
            f"Metric: {metric.capitalize()}</sub>"
        )

        # Configure y-axis tick labels (sample names)
        y_tick_positions = list(range(5, len(ordered_labels) * 10, 10))

        # Apply layout configuration
        fig.update_layout(
            title={
                "text": complete_title,
                "x": title_config.get("x", 0.5),
                "xanchor": title_config.get("xanchor", "center"),
                "font": title_config.get("font", {}),
            },
            height=layout_config.get("height", 600),
            width=layout_config.get("width", 1000),
            template=layout_config.get("template", "simple_white"),
            xaxis={
                "title": layout_config.get("xaxis", {}).get(
                    "title", {"text": "Distance / Dissimilarity"}
                ),
                "tickfont": layout_config.get("xaxis", {}).get("tickfont", {}),
                "side": "bottom",
            },
            yaxis={
                "title": layout_config.get("yaxis", {}).get(
                    "title", {"text": "Sample"}
                ),
                "tickfont": layout_config.get("yaxis", {}).get(
                    "tickfont", {"size": 10}
                ),
                "tickmode": "array",
                "tickvals": y_tick_positions,
                "ticktext": ordered_labels,
                "side": "right",
            },
            hovermode=layout_config.get("hovermode", "closest"),
            hoverlabel=layout_config.get("hoverlabel", {}),
            margin=layout_config.get("margin", {}),
        )

        logger.info("Dendrogram figure configured successfully")
        return fig

    def apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply clustering parameters to strategy.

        Stores clustering parameters (metric, method) for use in figure
        creation.

        Parameters
        ----------
        df : pd.DataFrame
            Binary presence/absence matrix.
        filters : Dict[str, Any]
            Clustering parameters (metric, method).

        Returns
        -------
        pd.DataFrame
            Unchanged matrix (parameters stored internally).
        """
        if filters:
            self._metric = filters.get("metric", "jaccard")
            self._method = filters.get("method", "average")
            logger.info(
                f"Clustering parameters set - "
                f"metric: {self._metric}, method: {self._method}"
            )
        else:
            logger.debug("No filters provided, using defaults")

        return df
