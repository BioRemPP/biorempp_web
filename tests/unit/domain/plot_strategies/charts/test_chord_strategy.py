"""
Unit Tests for ChordStrategy.

This module tests the ChordStrategy class, which creates chord diagrams for
visualizing relationships between categorical entities.

Test Categories:
- Initialization: Test strategy creation and configuration
- Data Validation: Test validate_data() method for all modes
- Data Processing - Aggregation Mode: Test _process_aggregation()
- Data Processing - Pairwise Mode: Test _process_pairwise()
- Data Processing - Set Intersection Mode: Test _process_set_intersection()
- Figure Creation: Test create_figure() and helper methods
- Integration: Test complete workflow
- Edge Cases: Test boundary conditions
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from src.domain.plot_strategies.charts.chord_strategy import ChordStrategy


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_aggregation_config():
    """Get configuration for aggregation mode."""
    return {
        'metadata': {'use_case_id': 'UC-5.1'},
        'visualization': {
            'strategy': 'ChordStrategy',
            'plotly': {
                'mode': 'aggregation',
                'source_column': 'sample',
                'target_column': 'compoundclass',
                'min_link_value': 1,
                'chart': {'title': {'text': 'Sample-Compound Interactions'}},
                'layout': {'height': 800, 'width': 800}
            }
        }
    }


def get_pairwise_config():
    """Get configuration for pairwise mode."""
    return {
        'metadata': {'use_case_id': 'UC-5.2'},
        'visualization': {
            'strategy': 'ChordStrategy',
            'plotly': {
                'mode': 'pairwise',
                'group_by_column': 'sample',
                'shared_column': 'compoundname',
                'min_link_value': 1
            }
        }
    }


def get_set_intersection_config():
    """Get configuration for set_intersection mode."""
    return {
        'metadata': {'use_case_id': 'UC-7.2'},
        'visualization': {
            'strategy': 'ChordStrategy',
            'plotly': {
                'mode': 'set_intersection',
                'set_column': 'risk_category',
                'element_column': 'compound',
                'min_link_value': 1
            }
        }
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestChordStrategyInitialization:
    """Test ChordStrategy initialization."""

    def test_initialization_aggregation_mode(self):
        """Test initialization with aggregation mode."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)

        assert strategy.mode == 'aggregation'
        assert strategy.source_column == 'sample'
        assert strategy.target_column == 'compoundclass'
        assert strategy.min_link_value == 1

    def test_initialization_pairwise_mode(self):
        """Test initialization with pairwise mode."""
        config = get_pairwise_config()
        strategy = ChordStrategy(config)

        assert strategy.mode == 'pairwise'
        assert strategy.group_by_column == 'sample'
        assert strategy.shared_column == 'compoundname'

    def test_initialization_set_intersection_mode(self):
        """Test initialization with set_intersection mode."""
        config = get_set_intersection_config()
        strategy = ChordStrategy(config)

        assert strategy.mode == 'set_intersection'
        assert strategy.set_column == 'risk_category'
        assert strategy.element_column == 'compound'

    def test_initialization_default_values(self):
        """Test that default values are set correctly."""
        config = {
            'metadata': {},
            'visualization': {'strategy': 'ChordStrategy', 'plotly': {}}
        }
        strategy = ChordStrategy(config)

        assert strategy.mode == 'aggregation'
        assert strategy.source_column == 'source'
        assert strategy.target_column == 'target'
        assert strategy.min_link_value == 1


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises ValueError."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_aggregation_mode_missing_source(self):
        """Test aggregation mode with missing source column."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)
        df = pd.DataFrame({'compoundclass': ['Class1']})

        with pytest.raises(ValueError, match="Missing columns"):
            strategy.validate_data(df)

    def test_validate_pairwise_mode_requires_config(self):
        """Test pairwise mode requires group_by and shared columns."""
        config = get_aggregation_config()
        config['visualization']['plotly']['mode'] = 'pairwise'
        strategy = ChordStrategy(config)
        df = pd.DataFrame({'sample': ['S1']})

        with pytest.raises(
            ValueError,
            match="Pairwise mode requires.*group_by_column.*shared_column"
        ):
            strategy.validate_data(df)

    def test_validate_set_intersection_mode_requires_config(self):
        """Test set_intersection mode requires config."""
        config = get_aggregation_config()
        config['visualization']['plotly']['mode'] = 'set_intersection'
        strategy = ChordStrategy(config)
        df = pd.DataFrame({'sample': ['S1']})

        with pytest.raises(
            ValueError,
            match="Set intersection mode requires.*set_column.*element_column"
        ):
            strategy.validate_data(df)

    def test_validate_unknown_mode_fails(self):
        """Test unknown mode raises ValueError."""
        config = get_aggregation_config()
        config['visualization']['plotly']['mode'] = 'invalid_mode'
        strategy = ChordStrategy(config)
        df = pd.DataFrame({'sample': ['S1']})

        with pytest.raises(ValueError, match="Unknown mode"):
            strategy.validate_data(df)


# ============================================================================
# AGGREGATION MODE TESTS
# ============================================================================

class TestAggregationMode:
    """Test _process_aggregation() method."""

    def test_process_aggregation_counts_interactions(self):
        """Test aggregation counts source-target interactions."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2'],
            'compoundclass': ['Class1', 'Class2', 'Class1', 'Class1']
        })

        result = strategy._process_aggregation(df)

        assert len(result) == 3  # 3 unique combinations
        assert list(result.columns) == ['source', 'target', 'value']
        assert result['value'].sum() == 4  # Total interactions

    def test_process_aggregation_with_value_column(self):
        """Test aggregation with pre-aggregated values."""
        config = get_aggregation_config()
        config['visualization']['plotly']['value_column'] = 'count'
        strategy = ChordStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'compoundclass': ['Class1', 'Class1'],
            'count': [5, 10]
        })

        result = strategy._process_aggregation(df)

        assert result['value'].sum() == 15


