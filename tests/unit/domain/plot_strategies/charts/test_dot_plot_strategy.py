"""
Unit Tests for DotPlotStrategy.

This module tests the DotPlotStrategy class, which creates scatter plots
and bubble charts for visualizing categorical and quantitative data.

Test Categories:
- Initialization: Test strategy creation and configuration
- Data Validation: Test validate_data() method
- Data Processing: Test process_data() and processing steps
- Figure Creation - Simple Scatter: Test _create_simple_scatter()
- Figure Creation - Bubble Chart: Test _create_bubble_chart()
- Layout Application: Test _apply_layout()
- Integration: Test complete workflow
- Edge Cases: Test boundary conditions
"""

import pytest
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from src.domain.plot_strategies.charts.dot_plot_strategy import DotPlotStrategy


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_simple_scatter_config():
    """Get configuration for simple scatter plot."""
    return {
        'metadata': {'use_case_id': 'UC-4.1'},
        'data': {
            'required_columns': ['sample', 'genesymbol'],
        },
        'visualization': {
            'strategy': 'DotPlotStrategy',
            'plotly': {
                'scatter': {
                    'x': 'sample',
                    'y': 'genesymbol',
                    'mode': 'simple',
                    'marker': {
                        'color': 'mediumseagreen',
                        'size': 10
                    }
                },
                'layout': {
                    'title': {'text': 'Gene Symbols by Sample'},
                    'height': 600,
                    'width': 800
                }
            }
        }
    }


def get_bubble_chart_config():
    """Get configuration for bubble chart."""
    return {
        'metadata': {'use_case_id': 'UC-4.2'},
        'data': {
            'required_columns': ['sample', 'compoundname', 'ko'],
            'processing': {
                'steps': [
                    {
                        'name': 'group_and_count',
                        'enabled': True,
                        'params': {
                            'group_by': ['sample', 'compoundname'],
                            'agg_column': 'ko',
                            'agg_function': 'nunique',
                            'result_column': 'unique_ko_count'
                        }
                    }
                ]
            }
        },
        'visualization': {
            'strategy': 'DotPlotStrategy',
            'plotly': {
                'scatter': {
                    'x': 'sample',
                    'y': 'compoundname',
                    'size': 'unique_ko_count',
                    'color': 'unique_ko_count',
                    'mode': 'bubble',
                    'size_max': 30,
                    'color_continuous_scale': 'Viridis'
                },
                'layout': {'height': 600}
            }
        }
    }


