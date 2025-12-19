"""
Sankey Strategy - Alluvial/Flow Diagram Visualizations.

This module implements the SankeyStrategy for generating Sankey (alluvial)
diagrams that visualize flow relationships between multiple categorical levels.

Classes
-------
SankeyStrategy
    Strategy for Sankey diagram generation using Plotly.

Notes
-----
- Visualizes flow/transition between categorical stages
- Shows proportional relationships across multiple levels
- Flow thickness proportional to count/aggregated value
- Supports flexible multi-level flow configuration

For supported use cases, refer to the official documentation.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


# Default color palette for Sankey nodes
DEFAULT_NODE_COLORS = [
    "rgba(31, 119, 180, 0.8)",  # Blue
    "rgba(255, 127, 14, 0.8)",  # Orange
    "rgba(44, 160, 44, 0.8)",  # Green
    "rgba(214, 39, 40, 0.8)",  # Red
    "rgba(148, 103, 189, 0.8)",  # Purple
    "rgba(140, 86, 75, 0.8)",  # Brown
    "rgba(227, 119, 194, 0.8)",  # Pink
    "rgba(127, 127, 127, 0.8)",  # Gray
    "rgba(188, 189, 34, 0.8)",  # Olive
    "rgba(23, 190, 207, 0.8)",  # Cyan
]


class SankeyStrategy(BasePlotStrategy):
    """
    Strategy for Sankey diagram flow/alluvial visualizations.

    This strategy creates Sankey diagrams showing flow relationships where
    nodes represent unique values and links show connections between stages.

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
    flow_columns : List[str]
        Columns defining the flow stages (in order).
    value_column : Optional[str]
        Column for value aggregation (None = count occurrences).
    aggregation : str
        Aggregation method: 'count', 'sum', 'nunique'.
    node_pad : int
        Padding between nodes.
    node_thickness : int
        Thickness of node rectangles.
    color_by_stage : bool
        If True, color nodes by their stage level.
    color_by_first_level : bool
        If True, color links by their source node at first level.

    Methods
    -------
    validate_data(df)
        Validate input data for Sankey diagram requirements
    process_data(df)
        Process data for Sankey diagram
    create_figure(processed_df)
        Create Sankey diagram figure from processed flow data
    get_stage_statistics(df)
        Calculate statistics for each stage in the flow

    Notes
    -----
    - Flow thickness proportional to count or aggregated value
    - Supports multiple aggregation methods
    - Customizable node and link colors
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

        # Flow configuration
        self.flow_columns: List[str] = self.plotly_config.get("flow_columns", [])

        # Value/aggregation configuration
        self.value_column: Optional[str] = self.plotly_config.get("value_column", None)
        self.aggregation: str = self.plotly_config.get("aggregation", "count")

        # Node configuration
        self.node_pad: int = self.plotly_config.get("node_pad", 15)
        self.node_thickness: int = self.plotly_config.get("node_thickness", 20)

        # Color configuration
        self.color_by_stage: bool = self.plotly_config.get("color_by_stage", True)
        self.color_by_first_level: bool = self.plotly_config.get(
            "color_by_first_level", False
        )
        self.link_opacity: float = self.plotly_config.get("link_opacity", 0.5)
        self.node_colors: List[str] = self.plotly_config.get(
            "node_colors", DEFAULT_NODE_COLORS
        )

        # Link color configuration
        self.link_color: str = self.plotly_config.get(
            "link_color", "rgba(180, 180, 180, 0.5)"
        )

        logger.info(
            f"SankeyStrategy initialized for "
            f"{self.metadata.get('use_case_id', 'unknown')}: "
            f"flow_columns={self.flow_columns}, "
            f"aggregation='{self.aggregation}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for Sankey diagram requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, flow columns missing, or fewer than
            2 flow columns specified.
        """
        logger.debug(
            f"Validating data - Shape: {df.shape}, " f"Columns: {df.columns.tolist()}"
        )

        if df.empty:
            raise ValueError("Input DataFrame is empty")

        # Validate flow columns exist
        if not self.flow_columns:
            raise ValueError(
                "No flow_columns specified in configuration. "
                "At least 2 columns are required for a Sankey diagram."
            )

        if len(self.flow_columns) < 2:
            raise ValueError(
                f"At least 2 flow columns required, got {len(self.flow_columns)}"
            )

        missing_cols = [c for c in self.flow_columns if c not in df.columns]
        if missing_cols:
            raise ValueError(
                f"Missing flow columns: {missing_cols}. "
                f"Available: {df.columns.tolist()}"
            )

        # Validate value column if specified
        if self.value_column and self.value_column not in df.columns:
            raise ValueError(
                f"Value column '{self.value_column}' not found. "
                f"Available: {df.columns.tolist()}"
            )

        logger.info(
            f"Data validation passed - {len(df)} records, "
            f"{len(self.flow_columns)} flow stages"
        )

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for Sankey diagram: aggregate flows between stages.

        Cleans data, removes placeholders, and aggregates flows between
        adjacent stages.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with flow columns.

        Returns
        -------
        pd.DataFrame
            Processed data with source, target, value columns for each link.
        """
        logger.info(f"Processing Sankey data with {len(self.flow_columns)} stages...")

        # Select only flow columns and drop nulls
        df_sankey = df[self.flow_columns].copy()
        initial_count = len(df_sankey)
        df_sankey = df_sankey.dropna()

        # Clean string values
        for col in self.flow_columns:
            df_sankey[col] = df_sankey[col].astype(str).str.strip()

        # Remove placeholder values
        placeholders = ["#N/D", "#N/A", "N/D", "", "nan", "None", "NaN"]
        for col in self.flow_columns:
            df_sankey = df_sankey[~df_sankey[col].isin(placeholders)]

        cleaned_count = len(df_sankey)
        logger.info(f"Data cleaned: {initial_count} -> {cleaned_count} rows")

        if df_sankey.empty:
            raise ValueError("No valid data remaining after cleaning flow columns.")

        # Aggregate: count occurrences for each unique path
        if self.value_column and self.value_column in df.columns:
            # Include value column for aggregation
            df_sankey["_value"] = df[self.value_column].loc[df_sankey.index]
            if self.aggregation == "sum":
                df_grouped = (
                    df_sankey.groupby(self.flow_columns)["_value"]
                    .sum()
                    .reset_index(name="value")
                )
            elif self.aggregation == "nunique":
                df_grouped = (
                    df_sankey.groupby(self.flow_columns)["_value"]
                    .nunique()
                    .reset_index(name="value")
                )
            else:
                df_grouped = (
                    df_sankey.groupby(self.flow_columns)
                    .size()
                    .reset_index(name="value")
                )
        else:
            # Count occurrences
            df_grouped = (
                df_sankey.groupby(self.flow_columns).size().reset_index(name="value")
            )

        logger.info(f"Aggregated to {len(df_grouped)} unique paths")

        return df_grouped

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create Sankey diagram figure from processed flow data.

        Builds node and link structures, applies styling, and creates
        Plotly Sankey visualization.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed data with flow columns and values.

        Returns
        -------
        go.Figure
            Configured Plotly Sankey figure.
        """
        logger.debug("Creating Sankey diagram figure...")

        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Build node and link structures
        all_labels, label_to_id, node_colors = self._build_nodes(processed_df)
        sources, targets, values, link_colors = self._build_links(
            processed_df, label_to_id, all_labels
        )

        # Handle title configuration
        title_config = chart_config.get("title", {})
        if isinstance(title_config, str):
            # Backward compatibility: string title
            show_title = True
            title_text = title_config
            title_font_size = 16
        else:
            # New format: dict with show, text, font
            show_title = title_config.get("show", True)
            title_text = (
                title_config.get("text", "Sankey Diagram") if show_title else ""
            )
            title_font_size = title_config.get("font", {}).get("size", 16)

        # Create Sankey trace
        sankey_trace = go.Sankey(
            node=dict(
                pad=self.node_pad,
                thickness=self.node_thickness,
                line=dict(color="black", width=0.5),
                label=all_labels,
                color=node_colors,
            ),
            link=dict(source=sources, target=targets, value=values, color=link_colors),
        )

        # Create figure
        fig = go.Figure(data=[sankey_trace])

        # Layout configuration
        height = layout_config.get("height", 900)
        use_autosize = layout_config.get("autosize", True)
        template = layout_config.get("template", "simple_white")

        # Get font size (global label font size)
        font_size = layout_config.get("font_size", 10)

        # Get margin configuration
        margin_config = layout_config.get("margin", {})
        margin = dict(
            l=margin_config.get("l", 10),
            r=margin_config.get("r", 10),
            t=margin_config.get("t", 60),
            b=margin_config.get("b", 20),
        )

        # Get paper background color
        paper_bgcolor = layout_config.get("paper_bgcolor", "white")

        # Build layout update dict
        layout_update = dict(
            font_size=font_size,
            height=height,
            template=template,
            margin=margin,
            paper_bgcolor=paper_bgcolor,
        )

        # Add title if enabled
        if show_title and title_text:
            layout_update["title"] = dict(
                text=title_text,
                x=0.5,
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

        # Log statistics
        n_nodes = len(all_labels)
        n_links = len(sources)
        logger.info(
            f"Sankey diagram created - {n_nodes} nodes, {n_links} links, "
            f"{len(self.flow_columns)} stages"
        )

        return fig

    def _build_nodes(
        self, df: pd.DataFrame
    ) -> Tuple[List[str], Dict[str, int], List[str]]:
        """
        Build node labels and mapping from flow data.

        Parameters
        ----------
        df : pd.DataFrame
            Processed flow data.

        Returns
        -------
        Tuple[List[str], Dict[str, int], List[str]]
            Tuple containing all_labels (list of unique node labels),
            label_to_id (mapping from label to numeric ID), and
            node_colors (list of colors for each node).
        """
        # Collect all unique labels across all flow columns
        all_labels = []
        stage_labels = {}  # Track which stage each label belongs to

        for stage_idx, col in enumerate(self.flow_columns):
            unique_vals = df[col].unique().tolist()
            for val in unique_vals:
                if val not in stage_labels:
                    stage_labels[val] = stage_idx
                    all_labels.append(val)

        # Create label to ID mapping
        label_to_id = {label: i for i, label in enumerate(all_labels)}

        # Assign colors based on stage
        node_colors = []
        for label in all_labels:
            stage_idx = stage_labels[label]
            color_idx = stage_idx % len(self.node_colors)
            node_colors.append(self.node_colors[color_idx])

        logger.debug(
            f"Built {len(all_labels)} nodes across " f"{len(self.flow_columns)} stages"
        )

        return all_labels, label_to_id, node_colors

    def _build_links(
        self, df: pd.DataFrame, label_to_id: Dict[str, int], all_labels: List[str]
    ) -> Tuple[List[int], List[int], List[float], List[str]]:
        """
        Build link structure connecting adjacent stages.

        Parameters
        ----------
        df : pd.DataFrame
            Processed flow data with value column.
        label_to_id : Dict[str, int]
            Mapping from label to numeric node ID.
        all_labels : List[str]
            List of all node labels.

        Returns
        -------
        Tuple[List[int], List[int], List[float], List[str]]
            Tuple containing sources (source node IDs), targets (target
            node IDs), values (flow values), and link_colors (colors for
            each link).
        """
        sources = []
        targets = []
        values = []
        link_colors = []

        # Build links for each stage transition
        for i in range(len(self.flow_columns) - 1):
            source_col = self.flow_columns[i]
            target_col = self.flow_columns[i + 1]

            # Aggregate values across identical source->target pairs
            stage_df = df.groupby([source_col, target_col])["value"].sum().reset_index()

            # Map labels to IDs and build link lists
            for _, row in stage_df.iterrows():
                source_label = row[source_col]
                target_label = row[target_col]
                value = row["value"]

                sources.append(label_to_id[source_label])
                targets.append(label_to_id[target_label])
                values.append(value)

                # Determine link color
                if self.color_by_first_level and i == 0:
                    # Color by first level source
                    first_stage_idx = label_to_id[source_label]
                    color_idx = first_stage_idx % len(self.node_colors)
                    base_color = self.node_colors[color_idx]
                    # Make link slightly more transparent
                    link_color = base_color.replace("0.8)", f"{self.link_opacity})")
                else:
                    link_color = self.link_color

                link_colors.append(link_color)

        logger.debug(
            f"Built {len(sources)} links connecting " f"{len(self.flow_columns)} stages"
        )

        return sources, targets, values, link_colors

    def get_stage_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate statistics for each stage in the flow.

        Parameters
        ----------
        df : pd.DataFrame
            Processed flow data.

        Returns
        -------
        Dict[str, Any]
            Statistics per stage including unique counts and top values.
        """
        stats = {}
        for col in self.flow_columns:
            unique_count = df[col].nunique()
            top_values = df[col].value_counts().head(5).to_dict()
            stats[col] = {"unique_count": unique_count, "top_values": top_values}
        return stats
