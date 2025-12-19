"""
Unit Tests for SankeyStrategy.

This module tests the SankeyStrategy class, which creates Sankey (alluvial)
diagrams for visualizing flow relationships between categorical levels.

Test Categories:
- Initialization: Test strategy creation and configuration
- Data Validation: Test validate_data() method
- Data Processing: Test process_data() and cleaning steps
- Node Building: Test _build_nodes() method
- Link Building: Test _build_links() method
- Figure Creation: Test create_figure() method
- Integration: Test complete workflow
- Edge Cases: Test boundary conditions
- Statistics: Test get_stage_statistics() helper
"""

import pytest
import pandas as pd
import plotly.graph_objects as go

from src.domain.plot_strategies.charts.sankey_strategy import (
    SankeyStrategy,
    DEFAULT_NODE_COLORS
)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_minimal_config():
    """Get minimal configuration for Sankey diagram."""
    return {
        'metadata': {'use_case_id': 'UC-6.1'},
        'visualization': {
            'strategy': 'SankeyStrategy',
            'plotly': {
                'flow_columns': ['stage1', 'stage2', 'stage3'],
                'aggregation': 'count'
            }
        }
    }


def get_full_config():
    """Get full configuration for Sankey diagram."""
    return {
        'metadata': {'use_case_id': 'UC-6.1'},
        'data': {
            'required_columns': ['referenceAG', 'sample', 'genesymbol', 'compoundname']
        },
        'visualization': {
            'strategy': 'SankeyStrategy',
            'plotly': {
                'flow_columns': ['referenceAG', 'sample', 'genesymbol', 'compoundname'],
                'value_column': None,
                'aggregation': 'count',
                'node_pad': 15,
                'node_thickness': 20,
                'color_by_stage': True,
                'color_by_first_level': False,
                'link_opacity': 0.5,
                'link_color': 'rgba(180, 180, 180, 0.5)',
                'chart': {
                    'title': {
                        'text': 'Agency → Sample → Gene → Compound Flow',
                        'font': {'size': 16}
                    }
                },
                'layout': {
                    'height': 900,
                    'width': 1400,
                    'autosize': False,
                    'template': 'simple_white',
                    'font_size': 10
                }
            }
        }
    }


