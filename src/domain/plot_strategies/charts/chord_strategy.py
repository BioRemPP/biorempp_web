"""
Chord Diagram Strategy.

This module implements the ChordStrategy class following the Strategy Pattern,
providing logic for generating chord diagrams that visualize relationships
between categorical entities as arcs connecting nodes arranged in a circle.

Classes
-------
ChordStrategy
    Concrete strategy for chord diagram generation using Plotly

Notes
-----
Chord diagrams are ideal for:
- Visualizing relationships between entities (source-target pairs)
- Showing interaction strength between categories
- Displaying sample similarity networks
- Mapping set intersections and overlaps

Processing Modes:
1. **Direct Aggregation Mode** (mode='aggregation'):
   - Groups by source and target columns
   - Aggregates count of interactions

2. **Pairwise Similarity Mode** (mode='pairwise'):
   - Computes shared entities between pairs
   - Creates links based on intersection size

3. **Set Intersection Mode** (mode='set_intersection'):
   - Computes pairwise intersections between named sets
   - Links represent overlap size between sets

For supported use cases, refer to the official documentation.

Version: 1.0.0
"""

import logging
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class ChordStrategy(BasePlotStrategy):
    """
    Chord diagram strategy for network relationship visualizations.

    This strategy creates chord diagrams showing relationships between
    categorical entities where:
    - Nodes: Categories arranged in a circle
    - Arcs: Connections between nodes weighted by interaction strength
    - Colors: Node/arc coloring based on category

    Attributes
    ----------
    data_config : Dict[str, Any]
        Data processing configuration
    plotly_config : Dict[str, Any]
        Plotly-specific configuration
    mode : str
        Processing mode: 'aggregation', 'pairwise', or 'set_intersection'
    source_column : str
        Column name for source entities
    target_column : str
        Column name for target entities
    value_column : Optional[str]
        Column for pre-aggregated values (if any)
    group_by_column : Optional[str]
        Column for grouping in pairwise mode
    shared_column : Optional[str]
        Column for computing shared entities in pairwise mode

    Notes
    -----
    Required YAML configuration structure:

    ```yaml
    visualization:
      strategy: "ChordStrategy"
      plotly:
        mode: "aggregation"  # or "pairwise", "set_intersection"
        source_column: "sample"
        target_column: "compoundclass"
        # For pairwise mode:
        # group_by_column: "sample"
        # shared_column: "compoundname"
        chart:
          title:
            text: "Sample-Compound Interactions"
          colorscale: "Category20"
        layout:
          height: 800
          width: 800
    ```

    Refer to the official documentation for supported use cases and
    detailed configuration examples.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize chord diagram strategy.

        Parameters
        ----------
        config : Dict[str, Any]
            Complete configuration from YAML file
        """
        super().__init__(config)
        self.data_config = config.get("data", {})
        self.plotly_config = self.viz_config.get("plotly", {})

        # Processing mode
        self.mode: str = self.plotly_config.get("mode", "aggregation")

        # Column configuration
        self.source_column: str = self.plotly_config.get("source_column", "source")
        self.target_column: str = self.plotly_config.get("target_column", "target")
        self.value_column: Optional[str] = self.plotly_config.get("value_column", None)

        # Pairwise mode configuration
        self.group_by_column: Optional[str] = self.plotly_config.get(
            "group_by_column", None
        )
        self.shared_column: Optional[str] = self.plotly_config.get(
            "shared_column", None
        )

        # Set intersection mode configuration
        self.set_column: Optional[str] = self.plotly_config.get("set_column", None)
        self.element_column: Optional[str] = self.plotly_config.get(
            "element_column", None
        )

        # Visual configuration
        self.colorscale: str = self.plotly_config.get("colorscale", "Category20")
        self.min_link_value: int = self.plotly_config.get("min_link_value", 1)

        # Circle arcs configuration
        circle_arc_config = self.plotly_config.get("circle_arcs", {})
        self.circle_arcs_enabled: bool = circle_arc_config.get("enabled", True)
        self.circle_arc_width: int = circle_arc_config.get("width", 15)
        self.circle_arc_gap: float = circle_arc_config.get("gap", 0.02)
        self.circle_arc_radius: float = circle_arc_config.get("radius", 1.0)
        self.circle_arc_proportional: bool = circle_arc_config.get("proportional", True)

        # Labels configuration
        label_config = self.plotly_config.get("labels", {})
        self.labels_enabled: bool = label_config.get("enabled", True)
        self.labels_radius_offset: float = label_config.get("radius_offset", 1.15)
        self.labels_font: Dict[str, Any] = label_config.get(
            "font", {"size": 11, "color": "#2c3e50"}
        )

        # Chord configuration
        chord_config = self.plotly_config.get("chords", {})
        self.chord_anchor: str = chord_config.get("anchor", "arc_midpoint")

        logger.info(
            f"ChordStrategy initialized for "
            f"{self.metadata.get('use_case_id', 'unknown')}: "
            f"mode='{self.mode}', "
            f"source='{self.source_column}', target='{self.target_column}', "
            f"circle_arcs={'enabled' if self.circle_arcs_enabled else 'disabled'}"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for chord diagram requirements.

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

        if df.empty:
            raise ValueError("Input DataFrame is empty")

        # Mode-specific validation
        if self.mode == "aggregation":
            required_cols = [self.source_column, self.target_column]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                raise ValueError(
                    f"Missing columns for aggregation mode: {missing}. "
                    f"Available: {df.columns.tolist()}"
                )

        elif self.mode == "pairwise":
            if not self.group_by_column or not self.shared_column:
                raise ValueError(
                    "Pairwise mode requires 'group_by_column' and "
                    "'shared_column' configuration."
                )
            required_cols = [self.group_by_column, self.shared_column]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                raise ValueError(
                    f"Missing columns for pairwise mode: {missing}. "
                    f"Available: {df.columns.tolist()}"
                )

        elif self.mode == "set_intersection":
            if not self.set_column or not self.element_column:
                raise ValueError(
                    "Set intersection mode requires 'set_column' and "
                    "'element_column' configuration."
                )
            required_cols = [self.set_column, self.element_column]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                raise ValueError(
                    f"Missing columns for set_intersection mode: {missing}. "
                    f"Available: {df.columns.tolist()}"
                )

        else:
            raise ValueError(
                f"Unknown mode: '{self.mode}'. "
                f"Supported: 'aggregation', 'pairwise', 'set_intersection'"
            )

        logger.info(f"Data validation passed - {len(df)} records, mode='{self.mode}'")

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data and create links DataFrame for chord diagram.

        Parameters
        ----------
        df : pd.DataFrame
            Input data with required columns

        Returns
        -------
        pd.DataFrame
            Links DataFrame with columns: source, target, value
        """
        logger.info(f"Processing data in '{self.mode}' mode...")

        if self.mode == "aggregation":
            links = self._process_aggregation(df)
        elif self.mode == "pairwise":
            links = self._process_pairwise(df)
        elif self.mode == "set_intersection":
            links = self._process_set_intersection(df)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

        # Filter by minimum link value
        if self.min_link_value > 1:
            initial_count = len(links)
            links = links[links["value"] >= self.min_link_value]
            logger.debug(
                f"Filtered links by min_value={self.min_link_value}: "
                f"{initial_count} -> {len(links)}"
            )

        if links.empty:
            raise ValueError(
                "No valid links after processing. "
                "Check data or adjust min_link_value."
            )

        logger.info(
            f"Links created - {len(links)} connections, "
            f"Value range: [{links['value'].min()}, {links['value'].max()}]"
        )

        return links

    def _process_aggregation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data using direct aggregation (groupby + count).

        Parameters
        ----------
        df : pd.DataFrame
            Input data

        Returns
        -------
        pd.DataFrame
            Links DataFrame
        """
        cols = [self.source_column, self.target_column]
        df_clean = df[cols].dropna()

        if self.value_column and self.value_column in df.columns:
            # Use pre-aggregated values
            df_clean = df[[*cols, self.value_column]].dropna()
            links = df_clean.groupby(cols)[self.value_column].sum().reset_index()
            links.columns = ["source", "target", "value"]
        else:
            # Count interactions
            links = df_clean.groupby(cols).size().reset_index(name="value")
            links.columns = ["source", "target", "value"]

        logger.debug(f"Aggregation: {len(df_clean)} records -> {len(links)} links")

        return links

    def _process_pairwise(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data using pairwise similarity (shared entities).

        Parameters
        ----------
        df : pd.DataFrame
            Input data

        Returns
        -------
        pd.DataFrame
            Links DataFrame with pairwise similarities
        """
        df_clean = df[[self.group_by_column, self.shared_column]].dropna()

        # Map each group to set of shared elements
        group_element_map = df_clean.groupby(self.group_by_column)[
            self.shared_column
        ].apply(set)

        all_groups = list(group_element_map.index)
        links_list = []

        # Compute pairwise intersections
        for group1, group2 in combinations(all_groups, 2):
            shared = group_element_map[group1].intersection(group_element_map[group2])
            strength = len(shared)

            if strength > 0:
                links_list.append(
                    {"source": group1, "target": group2, "value": strength}
                )

        links = pd.DataFrame(links_list)

        logger.debug(f"Pairwise: {len(all_groups)} groups -> {len(links)} links")

        return (
            links
            if not links.empty
            else pd.DataFrame(columns=["source", "target", "value"])
        )

    def _process_set_intersection(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data using set intersection mode.

        Parameters
        ----------
        df : pd.DataFrame
            Input data

        Returns
        -------
        pd.DataFrame
            Links DataFrame with set intersections
        """
        df_clean = df[[self.set_column, self.element_column]].dropna()

        # Build set dictionary
        set_element_map = (
            df_clean.groupby(self.set_column)[self.element_column].apply(set).to_dict()
        )

        set_names = list(set_element_map.keys())
        links_list = []

        # Compute pairwise intersections
        for name1, name2 in combinations(set_names, 2):
            intersection_size = len(
                set_element_map[name1].intersection(set_element_map[name2])
            )

            if intersection_size > 0:
                links_list.append(
                    {"source": name1, "target": name2, "value": intersection_size}
                )

        links = pd.DataFrame(links_list)

        logger.debug(f"Set intersection: {len(set_names)} sets -> {len(links)} links")

        return (
            links
            if not links.empty
            else pd.DataFrame(columns=["source", "target", "value"])
        )

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create chord diagram figure from processed links data.

        This implementation uses Plotly's graph_objects to create a custom
        chord diagram since Plotly Express doesn't have native chord support.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed links data with source, target, value columns

        Returns
        -------
        go.Figure
            Configured Plotly figure with chord diagram
        """
        logger.debug("Creating chord diagram figure...")

        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Title
        title_config = chart_config.get("title", {})
        show_title = title_config.get("show", True)
        title_text = title_config.get("text", "Chord Diagram") if show_title else ""

        # Get all unique nodes
        all_nodes = list(
            set(
                processed_df["source"].unique().tolist()
                + processed_df["target"].unique().tolist()
            )
        )
        all_nodes.sort()
        n_nodes = len(all_nodes)

        # Create node index mapping
        node_to_idx = {node: idx for idx, node in enumerate(all_nodes)}

        # Get colorscale
        colors = self._get_color_palette(n_nodes)

        # Calculate node connection values
        node_values = [
            self._count_connections(node, processed_df) for node in all_nodes
        ]
        total_value = sum(node_values)

        # Calculate arc spans for each node
        arc_spans = self._calculate_arc_spans(n_nodes, node_values, total_value)

        # Calculate value range for normalization
        min_value = processed_df["value"].min()
        max_value = processed_df["value"].max()

        logger.debug(
            f"Value range for line width: min={min_value}, " f"max={max_value}"
        )

        # Create traces
        traces = []

        # Add circle arc traces for each node
        if self.circle_arcs_enabled:
            for idx, node in enumerate(all_nodes):
                start_angle, end_angle = arc_spans[idx]
                arc_trace = self._create_circle_arc_trace(
                    start_angle,
                    end_angle,
                    self.circle_arc_radius,
                    colors[idx],
                    node,
                    node_values[idx],
                )
                traces.append(arc_trace)

        # Add chord (connection) traces for each link
        for _, row in processed_df.iterrows():
            source_idx = node_to_idx[row["source"]]
            target_idx = node_to_idx[row["target"]]
            value = row["value"]

            # Calculate connection points based on anchor setting
            if self.chord_anchor == "arc_midpoint":
                source_angle = (arc_spans[source_idx][0] + arc_spans[source_idx][1]) / 2
                target_angle = (arc_spans[target_idx][0] + arc_spans[target_idx][1]) / 2
            else:
                # Default to simple angle positions
                source_angle = arc_spans[source_idx][0]
                target_angle = arc_spans[target_idx][0]

            source_x = self.circle_arc_radius * np.cos(source_angle)
            source_y = self.circle_arc_radius * np.sin(source_angle)
            target_x = self.circle_arc_radius * np.cos(target_angle)
            target_y = self.circle_arc_radius * np.sin(target_angle)

            # Create bezier curve for the chord
            chord_trace = self._create_chord_trace(
                source_x,
                source_y,
                target_x,
                target_y,
                value,
                colors[source_idx],
                row["source"],
                row["target"],
                min_value,
                max_value,
            )
            traces.append(chord_trace)

        # Add label traces
        if self.labels_enabled:
            label_radius = self.circle_arc_radius * self.labels_radius_offset
            label_angles = [
                (arc_spans[i][0] + arc_spans[i][1]) / 2 for i in range(n_nodes)
            ]
            label_x = label_radius * np.cos(label_angles)
            label_y = label_radius * np.sin(label_angles)

            label_trace = go.Scatter(
                x=label_x.tolist(),
                y=label_y.tolist(),
                mode="text",
                text=all_nodes,
                textfont=self.labels_font,
                hoverinfo="skip",
                showlegend=False,
            )
            traces.append(label_trace)

        # Create figure
        fig = go.Figure(data=traces)

        # Layout configuration
        height = layout_config.get("height", 800)
        use_autosize = layout_config.get("autosize", False)

        layout_update = {
            "title": dict(
                text=title_text,
                x=0.5,
                xanchor="center",
                font=title_config.get("font", dict(size=16)),
            ),
            "showlegend": False,
            "hovermode": "closest",
            "xaxis": dict(
                showgrid=False, zeroline=False, showticklabels=False, range=[-1.5, 1.5]
            ),
            "yaxis": dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-1.5, 1.5],
                scaleanchor="x",
                scaleratio=1,
            ),
            "height": height,
            "template": layout_config.get("template", "simple_white"),
            "margin": layout_config.get("margin", dict(l=50, r=50, t=80, b=50)),
        }

        # Add autosize if enabled
        if use_autosize:
            layout_update["autosize"] = True
        else:
            if layout_config.get("width"):
                layout_update["width"] = layout_config.get("width", 800)

        fig.update_layout(**layout_update)

        logger.info(
            f"Chord diagram created - " f"{n_nodes} nodes, {len(processed_df)} links"
        )

        return fig

    def _create_chord_trace(
        self,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        value: float,
        color: str,
        source_name: str,
        target_name: str,
        min_value: float,
        max_value: float,
    ) -> go.Scatter:
        """
        Create a bezier curve trace representing a chord.

        Parameters
        ----------
        x0, y0 : float
            Source node coordinates.
        x1, y1 : float
            Target node coordinates.
        value : float
            Link value (connection strength).
        color : str
            Color for the chord.
        source_name : str
            Name of source node.
        target_name : str
            Name of target node.
        min_value : float
            Minimum value in the dataset (for normalization).
        max_value : float
            Maximum value in the dataset (for normalization).

        Returns
        -------
        go.Scatter
            Scatter trace representing the chord.
        """
        # Create bezier curve through center
        n_points = 50
        t = np.linspace(0, 1, n_points)

        # Control point at origin (center of circle)
        cx, cy = 0, 0

        # Quadratic bezier curve
        x = (1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t**2 * x1
        y = (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t**2 * y1

        # Normalize value to 0-1 range, then scale to line width (1-15)
        # This ensures visual differentiation between connection strengths
        value_range = max_value - min_value
        if value_range > 0:
            normalized = (value - min_value) / value_range
        else:
            normalized = 0.5  # All values equal, use middle width

        # Scale to line width: min=1, max=15
        min_width = 1
        max_width = 15
        line_width = min_width + normalized * (max_width - min_width)

        return go.Scatter(
            x=x.tolist(),
            y=y.tolist(),
            mode="lines",
            line=dict(width=line_width, color=color),
            opacity=0.6,
            hoverinfo="text",
            hovertext=f"<b>{source_name}</b> ↔ <b>{target_name}</b><br>Value: {int(value)}",
            showlegend=False,
        )

    def _get_color_palette(self, n_colors: int) -> List[str]:
        """
        Get a color palette for nodes.

        Parameters
        ----------
        n_colors : int
            Number of colors needed.

        Returns
        -------
        List[str]
            List of color values.
        """
        import plotly.express as px

        # Use Plotly's qualitative color sequences
        if self.colorscale == "Category20":
            colors = px.colors.qualitative.Plotly * ((n_colors // 10) + 1)
        elif self.colorscale == "Category20b":
            colors = px.colors.qualitative.D3 * ((n_colors // 10) + 1)
        elif self.colorscale == "Pastel1":
            colors = px.colors.qualitative.Pastel1 * ((n_colors // 9) + 1)
        else:
            colors = px.colors.qualitative.Plotly * ((n_colors // 10) + 1)

        return colors[:n_colors]

    def _count_connections(self, node: str, links_df: pd.DataFrame) -> int:
        """
        Count total connections for a node.

        Parameters
        ----------
        node : str
            Node name.
        links_df : pd.DataFrame
            Links DataFrame.

        Returns
        -------
        int
            Total connection count.
        """
        source_count = links_df[links_df["source"] == node]["value"].sum()
        target_count = links_df[links_df["target"] == node]["value"].sum()
        return int(source_count + target_count)

    def _calculate_arc_spans(
        self, n_nodes: int, node_values: List[int], total_value: int
    ) -> List[Tuple[float, float]]:
        """
        Calculate arc span angles for each node.

        Parameters
        ----------
        n_nodes : int
            Number of nodes.
        node_values : List[int]
            Connection values for each node.
        total_value : int
            Total of all connection values.

        Returns
        -------
        List[Tuple[float, float]]
            List of (start_angle, end_angle) tuples for each node.
        """
        arc_spans = []
        current_angle = 0

        if self.circle_arc_proportional and total_value > 0:
            # Proportional to connections
            available_angle = 2 * np.pi - n_nodes * self.circle_arc_gap
            for value in node_values:
                span = (value / total_value) * available_angle
                arc_spans.append((current_angle, current_angle + span))
                current_angle += span + self.circle_arc_gap
        else:
            # Equal spans
            span = (2 * np.pi - n_nodes * self.circle_arc_gap) / n_nodes
            for _ in range(n_nodes):
                arc_spans.append((current_angle, current_angle + span))
                current_angle += span + self.circle_arc_gap

        return arc_spans

    def _create_circle_arc_trace(
        self,
        start_angle: float,
        end_angle: float,
        radius: float,
        color: str,
        node_name: str,
        value: int,
    ) -> go.Scatter:
        """
        Create a circular arc trace for a node.

        Parameters
        ----------
        start_angle : float
            Starting angle in radians.
        end_angle : float
            Ending angle in radians.
        radius : float
            Radius of the circle.
        color : str
            Color of the arc.
        node_name : str
            Name of the node.
        value : int
            Total connection value for this node.

        Returns
        -------
        go.Scatter
            Scatter trace representing the circular arc.
        """
        # Number of points for smooth arc
        n_points = 50
        angles = np.linspace(start_angle, end_angle, n_points)

        # Calculate arc coordinates
        x = radius * np.cos(angles)
        y = radius * np.sin(angles)

        return go.Scatter(
            x=x.tolist(),
            y=y.tolist(),
            mode="lines",
            line=dict(width=self.circle_arc_width, color=color),
            hoverinfo="text",
            hovertext=f"<b>{node_name}</b><br>Total connections: {value}",
            showlegend=False,
        )