def get_filter_config():
    """Get configuration with filter processing step."""
    return {
        'metadata': {'use_case_id': 'UC-4.3'},
        'data': {
            'required_columns': ['sample', 'enzyme_activity', 'genesymbol'],
            'processing': {
                'steps': [
                    {
                        'name': 'filter',
                        'enabled': True,
                        'params': {
                            'column': 'enzyme_activity',
                            'operator': '!=',
                            'value': '#N/D'
                        }
                    }
                ]
            }
        },
        'visualization': {
            'strategy': 'DotPlotStrategy',
            'plotly': {
                'scatter': {
                    'x': 'sample',
                    'y': 'genesymbol',
                    'mode': 'simple'
                }
            }
        }
    }


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestDotPlotStrategyInitialization:
    """Test DotPlotStrategy initialization."""

    def test_initialization_simple_mode(self):
        """Test initialization with simple scatter mode."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        assert strategy.plotly_config is not None
        assert strategy.data_config is not None
        scatter_config = strategy.plotly_config.get('scatter', {})
        assert scatter_config.get('mode') == 'simple'

    def test_initialization_bubble_mode(self):
        """Test initialization with bubble chart mode."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        scatter_config = strategy.plotly_config.get('scatter', {})
        assert scatter_config.get('mode') == 'bubble'
        assert scatter_config.get('size') == 'unique_ko_count'
        assert scatter_config.get('color') == 'unique_ko_count'

    def test_initialization_with_processing_steps(self):
        """Test initialization with processing steps."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        steps = strategy.data_config.get('processing', {}).get('steps', [])
        assert len(steps) > 0
        assert steps[0]['name'] == 'group_and_count'

    def test_initialization_extracts_configs(self):
        """Test that initialization extracts configs correctly."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        assert 'scatter' in strategy.plotly_config
        assert 'layout' in strategy.plotly_config
        assert 'required_columns' in strategy.data_config


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises ValueError."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_required_columns(self):
        """Test missing required columns raises ValueError."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)
        df = pd.DataFrame({'sample': ['S1']})

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_missing_x_column(self):
        """Test missing x column raises ValueError."""
        config = get_simple_scatter_config()
        config['visualization']['plotly']['scatter']['x'] = 'missing_col'
        strategy = DotPlotStrategy(config)
        df = pd.DataFrame({'sample': ['S1'], 'genesymbol': ['G1']})

        with pytest.raises(ValueError, match="X column .* not found"):
            strategy.validate_data(df)

    def test_validate_missing_y_column(self):
        """Test missing y column raises ValueError."""
        config = get_simple_scatter_config()
        config['visualization']['plotly']['scatter']['y'] = 'missing_col'
        strategy = DotPlotStrategy(config)
        df = pd.DataFrame({'sample': ['S1'], 'genesymbol': ['G1']})

        with pytest.raises(ValueError, match="Y column .* not found"):
            strategy.validate_data(df)

    def test_validate_missing_scatter_config(self):
        """Test missing scatter config raises ValueError."""
        config = get_simple_scatter_config()
        del config['visualization']['plotly']['scatter']['x']
        strategy = DotPlotStrategy(config)
        df = pd.DataFrame({'sample': ['S1'], 'genesymbol': ['G1']})

        with pytest.raises(ValueError, match="must specify 'x' and 'y'"):
            strategy.validate_data(df)

    def test_validate_bubble_mode_with_processing_step(self):
        """Test bubble mode validation allows column created by processing."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        # DataFrame doesn't have unique_ko_count yet
        df = pd.DataFrame({
            'sample': ['S1', 'S1'],
            'compoundname': ['C1', 'C2'],
            'ko': ['K00001', 'K00002']
        })

        # Should NOT raise error because unique_ko_count is created by processing
        strategy.validate_data(df)

    def test_validate_bubble_mode_missing_size_column(self):
        """Test bubble mode with missing size column (not in processing)."""
        config = get_bubble_chart_config()
        config['visualization']['plotly']['scatter']['size'] = 'missing_size_col'
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'compoundname': ['C1'],
            'ko': ['K00001']
        })

        with pytest.raises(ValueError, match="Size column .* not found"):
            strategy.validate_data(df)

    def test_validate_success(self):
        """Test successful validation."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)
        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'genesymbol': ['G1', 'G2']
        })

        # Should not raise
        strategy.validate_data(df)


# ============================================================================
# DATA PROCESSING TESTS
# ============================================================================

class TestDataProcessing:
    """Test process_data() method and processing steps."""

    def test_process_data_no_steps(self):
        """Test process_data with no processing steps."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'genesymbol': ['G1', 'G2']
        })

        result = strategy.process_data(df)

        assert len(result) == 2
        pd.testing.assert_frame_equal(result, df)

    def test_process_data_filter_step(self):
        """Test filter processing step."""
        config = get_filter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2'],
            'genesymbol': ['G1', 'G2', 'G3'],
            'enzyme_activity': ['Active', '#N/D', 'Active']
        })

        result = strategy.process_data(df)

        # Should filter out #N/D row
        assert len(result) == 2
        assert '#N/D' not in result['enzyme_activity'].values

    def test_process_data_grouping_step_nunique(self):
        """Test group_and_count with nunique aggregation."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S1', 'S2', 'S2'],
            'compoundname': ['C1', 'C1', 'C2', 'C1', 'C1'],
            'ko': ['K00001', 'K00002', 'K00003', 'K00001', 'K00002']
        })

        result = strategy.process_data(df)

        # Should group and count unique KOs
        assert 'unique_ko_count' in result.columns
        assert len(result) == 3  # S1-C1, S1-C2, S2-C1

        # S1-C1 has 2 unique KOs
        s1_c1 = result[(result['sample'] == 'S1') &
                       (result['compoundname'] == 'C1')]
        assert s1_c1['unique_ko_count'].values[0] == 2

    def test_process_data_grouping_step_count(self):
        """Test group_and_count with count aggregation."""
        config = get_bubble_chart_config()
        config['data']['processing']['steps'][0]['params']['agg_function'] = 'count'
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S1'],
            'compoundname': ['C1', 'C1', 'C2'],
            'ko': ['K00001', 'K00002', 'K00003']
        })

        result = strategy.process_data(df)

        # S1-C1 has 2 rows
        s1_c1 = result[(result['sample'] == 'S1') &
                       (result['compoundname'] == 'C1')]
        assert s1_c1['unique_ko_count'].values[0] == 2

    def test_process_data_grouping_step_sum(self):
        """Test group_and_count with sum aggregation."""
        config = get_bubble_chart_config()
        config['data']['processing']['steps'][0]['params']['agg_function'] = 'sum'
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2'],
            'compoundname': ['C1', 'C1', 'C1'],
            'ko': [10, 20, 30]
        })

        result = strategy.process_data(df)

        # S1-C1 sum = 30
        s1_c1 = result[(result['sample'] == 'S1') &
                       (result['compoundname'] == 'C1')]
        assert s1_c1['unique_ko_count'].values[0] == 30

    def test_process_data_sort_step(self):
        """Test sort processing step."""
        config = get_simple_scatter_config()
        config['data']['processing'] = {
            'steps': [
                {
                    'name': 'sort',
                    'enabled': True,
                    'params': {
                        'by': 'genesymbol',
                        'ascending': False
                    }
                }
            ]
        }
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'genesymbol': ['G1', 'G3', 'G2']
        })

        result = strategy.process_data(df)

        # Should be sorted by genesymbol descending
        assert result['genesymbol'].tolist() == ['G3', 'G2', 'G1']

    def test_process_data_disabled_step(self):
        """Test that disabled processing steps are skipped."""
        config = get_filter_config()
        config['data']['processing']['steps'][0]['enabled'] = False
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'genesymbol': ['G1', 'G2'],
            'enzyme_activity': ['#N/D', 'Active']
        })

        result = strategy.process_data(df)

        # Filter not applied, #N/D should still be there
        assert len(result) == 2
        assert '#N/D' in result['enzyme_activity'].values

    def test_process_data_unknown_step(self):
        """Test unknown processing step is logged and skipped."""
        config = get_simple_scatter_config()
        config['data']['processing'] = {
            'steps': [
                {
                    'name': 'unknown_step',
                    'enabled': True,
                    'params': {}
                }
            ]
        }
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'genesymbol': ['G1']
        })

        result = strategy.process_data(df)

        # Should return original data
        assert len(result) == 1

    def test_apply_filter_step_all_operators(self):
        """Test all filter operators."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'genesymbol': ['G1', 'G2', 'G3'],
            'value': [10, 20, 30]
        })

        # Test ==
        result = strategy._apply_filter_step(df, {
            'column': 'value',
            'operator': '==',
            'value': 20
        })
        assert len(result) == 1
        assert result['value'].values[0] == 20

        # Test !=
        result = strategy._apply_filter_step(df, {
            'column': 'value',
            'operator': '!=',
            'value': 20
        })
        assert len(result) == 2
        assert 20 not in result['value'].values

        # Test >
        result = strategy._apply_filter_step(df, {
            'column': 'value',
            'operator': '>',
            'value': 15
        })
        assert len(result) == 2

        # Test <
        result = strategy._apply_filter_step(df, {
            'column': 'value',
            'operator': '<',
            'value': 25
        })
        assert len(result) == 2

        # Test >=
        result = strategy._apply_filter_step(df, {
            'column': 'value',
            'operator': '>=',
            'value': 20
        })
        assert len(result) == 2

        # Test <=
        result = strategy._apply_filter_step(df, {
            'column': 'value',
            'operator': '<=',
            'value': 20
        })
        assert len(result) == 2