def get_value_aggregation_config():
    """Get configuration with value aggregation."""
    return {
        'metadata': {'use_case_id': 'UC-6.2'},
        'visualization': {
            'strategy': 'SankeyStrategy',
            'plotly': {
                'flow_columns': ['stage1', 'stage2'],
                'value_column': 'count',
                'aggregation': 'sum'
            }
        }
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestSankeyStrategyInitialization:
    """Test SankeyStrategy initialization."""

    def test_initialization_minimal_config(self):
        """Test initialization with minimal configuration."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        assert strategy.flow_columns == ['stage1', 'stage2', 'stage3']
        assert strategy.aggregation == 'count'
        assert strategy.value_column is None

    def test_initialization_full_config(self):
        """Test initialization with full configuration."""
        config = get_full_config()
        strategy = SankeyStrategy(config)

        assert len(strategy.flow_columns) == 4
        assert strategy.node_pad == 15
        assert strategy.node_thickness == 20
        assert strategy.color_by_stage is True
        assert strategy.link_opacity == 0.5

    def test_initialization_default_values(self):
        """Test that default values are set correctly."""
        config = {
            'metadata': {},
            'visualization': {
                'strategy': 'SankeyStrategy',
                'plotly': {
                    'flow_columns': ['A', 'B']
                }
            }
        }
        strategy = SankeyStrategy(config)

        assert strategy.aggregation == 'count'
        assert strategy.node_pad == 15
        assert strategy.node_thickness == 20
        assert strategy.color_by_stage is True
        assert strategy.link_opacity == 0.5

    def test_initialization_custom_colors(self):
        """Test initialization with custom node colors."""
        config = get_minimal_config()
        custom_colors = ['red', 'blue', 'green']
        config['visualization']['plotly']['node_colors'] = custom_colors
        strategy = SankeyStrategy(config)

        assert strategy.node_colors == custom_colors

    def test_initialization_extracts_configs(self):
        """Test that initialization extracts configs correctly."""
        config = get_full_config()
        strategy = SankeyStrategy(config)

        assert strategy.data_config is not None
        assert strategy.plotly_config is not None
        assert 'flow_columns' in strategy.plotly_config


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises ValueError."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="Input DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_no_flow_columns_fails(self):
        """Test that missing flow_columns config raises ValueError."""
        config = get_minimal_config()
        config['visualization']['plotly']['flow_columns'] = []
        strategy = SankeyStrategy(config)
        df = pd.DataFrame({'A': [1, 2]})

        with pytest.raises(ValueError, match="No flow_columns specified"):
            strategy.validate_data(df)

    def test_validate_single_flow_column_fails(self):
        """Test that single flow column raises ValueError."""
        config = get_minimal_config()
        config['visualization']['plotly']['flow_columns'] = ['stage1']
        strategy = SankeyStrategy(config)
        df = pd.DataFrame({'stage1': ['A', 'B']})

        with pytest.raises(ValueError, match="At least 2 flow columns required"):
            strategy.validate_data(df)

    def test_validate_missing_flow_columns(self):
        """Test missing flow columns raises ValueError."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)
        df = pd.DataFrame({'stage1': ['A'], 'other': ['B']})

        with pytest.raises(ValueError, match="Missing flow columns"):
            strategy.validate_data(df)

    def test_validate_missing_value_column(self):
        """Test missing value column raises ValueError."""
        config = get_value_aggregation_config()
        strategy = SankeyStrategy(config)
        df = pd.DataFrame({
            'stage1': ['A'],
            'stage2': ['B']
        })

        with pytest.raises(ValueError, match="Value column .* not found"):
            strategy.validate_data(df)

    def test_validate_success(self):
        """Test successful validation."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)
        df = pd.DataFrame({
            'stage1': ['A', 'B'],
            'stage2': ['C', 'D'],
            'stage3': ['E', 'F']
        })

        # Should not raise
        strategy.validate_data(df)

    def test_validate_with_value_column_success(self):
        """Test successful validation with value column."""
        config = get_value_aggregation_config()
        strategy = SankeyStrategy(config)
        df = pd.DataFrame({
            'stage1': ['A', 'B'],
            'stage2': ['C', 'D'],
            'count': [10, 20]
        })

        # Should not raise
        strategy.validate_data(df)


# ============================================================================
# DATA PROCESSING TESTS
# ============================================================================

class TestDataProcessing:
    """Test process_data() method."""

    def test_process_data_count_aggregation(self):
        """Test process_data with count aggregation."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'A', 'B', 'B'],
            'stage2': ['C', 'C', 'D', 'D'],
            'stage3': ['E', 'E', 'F', 'F']
        })

        result = strategy.process_data(df)

        assert 'value' in result.columns
        assert len(result) == 2  # A->C->E (count 2), B->D->F (count 2)
        assert result['value'].sum() == 4

    def test_process_data_removes_nulls(self):
        """Test that null values are removed."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'B', None],
            'stage2': ['C', None, 'E'],
            'stage3': ['F', 'G', 'H']
        })

        result = strategy.process_data(df)

        # Only first row (A->C->F) is valid
        assert len(result) == 1
        assert result.iloc[0]['stage1'] == 'A'

    def test_process_data_strips_whitespace(self):
        """Test that whitespace is stripped."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['  A  ', 'B'],
            'stage2': ['C  ', '  D'],
            'stage3': ['E', 'F']
        })

        result = strategy.process_data(df)

        assert result.iloc[0]['stage1'] == 'A'
        assert result.iloc[0]['stage2'] == 'C'

    def test_process_data_removes_placeholders(self):
        """Test that placeholder values are removed."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', '#N/D', 'B', 'N/D'],
            'stage2': ['C', 'D', '#N/A', 'F'],
            'stage3': ['G', 'H', 'I', 'J']
        })

        result = strategy.process_data(df)

        # Only first row (A->C->G) is valid
        assert len(result) == 1
        assert result.iloc[0]['stage1'] == 'A'

    def test_process_data_sum_aggregation(self):
        """Test process_data with sum aggregation."""
        config = get_value_aggregation_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'A', 'B'],
            'stage2': ['C', 'C', 'D'],
            'count': [10, 20, 30]
        })

        result = strategy.process_data(df)

        # A->C should have value=30 (10+20)
        a_to_c = result[(result['stage1'] == 'A') & (result['stage2'] == 'C')]
        assert a_to_c['value'].values[0] == 30

        # B->D should have value=30
        b_to_d = result[(result['stage1'] == 'B') & (result['stage2'] == 'D')]
        assert b_to_d['value'].values[0] == 30

    def test_process_data_nunique_aggregation(self):
        """Test process_data with nunique aggregation."""
        config = get_value_aggregation_config()
        config['visualization']['plotly']['aggregation'] = 'nunique'
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'A', 'A'],
            'stage2': ['C', 'C', 'C'],
            'count': ['X', 'Y', 'X']  # 2 unique values
        })

        result = strategy.process_data(df)

        # Should count 2 unique values
        assert result['value'].values[0] == 2

    def test_process_data_empty_after_cleaning_fails(self):
        """Test that empty data after cleaning raises ValueError."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['#N/D', None],
            'stage2': ['#N/A', None],
            'stage3': ['N/D', None]
        })

        with pytest.raises(ValueError, match="No valid data remaining"):
            strategy.process_data(df)