# ============================================================================
# PAIRWISE MODE TESTS
# ============================================================================

class TestPairwiseMode:
    """Test _process_pairwise() method."""

    def test_process_pairwise_computes_shared_entities(self):
        """Test pairwise mode computes shared entities."""
        config = get_pairwise_config()
        strategy = ChordStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2', 'S3'],
            'compoundname': ['C1', 'C2', 'C1', 'C3', 'C4']
        })

        result = strategy._process_pairwise(df)

        # S1 and S2 share C1
        assert len(result) == 1
        s1_s2 = result[
            (result['source'] == 'S1') & (result['target'] == 'S2')
        ]
        assert s1_s2['value'].values[0] == 1

    def test_process_pairwise_no_shared_entities(self):
        """Test pairwise with no shared entities."""
        config = get_pairwise_config()
        strategy = ChordStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'compoundname': ['C1', 'C2']
        })

        result = strategy._process_pairwise(df)

        assert len(result) == 0


# ============================================================================
# SET INTERSECTION MODE TESTS
# ============================================================================

class TestSetIntersectionMode:
    """Test _process_set_intersection() method."""

    def test_process_set_intersection_computes_overlaps(self):
        """Test set_intersection computes overlaps."""
        config = get_set_intersection_config()
        strategy = ChordStrategy(config)

        df = pd.DataFrame({
            'risk_category': ['High', 'High', 'Medium', 'Medium'],
            'compound': ['C1', 'C2', 'C1', 'C3']
        })

        result = strategy._process_set_intersection(df)

        # High and Medium share C1
        assert len(result) == 1
        assert result['value'].values[0] == 1


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete workflow."""

    def test_process_data_aggregation_mode(self):
        """Test complete process_data in aggregation mode."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2'],
            'compoundclass': ['Class1', 'Class2', 'Class1']
        })

        result = strategy.process_data(df)

        assert 'source' in result.columns
        assert 'target' in result.columns
        assert 'value' in result.columns
        assert len(result) > 0

    def test_process_data_filters_min_link_value(self):
        """Test that min_link_value filters weak links."""
        config = get_aggregation_config()
        config['visualization']['plotly']['min_link_value'] = 2
        strategy = ChordStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2'],
            'compoundclass': ['Class1', 'Class1', 'Class2']
        })

        result = strategy.process_data(df)

        # Only S1-Class1 with count=2 survives
        assert len(result) == 1
        assert result['value'].values[0] == 2

    def test_create_figure_returns_figure(self):
        """Test that create_figure returns a Plotly Figure."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)

        links = pd.DataFrame({
            'source': ['S1', 'S2'],
            'target': ['Class1', 'Class1'],
            'value': [5, 3]
        })

        fig = strategy.create_figure(links)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) > 0  # Has traces

    def test_generate_plot_complete_workflow(self):
        """Test complete generate_plot workflow."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2'],
            'compoundclass': ['Class1', 'Class2', 'Class1', 'Class2']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)