# ============================================================================
# FIGURE CREATION - SIMPLE SCATTER TESTS
# ============================================================================

class TestSimpleScatterCreation:
    """Test _create_simple_scatter() method."""

    def test_create_simple_scatter(self):
        """Test simple scatter creation."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'genesymbol': ['G1', 'G2', 'G3']
        })

        scatter_config = strategy.plotly_config.get('scatter', {})
        fig = strategy._create_simple_scatter(df, scatter_config)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'scatter'

    def test_create_simple_scatter_marker_properties(self):
        """Test simple scatter marker properties."""
        config = get_simple_scatter_config()
        config['visualization']['plotly']['scatter']['marker'] = {
            'color': 'blue',
            'size': 15
        }
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'genesymbol': ['G1']
        })

        scatter_config = strategy.plotly_config.get('scatter', {})
        fig = strategy._create_simple_scatter(df, scatter_config)

        # Check marker properties
        assert fig.data[0].marker.color == 'blue'
        assert fig.data[0].marker.size == 15

    def test_create_simple_scatter_with_hover_data(self):
        """Test simple scatter with hover data."""
        config = get_simple_scatter_config()
        config['visualization']['plotly']['scatter']['hover_data'] = {
            'sample': True,
            'genesymbol': True
        }
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'genesymbol': ['G1', 'G2']
        })

        scatter_config = strategy.plotly_config.get('scatter', {})
        fig = strategy._create_simple_scatter(df, scatter_config)

        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].x) == 2


# ============================================================================
# FIGURE CREATION - BUBBLE CHART TESTS
# ============================================================================

class TestBubbleChartCreation:
    """Test _create_bubble_chart() method."""

    def test_create_bubble_chart(self):
        """Test bubble chart creation."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'compoundname': ['C1', 'C2', 'C3'],
            'unique_ko_count': [5, 10, 15]
        })

        scatter_config = strategy.plotly_config.get('scatter', {})
        fig = strategy._create_bubble_chart(df, scatter_config)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'scatter'

    def test_create_bubble_chart_size_encoding(self):
        """Test bubble chart size encoding."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'compoundname': ['C1', 'C2'],
            'unique_ko_count': [5, 20]
        })

        scatter_config = strategy.plotly_config.get('scatter', {})
        fig = strategy._create_bubble_chart(df, scatter_config)

        # Check that marker sizes are encoded
        assert fig.data[0].marker.size is not None

    def test_create_bubble_chart_color_encoding(self):
        """Test bubble chart color encoding."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'compoundname': ['C1', 'C2', 'C3'],
            'unique_ko_count': [5, 10, 15]
        })

        scatter_config = strategy.plotly_config.get('scatter', {})
        fig = strategy._create_bubble_chart(df, scatter_config)

        # Check color encoding
        assert fig.data[0].marker.color is not None

    def test_create_bubble_chart_colorbar_ticks(self):
        """Test bubble chart colorbar with integer ticks."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        # Small range (≤15) triggers integer ticks
        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'compoundname': ['C1', 'C2', 'C3'],
            'unique_ko_count': [1, 2, 3]
        })

        scatter_config = strategy.plotly_config.get('scatter', {})
        fig = strategy._create_bubble_chart(df, scatter_config)

        # Should have colorbar configuration
        assert 'coloraxis' in fig.layout

    def test_create_bubble_chart_no_colorbar_ticks_large_range(self):
        """Test bubble chart without integer ticks for large range."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        # Large range (>15) doesn't trigger integer ticks
        df = pd.DataFrame({
            'sample': [f'S{i}' for i in range(20)],
            'compoundname': [f'C{i}' for i in range(20)],
            'unique_ko_count': list(range(1, 21))
        })

        scatter_config = strategy.plotly_config.get('scatter', {})
        fig = strategy._create_bubble_chart(df, scatter_config)

        assert isinstance(fig, go.Figure)


