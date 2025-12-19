"""
Unit tests for NetworkStrategy.

This module tests the NetworkStrategy class which creates network (graph)
visualizations for bipartite and similarity networks.

Test Categories
---------------
1. Initialization (7 tests)
2. Validation (11 tests)
3. Bipartite Processing (8 tests)
4. Similarity Processing (9 tests)
5. Graph Building (6 tests)
6. Layout Calculation (5 tests)
7. Figure Creation (12 tests)
8. Integration (4 tests)
9. Edge Cases (10 tests)

Total: 72 tests
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pytest
import networkx as nx

from src.domain.plot_strategies.charts.network_strategy import NetworkStrategy


# =======================
# Helper Functions
# =======================


def get_bipartite_config():
    """Get configuration for bipartite network mode."""
    return {
        'metadata': {
            'use_case_id': 'UC-5.4',
            'module': 'module5'
        },
        'data': {},
        'visualization': {
            'strategy': 'NetworkStrategy',
            'plotly': {
                'mode': 'bipartite',
                'source_column': 'genesymbol',
                'target_column': 'compoundname',
                'node_size': 10,
                'edge_width': 0.5,
                'edge_color': '#888',
                'node_colors': {
                    'source': 'darkblue',
                    'target': 'darkgreen'
                },
                'layout_algorithm': {
                    'algorithm': 'spring',
                    'k': 0.15,
                    'iterations': 100,
                    'seed': 42
                },
                'chart': {
                    'title': {
                        'text': 'Gene-Compound Interaction Network',
                        'show': True
                    },
                    'show_legend': True
                },
                'layout': {
                    'height': 800,
                    'width': 1000,
                    'template': 'simple_white'
                }
            }
        }
    }


def get_similarity_config():
    """Get configuration for similarity network mode."""
    return {
        'metadata': {
            'use_case_id': 'UC-5.5',
            'module': 'module5'
        },
        'data': {},
        'visualization': {
            'strategy': 'NetworkStrategy',
            'plotly': {
                'mode': 'similarity',
                'group_by_column': 'genesymbol',
                'shared_column': 'compoundname',
                'min_edge_weight': 2,
                'node_size': 10,
                'edge_width': 0.5,
                'colorscale': 'YlGnBu',
                'layout_algorithm': {
                    'algorithm': 'spring',
                    'k': 0.15,
                    'iterations': 100,
                    'seed': 42
                },
                'chart': {
                    'title': {
                        'text': 'Gene Similarity Network',
                        'show': True
                    },
                    'show_legend': False
                },
                'layout': {
                    'height': 800,
                    'width': 1000,
                    'template': 'simple_white'
                }
            }
        }
    }


def get_bipartite_data():
    """
    Get sample bipartite network data.

    Returns
    -------
    pd.DataFrame
        Gene-Compound interaction data.
    """
    np.random.seed(42)
    return pd.DataFrame({
        'genesymbol': ['GeneA', 'GeneA', 'GeneB', 'GeneB', 'GeneC'],
        'compoundname': ['Benzene', 'Toluene', 'Benzene', 'Xylene', 'Toluene']
    })


def get_similarity_data():
    """
    Get sample similarity network data.

    Returns
    -------
    pd.DataFrame
        Gene-Compound data for similarity computation.
    """
    np.random.seed(42)
    return pd.DataFrame({
        'genesymbol': ['Gene1', 'Gene1', 'Gene1', 'Gene2', 'Gene2', 'Gene3', 'Gene3'],
        'compoundname': ['CompA', 'CompB', 'CompC', 'CompA', 'CompB', 'CompC', 'CompD']
    })


def get_large_bipartite_data():
    """
    Get large bipartite network data.

    Returns
    -------
    pd.DataFrame
        Large Gene-Compound interaction data.
    """
    np.random.seed(42)
    n = 50
    genes = [f'Gene{i}' for i in range(20)]
    compounds = [f'Comp{i}' for i in range(15)]

    data = []
    for _ in range(n):
        gene = np.random.choice(genes)
        compound = np.random.choice(compounds)
        data.append({'genesymbol': gene, 'compoundname': compound})

    return pd.DataFrame(data)


# =======================
# Test Class
# =======================


class TestNetworkStrategy:
    """Test suite for NetworkStrategy."""

    # =======================
    # 1. Initialization Tests
    # =======================

    def test_init_bipartite_mode(self):
        """Test initialization with bipartite mode."""
        # Arrange & Act
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)

        # Assert
        assert strategy is not None
        assert strategy.mode == 'bipartite'
        assert strategy.source_column == 'genesymbol'
        assert strategy.target_column == 'compoundname'

    def test_init_similarity_mode(self):
        """Test initialization with similarity mode."""
        # Arrange & Act
        config = get_similarity_config()
        strategy = NetworkStrategy(config)

        # Assert
        assert strategy is not None
        assert strategy.mode == 'similarity'
        assert strategy.group_by_column == 'genesymbol'
        assert strategy.shared_column == 'compoundname'

    def test_init_default_parameters(self):
        """Test initialization sets default parameters."""
        # Arrange & Act
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)

        # Assert
        assert strategy.node_size == 10
        assert strategy.edge_width == 0.5
        assert strategy.edge_color == '#888'
        assert strategy.layout_algorithm == 'spring'
        assert strategy.layout_k == 0.15
        assert strategy.layout_iterations == 100
        assert strategy.layout_seed == 42

    def test_init_custom_colors(self):
        """Test initialization with custom node colors."""
        # Arrange & Act
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)

        # Assert
        assert strategy.source_color == 'darkblue'
        assert strategy.target_color == 'darkgreen'

    def test_init_min_edge_weight(self):
        """Test initialization with min_edge_weight."""
        # Arrange & Act
        config = get_similarity_config()
        strategy = NetworkStrategy(config)

        # Assert
        assert strategy.min_edge_weight == 2

    def test_init_colorscale(self):
        """Test initialization with colorscale."""
        # Arrange & Act
        config = get_similarity_config()
        strategy = NetworkStrategy(config)

        # Assert
        assert strategy.colorscale == 'YlGnBu'

    def test_init_layout_config(self):
        """Test initialization extracts layout configuration."""
        # Arrange & Act
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)

        # Assert
        assert 'layout' in strategy.plotly_config
        assert strategy.plotly_config['layout']['height'] == 800
        assert strategy.plotly_config['layout']['width'] == 1000

    # =======================
    # 2. Validation Tests
    # =======================

    def test_validate_empty_dataframe_fails(self):
        """Test validation fails with empty DataFrame."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame()

        # Act & Assert
        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_bipartite_missing_source_column(self):
        """Test validation fails when source column is missing."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({'compoundname': ['Benzene']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing columns for bipartite mode"):
            strategy.validate_data(df)

    def test_validate_bipartite_missing_target_column(self):
        """Test validation fails when target column is missing."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({'genesymbol': ['GeneA']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing columns for bipartite mode"):
            strategy.validate_data(df)

    def test_validate_bipartite_success(self):
        """Test validation passes with valid bipartite data."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_similarity_missing_group_by_column(self):
        """Test validation fails when group_by_column is missing."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({'compoundname': ['CompA']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing columns for similarity mode"):
            strategy.validate_data(df)

    def test_validate_similarity_missing_shared_column(self):
        """Test validation fails when shared_column is missing."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({'genesymbol': ['Gene1']})

        # Act & Assert
        with pytest.raises(ValueError, match="Missing columns for similarity mode"):
            strategy.validate_data(df)

    def test_validate_similarity_no_config(self):
        """Test validation fails when similarity config is missing."""
        # Arrange
        config = get_bipartite_config()
        config['visualization']['plotly']['mode'] = 'similarity'
        # Don't set group_by_column and shared_column
        strategy = NetworkStrategy(config)
        df = get_similarity_data()

        # Act & Assert
        with pytest.raises(ValueError, match="Similarity mode requires"):
            strategy.validate_data(df)

    def test_validate_similarity_success(self):
        """Test validation passes with valid similarity data."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = get_similarity_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_unknown_mode_fails(self):
        """Test validation fails with unknown mode."""
        # Arrange
        config = get_bipartite_config()
        config['visualization']['plotly']['mode'] = 'invalid_mode'
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()

        # Act & Assert
        with pytest.raises(ValueError, match="Unknown mode"):
            strategy.validate_data(df)

    def test_validate_large_dataframe(self):
        """Test validation passes with large DataFrame."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_large_bipartite_data()

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    def test_validate_additional_columns_ok(self):
        """Test validation passes with additional columns."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        df['extra_column'] = 'extra'

        # Act & Assert (should not raise)
        strategy.validate_data(df)

    # =======================
    # 3. Bipartite Processing Tests
    # =======================

    def test_process_bipartite_creates_edges(self):
        """Test bipartite processing creates edge list."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert 'source' in result.columns
        assert 'target' in result.columns
        assert 'weight' in result.columns

    def test_process_bipartite_correct_edge_count(self):
        """Test bipartite processing creates correct number of edges."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Should have 5 unique edges (all rows are unique)
        assert len(result) == 5

    def test_process_bipartite_removes_nulls(self):
        """Test bipartite processing removes null values."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['GeneA', None, 'GeneC'],
            'compoundname': ['Benzene', 'Toluene', None]
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        assert len(result) == 1  # Only GeneA-Benzene remains

    def test_process_bipartite_removes_duplicates(self):
        """Test bipartite processing removes duplicate edges."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['GeneA', 'GeneA', 'GeneA'],
            'compoundname': ['Benzene', 'Benzene', 'Benzene']
        })

        # Act
        result = strategy.process_data(df)

        # Assert
        assert len(result) == 1  # Only one unique edge

    def test_process_bipartite_converts_to_string(self):
        """Test bipartite processing converts nodes to strings."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert all(isinstance(s, str) for s in result['source'])
        assert all(isinstance(t, str) for t in result['target'])

    def test_process_bipartite_sets_node_types(self):
        """Test bipartite processing sets node types."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert 'source_type' in result.columns
        assert 'target_type' in result.columns
        assert all(result['source_type'] == 'source')
        assert all(result['target_type'] == 'target')

    def test_process_bipartite_sets_weight_to_one(self):
        """Test bipartite processing sets weight to 1."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert all(result['weight'] == 1)

    def test_process_bipartite_large_dataset(self):
        """Test bipartite processing with large dataset."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_large_bipartite_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert len(result) > 0
        assert 'source' in result.columns
        assert 'target' in result.columns

    # =======================
    # 4. Similarity Processing Tests
    # =======================

    def test_process_similarity_creates_edges(self):
        """Test similarity processing creates edge list."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = get_similarity_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert isinstance(result, pd.DataFrame)
        assert 'source' in result.columns
        assert 'target' in result.columns
        assert 'weight' in result.columns

    def test_process_similarity_correct_weights(self):
        """Test similarity processing computes correct weights."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        # Gene1: {CompA, CompB, CompC}
        # Gene2: {CompA, CompB}
        # Gene3: {CompC, CompD}
        df = get_similarity_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Gene1-Gene2 share 2 compounds (CompA, CompB)
        # Gene1-Gene3 share 1 compound (CompC) - filtered out by min_edge_weight=2
        # Gene2-Gene3 share 0 compounds
        assert len(result) == 1  # Only Gene1-Gene2
        assert result.iloc[0]['weight'] == 2

    def test_process_similarity_respects_min_edge_weight(self):
        """Test similarity processing respects min_edge_weight."""
        # Arrange
        config = get_similarity_config()
        config['visualization']['plotly']['min_edge_weight'] = 1
        strategy = NetworkStrategy(config)
        df = get_similarity_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # With min_edge_weight=1, Gene1-Gene3 edge should appear
        assert len(result) >= 2

    def test_process_similarity_no_shared_elements(self):
        """Test similarity processing with no shared elements."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['Gene1', 'Gene2', 'Gene3'],
            'compoundname': ['CompA', 'CompB', 'CompC']
        })

        # Act & Assert
        with pytest.raises(ValueError, match="No valid edges"):
            strategy.process_data(df)

    def test_process_similarity_removes_nulls(self):
        """Test similarity processing removes null values."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['Gene1', 'Gene1', None, 'Gene2'],
            'compoundname': ['CompA', None, 'CompB', 'CompA']
        })

        # Act & Assert
        # Gene1: {CompA}, Gene2: {CompA} -> weight=1
        # But min_edge_weight=2, so no edges -> ValueError
        with pytest.raises(ValueError, match="No valid edges"):
            strategy.process_data(df)

    def test_process_similarity_single_group(self):
        """Test similarity processing with single group fails."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['Gene1', 'Gene1'],
            'compoundname': ['CompA', 'CompB']
        })

        # Act & Assert
        # Single group cannot form edges
        with pytest.raises(ValueError, match="No valid edges"):
            strategy.process_data(df)

    def test_process_similarity_converts_to_string(self):
        """Test similarity processing converts nodes to strings."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = get_similarity_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert all(isinstance(s, str) for s in result['source'])
        assert all(isinstance(t, str) for t in result['target'])

    def test_process_similarity_symmetric_edges(self):
        """Test similarity processing creates undirected edges."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = get_similarity_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        # Each pair should appear only once (not both A-B and B-A)
        for _, row in result.iterrows():
            reverse_edge = result[
                (result['source'] == row['target']) &
                (result['target'] == row['source'])
            ]
            assert len(reverse_edge) == 0

    def test_process_similarity_weight_range(self):
        """Test similarity processing weight values are positive integers."""
        # Arrange
        config = get_similarity_config()
        config['visualization']['plotly']['min_edge_weight'] = 1
        strategy = NetworkStrategy(config)
        df = get_similarity_data()

        # Act
        result = strategy.process_data(df)

        # Assert
        assert all(result['weight'] > 0)
        assert all(result['weight'] == result['weight'].astype(int))

    # =======================
    # 5. Graph Building Tests
    # =======================

    def test_build_graph_creates_networkx_graph(self):
        """Test _build_graph creates NetworkX graph."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        edges_df = pd.DataFrame({
            'source': ['A', 'B'],
            'target': ['C', 'D'],
            'weight': [1, 1]
        })

        # Act
        G = strategy._build_graph(edges_df)

        # Assert
        assert isinstance(G, nx.Graph)
        assert G.number_of_nodes() == 4
        assert G.number_of_edges() == 2

    def test_build_graph_adds_edges_with_weights(self):
        """Test _build_graph adds edges with weights."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        edges_df = pd.DataFrame({
            'source': ['A', 'B'],
            'target': ['C', 'D'],
            'weight': [2, 3]
        })

        # Act
        G = strategy._build_graph(edges_df)

        # Assert
        assert G.edges['A', 'C']['weight'] == 2
        assert G.edges['B', 'D']['weight'] == 3

    def test_build_graph_bipartite_node_types(self):
        """Test _build_graph sets node types for bipartite."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        edges_df = pd.DataFrame({
            'source': ['Gene1'],
            'target': ['Comp1'],
            'weight': [1],
            'source_type': ['source'],
            'target_type': ['target']
        })

        # Act
        G = strategy._build_graph(edges_df)

        # Assert
        assert G.nodes['Gene1']['node_type'] == 'source'
        assert G.nodes['Comp1']['node_type'] == 'target'

    def test_build_graph_similarity_no_node_types(self):
        """Test _build_graph doesn't set node types for similarity."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        edges_df = pd.DataFrame({
            'source': ['Gene1'],
            'target': ['Gene2'],
            'weight': [2]
        })

        # Act
        G = strategy._build_graph(edges_df)

        # Assert
        assert 'node_type' not in G.nodes['Gene1']
        assert 'node_type' not in G.nodes['Gene2']

    def test_build_graph_handles_duplicate_edges(self):
        """Test _build_graph handles duplicate edges."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        edges_df = pd.DataFrame({
            'source': ['A', 'A'],
            'target': ['B', 'B'],
            'weight': [1, 1]
        })

        # Act
        G = strategy._build_graph(edges_df)

        # Assert
        # Should have 1 edge (graphs don't support parallel edges)
        assert G.number_of_edges() == 1

    def test_build_graph_large_network(self):
        """Test _build_graph with large network."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_large_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        G = strategy._build_graph(processed)

        # Assert
        assert G.number_of_nodes() > 0
        assert G.number_of_edges() > 0

    # =======================
    # 6. Layout Calculation Tests
    # =======================

    def test_calculate_layout_spring(self):
        """Test layout calculation with spring algorithm."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        G = nx.Graph()
        G.add_edges_from([('A', 'B'), ('B', 'C')])

        # Act
        pos = strategy._calculate_layout(G)

        # Assert
        assert isinstance(pos, dict)
        assert len(pos) == 3
        # NetworkX returns numpy arrays, not tuples
        assert all(len(coord) == 2 for coord in pos.values())

    def test_calculate_layout_circular(self):
        """Test layout calculation with circular algorithm."""
        # Arrange
        config = get_bipartite_config()
        config['visualization']['plotly']['layout_algorithm']['algorithm'] = 'circular'
        strategy = NetworkStrategy(config)
        G = nx.Graph()
        G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'A')])

        # Act
        pos = strategy._calculate_layout(G)

        # Assert
        assert isinstance(pos, dict)
        assert len(pos) == 3

    def test_calculate_layout_kamada_kawai(self):
        """Test layout calculation with kamada_kawai algorithm."""
        # Arrange
        config = get_bipartite_config()
        config['visualization']['plotly']['layout_algorithm']['algorithm'] = 'kamada_kawai'
        strategy = NetworkStrategy(config)
        G = nx.Graph()
        G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'A')])

        # Act
        pos = strategy._calculate_layout(G)

        # Assert
        assert isinstance(pos, dict)
        assert len(pos) == 3

    def test_calculate_layout_shell(self):
        """Test layout calculation with shell algorithm."""
        # Arrange
        config = get_bipartite_config()
        config['visualization']['plotly']['layout_algorithm']['algorithm'] = 'shell'
        strategy = NetworkStrategy(config)
        G = nx.Graph()
        G.add_edges_from([('A', 'B'), ('B', 'C'), ('C', 'D')])

        # Act
        pos = strategy._calculate_layout(G)

        # Assert
        assert isinstance(pos, dict)
        assert len(pos) == 4

    def test_calculate_layout_unknown_fallback(self):
        """Test layout calculation falls back to spring for unknown algorithm."""
        # Arrange
        config = get_bipartite_config()
        config['visualization']['plotly']['layout_algorithm']['algorithm'] = 'unknown'
        strategy = NetworkStrategy(config)
        G = nx.Graph()
        G.add_edges_from([('A', 'B')])

        # Act
        pos = strategy._calculate_layout(G)

        # Assert
        assert isinstance(pos, dict)
        assert len(pos) == 2

    # =======================
    # 7. Figure Creation Tests
    # =======================

    def test_create_figure_returns_figure(self):
        """Test create_figure returns Plotly Figure."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_create_figure_bipartite_has_traces(self):
        """Test bipartite figure has edge and node traces."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Should have edge trace + 2 node traces (source, target)
        assert len(fig.data) >= 2

    def test_create_figure_similarity_has_traces(self):
        """Test similarity figure has edge and node traces."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = get_similarity_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Should have edge traces + 1 node trace
        assert len(fig.data) >= 2

    def test_create_figure_title_configuration(self):
        """Test figure title is configured correctly."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert 'Gene-Compound Interaction Network' in fig.layout.title.text

    def test_create_figure_layout_configuration(self):
        """Test figure applies layout configuration."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.height == 800
        assert fig.layout.width == 1000

    def test_create_figure_hides_axes(self):
        """Test figure hides axis ticks and labels."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.xaxis.showticklabels == False
        assert fig.layout.yaxis.showticklabels == False

    def test_create_figure_bipartite_shows_legend(self):
        """Test bipartite figure shows legend by default."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.showlegend == True

    def test_create_figure_similarity_hides_legend(self):
        """Test similarity figure hides legend by default."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = get_similarity_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.showlegend == False

    def test_create_figure_custom_show_legend(self):
        """Test figure respects show_legend configuration."""
        # Arrange
        config = get_similarity_config()
        config['visualization']['plotly']['chart']['show_legend'] = True
        strategy = NetworkStrategy(config)
        df = get_similarity_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.showlegend == True

    def test_create_figure_autosize(self):
        """Test figure with autosize enabled."""
        # Arrange
        config = get_bipartite_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_create_figure_title_hide(self):
        """Test figure with title hidden."""
        # Arrange
        config = get_bipartite_config()
        config['visualization']['plotly']['chart']['title']['show'] = False
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        # Title should be empty or not set
        assert fig.layout.title.text == '' or fig.layout.title.text is None

    def test_create_figure_background_colors(self):
        """Test figure with custom background colors."""
        # Arrange
        config = get_bipartite_config()
        config['visualization']['plotly']['layout']['plot_bgcolor'] = 'lightgray'
        config['visualization']['plotly']['layout']['paper_bgcolor'] = 'beige'
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()
        processed = strategy.process_data(df)

        # Act
        fig = strategy.create_figure(processed)

        # Assert
        assert fig.layout.plot_bgcolor == 'lightgray'
        assert fig.layout.paper_bgcolor == 'beige'

    # =======================
    # 8. Integration Tests
    # =======================

    def test_generate_plot_bipartite_full_workflow(self):
        """Test complete workflow for bipartite mode."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_bipartite_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_generate_plot_similarity_full_workflow(self):
        """Test complete workflow for similarity mode."""
        # Arrange
        config = get_similarity_config()
        strategy = NetworkStrategy(config)
        df = get_similarity_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_generate_plot_large_bipartite(self):
        """Test workflow with large bipartite dataset."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = get_large_bipartite_data()

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0

    def test_generate_plot_with_nulls(self):
        """Test workflow handles null values correctly."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['GeneA', None, 'GeneC'],
            'compoundname': ['Benzene', 'Toluene', None]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    # =======================
    # 9. Edge Cases
    # =======================

    def test_edge_case_single_edge(self):
        """Test network with single edge."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['GeneA'],
            'compoundname': ['Benzene']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_star_topology(self):
        """Test network with star topology (one hub)."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['Hub'] * 5,
            'compoundname': ['A', 'B', 'C', 'D', 'E']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_complete_graph(self):
        """Test similarity network with complete graph."""
        # Arrange
        config = get_similarity_config()
        config['visualization']['plotly']['min_edge_weight'] = 1
        strategy = NetworkStrategy(config)
        # All genes share CompA
        df = pd.DataFrame({
            'genesymbol': ['Gene1', 'Gene2', 'Gene3'] * 2,
            'compoundname': ['CompA'] * 6
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_disconnected_components(self):
        """Test network with disconnected components."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['Gene1', 'Gene2'],
            'compoundname': ['CompA', 'CompB']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_special_characters_in_names(self):
        """Test network with special characters in node names."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['Gene@1', 'Gene#2'],
            'compoundname': ['Comp$A', 'Comp%B']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_very_long_names(self):
        """Test network with very long node names."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        long_name = 'A' * 100
        df = pd.DataFrame({
            'genesymbol': [long_name],
            'compoundname': ['CompA']
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_numeric_node_names(self):
        """Test network with numeric node names."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': [1, 2, 3],
            'compoundname': [10, 20, 30]
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_min_edge_weight_filters_all(self):
        """Test similarity with min_edge_weight that filters all edges."""
        # Arrange
        config = get_similarity_config()
        config['visualization']['plotly']['min_edge_weight'] = 100
        strategy = NetworkStrategy(config)
        df = get_similarity_data()

        # Act & Assert
        with pytest.raises(ValueError, match="No valid edges"):
            strategy.generate_plot(df)

    def test_edge_case_identical_source_target_columns(self):
        """Test bipartite with same values in source and target."""
        # Arrange
        config = get_bipartite_config()
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['A', 'B'],
            'compoundname': ['A', 'B']  # Same as genes
        })

        # Act
        fig = strategy.generate_plot(df)

        # Assert
        assert isinstance(fig, go.Figure)

    def test_edge_case_self_loops_similarity(self):
        """Test similarity mode doesn't create self-loops."""
        # Arrange
        config = get_similarity_config()
        config['visualization']['plotly']['min_edge_weight'] = 1
        strategy = NetworkStrategy(config)
        df = pd.DataFrame({
            'genesymbol': ['Gene1', 'Gene1'],
            'compoundname': ['CompA', 'CompB']
        })

        # Act & Assert
        # Single group cannot create edges (combinations requires 2+ items)
        with pytest.raises(ValueError, match="No valid edges"):
            strategy.generate_plot(df)