# ============================================================================
# NODE BUILDING TESTS
# ============================================================================

class TestNodeBuilding:
    """Test _build_nodes() method."""

    def test_build_nodes_collects_unique_labels(self):
        """Test that build_nodes collects unique labels from all stages."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'B'],
            'stage2': ['C', 'D'],
            'stage3': ['E', 'F'],
            'value': [1, 1]
        })

        all_labels, label_to_id, node_colors = strategy._build_nodes(df)

        assert len(all_labels) == 6  # A, B, C, D, E, F
        assert set(all_labels) == {'A', 'B', 'C', 'D', 'E', 'F'}

    def test_build_nodes_creates_label_mapping(self):
        """Test that build_nodes creates correct label to ID mapping."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'B'],
            'stage2': ['C', 'D'],
            'stage3': ['E', 'F'],
            'value': [1, 1]
        })

        all_labels, label_to_id, node_colors = strategy._build_nodes(df)

        # Each label should have a unique ID
        assert len(label_to_id) == len(all_labels)
        assert all(isinstance(id, int) for id in label_to_id.values())

    def test_build_nodes_assigns_colors_by_stage(self):
        """Test that build_nodes assigns colors based on stage."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'B'],
            'stage2': ['C', 'D'],
            'stage3': ['E', 'F'],
            'value': [1, 1]
        })

        all_labels, label_to_id, node_colors = strategy._build_nodes(df)

        # Should have colors for all nodes
        assert len(node_colors) == len(all_labels)
        # Colors should be from node_colors palette
        assert all(color in strategy.node_colors for color in node_colors)

    def test_build_nodes_handles_shared_values(self):
        """Test build_nodes with values appearing in multiple stages."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        # 'X' appears in both stage1 and stage2
        df = pd.DataFrame({
            'stage1': ['X', 'A'],
            'stage2': ['X', 'B'],
            'stage3': ['C', 'D'],
            'value': [1, 1]
        })

        all_labels, label_to_id, node_colors = strategy._build_nodes(df)

        # 'X' should appear only once (first occurrence in stage1)
        assert all_labels.count('X') == 1


# ============================================================================
# LINK BUILDING TESTS
# ============================================================================

