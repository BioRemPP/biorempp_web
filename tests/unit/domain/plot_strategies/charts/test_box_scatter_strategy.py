"""
Unit Tests for BoxScatterStrategy.

This module tests the BoxScatterStrategy class, which creates combined
box plot with jittered scatter plot visualizations.

Test Categories:
- Initialization: Test strategy creation and configuration
- Data Validation: Test validate_data() method
- Data Processing: Test process_data() method
- Box Trace Creation: Test _add_box_trace() method
- Scatter Trace Creation: Test _add_scatter_trace() method
- Jitter Application: Test _apply_jitter() method
- Layout Application: Test _apply_layout() method
- Figure Creation: Test create_figure() and generate() methods
- Integration: Test complete workflow
- Edge Cases: Test boundary conditions
"""

import pytest
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from src.domain.plot_strategies.charts.box_scatter_strategy import BoxScatterStrategy


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_minimal_config():
    """Get minimal configuration for box scatter plot."""
    return {
        'metadata': {'use_case_id': 'UC-2.3'},
        'visualization': {
            'strategy': 'BoxScatterStrategy',
            'plotly': {
                'scatter': {
                    'y': 'unique_ko_count'
                }
            }
        }
    }


def get_full_config():
    """Get full configuration for box scatter plot."""
    return {
        'metadata': {'use_case_id': 'UC-2.3'},
        'data': {
            'required_columns': ['sample', 'unique_ko_count', 'rank']
        },
        'visualization': {
            'strategy': 'BoxScatterStrategy',
            'plotly': {
                'box': {
                    'y': 'unique_ko_count',
                    'name': 'Distribution',
                    'boxmean': True,
                    'marker': {
                        'color': '#198754'
                    }
                },
                'scatter': {
                    'y': 'unique_ko_count',
                    'mode': 'markers',
                    'name': 'Samples',
                    'jitter': 0.01,
                    'marker': {
                        'color': 'rgba(0,0,0,0.5)',
                        'size': 8,
                        'line': {
                            'color': 'white',
                            'width': 1
                        }
                    },
                    'customdata_columns': ['sample', 'rank'],
                    'hovertemplate': '<b>%{customdata[0]}</b><br>Rank: %{customdata[1]}<br>Count: %{y}<extra></extra>'
                },
                'layout': {
                    'yaxis': {
                        'title': 'Unique KO Count'
                    },
                    'showlegend': False,
                    'hovermode': 'closest',
                    'plot_bgcolor': 'white',
                    'paper_bgcolor': 'white'
                }
            }
        }
    }


def get_sample_data():
    """Get sample aggregated data for testing."""
    return pd.DataFrame({
        'sample': ['S1', 'S2', 'S3', 'S4', 'S5'],
        'unique_ko_count': [10, 15, 12, 18, 14],
        'rank': [5, 2, 4, 1, 3]
    })


# ============================================================================
# INITIALIZATION TESTS
# ============================================================================

class TestBoxScatterStrategyInitialization:
    """Test BoxScatterStrategy initialization."""

    def test_initialization_minimal_config(self):
        """Test initialization with minimal configuration."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        assert strategy.plotly_config is not None
        assert strategy.data_config is not None

    def test_initialization_full_config(self):
        """Test initialization with full configuration."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        assert 'box' in strategy.plotly_config
        assert 'scatter' in strategy.plotly_config
        assert 'layout' in strategy.plotly_config

    def test_initialization_extracts_configs(self):
        """Test that initialization extracts configs correctly."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        box_config = strategy.plotly_config.get('box', {})
        scatter_config = strategy.plotly_config.get('scatter', {})

        assert box_config.get('boxmean') is True
        assert scatter_config.get('jitter') == 0.01


# ============================================================================
# DATA VALIDATION TESTS
# ============================================================================

class TestDataValidation:
    """Test validate_data() method."""

    def test_validate_empty_dataframe_fails(self):
        """Test that empty DataFrame raises ValueError."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="DataFrame is empty"):
            strategy.validate_data(df)

    def test_validate_missing_required_columns(self):
        """Test missing required columns raises ValueError."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = pd.DataFrame({'sample': ['S1']})

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)

    def test_validate_success_with_config(self):
        """Test successful validation with configured columns."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        # Should not raise
        strategy.validate_data(df)

    def test_validate_uses_default_columns(self):
        """Test that default columns are used when not configured."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        # Should use default columns: sample, unique_ko_count, rank
        df = get_sample_data()
        strategy.validate_data(df)  # Should not raise

    def test_validate_fails_with_missing_defaults(self):
        """Test validation fails when default columns missing."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)
        df = pd.DataFrame({'other_column': [1, 2, 3]})

        with pytest.raises(ValueError, match="Missing required columns"):
            strategy.validate_data(df)