# ============================================================================
# HELPER METHOD TESTS
# ============================================================================

class TestHelperMethods:
    """Test helper methods."""

    def test_count_connections(self):
        """Test _count_connections method."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)

        links = pd.DataFrame({
            'source': ['S1', 'S2'],
            'target': ['Class1', 'S1'],
            'value': [5, 3]
        })

        # S1 appears as source (5) and target (3)
        count = strategy._count_connections('S1', links)
        assert count == 8

    def test_get_color_palette(self):
        """Test _get_color_palette method."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)

        colors = strategy._get_color_palette(5)

        assert len(colors) == 5
        assert all(isinstance(c, str) for c in colors)

    def test_calculate_arc_spans_proportional(self):
        """Test _calculate_arc_spans with proportional mode."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)
        strategy.circle_arc_proportional = True

        arc_spans = strategy._calculate_arc_spans(
            n_nodes=3,
            node_values=[10, 20, 10],
            total_value=40
        )

        assert len(arc_spans) == 3
        # Each span is (start, end) tuple
        assert all(isinstance(span, tuple) for span in arc_spans)

    def test_calculate_arc_spans_equal(self):
        """Test _calculate_arc_spans with equal spacing."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)
        strategy.circle_arc_proportional = False

        arc_spans = strategy._calculate_arc_spans(
            n_nodes=3,
            node_values=[10, 20, 10],
            total_value=40
        )

        assert len(arc_spans) == 3
        # All spans should be roughly equal
        span_sizes = [end - start for start, end in arc_spans]
        assert abs(span_sizes[0] - span_sizes[1]) < 0.1


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_process_data_empty_after_filtering(self):
        """Test that empty result after filtering raises error."""
        config = get_aggregation_config()
        config['visualization']['plotly']['min_link_value'] = 100
        strategy = ChordStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'compoundclass': ['Class1']
        })

        with pytest.raises(ValueError, match="No valid links"):
            strategy.process_data(df)

    def test_single_node(self):
        """Test with single node."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)

        links = pd.DataFrame({
            'source': ['S1'],
            'target': ['S1'],
            'value': [1]
        })

        fig = strategy.create_figure(links)
        assert isinstance(fig, go.Figure)

    def test_large_number_of_nodes(self):
        """Test with many nodes."""
        config = get_aggregation_config()
        strategy = ChordStrategy(config)

        links = pd.DataFrame({
            'source': [f'S{i}' for i in range(20)],
            'target': [f'T{i}' for i in range(20)],
            'value': [1] * 20
        })

        fig = strategy.create_figure(links)
        assert isinstance(fig, go.Figure)

    def test_layout_with_autosize(self):
        """Test layout with autosize enabled."""
        config = get_aggregation_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = ChordStrategy(config)

        links = pd.DataFrame({
            'source': ['S1'],
            'target': ['T1'],
            'value': [1]
        })

        fig = strategy.create_figure(links)
        assert isinstance(fig, go.Figure)