class TestLinkBuilding:
    """Test _build_links() method."""

    def test_build_links_creates_stage_transitions(self):
        """Test that build_links creates links between adjacent stages."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'B'],
            'stage2': ['C', 'D'],
            'stage3': ['E', 'F'],
            'value': [10, 20]
        })

        all_labels, label_to_id, _ = strategy._build_nodes(df)
        sources, targets, values, link_colors = strategy._build_links(
            df, label_to_id, all_labels
        )

        # Should have 4 links: A->C, C->E, B->D, D->F
        assert len(sources) == 4
        assert len(targets) == 4
        assert len(values) == 4

    def test_build_links_aggregates_duplicate_pairs(self):
        """Test that build_links aggregates duplicate source->target pairs."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'A', 'A'],
            'stage2': ['C', 'C', 'D'],
            'stage3': ['E', 'E', 'F'],
            'value': [10, 20, 30]
        })

        all_labels, label_to_id, _ = strategy._build_nodes(df)
        sources, targets, values, link_colors = strategy._build_links(
            df, label_to_id, all_labels
        )

        # A->C appears twice (aggregated)
        # Find A->C link
        a_id = label_to_id['A']
        c_id = label_to_id['C']
        a_to_c_indices = [i for i, (s, t) in enumerate(zip(sources, targets))
                          if s == a_id and t == c_id]

        assert len(a_to_c_indices) == 1  # Should be aggregated
        assert values[a_to_c_indices[0]] == 30  # 10 + 20

    def test_build_links_uses_default_link_color(self):
        """Test that build_links uses default link color."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A'],
            'stage2': ['B'],
            'stage3': ['C'],
            'value': [1]
        })

        all_labels, label_to_id, _ = strategy._build_nodes(df)
        sources, targets, values, link_colors = strategy._build_links(
            df, label_to_id, all_labels
        )

        # Should use default link color
        assert all(color == strategy.link_color for color in link_colors)

    def test_build_links_color_by_first_level(self):
        """Test build_links with color_by_first_level enabled."""
        config = get_minimal_config()
        config['visualization']['plotly']['color_by_first_level'] = True
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'B'],
            'stage2': ['C', 'D'],
            'stage3': ['E', 'F'],
            'value': [1, 1]
        })

        all_labels, label_to_id, _ = strategy._build_nodes(df)
        sources, targets, values, link_colors = strategy._build_links(
            df, label_to_id, all_labels
        )

        # First stage links should have custom colors
        # Later stages should use default
        assert len(link_colors) == 4
        assert any('0.5)' in color for color in link_colors)  # Custom opacity


# ============================================================================
# FIGURE CREATION TESTS
# ============================================================================

class TestFigureCreation:
    """Test create_figure() method."""

    def test_create_figure_returns_figure(self):
        """Test that create_figure returns a Plotly Figure."""
        config = get_full_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA', 'FDA'],
            'sample': ['S1', 'S2'],
            'genesymbol': ['G1', 'G2'],
            'compoundname': ['C1', 'C2'],
            'value': [10, 20]
        })

        fig = strategy.create_figure(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'sankey'

    def test_create_figure_has_nodes_and_links(self):
        """Test that created figure has nodes and links."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'B'],
            'stage2': ['C', 'D'],
            'stage3': ['E', 'F'],
            'value': [1, 1]
        })

        fig = strategy.create_figure(df)

        sankey_trace = fig.data[0]
        assert sankey_trace.node is not None
        assert sankey_trace.link is not None
        assert len(sankey_trace.node.label) > 0
        assert len(sankey_trace.link.source) > 0

    def test_create_figure_applies_title(self):
        """Test that figure applies title from config."""
        config = get_full_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA'],
            'sample': ['S1'],
            'genesymbol': ['G1'],
            'compoundname': ['C1'],
            'value': [1]
        })

        fig = strategy.create_figure(df)

        assert fig.layout.title.text == 'Agency → Sample → Gene → Compound Flow'

    def test_create_figure_title_hidden(self):
        """Test figure with title disabled."""
        config = get_full_config()
        config['visualization']['plotly']['chart']['title'] = {
            'show': False,
            'text': 'Should not appear'
        }
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA'],
            'sample': ['S1'],
            'genesymbol': ['G1'],
            'compoundname': ['C1'],
            'value': [1]
        })

        fig = strategy.create_figure(df)

        # Title should be empty or None when disabled
        assert fig.layout.title.text == '' or fig.layout.title.text is None

    def test_create_figure_applies_layout_config(self):
        """Test that layout configuration is applied."""
        config = get_full_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA'],
            'sample': ['S1'],
            'genesymbol': ['G1'],
            'compoundname': ['C1'],
            'value': [1]
        })

        fig = strategy.create_figure(df)

        assert fig.layout.height == 900
        assert fig.layout.width == 1400
        assert fig.layout.font.size == 10

    def test_create_figure_with_autosize(self):
        """Test figure with autosize enabled."""
        config = get_full_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA'],
            'sample': ['S1'],
            'genesymbol': ['G1'],
            'compoundname': ['C1'],
            'value': [1]
        })

        fig = strategy.create_figure(df)

        assert fig.layout.autosize is True

    def test_create_figure_node_configuration(self):
        """Test that node configuration is applied."""
        config = get_full_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA'],
            'sample': ['S1'],
            'genesymbol': ['G1'],
            'compoundname': ['C1'],
            'value': [1]
        })

        fig = strategy.create_figure(df)

        sankey_trace = fig.data[0]
        assert sankey_trace.node.pad == 15
        assert sankey_trace.node.thickness == 20


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete workflow."""

    def test_generate_plot_complete_workflow(self):
        """Test complete generate_plot workflow."""
        config = get_full_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'referenceAG': ['EPA', 'EPA', 'FDA', 'FDA'],
            'sample': ['S1', 'S2', 'S1', 'S2'],
            'genesymbol': ['G1', 'G2', 'G1', 'G3'],
            'compoundname': ['C1', 'C2', 'C1', 'C3']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'sankey'

    def test_generate_with_validation(self):
        """Test generate workflow with explicit validation."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'B', 'C'],
            'stage2': ['D', 'E', 'F'],
            'stage3': ['G', 'H', 'I']
        })

        strategy.validate_data(df)
        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        assert 'value' in processed.columns

    def test_generate_with_value_aggregation(self):
        """Test complete workflow with value aggregation."""
        config = get_value_aggregation_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'A', 'B'],
            'stage2': ['C', 'C', 'D'],
            'count': [10, 20, 30]
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        # Verify aggregation occurred
        sankey_trace = fig.data[0]
        assert sum(sankey_trace.link.value) == 60  # 30 + 30