# ============================================================================
# DATA PROCESSING TESTS
# ============================================================================

class TestDataProcessing:
    """Test process_data() method."""

    def test_process_data_returns_copy(self):
        """Test that process_data returns a clean copy."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        result = strategy.process_data(df)

        # Should be equal but not same object
        pd.testing.assert_frame_equal(result, df)
        assert result is not df

    def test_process_data_preserves_data(self):
        """Test that process_data preserves all data."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        result = strategy.process_data(df)

        assert len(result) == len(df)
        assert list(result.columns) == list(df.columns)


# ============================================================================
# JITTER TESTS
# ============================================================================

class TestJitter:
    """Test _apply_jitter() method."""

    def test_apply_jitter_returns_array(self):
        """Test that jitter returns numpy array."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        result = strategy._apply_jitter(
            x_position=1.0,
            n_points=10,
            jitter_scale=0.01
        )

        assert isinstance(result, np.ndarray)
        assert len(result) == 10

    def test_apply_jitter_centers_at_position(self):
        """Test that jitter centers around x_position."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        result = strategy._apply_jitter(
            x_position=5.0,
            n_points=1000,
            jitter_scale=0.01
        )

        # Mean should be close to x_position
        assert abs(np.mean(result) - 5.0) < 0.01

    def test_apply_jitter_respects_scale(self):
        """Test that jitter respects scale parameter."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        result = strategy._apply_jitter(
            x_position=1.0,
            n_points=1000,
            jitter_scale=0.05
        )

        # Standard deviation should be close to scale
        assert abs(np.std(result) - 0.05) < 0.01

    def test_apply_jitter_reproducible(self):
        """Test that jitter is reproducible with same seed."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        result1 = strategy._apply_jitter(
            x_position=1.0,
            n_points=10,
            jitter_scale=0.01,
            random_seed=42
        )

        result2 = strategy._apply_jitter(
            x_position=1.0,
            n_points=10,
            jitter_scale=0.01,
            random_seed=42
        )

        np.testing.assert_array_equal(result1, result2)

    def test_apply_jitter_different_seeds(self):
        """Test that different seeds produce different jitter."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        result1 = strategy._apply_jitter(
            x_position=1.0,
            n_points=10,
            jitter_scale=0.01,
            random_seed=42
        )

        result2 = strategy._apply_jitter(
            x_position=1.0,
            n_points=10,
            jitter_scale=0.01,
            random_seed=99
        )

        # Should be different
        assert not np.array_equal(result1, result2)


# ============================================================================
# BOX TRACE TESTS
# ============================================================================

class TestBoxTrace:
    """Test _add_box_trace() method."""

    def test_add_box_trace_adds_trace(self):
        """Test that box trace is added to figure."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        box_config = strategy.plotly_config.get('box', {})

        result = strategy._add_box_trace(
            fig, df, 'unique_ko_count', box_config
        )

        assert len(result.data) == 1
        assert result.data[0].type == 'box'

    def test_add_box_trace_uses_correct_data(self):
        """Test that box trace uses correct y-data."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        box_config = strategy.plotly_config.get('box', {})

        result = strategy._add_box_trace(
            fig, df, 'unique_ko_count', box_config
        )

        # Check y-values
        np.testing.assert_array_equal(
            result.data[0].y,
            df['unique_ko_count'].values
        )

    def test_add_box_trace_applies_color(self):
        """Test that box trace applies color from config."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        box_config = strategy.plotly_config.get('box', {})

        result = strategy._add_box_trace(
            fig, df, 'unique_ko_count', box_config
        )

        assert result.data[0].marker.color == '#198754'

    def test_add_box_trace_default_position(self):
        """Test box trace with default x position."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        box_config = {}

        result = strategy._add_box_trace(
            fig, df, 'unique_ko_count', box_config
        )

        # Should use position 1
        assert all(x == 1 for x in result.data[0].x)

    def test_add_box_trace_custom_position(self):
        """Test box trace with custom x position."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        box_config = {'x': 5.0}

        result = strategy._add_box_trace(
            fig, df, 'unique_ko_count', box_config
        )

        # Should use position 5
        assert all(x == 5.0 for x in result.data[0].x)


# ============================================================================
# SCATTER TRACE TESTS
# ============================================================================

