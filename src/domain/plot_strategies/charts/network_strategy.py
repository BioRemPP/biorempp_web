"""
Network Strategy - Interaction Network Visualizations.

This module implements the NetworkStrategy for creating network (graph) diagrams
that visualize relationships between entities such as genes, compounds, samples,
and pathways.

Classes
-------
NetworkStrategy
    Strategy for network diagram generation using Plotly and NetworkX.

Notes
-----
- Supports bipartite networks (two node types)
- Supports similarity networks (weighted edges based on shared attributes)
- Multiple layout algorithms available (spring, circular, kamada_kawai)

For supported use cases, refer to the official documentation.
"""

import logging
from itertools import combinations
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.domain.plot_strategies.base.base_plot_strategy import BasePlotStrategy

logger = logging.getLogger(__name__)


class NetworkStrategy(BasePlotStrategy):
    """
    Strategy for network diagram interaction visualizations.

    This strategy creates network graphs showing relationships between entities
    where nodes represent entities and edges represent connections.

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
    mode : str
        Processing mode: 'bipartite' or 'similarity'.
    source_column : str
        Column name for source/primary entities.
    target_column : str
        Column name for target/secondary entities.
    node_type_column : Optional[str]
        Column indicating node type (for bipartite mode).
    shared_column : Optional[str]
        Column for computing similarity (for similarity mode).

    Methods
    -------
    validate_data(df)
        Validate input data for network diagram requirements
    process_data(df)
        Process data and create graph structure
    create_figure(processed_df)
        Create network diagram figure from processed graph data

    Notes
    -----
    - Supports bipartite and similarity network modes
    - Multiple layout algorithms available
    - Visual encoding: node size/color by degree, edge width by weight
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

        # Processing mode
        self.mode: str = self.plotly_config.get("mode", "bipartite")

        # Column configuration
        self.source_column: str = self.plotly_config.get("source_column", "genesymbol")
        self.target_column: str = self.plotly_config.get(
            "target_column", "compoundname"
        )

        # Similarity mode configuration
        self.group_by_column: Optional[str] = self.plotly_config.get(
            "group_by_column", None
        )
        self.shared_column: Optional[str] = self.plotly_config.get(
            "shared_column", None
        )

        # Layout algorithm configuration
        layout_algo_config = self.plotly_config.get("layout_algorithm", {})
        self.layout_algorithm: str = layout_algo_config.get("algorithm", "spring")
        self.layout_k: float = layout_algo_config.get("k", 0.15)
        self.layout_iterations: int = layout_algo_config.get("iterations", 100)
        self.layout_seed: int = layout_algo_config.get("seed", 42)

        # Visual configuration
        self.node_size: int = self.plotly_config.get("node_size", 10)
        self.edge_width: float = self.plotly_config.get("edge_width", 0.5)
        self.edge_color: str = self.plotly_config.get("edge_color", "#888")
        self.colorscale: str = self.plotly_config.get("colorscale", "YlGnBu")

        # Node type colors (for bipartite mode)
        node_colors = self.plotly_config.get("node_colors", {})
        self.source_color: str = node_colors.get("source", "darkblue")
        self.target_color: str = node_colors.get("target", "darkgreen")

        # Minimum edge weight (for similarity mode)
        self.min_edge_weight: int = self.plotly_config.get("min_edge_weight", 1)

        logger.info(
            f"NetworkStrategy initialized for "
            f"{self.metadata.get('use_case_id', 'unknown')}: "
            f"mode='{self.mode}', "
            f"source='{self.source_column}', target='{self.target_column}'"
        )

    def validate_data(self, df: pd.DataFrame) -> None:
        """
        Validate input data for network diagram requirements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data to validate.

        Raises
        ------
        ValueError
            If DataFrame is empty, required columns missing, or mode
            configuration invalid.
        """
        logger.debug(
            f"Validating data - Shape: {df.shape}, " f"Columns: {df.columns.tolist()}"
        )

        if df.empty:
            raise ValueError("Input DataFrame is empty")

        # Mode-specific validation
        if self.mode == "bipartite":
            required_cols = [self.source_column, self.target_column]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                raise ValueError(
                    f"Missing columns for bipartite mode: {missing}. "
                    f"Available: {df.columns.tolist()}"
                )

        elif self.mode == "similarity":
            if not self.group_by_column or not self.shared_column:
                raise ValueError(
                    "Similarity mode requires 'group_by_column' and "
                    "'shared_column' configuration."
                )
            required_cols = [self.group_by_column, self.shared_column]
            missing = [c for c in required_cols if c not in df.columns]
            if missing:
                raise ValueError(
                    f"Missing columns for similarity mode: {missing}. "
                    f"Available: {df.columns.tolist()}"
                )

        else:
            raise ValueError(
                f"Unknown mode: '{self.mode}'. " f"Supported: 'bipartite', 'similarity'"
            )

        logger.info(f"Data validation passed - {len(df)} records, mode='{self.mode}'")

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data and create graph structure for network visualization.

        Creates edge list based on configured mode (bipartite or similarity).

        Parameters
        ----------
        df : pd.DataFrame
            Input data with required columns.

        Returns
        -------
        pd.DataFrame
            Graph data as DataFrame with source, target, and weight columns.
        """
        logger.info(f"Processing data in '{self.mode}' mode...")

        if self.mode == "bipartite":
            graph_data = self._process_bipartite(df)
        elif self.mode == "similarity":
            graph_data = self._process_similarity(df)
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

        if graph_data.empty:
            raise ValueError(
                "No valid edges after processing. "
                "Check data or adjust min_edge_weight."
            )

        logger.info(f"Graph data created - {len(graph_data)} edges")

        return graph_data

    def _process_bipartite(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for bipartite network (two node types).

        Parameters
        ----------
        df : pd.DataFrame
            Input data.

        Returns
        -------
        pd.DataFrame
            Edge list with source, target, source_type, target_type columns.
        """
        cols = [self.source_column, self.target_column]
        df_clean = df[cols].dropna().drop_duplicates()

        # Create edge list with node type information
        edges = []
        for _, row in df_clean.iterrows():
            edges.append(
                {
                    "source": str(row[self.source_column]),
                    "target": str(row[self.target_column]),
                    "source_type": "source",
                    "target_type": "target",
                    "weight": 1,
                }
            )

        edges_df = pd.DataFrame(edges)

        logger.debug(
            f"Bipartite: {len(df_clean)} interactions -> {len(edges_df)} edges"
        )

        return edges_df

    def _process_similarity(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Process data for similarity network (weighted edges).

        Computes pairwise similarity based on shared elements.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.

        Returns
        -------
        pd.DataFrame
            Edge list with source, target, and weight columns.
        """
        df_clean = df[[self.group_by_column, self.shared_column]].dropna()

        # Map each group to set of shared elements
        group_element_map = df_clean.groupby(self.group_by_column)[
            self.shared_column
        ].apply(set)

        all_groups = list(group_element_map.index)
        edges_list = []

        # Compute pairwise similarities (shared elements)
        for group1, group2 in combinations(all_groups, 2):
            shared = group_element_map[group1].intersection(group_element_map[group2])
            weight = len(shared)

            if weight >= self.min_edge_weight:
                edges_list.append(
                    {"source": str(group1), "target": str(group2), "weight": weight}
                )

        edges_df = pd.DataFrame(edges_list)

        logger.debug(f"Similarity: {len(all_groups)} groups -> {len(edges_df)} edges")

        return (
            edges_df
            if not edges_df.empty
            else pd.DataFrame(columns=["source", "target", "weight"])
        )

    def create_figure(self, processed_df: pd.DataFrame) -> go.Figure:
        """
        Create network diagram figure from processed graph data.

        Parameters
        ----------
        processed_df : pd.DataFrame
            Processed edge list data.

        Returns
        -------
        go.Figure
            Configured Plotly figure with network diagram.
        """
        logger.debug("Creating network diagram figure...")

        chart_config = self.plotly_config.get("chart", {})
        layout_config = self.plotly_config.get("layout", {})

        # Build NetworkX graph
        G = self._build_graph(processed_df)

        # Calculate node positions
        pos = self._calculate_layout(G)

        # Handle title configuration (support both string and dict)
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
                title_config.get("text", "Network Diagram") if show_title else ""
            )
            title_font_size = title_config.get("font", {}).get("size", 16)

        # Create traces
        traces = []

        # Create edge traces
        edge_traces = self._create_edge_traces(G, pos, processed_df)
        traces.extend(edge_traces)

        # Create node traces
        if self.mode == "bipartite":
            node_traces = self._create_bipartite_node_traces(G, pos, processed_df)
        else:
            node_traces = self._create_similarity_node_traces(G, pos)

        traces.extend(node_traces)

        # Create figure
        fig = go.Figure(data=traces)

        # Layout configuration
        height = layout_config.get("height", 800)
        use_autosize = layout_config.get("autosize", False)

        # Show legend configuration
        show_legend_config = chart_config.get("show_legend", None)
        if show_legend_config is not None:
            show_legend = show_legend_config
        else:
            # Default: show legend only for bipartite mode
            show_legend = self.mode == "bipartite"

        # Get margin configuration
        margin_config = layout_config.get("margin", {})
        margin = dict(
            l=margin_config.get("l", 20),
            r=margin_config.get("r", 20),
            t=margin_config.get("t", 60),
            b=margin_config.get("b", 20),
        )

        # Get background colors
        plot_bgcolor = layout_config.get("plot_bgcolor", "white")
        paper_bgcolor = layout_config.get("paper_bgcolor", "white")

        # Get template
        template = layout_config.get("template", "simple_white")

        # Build layout update dict
        layout_update = {
            "height": height,
            "showlegend": show_legend,
            "legend": dict(x=1, y=1, bordercolor="Gainsboro", borderwidth=1),
            "hovermode": "closest",
            "xaxis": dict(showgrid=False, zeroline=False, showticklabels=False),
            "yaxis": dict(showgrid=False, zeroline=False, showticklabels=False),
            "plot_bgcolor": plot_bgcolor,
            "paper_bgcolor": paper_bgcolor,
            "template": template,
            "margin": margin,
        }

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

        logger.info(
            f"Network diagram created - "
            f"{G.number_of_nodes()} nodes, {G.number_of_edges()} edges, "
            f"Layout: {self.layout_algorithm}"
        )

        return fig

    def _build_graph(self, edges_df: pd.DataFrame) -> nx.Graph:
        """
        Build NetworkX graph from edge list.

        Parameters
        ----------
        edges_df : pd.DataFrame
            Edge list with source, target, weight columns.

        Returns
        -------
        nx.Graph
            NetworkX graph object.
        """
        G = nx.Graph()

        for _, row in edges_df.iterrows():
            source = row["source"]
            target = row["target"]
            weight = row.get("weight", 1)

            # Add nodes with type attribute (for bipartite)
            if self.mode == "bipartite":
                source_type = row.get("source_type", "source")
                target_type = row.get("target_type", "target")
                G.add_node(source, node_type=source_type)
                G.add_node(target, node_type=target_type)
            else:
                G.add_node(source)
                G.add_node(target)

            # Add edge with weight
            G.add_edge(source, target, weight=weight)

        logger.debug(
            f"Graph built: {G.number_of_nodes()} nodes, " f"{G.number_of_edges()} edges"
        )

        return G

    def _calculate_layout(self, G: nx.Graph) -> Dict[str, Tuple[float, float]]:
        """
        Calculate node positions using specified layout algorithm.

        Parameters
        ----------
        G : nx.Graph
            NetworkX graph.

        Returns
        -------
        Dict[str, Tuple[float, float]]
            Dictionary mapping node names to (x, y) coordinates.
        """
        if self.layout_algorithm == "spring":
            pos = nx.spring_layout(
                G,
                k=self.layout_k,
                iterations=self.layout_iterations,
                seed=self.layout_seed,
            )
        elif self.layout_algorithm == "circular":
            pos = nx.circular_layout(G)
        elif self.layout_algorithm == "kamada_kawai":
            pos = nx.kamada_kawai_layout(G)
        elif self.layout_algorithm == "shell":
            pos = nx.shell_layout(G)
        else:
            logger.warning(
                f"Unknown layout algorithm '{self.layout_algorithm}', "
                f"using spring layout"
            )
            pos = nx.spring_layout(G, k=self.layout_k, seed=self.layout_seed)

        logger.debug(f"Layout calculated using {self.layout_algorithm}")

        return pos

    def _create_edge_traces(
        self, G: nx.Graph, pos: Dict[str, Tuple[float, float]], edges_df: pd.DataFrame
    ) -> List[go.Scatter]:
        """
        Create edge traces for the network.

        Parameters
        ----------
        G : nx.Graph
            NetworkX graph.
        pos : Dict
            Node positions.
        edges_df : pd.DataFrame
            Edge data with weights.

        Returns
        -------
        List[go.Scatter]
            List of edge traces.
        """
        traces = []

        # For similarity mode with varying weights, create individual edge traces
        if self.mode == "similarity" and "weight" in edges_df.columns:
            weights = edges_df["weight"].values
            max_weight = max(weights) if len(weights) > 0 else 1
            min_weight = min(weights) if len(weights) > 0 else 1

            for edge in G.edges():
                source, target = edge
                x0, y0 = pos[source]
                x1, y1 = pos[target]
                weight = G.edges[edge].get("weight", 1)

                # Normalize width (1 to 5)
                if max_weight > min_weight:
                    normalized = (weight - min_weight) / (max_weight - min_weight)
                else:
                    normalized = 0.5
                width = 1 + normalized * 4

                trace = go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode="lines",
                    line=dict(
                        width=width,
                        color=f"rgba(136, 136, 136, {0.3 + normalized * 0.5})",
                    ),
                    hoverinfo="text",
                    hovertext=f"{source} ↔ {target}<br>Shared: {weight}",
                    showlegend=False,
                )
                traces.append(trace)
        else:
            # Single edge trace for bipartite mode
            edge_x, edge_y = [], []
            for source, target in G.edges():
                x0, y0 = pos[source]
                x1, y1 = pos[target]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            edge_trace = go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                hoverinfo="none",
                line=dict(width=self.edge_width, color=self.edge_color),
                showlegend=False,
            )
            traces.append(edge_trace)

        return traces

    def _create_bipartite_node_traces(
        self, G: nx.Graph, pos: Dict[str, Tuple[float, float]], edges_df: pd.DataFrame
    ) -> List[go.Scatter]:
        """
        Create node traces for bipartite network (two colors).

        Parameters
        ----------
        G : nx.Graph
            NetworkX graph.
        pos : Dict
            Node positions.
        edges_df : pd.DataFrame
            Edge data with node type information.

        Returns
        -------
        List[go.Scatter]
            List of node traces (one per node type).
        """
        traces = []
        degree_dict = dict(G.degree())

        # Separate nodes by type
        source_nodes = set(edges_df["source"].unique())
        target_nodes = set(edges_df["target"].unique())

        # Source node trace
        source_x, source_y, source_text = [], [], []
        for node in G.nodes():
            if node in source_nodes and node not in target_nodes:
                x, y = pos[node]
                source_x.append(x)
                source_y.append(y)
                degree = degree_dict.get(node, 0)
                source_text.append(
                    f"<b>{self.source_column}:</b> {node}<br>"
                    f"<b>Interactions:</b> {degree}"
                )

        if source_x:
            source_trace = go.Scatter(
                x=source_x,
                y=source_y,
                mode="markers",
                name=self.source_column.replace("_", " ").title(),
                hoverinfo="text",
                text=source_text,
                marker=dict(
                    size=self.node_size,
                    color=self.source_color,
                    line=dict(width=0.5, color="white"),
                ),
            )
            traces.append(source_trace)

        # Target node trace
        target_x, target_y, target_text = [], [], []
        for node in G.nodes():
            if node in target_nodes and node not in source_nodes:
                x, y = pos[node]
                target_x.append(x)
                target_y.append(y)
                degree = degree_dict.get(node, 0)
                target_text.append(
                    f"<b>{self.target_column}:</b> {node}<br>"
                    f"<b>Interactions:</b> {degree}"
                )

        if target_x:
            target_trace = go.Scatter(
                x=target_x,
                y=target_y,
                mode="markers",
                name=self.target_column.replace("_", " ").title(),
                hoverinfo="text",
                text=target_text,
                marker=dict(
                    size=self.node_size,
                    color=self.target_color,
                    line=dict(width=0.5, color="white"),
                ),
            )
            traces.append(target_trace)

        return traces

    def _create_similarity_node_traces(
        self, G: nx.Graph, pos: Dict[str, Tuple[float, float]]
    ) -> List[go.Scatter]:
        """
        Create node traces for similarity network (color by degree).

        Parameters
        ----------
        G : nx.Graph
            NetworkX graph.
        pos : Dict
            Node positions.

        Returns
        -------
        List[go.Scatter]
            Single node trace with color scale.
        """
        node_x, node_y, node_text, node_color = [], [], [], []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            degree = G.degree(node)
            node_text.append(f"<b>{node}</b><br>Connections: {degree}")
            node_color.append(degree)

        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers",
            hoverinfo="text",
            text=node_text,
            showlegend=False,
            marker=dict(
                showscale=True,
                colorscale=self.colorscale,
                reversescale=True,
                color=node_color,
                size=self.node_size + 5,
                colorbar=dict(
                    thickness=15,
                    title=dict(text="Connections", side="right"),
                    xanchor="left"
                ),
                line=dict(width=2, color="white"),
            ),
        )

        return [node_trace]