# ============================================================================
# LAYOUT APPLICATION TESTS
# ============================================================================

class TestLayoutApplication:
    """Test _apply_layout() method."""

    def test_apply_layout_basic(self):
        """Test basic layout application."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._apply_layout(fig, layout_config, scatter_config)

        assert result.layout.title.text == 'Gene Symbols by Sample'
        assert result.layout.height == 600

    def test_apply_layout_title_dict_format(self):
        """Test layout with dict-formatted title."""
        config = get_simple_scatter_config()
        config['visualization']['plotly']['layout']['title'] = {
            'show': True,
            'text': 'Custom Title',
            'x': 0.3
        }
        strategy = DotPlotStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._apply_layout(fig, layout_config, scatter_config)

        assert result.layout.title.text == 'Custom Title'
        assert result.layout.title.x == 0.3

    def test_apply_layout_title_hidden(self):
        """Test layout with hidden title."""
        config = get_simple_scatter_config()
        config['visualization']['plotly']['layout']['title'] = {
            'show': False,
            'text': 'Hidden Title'
        }
        strategy = DotPlotStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._apply_layout(fig, layout_config, scatter_config)

        assert result.layout.title.text == ''

    def test_apply_layout_axis_customization(self):
        """Test layout with axis customization."""
        config = get_simple_scatter_config()
        config['visualization']['plotly']['layout']['xaxis'] = {
            'title': 'Sample ID',
            'tickangle': -90
        }
        config['visualization']['plotly']['layout']['yaxis'] = {
            'title': 'Gene Symbol',
            'tickangle': 45
        }
        strategy = DotPlotStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._apply_layout(fig, layout_config, scatter_config)

        assert result.layout.xaxis.title.text == 'Sample ID'
        assert result.layout.xaxis.tickangle == -90
        assert result.layout.yaxis.title.text == 'Gene Symbol'
        assert result.layout.yaxis.tickangle == 45

    def test_apply_layout_with_autosize(self):
        """Test layout with autosize enabled."""
        config = get_simple_scatter_config()
        config['visualization']['plotly']['layout']['autosize'] = True
        del config['visualization']['plotly']['layout']['width']
        strategy = DotPlotStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._apply_layout(fig, layout_config, scatter_config)

        assert result.layout.autosize is True

    def test_apply_layout_legend_config(self):
        """Test layout with legend configuration."""
        config = get_simple_scatter_config()
        config['visualization']['plotly']['layout']['legend'] = {
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': -0.2,
            'xanchor': 'center',
            'x': 0.5
        }
        strategy = DotPlotStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._apply_layout(fig, layout_config, scatter_config)

        assert result.layout.legend.orientation == 'h'
        assert result.layout.legend.y == -0.2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete workflow."""

    def test_generate_simple_scatter(self):
        """Test complete workflow for simple scatter."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'genesymbol': ['G1', 'G2', 'G3']
        })

        fig = strategy.generate(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 1
        assert fig.data[0].type == 'scatter'

    def test_generate_bubble_chart_with_processing(self):
        """Test complete workflow for bubble chart with processing."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S2'],
            'compoundname': ['C1', 'C1', 'C2', 'C2'],
            'ko': ['K00001', 'K00002', 'K00003', 'K00004']
        })

        # Validate, process, create
        strategy.validate_data(df)
        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        assert 'unique_ko_count' in processed.columns
        assert len(processed) == 2  # S1-C1, S2-C2

    def test_generate_plot_complete_workflow(self):
        """Test generate_plot() method (inherited from BasePlotStrategy)."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'genesymbol': ['G1', 'G2']
        })

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)

    def test_generate_with_filter_and_grouping(self):
        """Test workflow with filter and grouping steps."""
        config = get_bubble_chart_config()
        config['data']['processing']['steps'].insert(0, {
            'name': 'filter',
            'enabled': True,
            'params': {
                'column': 'sample',
                'operator': '!=',
                'value': 'S3'
            }
        })
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S2', 'S3'],
            'compoundname': ['C1', 'C1', 'C1', 'C1'],
            'ko': ['K00001', 'K00002', 'K00003', 'K00004']
        })

        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        # S3 should be filtered out
        assert 'S3' not in processed['sample'].values
        assert isinstance(fig, go.Figure)


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_generate_empty_data_fails(self):
        """Test that empty data raises ValueError."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="DataFrame is empty"):
            strategy.generate(df)

    def test_single_data_point(self):
        """Test with single data point."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'genesymbol': ['G1']
        })

        fig = strategy.generate(df)
        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].x) == 1

    def test_large_dataset(self):
        """Test with large dataset."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': [f'S{i}' for i in range(100)],
            'genesymbol': [f'G{i}' for i in range(100)]
        })

        fig = strategy.generate(df)
        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].x) == 100

    def test_filter_removes_all_data(self):
        """Test filter that removes all data."""
        config = get_filter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'genesymbol': ['G1', 'G2'],
            'enzyme_activity': ['#N/D', '#N/D']
        })

        result = strategy.process_data(df)

        # All rows filtered out
        assert len(result) == 0

    def test_grouping_with_single_group(self):
        """Test grouping that results in single group."""
        config = get_bubble_chart_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S1', 'S1'],
            'compoundname': ['C1', 'C1', 'C1'],
            'ko': ['K00001', 'K00002', 'K00003']
        })

        result = strategy.process_data(df)

        assert len(result) == 1
        assert result['unique_ko_count'].values[0] == 3

    def test_filter_with_missing_column(self):
        """Test filter with missing column (logs warning, returns original)."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'genesymbol': ['G1']
        })

        result = strategy._apply_filter_step(df, {
            'column': 'missing_col',
            'operator': '==',
            'value': 'test'
        })

        # Should return original data
        assert len(result) == 1

    def test_grouping_with_missing_columns(self):
        """Test grouping with missing columns (logs warning, returns original)."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'genesymbol': ['G1']
        })

        result = strategy._apply_grouping_step(df, {
            'group_by': ['missing_col'],
            'agg_column': 'another_missing',
            'agg_function': 'count'
        })

        # Should return original data
        assert len(result) == 1

    def test_sort_with_missing_column(self):
        """Test sort with missing column (logs warning, returns original)."""
        config = get_simple_scatter_config()
        strategy = DotPlotStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2'],
            'genesymbol': ['G1', 'G2']
        })

        result = strategy._apply_sort_step(df, {
            'by': 'missing_col',
            'ascending': True
        })

        # Should return original data
        assert len(result) == 2