class TestScatterTrace:
    """Test _add_scatter_trace() method."""

    def test_add_scatter_trace_adds_trace(self):
        """Test that scatter trace is added to figure."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._add_scatter_trace(
            fig, df, 'unique_ko_count', scatter_config
        )

        assert len(result.data) == 1
        assert result.data[0].type == 'scatter'

    def test_add_scatter_trace_uses_correct_data(self):
        """Test that scatter trace uses correct y-data."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._add_scatter_trace(
            fig, df, 'unique_ko_count', scatter_config
        )

        # Check y-values
        np.testing.assert_array_equal(
            result.data[0].y,
            df['unique_ko_count'].values
        )

    def test_add_scatter_trace_applies_jitter(self):
        """Test that scatter trace applies jitter to x-coordinates."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._add_scatter_trace(
            fig, df, 'unique_ko_count', scatter_config
        )

        # X-values should be jittered (not all equal)
        x_values = result.data[0].x
        assert len(set(x_values)) > 1  # Should have variation

    def test_add_scatter_trace_applies_marker_config(self):
        """Test that scatter trace applies marker configuration."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._add_scatter_trace(
            fig, df, 'unique_ko_count', scatter_config
        )

        assert result.data[0].marker.color == 'rgba(0,0,0,0.5)'
        assert result.data[0].marker.size == 8

    def test_add_scatter_trace_with_customdata(self):
        """Test scatter trace with customdata columns."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._add_scatter_trace(
            fig, df, 'unique_ko_count', scatter_config
        )

        # Should have customdata
        assert result.data[0].customdata is not None
        assert result.data[0].customdata.shape[0] == len(df)
        assert result.data[0].customdata.shape[1] == 2  # sample, rank

    def test_add_scatter_trace_without_customdata(self):
        """Test scatter trace without customdata columns."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        scatter_config = {'y': 'unique_ko_count'}

        result = strategy._add_scatter_trace(
            fig, df, 'unique_ko_count', scatter_config
        )

        # Should not have customdata
        assert result.data[0].customdata is None

    def test_add_scatter_trace_with_hovertemplate(self):
        """Test scatter trace with hover template."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        df = get_sample_data()
        scatter_config = strategy.plotly_config.get('scatter', {})

        result = strategy._add_scatter_trace(
            fig, df, 'unique_ko_count', scatter_config
        )

        # Should have hovertemplate
        assert result.data[0].hovertemplate is not None


# ============================================================================
# LAYOUT TESTS
# ============================================================================

class TestLayout:
    """Test _apply_layout() method."""

    def test_apply_layout_basic(self):
        """Test basic layout application."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})

        result = strategy._apply_layout(fig, layout_config)

        assert result.layout.yaxis.title.text == 'Unique KO Count'
        assert result.layout.showlegend is False

    def test_apply_layout_xaxis_hidden(self):
        """Test that xaxis is hidden by default."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})

        result = strategy._apply_layout(fig, layout_config)

        assert result.layout.xaxis.showticklabels is False
        assert result.layout.xaxis.showgrid is False

    def test_apply_layout_yaxis_grid(self):
        """Test yaxis grid configuration."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})

        result = strategy._apply_layout(fig, layout_config)

        assert result.layout.yaxis.zeroline is True
        assert result.layout.yaxis.zerolinecolor == '#cccccc'

    def test_apply_layout_background_colors(self):
        """Test background color configuration."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        layout_config = strategy.plotly_config.get('layout', {})

        result = strategy._apply_layout(fig, layout_config)

        assert result.layout.plot_bgcolor == 'white'
        assert result.layout.paper_bgcolor == 'white'

    def test_apply_layout_default_yaxis_title(self):
        """Test default yaxis title when not configured."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)

        fig = go.Figure()
        layout_config = {}

        result = strategy._apply_layout(fig, layout_config)

        # Should use default title
        assert 'No. of Unique KOs per Sample' in result.layout.yaxis.title.text


# ============================================================================
# FIGURE CREATION TESTS
# ============================================================================