# ============================================================================
# STATISTICS TESTS
# ============================================================================

class TestStatistics:
    """Test get_stage_statistics() helper method."""

    def test_get_stage_statistics(self):
        """Test stage statistics calculation."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'A', 'B', 'B', 'B'],
            'stage2': ['C', 'D', 'D', 'E', 'E'],
            'stage3': ['F', 'F', 'F', 'G', 'G'],
            'value': [1, 1, 1, 1, 1]
        })

        stats = strategy.get_stage_statistics(df)

        assert 'stage1' in stats
        assert 'stage2' in stats
        assert 'stage3' in stats

        # stage1 has 2 unique values (A, B)
        assert stats['stage1']['unique_count'] == 2

        # stage2 has 3 unique values (C, D, E)
        assert stats['stage2']['unique_count'] == 3

    def test_get_stage_statistics_top_values(self):
        """Test that statistics include top values."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A'] * 10 + ['B'] * 5 + ['C'] * 2,
            'stage2': ['D'] * 17,
            'stage3': ['E'] * 17,
            'value': [1] * 17
        })

        stats = strategy.get_stage_statistics(df)

        # Top values should be ordered by frequency
        top_stage1 = stats['stage1']['top_values']
        assert 'A' in top_stage1
        assert top_stage1['A'] == 10


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_path(self):
        """Test with single path through all stages."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A'],
            'stage2': ['B'],
            'stage3': ['C'],
            'value': [1]
        })

        fig = strategy.create_figure(df)

        assert isinstance(fig, go.Figure)
        sankey_trace = fig.data[0]
        assert len(sankey_trace.node.label) == 3  # A, B, C
        assert len(sankey_trace.link.source) == 2  # A->B, B->C

    def test_many_stages(self):
        """Test with many flow stages."""
        config = get_minimal_config()
        config['visualization']['plotly']['flow_columns'] = [
            'stage1', 'stage2', 'stage3', 'stage4', 'stage5'
        ]
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A'] * 5,
            'stage2': ['B'] * 5,
            'stage3': ['C'] * 5,
            'stage4': ['D'] * 5,
            'stage5': ['E'] * 5
        })

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        sankey_trace = fig.data[0]
        # 5 stages = 4 links (between adjacent stages)
        assert len(sankey_trace.link.source) >= 4

    def test_large_flow(self):
        """Test with large number of nodes and links."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        # Create diverse data
        df = pd.DataFrame({
            'stage1': [f'A{i}' for i in range(20)],
            'stage2': [f'B{i}' for i in range(20)],
            'stage3': [f'C{i}' for i in range(20)]
        })

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        sankey_trace = fig.data[0]
        assert len(sankey_trace.node.label) == 60  # 20 per stage

    def test_minimal_flow_two_stages(self):
        """Test with minimal two-stage flow."""
        config = {
            'metadata': {},
            'visualization': {
                'strategy': 'SankeyStrategy',
                'plotly': {
                    'flow_columns': ['A', 'B']
                }
            }
        }
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'A': ['X', 'Y'],
            'B': ['Z', 'W']
        })

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        sankey_trace = fig.data[0]
        assert len(sankey_trace.link.source) == 2  # X->Z, Y->W

    def test_convergent_flow(self):
        """Test flow where multiple sources converge to same target."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'B', 'C'],
            'stage2': ['D', 'D', 'D'],  # All converge to D
            'stage3': ['E', 'E', 'E']   # All continue to E
        })

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        sankey_trace = fig.data[0]
        # Should have 3 links to D: A->D, B->D, C->D
        # And 1 link from D: D->E
        assert len(sankey_trace.link.source) == 4

    def test_divergent_flow(self):
        """Test flow where single source diverges to multiple targets."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'A', 'A'],
            'stage2': ['B', 'C', 'D'],  # A diverges to B, C, D
            'stage3': ['E', 'F', 'G']
        })

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        sankey_trace = fig.data[0]
        # Should have links: A->B, A->C, A->D, B->E, C->F, D->G
        assert len(sankey_trace.link.source) == 6

    def test_all_same_values(self):
        """Test with all identical flow paths."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A'] * 100,
            'stage2': ['B'] * 100,
            'stage3': ['C'] * 100
        })

        processed = strategy.process_data(df)

        # Should aggregate to single path with count=100
        assert len(processed) == 1
        assert processed['value'].values[0] == 100

    def test_empty_strings_filtered(self):
        """Test that empty strings are filtered out."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', '', 'B'],
            'stage2': ['C', 'D', ''],
            'stage3': ['E', 'F', 'G']
        })

        processed = strategy.process_data(df)

        # Empty strings should be filtered
        assert '' not in processed['stage1'].values
        assert '' not in processed['stage2'].values

    def test_string_nan_filtered(self):
        """Test that string 'nan' is filtered out."""
        config = get_minimal_config()
        strategy = SankeyStrategy(config)

        df = pd.DataFrame({
            'stage1': ['A', 'nan', 'B'],
            'stage2': ['C', 'D', 'None'],
            'stage3': ['E', 'F', 'G']
        })

        processed = strategy.process_data(df)

        # String 'nan' and 'None' should be filtered
        assert 'nan' not in processed['stage1'].values
        assert 'None' not in processed['stage2'].values