class TestFigureCreation:
    """Test create_figure() and generate() methods."""

    def test_generate_returns_figure(self):
        """Test that generate returns a Plotly Figure."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        fig = strategy.generate(df)

        assert isinstance(fig, go.Figure)

    def test_generate_has_two_traces(self):
        """Test that generated figure has box and scatter traces."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        fig = strategy.generate(df)

        assert len(fig.data) == 2
        assert fig.data[0].type == 'box'
        assert fig.data[1].type == 'scatter'

    def test_generate_empty_data_fails(self):
        """Test that empty data raises ValueError."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = pd.DataFrame()

        with pytest.raises(ValueError, match="DataFrame is empty"):
            strategy.generate(df)

    def test_generate_missing_y_column_fails(self):
        """Test that missing y column raises ValueError."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = pd.DataFrame({'other': [1, 2, 3]})

        with pytest.raises(ValueError, match="Column .* not found"):
            strategy.generate(df)

    def test_generate_missing_config_fails(self):
        """Test that missing scatter.y config raises ValueError."""
        config = get_minimal_config()
        del config['visualization']['plotly']['scatter']['y']
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        with pytest.raises(ValueError, match="Configuration missing"):
            strategy.generate(df)

    def test_create_figure_calls_generate(self):
        """Test that create_figure calls generate."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        fig = strategy.create_figure(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Test complete workflow."""

    def test_generate_plot_complete_workflow(self):
        """Test complete generate_plot workflow."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_workflow_with_validation(self):
        """Test workflow with explicit validation."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        strategy.validate_data(df)
        processed = strategy.process_data(df)
        fig = strategy.create_figure(processed)

        assert isinstance(fig, go.Figure)
        assert len(processed) == len(df)

    def test_workflow_minimal_config(self):
        """Test workflow with minimal configuration."""
        config = get_minimal_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        fig = strategy.generate_plot(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_workflow_preserves_data_integrity(self):
        """Test that workflow preserves data integrity."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()
        original_sum = df['unique_ko_count'].sum()

        fig = strategy.generate_plot(df)

        # Check that box trace has correct sum
        box_sum = sum(fig.data[0].y)
        scatter_sum = sum(fig.data[1].y)

        assert box_sum == original_sum
        assert scatter_sum == original_sum


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_single_data_point(self):
        """Test with single data point."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1'],
            'unique_ko_count': [10],
            'rank': [1]
        })

        fig = strategy.generate(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].y) == 1
        assert len(fig.data[1].y) == 1

    def test_large_dataset(self):
        """Test with large dataset."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        df = pd.DataFrame({
            'sample': [f'S{i}' for i in range(100)],
            'unique_ko_count': np.random.randint(5, 50, 100),
            'rank': list(range(1, 101))
        })

        fig = strategy.generate(df)

        assert isinstance(fig, go.Figure)
        assert len(fig.data[0].y) == 100
        assert len(fig.data[1].y) == 100

    def test_all_same_values(self):
        """Test with all identical values."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'unique_ko_count': [10, 10, 10],
            'rank': [1, 2, 3]
        })

        fig = strategy.generate(df)

        assert isinstance(fig, go.Figure)
        # Box plot should still work with no variance
        assert len(fig.data) == 2

    def test_extreme_jitter_values(self):
        """Test with extreme jitter scale."""
        config = get_full_config()
        config['visualization']['plotly']['scatter']['jitter'] = 1.0
        strategy = BoxScatterStrategy(config)

        df = get_sample_data()
        fig = strategy.generate(df)

        # Should still generate valid figure
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_zero_jitter(self):
        """Test with zero jitter."""
        config = get_full_config()
        config['visualization']['plotly']['scatter']['jitter'] = 0.0
        strategy = BoxScatterStrategy(config)

        df = get_sample_data()
        fig = strategy.generate(df)

        # All scatter points should be at same x position
        x_values = fig.data[1].x
        assert abs(np.std(x_values)) < 0.0001

    def test_missing_optional_configs(self):
        """Test with missing optional configuration."""
        config = {
            'metadata': {},
            'visualization': {
                'strategy': 'BoxScatterStrategy',
                'plotly': {
                    'scatter': {'y': 'unique_ko_count'}
                }
            }
        }
        strategy = BoxScatterStrategy(config)
        df = get_sample_data()

        fig = strategy.generate(df)

        # Should use defaults
        assert isinstance(fig, go.Figure)
        assert len(fig.data) == 2

    def test_custom_y_column(self):
        """Test with custom y column name."""
        config = get_minimal_config()
        config['visualization']['plotly']['scatter']['y'] = 'custom_value'
        strategy = BoxScatterStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'custom_value': [100, 200, 150],
            'unique_ko_count': [10, 20, 15],
            'rank': [1, 2, 3]
        })

        fig = strategy.generate(df)

        # Should use custom_value column
        assert list(fig.data[0].y) == [100, 200, 150]
        assert list(fig.data[1].y) == [100, 200, 150]

    def test_negative_values(self):
        """Test with negative values in data."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'unique_ko_count': [-5, 0, 5],
            'rank': [3, 2, 1]
        })

        fig = strategy.generate(df)

        # Should handle negative values
        assert isinstance(fig, go.Figure)
        assert min(fig.data[0].y) == -5

    def test_float_values(self):
        """Test with float values in data."""
        config = get_full_config()
        strategy = BoxScatterStrategy(config)

        df = pd.DataFrame({
            'sample': ['S1', 'S2', 'S3'],
            'unique_ko_count': [10.5, 15.7, 12.3],
            'rank': [3, 1, 2]
        })

        fig = strategy.generate(df)

        assert isinstance(fig, go.Figure)
        assert abs(fig.data[0].y[0] - 10.5) < 0.01
